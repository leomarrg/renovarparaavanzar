#!/usr/bin/env python
"""
Script para envío masivo de emails usando SendGrid API.
Mucho más rápido y confiable que Gmail SMTP.
"""

import os
import sys
import django
import time
from datetime import datetime
from pathlib import Path

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.conf import settings

# Intentar importar SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content, Category, Attachment, FileContent, FileName, FileType, Disposition
    import base64
except ImportError:
    print("ERROR: SendGrid no está instalado.")
    print("Ejecuta: pip install sendgrid")
    sys.exit(1)

# Configuración
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'registro@renovarparaavanzar.com')
SITE_URL = settings.SITE_URL
LOGO_URL = f"{SITE_URL}/static/landing/img/email/DR_x_RPA@4x.png"
DOCTOR_PHOTO_URL = f"{SITE_URL}/static/landing/img/dr_cutout.png"
DOCTOR_TUX_URL = f"{SITE_URL}/static/landing/img/dr_tux.jpg"
BALA1_NUEVODIA_URL = f"{SITE_URL}/static/landing/img/email/balas/bala1_nuevodia.jpg"
BALA1_NUEVODIA_PT2_URL = f"{SITE_URL}/static/landing/img/email/balas/bala_1_nuevodia_pt2.jpg"
FECHAS_VOTACION_URL = f"{SITE_URL}/static/landing/img/email/fechas_votacion.jpg"
VOTA_2_URL = f"{SITE_URL}/static/landing/img/email/Vota_num2.jpg"
UNSUBSCRIBE_URL = f"{SITE_URL}/unsubscribe/"

# Configuración de envío
BATCH_SIZE = 100  # SendGrid puede manejar más
PAUSE_BETWEEN_BATCHES = 30  # Menos pausa necesaria con SendGrid
DELAY_BETWEEN_EMAILS = 0.1  # SendGrid es más rápido


class SendGridEmailSender:
    """
    Clase para enviar emails masivos con SendGrid.
    """

    def __init__(self, email_type='frente_comun'):
        """
        Inicializa el cliente de SendGrid.

        Args:
            email_type: 'frente_comun' o 'encuesta'
        """
        if not SENDGRID_API_KEY:
            print("ERROR: SENDGRID_API_KEY no está configurado.")
            print("Configura la variable de entorno:")
            print("  export SENDGRID_API_KEY='SG.xxxxx.yyyyy'")
            sys.exit(1)

        self.sg = SendGridAPIClient(SENDGRID_API_KEY)
        self.email_type = email_type

    def generate_frente_comun_html(self, nombre_completo, email_destinatario):
        """Genera HTML para email 'Un frente común'."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Un frente común por la clase médica</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Forzar colores en dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #377e7c !important;
                color: white !important;
            }}
            .container {{
                background-color: #377e7c !important;
            }}
            .header {{
                background-color: #377e7c !important;
            }}
            .content {{
                background-color: #377e7c !important;
            }}
            .footer {{
                background-color: #2a615f !important;
            }}
        }}

        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #377e7c !important;
            color: white !important;
            -webkit-text-size-adjust: 100%;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #377e7c !important;
        }}
        .header {{
            background-color: #377e7c !important;
            padding: 40px 30px;
            text-align: center;
        }}
        .header img {{
            max-width: 250px;
            height: auto;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: white !important;
            font-size: 28px;
            margin: 0;
            font-weight: 700;
            line-height: 1.3;
            font-family: 'Montserrat', sans-serif;
        }}
        .doctor-photo {{
            max-width: 300px;
            width: 100%;
            height: auto;
            margin: 20px auto 5px auto;
            display: block;
            border-radius: 10px;
        }}
        .content {{
            padding: 5px 30px 40px 30px;
            background-color: #377e7c !important;
        }}
        .greeting {{
            font-size: 20px;
            color: white !important;
            margin-bottom: 25px;
            font-weight: 600;
            font-family: 'Montserrat', sans-serif;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.8;
            color: white !important;
            margin-bottom: 25px;
            font-family: 'Montserrat', sans-serif;
        }}
        .message strong {{
            color: white !important;
            font-weight: 700;
        }}
        .highlight {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            padding: 25px;
            border-left: 4px solid white;
            margin: 30px 0;
            border-radius: 5px;
        }}
        .highlight p {{
            margin: 0;
            font-size: 17px;
            color: white !important;
            line-height: 1.6;
            font-weight: 500;
            font-family: 'Montserrat', sans-serif;
        }}
        .cta-section {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            padding: 30px;
            text-align: center;
            margin: 30px 0;
            border-radius: 8px;
            border: 2px solid white;
        }}
        .cta-text {{
            font-size: 24px;
            color: white !important;
            font-weight: 700;
            margin: 20px 0;
            font-family: 'Montserrat', sans-serif;
        }}
        .hashtag {{
            font-size: 22px;
            color: white !important;
            font-weight: 700;
            margin-top: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer {{
            background-color: #2a615f !important;
            color: white !important;
            padding: 30px;
            text-align: center;
        }}
        .footer-content {{
            margin-bottom: 20px;
        }}
        .footer-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 10px;
            color: white !important;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer-subtitle {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9) !important;
            margin-bottom: 10px;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe {{
            margin-top: 20px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8) !important;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe a {{
            color: white !important;
            text-decoration: underline;
        }}
        .legal {{
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7) !important;
            margin-top: 15px;
            font-family: 'Montserrat', sans-serif;
        }}
        .signature {{
            text-align: center;
            padding: 25px;
            font-style: italic;
            color: white !important;
            font-size: 18px;
            font-weight: 500;
            background-color: rgba(255, 255, 255, 0.1) !important;
            font-family: 'Montserrat', sans-serif;
        }}

        /* Gmail dark mode específico */
        [data-ogsc] body {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .container {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .header {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .content {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .footer {{
            background-color: #2a615f !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{LOGO_URL}" alt="Renovar para Avanzar" />
            <h1>Un frente común por la clase médica</h1>
            <img src="{DOCTOR_TUX_URL}" alt="Dr. Méndez Sexto" class="doctor-photo" />
        </div>

        <div class="content">
            <p class="greeting">Estimado colega,</p>

            <p class="message">
                <strong>No más promesas vacías ni comités sin resultados.</strong> Es momento de
                unirnos en un frente común para poner fin al dilema de los planes médicos y
                lograr incentivos contributivos que hagan justicia a nuestra clase médica.
            </p>

            <div class="highlight">
                <p>
                    El Dr. Méndez Sexto y su equipo representan una nueva visión:
                    <strong>resultados reales, diálogo efectivo y una defensa firme</strong>
                    en favor de los médicos y la salud de Puerto Rico.
                </p>
            </div>

            <p class="message">
                Te invitamos a ser parte del cambio.
            </p>

            <div class="cta-section">
                <p class="cta-text">
                    Vota por el Dr. Méndez Sexto y su equipo
                </p>
                <p class="hashtag">#RenovarParaAvanzar</p>
            </div>
        </div>

        <div class="signature">
            "Juntos renovamos, juntos avanzamos"
        </div>

        <div class="footer">
            <div class="footer-content">
                <div class="footer-title">Dr. Méndez Sexto</div>
                <div class="footer-subtitle">Candidato a la Presidencia del Colegio de Médicos</div>
                <div class="footer-subtitle">#RenovarParaAvanzar</div>
            </div>

            <div class="legal">
                Pagado por el Comité Dr. Méndez Sexto
            </div>

            <div class="unsubscribe">
                Si no deseas recibir más comunicaciones, puedes
                <a href="https://www.renovarparaavanzar.com/unsubscribe/?email={email_destinatario}">
                    darte de baja aquí
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def generate_planes_medicos_html(self, nombre_completo, email_destinatario):
        """Genera HTML para email sobre Planes Médicos."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Los planes médicos no pueden seguir dictando nuestra práctica</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Forzar colores en dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #377e7c !important;
                color: white !important;
            }}
            .container {{
                background-color: #377e7c !important;
            }}
            .header {{
                background-color: #377e7c !important;
            }}
            .content {{
                background-color: #377e7c !important;
            }}
            .footer {{
                background-color: #2a615f !important;
            }}
        }}

        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #377e7c !important;
            color: white !important;
            -webkit-text-size-adjust: 100%;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #377e7c !important;
        }}
        .header {{
            background-color: #377e7c !important;
            padding: 40px 30px;
            text-align: center;
        }}
        .header img {{
            max-width: 250px;
            height: auto;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: white !important;
            font-size: 26px;
            margin: 0;
            font-weight: 700;
            line-height: 1.3;
            font-family: 'Montserrat', sans-serif;
        }}
        .doctor-photo {{
            max-width: 300px;
            width: 100%;
            height: auto;
            margin: 20px auto 5px auto;
            display: block;
            border-radius: 10px;
        }}
        .content {{
            padding: 5px 30px 40px 30px;
            background-color: #377e7c !important;
        }}
        .greeting {{
            font-size: 20px;
            color: white !important;
            margin-bottom: 25px;
            font-weight: 600;
            font-family: 'Montserrat', sans-serif;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.8;
            color: white !important;
            margin-bottom: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .message strong {{
            font-weight: 700;
            color: white !important;
        }}
        .highlight {{
            margin: 25px 0;
            padding-left: 15px;
            border-left: 3px solid rgba(255, 255, 255, 0.4);
        }}
        .highlight p {{
            margin: 0;
            font-size: 16px;
            line-height: 1.7;
            color: white !important;
            font-family: 'Montserrat', sans-serif;
        }}
        .simple-link {{
            color: white !important;
            text-decoration: underline;
            font-weight: 600;
        }}
        .footer {{
            background-color: #2a615f !important;
            padding: 30px;
            text-align: center;
            border-top: 2px solid rgba(255, 255, 255, 0.2);
        }}
        .footer-title {{
            color: white !important;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 5px;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer-subtitle {{
            color: rgba(255, 255, 255, 0.7) !important;
            font-size: 14px;
            margin: 5px 0;
            font-family: 'Montserrat', sans-serif;
        }}
        .legal {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6) !important;
            margin-top: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7) !important;
            margin-top: 15px;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe a {{
            color: white !important;
            text-decoration: underline;
        }}

        /* Gmail dark mode específico */
        [data-ogsc] body {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .container {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .header {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .content {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .footer {{
            background-color: #2a615f !important;
        }}
    </style>
</head>
<body style="background-color: #377e7c !important; color: white !important;">
    <div class="container" style="background-color: #377e7c !important;">
        <div class="header" style="background-color: #377e7c !important;">
            <img src="{LOGO_URL}" alt="Renovar para Avanzar" />
            <h1 style="color: white !important;">Los planes médicos no pueden seguir dictando nuestra práctica</h1>
            <img src="{DOCTOR_TUX_URL}" alt="Dr. Méndez Sexto" class="doctor-photo" />
        </div>

        <div class="content" style="background-color: #377e7c !important;">
            <p class="greeting" style="color: white !important;">Estimado colega:</p>

            <p class="message" style="color: white !important;">
                Durante años, hemos trabajado bajo tarifas injustas, pagos tardíos y denegaciones arbitrarias.
                El Colegio se ha limitado a quejarse sin lograr un solo cambio concreto.
            </p>

            <p class="message" style="color: white !important;">
                La clase médica merece representación real, no comunicados vacíos.
            </p>

            <div class="highlight">
                <p style="color: white !important;">
                    El Dr. Ramón Méndez Sexto entiende cómo se defienden los intereses de los médicos:
                    con seriedad, credibilidad y estrategia. Su liderazgo devolverá la voz del médico
                    a las mesas donde se decide nuestro valor profesional.
                </p>
            </div>

            <p class="message" style="color: white !important;">
                Vota por el Dr. Ramón Méndez Sexto y recuperemos la fuerza frente a los planes médicos.
            </p>

            <p class="message" style="color: white !important;">
                Conoce más sobre la propuesta en <a href="https://www.renovarparaavanzar.com" class="simple-link" style="color: white !important; text-decoration: underline;">www.renovarparaavanzar.com</a>
            </p>

            <p class="message" style="color: white !important;">
                Atentamente,<br>
                Comité Dr. Méndez Sexto
            </p>
        </div>

        <div class="footer">
            <div class="footer-title">Dr. Ramón Méndez Sexto</div>
            <div class="footer-subtitle">Candidato a la Presidencia del Colegio de Médicos</div>
            <div class="footer-subtitle">#RenovarParaAvanzar</div>

            <div class="legal">
                Pagado por el Comité Dr. Méndez Sexto
            </div>

            <div class="unsubscribe">
                Si no deseas recibir más comunicaciones, puedes
                <a href="https://www.renovarparaavanzar.com/unsubscribe/?email={email_destinatario}">
                    darte de baja aquí
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def generate_liderazgo_resultados_html(self, nombre_completo, email_destinatario):
        """Genera HTML para email sobre liderazgo con resultados."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>La clase médica necesita liderazgo con resultados</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Forzar colores en dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #21211f !important;
                color: white !important;
            }}
            .container {{
                background-color: #21211f !important;
            }}
            .header {{
                background-color: #21211f !important;
            }}
            .content {{
                background-color: #21211f !important;
            }}
            .footer {{
                background-color: #1a1a18 !important;
            }}
        }}

        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: transparent !important;
            -webkit-text-size-adjust: 100%;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: transparent !important;
            border: 2px solid #21211f !important;
            border-radius: 8px;
        }}
        .header {{
            background-color: transparent !important;
            padding: 40px 30px 20px 30px;
            text-align: center;
        }}
        .header img {{
            max-width: 250px;
            height: auto;
            margin-bottom: 20px;
        }}
        .content {{
            padding: 20px 30px 40px 30px;
            background-color: transparent !important;
        }}
        .message {{
            font-size: 18px;
            line-height: 1.6;
            color: #21211f !important;
            margin-bottom: 30px;
            font-family: 'Montserrat', sans-serif;
            text-align: center;
            font-weight: 500;
        }}
        .image-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .image-container img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto 20px auto;
            border-radius: 5px;
        }}
        .footer {{
            background-color: transparent !important;
            padding: 30px;
            text-align: center;
            border-top: 2px solid #21211f;
        }}
        .footer-title {{
            color: #21211f !important;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer-subtitle {{
            color: #333333 !important;
            font-size: 14px;
            margin-bottom: 5px;
            font-family: 'Montserrat', sans-serif;
        }}
        .legal {{
            color: #666666 !important;
            font-size: 11px;
            margin-top: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe {{
            margin-top: 20px;
            font-size: 11px;
            color: #666666 !important;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe a {{
            color: #333333 !important;
            text-decoration: underline;
        }}

        @media only screen and (max-width: 600px) {{
            body {{
                background-color: transparent !important;
            }}
            .container {{
                background-color: transparent !important;
            }}
            .header {{
                padding: 30px 20px 15px 20px;
                background-color: transparent !important;
            }}
            .content {{
                padding: 15px 20px 30px 20px;
                background-color: transparent !important;
            }}
            .message {{
                font-size: 16px;
                color: #000000 !important;
            }}
            .footer {{
                padding: 25px 20px;
                background-color: transparent !important;
            }}
            .footer-title {{
                color: #000000 !important;
            }}
            .footer-subtitle {{
                color: #333333 !important;
            }}
            .legal {{
                color: #666666 !important;
            }}
            .unsubscribe {{
                color: #666666 !important;
            }}
            .unsubscribe a {{
                color: #333333 !important;
            }}
        }}
    </style>
</head>
<body style="background-color: transparent !important; padding: 20px;">
    <div class="container" style="background-color: transparent !important; border: 2px solid #21211f !important; border-radius: 8px;">
        <div class="content" style="background-color: transparent !important; padding-top: 40px;">
            <p class="message" style="color: #21211f !important;">
                Es momento de reconocer lo evidente: la clase médica necesita liderazgo con resultados, no con permanencia.
            </p>

            <div class="image-container">
                <img src="{BALA1_NUEVODIA_URL}" alt="Liderazgo con resultados" />
                <img src="{BALA1_NUEVODIA_PT2_URL}" alt="Liderazgo con resultados" />
            </div>
        </div>

        <div class="footer" style="background-color: transparent !important; border-top: 2px solid #21211f;">
            <div class="footer-title" style="color: #21211f !important;">Dr. Ramón Méndez Sexto</div>
            <div class="footer-subtitle" style="color: #333333 !important;">Candidato a la Presidencia del Colegio de Médicos</div>
            <div class="footer-subtitle" style="color: #333333 !important;">#RenovarParaAvanzar</div>

            <div class="legal" style="color: #666666 !important;">
                Pagado por el Comité Dr. Méndez Sexto
            </div>

            <div class="unsubscribe" style="color: #666666 !important;">
                Si no deseas recibir más comunicaciones, puedes
                <a href="https://www.renovarparaavanzar.com/unsubscribe/?email={email_destinatario}" style="color: #333333 !important; text-decoration: underline;">
                    darte de baja aquí
                </a>.
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def generate_fechas_votacion_html(self, nombre_completo, email_destinatario):
        """Genera HTML para email sobre fechas de votación."""
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vota #2 por nuestro equipo — Conoce las fechas</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #ffffff;
            -webkit-text-size-adjust: 100%;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: transparent;
            border: 2px solid #377e7c;
            border-radius: 8px;
        }}
        .content {{
            padding: 40px 30px 40px 30px;
            background-color: transparent;
        }}
        .greeting {{
            font-size: 18px;
            color: #333333;
            margin-bottom: 20px;
            font-family: 'Montserrat', sans-serif;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.7;
            color: #333333;
            margin-bottom: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .message strong {{
            font-weight: 700;
            color: #377e7c;
        }}
        .voting-dates {{
            margin: 30px 0;
            padding: 20px;
            background-color: rgba(55, 126, 124, 0.05);
            border: 1px solid #377e7c;
            border-radius: 5px;
        }}
        .date-block {{
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(55, 126, 124, 0.3);
        }}
        .date-block:last-child {{
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }}
        .date-title {{
            font-size: 16px;
            font-weight: 700;
            color: #377e7c;
            margin-bottom: 5px;
            font-family: 'Montserrat', sans-serif;
        }}
        .date-detail {{
            font-size: 14px;
            color: #666666;
            font-family: 'Montserrat', sans-serif;
        }}
        .image-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .image-container img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
            border-radius: 5px;
        }}
        .hashtag {{
            font-size: 18px;
            font-weight: 700;
            color: #377e7c;
            margin-top: 30px;
            text-align: center;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer {{
            background-color: rgba(55, 126, 124, 0.05);
            padding: 30px;
            text-align: center;
            border-top: 2px solid #377e7c;
        }}
        .footer-title {{
            color: #377e7c;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 8px;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer-subtitle {{
            color: #666666;
            font-size: 14px;
            margin-bottom: 5px;
            font-family: 'Montserrat', sans-serif;
        }}
        .legal {{
            color: #999999;
            font-size: 11px;
            margin-top: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe {{
            margin-top: 20px;
            font-size: 11px;
            color: #999999;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe a {{
            color: #377e7c;
            text-decoration: underline;
        }}

        @media only screen and (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .message {{
                font-size: 15px;
            }}
            .footer {{
                padding: 25px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <p class="greeting">Estimado colega:</p>

            <p class="message">
                Las elecciones para la presidencia del Colegio de Médicos Cirujanos de Puerto Rico ya están aquí.
            </p>

            <p class="message">
                Tienes tres formas de ejercer tu voto:
            </p>

            <div class="voting-dates">
                <div class="date-block">
                    <div class="date-title">24 - 26 de noviembre</div>
                    <div class="date-detail">En las oficinas del Colegio (voto en papeleta)</div>
                </div>

                <div class="date-block">
                    <div class="date-title">27 de noviembre al 11 de diciembre</div>
                    <div class="date-detail">Voto electrónico</div>
                </div>

                <div class="date-block">
                    <div class="date-title">12 - 13 de diciembre</div>
                    <div class="date-detail">En Convención (voto en papeleta)</div>
                </div>
            </div>

            <div class="image-container">
                <img src="{FECHAS_VOTACION_URL}" alt="Fechas de votación" />
            </div>

            <p class="message">
                Vota #2 por nuestro equipo para renovar el liderazgo del Colegio.
            </p>

            <p class="hashtag">#RenovarParaAvanzar</p>
        </div>

        <div class="footer">
            <div class="footer-title">Dr. Ramón Méndez Sexto</div>
            <div class="footer-subtitle">Candidato a la Presidencia del Colegio de Médicos</div>
            <div class="footer-subtitle">#RenovarParaAvanzar</div>

            <div class="legal">
                Pagado por el Comité Dr. Méndez Sexto
            </div>

            <div class="unsubscribe">
                Si no deseas recibir más comunicaciones, puedes
                <a href="https://www.renovarparaavanzar.com/unsubscribe/?email={email_destinatario}">
                    darte de baja aquí
                </a>.
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def generate_renovacion_html(self, nombre_completo, email_destinatario):
        """
        Genera el HTML para el email de renovación con las 2 imágenes del equipo #2
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Renovar para Avanzar - Dr. Méndez Sexto</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: transparent;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: transparent;">
        <tr>
            <td style="padding: 20px 0;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; background-color: #ffffff; border: 3px solid #008B8B; border-radius: 10px;">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center; background: linear-gradient(135deg, #008B8B 0%, #20B2AA 100%); border-radius: 7px 7px 0 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                                ¡Saludos!
                            </h1>
                        </td>
                    </tr>

                    <!-- Contenido Principal -->
                    <tr>
                        <td style="padding: 40px 30px; color: #000000;">
                            <p style="font-size: 18px; line-height: 1.6; margin: 0 0 20px 0; color: #000000;">
                                Soy el Dr. Ramón Méndez Sexto y juntos tenemos una cita para iniciar la renovación del Colegio de Médicos y Cirujanos.
                            </p>

                            <p style="font-size: 18px; line-height: 1.6; margin: 20px 0; font-weight: bold; color: #008B8B;">
                                Es tiempo de lograr justicia verdadera frente a los planes médicos.
                            </p>

                            <p style="font-size: 18px; line-height: 1.6; margin: 20px 0; font-weight: bold; color: #008B8B;">
                                Es tiempo de recuperar credibilidad frente a las instituciones y el Gobierno.
                            </p>

                            <p style="font-size: 18px; line-height: 1.6; margin: 20px 0; font-weight: bold; color: #008B8B;">
                                Es tiempo de recuperar tú voz y adelantar tú agenda, la de todos los médicos.
                            </p>
                        </td>
                    </tr>

                    <!-- Imagen Vota #2 -->
                    <tr>
                        <td style="padding: 20px 30px; text-align: center;">
                            <img src="{VOTA_2_URL}" alt="Vota por el equipo #2" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />
                        </td>
                    </tr>

                    <!-- Imagen Fechas de Votación -->
                    <tr>
                        <td style="padding: 20px 30px; text-align: center;">
                            <img src="{FECHAS_VOTACION_URL}" alt="Fechas de Votación" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />
                        </td>
                    </tr>

                    <!-- Call to Action -->
                    <tr>
                        <td style="padding: 30px; text-align: center; background-color: #f8f8f8;">
                            <p style="font-size: 22px; font-weight: bold; color: #008B8B; margin: 0 0 20px 0;">
                                Vota por la renovación, por el equipo #2
                            </p>
                            <p style="font-size: 16px; color: #000000; margin: 10px 0;">
                                #RenovarParaAvanzar
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px; text-align: center; background-color: #008B8B; border-radius: 0 0 7px 7px;">
                            <p style="color: #ffffff; font-size: 14px; margin: 5px 0;">
                                Dr. Ramón Méndez Sexto
                            </p>
                            <p style="color: #ffffff; font-size: 14px; margin: 5px 0;">
                                Candidato a la Presidencia del Colegio de Médicos y Cirujanos
                            </p>
                            <p style="color: #ffffff; font-size: 12px; margin: 15px 0 5px 0;">
                                Pagado por el Comité Dr. Méndez Sexto
                            </p>
                            <p style="color: #ffffff; font-size: 11px; margin: 15px 0 0 0;">
                                Para dejar de recibir emails, haz <a href="{UNSUBSCRIBE_URL}?email={email_destinatario}" style="color: #ffffff; text-decoration: underline;">clic aquí</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html_content

    def send_email(self, to_email, subject, html_content, nombre_completo, attachment_path=None):
        """
        Envía un email usando SendGrid API con mejores prácticas anti-spam.

        Args:
            to_email: Email destinatario
            subject: Asunto del email
            html_content: Contenido HTML
            nombre_completo: Nombre del destinatario
            attachment_path: Ruta opcional a un archivo PDF para adjuntar
        """
        try:
            # Crear texto plano simple
            text_content = f"""
Estimado colega,

No más promesas vacías ni comités sin resultados. Es momento de unirnos en un frente común.

El Dr. Méndez Sexto y su equipo representan una nueva visión: resultados reales, diálogo efectivo y una defensa firme.

Te invitamos a ser parte del cambio.

¡Vota por el Dr. Méndez Sexto y su equipo!

#RenovarParaAvanzar

---
Dr. Méndez Sexto
Candidato a la Presidencia del Colegio de Médicos

Pagado por el Comité Dr. Méndez Sexto

Si deseas dejar de recibir emails, responde con "BAJA" a support@renovarparaavanzar.com
"""

            message = Mail(
                from_email=(FROM_EMAIL, 'Dr. Méndez Sexto - Renovar para Avanzar'),
                to_emails=to_email,
                subject=subject,
                plain_text_content=text_content,
                html_content=html_content
            )

            # Configurar Reply-To
            message.reply_to = 'support@renovarparaavanzar.com'

            # Agregar categorías para tracking
            message.add_category(Category('frente_comun'))
            message.add_category(Category('campana_2024'))

            # Agregar adjunto si se proporcionó
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    data = f.read()
                    encoded_file = base64.b64encode(data).decode()

                # Obtener nombre del archivo
                file_name = os.path.basename(attachment_path)

                # Crear objeto Attachment
                attached_file = Attachment(
                    FileContent(encoded_file),
                    FileName(file_name),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                message.attachment = attached_file

            # Enviar
            response = self.sg.send(message)

            # SendGrid devuelve 202 si fue aceptado
            if response.status_code in [200, 201, 202]:
                return True, "Enviado"
            else:
                return False, f"Status {response.status_code}"

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"\nError detallado:\n{error_detail}")
            return False, str(e)

    def send_batch(self, registrations, subject, attachment_path=None):
        """
        Envía un lote de emails.

        Args:
            registrations: Lista de objetos Registration
            subject: Asunto del email
            attachment_path: Ruta opcional a un archivo PDF para adjuntar
        """
        exitosos = 0
        fallidos = 0
        errores = []

        for i, reg in enumerate(registrations, 1):
            nombre_completo = f"{reg.name} {reg.last_name}".strip()
            if not nombre_completo or nombre_completo == " ":
                nombre_completo = "Estimado/a colega"

            print(f"  [{i}/{len(registrations)}] {reg.email} ({nombre_completo})... ", end="", flush=True)

            # Generar HTML según el tipo de email
            if self.email_type == 'planes_medicos':
                html_content = self.generate_planes_medicos_html(nombre_completo, reg.email)
            elif self.email_type == 'liderazgo_resultados':
                html_content = self.generate_liderazgo_resultados_html(nombre_completo, reg.email)
            elif self.email_type == 'fechas_votacion':
                html_content = self.generate_fechas_votacion_html(nombre_completo, reg.email)
            elif self.email_type == 'renovacion':
                html_content = self.generate_renovacion_html(nombre_completo, reg.email)
            else:
                html_content = self.generate_frente_comun_html(nombre_completo, reg.email)

            # Enviar
            success, message = self.send_email(reg.email, subject, html_content, nombre_completo, attachment_path)

            if success:
                print("[OK]")
                exitosos += 1
            else:
                print(f"[FALLO]")
                fallidos += 1
                errores.append({'email': reg.email, 'error': message})

            # Pequeña pausa (SendGrid es rápido)
            if i < len(registrations):
                time.sleep(DELAY_BETWEEN_EMAILS)

        return exitosos, fallidos, errores


def send_mass_email_sendgrid(batch_size=100, pause=30, limit=None, offset=0, attachment_path=None, email_type='frente_comun'):
    """
    Envía emails masivos usando SendGrid.

    Args:
        batch_size: Cantidad de emails por lote
        pause: Pausa en segundos entre lotes
        limit: Límite opcional de emails a enviar
        offset: Offset para empezar desde un registro específico
        attachment_path: Ruta opcional a un archivo PDF para adjuntar
        email_type: Tipo de email ('frente_comun' o 'planes_medicos')
    """
    print("=" * 60)
    print("ENVÍO MASIVO CON SENDGRID")
    print("=" * 60)
    print()

    # Inicializar SendGrid
    sender = SendGridEmailSender(email_type=email_type)

    # Obtener registros (excluir usuarios que se dieron de baja)
    registrations = Registration.objects.filter(
        email__isnull=False,
        unsubscribed=False  # Solo enviar a usuarios suscritos
    ).exclude(
        email__exact=''
    ).order_by('id')

    if offset > 0:
        registrations = registrations[offset:]

    if limit:
        registrations = registrations[:limit]

    total = registrations.count()

    print(f"Total de emails a enviar: {total}")
    print(f"Tamaño de lote: {batch_size}")
    print(f"Pausa entre lotes: {pause} segundos")
    print()

    # Calcular tiempo estimado
    batches = (total + batch_size - 1) // batch_size
    tiempo_total = (total * DELAY_BETWEEN_EMAILS + (batches - 1) * pause) / 60

    print(f"Tiempo estimado: {tiempo_total:.1f} minutos ({tiempo_total/60:.1f} horas)")
    print()

    print("¿Confirmas el envío? (escribe SI):")
    if input().strip().upper() != 'SI':
        print("Envío cancelado.")
        return

    # Enviar
    start_time = time.time()
    total_exitosos = 0
    total_fallidos = 0
    all_errores = []

    registrations_list = list(registrations)

    for batch_num in range(0, len(registrations_list), batch_size):
        batch_end = min(batch_num + batch_size, len(registrations_list))
        batch = registrations_list[batch_num:batch_end]

        current_batch = (batch_num // batch_size) + 1
        total_batches = (len(registrations_list) + batch_size - 1) // batch_size

        print(f"\nLOTE {current_batch}/{total_batches} - Emails {batch_num + 1} a {batch_end}")
        print("-" * 40)

        # Definir subject según el tipo de email
        if email_type == 'planes_medicos':
            subject = 'Los planes médicos no pueden seguir dictando nuestra práctica'
        elif email_type == 'liderazgo_resultados':
            subject = 'La clase médica necesita liderazgo con resultados'
        elif email_type == 'fechas_votacion':
            subject = 'Vota #2 por nuestro equipo — Conoce las fechas'
        elif email_type == 'renovacion':
            subject = 'Es tiempo de renovar el Colegio de Médicos — Vota #2'
        else:
            subject = 'Un frente común por la clase médica — ¡Renovar para avanzar!'

        exitosos, fallidos, errores = sender.send_batch(
            batch,
            subject,
            attachment_path
        )

        total_exitosos += exitosos
        total_fallidos += fallidos
        all_errores.extend(errores)

        print(f"\nLote {current_batch} completado: {exitosos} enviados, {fallidos} fallidos")
        print(f"Acumulado: {total_exitosos} enviados, {total_fallidos} fallidos")

        # Pausa entre lotes
        if batch_end < len(registrations_list):
            print(f"\nPausando {pause} segundos...")
            time.sleep(pause)

    # Resumen
    elapsed = (time.time() - start_time) / 60
    offset_final = offset + len(registrations_list)

    print()
    print("=" * 60)
    print("RESUMEN DE ENVÍO")
    print("=" * 60)
    print(f"Offset inicial: {offset}")
    print(f"Offset final: {offset_final}")
    print(f"Total procesados: {total_exitosos + total_fallidos}")
    print(f"Enviados: {total_exitosos}")
    print(f"Fallidos: {total_fallidos}")
    print(f"Tasa de éxito: {(total_exitosos / (total_exitosos + total_fallidos) * 100):.1f}%")
    print(f"Tiempo: {elapsed:.1f} minutos")
    print()
    print(f">>> PRÓXIMO COMANDO: python send_email_sendgrid.py --offset {offset_final} --limit 3000 --batch-size 500 --pause 600 --email-type {email_type}")
    print()

    # Guardar reporte completo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"sendgrid_report_{timestamp}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("REPORTE DE ENVÍO MASIVO - SENDGRID\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tipo de email: {email_type}\n")
        f.write(f"Subject: {subject}\n")
        f.write(f"Offset inicial: {offset}\n")
        f.write(f"Offset final: {offset_final}\n")
        f.write(f"Límite de envío: {limit if limit else 'Sin límite'}\n")
        f.write(f"Tamaño de lote: {batch_size}\n")
        f.write(f"Pausa entre lotes: {pause} segundos\n")
        f.write(f"Adjunto: {'Sí' if attachment_path else 'No'}\n")
        f.write("\n" + "-" * 60 + "\n")
        f.write("RESULTADOS\n")
        f.write("-" * 60 + "\n\n")
        f.write(f"Total procesados: {total_exitosos + total_fallidos}\n")
        f.write(f"✓ Enviados exitosamente: {total_exitosos}\n")
        f.write(f"✗ Fallidos: {total_fallidos}\n")
        f.write(f"Tasa de éxito: {(total_exitosos / (total_exitosos + total_fallidos) * 100):.1f}%\n")
        f.write(f"Tiempo total: {elapsed:.1f} minutos\n")
        f.write(f"Velocidad: {(total_exitosos + total_fallidos) / elapsed:.1f} emails/minuto\n")
        f.write("\n" + "-" * 60 + "\n")
        f.write("PRÓXIMO COMANDO\n")
        f.write("-" * 60 + "\n\n")
        f.write(f"python send_email_sendgrid.py --offset {offset_final} --limit 3000 --batch-size 500 --pause 600 --email-type {email_type}\n")

        if all_errores:
            f.write("\n" + "-" * 60 + "\n")
            f.write("ERRORES DETALLADOS\n")
            f.write("-" * 60 + "\n\n")
            for error in all_errores:
                f.write(f"{error['email']}\t→\t{error['error']}\n")

    print(f"Reporte completo guardado en: {report_file}")

    # Guardar errores por separado (por compatibilidad)
    if all_errores:
        error_file = f"sendgrid_failed_{timestamp}.txt"
        with open(error_file, 'w') as f:
            for error in all_errores:
                f.write(f"{error['email']}\t{error['error']}\n")
        print(f"Errores guardados en: {error_file}")

    print("\n¡Envío completado!")
    print("\nPuedes ver estadísticas en: https://app.sendgrid.com/statistics")


def send_test_email(test_email, attachment_path=None, email_type='liderazgo_resultados'):
    """
    Envía un email de prueba a una dirección específica.

    Args:
        test_email: Email de destino
        attachment_path: Ruta opcional a un archivo PDF para adjuntar
        email_type: Tipo de email a enviar (frente_comun, planes_medicos o liderazgo_resultados)
    """
    print("=" * 60)
    print("ENVÍO DE PRUEBA CON SENDGRID")
    print("=" * 60)
    print()

    # Inicializar SendGrid
    sender = SendGridEmailSender(email_type=email_type)

    # Crear un registro temporal para la prueba
    class TempRegistration:
        def __init__(self, email):
            self.email = email
            self.name = "Usuario"
            self.last_name = "Prueba"

    reg = TempRegistration(test_email)

    print(f"Enviando email de prueba a: {test_email}")
    print(f"Tipo de email: {email_type}")
    print()

    nombre_completo = "Usuario Prueba"

    # Generar HTML según el tipo
    if email_type == 'planes_medicos':
        html_content = sender.generate_planes_medicos_html(nombre_completo, test_email)
        subject = 'Los planes médicos no pueden seguir dictando nuestra práctica'
    elif email_type == 'liderazgo_resultados':
        html_content = sender.generate_liderazgo_resultados_html(nombre_completo, test_email)
        subject = 'La clase médica necesita liderazgo con resultados'
    elif email_type == 'fechas_votacion':
        html_content = sender.generate_fechas_votacion_html(nombre_completo, test_email)
        subject = 'Vota #2 por nuestro equipo — Conoce las fechas'
    elif email_type == 'renovacion':
        html_content = sender.generate_renovacion_html(nombre_completo, test_email)
        subject = 'Es tiempo de renovar el Colegio de Médicos — Vota #2'
    else:
        html_content = sender.generate_frente_comun_html(nombre_completo, test_email)
        subject = 'Un frente común por la clase médica — ¡Renovar para avanzar!'

    success, message = sender.send_email(
        test_email,
        subject,
        html_content,
        nombre_completo,
        attachment_path
    )

    if success:
        print("[OK] Email enviado exitosamente!")
        print()
        print("Verifica tu bandeja de entrada en:", test_email)
        print("Revisa también la carpeta de spam si no lo ves.")
    else:
        print(f"[ERROR] No se pudo enviar: {message}")

    print()
    print("Puedes ver el estado en: https://app.sendgrid.com/email_activity")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Envío masivo con SendGrid')
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--pause', type=int, default=30)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--test', action='store_true', help='Enviar solo 5 emails de prueba')
    parser.add_argument('--to', type=str, help='Enviar a un email específico para prueba')
    parser.add_argument('--attachment', type=str, help='Ruta a un archivo PDF para adjuntar')
    parser.add_argument('--email-type', type=str, default='frente_comun',
                        choices=['frente_comun', 'planes_medicos', 'liderazgo_resultados', 'fechas_votacion', 'renovacion'],
                        help='Tipo de email a enviar (frente_comun, planes_medicos, liderazgo_resultados, fechas_votacion o renovacion)')

    args = parser.parse_args()

    if args.to:
        # Enviar a un email específico
        send_test_email(args.to, args.attachment, args.email_type)
    elif args.test:
        print("MODO PRUEBA: Enviando 5 emails")
        send_mass_email_sendgrid(batch_size=5, pause=5, limit=5, attachment_path=args.attachment, email_type=args.email_type)
    else:
        send_mass_email_sendgrid(
            batch_size=args.batch_size,
            pause=args.pause,
            limit=args.limit,
            offset=args.offset,
            attachment_path=args.attachment,
            email_type=args.email_type
        )


if __name__ == "__main__":
    main()