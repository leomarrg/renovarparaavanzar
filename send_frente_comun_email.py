#!/usr/bin/env python
"""
Script para enviar email "Un frente común por la clase médica"
"""

import os
import sys
import django
import time
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration

# Configuración del email
SUBJECT = 'Un frente común por la clase médica — ¡Renovar para avanzar!'
FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
SITE_URL = settings.SITE_URL
LOGO_URL = f"{SITE_URL}/static/landing/img/email/DR_x_RPA@4x.png"

# Configuración de envío por bloques
BLOCK_SIZE = 50
PAUSE_BETWEEN_BLOCKS = 60
PAUSE_BETWEEN_EMAILS = 1


def generate_email_html(nombre_completo, email_destinatario):
    """Genera el HTML del email."""
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Un frente común por la clase médica</title>
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
            line-height: 1.3;
        }}
        .content {{
            padding: 40px 30px;
            background-color: white;
        }}
        .greeting {{
            font-size: 20px;
            color: #377e7c;
            margin-bottom: 25px;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.8;
            color: #333;
            margin-bottom: 25px;
        }}
        .message strong {{
            color: #377e7c;
        }}
        .highlight {{
            background-color: #e8f7f7;
            padding: 25px;
            border-left: 4px solid #377e7c;
            margin: 30px 0;
            border-radius: 5px;
        }}
        .highlight p {{
            margin: 0;
            font-size: 17px;
            color: #377e7c;
            line-height: 1.6;
            font-weight: 500;
        }}
        .cta-section {{
            background-color: #f9f9f9;
            padding: 30px;
            text-align: center;
            margin: 30px 0;
            border-radius: 8px;
        }}
        .cta-section p {{
            font-size: 18px;
            color: #377e7c;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .cta-text {{
            font-size: 24px;
            color: #377e7c;
            font-weight: 700;
            margin: 20px 0;
        }}
        .hashtag {{
            font-size: 22px;
            color: #4dabaa;
            font-weight: 700;
            margin-top: 20px;
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
            margin-bottom: 10px;
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
            padding: 25px;
            font-style: italic;
            color: #377e7c;
            font-size: 18px;
            font-weight: 500;
            background-color: #f9f9f9;
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


def generate_text_content(nombre_completo):
    """Genera la versión de texto plano del email."""
    text_content = f"""
Estimado colega,

No más promesas vacías ni comités sin resultados. Es momento de unirnos en un frente común para poner fin al dilema de los planes médicos y lograr incentivos contributivos que hagan justicia a nuestra clase médica.

El Dr. Méndez Sexto y su equipo representan una nueva visión: resultados reales, diálogo efectivo y una defensa firme en favor de los médicos y la salud de Puerto Rico.

Te invitamos a ser parte del cambio.

¡Vota por el Dr. Méndez Sexto y su equipo!

#RenovarParaAvanzar

---

"Juntos renovamos, juntos avanzamos"

Dr. Méndez Sexto
Candidato a la Presidencia del Colegio de Médicos
#RenovarParaAvanzar

---
Pagado por el Comité Dr. Méndez Sexto

Si no deseas recibir más comunicaciones, envía un email a creatudominiopr@gmail.com con la palabra "BAJA".
"""
    return text_content


def send_email(registration, retry_count=3):
    """
    Envía un email con reintentos automáticos.
    """
    nombre_completo = f"{registration.name} {registration.last_name}".strip()
    if not nombre_completo or nombre_completo == " ":
        nombre_completo = "Estimado/a colega"

    for attempt in range(retry_count):
        try:
            html_content = generate_email_html(nombre_completo, registration.email)
            text_content = generate_text_content(nombre_completo)

            email = EmailMultiAlternatives(
                subject=SUBJECT,
                body=text_content,
                from_email=FROM_EMAIL,
                to=[registration.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return True, "Enviado"

        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(2)
            else:
                return False, str(e)

    return False, "Error desconocido"


def send_mass_emails(block_size=50, pause_between_blocks=60, limit=None, offset=0):
    """
    Envía emails en bloques con pausas.
    """
    print("=" * 60)
    print("ENVÍO MASIVO: UN FRENTE COMÚN POR LA CLASE MÉDICA")
    print("=" * 60)
    print()

    # Obtener todos los registros con email
    registrations = Registration.objects.filter(
        email__isnull=False
    ).exclude(
        email__exact=''
    ).order_by('id')

    # Aplicar offset
    if offset > 0:
        registrations = registrations[offset:]

    total = registrations.count()

    # Aplicar límite
    if limit:
        registrations = registrations[:limit]

    print(f"Total de emails a enviar: {registrations.count()}")
    if offset > 0:
        print(f"Comenzando desde el registro: {offset + 1}")
    print(f"Tamaño de bloque: {block_size} emails")
    print(f"Pausa entre bloques: {pause_between_blocks} segundos ({pause_between_blocks/60:.1f} minutos)")
    print()

    # Calcular tiempo estimado
    blocks_count = (registrations.count() + block_size - 1) // block_size
    tiempo_envio = (registrations.count() * PAUSE_BETWEEN_EMAILS) / 60
    tiempo_pausas = ((blocks_count - 1) * pause_between_blocks) / 60
    tiempo_total = tiempo_envio + tiempo_pausas

    print(f"Bloques necesarios: {blocks_count}")
    print(f"Tiempo estimado: {tiempo_total:.1f} minutos ({tiempo_total/60:.1f} horas)")
    print()

    print("¿Confirmas el envío? (escribe SI):")
    if input().strip().upper() != 'SI':
        print("Envío cancelado.")
        return

    # Contadores
    exitosos = 0
    fallidos = 0
    errores = []

    start_time = time.time()

    print()
    print("Iniciando envío por bloques...")
    print("=" * 60)

    # Convertir a lista para indexar
    registrations_list = list(registrations)

    # Procesar por bloques
    for block_num in range(0, len(registrations_list), block_size):
        block_end = min(block_num + block_size, len(registrations_list))
        block = registrations_list[block_num:block_end]

        current_block = (block_num // block_size) + 1
        total_blocks = (len(registrations_list) + block_size - 1) // block_size

        print(f"\nBLOQUE {current_block}/{total_blocks} - Emails {block_num + 1} a {block_end}")
        print("-" * 40)

        # Enviar emails del bloque
        for i, reg in enumerate(block, 1):
            global_index = block_num + i
            nombre = f"{reg.name} {reg.last_name}"

            print(f"[{global_index}/{len(registrations_list)}] {reg.email} ({nombre})... ", end="", flush=True)

            success, message = send_email(reg)

            if success:
                print("[OK]")
                exitosos += 1
            else:
                print(f"[FALLO: {message[:30]}]")
                fallidos += 1
                errores.append({
                    'email': reg.email,
                    'error': message
                })

            # Pausa entre emails
            if i < len(block):
                time.sleep(PAUSE_BETWEEN_EMAILS)

        # Mostrar progreso del bloque
        print(f"\nBloque {current_block} completado: {len(block)} emails procesados")
        print(f"Acumulado: {exitosos} enviados, {fallidos} fallidos")

        # Pausa entre bloques (excepto después del último)
        if block_end < len(registrations_list):
            print(f"\nPausando {pause_between_blocks} segundos antes del siguiente bloque...")
            time.sleep(pause_between_blocks)

    # Resumen final
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60

    print()
    print("=" * 60)
    print("RESUMEN DE ENVÍO MASIVO")
    print("=" * 60)
    print(f"Total procesados: {exitosos + fallidos}")
    print(f"Enviados exitosamente: {exitosos}")
    print(f"Fallidos: {fallidos}")
    print(f"Tasa de éxito: {(exitosos / (exitosos + fallidos) * 100):.1f}%")
    print(f"Tiempo total: {elapsed_time:.1f} minutos ({elapsed_time/60:.1f} horas)")
    print()

    # Guardar errores
    if errores:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = f"failed_frente_comun_{timestamp}.txt"

        with open(error_file, 'w', encoding='utf-8') as f:
            for error in errores:
                f.write(f"{error['email']}\t{error['error']}\n")

        print(f"Emails fallidos guardados en: {error_file}")
        print()

    print("¡Envío masivo completado!")


def main():
    """
    Función principal con opciones.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Envío masivo: Un frente común')
    parser.add_argument(
        '--block-size',
        type=int,
        default=50,
        help='Cantidad de emails por bloque (default: 50)'
    )
    parser.add_argument(
        '--pause',
        type=int,
        default=60,
        help='Segundos de pausa entre bloques (default: 60)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limitar cantidad de emails a enviar'
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=0,
        help='Comenzar desde el registro N (default: 0)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Modo prueba: solo envía 5 emails'
    )

    args = parser.parse_args()

    if args.test:
        print("MODO PRUEBA: Enviando solo 5 emails")
        send_mass_emails(block_size=5, pause_between_blocks=10, limit=5)
    else:
        send_mass_emails(
            block_size=args.block_size,
            pause_between_blocks=args.pause,
            limit=args.limit,
            offset=args.offset
        )


if __name__ == "__main__":
    main()