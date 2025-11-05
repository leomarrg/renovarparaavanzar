#!/usr/bin/env python
"""
Script para exportar todos los números de teléfono de usuarios registrados
en la plataforma Renovar para Avanzar a un archivo CSV.
"""

import os
import sys
import django
import csv
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration


def clean_phone_number(phone):
    """
    Limpia el número de teléfono eliminando caracteres especiales
    y dejando solo dígitos.
    """
    if phone:
        # Eliminar todos los caracteres que no sean dígitos
        cleaned = ''.join(filter(str.isdigit, phone))
        return cleaned
    return ''


def format_phone_number(phone):
    """
    Formatea el número de teléfono en un formato estándar (XXX) XXX-XXXX
    si tiene 10 dígitos.
    """
    cleaned = clean_phone_number(phone)
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    elif len(cleaned) == 11 and cleaned[0] == '1':
        # Si tiene código de país 1
        return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
    return phone  # Devolver el original si no se puede formatear


def export_phones_to_csv():
    """
    Exporta todos los números de teléfono a un archivo CSV.
    """
    print("=" * 60)
    print("EXPORTADOR DE TELÉFONOS - RENOVAR PARA AVANZAR")
    print("=" * 60)
    print()

    # Obtener todos los registros con número de teléfono
    registrations = Registration.objects.filter(
        phone_number__isnull=False
    ).exclude(
        phone_number__exact=''
    ).order_by('created_at')

    total = registrations.count()

    if total == 0:
        print("No hay usuarios registrados con número de teléfono.")
        return

    print(f"Total de usuarios con teléfono: {total}")
    print()

    # Generar nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"telefonos_registrados_{timestamp}.csv"

    # Crear el archivo CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'ID',
            'Nombre',
            'Apellidos',
            'Telefono_Original',
            'Telefono_Limpio',
            'Telefono_Formateado',
            'Email',
            'Es_Medico',
            'Especialidad',
            'Colegiado',
            'Necesita_Ayuda_Voto',
            'Acepta_Promociones',
            'Fecha_Registro',
            'Direccion_Postal',
            'Lugar_Servicio'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Exportando registros...")
        print("-" * 40)

        exported = 0
        skipped = 0

        for registration in registrations:
            try:
                # Preparar datos del registro
                row = {
                    'ID': registration.unique_id,
                    'Nombre': registration.name,
                    'Apellidos': registration.last_name,
                    'Telefono_Original': registration.phone_number,
                    'Telefono_Limpio': clean_phone_number(registration.phone_number),
                    'Telefono_Formateado': format_phone_number(registration.phone_number),
                    'Email': registration.email or 'N/A',
                    'Es_Medico': 'Sí' if registration.is_doctor else 'No',
                    'Especialidad': registration.specialty or 'N/A',
                    'Colegiado': 'Sí' if registration.is_licensed else 'No',
                    'Necesita_Ayuda_Voto': 'Sí' if registration.needs_voting_help else 'No',
                    'Acepta_Promociones': 'Sí' if registration.accepts_promotions else 'No',
                    'Fecha_Registro': registration.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Direccion_Postal': registration.postal_address or 'N/A',
                    'Lugar_Servicio': registration.service_location or 'N/A'
                }

                writer.writerow(row)
                exported += 1

                # Mostrar progreso
                if exported % 10 == 0:
                    print(f"  Exportados {exported} de {total} registros...")

            except Exception as e:
                print(f"  [ERROR] No se pudo exportar registro {registration.unique_id}: {str(e)}")
                skipped += 1

    print()
    print("=" * 60)
    print("RESUMEN DE EXPORTACIÓN")
    print("=" * 60)
    print(f"Total procesados: {exported + skipped}")
    print(f"Exportados exitosamente: {exported}")
    print(f"Omitidos por error: {skipped}")
    print()
    print(f"Archivo generado: {csv_filename}")
    print(f"Ubicación: {os.path.abspath(csv_filename)}")
    print()

    # Análisis adicional de los números
    print("ANÁLISIS DE NÚMEROS DE TELÉFONO")
    print("-" * 40)

    # Estadísticas de los números
    phone_lengths = {}
    for registration in registrations:
        cleaned = clean_phone_number(registration.phone_number)
        length = len(cleaned)
        if length in phone_lengths:
            phone_lengths[length] += 1
        else:
            phone_lengths[length] = 1

    print("Distribución por cantidad de dígitos:")
    for length, count in sorted(phone_lengths.items()):
        print(f"  {length} dígitos: {count} números")

    # Identificar prefijos más comunes (primeros 3 dígitos)
    prefixes = {}
    for registration in registrations:
        cleaned = clean_phone_number(registration.phone_number)
        if len(cleaned) >= 3:
            prefix = cleaned[:3]
            if prefix in prefixes:
                prefixes[prefix] += 1
            else:
                prefixes[prefix] = 1

    print()
    print("Top 10 prefijos más comunes:")
    sorted_prefixes = sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:10]
    for prefix, count in sorted_prefixes:
        print(f"  {prefix}: {count} números")

    print()
    print("Proceso completado exitosamente.")

    return csv_filename


def export_phones_simple():
    """
    Exporta solo los números de teléfono en un formato simple (un número por línea).
    """
    print()
    print("Generando archivo simple de teléfonos...")

    # Obtener todos los registros con número de teléfono
    registrations = Registration.objects.filter(
        phone_number__isnull=False
    ).exclude(
        phone_number__exact=''
    ).order_by('created_at')

    # Generar nombre del archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_filename = f"telefonos_simple_{timestamp}.txt"

    with open(txt_filename, 'w', encoding='utf-8') as txtfile:
        for registration in registrations:
            cleaned = clean_phone_number(registration.phone_number)
            if cleaned:
                txtfile.write(f"{cleaned}\n")

    print(f"Archivo simple generado: {txt_filename}")
    print(f"Ubicación: {os.path.abspath(txt_filename)}")

    return txt_filename


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Exportar números de teléfono de usuarios registrados')
    parser.add_argument('--simple', action='store_true',
                      help='Exportar solo números en formato simple (un número por línea)')
    parser.add_argument('--format', choices=['csv', 'txt', 'both'], default='csv',
                      help='Formato de exportación: csv (detallado), txt (simple), both (ambos)')

    args = parser.parse_args()

    try:
        if args.format == 'csv' or args.format == 'both':
            csv_file = export_phones_to_csv()

        if args.format == 'txt' or args.format == 'both' or args.simple:
            txt_file = export_phones_simple()

    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error inesperado: {str(e)}")
        sys.exit(1)