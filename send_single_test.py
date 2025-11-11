#!/usr/bin/env python
"""
Script simple para enviar UN SOLO email de prueba y diagnosticar el problema.
"""

import os
import sys
import time
from datetime import datetime

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Category
except ImportError:
    print("ERROR: SendGrid no está instalado.")
    print("Ejecuta: pip install sendgrid")
    sys.exit(1)

# Configuración
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'registro@renovarparaavanzar.com')

if not SENDGRID_API_KEY:
    print("ERROR: SENDGRID_API_KEY no está configurado.")
    sys.exit(1)


def send_simple_test(to_email):
    """Envía un email de prueba SIMPLE sin Django."""

    print("=" * 60)
    print("PRUEBA SIMPLE DE SENDGRID")
    print("=" * 60)
    print()
    print(f"De: {FROM_EMAIL}")
    print(f"Para: {to_email}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # HTML muy simple para prueba
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email de Prueba</title>
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #377e7c;">Email de Prueba - SendGrid</h2>
    <p>Este es un email de prueba enviado desde SendGrid.</p>
    <p><strong>Timestamp único:</strong> {timestamp}</p>
    <p>Si recibes este email múltiples veces con el MISMO timestamp, el problema está en SendGrid o en tu cliente de email.</p>
    <p>Si recibes emails con timestamps DIFERENTES, significa que el script se está ejecutando múltiples veces.</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        Dr. Méndez Sexto - Renovar para Avanzar<br>
        Prueba técnica
    </p>
</body>
</html>
"""

    text_content = f"""
Email de Prueba - SendGrid

Este es un email de prueba enviado desde SendGrid.

Timestamp único: {timestamp}

Si recibes este email múltiples veces con el MISMO timestamp, el problema está en SendGrid o en tu cliente de email.
Si recibes emails con timestamps DIFERENTES, significa que el script se está ejecutando múltiples veces.

---
Dr. Méndez Sexto - Renovar para Avanzar
Prueba técnica
"""

    try:
        # Crear mensaje
        message = Mail(
            from_email=(FROM_EMAIL, 'Dr. Méndez Sexto - Prueba'),
            to_emails=to_email,
            subject=f'Prueba SendGrid - {timestamp}',
            plain_text_content=text_content,
            html_content=html_content
        )

        # Reply-to
        message.reply_to = 'support@renovarparaavanzar.com'

        # Categoría única para identificar
        message.add_category(Category(f'test_{int(time.time())}'))

        print("Enviando email...")
        print()

        # Enviar
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        print()

        if response.status_code in [200, 201, 202]:
            print("✓ Email ACEPTADO por SendGrid")
            print()
            print("IMPORTANTE:")
            print("- Anota el timestamp: " + timestamp)
            print("- Si el email llega, verifica que tenga ESTE timestamp")
            print("- Si llegan 2 emails con timestamps DIFERENTES, ejecutaste el script 2 veces")
            print("- Si llegan 2 emails con el MISMO timestamp, hay un problema de duplicación")
            print()
            print("Verifica en:")
            print("https://app.sendgrid.com/email_activity")
            print()
        else:
            print("✗ Error al enviar")

        return response.status_code

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Prueba simple de SendGrid')
    parser.add_argument('email', help='Email de destino para la prueba')

    args = parser.parse_args()

    send_simple_test(args.email)


if __name__ == "__main__":
    main()
