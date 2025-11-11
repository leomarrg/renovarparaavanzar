"""
Script para verificar el progreso de envío de emails y calcular el offset
"""
import os
import sys
import django

# Setup Django
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration

def check_email_progress():
    """Verificar cuántos emails quedan por enviar"""

    # Total de registros con email y suscritos
    total_with_email = Registration.objects.filter(
        email__isnull=False,
        unsubscribed=False
    ).exclude(email='').count()

    print("=" * 60)
    print("PROGRESO DE ENVÍO DE EMAILS")
    print("=" * 60)
    print()

    print(f"Total de registros con email (suscritos): {total_with_email}")
    print()

    # Si ya enviaste 2500
    enviados = 2500
    pendientes = total_with_email - enviados

    print(f"[OK] Emails enviados hasta ahora: {enviados}")
    print(f"[PENDIENTE] Emails pendientes: {pendientes}")
    print()

    # Calcular lotes restantes
    batch_size = 500
    lotes_restantes = (pendientes + batch_size - 1) // batch_size

    print(f"Lotes de {batch_size} restantes: {lotes_restantes}")
    print()

    # Mostrar primeros 5 registros que se enviarían
    next_registrations = Registration.objects.filter(
        email__isnull=False,
        unsubscribed=False
    ).exclude(email='').order_by('id')[enviados:enviados+5]

    print("Próximos 5 registros a enviar:")
    print("-" * 60)
    for i, reg in enumerate(next_registrations, 1):
        print(f"{i}. ID: {reg.id} | {reg.name} {reg.last_name} | {reg.email}")
    print()

    print("=" * 60)
    print("COMANDO PARA CONTINUAR:")
    print("=" * 60)
    print()
    print(f"python send_email_sendgrid.py --offset {enviados} --batch-size 500 --pause 60")
    print()
    print("Esto continuará enviando desde el registro {enviados + 1} en adelante")
    print()

if __name__ == '__main__':
    check_email_progress()
