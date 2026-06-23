"""Orchestrate: build context -> render DOCX -> convert to PDF -> save -> persist GeneratedDocument."""

from __future__ import annotations

import logging
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.db.models import DeliveryDocket, GeneratedDocument, SalesOrder
from app.documents.context_builder import (
    build_context_from_contact_and_lines,
    build_context_from_delivery_docket,
    build_context_from_order_product_summary,
    build_context_from_sales_order,
    safe_slug_for_filename,
)
from app.documents.contracts import DocumentContext, DocumentOverrides
from app.documents.converter import convert_to_pdf
from app.documents.renderer import render_docx
from app.documents.repository import (
    create_document_record,
    mark_completed,
    mark_failed,
    mark_running,
)
from app.settings import settings

logger = logging.getLogger(__name__)


class DocumentGenerationService:
    """Generate PDF (and optional DOCX) from template + DB data."""

    def __init__(
        self,
        session: Session,
        template_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        keep_docx: Optional[bool] = None,
        conversion_backend: Optional[str] = None,
        conversion_timeout: Optional[int] = None,
        libreoffice_path: Optional[str] = None,
    ):
        self.session = session
        cfg = settings.docgen
        self.template_dir = template_dir or cfg.template_dir
        self.output_dir = output_dir or cfg.output_dir
        self.keep_docx = keep_docx if keep_docx is not None else cfg.keep_docx
        self.conversion_backend = conversion_backend or cfg.conversion_backend
        self.conversion_timeout = conversion_timeout or cfg.conversion_timeout_seconds
        self.libreoffice_path = libreoffice_path or cfg.libreoffice_path

    def _template_path(self, template_name: str) -> Path:
        """Resolve template file. template_name can be filename or path relative to template_dir."""
        p = Path(template_name)
        if not p.suffix:
            p = Path(template_name + ".docx")
        if not p.is_absolute():
            p = self.template_dir / p
        return p

    def generate(
        self,
        template_name: str,
        doc_type: str,
        doc_number: str,
        contact_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        quote_id: Optional[str] = None,
        delivery_docket_id: Optional[str] = None,
        line_specs: Optional[list] = None,
        overrides: Optional[DocumentOverrides] = None,
        output_docx: Optional[bool] = None,
        product_summary_rows: Optional[list] = None,
        product_summary_orders: Optional[list] = None,
        product_summary_order_count: Optional[int] = None,
        product_summary_period_start: Optional["date"] = None,
        product_summary_period_end: Optional["date"] = None,
        product_summary_total_ex_gst: Optional["Decimal"] = None,
        product_summary_total_inc_gst: Optional["Decimal"] = None,
        product_summary_total_qty: Optional["Decimal"] = None,
    ) -> tuple[Optional[GeneratedDocument], Optional[Path], Optional[Path], str]:
        """
        Generate document. Returns (doc_record, pdf_path, docx_path, error_message).
        If error_message is non-empty, doc_record may still be created (status FAILED).
        """
        output_docx = (
            output_docx if output_docx is not None else settings.docgen.keep_docx
        )
        template_path = self._template_path(template_name)
        if not template_path.exists():
            return None, None, None, f"Template not found: {template_path}"

        # Build context and create DB record first
        context: Optional[DocumentContext] = None
        if product_summary_rows is not None:
            from decimal import Decimal as D

            context = build_context_from_order_product_summary(
                self.session,
                customer_id=customer_id,
                rows=product_summary_rows,
                order_rows=product_summary_orders,
                order_count=product_summary_order_count or 0,
                period_start=product_summary_period_start,
                period_end=product_summary_period_end,
                total_ex_gst=D(str(product_summary_total_ex_gst or 0)),
                total_inc_gst=D(str(product_summary_total_inc_gst or 0)),
                total_qty=D(str(product_summary_total_qty or 0)),
                doc_type=doc_type,
            )
            doc_number = doc_number or context.document.doc_number
        elif delivery_docket_id:
            docket = self.session.get(DeliveryDocket, delivery_docket_id)
            if not docket:
                return (
                    None,
                    None,
                    None,
                    f"DeliveryDocket not found: {delivery_docket_id}",
                )
            context = build_context_from_delivery_docket(
                self.session, docket, doc_type=doc_type, overrides=overrides
            )
            customer_id = str(docket.customer_id) if docket.customer_id else None
            contact_id = None
            doc_number = doc_number or docket.docket_number
        elif quote_id:
            order = self.session.get(SalesOrder, quote_id)
            if not order:
                return None, None, None, f"SalesOrder not found: {quote_id}"
            context = build_context_from_sales_order(
                self.session, order, doc_type=doc_type, overrides=overrides
            )
            customer_id = str(order.customer_id) if order.customer_id else None
            contact_id = None
            doc_number = doc_number or (order.order_ref or str(order.id))
        else:
            line_specs = line_specs or []
            context = build_context_from_contact_and_lines(
                self.session,
                contact_id=contact_id,
                customer_id=customer_id,
                line_specs=line_specs,
                doc_type=doc_type,
                doc_number=doc_number,
                overrides=overrides,
            )

        slug = safe_slug_for_filename(context.contact, doc_number, doc_type)
        doc_record = create_document_record(
            self.session,
            doc_type=doc_type,
            template_name=template_name,
            doc_number=doc_number,
            contact_id=contact_id,
            customer_id=customer_id,
            sales_order_id=quote_id,
            delivery_docket_id=delivery_docket_id,
        )
        self.session.commit()
        document_id = doc_record.id

        try:
            mark_running(self.session, document_id)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        pdf_path = self.output_dir / f"{slug}.pdf"
        docx_path_temp: Optional[Path] = None
        tmpdir = None
        try:
            import shutil
            import time

            tmpdir = tempfile.mkdtemp(prefix="docgen_")
            tmp = Path(tmpdir)
            docx_temp = tmp / "output.docx"
            render_docx(template_path, context, docx_temp)
            ok, err = convert_to_pdf(
                docx_temp,
                pdf_path,
                backend=self.conversion_backend,
                timeout_seconds=self.conversion_timeout,
                libreoffice_path=self.libreoffice_path,
            )
            if not ok:
                if self.keep_docx:
                    docx_fallback = self.output_dir / f"{slug}_rendered.docx"
                    docx_fallback.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy(docx_temp, docx_fallback)
                        logger.info(
                            "Conversion failed; saved rendered DOCX to %s",
                            docx_fallback,
                        )
                    except Exception:
                        pass
                mark_failed(self.session, document_id, err)
                self.session.commit()
                return doc_record, None, None, err
            time.sleep(0.5)  # Let Word release the file on Windows
            if output_docx:
                docx_path_temp = self.output_dir / f"{slug}.docx"
                docx_path_temp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(docx_temp, docx_path_temp)
        except Exception as e:
            logger.exception("Document generation failed")
            mark_failed(self.session, document_id, str(e))
            self.session.commit()
            return doc_record, None, None, str(e)
        finally:
            if tmpdir:
                try:
                    import shutil

                    shutil.rmtree(tmpdir, ignore_errors=True)
                except Exception:
                    pass

        pdf_str = str(pdf_path.resolve())
        docx_str = str(docx_path_temp.resolve()) if docx_path_temp else None
        mark_completed(self.session, document_id, pdf_str, docx_str)
        if delivery_docket_id:
            docket = self.session.get(DeliveryDocket, delivery_docket_id)
            if docket:
                docket.generated_document_id = document_id
        self.session.commit()
        doc_record = self.session.get(GeneratedDocument, document_id)
        return doc_record, pdf_path, docx_path_temp, ""

    def generate_from_context(
        self,
        template_name: str,
        doc_type: str,
        context: DocumentContext,
        *,
        customer_id: Optional[str] = None,
        contact_id: Optional[str] = None,
        doc_number: Optional[str] = None,
        output_docx: Optional[bool] = None,
    ) -> tuple[Optional[GeneratedDocument], Optional[Path], Optional[Path], str]:
        """Generate PDF from a pre-built DocumentContext (e.g. CRM summary)."""
        output_docx = (
            output_docx if output_docx is not None else settings.docgen.keep_docx
        )
        template_path = self._template_path(template_name)
        if not template_path.exists():
            return None, None, None, f"Template not found: {template_path}"

        doc_number = doc_number or context.document.doc_number
        slug = safe_slug_for_filename(context.contact, doc_number, doc_type)
        doc_record = create_document_record(
            self.session,
            doc_type=doc_type,
            template_name=template_name,
            doc_number=doc_number,
            contact_id=contact_id,
            customer_id=customer_id,
        )
        self.session.commit()
        document_id = doc_record.id

        try:
            mark_running(self.session, document_id)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        pdf_path = self.output_dir / f"{slug}.pdf"
        docx_path_temp: Optional[Path] = None
        tmpdir = None
        try:
            import shutil
            import time

            tmpdir = tempfile.mkdtemp(prefix="docgen_")
            tmp = Path(tmpdir)
            docx_temp = tmp / "output.docx"
            render_docx(template_path, context, docx_temp)
            ok, err = convert_to_pdf(
                docx_temp,
                pdf_path,
                backend=self.conversion_backend,
                timeout_seconds=self.conversion_timeout,
                libreoffice_path=self.libreoffice_path,
            )
            if not ok:
                mark_failed(self.session, document_id, err)
                self.session.commit()
                return doc_record, None, None, err
            time.sleep(0.5)
            if output_docx:
                docx_path_temp = self.output_dir / f"{slug}.docx"
                docx_path_temp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(docx_temp, docx_path_temp)
        except Exception as e:
            logger.exception("Document generation failed")
            mark_failed(self.session, document_id, str(e))
            self.session.commit()
            return doc_record, None, None, str(e)
        finally:
            if tmpdir:
                try:
                    import shutil

                    shutil.rmtree(tmpdir, ignore_errors=True)
                except Exception:
                    pass

        pdf_str = str(pdf_path.resolve())
        docx_str = str(docx_path_temp.resolve()) if docx_path_temp else None
        mark_completed(self.session, document_id, pdf_str, docx_str)
        self.session.commit()
        doc_record = self.session.get(GeneratedDocument, document_id)
        return doc_record, pdf_path, docx_path_temp, ""
