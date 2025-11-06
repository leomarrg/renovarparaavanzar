#!/usr/bin/env python
"""
Script para enviar emails masivos usando Amazon SES.
Optimizado para enviar 6000+ emails de manera confiable.
"""

import os
import sys
import django
import time
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timedelta
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.conf import settings

# Configuración de AWS SES
AWS_REGION = 'us-east-1'  # Cambiar según tu región de SES
SENDER_EMAIL = 'creatudominiopr@gmail.com'  # Debe estar verificado en SES
SENDER_NAME = 'Dr. Méndez Sexto - Renovar para Avanzar'

# Configuración del email
SUBJECT = 'Ayúdanos a fortalecer la campaña del Dr. Méndez Sexto - Encuesta'
SURVEY_URL = "https://us10.list-manage.com/survey?u=32f93d7ae2a7bd70efbba97b6&id=e194374f1d&e=54e0690aa6"

# Configuración de envío
BATCH_SIZE = 50  # SES permite hasta 50 destinatarios por llamada
SEND_RATE = 14  # Emails por segundo (ajustar según tu límite de SES)
DAILY_LIMIT = 10000  # Límite diario de SES (ajustar según tu cuenta)

# Para usar el logo, necesitarás subirlo a S3 o usar una URL pública
LOGO_URL = "https://www.renovarparaavanzar.com/static/landing/img/email/DR_x_RPA@4x.png"


class SESEmailSender:
    """
    Clase para manejar el envío de emails masivos con Amazon SES.
    """

    def __init__(self):
        """
        Inicializa el cliente de SES.
        """
        try:
            self.ses_client = boto3.client('ses', region_name=AWS_REGION)
            self.check_ses_configuration()
        except NoCredentialsError:
            print("[ERROR] No se encontraron credenciales de AWS.")
            print("Configura tus credenciales usando:")
            print("  export AWS_ACCESS_KEY_ID='tu-access-key'")
            print("  export AWS_SECRET_ACCESS_KEY='tu-secret-key'")
            sys.exit(1)

    def check_ses_configuration(self):
        """
        Verifica la configuración de SES y los límites de envío.
        """
        try:
            # Obtener cuota de envío
            response = self.ses_client.get_send_quota()

            print("=" * 60)
            print("CONFIGURACIÓN DE AMAZON SES")
            print("=" * 60)
            print(f"Límite de envío diario: {response['Max24HourSend']}")
            print(f"Emails enviados hoy: {response['SentLast24Hours']}")
            print(f"Tasa de envío: {response['MaxSendRate']} emails/segundo")
            print()

            # Verificar si el email remitente está verificado
            verified = self.ses_client.list_verified_email_addresses()
            if SENDER_EMAIL not in verified['VerifiedEmailAddresses']:
                print(f"[ADVERTENCIA] {SENDER_EMAIL} no está verificado en SES.")
                print("Debes verificar este email antes de poder enviar.")
                return False

            return True

        except ClientError as e:
            print(f"[ERROR] Error verificando SES: {e}")
            return False

    def generate_email_html(self, nombre_completo):
        """
        Genera el HTML del email.
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
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
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
        <div class="header">
            <img src="{LOGO_URL}" alt="Renovar para Avanzar" />
            <h1>Tu voz fortalece nuestra campaña</h1>
        </div>

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

            <div class="button-container">
                <a href="{SURVEY_URL}" class="cta-button">
                    Completar Encuesta
                </a>
            </div>

            <p class="message" style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                Si el botón no funciona, puedes copiar y pegar este enlace en tu navegador:<br>
                <a href="{SURVEY_URL}" style="color: #377e7c; word-break: break-all;">
                    {SURVEY_URL}
                </a>
            </p>
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
                Si no deseas recibir más comunicaciones, envía un email a<br>
                <a href="mailto:creatudominiopr@gmail.com?subject=Baja">
                    creatudominiopr@gmail.com
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def generate_text_content(self, nombre_completo):
        """
        Genera la versión de texto plano del email.
        """
        text_content = f"""
Estimado/a {nombre_completo},

Gracias por ser parte del movimiento Renovar para Avanzar.

Tu apoyo continúa siendo fundamental para el cambio que nuestro Colegio de Médicos necesita.

TU OPINIÓN PUEDE HACER LA DIFERENCIA

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
        return text_content

    def send_batch(self, registrations):
        """
        Envía un lote de emails usando SES.
        """
        destinations = []

        for reg in registrations:
            nombre_completo = f"{reg.name} {reg.last_name}".strip()
            if not nombre_completo or nombre_completo == " ":
                nombre_completo = "Estimado/a doctor/a"

            destinations.append({
                'Destination': {
                    'ToAddresses': [reg.email],
                },
                'ReplacementTemplateData': json.dumps({
                    'nombre_completo': nombre_completo,
                    'email': reg.email
                })
            })

        # Para envío masivo con SES, es mejor usar plantillas
        # Por ahora usaremos envíos individuales optimizados
        success_count = 0
        failed_emails = []

        for reg in registrations:
            try:
                nombre_completo = f"{reg.name} {reg.last_name}".strip()
                if not nombre_completo or nombre_completo == " ":
                    nombre_completo = "Estimado/a doctor/a"

                response = self.ses_client.send_email(
                    Source=f'{SENDER_NAME} <{SENDER_EMAIL}>',
                    Destination={
                        'ToAddresses': [reg.email]
                    },
                    Message={
                        'Subject': {
                            'Data': SUBJECT,
                            'Charset': 'UTF-8'
                        },
                        'Body': {
                            'Html': {
                                'Data': self.generate_email_html(nombre_completo),
                                'Charset': 'UTF-8'
                            },
                            'Text': {
                                'Data': self.generate_text_content(nombre_completo),
                                'Charset': 'UTF-8'
                            }
                        }
                    }
                )
                success_count += 1
                print(f"  [OK] {reg.email}")

            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'MessageRejected':
                    print(f"  [RECHAZADO] {reg.email}: Email rechazado por SES")
                elif error_code == 'MailFromDomainNotVerified':
                    print(f"  [ERROR] Dominio no verificado en SES")
                    return success_count, failed_emails
                else:
                    print(f"  [ERROR] {reg.email}: {error_code}")
                failed_emails.append(reg.email)

            # Control de tasa de envío
            time.sleep(1.0 / SEND_RATE)

        return success_count, failed_emails


def main():
    """
    Función principal para envío masivo con SES.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Enviar emails masivos con AWS SES')
    parser.add_argument('--limit', type=int, help='Limitar cantidad de emails a enviar')
    parser.add_argument('--offset', type=int, default=0, help='Comenzar desde el registro N')
    parser.add_argument('--test', action='store_true', help='Modo prueba (envía solo 10)')
    parser.add_argument('--dry-run', action='store_true', help='Simula sin enviar')

    args = parser.parse_args()

    print("=" * 60)
    print("ENVÍO MASIVO DE EMAILS CON AWS SES")
    print("=" * 60)
    print()

    # Inicializar SES
    sender = SESEmailSender()

    # Obtener registros
    registrations = Registration.objects.filter(
        email__isnull=False
    ).exclude(
        email__exact=''
    ).order_by('created_at')

    # Aplicar offset y límite
    if args.offset:
        registrations = registrations[args.offset:]

    total = registrations.count()

    if args.test:
        registrations = registrations[:10]
        print("MODO PRUEBA: Enviando solo 10 emails")
    elif args.limit:
        registrations = registrations[:args.limit]
        print(f"Limitado a {args.limit} emails")

    print(f"Total de emails a enviar: {registrations.count()}")
    print(f"Total en base de datos: {total}")

    if args.dry_run:
        print("\n[MODO DRY RUN] No se enviarán emails realmente.")
        print("\nPrimeros 10 destinatarios:")
        for reg in registrations[:10]:
            print(f"  - {reg.email} ({reg.name} {reg.last_name})")
        return

    # Confirmar envío
    if not args.test:
        print("\n¿Confirmas el envío masivo?")
        print("Escribe 'SI' para continuar:")
        if input().strip().upper() != 'SI':
            print("Envío cancelado.")
            return

    # Enviar por lotes
    print("\nIniciando envío...")
    print("-" * 40)

    total_sent = 0
    total_failed = 0
    all_failed_emails = []

    batch = []
    for i, reg in enumerate(registrations, 1):
        batch.append(reg)

        # Enviar cuando alcanzamos el tamaño del lote
        if len(batch) >= BATCH_SIZE or i == registrations.count():
            print(f"\nEnviando lote {i - len(batch) + 1}-{i}...")
            sent, failed = sender.send_batch(batch)
            total_sent += sent
            total_failed += len(failed)
            all_failed_emails.extend(failed)
            batch = []

    # Resumen final
    print()
    print("=" * 60)
    print("RESUMEN DE ENVÍO")
    print("=" * 60)
    print(f"Total procesados: {total_sent + total_failed}")
    print(f"Enviados exitosamente: {total_sent}")
    print(f"Fallidos: {total_failed}")

    # Guardar log
    if all_failed_emails:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"ses_failed_emails_{timestamp}.txt"
        with open(log_file, 'w') as f:
            for email in all_failed_emails:
                f.write(f"{email}\n")
        print(f"\nEmails fallidos guardados en: {log_file}")

    print("\nProceso completado.")


if __name__ == "__main__":
    main()