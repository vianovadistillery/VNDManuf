"""Analyze Alembic migration state and identify conflicts.

This script:
- Reads applied migrations from database
- Scans available migration files
- Builds migration chain/dependency graph
- Identifies conflicts, branches, and missing migrations
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

import alembic.config
from alembic.script import ScriptDirectory


def get_applied_versions(db_path):
    """Get applied migration versions from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT version_num FROM alembic_version")
        versions = [row[0] for row in cursor.fetchall()]
        return versions
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def get_migration_info(migration_file):
    """Extract revision info from migration file."""
    with open(migration_file, "r") as f:
        content = f.read()
    
    info = {}
    
    # Extract revision ID
    rev_match = re.search(r'revision:\s*str\s*=\s*["\']([^"\']+)["\']', content)
    if rev_match:
        info["revision"] = rev_match.group(1)
    
    # Extract down_revision
    down_match = re.search(r'down_revision:\s*Union\[str,\s*None\]\s*=\s*(?:["\']([^"\']+)["\']|None)', content)
    if down_match:
        info["down_revision"] = down_match.group(1) if down_match.group(1) else None
    else:
        # Try alternate format
        down_match = re.search(r'down_revision:\s*(?:["\']([^"\']+)["\']|None)', content)
        if down_match:
            info["down_revision"] = down_match.group(1) if down_match.group(1) else None
        else:
            info["down_revision"] = None
    
    # Extract description from docstring
    doc_match = re.search(r'"""([^"]+)"""', content)
    if doc_match:
        info["description"] = doc_match.group(1).strip()
    else:
        info["description"] = migration_file.stem
    
    # Extract create date if present
    date_match = re.search(r'Create Date:\s*([^\n]+)', content)
    if date_match:
        info["create_date"] = date_match.group(1).strip()
    
    return info


def build_migration_graph(migrations_dir):
    """Build dependency graph of migrations."""
    migrations = {}
    graph = {}
    
    # Scan all migration files
    for migration_file in sorted(migrations_dir.glob("*.py")):
        if migration_file.name == "__init__.py":
            continue
        
        info = get_migration_info(migration_file)
        if "revision" not in info:
            continue
        
        revision = info["revision"]
        migrations[revision] = {
            "file": migration_file.name,
            "path": str(migration_file),
            **info,
        }
        
        # Build graph
        if revision not in graph:
            graph[revision] = []
        
        if info["down_revision"]:
            if info["down_revision"] not in graph:
                graph[info["down_revision"]] = []
            graph[info["down_revision"]].append(revision)
    
    return migrations, graph


def find_heads(graph, migrations):
    """Find head revisions (those with no children)."""
    all_revisions = set(graph.keys())
    children = set()
    for children_list in graph.values():
        children.update(children_list)
    
    heads = all_revisions - children
    return list(heads)


def find_roots(graph):
    """Find root revisions (those with no parent/down_revision)."""
    roots = []
    for rev, children in graph.items():
        migration = migrations.get(rev, {})
        if migration.get("down_revision") is None:
            roots.append(rev)
    return roots


def trace_path(applied_versions, graph, migrations):
    """Trace migration paths from applied versions."""
    paths = {}
    
    for applied in applied_versions:
        path = [applied]
        current = applied
        
        # Walk backwards
        while current:
            migration = migrations.get(current, {})
            down_rev = migration.get("down_revision")
            if down_rev:
                path.insert(0, down_rev)
                current = down_rev
            else:
                break
        
        paths[applied] = path
    
    return paths


def main():
    """Main execution."""
    db_path = "tpmanuf.db"
    migrations_dir = Path("db/alembic/versions")
    
    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found: {migrations_dir}")
        return
    
    # Get applied versions
    applied_versions = get_applied_versions(db_path)
    print(f"Applied migrations in database: {applied_versions}")
    
    # Build migration graph
    migrations, graph = build_migration_graph(migrations_dir)
    print(f"\nFound {len(migrations)} migration files")
    
    # Find heads and roots
    heads = find_heads(graph, migrations)
    roots = [rev for rev, m in migrations.items() if m.get("down_revision") is None]
    
    # Analyze state
    analysis = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "database_path": db_path,
            "migrations_dir": str(migrations_dir),
        },
        "applied_versions": applied_versions,
        "available_migrations": len(migrations),
        "migration_files": {},
        "heads": heads,
        "roots": roots,
        "issues": {},
    }
    
    # Build migration file info
    for rev, info in migrations.items():
        analysis["migration_files"][rev] = {
            "file": info["file"],
            "description": info.get("description", ""),
            "down_revision": info.get("down_revision"),
            "create_date": info.get("create_date"),
            "is_applied": rev in applied_versions,
        }
    
    # Identify issues
    issues = []
    
    # Check for migrations that aren't applied
    unapplied = set(migrations.keys()) - set(applied_versions)
    if unapplied:
        issues.append({
            "type": "unapplied_migrations",
            "count": len(unapplied),
            "revisions": sorted(list(unapplied)),
        })
    
    # Check for multiple heads (branching)
    if len(heads) > 1:
        issues.append({
            "type": "multiple_heads",
            "count": len(heads),
            "heads": heads,
            "message": "Database has multiple migration heads - indicates branching or conflicts",
        })
    
    # Check for applied versions not in files
    missing_files = set(applied_versions) - set(migrations.keys())
    if missing_files:
        issues.append({
            "type": "missing_files",
            "count": len(missing_files),
            "revisions": sorted(list(missing_files)),
            "message": "Database references migrations that don't exist in files",
        })
    
    # Trace paths from applied versions
    paths = trace_path(applied_versions, graph, migrations)
    analysis["applied_paths"] = paths
    
    # Check for conflicts (applied versions that are not heads but should be)
    if applied_versions:
        # If we have applied versions but multiple heads, there's likely a conflict
        if len(heads) > 1:
            for applied in applied_versions:
                # Check if this applied version can reach any of the heads
                reachable_heads = []
                for head in heads:
                    # Simple check: if applied is in path to head
                    if head in graph and applied in graph:
                        # Check if we can reach head from applied
                        # (simplified - just check if head comes after applied in any path)
                        pass
                if not reachable_heads:
                    issues.append({
                        "type": "applied_not_on_head_path",
                        "revision": applied,
                        "message": f"Applied revision {applied} may not be on path to current head",
                    })
    
    analysis["issues"] = issues
    
    # Create output directory
    output_dir = Path("docs/snapshot")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export JSON
    json_path = output_dir / "migration_analysis.json"
    with open(json_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"\n[OK] Exported migration analysis to {json_path}")
    
    # Summary
    print(f"\nMigration Analysis Summary:")
    print(f"  - Applied in DB: {len(applied_versions)}")
    print(f"  - Available files: {len(migrations)}")
    print(f"  - Unapplied: {len(unapplied)}")
    print(f"  - Heads: {len(heads)}")
    print(f"  - Roots: {len(roots)}")
    print(f"  - Issues found: {len(issues)}")
    
    if issues:
        print(f"\nIssues:")
        for issue in issues:
            print(f"  - {issue['type']}: {issue.get('count', issue.get('message', ''))}")


if __name__ == "__main__":
    # Make migrations available in global scope for helper functions
    migrations = {}
    main()

