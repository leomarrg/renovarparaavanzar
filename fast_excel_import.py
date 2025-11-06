#!/usr/bin/env python
"""
Script OPTIMIZADO para importación masiva desde archivos Excel (XLSX).
Diseñado para importar 6000+ registros en segundos.
"""

import os
import sys
import django
import time
from datetime import datetime
import random
import string
from django.db import transaction
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration


class FastExcelImporter:
    """
    Importador optimizado para archivos Excel.
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

    def read_excel_emails(self, file_path):
        """
        Lee emails del archivo Excel de manera eficiente.
        """
        emails = []

        print(f"Leyendo archivo Excel: {file_path}")

        try:
            # Leer el archivo Excel
            df = pd.read_excel(file_path, engine='openpyxl')

            print(f"  Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
            print(f"  Columnas encontradas: {', '.join(df.columns.tolist())}")

            # Buscar columna de email
            email_col = None

            # Buscar por nombre de columna
            for col in df.columns:
                col_lower = str(col).lower()
                if 'email' in col_lower or 'correo' in col_lower or 'mail' in col_lower:
                    email_col = col
                    print(f"  Columna de email detectada: '{col}'")
                    break

            # Si no se encuentra por nombre, buscar por contenido
            if email_col is None:
                for col in df.columns:
                    # Verificar si la columna contiene emails
                    sample = df[col].dropna().astype(str).head(10)
                    if sample.str.contains('@').any():
                        email_col = col
                        print(f"  Columna de email detectada por contenido: '{col}'")
                        break

            if email_col is None:
                # Usar la primera columna como fallback
                email_col = df.columns[0]
                print(f"  Usando primera columna por defecto: '{email_col}'")

            # Extraer emails
            for value in df[email_col].dropna():
                email = str(value).strip().lower()
                # Validar formato básico de email
                if '@' in email and '.' in email:
                    # Limpiar espacios y caracteres extraños
                    email = email.replace(' ', '')
                    emails.append(email)

            print(f"  Emails válidos encontrados: {len(emails)}")

        except Exception as e:
            print(f"Error leyendo archivo Excel: {e}")
            print("Asegúrate de tener pandas y openpyxl instalados:")
            print("  pip install pandas openpyxl")
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
        Importa todos los emails del archivo Excel.
        """
        print("=" * 60)
        print("IMPORTACIÓN MASIVA DESDE EXCEL")
        print("=" * 60)
        print()

        # Verificar que pandas está instalado
        try:
            import pandas
            import openpyxl
        except ImportError:
            print("ERROR: Necesitas instalar las dependencias:")
            print("  pip install pandas openpyxl")
            print()
            print("En el servidor ejecuta:")
            print("  source venv/bin/activate")
            print("  pip install pandas openpyxl")
            return

        start_time = time.time()

        # 1. Cargar emails existentes
        self.load_existing_emails()

        # 2. Leer emails del Excel
        all_emails = self.read_excel_emails(file_path)

        if not all_emails:
            print("No se encontraron emails válidos en el archivo.")
            return

        print(f"\nEmails encontrados en Excel: {len(all_emails)}")

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
        if elapsed > 0:
            print(f"Velocidad: {len(new_emails) / elapsed:.0f} emails/segundo")

        # Guardar log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"import_excel_log_{timestamp}.txt"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Importación desde Excel - {datetime.now()}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Archivo: {file_path}\n")
            f.write(f"Emails en Excel: {len(all_emails)}\n")
            f.write(f"Emails nuevos: {len(new_emails)}\n")
            f.write(f"Registros creados: {final_count}\n")
            f.write(f"Tiempo: {elapsed:.2f} segundos\n")
            if elapsed > 0:
                f.write(f"Velocidad: {len(new_emails) / elapsed:.0f} emails/segundo\n")

            # Guardar lista de emails importados
            f.write("\nEmails importados:\n")
            for email in new_emails[:100]:  # Primeros 100
                f.write(f"  {email}\n")
            if len(new_emails) > 100:
                f.write(f"  ... y {len(new_emails) - 100} más\n")

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
        description='Importación RÁPIDA de emails desde archivo Excel (XLSX)'
    )
    parser.add_argument(
        'excel_file',
        help='Archivo Excel (.xlsx) con los emails'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Tamaño del lote para bulk_create (default: 1000)'
    )
    parser.add_argument(
        '--sheet',
        type=str,
        default=None,
        help='Nombre de la hoja de Excel a leer (default: primera hoja)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.excel_file):
        print(f"Error: El archivo {args.excel_file} no existe.")
        sys.exit(1)

    if not args.excel_file.endswith(('.xlsx', '.xls')):
        print("Advertencia: El archivo no parece ser un Excel (.xlsx o .xls)")
        print("¿Deseas continuar de todos modos? (SI/NO)")
        if input().strip().upper() != 'SI':
            sys.exit(1)

    importer = FastExcelImporter(batch_size=args.batch_size)
    importer.import_all(args.excel_file)


if __name__ == "__main__":
    main()