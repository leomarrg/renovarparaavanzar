#!/usr/bin/env python
"""
Script gestor de envíos masivos con reintentos automáticos y gestión de errores.
Divide el envío en lotes y maneja automáticamente los fallos.
"""

import os
import sys
import django
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class BatchEmailManager:
    """
    Gestor de envío de emails por lotes con control de estado.
    """

    def __init__(self, batch_size=100, delay_between_batches=60):
        """
        Args:
            batch_size: Número de emails por lote
            delay_between_batches: Segundos de espera entre lotes
        """
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.state_file = 'email_batch_state.json'
        self.state = self.load_state()

    def load_state(self):
        """
        Carga el estado del envío desde un archivo.
        """
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'last_sent_id': 0,
            'total_sent': 0,
            'total_failed': 0,
            'failed_emails': [],
            'started_at': None,
            'last_batch_at': None
        }

    def save_state(self):
        """
        Guarda el estado actual del envío.
        """
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def get_next_batch(self):
        """
        Obtiene el siguiente lote de registros a procesar.
        """
        # Obtener registros no procesados
        query = Registration.objects.filter(
            email__isnull=False,
            id__gt=self.state['last_sent_id']
        ).exclude(
            email__exact=''
        ).order_by('id')

        return query[:self.batch_size]

    def send_email_with_retry(self, registration, max_retries=3):
        """
        Envía un email con reintentos automáticos.
        """
        from send_survey_email import generate_email_html

        nombre_completo = f"{registration.name} {registration.last_name}".strip()
        if not nombre_completo:
            nombre_completo = "Estimado/a doctor/a"

        for attempt in range(max_retries):
            try:
                # Generar contenido
                html_content = generate_email_html(nombre_completo, registration.email)

                text_content = f"""
Estimado/a {nombre_completo},

Gracias por ser parte del movimiento Renovar para Avanzar.

TU OPINIÓN PUEDE HACER LA DIFERENCIA

Los resultados de esta encuesta ayudarán al Dr. Méndez Sexto y su equipo.

Solo te tomará 3-5 minutos.

COMPLETAR ENCUESTA:
https://us10.list-manage.com/survey?u=32f93d7ae2a7bd70efbba97b6&id=e194374f1d&e=54e0690aa6

Juntos renovamos, juntos avanzamos.

Dr. Méndez Sexto
#RenovarParaAvanzar
"""

                # Crear y enviar email
                email = EmailMultiAlternatives(
                    subject='Ayúdanos a fortalecer la campaña del Dr. Méndez Sexto - Encuesta',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[registration.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                return True, "Enviado"

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Espera exponencial
                else:
                    return False, str(e)

        return False, "Max reintentos alcanzado"

    def process_batch(self, batch):
        """
        Procesa un lote de registros.
        """
        batch_sent = 0
        batch_failed = 0

        print(f"\nProcesando lote de {len(batch)} emails...")
        print("-" * 40)

        for i, registration in enumerate(batch, 1):
            nombre = f"{registration.name} {registration.last_name}"
            print(f"[{i}/{len(batch)}] {registration.email} ({nombre})... ", end="")

            success, message = self.send_email_with_retry(registration)

            if success:
                print("[OK]")
                batch_sent += 1
                self.state['total_sent'] += 1
            else:
                print(f"[FALLO: {message[:30]}...]")
                batch_failed += 1
                self.state['total_failed'] += 1
                self.state['failed_emails'].append({
                    'email': registration.email,
                    'error': message,
                    'timestamp': datetime.now().isoformat()
                })

            # Actualizar último ID procesado
            self.state['last_sent_id'] = registration.id

            # Pausa entre emails
            time.sleep(0.5)

        return batch_sent, batch_failed

    def run(self, total_limit=None):
        """
        Ejecuta el proceso de envío por lotes.
        """
        print("=" * 60)
        print("GESTOR DE ENVÍO MASIVO POR LOTES")
        print("=" * 60)
        print()

        if self.state['started_at'] is None:
            self.state['started_at'] = datetime.now().isoformat()

        # Contar total de emails pendientes
        total_pending = Registration.objects.filter(
            email__isnull=False,
            id__gt=self.state['last_sent_id']
        ).exclude(email__exact='').count()

        print(f"Estado actual:")
        print(f"  - Emails enviados previamente: {self.state['total_sent']}")
        print(f"  - Emails fallidos: {self.state['total_failed']}")
        print(f"  - Emails pendientes: {total_pending}")
        print(f"  - Tamaño de lote: {self.batch_size}")
        print(f"  - Pausa entre lotes: {self.delay_between_batches} segundos")
        print()

        if total_pending == 0:
            print("No hay emails pendientes de enviar.")
            return

        # Confirmar
        print(f"¿Deseas continuar con el envío de {total_pending} emails?")
        print("Escribe 'SI' para confirmar:")
        if input().strip().upper() != 'SI':
            print("Envío cancelado.")
            return

        # Procesar lotes
        batch_number = 1
        total_processed = 0

        while True:
            # Obtener siguiente lote
            batch = self.get_next_batch()

            if not batch:
                break

            if total_limit and total_processed >= total_limit:
                print(f"\nLímite de {total_limit} emails alcanzado.")
                break

            print(f"\n{'='*40}")
            print(f"LOTE #{batch_number}")
            print(f"{'='*40}")

            # Procesar lote
            sent, failed = self.process_batch(batch)
            total_processed += sent + failed
            batch_number += 1

            # Guardar estado
            self.state['last_batch_at'] = datetime.now().isoformat()
            self.save_state()

            print(f"\nLote completado: {sent} enviados, {failed} fallidos")
            print(f"Total acumulado: {self.state['total_sent']} enviados, {self.state['total_failed']} fallidos")

            # Si hay más lotes, pausar
            if batch.count() == self.batch_size:
                print(f"\nPausando {self.delay_between_batches} segundos antes del siguiente lote...")
                time.sleep(self.delay_between_batches)

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """
        Imprime el resumen del envío.
        """
        print()
        print("=" * 60)
        print("RESUMEN FINAL DE ENVÍO")
        print("=" * 60)
        print(f"Total enviados: {self.state['total_sent']}")
        print(f"Total fallidos: {self.state['total_failed']}")
        print(f"Tasa de éxito: {self.state['total_sent'] / (self.state['total_sent'] + self.state['total_failed']) * 100:.1f}%")

        if self.state['failed_emails']:
            # Guardar emails fallidos en archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            failed_file = f"failed_emails_{timestamp}.txt"

            with open(failed_file, 'w') as f:
                for item in self.state['failed_emails']:
                    f.write(f"{item['email']}\t{item['error']}\t{item['timestamp']}\n")

            print(f"\nEmails fallidos guardados en: {failed_file}")

        print("\nProceso completado.")

    def reset_state(self):
        """
        Reinicia el estado del envío.
        """
        print("¿Estás seguro de que quieres reiniciar el estado? (SI/NO)")
        if input().strip().upper() == 'SI':
            self.state = {
                'last_sent_id': 0,
                'total_sent': 0,
                'total_failed': 0,
                'failed_emails': [],
                'started_at': None,
                'last_batch_at': None
            }
            self.save_state()
            print("Estado reiniciado.")

    def retry_failed(self):
        """
        Reintenta enviar los emails fallidos.
        """
        if not self.state['failed_emails']:
            print("No hay emails fallidos para reintentar.")
            return

        print(f"Hay {len(self.state['failed_emails'])} emails fallidos.")
        print("¿Deseas reintentar el envío? (SI/NO)")

        if input().strip().upper() != 'SI':
            return

        failed_to_retry = self.state['failed_emails'].copy()
        self.state['failed_emails'] = []

        for item in failed_to_retry:
            try:
                reg = Registration.objects.filter(email=item['email']).first()
                if reg:
                    success, message = self.send_email_with_retry(reg)
                    if success:
                        self.state['total_sent'] += 1
                        self.state['total_failed'] -= 1
                        print(f"[OK] {item['email']}")
                    else:
                        self.state['failed_emails'].append(item)
                        print(f"[FALLO] {item['email']}")
            except Exception as e:
                print(f"[ERROR] {item['email']}: {e}")
                self.state['failed_emails'].append(item)

        self.save_state()
        print(f"\nReintento completado. Aún fallan: {len(self.state['failed_emails'])}")


def main():
    """
    Función principal con opciones de línea de comandos.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Gestor de envío masivo de emails')
    parser.add_argument('--batch-size', type=int, default=100,
                      help='Tamaño del lote (default: 100)')
    parser.add_argument('--delay', type=int, default=60,
                      help='Segundos entre lotes (default: 60)')
    parser.add_argument('--limit', type=int,
                      help='Límite total de emails a enviar')
    parser.add_argument('--reset', action='store_true',
                      help='Reiniciar el estado del envío')
    parser.add_argument('--retry-failed', action='store_true',
                      help='Reintentar emails fallidos')
    parser.add_argument('--status', action='store_true',
                      help='Ver estado actual del envío')

    args = parser.parse_args()

    manager = BatchEmailManager(
        batch_size=args.batch_size,
        delay_between_batches=args.delay
    )

    if args.reset:
        manager.reset_state()
    elif args.retry_failed:
        manager.retry_failed()
    elif args.status:
        print("Estado actual del envío:")
        print(json.dumps(manager.state, indent=2, default=str))
    else:
        manager.run(total_limit=args.limit)


if __name__ == "__main__":
    main()