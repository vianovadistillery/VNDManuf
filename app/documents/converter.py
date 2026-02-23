"""DOCX to PDF: docx2pdf (Word) primary, LibreOffice fallback. Timeouts and retries."""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _run_with_timeout(
    cmd: list,
    cwd: Optional[Path] = None,
    timeout_seconds: int = 60,
) -> tuple[bool, str]:
    """Run command; return (success, error_message)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        if result.returncode != 0:
            return (
                False,
                result.stderr or result.stdout or f"Exit code {result.returncode}",
            )
        return True, ""
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout_seconds}s"
    except FileNotFoundError as e:
        return False, f"Command not found: {e}"
    except Exception as e:
        return False, str(e)


def convert_docx2pdf(
    docx_path: Path,
    pdf_path: Path,
    timeout_seconds: int = 60,
    max_retries: int = 2,
) -> tuple[bool, str]:
    """Convert using docx2pdf (Microsoft Word on Windows). Retries with 5s backoff. Returns (success, error_message)."""
    try:
        from docx2pdf import convert as docx2pdf_convert
    except ImportError:
        return False, "docx2pdf not installed"
    import sys
    import time as _time

    docx_path = docx_path.resolve()
    pdf_path = pdf_path.resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    last_err = ""

    for attempt in range(max_retries + 1):
        if attempt > 0:
            _time.sleep(5)  # backoff 5s
        try:
            if sys.platform == "win32":
                try:
                    import pythoncom

                    pythoncom.CoInitialize()
                except ImportError:
                    pass
            docx2pdf_convert(str(docx_path), str(pdf_path))
            return True, ""
        except BaseException as e:
            last_err = str(e)
    return False, last_err


def convert_libreoffice(
    docx_path: Path,
    output_dir: Path,
    timeout_seconds: int = 120,
    soffice_path: Optional[str] = None,
) -> tuple[Optional[Path], str]:
    """Convert using LibreOffice headless. Returns (pdf_path, error_message). PDF is output_dir/<docx_stem>.pdf."""
    docx_path = docx_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    exe = soffice_path or "soffice"
    cmd = [
        exe,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(docx_path),
    ]
    ok, err = _run_with_timeout(cmd, timeout_seconds=timeout_seconds)
    if not ok:
        return None, err
    pdf_path = output_dir / f"{docx_path.stem}.pdf"
    if not pdf_path.exists():
        return None, "LibreOffice did not produce PDF"
    return pdf_path, ""


def convert_to_pdf(
    docx_path: Path,
    pdf_path: Path,
    backend: str = "auto",
    timeout_seconds: int = 60,
    libreoffice_path: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Convert DOCX to PDF. backend: docx2pdf | libreoffice | auto.
    Returns (success, error_message). On success pdf_path exists.
    """
    docx_path = docx_path.resolve()
    pdf_path = pdf_path.resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    if backend == "libreoffice":
        out_dir = pdf_path.parent
        result_path, err = convert_libreoffice(
            docx_path,
            out_dir,
            timeout_seconds=max(timeout_seconds, 120),
            soffice_path=libreoffice_path,
        )
        if result_path is None:
            return False, err
        if result_path != pdf_path and result_path.exists():
            result_path.rename(pdf_path)
        return True, ""

    if backend == "docx2pdf" or backend == "auto":
        ok, err = convert_docx2pdf(docx_path, pdf_path, timeout_seconds=timeout_seconds)
        if ok:
            return True, ""
        if backend == "docx2pdf":
            return False, err
        logger.warning("docx2pdf failed, trying LibreOffice fallback: %s", err)

    out_dir = pdf_path.parent
    result_path, err_lo = convert_libreoffice(
        docx_path,
        out_dir,
        timeout_seconds=max(timeout_seconds, 120),
        soffice_path=libreoffice_path,
    )
    if result_path is None:
        return False, f"docx2pdf failed: {err}; LibreOffice failed: {err_lo}"
    if result_path != pdf_path and result_path.exists():
        result_path.rename(pdf_path)
    return True, ""
