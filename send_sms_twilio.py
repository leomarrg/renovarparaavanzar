#!/usr/bin/env python
"""
Script para envío masivo de SMS usando Twilio API.
Cumple con todas las regulaciones de Twilio Messaging Policy.
"""

import os
import sys
import django
import time
from datetime import datetime
from pathlib import Path
import argparse

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.conf import settings

# Intentar importar Twilio
try:
    from twilio.rest import Client
except ImportError:
    print("ERROR: Twilio no está instalado.")
    print("Ejecuta: pip install twilio")
    sys.exit(1)

# Configuración de Twilio
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
SITE_URL = settings.SITE_URL

# Validar credenciales
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    print("ERROR: Faltan credenciales de Twilio en el archivo .env")
    print("Necesitas:")
    print("  TWILIO_ACCOUNT_SID=tu_account_sid")
    print("  TWILIO_AUTH_TOKEN=tu_auth_token")
    print("  TWILIO_PHONE_NUMBER=+18446815099")
    sys.exit(1)

# Configuración de envío
BATCH_SIZE = 50  # Twilio toll-free: max 3 MPS, vamos conservadores
PAUSE_BETWEEN_BATCHES = 20  # Pausa en segundos entre lotes
DELAY_BETWEEN_SMS = 1.0  # 1 segundo entre cada SMS (1 MPS)

class TwilioSMSSender:
    def __init__(self):
        """Inicializa el cliente de Twilio"""
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.from_number = TWILIO_PHONE_NUMBER

    def format_phone_number(self, phone):
        """
        Formatea número de teléfono para Twilio (formato E.164)
        Asume números de Puerto Rico si no tienen código de país
        """
        # Eliminar espacios, guiones, paréntesis
        phone = ''.join(filter(str.isdigit, phone))

        # Si el número tiene 10 dígitos, agregar +1 (USA/PR)
        if len(phone) == 10:
            return f'+1{phone}'

        # Si ya tiene 11 dígitos y empieza con 1
        if len(phone) == 11 and phone.startswith('1'):
            return f'+{phone}'

        # Si ya tiene el formato correcto
        if phone.startswith('+'):
            return phone

        # Caso por defecto: asumir Puerto Rico
        return f'+1{phone}'

    def send_sms(self, to_phone, message_body, media_urls=None):
        """
        Envía un SMS/MMS usando Twilio

        Args:
            to_phone: Número de teléfono destino
            message_body: Contenido del mensaje
            media_urls: Lista de URLs de imágenes para MMS (opcional)

        Returns:
            tuple: (success: bool, message_sid o error)
        """
        try:
            # Formatear número
            formatted_phone = self.format_phone_number(to_phone)

            # Preparar parámetros del mensaje
            message_params = {
                'body': message_body,
                'from_': self.from_number,
                'to': formatted_phone
            }

            # Agregar media URLs si se proporcionan (para MMS)
            if media_urls and len(media_urls) > 0:
                message_params['media_url'] = media_urls

            # Enviar SMS/MMS
            message = self.client.messages.create(**message_params)

            return True, message.sid

        except Exception as e:
            error_msg = str(e)
            return False, error_msg

    def send_batch(self, registrations, message_template, media_urls=None, offset=0):
        """
        Envía SMS/MMS a un lote de registros

        Args:
            registrations: QuerySet de Registration
            message_template: Template del mensaje (puede usar {nombre})
            media_urls: Lista de URLs de imágenes para MMS
            offset: Offset inicial para reporting
        """
        total = len(registrations)
        success_count = 0
        error_count = 0
        errors = []

        print(f"\n{'='*60}")
        print(f"INICIANDO ENVÍO DE LOTE")
        print(f"Total de SMS: {total}")
        print(f"{'='*60}\n")

        for idx, reg in enumerate(registrations, 1):
            # Verificar que tiene número de teléfono
            if not reg.phone_number:
                print(f"  [{idx}/{total}] {reg.name} {reg.last_name} - OMITIDO (sin teléfono)")
                error_count += 1
                errors.append({
                    'name': f"{reg.name} {reg.last_name}",
                    'phone': 'N/A',
                    'error': 'Sin número de teléfono'
                })
                continue

            # Personalizar mensaje
            nombre_completo = f"{reg.name} {reg.last_name}"
            message = message_template.format(
                nombre=reg.name,
                nombre_completo=nombre_completo
            )

            # Enviar SMS/MMS
            print(f"  [{idx}/{total}] {nombre_completo} ({reg.phone_number})...", end=" ")
            success, result = self.send_sms(reg.phone_number, message, media_urls=media_urls)

            if success:
                print(f"[OK] SID: {result[:20]}...")
                success_count += 1
            else:
                print(f"[ERROR] {result}")
                error_count += 1
                errors.append({
                    'name': nombre_completo,
                    'phone': reg.phone_number,
                    'error': result
                })

            # Delay entre SMS
            if idx < total:
                time.sleep(DELAY_BETWEEN_SMS)

        return success_count, error_count, errors


def send_mass_sms_twilio(message_template, media_urls=None, offset=0, limit=None, batch_size=BATCH_SIZE,
                         pause=PAUSE_BETWEEN_BATCHES, test_phone=None):
    """
    Función principal para envío masivo de SMS/MMS

    Args:
        message_template: Template del mensaje
        media_urls: Lista de URLs de imágenes para MMS (opcional)
        offset: Desde qué registro empezar
        limit: Cuántos registros procesar (None = todos)
        batch_size: Tamaño de cada lote
        pause: Pausa entre lotes en segundos
        test_phone: Si se proporciona, solo envía a este número (modo prueba)
    """
    sender = TwilioSMSSender()

    # Determinar si es SMS o MMS
    message_type = "MMS" if media_urls else "SMS"

    # Modo prueba
    if test_phone:
        print(f"\n{'='*60}")
        print(f"MODO PRUEBA - ENVIANDO A: {test_phone}")
        print(f"{'='*60}\n")
        print(f"Mensaje:")
        print(message_template.format(nombre='[Nombre]', nombre_completo='[Nombre Completo]'))
        print(f"\n{'='*60}")
        print(f"Longitud: {len(message_template.format(nombre='Prueba', nombre_completo='Prueba Test'))} caracteres")
        print(f"Segmentos SMS: {(len(message_template.format(nombre='Prueba', nombre_completo='Prueba Test')) // 160) + 1}")
        print(f"\n¿Confirmas el envío de prueba? (escribe SI): ", end="")

        if input().strip().upper() != 'SI':
            print("Envío cancelado.")
            return

        success, result = sender.send_sms(test_phone, message_template.format(
            nombre='Prueba',
            nombre_completo='Prueba Test'
        ), media_urls=media_urls)

        if success:
            print(f"\n✅ SMS de prueba enviado exitosamente!")
            print(f"SID: {result}")
        else:
            print(f"\n❌ Error al enviar SMS de prueba:")
            print(f"Error: {result}")

        return

    # Obtener registros
    # Filtrar solo los que tienen teléfono y no están unsubscribed
    registrations = Registration.objects.filter(
        phone_number__isnull=False,
        unsubscribed=False
    ).exclude(
        phone_number=''
    ).order_by('id')

    total_available = registrations.count()

    # Aplicar offset y limit
    if offset > 0:
        registrations = registrations[offset:]

    if limit:
        registrations = registrations[:limit]

    registrations_list = list(registrations)
    total_to_send = len(registrations_list)

    if total_to_send == 0:
        print("No hay registros para enviar SMS.")
        return

    # Calcular tiempo estimado
    num_batches = (total_to_send + batch_size - 1) // batch_size
    time_per_batch = (batch_size * DELAY_BETWEEN_SMS) + pause
    estimated_minutes = (num_batches * time_per_batch) / 60

    # Calcular segmentos SMS
    sample_message = message_template.format(nombre='Juan', nombre_completo='Juan Pérez')
    message_length = len(sample_message)
    segments_per_sms = (message_length // 160) + 1

    # Mostrar resumen
    print(f"\n{'='*60}")
    print(f"ENVÍO MASIVO DE SMS CON TWILIO")
    print(f"{'='*60}\n")
    print(f"Total de registros en DB: {total_available}")
    print(f"Offset: {offset}")
    print(f"Límite: {limit if limit else 'Sin límite'}")
    print(f"Total de SMS a enviar: {total_to_send}")
    print(f"Tamaño de lote: {batch_size}")
    print(f"Pausa entre lotes: {pause} segundos")
    print(f"\nMensaje ({message_length} caracteres, ~{segments_per_sms} segmentos):")
    print(f"{'─'*60}")
    print(message_template.format(nombre='[Nombre]', nombre_completo='[Nombre Completo]'))
    print(f"{'─'*60}")
    print(f"\nTiempo estimado: {estimated_minutes:.1f} minutos ({estimated_minutes/60:.1f} horas)")
    print(f"\n⚠️  IMPORTANTE - CUMPLIMIENTO TWILIO:")
    print(f"  • Todos los destinatarios deben haber dado consentimiento")
    print(f"  • El mensaje incluye instrucciones de opt-out")
    print(f"  • Costo estimado: ~${total_to_send * segments_per_sms * 0.0079:.2f} USD")
    print(f"\n{'='*60}")
    print(f"\n¿Confirmas el envío? (escribe SI): ", end="")

    if input().strip().upper() != 'SI':
        print("Envío cancelado.")
        return

    # Iniciar envío
    start_time = time.time()
    total_success = 0
    total_errors = 0
    all_errors = []

    print(f"\n{'='*60}")
    print(f"INICIANDO ENVÍO DE SMS")
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Enviar en lotes
    for batch_num in range(0, total_to_send, batch_size):
        batch = registrations_list[batch_num:batch_num + batch_size]
        batch_number = (batch_num // batch_size) + 1
        total_batches = num_batches

        print(f"\n--- Lote {batch_number}/{total_batches} ---")

        success, errors, error_list = sender.send_batch(
            batch,
            message_template,
            media_urls=media_urls,
            offset=offset + batch_num
        )

        total_success += success
        total_errors += errors
        all_errors.extend(error_list)

        # Pausa entre lotes (excepto en el último)
        if batch_num + batch_size < total_to_send:
            print(f"\nPausa de {pause} segundos antes del siguiente lote...")
            time.sleep(pause)

    # Resumen final
    elapsed = (time.time() - start_time) / 60
    offset_final = offset + total_to_send

    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Tiempo transcurrido: {elapsed:.1f} minutos")
    print(f"Total de SMS enviados: {total_success}")
    print(f"Total de errores: {total_errors}")
    print(f"Tasa de éxito: {(total_success/total_to_send*100):.1f}%")
    print(f"\nOffset inicial: {offset}")
    print(f"Offset final: {offset_final}")
    print(f"\n>>> PRÓXIMO COMANDO:")
    print(f"python send_sms_twilio.py --offset {offset_final} --limit 1000 --batch-size {batch_size} --pause {pause}")
    print(f"{'='*60}\n")

    # Guardar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"sms_report_{timestamp}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"REPORTE DE ENVÍO DE SMS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Total de SMS enviados: {total_success}\n")
        f.write(f"Total de errores: {total_errors}\n")
        f.write(f"Tasa de éxito: {(total_success/total_to_send*100):.1f}%\n")
        f.write(f"Tiempo transcurrido: {elapsed:.1f} minutos\n\n")
        f.write(f"Offset inicial: {offset}\n")
        f.write(f"Offset final: {offset_final}\n\n")
        f.write(f"Próximo comando:\n")
        f.write(f"python send_sms_twilio.py --offset {offset_final} --limit 1000 --batch-size {batch_size} --pause {pause}\n\n")

        if all_errors:
            f.write(f"\nERRORES DETALLADOS:\n")
            f.write(f"{'='*60}\n")
            for err in all_errors:
                f.write(f"\nNombre: {err['name']}\n")
                f.write(f"Teléfono: {err['phone']}\n")
                f.write(f"Error: {err['error']}\n")
                f.write(f"-" * 40 + "\n")

    print(f"Reporte guardado en: {report_file}")


def main():
    parser = argparse.ArgumentParser(description='Envío masivo de SMS con Twilio')
    parser.add_argument('--offset', type=int, default=0,
                        help='Offset inicial (default: 0)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Límite de registros a procesar (default: todos)')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                        help=f'Tamaño de cada lote (default: {BATCH_SIZE})')
    parser.add_argument('--pause', type=int, default=PAUSE_BETWEEN_BATCHES,
                        help=f'Pausa entre lotes en segundos (default: {PAUSE_BETWEEN_BATCHES})')
    parser.add_argument('--to', type=str, default=None,
                        help='Enviar SMS de prueba a este número')
    parser.add_argument('--message-type', type=str, default='renovacion',
                        choices=['renovacion', 'fechas_votacion'],
                        help='Tipo de mensaje a enviar')

    args = parser.parse_args()

    # Mensajes predefinidos (cumpliendo con regulaciones de Twilio)
    media_urls = None  # Por defecto sin imágenes (SMS)

    if args.message_type == 'renovacion':
        message = """¡Saludos!

Soy el Dr. Ramón Méndez Sexto. Juntos tenemos una cita para renovar el Colegio de Médicos.

Es tiempo de lograr justicia frente a los planes médicos.

Es tiempo de recuperar credibilidad y TU voz.

Vota #2 por la renovación.

Responde STOP para cancelar."""

        # URLs de las imágenes para MMS (JPG optimizado para mejor compatibilidad)
        media_urls = [
            f"{SITE_URL}/static/landing/img/email/Vota_num2.jpg",
            f"{SITE_URL}/static/landing/img/email/fechas_votacion.jpg"
        ]

    elif args.message_type == 'fechas_votacion':
        message = """Elecciones Colegio de Médicos:

📅 Nov 24-26: Voto en oficinas
📱 Nov 27-Dic 11: Voto electrónico
📋 Dic 12-13: Voto en Convención

Vota #2 - Dr. Méndez Sexto
#RenovarParaAvanzar

STOP para cancelar"""

        # URL de imagen para MMS
        media_urls = [
            f"{SITE_URL}/static/landing/img/email/fechas_votacion.jpg"
        ]

    # Ejecutar envío
    send_mass_sms_twilio(
        message_template=message,
        media_urls=media_urls,
        offset=args.offset,
        limit=args.limit,
        batch_size=args.batch_size,
        pause=args.pause,
        test_phone=args.to
    )


if __name__ == '__main__':
    main()
