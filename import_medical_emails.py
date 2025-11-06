#!/usr/bin/env python
"""
Script para importar emails de médicos colegiados a la base de datos.
Los registros se crearán con información predeterminada.
"""

import os
import sys
import django
import csv
from datetime import datetime
import random
import string

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration


def generate_unique_id():
    """
    Genera un ID único de 6 caracteres.
    """
    while True:
        unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Registration.objects.filter(unique_id=unique_id).exists():
            return unique_id


def import_emails_from_file(file_path, dry_run=False):
    """
    Importa emails desde un archivo CSV o TXT.

    Args:
        file_path: Ruta del archivo con los emails
        dry_run: Si es True, no guarda en la base de datos
    """
    print("=" * 60)
    print("IMPORTADOR DE EMAILS DE MÉDICOS COLEGIADOS")
    print("=" * 60)
    print()
    print(f"Archivo de entrada: {file_path}")
    print()

    if not os.path.exists(file_path):
        print(f"[ERROR] El archivo {file_path} no existe.")
        return

    # Detectar formato del archivo
    file_extension = os.path.splitext(file_path)[1].lower()

    emails_to_import = []

    try:
        # Leer emails del archivo
        if file_extension == '.csv':
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                # Intentar detectar si hay headers
                first_row = next(reader, None)
                if first_row and '@' in first_row[0]:
                    # No hay headers, el primer elemento es un email
                    emails_to_import.append(first_row[0].strip().lower())
                elif first_row:
                    # Puede haber headers, buscar columna de email
                    email_col = None
                    for i, header in enumerate(first_row):
                        if 'email' in header.lower() or '@' in header:
                            email_col = i
                            break

                    if email_col is not None:
                        # Hay una columna de email específica
                        for row in reader:
                            if len(row) > email_col and '@' in row[email_col]:
                                emails_to_import.append(row[email_col].strip().lower())
                    else:
                        # Buscar emails en cualquier columna
                        f.seek(0)
                        reader = csv.reader(f)
                        for row in reader:
                            for cell in row:
                                if '@' in cell:
                                    emails_to_import.append(cell.strip().lower())
                                    break

        else:  # .txt u otro formato
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if '@' in line:
                        # Extraer el email de la línea
                        parts = line.split()
                        for part in parts:
                            if '@' in part:
                                email = part.strip().lower()
                                # Limpiar caracteres especiales comunes
                                email = email.strip(',;:')
                                emails_to_import.append(email)
                                break

    except Exception as e:
        print(f"[ERROR] Error al leer el archivo: {e}")
        return

    # Eliminar duplicados y validar formato básico
    unique_emails = []
    seen = set()

    for email in emails_to_import:
        if email not in seen and '@' in email and '.' in email:
            seen.add(email)
            unique_emails.append(email)

    print(f"Emails únicos encontrados: {len(unique_emails)}")

    if len(unique_emails) == 0:
        print("[ERROR] No se encontraron emails válidos en el archivo.")
        return

    # Verificar emails que ya existen en la base de datos
    existing_emails = set(
        Registration.objects.filter(
            email__in=unique_emails
        ).values_list('email', flat=True)
    )

    new_emails = [email for email in unique_emails if email not in existing_emails]

    print(f"Emails ya registrados: {len(existing_emails)}")
    print(f"Emails nuevos a importar: {len(new_emails)}")
    print()

    if len(new_emails) == 0:
        print("No hay emails nuevos para importar.")
        return

    if dry_run:
        print("[MODO DRY RUN] No se guardarán los datos en la base de datos.")
        print()
        print("Primeros 10 emails a importar:")
        for email in new_emails[:10]:
            print(f"  - {email}")
        if len(new_emails) > 10:
            print(f"  ... y {len(new_emails) - 10} más")
        return

    # Confirmar antes de importar
    print("Los registros se crearán con la siguiente información predeterminada:")
    print("  - Nombre: 'Doctor'")
    print("  - Apellido: 'Médico Colegiado'")
    print("  - Es médico: Sí")
    print("  - Es colegiado: Sí")
    print("  - Acepta términos: Sí")
    print("  - Acepta promociones: Sí")
    print("  - Dirección: 'Puerto Rico'")
    print("  - Teléfono: '000-000-0000'")
    print()
    print(f"¿Deseas importar {len(new_emails)} emails nuevos?")
    print("Escribe 'SI' para confirmar:")

    confirmacion = input().strip().upper()

    if confirmacion != 'SI':
        print("Importación cancelada.")
        return

    print()
    print("Importando emails...")
    print("-" * 40)

    imported = 0
    failed = 0
    errors = []

    # Importar por lotes para mayor eficiencia
    batch_size = 100
    registrations_to_create = []

    for i, email in enumerate(new_emails, 1):
        try:
            # Crear objeto Registration
            registration = Registration(
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
                unique_id=generate_unique_id()
            )

            registrations_to_create.append(registration)

            # Guardar por lotes
            if len(registrations_to_create) >= batch_size:
                Registration.objects.bulk_create(registrations_to_create)
                imported += len(registrations_to_create)
                print(f"  Importados: {imported} de {len(new_emails)}")
                registrations_to_create = []

        except Exception as e:
            failed += 1
            errors.append(f"Error con {email}: {str(e)}")

    # Guardar los registros restantes
    if registrations_to_create:
        try:
            Registration.objects.bulk_create(registrations_to_create)
            imported += len(registrations_to_create)
            print(f"  Importados: {imported} de {len(new_emails)}")
        except Exception as e:
            failed += len(registrations_to_create)
            errors.append(f"Error en lote final: {str(e)}")

    # Resumen final
    print()
    print("=" * 60)
    print("RESUMEN DE IMPORTACIÓN")
    print("=" * 60)
    print(f"Total de emails procesados: {len(unique_emails)}")
    print(f"Emails ya existentes (omitidos): {len(existing_emails)}")
    print(f"Emails nuevos importados: {imported}")
    print(f"Emails con error: {failed}")

    if errors:
        print("\nPrimeros errores encontrados:")
        for error in errors[:10]:
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... y {len(errors) - 10} errores más")

    # Guardar registro de importación
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"import_log_{timestamp}.txt"

    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Importación de emails - {datetime.now()}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Archivo de origen: {file_path}\n")
        f.write(f"Total procesados: {len(unique_emails)}\n")
        f.write(f"Ya existentes: {len(existing_emails)}\n")
        f.write(f"Importados: {imported}\n")
        f.write(f"Con error: {failed}\n")
        f.write("\n")

        if errors:
            f.write("Errores:\n")
            for error in errors:
                f.write(f"  - {error}\n")

    print()
    print(f"Log de importación guardado en: {log_file}")
    print("Proceso completado.")


def main():
    """
    Función principal del script.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Importar emails de médicos colegiados a la base de datos'
    )
    parser.add_argument(
        'file_path',
        help='Ruta del archivo CSV o TXT con los emails'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula la importación sin guardar en la base de datos'
    )
    parser.add_argument(
        '--custom-name',
        type=str,
        default='Doctor',
        help='Nombre personalizado para los registros (default: Doctor)'
    )
    parser.add_argument(
        '--custom-lastname',
        type=str,
        default='Médico Colegiado',
        help='Apellido personalizado para los registros (default: Médico Colegiado)'
    )

    args = parser.parse_args()

    # Ejecutar importación
    import_emails_from_file(args.file_path, args.dry_run)


if __name__ == "__main__":
    main()