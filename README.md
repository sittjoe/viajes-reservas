# Generador de itinerarios premium

Aplicación Flask que permite cargar referencias (PDF, texto, imágenes) y construir un itinerario de viaje con narrativa profesional. El resultado se muestra en HTML y puede descargarse en PDF.

## Requisitos

- Python 3.11+
- Dependencias listadas en `requirements.txt`

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Ejecución

```bash
flask --app app:create_app run --debug
```

Visita `http://localhost:5000` y completa el formulario:

1. Introduce datos del cliente, fechas y estilo de viaje.
2. Adjunta archivos PDF o texto con instrucciones o inspiraciones.
3. Envía el formulario para generar el itinerario.
4. Descarga el PDF con el botón "Descargar en PDF".

## Notas

- La extracción de texto soporta archivos PDF y TXT. Otros formatos se listan como referencia.
- Los itinerarios se mantienen en memoria solo durante la sesión del servidor.
- El PDF se genera con `reportlab` y replica la estructura mostrada en la versión HTML.
