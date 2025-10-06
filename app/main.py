"""Main routes for the travel itinerary application."""

from __future__ import annotations

import uuid
from datetime import datetime
from io import BytesIO
from typing import Dict

from flask import Blueprint, Response, flash, redirect, render_template, request, send_file, url_for
from werkzeug.datastructures import FileStorage

from .services.itinerary_builder import ItineraryBuilder, ItineraryRequest
from .services.text_extractor import AttachmentSummary, TextExtractor
from .services.pdf_renderer import PdfRenderer

main_bp = Blueprint("main", __name__)

# In-memory storage for generated itineraries. In a real application this would be persisted.
_GENERATED_ITINERARIES: Dict[str, Dict] = {}


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


@main_bp.route("/", methods=["GET"])
def index() -> str:
    """Render the landing page with the itinerary form."""
    return render_template("index.html")


@main_bp.route("/generate", methods=["POST"])
def generate_itinerary() -> str:
    """Create an itinerary using the submitted form and uploaded files."""
    form = request.form

    try:
        start_date = _parse_date(form["start_date"])
        end_date = _parse_date(form["end_date"])
    except (KeyError, ValueError):
        flash("Las fechas proporcionadas no son válidas. Usa el formato AAAA-MM-DD.", "error")
        return redirect(url_for("main.index"))

    if end_date < start_date:
        flash("La fecha de fin debe ser posterior a la fecha de inicio.", "error")
        return redirect(url_for("main.index"))

    client_name = form.get("client_name", "Cliente")
    primary_destination = form.get("primary_destination", "Destino principal")
    travel_style = form.get("travel_style", "Premium")
    special_requests = form.get("special_requests", "")

    uploaded_files = request.files.getlist("attachments")
    attachments = [file for file in uploaded_files if isinstance(file, FileStorage) and file.filename]

    extractor = TextExtractor()
    extracted_text, attachment_summaries = extractor.extract(attachments)

    builder = ItineraryBuilder()
    itinerary_request = ItineraryRequest(
        client_name=client_name,
        start_date=start_date,
        end_date=end_date,
        destination=primary_destination,
        travel_style=travel_style,
        special_requests=special_requests,
    )

    itinerary = builder.build(itinerary_request, extracted_text, attachment_summaries)

    itinerary_id = uuid.uuid4().hex
    _GENERATED_ITINERARIES[itinerary_id] = itinerary

    return render_template("itinerary.html", itinerary=itinerary, itinerary_id=itinerary_id)


@main_bp.route("/itinerary/<itinerary_id>/pdf", methods=["GET"])
def download_itinerary_pdf(itinerary_id: str) -> Response:
    """Return the generated itinerary as a PDF file."""
    itinerary = _GENERATED_ITINERARIES.get(itinerary_id)
    if not itinerary:
        flash("No se encontró el itinerario solicitado.", "error")
        return redirect(url_for("main.index"))

    pdf_renderer = PdfRenderer()
    pdf_bytes = pdf_renderer.render(itinerary)

    buffer = BytesIO(pdf_bytes)
    filename = f"itinerario_{itinerary['client']['name'].replace(' ', '_').lower()}.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


@main_bp.app_errorhandler(500)
def handle_server_error(error):  # type: ignore[override]
    return render_template("error.html", error_message=str(error)), 500


@main_bp.app_errorhandler(404)
def handle_not_found(error):  # type: ignore[override]
    return render_template("error.html", error_message="Página no encontrada"), 404
