#!/usr/bin/env python
"""
Script para enviar email con enlace de encuesta de la campaña Renovar para Avanzar
a todos los usuarios registrados en la plataforma.
"""

import os
import sys
import django
import time
import argparse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from html import unescape

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.conf import settings

# Configuración del email
SUBJECT = 'Ayúdanos a fortalecer la campaña del Dr. Méndez Sexto - Encuesta'
FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
CONTACT_EMAIL = "info@drmendezsexto.com"

# URL de la encuesta
SURVEY_URL = "https://us10.list-manage.com/survey?u=32f93d7ae2a7bd70efbba97b6&id=e194374f1d&e=54e0690aa6"

# URLs de imágenes (usando el servidor local para desarrollo)
SITE_URL = settings.SITE_URL
LOGO_URL = f"{SITE_URL}/static/landing/img/email/DR_x_RPA@4x.png"


def generate_email_html(nombre_completo, email_destinatario):
    """
    Genera el HTML del email con el enlace de la encuesta.
    """
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Encuesta - Renovar para Avanzar</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #377e7c, #4dabaa);
            padding: 40px 30px;
            text-align: center;
        }}
        .header img {{
            max-width: 250px;
            height: auto;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: white;
            font-size: 28px;
            margin: 0;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
            background-color: white;
        }}
        .greeting {{
            font-size: 20px;
            color: #377e7c;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 25px;
        }}
        .highlight {{
            background-color: #e8f7f7;
            padding: 20px;
            border-left: 4px solid #377e7c;
            margin: 25px 0;
            border-radius: 5px;
        }}
        .highlight p {{
            margin: 0;
            font-size: 16px;
            color: #377e7c;
            line-height: 1.6;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #377e7c, #4dabaa);
            color: white !important;
            padding: 15px 35px;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 600;
            font-size: 18px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(55, 126, 124, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(55, 126, 124, 0.4);
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .benefits {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        .benefits h3 {{
            color: #377e7c;
            font-size: 18px;
            margin-bottom: 15px;
        }}
        .benefits ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .benefits li {{
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
            color: #333;
            font-size: 15px;
        }}
        .benefits li:before {{
            content: "✓";
            color: #377e7c;
            font-weight: bold;
            position: absolute;
            left: 0;
        }}
        .footer {{
            background-color: #1a1a1a;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .footer-content {{
            margin-bottom: 20px;
        }}
        .footer-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .footer-subtitle {{
            font-size: 14px;
            color: #b0b0b0;
            margin-bottom: 15px;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            display: inline-block;
            margin: 0 10px;
            color: white;
            text-decoration: none;
            font-size: 14px;
            padding: 8px 15px;
            background-color: #333;
            border-radius: 20px;
            transition: background-color 0.3s ease;
        }}
        .social-links a:hover {{
            background-color: #377e7c;
        }}
        .unsubscribe {{
            margin-top: 20px;
            font-size: 12px;
            color: #999;
        }}
        .unsubscribe a {{
            color: #4dabaa;
            text-decoration: none;
        }}
        .legal {{
            font-size: 11px;
            color: #666;
            margin-top: 15px;
        }}
        .signature {{
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #377e7c;
            font-size: 18px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header con logo -->
        <div class="header">
            <img src="{LOGO_URL}" alt="Renovar para Avanzar" />
            <h1>Tu voz fortalece nuestra campaña</h1>
        </div>

        <!-- Contenido principal -->
        <div class="content">
            <p class="greeting">Estimado/a {nombre_completo},</p>

            <p class="message">
                Gracias por ser parte del movimiento <strong>Renovar para Avanzar</strong>.
                Tu apoyo continúa siendo fundamental para el cambio que nuestro
                Colegio de Médicos necesita.
            </p>

            <div class="highlight">
                <p>
                    <strong>Tu opinión puede hacer la diferencia.</strong>
                </p>
            </div>

            <p class="message">
                Los resultados de esta encuesta ayudarán al <strong>Dr. Méndez Sexto</strong> y
                su equipo a fortalecer las propuestas de la campaña <strong>Renovar para Avanzar</strong>,
                asegurando que representen verdaderamente las necesidades y expectativas de todos.
            </p>

            <p class="message">
                <strong>Solo te tomará 3-5 minutos</strong>. Tu participación es completamente
                voluntaria y anónima.
            </p>

            <!-- Botón CTA -->
            <div class="button-container">
                <a href="{SURVEY_URL}" class="cta-button">
                    Completar Encuesta
                </a>
            </div>

            <p class="message" style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                Si el botón no funciona, puedes copiar y pegar este enlace en tu navegador:<br>
                <a href="{SURVEY_URL}" style="color: #0077be; word-break: break-all;">
                    {SURVEY_URL}
                </a>
            </p>
        </div>

        <!-- Firma -->
        <div class="signature">
            "Juntos renovamos, juntos avanzamos"
        </div>

        <!-- Footer -->
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
                <a href="mailto:creatudominiopr@gmail.com?subject=Solicitud de baja&body=Por favor, eliminen mi correo {email_destinatario} de su lista de envíos.">
                    darte de baja aquí
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html_content


def send_survey_email(registration, dry_run=False):
    """
    Envía el email con el enlace de la encuesta a un usuario registrado.

    Args:
        registration: Objeto Registration con los datos del usuario
        dry_run: Si es True, no envía el email realmente

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verificar que el usuario tenga email
        if not registration.email:
            return False, f"Usuario {registration.name} {registration.last_name} no tiene email"

        # Generar nombre completo
        nombre_completo = f"{registration.name} {registration.last_name}".strip()
        if not nombre_completo:
            nombre_completo = "Estimado/a doctor/a"

        # Generar HTML del email
        html_content = generate_email_html(nombre_completo, registration.email)

        # Crear versión de texto plano
        text_content = f"""
Estimado/a {nombre_completo},

Gracias por ser parte del movimiento Renovar para Avanzar.

Tu apoyo continúa siendo fundamental para el cambio que nuestro Colegio de Médicos necesita.

TU OPINIÓN PUEDE HACER LA DIFERENCIA
Un aliado de nuestra campaña está realizando una encuesta independiente para conocer las opiniones
de la comunidad médica sobre temas cruciales para el futuro del Colegio de Médicos.

Los resultados de esta encuesta ayudarán al Dr. Méndez Sexto y su equipo a fortalecer las
propuestas de la campaña Renovar para Avanzar.

Solo te tomará 3-5 minutos. Tu participación es completamente voluntaria y anónima.

COMPLETAR ENCUESTA:
{SURVEY_URL}

Juntos renovamos, juntos avanzamos.

Dr. Méndez Sexto
Candidato a la Presidencia del Colegio de Médicos
#RenovarParaAvanzar

---
Pagado por el Comité Dr. Méndez Sexto

Si no deseas recibir más comunicaciones, envía un email a creatudominiopr@gmail.com con la palabra "BAJA".
"""

        if dry_run:
            print(f"[DRY RUN] Email a: {registration.email}")
            print(f"[DRY RUN] Asunto: {SUBJECT}")
            print(f"[DRY RUN] Nombre: {nombre_completo}")
            return True, "Email simulado (dry run)"

        # Crear y enviar el email
        email = EmailMultiAlternatives(
            subject=SUBJECT,
            body=text_content,
            from_email=FROM_EMAIL,
            to=[registration.email]
        )

        # Adjuntar versión HTML
        email.attach_alternative(html_content, "text/html")

        # Enviar
        email.send()

        return True, f"Email enviado exitosamente a {registration.email}"

    except Exception as e:
        return False, f"Error al enviar a {registration.email}: {str(e)}"


def main():
    """
    Función principal del script.
    """
    parser = argparse.ArgumentParser(description='Enviar email con encuesta a usuarios registrados')
    parser.add_argument('--dry-run', action='store_true',
                      help='Simula el envío sin enviar realmente')
    parser.add_argument('--test', action='store_true',
                      help='Envía solo a los primeros 3 usuarios como prueba')
    parser.add_argument('--to', type=str,
                      help='Envía a un email específico para prueba')

    args = parser.parse_args()

    print("=" * 60)
    print("SCRIPT DE ENVÍO DE ENCUESTA - RENOVAR PARA AVANZAR")
    print("=" * 60)
    print()

    if args.to:
        # Modo prueba con email específico
        print(f"MODO PRUEBA: Enviando a {args.to}")
        print()

        # Crear registro temporal para prueba
        test_registration = Registration(
            name="Usuario",
            last_name="Prueba",
            email=args.to
        )

        success, message = send_survey_email(test_registration, args.dry_run)

        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")

        print("\nPrueba completada.")
        return

    # Obtener todos los registros con email
    registrations = Registration.objects.filter(
        email__isnull=False
    ).exclude(
        email__exact=''
    ).order_by('created_at')

    total = registrations.count()

    if total == 0:
        print("No hay usuarios registrados con email.")
        return

    print(f"Total de usuarios con email: {total}")
    print()

    if args.test:
        # Modo prueba: solo primeros 3
        registrations = registrations[:3]
        print("MODO PRUEBA: Enviando solo a los primeros 3 usuarios")
        print()

    if args.dry_run:
        print("MODO DRY RUN: No se enviarán emails realmente")
        print()

    # Confirmar antes de enviar
    if not args.dry_run and not args.test:
        print(f"¿Estás seguro de que quieres enviar {total} emails?")
        print("Escribe 'SI' para confirmar:")
        confirmacion = input().strip().upper()

        if confirmacion != 'SI':
            print("Envío cancelado.")
            return
        print()

    # Contadores
    exitosos = 0
    fallidos = 0
    errores = []

    print("Iniciando envío de emails...")
    print("-" * 40)

    # Enviar emails
    for i, registration in enumerate(registrations, 1):
        nombre = f"{registration.name} {registration.last_name}"
        print(f"[{i}/{len(registrations)}] Enviando a {registration.email} ({nombre})... ", end="")

        success, message = send_survey_email(registration, args.dry_run)

        if success:
            print("[OK]")
            exitosos += 1
        else:
            print("[FALLO]")
            fallidos += 1
            errores.append(f"  - {message}")

        # Pausa entre envíos para no saturar el servidor
        if not args.dry_run and i < len(registrations):
            time.sleep(0.5)

    # Resumen final
    print()
    print("=" * 60)
    print("RESUMEN DE ENVÍO")
    print("=" * 60)
    print(f"Total procesados: {exitosos + fallidos}")
    print(f"Exitosos: {exitosos}")
    print(f"Fallidos: {fallidos}")

    if errores:
        print("\nErrores encontrados:")
        for error in errores:
            print(error)

    print()
    print("Proceso completado.")


if __name__ == "__main__":
    main()