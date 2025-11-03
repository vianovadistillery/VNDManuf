"""Extract SQLAlchemy model structure from code.

This script imports all models and uses SQLAlchemy introspection to extract:
- Table names
- Column definitions (name, type, nullable, default, etc.)
- Indexes
- Foreign keys
- Relationships
- Constraints
"""

import inspect
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect as sqla_inspect


def get_column_info(column):
    """Extract information from a SQLAlchemy Column."""
    col_info = {
        "name": column.name,
        "type": str(column.type),
    }
    
    # Get nullable - handle Boolean columns specially
    try:
        col_info["nullable"] = bool(column.nullable) if column.nullable is not None else None
    except (TypeError, ValueError):
        # Boolean columns may have nullable that can't be evaluated directly
        col_info["nullable"] = None
    
    # Get default value if present
    try:
        if column.default is not None:
            if hasattr(column.default, "arg"):
                col_info["default"] = str(column.default.arg)
            else:
                col_info["default"] = str(column.default)
        elif column.server_default is not None:
            col_info["server_default"] = str(column.server_default)
    except Exception:
        pass
    
    # Check if primary key
    col_info["primary_key"] = column.primary_key
    
    # Get foreign key info
    try:
        if column.foreign_keys:
            fk_info = []
            for fk in column.foreign_keys:
                fk_info.append({
                    "target_table": fk.column.table.name if fk.column else None,
                    "target_column": fk.column.name if fk.column else None,
                })
            col_info["foreign_keys"] = fk_info
    except Exception:
        pass
    
    return col_info


def get_table_info(model_class):
    """Extract complete information about a model's table."""
    inspector = sqla_inspect(model_class)
    table = model_class.__table__
    
    info = {
        "table_name": table.name,
        "columns": [],
        "indexes": [],
        "foreign_keys": [],
        "constraints": [],
    }
    
    # Extract columns
    for column in table.columns:
        info["columns"].append(get_column_info(column))
    
    # Extract indexes
    for index in table.indexes:
        idx_info = {
            "name": index.name,
            "unique": index.unique,
            "columns": [col.name for col in index.columns],
        }
        info["indexes"].append(idx_info)
    
    # Extract constraints
    for constraint in table.constraints:
        if hasattr(constraint, "columns"):
            constraint_info = {
                "name": constraint.name if hasattr(constraint, "name") else None,
                "type": constraint.__class__.__name__,
                "columns": [col.name for col in constraint.columns],
            }
            if hasattr(constraint, "unique"):
                constraint_info["unique"] = constraint.unique
            info["constraints"].append(constraint_info)
    
    # Extract relationships
    relationships = []
    for rel_name, rel_prop in inspector.relationships.items():
        rel_info = {
            "name": rel_name,
            "target": rel_prop.entity.class_.__name__ if rel_prop.entity else None,
            "target_table": rel_prop.entity.class_.__table__.name if rel_prop.entity else None,
            "direction": str(rel_prop.direction),
        }
        if rel_prop.uselist is not None:
            rel_info["uselist"] = rel_prop.uselist
        relationships.append(rel_info)
    info["relationships"] = relationships
    
    return info


def find_all_models():
    """Import and discover all SQLAlchemy models."""
    # Import all model modules to register them with Base
    try:
        from app.adapters.db import models
        from app.adapters.db import models_assemblies_shopify
    except ImportError as e:
        print(f"Warning: Could not import models: {e}")
        return []
    
    # Try to import qb_models if it exists
    try:
        from app.adapters.db import qb_models
    except ImportError:
        qb_models = None
    
    # Get Base
    from app.adapters.db.base import Base
    
    # Find all classes that inherit from Base and have __tablename__
    all_models = []
    
    # Check models module
    for name in dir(models):
        obj = getattr(models, name)
        if (
            inspect.isclass(obj)
            and issubclass(obj, Base)
            and hasattr(obj, "__tablename__")
            and obj != Base
        ):
            all_models.append(obj)
    
    # Check models_assemblies_shopify module
    for name in dir(models_assemblies_shopify):
        obj = getattr(models_assemblies_shopify, name)
        if (
            inspect.isclass(obj)
            and issubclass(obj, Base)
            and hasattr(obj, "__tablename__")
            and obj != Base
        ):
            all_models.append(obj)
    
    # Check qb_models if it exists
    if qb_models:
        for name in dir(qb_models):
            obj = getattr(qb_models, name)
            if (
                inspect.isclass(obj)
                and issubclass(obj, Base)
                and hasattr(obj, "__tablename__")
                and obj != Base
            ):
                all_models.append(obj)
    
    return all_models


def main():
    """Main execution."""
    print("Discovering SQLAlchemy models...")
    
    models = find_all_models()
    
    if not models:
        print("Error: No models found!")
        return
    
    print(f"Found {len(models)} models")
    
    # Extract model information
    code_data = {
        "metadata": {
            "snapshot_date": datetime.now().isoformat(),
            "total_models": len(models),
        },
        "models": {},
    }
    
    for model_class in models:
        try:
            table_name = model_class.__tablename__
            info = get_table_info(model_class)
            code_data["models"][table_name] = {
                "class_name": model_class.__name__,
                "module": model_class.__module__,
                "table_info": info,
            }
            print(f"  - {model_class.__name__} -> {table_name}")
        except Exception as e:
            # Try to get at least table name even if inspection fails
            try:
                table_name = getattr(model_class, "__tablename__", None)
                if table_name:
                    code_data["models"][table_name] = {
                        "class_name": model_class.__name__,
                        "module": model_class.__module__,
                        "error": str(e),
                    }
                    print(f"  - {model_class.__name__} -> {table_name} (partial - inspection error)")
                else:
                    print(f"  - Error processing {model_class.__name__}: {e}")
            except Exception:
                print(f"  - Error processing {model_class.__name__}: {e}")
    
    # Create output directory
    output_dir = Path("docs/snapshot")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export JSON
    json_path = output_dir / "code_models.json"
    with open(json_path, "w") as f:
        json.dump(code_data, f, indent=2, default=str)
    print(f"\n[OK] Exported code models to {json_path}")
    
    # Summary
    print(f"\nCode Snapshot Summary:")
    print(f"  - Models: {len(code_data['models'])}")
    print(f"  - Tables: {', '.join(sorted(code_data['models'].keys()))}")


if __name__ == "__main__":
    main()

