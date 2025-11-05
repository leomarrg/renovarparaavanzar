#!/usr/bin/env python
"""
Script para limpiar archivo CSV y dejar solo nombres completos y números de teléfono.
"""

import csv
import os
import sys
from datetime import datetime


def clean_phone_csv(input_file, output_file=None):
    """
    Limpia el archivo CSV dejando solo nombres y teléfonos.

    Args:
        input_file: Ruta del archivo CSV de entrada
        output_file: Ruta del archivo CSV de salida (opcional)
    """

    # Si no se especifica archivo de salida, generar uno automático
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}_limpio_{timestamp}.csv"

    print("=" * 60)
    print("LIMPIADOR DE CSV - NOMBRES Y TELÉFONOS")
    print("=" * 60)
    print()
    print(f"Archivo de entrada: {input_file}")
    print(f"Archivo de salida: {output_file}")
    print()

    try:
        # Verificar que el archivo existe
        if not os.path.exists(input_file):
            print(f"[ERROR] El archivo {input_file} no existe.")
            return False

        # Leer el archivo CSV original
        with open(input_file, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)

            # Verificar que las columnas necesarias existen
            if 'Nombre' not in reader.fieldnames or 'Apellidos' not in reader.fieldnames:
                print("[ERROR] El archivo no contiene las columnas 'Nombre' y 'Apellidos'")
                return False

            # Buscar columna de teléfono (puede tener varios nombres)
            phone_column = None
            possible_phone_columns = [
                'Telefono_Limpio',
                'Telefono_Formateado',
                'Telefono_Original',
                'Telefono',
                'Phone',
                'phone_number'
            ]

            for col in possible_phone_columns:
                if col in reader.fieldnames:
                    phone_column = col
                    break

            if not phone_column:
                print("[ERROR] No se encontró columna de teléfono en el archivo")
                print(f"Columnas disponibles: {', '.join(reader.fieldnames)}")
                return False

            print(f"Usando columna de teléfono: {phone_column}")
            print()

            # Crear archivo de salida limpio
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
                # Solo dos columnas: Nombre Completo y Teléfono
                fieldnames = ['Nombre_Completo', 'Telefono']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                processed = 0
                skipped = 0

                print("Procesando registros...")
                print("-" * 40)

                # Volver al inicio del archivo para leer los datos
                infile.seek(0)
                next(reader)  # Saltar el header

                for row in reader:
                    try:
                        # Obtener nombre completo
                        nombre = row.get('Nombre', '').strip()
                        apellidos = row.get('Apellidos', '').strip()
                        nombre_completo = f"{nombre} {apellidos}".strip()

                        # Obtener teléfono
                        telefono = row.get(phone_column, '').strip()

                        # Solo escribir si hay nombre y teléfono
                        if nombre_completo and telefono and telefono != 'N/A':
                            # Limpiar el teléfono de caracteres especiales si es necesario
                            telefono_limpio = ''.join(filter(str.isdigit, telefono))

                            # Si el teléfono tiene dígitos, escribirlo
                            if telefono_limpio:
                                writer.writerow({
                                    'Nombre_Completo': nombre_completo,
                                    'Telefono': telefono_limpio
                                })
                                processed += 1

                                # Mostrar progreso cada 10 registros
                                if processed % 10 == 0:
                                    print(f"  Procesados: {processed} registros")
                            else:
                                skipped += 1
                        else:
                            skipped += 1

                    except Exception as e:
                        print(f"  [ERROR] Error procesando registro: {e}")
                        skipped += 1

        print()
        print("=" * 60)
        print("RESUMEN DEL PROCESO")
        print("=" * 60)
        print(f"Registros procesados exitosamente: {processed}")
        print(f"Registros omitidos (sin datos válidos): {skipped}")
        print(f"Total de registros leídos: {processed + skipped}")
        print()
        print(f"Archivo limpio generado: {output_file}")
        print(f"Ubicación: {os.path.abspath(output_file)}")
        print()

        # Generar también una versión de texto simple (opcional)
        create_simple_version = input("¿Deseas generar también un archivo de texto simple? (s/n): ").lower()
        if create_simple_version == 's':
            generate_simple_text(output_file)

        return True

    except Exception as e:
        print(f"[ERROR] Error al procesar el archivo: {e}")
        return False


def generate_simple_text(csv_file):
    """
    Genera un archivo de texto simple con formato Nombre - Teléfono
    """
    try:
        txt_file = csv_file.replace('.csv', '.txt')

        with open(csv_file, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)

            with open(txt_file, 'w', encoding='utf-8') as outfile:
                for row in reader:
                    nombre = row.get('Nombre_Completo', '')
                    telefono = row.get('Telefono', '')
                    if nombre and telefono:
                        outfile.write(f"{nombre} - {telefono}\n")

        print(f"Archivo de texto simple generado: {txt_file}")
        print(f"Ubicación: {os.path.abspath(txt_file)}")

    except Exception as e:
        print(f"[ERROR] No se pudo generar archivo de texto: {e}")


def main():
    """
    Función principal
    """
    import argparse

    parser = argparse.ArgumentParser(description='Limpiar CSV dejando solo nombres y teléfonos')
    parser.add_argument('input_file', nargs='?',
                       default=r'C:\Users\Leomar\Documents\Proyectos\renovarparaavanzar\telefonos_registrados_20251105_180817.csv',
                       help='Archivo CSV de entrada')
    parser.add_argument('-o', '--output', type=str,
                       help='Archivo CSV de salida (opcional)')

    args = parser.parse_args()

    # Ejecutar limpieza
    success = clean_phone_csv(args.input_file, args.output)

    if success:
        print("Proceso completado exitosamente.")
    else:
        print("El proceso no se completó correctamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()