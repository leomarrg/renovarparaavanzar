#!/usr/bin/env python
"""
Script para reenviar emails con encuesta solo a los que fallaron
en el envío anterior por error de conexión.
"""

import os
import sys
import django
import time
from django.core.mail import EmailMultiAlternatives

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.conf import settings

# Lista de emails que fallaron (extraídos del log)
FAILED_EMAILS = [
    'eurifernandeznunez@gmail.com',
    'johndanet@yahoo.com',
    'berniemalpica@gmail.com',
    'erikarentas@yahoo.com',
    'berenisperezmd@gmail.com',
    'cibelletp@gmail.com',
    'cuconavi@yahoo.com',
    'guillermopastrana@gmail.com',
    'madelinesantosmd@yahoo.com',
    'rhaumd@yahoo.com',
    'maldonadocpr@hotmail.com',
    'juan.zaiter@gmail.com',
    'pachecoriveraal@gmail.com',
    'vrsanchezquiles@yahoo.com',
    'raulretina@gmail.com',
    'mariamontescordero87@gmail.com',
    'titapr12@gmail.com',
    'familymedicalclinicss@gmail.com',
    'kimberlyramos@gmail.com',
    'npriscilla.md@gmail.com',
    'luis.molinary@gmail.com',
    'jjbrainmind@gmail.com',
    'odarude.rs@gmail.com',
    'rosarioreymd@hotmail.com',
    'sevilla107@yahoo.com',
    'anisha.miranda@gmail.com',
    'mmsantia@yahoo.com',
    'drrahu27@gmail.com',
    'leidyfelizcarrasco@gmail.com',
    'drjuanrobles@yahoo.com',
    'martinezselma@gmail.com',
    'joed.laboy.md@gmail.com',
    'rtroche@hotmail.com',
    'moraimalandrau@yahoo.com',
    'lauracordovamd@gmail.com',
    'leonleduardmd@gmail.com',
    'javiermonett@gmail.com',
    'DoctorFelixSchmidt@gmail.com',
    'eliecereliecer84@yahoo.com',
    'chiques@icloud.com',
    'glorimarnazario.md@gmail.com',
    'dra.fulgencioreyes@gmail.com',
    'yyboscan@hotmail.com',
    'dra.yolandavarela@hotmail.com',
    'drjjfi@gmail.com',
    'paolarijo@gmail.com',
    'naty_8723@hotmail.com',
    'edrick.ramirezmd@gmail.com',
    'eneidanarvaezmd@hotmail.com',
    'dracsanchez911@gmail.com',
    'jorgevazquezgonzalez@hotmail.com',
    'domingonevarez@outlook.com',
    'albertcserrano0@gmail.com',
    'afeliciano@afmedicalgroup.net',
    'implante1@gmail.com',
    'egm012@yahoo.com',
    'cveras@prsupplies.com',
    'lfragoso2010@gmail.com',
    'abeauchamp@me.com',
    'lmarreromd@gmail.com',
    'dr_anthonyrivera@yahoo.com',
    'berfacastillo@gmail.com',
    'jfjimenezmd@att.net',
    'karlosbargas@yahoo.com',
    'jvelazquezmd05@gmail.com',
    'eliut.melendez@yahoo.com',
    'anpazmd@gmail.com',
    'mlmmd1995@hotmail.com'
]

# Configuración del email
SUBJECT = 'Ayúdanos a fortalecer la campaña del Dr. Méndez Sexto - Encuesta'
FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
SURVEY_URL = "https://us10.list-manage.com/survey?u=32f93d7ae2a7bd70efbba97b6&id=e194374f1d&e=54e0690aa6"
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
                <a href="{SURVEY_URL}" style="color: #377e7c; word-break: break-all;">
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


def send_survey_email(registration):
    """
    Envía el email con el enlace de la encuesta a un usuario registrado.
    """
    try:
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
    Función principal del script para reenviar emails fallidos.
    """
    print("=" * 60)
    print("REENVÍO DE EMAILS FALLIDOS - ENCUESTA")
    print("=" * 60)
    print()

    # Limpiar lista de emails únicos (eliminar duplicados)
    unique_failed_emails = list(set(FAILED_EMAILS))

    print(f"Total de emails únicos que fallaron: {len(unique_failed_emails)}")
    print()

    # Confirmar antes de enviar
    print("¿Deseas reenviar a todos estos emails?")
    print("Escribe 'SI' para confirmar:")
    confirmacion = input().strip().upper()

    if confirmacion != 'SI':
        print("Reenvío cancelado.")
        return

    print()
    print("Iniciando reenvío con pausas más largas para evitar errores de conexión...")
    print("-" * 40)

    # Contadores
    exitosos = 0
    fallidos = 0
    no_encontrados = 0
    errores = []

    # Reenviar emails
    for i, email_address in enumerate(unique_failed_emails, 1):
        # Buscar el registro en la base de datos
        try:
            # Buscar el registro más reciente con este email
            registration = Registration.objects.filter(email=email_address).last()

            if not registration:
                print(f"[{i}/{len(unique_failed_emails)}] {email_address} - No encontrado en BD")
                no_encontrados += 1
                continue

            nombre = f"{registration.name} {registration.last_name}"
            print(f"[{i}/{len(unique_failed_emails)}] Enviando a {email_address} ({nombre})... ", end="")

            # Intentar enviar el email
            success, message = send_survey_email(registration)

            if success:
                print("[OK]")
                exitosos += 1
            else:
                print("[FALLO]")
                fallidos += 1
                errores.append(f"  - {message}")

            # Pausa más larga entre envíos para evitar problemas de conexión
            # Cada 10 emails, hacer una pausa más larga
            if i % 10 == 0:
                print("  [Pausa de 5 segundos para evitar sobrecarga...]")
                time.sleep(5)
            else:
                time.sleep(2)  # Pausa normal de 2 segundos

        except Exception as e:
            print(f"[ERROR]")
            fallidos += 1
            errores.append(f"  - Error procesando {email_address}: {str(e)}")

            # Si hay un error de conexión, esperar más tiempo
            if "Connection" in str(e):
                print("  [Error de conexión detectado. Esperando 10 segundos...]")
                time.sleep(10)

    # Resumen final
    print()
    print("=" * 60)
    print("RESUMEN DE REENVÍO")
    print("=" * 60)
    print(f"Total procesados: {len(unique_failed_emails)}")
    print(f"Exitosos: {exitosos}")
    print(f"Fallidos: {fallidos}")
    print(f"No encontrados en BD: {no_encontrados}")

    if errores:
        print("\nErrores encontrados:")
        for error in errores[:10]:  # Mostrar solo los primeros 10 errores
            print(error)
        if len(errores) > 10:
            print(f"  ... y {len(errores) - 10} errores más")

    print()
    print("Proceso de reenvío completado.")


if __name__ == "__main__":
    main()