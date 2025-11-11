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
        .content {{
            padding: 40px 30px;
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

            # Generar HTML
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


def send_mass_email_sendgrid(batch_size=100, pause=30, limit=None, offset=0, attachment_path=None):
    """
    Envía emails masivos usando SendGrid.

    Args:
        batch_size: Cantidad de emails por lote
        pause: Pausa en segundos entre lotes
        limit: Límite opcional de emails a enviar
        offset: Offset para empezar desde un registro específico
        attachment_path: Ruta opcional a un archivo PDF para adjuntar
    """
    print("=" * 60)
    print("ENVÍO MASIVO CON SENDGRID")
    print("=" * 60)
    print()

    # Inicializar SendGrid
    sender = SendGridEmailSender(email_type='frente_comun')

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

        exitosos, fallidos, errores = sender.send_batch(
            batch,
            'Un frente común por la clase médica — ¡Renovar para avanzar!',
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

    print()
    print("=" * 60)
    print("RESUMEN DE ENVÍO")
    print("=" * 60)
    print(f"Total procesados: {total_exitosos + total_fallidos}")
    print(f"Enviados: {total_exitosos}")
    print(f"Fallidos: {total_fallidos}")
    print(f"Tasa de éxito: {(total_exitosos / (total_exitosos + total_fallidos) * 100):.1f}%")
    print(f"Tiempo: {elapsed:.1f} minutos")
    print()

    # Guardar errores
    if all_errores:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = f"sendgrid_failed_{timestamp}.txt"
        with open(error_file, 'w') as f:
            for error in all_errores:
                f.write(f"{error['email']}\t{error['error']}\n")
        print(f"Errores guardados en: {error_file}")

    print("\n¡Envío completado!")
    print("\nPuedes ver estadísticas en: https://app.sendgrid.com/statistics")


def send_test_email(test_email, attachment_path=None):
    """
    Envía un email de prueba a una dirección específica.

    Args:
        test_email: Email de destino
        attachment_path: Ruta opcional a un archivo PDF para adjuntar
    """
    print("=" * 60)
    print("ENVÍO DE PRUEBA CON SENDGRID")
    print("=" * 60)
    print()

    # Inicializar SendGrid
    sender = SendGridEmailSender(email_type='frente_comun')

    # Crear un registro temporal para la prueba
    class TempRegistration:
        def __init__(self, email):
            self.email = email
            self.name = "Usuario"
            self.last_name = "Prueba"

    reg = TempRegistration(test_email)

    print(f"Enviando email de prueba a: {test_email}")
    print()

    nombre_completo = "Usuario Prueba"
    html_content = sender.generate_frente_comun_html(nombre_completo, test_email)

    success, message = sender.send_email(
        test_email,
        'Un frente común por la clase médica — ¡Renovar para avanzar!',
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

    args = parser.parse_args()

    if args.to:
        # Enviar a un email específico
        send_test_email(args.to, args.attachment)
    elif args.test:
        print("MODO PRUEBA: Enviando 5 emails")
        send_mass_email_sendgrid(batch_size=5, pause=5, limit=5, attachment_path=args.attachment)
    else:
        send_mass_email_sendgrid(
            batch_size=args.batch_size,
            pause=args.pause,
            limit=args.limit,
            offset=args.offset,
            attachment_path=args.attachment
        )


if __name__ == "__main__":
    main()