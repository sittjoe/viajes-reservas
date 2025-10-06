"""Logic to transform client inputs and attachments into a structured itinerary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List

from .text_extractor import AttachmentSummary


@dataclass
class ItineraryRequest:
    """Structured data for requesting an itinerary generation."""

    client_name: str
    start_date: datetime
    end_date: datetime
    destination: str
    travel_style: str
    special_requests: str = ""


class ItineraryBuilder:
    """Create narrative itineraries using lightweight heuristics."""

    def build(
        self,
        request: ItineraryRequest,
        extracted_text: str,
        attachments: Iterable[AttachmentSummary],
    ) -> Dict:
        days = self._build_daily_schedule(request, extracted_text)

        recommendations = self._build_recommendations(request, extracted_text)
        attachments_info = [attachment.to_dict() for attachment in attachments]

        itinerary = {
            "client": {
                "name": request.client_name,
                "style": request.travel_style,
                "special_requests": request.special_requests,
            },
            "trip": {
                "destination": request.destination,
                "start_date": request.start_date.strftime("%d %B %Y"),
                "end_date": request.end_date.strftime("%d %B %Y"),
                "nights": (request.end_date - request.start_date).days + 1,
            },
            "days": days,
            "recommendations": recommendations,
            "attachments": attachments_info,
        }

        return itinerary

    def _build_daily_schedule(self, request: ItineraryRequest, extracted_text: str) -> List[Dict]:
        keywords = self._extract_keywords(extracted_text, request.destination)
        curated_highlights = self._curate_highlights(keywords, request.travel_style)

        total_days = (request.end_date - request.start_date).days + 1

        schedule = []
        for offset in range(total_days):
            current_date = request.start_date + timedelta(days=offset)
            highlight = curated_highlights[offset % len(curated_highlights)] if curated_highlights else "Exploración libre"

            schedule.append(
                {
                    "date": current_date.strftime("%A %d %B"),
                    "title": f"Día {offset + 1} - {highlight['title']}",
                    "summary": highlight["summary"],
                    "morning": highlight["morning"],
                    "afternoon": highlight["afternoon"],
                    "evening": highlight["evening"],
                }
            )

        return schedule

    def _build_recommendations(self, request: ItineraryRequest, extracted_text: str) -> Dict:
        base = {
            "gastronomy": [],
            "logistics": [],
            "wellness": [],
            "insider": [],
        }

        keywords = self._extract_keywords(extracted_text, request.destination)

        if "family" in keywords or "familia" in keywords:
            base["insider"].append("Reservar actividades con guía privado enfocado en familias para maximizar seguridad y aprendizaje.")
        if "negocio" in keywords or "corporativo" in keywords:
            base["logistics"].append("Incluir tiempos de traslado flexibles y salas de reuniones en cada hotel seleccionado.")
        if "gastronom" in "".join(keywords):
            base["gastronomy"].append("Coordinar experiencias culinarias con chefs locales y reservas anticipadas en restaurantes icónicos.")
        if request.travel_style.lower() in {"premium", "lujo", "luxury"}:
            base["wellness"].append("Añadir tratamientos de spa o rituales de bienestar exclusivos en los hoteles boutique seleccionados.")
        if request.special_requests:
            base["insider"].append(f"Considerar peticiones especiales: {request.special_requests}.")

        if not base["gastronomy"]:
            base["gastronomy"].append("Programar una cena de bienvenida con degustación regional y maridaje de vinos locales.")
        if not base["logistics"]:
            base["logistics"].append("Gestionar traslados privados puerta a puerta con asistencia multilingüe.")
        if not base["wellness"]:
            base["wellness"].append("Bloquear espacios de tiempo para actividades regenerativas como yoga al amanecer o masajes signature.")
        if not base["insider"]:
            base["insider"].append("Ofrecer un concierge 24/7 para ajustes de último minuto y acceso a experiencias exclusivas.")

        return base

    def _extract_keywords(self, extracted_text: str, destination: str) -> List[str]:
        tokens = {token.lower() for token in extracted_text.split() if len(token) > 3}
        tokens.add(destination.lower())
        return sorted(tokens)

    def _curate_highlights(self, keywords: Iterable[str], travel_style: str) -> List[Dict]:
        highlights: List[Dict] = []

        themes = [keyword for keyword in keywords if keyword in {"cultura", "gastronomía", "aventura", "relax", "arte", "historia"}]

        default_templates = [
            {
                "title": "Bienvenida y aclimatación",
                "summary": "Recepción personalizada, check-in express y recorrido de orientación por el hotel.",
                "morning": "Traslado privado y recepción con amenities premium.",
                "afternoon": "City tour introductorio con guía experto en español.",
                "evening": "Cena de autor con maridaje diseñado por el sommelier de la casa.",
            },
            {
                "title": "Cultura y patrimonio",
                "summary": "Acceso prioritario a museos icónicos y experiencias culturales privadas.",
                "morning": "Visita guiada antes de la apertura al público en el principal museo local.",
                "afternoon": "Encuentro con artesanos para un taller exclusivo detrás de bambalinas.",
                "evening": "Coctel en rooftop con vistas panorámicas y música en vivo.",
            },
            {
                "title": "Sabores locales",
                "summary": "Ruta gastronómica con maridajes y experiencias culinarias de autor.",
                "morning": "Clase de cocina con chef reconocido para aprender recetas tradicionales.",
                "afternoon": "Tour de mercados gourmet y degustación de productos de temporada.",
                "evening": "Reserva VIP en restaurante insignia con menú degustación sorpresa.",
            },
            {
                "title": "Bienestar y desconexión",
                "summary": "Jornada enfocada en bienestar holístico con tratamientos de spa signature.",
                "morning": "Sesión de yoga o meditación guiada al amanecer.",
                "afternoon": "Circuito de hidroterapia y masaje de autor en cabina privada.",
                "evening": "Cena ligera de inspiración healthy con mixología botánica.",
            },
        ]

        if themes:
            for theme in themes:
                if theme == "aventura":
                    highlights.append(
                        {
                            "title": "Aventura sob medida",
                            "summary": "Actividades outdoor con guías certificados y medidas de seguridad premium.",
                            "morning": "Exploración privada por senderos exclusivos con picnic gourmet.",
                            "afternoon": "Actividad adrenalínica como vuelo en helicóptero o navegación privada.",
                            "evening": "Fogata o cena temática con storytelling local y mixología artesanal.",
                        }
                    )
                elif theme == "cultura":
                    highlights.append(default_templates[1])
                elif theme == "gastronomía":
                    highlights.append(default_templates[2])
                elif theme == "relax":
                    highlights.append(default_templates[3])
                elif theme == "arte":
                    highlights.append(
                        {
                            "title": "Arte contemporáneo y clásico",
                            "summary": "Visitas privadas a galerías con curadores y coleccionistas.",
                            "morning": "Recorrido con curador por galerías emergentes.",
                            "afternoon": "Acceso a colección privada con anfitrión experto.",
                            "evening": "Cena temática rodeada de arte con menú inspirado en artistas locales.",
                        }
                    )
                elif theme == "historia":
                    highlights.append(
                        {
                            "title": "Historia viva",
                            "summary": "Rutas exclusivas por sitios patrimoniales con guía especializado.",
                            "morning": "Visita privada a monumentos antes del horario público.",
                            "afternoon": "Acceso a archivos históricos y encuentro con historiador local.",
                            "evening": "Cena en edificio histórico con iluminación especial y menú de época.",
                        }
                    )

        if not highlights:
            highlights = default_templates

        if travel_style.lower() in {"aventura", "experiencial"}:
            highlights = sorted(highlights, key=lambda item: "aventura" not in item["title"], reverse=False)

        return highlights
