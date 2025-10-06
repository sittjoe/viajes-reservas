"""Utilities to read the content of uploaded attachments."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from werkzeug.datastructures import FileStorage

try:  # Optional dependency for PDF extraction
    from PyPDF2 import PdfReader  # type: ignore
except Exception:  # pragma: no cover - fallback when PyPDF2 is missing
    PdfReader = None  # type: ignore


@dataclass
class AttachmentSummary:
    """Structured description of a processed attachment."""

    filename: str
    content_type: str
    notes: str

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "content_type": self.content_type,
            "notes": self.notes,
        }


class TextExtractor:
    """Extract plain text from user attachments using best effort heuristics."""

    SUPPORTED_TEXT_TYPES = {"text/plain", "application/pdf"}

    def extract(self, attachments: Iterable[FileStorage]) -> Tuple[str, List[AttachmentSummary]]:
        text_fragments: List[str] = []
        summaries: List[AttachmentSummary] = []

        for attachment in attachments:
            content_type = attachment.mimetype or "application/octet-stream"
            filename = attachment.filename or "documento"

            if content_type == "text/plain":
                body = attachment.stream.read().decode("utf-8", errors="ignore")
                text_fragments.append(body)
                notes = "Texto leído correctamente."
            elif content_type == "application/pdf" and PdfReader is not None:
                notes = self._read_pdf(attachment, text_fragments)
            else:
                notes = "Formato no procesado automáticamente; se considerará para contexto general."

            summaries.append(AttachmentSummary(filename=filename, content_type=content_type, notes=notes))

        return "\n".join(text_fragments), summaries

    def _read_pdf(self, attachment: FileStorage, text_fragments: List[str]) -> str:
        try:
            reader = PdfReader(attachment.stream)
            for page in reader.pages:
                text_fragments.append(page.extract_text() or "")
            notes = "Texto extraído del PDF."
        except Exception as exc:  # pragma: no cover - pdf parsing best effort
            notes = f"No se pudo leer el PDF: {exc}"[:200]
        finally:
            attachment.stream.seek(0)
        return notes
