#!/usr/bin/env python
"""
Script OPTIMIZADO para importación masiva y rápida de emails.
Diseñado para importar 6000+ registros en segundos.
"""

import os
import sys
import django
import csv
import time
from datetime import datetime
import random
import string
from django.db import transaction, connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.db.models import Max


class FastBulkImporter:
    """
    Importador optimizado para máxima velocidad.
    """

    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
        self.generated_ids = set()
        self.existing_emails = set()

    def generate_unique_ids(self, count):
        """
        Genera múltiples IDs únicos de una vez.
        """
        ids = []
        # Obtener IDs existentes de la BD
        existing = set(Registration.objects.values_list('unique_id', flat=True))

        while len(ids) < count:
            new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if new_id not in existing and new_id not in self.generated_ids:
                ids.append(new_id)
                self.generated_ids.add(new_id)

        return ids

    def load_existing_emails(self):
        """
        Carga todos los emails existentes en memoria para verificación rápida.
        """
        print("Cargando emails existentes...")
        self.existing_emails = set(
            Registration.objects.values_list('email', flat=True)
        )
        print(f"  {len(self.existing_emails)} emails ya en la base de datos")

    def read_csv_emails(self, file_path):
        """
        Lee emails del CSV de manera eficiente.
        """
        emails = []

        print(f"Leyendo archivo: {file_path}")

        try:
            # Detectar encoding
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'iso-8859-1']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        # Detectar si tiene headers
                        sample = f.read(1024)
                        f.seek(0)

                        has_header = '@' not in sample.split('\n')[0] if '\n' in sample else False

                        reader = csv.reader(f)

                        if has_header:
                            headers = next(reader)
                            # Buscar columna de email
                            email_col = None
                            for i, h in enumerate(headers):
                                if 'email' in h.lower() or 'correo' in h.lower():
                                    email_col = i
                                    break

                            if email_col is None:
                                # Si no hay columna email, asumir primera columna
                                email_col = 0
                        else:
                            email_col = 0

                        # Leer todos los emails
                        for row in reader:
                            if row and len(row) > email_col:
                                email = row[email_col].strip().lower()
                                if '@' in email and '.' in email:
                                    emails.append(email)

                    print(f"  Archivo leído con encoding: {encoding}")
                    break

                except UnicodeDecodeError:
                    continue

        except Exception as e:
            print(f"Error leyendo archivo: {e}")
            return []

        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_emails = []
        for email in emails:
            if email not in seen:
                seen.add(email)
                unique_emails.append(email)

        return unique_emails

    def import_batch(self, emails_batch, unique_ids):
        """
        Importa un lote de emails usando bulk_create.
        """
        registrations = []

        for email, unique_id in zip(emails_batch, unique_ids):
            registrations.append(
                Registration(
                    name="Doctor",
                    last_name="Médico Colegiado",
                    email=email,
                    phone_number="000-000-0000",
                    postal_address="Puerto Rico",
                    is_doctor=True,
                    specialty="Medicina General",
                    years_practicing=1,
                    is_licensed=True,
                    service_location="Puerto Rico",
                    needs_voting_help=False,
                    accepts_promotions=True,
                    accepts_terms=True,
                    unique_id=unique_id
                )
            )

        # Usar bulk_create con ignore_conflicts para máxima velocidad
        created = Registration.objects.bulk_create(
            registrations,
            batch_size=self.batch_size,
            ignore_conflicts=True
        )

        return len(created)

    def import_all(self, file_path):
        """
        Importa todos los emails del archivo CSV.
        """
        print("=" * 60)
        print("IMPORTACIÓN MASIVA RÁPIDA")
        print("=" * 60)
        print()

        start_time = time.time()

        # 1. Cargar emails existentes
        self.load_existing_emails()

        # 2. Leer emails del CSV
        all_emails = self.read_csv_emails(file_path)

        if not all_emails:
            print("No se encontraron emails válidos en el archivo.")
            return

        print(f"\nEmails encontrados en CSV: {len(all_emails)}")

        # 3. Filtrar solo emails nuevos
        new_emails = [e for e in all_emails if e not in self.existing_emails]

        print(f"Emails nuevos a importar: {len(new_emails)}")
        print(f"Emails duplicados (omitidos): {len(all_emails) - len(new_emails)}")

        if not new_emails:
            print("\nNo hay emails nuevos para importar.")
            return

        # 4. Mostrar muestra
        print("\nPrimeros 5 emails a importar:")
        for email in new_emails[:5]:
            print(f"  - {email}")
        if len(new_emails) > 5:
            print(f"  ... y {len(new_emails) - 5} más")

        # 5. Confirmar importación
        print()
        print("Configuración de importación:")
        print(f"  - Total a importar: {len(new_emails)}")
        print(f"  - Tamaño de lote: {self.batch_size}")
        print(f"  - Lotes necesarios: {(len(new_emails) + self.batch_size - 1) // self.batch_size}")
        print()
        print("Los registros se crearán con:")
        print("  - Nombre: Doctor")
        print("  - Apellido: Médico Colegiado")
        print("  - Es médico: Sí")
        print("  - Es colegiado: Sí")
        print("  - Acepta términos: Sí")
        print("  - Acepta promociones: Sí")
        print()

        print("¿Confirmas la importación? (escribe SI):")
        if input().strip().upper() != 'SI':
            print("Importación cancelada.")
            return

        # 6. Generar todos los IDs únicos de una vez
        print("\nGenerando IDs únicos...")
        all_unique_ids = self.generate_unique_ids(len(new_emails))

        # 7. Importar en lotes con transacción
        print("Iniciando importación...")
        print("-" * 40)

        total_imported = 0

        with transaction.atomic():
            for i in range(0, len(new_emails), self.batch_size):
                batch_emails = new_emails[i:i + self.batch_size]
                batch_ids = all_unique_ids[i:i + self.batch_size]

                batch_num = (i // self.batch_size) + 1
                total_batches = (len(new_emails) + self.batch_size - 1) // self.batch_size

                print(f"Lote {batch_num}/{total_batches}: Importando {len(batch_emails)} registros... ", end="")

                imported = self.import_batch(batch_emails, batch_ids)
                total_imported += len(batch_emails)  # Contamos los intentados

                print(f"[OK]")

        # 8. Verificar resultado
        end_time = time.time()
        elapsed = end_time - start_time

        # Contar registros reales en BD
        final_count = Registration.objects.filter(
            email__in=new_emails
        ).count()

        print()
        print("=" * 60)
        print("IMPORTACIÓN COMPLETADA")
        print("=" * 60)
        print(f"Tiempo total: {elapsed:.2f} segundos")
        print(f"Emails procesados: {len(new_emails)}")
        print(f"Registros creados: {final_count}")
        print(f"Velocidad: {len(new_emails) / elapsed:.0f} emails/segundo")

        # Guardar log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"import_log_{timestamp}.txt"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Importación masiva - {datetime.now()}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Archivo: {file_path}\n")
            f.write(f"Emails en CSV: {len(all_emails)}\n")
            f.write(f"Emails nuevos: {len(new_emails)}\n")
            f.write(f"Registros creados: {final_count}\n")
            f.write(f"Tiempo: {elapsed:.2f} segundos\n")
            f.write(f"Velocidad: {len(new_emails) / elapsed:.0f} emails/segundo\n")

        print(f"\nLog guardado en: {log_file}")
        print("\n¡Importación exitosa!")

        # Mostrar total en BD
        total_in_db = Registration.objects.filter(email__isnull=False).count()
        print(f"\nTotal de registros con email en la base de datos: {total_in_db}")


def main():
    """
    Función principal.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Importación RÁPIDA de emails desde CSV'
    )
    parser.add_argument(
        'csv_file',
        help='Archivo CSV con los emails'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Tamaño del lote para bulk_create (default: 1000)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Error: El archivo {args.csv_file} no existe.")
        sys.exit(1)

    importer = FastBulkImporter(batch_size=args.batch_size)
    importer.import_all(args.csv_file)


if __name__ == "__main__":
    main()