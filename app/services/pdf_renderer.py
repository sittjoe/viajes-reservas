"""Render itinerary dictionaries into PDF documents."""

from __future__ import annotations

from io import BytesIO
from typing import Dict, Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle


def _build_styles() -> Dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Heading1Alt", parent=styles["Heading1"], fontSize=18, leading=22, spaceAfter=12))
    styles.add(ParagraphStyle(name="Heading2Alt", parent=styles["Heading2"], fontSize=14, leading=18, spaceBefore=18, spaceAfter=8))
    styles.add(ParagraphStyle(name="BodyAlt", parent=styles["BodyText"], leading=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=11, textColor=colors.grey))
    return styles


class PdfRenderer:
    """Create a professional PDF representation of the itinerary."""

    def __init__(self) -> None:
        self.styles = _build_styles()

    def render(self, itinerary: Dict) -> bytes:
        buffer = BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=A4, title="Itinerario de viaje")

        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
        doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])

        story = []
        story.extend(self._build_header(itinerary))
        story.extend(self._build_day_by_day(itinerary))
        story.extend(self._build_recommendations(itinerary))
        story.extend(self._build_attachments(itinerary))

        doc.build(story)
        return buffer.getvalue()

    def _build_header(self, itinerary: Dict) -> Iterable:
        story = [Paragraph("Plan Maestro de Viaje", self.styles["Heading1Alt"])]

        client = itinerary["client"]
        trip = itinerary["trip"]

        summary_table = Table(
            [
                ["Cliente", client["name"], "Estilo", client["style"]],
                ["Destino", trip["destination"], "Duración", f"{trip['nights']} noches"],
                ["Fechas", f"{trip['start_date']} - {trip['end_date']}", "Peticiones", client["special_requests"] or "N/A"],
            ],
            colWidths=[3 * cm, 6 * cm, 3 * cm, 6 * cm],
            hAlign="LEFT",
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 12))
        story.append(Paragraph("Resumen ejecutivo", self.styles["Heading2Alt"]))
        story.append(
            Paragraph(
                "Este documento reúne un programa integral con experiencias personalizadas, logística minuciosa y recomendaciones premium para garantizar un viaje impecable.",
                self.styles["BodyAlt"],
            )
        )
        return story

    def _build_day_by_day(self, itinerary: Dict) -> Iterable:
        story = [Paragraph("Agenda día por día", self.styles["Heading2Alt"])]

        for day in itinerary["days"]:
            story.append(Paragraph(day["title"], self.styles["Heading3"]))
            story.append(Paragraph(day["summary"], self.styles["BodyAlt"]))

            table = Table(
                [
                    ["Mañana", day["morning"]],
                    ["Tarde", day["afternoon"]],
                    ["Noche", day["evening"]],
                ],
                colWidths=[4 * cm, 12 * cm],
                hAlign="LEFT",
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 12))

        return story

    def _build_recommendations(self, itinerary: Dict) -> Iterable:
        story = [Paragraph("Recomendaciones estratégicas", self.styles["Heading2Alt"])]
        recommendations = itinerary["recommendations"]
        for section, items in recommendations.items():
            story.append(Paragraph(section.capitalize(), self.styles["Heading3"]))
            for item in items:
                story.append(Paragraph(f"• {item}", self.styles["BodyAlt"]))
        story.append(Spacer(1, 12))
        return story

    def _build_attachments(self, itinerary: Dict) -> Iterable:
        attachments = itinerary.get("attachments", [])
        if not attachments:
            return []

        story = [Paragraph("Documentos recibidos", self.styles["Heading2Alt"])]
        rows = [["Archivo", "Tipo", "Notas"]]
        for attachment in attachments:
            rows.append([attachment["filename"], attachment["content_type"], attachment["notes"]])

        table = Table(rows, colWidths=[6 * cm, 4 * cm, 6 * cm], hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
        return story
