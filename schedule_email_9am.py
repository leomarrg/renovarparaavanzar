"""
Script para programar envío de emails a las 9am hora de Puerto Rico
"""
import time
from datetime import datetime, timedelta
import pytz
import subprocess
import sys

def wait_until_9am_pr():
    """Espera hasta las 9:00 AM hora de Puerto Rico"""
    # Timezone de Puerto Rico (Atlantic Standard Time - no tiene DST)
    pr_tz = pytz.timezone('America/Puerto_Rico')

    while True:
        # Hora actual en Puerto Rico
        now_pr = datetime.now(pr_tz)
        print(f"Hora actual en PR: {now_pr.strftime('%Y-%m-%d %H:%M:%S')}")

        # Si ya pasaron las 9am hoy, programar para mañana
        target_time = now_pr.replace(hour=9, minute=0, second=0, microsecond=0)
        if now_pr >= target_time:
            target_time += timedelta(days=1)

        # Calcular tiempo de espera
        wait_seconds = (target_time - now_pr).total_seconds()
        wait_hours = wait_seconds / 3600

        print(f"El envío está programado para: {target_time.strftime('%Y-%m-%d %H:%M:%S')} hora PR")
        print(f"Tiempo de espera: {wait_hours:.2f} horas ({wait_seconds/60:.0f} minutos)")
        print("Presiona Ctrl+C para cancelar\n")

        try:
            # Actualizar cada minuto
            if wait_seconds > 60:
                time.sleep(60)
            else:
                time.sleep(wait_seconds)
                break
        except KeyboardInterrupt:
            print("\nProgramación cancelada por el usuario")
            sys.exit(0)

def run_email_campaign():
    """Ejecuta el script de envío de emails"""
    print("\n" + "="*60)
    print("INICIANDO ENVÍO DE EMAILS - 9:00 AM")
    print("="*60 + "\n")

    # Comando a ejecutar - continúa desde offset 2500
    cmd = [
        'python',
        'send_email_sendgrid.py',
        '--offset', '2500',
        '--limit', '3000',
        '--batch-size', '500',
        '--pause', '600',
        '--email-type', 'liderazgo_resultados'
    ]

    try:
        # Ejecutar el script
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("\n" + "="*60)
        print("ENVÍO COMPLETADO EXITOSAMENTE")
        print("="*60)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR en el envío: {e}")
        return e.returncode
    except Exception as e:
        print(f"\n❌ ERROR inesperado: {e}")
        return 1

if __name__ == '__main__':
    print("="*60)
    print("PROGRAMADOR DE EMAILS - 9:00 AM HORA PUERTO RICO")
    print("="*60 + "\n")

    # Esperar hasta las 9am
    wait_until_9am_pr()

    # Ejecutar campaña
    exit_code = run_email_campaign()
    sys.exit(exit_code)
