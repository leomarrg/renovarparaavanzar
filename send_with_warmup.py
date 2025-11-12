#!/usr/bin/env python
"""
Script de envío masivo con Warm-up Plan automático.
Previene bloqueos de SendGrid incrementando gradualmente el volumen.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from landing.models import Registration

# Archivo para guardar progreso
PROGRESS_FILE = Path(__file__).parent / 'email_progress.json'

# Plan de Warm-up (días: cantidad_emails)
WARMUP_PLAN = {
    1: 500,    # Día 1: 500 emails
    2: 1000,   # Día 2: 1000 emails
    3: 2000,   # Día 3: 2000 emails
    4: 3500,   # Día 4: 3500 emails (el resto)
}


def load_progress():
    """Cargar progreso guardado"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'emails_sent': 0,
        'last_batch_date': None,
        'current_day': 0,
        'failed_emails': []
    }


def save_progress(progress):
    """Guardar progreso"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_total_pending():
    """Obtener total de emails pendientes"""
    return Registration.objects.filter(
        email__isnull=False,
        unsubscribed=False
    ).exclude(email='').count()


def calculate_next_batch():
    """Calcular cuántos emails enviar hoy según el plan de warm-up"""
    progress = load_progress()
    total_pending = get_total_pending()
    emails_sent = progress['emails_sent']

    # Verificar si es el mismo día
    today = datetime.now().date()
    last_date = progress.get('last_batch_date')

    if last_date:
        last_date = datetime.fromisoformat(last_date).date()
        if last_date == today:
            print("⚠️  YA ENVIASTE EMAILS HOY")
            print(f"Última ejecución: {progress['last_batch_date']}")
            print(f"Emails enviados hoy: {progress.get('emails_sent_today', 0)}")
            print()
            print("Para proteger tu cuenta, espera hasta mañana.")
            print("SendGrid penaliza picos repentinos de volumen.")
            return None

        # Incrementar día del plan
        if last_date < today:
            progress['current_day'] += 1
    else:
        progress['current_day'] = 1

    current_day = progress['current_day']

    # Obtener límite del día según el plan
    if current_day > len(WARMUP_PLAN):
        # Ya terminó el warm-up, enviar el resto
        batch_size = total_pending - emails_sent
    else:
        # Seguir el plan de warm-up
        daily_limit = WARMUP_PLAN[current_day]
        batch_size = min(daily_limit, total_pending - emails_sent)

    return {
        'batch_size': batch_size,
        'current_day': current_day,
        'offset': emails_sent,
        'progress': progress
    }


def show_status():
    """Mostrar estado actual"""
    progress = load_progress()
    total = get_total_pending()
    sent = progress['emails_sent']
    pending = total - sent

    print("=" * 60)
    print("📊 ESTADO DEL ENVÍO MASIVO")
    print("=" * 60)
    print()
    print(f"Total de emails a enviar:     {total:,}")
    print(f"✓ Emails enviados:            {sent:,}")
    print(f"⏳ Emails pendientes:          {pending:,}")
    print()

    if progress.get('last_batch_date'):
        print(f"Último envío: {progress['last_batch_date']}")
        print(f"Día del plan: {progress['current_day']}/{len(WARMUP_PLAN)}")

    print()
    print("=" * 60)
    print("📅 PLAN DE WARM-UP")
    print("=" * 60)
    for day, limit in WARMUP_PLAN.items():
        status = "✓" if day < progress['current_day'] else ("▶" if day == progress['current_day'] else "○")
        print(f"{status} Día {day}: {limit:,} emails")
    print()


def send_today_batch():
    """Enviar el lote de hoy según el warm-up plan"""
    batch_info = calculate_next_batch()

    if not batch_info:
        return

    batch_size = batch_info['batch_size']
    offset = batch_info['offset']
    current_day = batch_info['current_day']

    if batch_size <= 0:
        print("✅ ¡TODOS LOS EMAILS HAN SIDO ENVIADOS!")
        return

    print("=" * 60)
    print(f"📧 ENVÍO DEL DÍA {current_day}")
    print("=" * 60)
    print()
    print(f"Emails a enviar hoy: {batch_size:,}")
    print(f"Offset (desde registro): {offset}")
    print()
    print("Se enviará en lotes de 500 con pausa de 60 segundos entre lotes.")
    print()

    # Importar el script original
    sys.path.insert(0, str(Path(__file__).parent))
    from send_email_sendgrid import send_mass_email_sendgrid

    # Buscar archivo PDF adjunto
    pdf_path = Path(__file__).parent / 'static' / 'landing' / 'pdf' / 'flyer.pdf'
    if not pdf_path.exists():
        pdf_path = None
        print("⚠️  No se encontró el PDF adjunto, se enviará sin archivo.")
        print()

    print("¿Confirmas el envío? (escribe SI):")
    if input().strip().upper() != 'SI':
        print("Envío cancelado.")
        return

    # Enviar
    try:
        send_mass_email_sendgrid(
            batch_size=500,
            pause=60,
            limit=batch_size,
            offset=offset,
            attachment_path=str(pdf_path) if pdf_path else None
        )

        # Actualizar progreso
        progress = batch_info['progress']
        progress['emails_sent'] += batch_size
        progress['last_batch_date'] = datetime.now().isoformat()
        progress['emails_sent_today'] = batch_size
        save_progress(progress)

        print()
        print("=" * 60)
        print("✅ LOTE COMPLETADO")
        print("=" * 60)
        print(f"Emails enviados hoy: {batch_size}")
        print(f"Total acumulado: {progress['emails_sent']}")
        print()
        print("Vuelve mañana para continuar con el siguiente lote.")
        print("Esto previene bloqueos de SendGrid.")

    except Exception as e:
        print(f"❌ Error durante el envío: {e}")
        import traceback
        traceback.print_exc()


def reset_progress():
    """Reiniciar el progreso (usar con cuidado)"""
    print("⚠️  ADVERTENCIA: Esto borrará todo el progreso guardado.")
    print("¿Estás seguro? (escribe RESET):")
    if input().strip() == 'RESET':
        if PROGRESS_FILE.exists():
            PROGRESS_FILE.unlink()
        print("✓ Progreso reiniciado.")
    else:
        print("Operación cancelada.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Envío masivo con warm-up automático')
    parser.add_argument('--status', action='store_true', help='Ver estado actual')
    parser.add_argument('--send', action='store_true', help='Enviar lote de hoy')
    parser.add_argument('--reset', action='store_true', help='Reiniciar progreso')

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.send:
        send_today_batch()
    elif args.reset:
        reset_progress()
    else:
        # Por defecto, mostrar estado
        show_status()
        print()
        print("Comandos disponibles:")
        print("  python send_with_warmup.py --status   # Ver estado")
        print("  python send_with_warmup.py --send     # Enviar lote de hoy")
        print("  python send_with_warmup.py --reset    # Reiniciar progreso")


if __name__ == '__main__':
    main()
