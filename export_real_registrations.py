#!/usr/bin/env python
"""
Script para exportar SOLO las personas que se registraron manualmente,
excluyendo los 6000+ médicos que fueron importados automáticamente.
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


def export_real_registrations():
    """
    Exporta solo los registros reales (no los importados automáticamente).
    Elimina duplicados quedándose con el registro más reciente por email.
    """
    print("=" * 60)
    print("EXPORTAR REGISTROS MANUALES (REALES)")
    print("=" * 60)
    print()

    # Los registros importados tienen:
    # - name = "Doctor"
    # - last_name = "Médico Colegiado"
    # - phone_number = "000-000-0000"
    # - postal_address = "Puerto Rico"
    # Los registros reales tienen información personalizada

    # Obtener registros importados automáticamente
    imported_registrations = Registration.objects.filter(
        name="Doctor",
        last_name="Médico Colegiado",
        phone_number="000-000-0000",
        postal_address="Puerto Rico"
    )

    # Obtener todos los registros
    all_registrations = Registration.objects.all()

    # Registros reales = todos - importados
    real_registrations_all = Registration.objects.exclude(
        name="Doctor",
        last_name="Médico Colegiado",
        phone_number="000-000-0000",
        postal_address="Puerto Rico"
    ).order_by('created_at')

    # Eliminar duplicados por email (quedarse con el más reciente)
    unique_emails = {}
    duplicates_found = []

    for reg in real_registrations_all:
        email = reg.email.lower() if reg.email else None

        if email:
            if email in unique_emails:
                # Ya existe, comparar fechas
                existing = unique_emails[email]
                if reg.created_at > existing.created_at:
                    # El nuevo es más reciente
                    duplicates_found.append(existing)
                    unique_emails[email] = reg
                else:
                    # El existente es más reciente
                    duplicates_found.append(reg)
            else:
                unique_emails[email] = reg
        else:
            # No tiene email, agregar de todos modos
            unique_key = f"no_email_{reg.id}"
            unique_emails[unique_key] = reg

    # Convertir a lista
    real_registrations = list(unique_emails.values())
    real_registrations.sort(key=lambda x: x.created_at)

    print(f"Total de registros en la base de datos: {all_registrations.count()}")
    print(f"Registros importados automáticamente: {imported_registrations.count()}")
    print(f"Registros reales (con duplicados): {real_registrations_all.count()}")
    print(f"Duplicados encontrados: {len(duplicates_found)}")
    print(f"Registros ÚNICOS reales: {len(real_registrations)}")
    print()

    # Mostrar duplicados si existen
    if duplicates_found:
        print("DUPLICADOS ENCONTRADOS (se usará el más reciente):")
        dup_emails = {}
        for dup in duplicates_found:
            email = dup.email.lower() if dup.email else 'Sin email'
            if email not in dup_emails:
                dup_emails[email] = []
            dup_emails[email].append(dup)

        for email, dups in list(dup_emails.items())[:5]:
            print(f"  - {email}: {len(dups) + 1} registros")
        if len(dup_emails) > 5:
            print(f"  ... y {len(dup_emails) - 5} emails duplicados más")
        print()

    if len(real_registrations) == 0:
        print("No hay registros reales para exportar.")
        return

    # Mostrar algunos ejemplos
    print("Ejemplos de registros reales ÚNICOS:")
    for reg in real_registrations[:5]:
        print(f"  - {reg.name} {reg.last_name} ({reg.email}) - {reg.created_at.strftime('%Y-%m-%d')}")
    if len(real_registrations) > 5:
        print(f"  ... y {len(real_registrations) - 5} más")
    print()

    # Confirmar exportación
    print("¿Deseas exportar estos registros a CSV? (escribe SI):")
    if input().strip().upper() != 'SI':
        print("Exportación cancelada.")
        return

    # Generar nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"registros_reales_{timestamp}.csv"

    # Exportar a CSV
    print(f"\nExportando a {csv_filename}...")

    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = [
            'ID',
            'Nombre',
            'Apellidos',
            'Nombre_Completo',
            'Email',
            'Telefono',
            'Direccion_Postal',
            'Es_Medico',
            'Especialidad',
            'Anos_Practicando',
            'Es_Colegiado',
            'Lugar_Servicio',
            'Necesita_Ayuda_Voto',
            'Acepta_Promociones',
            'Acepta_Terminos',
            'Fecha_Registro',
            'Fecha_Actualizacion'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for reg in real_registrations:
            writer.writerow({
                'ID': reg.unique_id,
                'Nombre': reg.name,
                'Apellidos': reg.last_name,
                'Nombre_Completo': f"{reg.name} {reg.last_name}",
                'Email': reg.email or 'N/A',
                'Telefono': reg.phone_number or 'N/A',
                'Direccion_Postal': reg.postal_address or 'N/A',
                'Es_Medico': 'Sí' if reg.is_doctor else 'No',
                'Especialidad': reg.specialty or 'N/A',
                'Anos_Practicando': reg.years_practicing or 'N/A',
                'Es_Colegiado': 'Sí' if reg.is_licensed else 'No',
                'Lugar_Servicio': reg.service_location or 'N/A',
                'Necesita_Ayuda_Voto': 'Sí' if reg.needs_voting_help else 'No',
                'Acepta_Promociones': 'Sí' if reg.accepts_promotions else 'No',
                'Acepta_Terminos': 'Sí' if reg.accepts_terms else 'No',
                'Fecha_Registro': reg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Fecha_Actualizacion': reg.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })

    print()
    print("=" * 60)
    print("EXPORTACIÓN COMPLETADA")
    print("=" * 60)
    print(f"Archivo generado: {csv_filename}")
    print(f"Ubicación: {os.path.abspath(csv_filename)}")
    print(f"Registros exportados: {len(real_registrations)}")
    print()

    # Estadísticas adicionales
    print("ESTADÍSTICAS DE REGISTROS REALES ÚNICOS:")
    print("-" * 40)

    # Médicos vs no médicos
    medicos = sum(1 for r in real_registrations if r.is_doctor)
    no_medicos = len(real_registrations) - medicos
    print(f"Médicos: {medicos}")
    print(f"No médicos: {no_medicos}")

    # Con email vs sin email
    con_email = sum(1 for r in real_registrations if r.email)
    sin_email = len(real_registrations) - con_email
    print(f"Con email: {con_email}")
    print(f"Sin email: {sin_email}")

    # Necesitan ayuda de voto
    ayuda_voto = sum(1 for r in real_registrations if r.needs_voting_help)
    print(f"Necesitan ayuda con voto adelantado: {ayuda_voto}")

    # Aceptan promociones
    promociones = sum(1 for r in real_registrations if r.accepts_promotions)
    print(f"Aceptan promociones: {promociones}")

    # Especialidades más comunes
    print("\nTop 5 especialidades:")
    from collections import Counter
    especialidades = [r.specialty for r in real_registrations if r.specialty]
    top_esp = Counter(especialidades).most_common(5)

    for esp, count in top_esp:
        print(f"  - {esp}: {count}")

    # Registros por mes
    print("\nRegistros por mes:")
    meses = {}
    for reg in real_registrations:
        mes_key = reg.created_at.strftime('%Y-%m')
        mes_display = reg.created_at.strftime('%B %Y')
        if mes_key not in meses:
            meses[mes_key] = {'display': mes_display, 'count': 0}
        meses[mes_key]['count'] += 1

    sorted_meses = sorted(meses.items(), key=lambda x: x[0], reverse=True)[:6]
    for mes_key, data in sorted_meses:
        print(f"  - {data['display']}: {data['count']}")

    print("\n¡Exportación exitosa!")


def export_imported_registrations():
    """
    Exporta solo los registros importados (para verificación).
    """
    print("=" * 60)
    print("EXPORTAR REGISTROS IMPORTADOS AUTOMÁTICAMENTE")
    print("=" * 60)
    print()

    imported = Registration.objects.filter(
        name="Doctor",
        last_name="Médico Colegiado"
    ).order_by('created_at')

    print(f"Total de registros importados: {imported.count()}")
    print()

    if imported.count() == 0:
        print("No hay registros importados.")
        return

    print("¿Deseas exportar estos registros? (escribe SI):")
    if input().strip().upper() != 'SI':
        print("Exportación cancelada.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"registros_importados_{timestamp}.csv"

    print(f"\nExportando a {csv_filename}...")

    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['ID', 'Email', 'Fecha_Registro']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for reg in imported:
            writer.writerow({
                'ID': reg.unique_id,
                'Email': reg.email,
                'Fecha_Registro': reg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

    print(f"\nArchivo generado: {csv_filename}")
    print(f"Ubicación: {os.path.abspath(csv_filename)}")
    print(f"Registros exportados: {imported.count()}")


def compare_statistics():
    """
    Muestra estadísticas comparativas entre registros reales e importados.
    """
    print("=" * 60)
    print("COMPARACIÓN: REGISTROS REALES vs IMPORTADOS")
    print("=" * 60)
    print()

    real = Registration.objects.exclude(
        name="Doctor",
        last_name="Médico Colegiado"
    )

    imported = Registration.objects.filter(
        name="Doctor",
        last_name="Médico Colegiado"
    )

    total = Registration.objects.all().count()

    print(f"{'Categoría':<30} {'Reales':<15} {'Importados':<15} {'Total':<15}")
    print("-" * 75)
    print(f"{'Total de registros':<30} {real.count():<15} {imported.count():<15} {total:<15}")

    real_con_email = real.filter(email__isnull=False).exclude(email='').count()
    imported_con_email = imported.filter(email__isnull=False).exclude(email='').count()
    total_con_email = Registration.objects.filter(email__isnull=False).exclude(email='').count()
    print(f"{'Con email':<30} {real_con_email:<15} {imported_con_email:<15} {total_con_email:<15}")

    real_medicos = real.filter(is_doctor=True).count()
    imported_medicos = imported.filter(is_doctor=True).count()
    total_medicos = Registration.objects.filter(is_doctor=True).count()
    print(f"{'Son médicos':<30} {real_medicos:<15} {imported_medicos:<15} {total_medicos:<15}")

    real_colegiados = real.filter(is_licensed=True).count()
    imported_colegiados = imported.filter(is_licensed=True).count()
    total_colegiados = Registration.objects.filter(is_licensed=True).count()
    print(f"{'Son colegiados':<30} {real_colegiados:<15} {imported_colegiados:<15} {total_colegiados:<15}")

    print()


def main():
    """
    Función principal con menú de opciones.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Exportar registros reales vs importados'
    )
    parser.add_argument(
        '--mode',
        choices=['real', 'imported', 'compare'],
        default='real',
        help='Modo de operación: real (registros manuales), imported (importados), compare (comparar)'
    )

    args = parser.parse_args()

    if args.mode == 'real':
        export_real_registrations()
    elif args.mode == 'imported':
        export_imported_registrations()
    elif args.mode == 'compare':
        compare_statistics()


if __name__ == "__main__":
    main()