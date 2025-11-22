#!/usr/bin/env python
"""
Script para optimizar imágenes para MMS.
Reduce el tamaño de archivo manteniendo buena calidad visual.
"""

from PIL import Image
import os

def optimize_image(input_path, output_path, max_size_kb=200, quality=85):
    """
    Optimiza una imagen para MMS.

    Args:
        input_path: Ruta de la imagen original
        output_path: Ruta donde guardar la imagen optimizada
        max_size_kb: Tamaño máximo deseado en KB
        quality: Calidad de compresión (1-100)
    """
    print(f"\nOptimizando: {input_path}")

    # Abrir imagen
    img = Image.open(input_path)

    # Obtener tamaño original
    original_size = os.path.getsize(input_path) / 1024
    print(f"  Tamaño original: {original_size:.1f} KB")
    print(f"  Dimensiones originales: {img.size[0]}x{img.size[1]} px")

    # Convertir a RGB si es necesario (para PNG con transparencia)
    if img.mode in ('RGBA', 'LA', 'P'):
        # Crear fondo blanco
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background

    # Determinar si necesitamos redimensionar
    max_dimension = 1200  # Máximo ancho o alto
    if img.size[0] > max_dimension or img.size[1] > max_dimension:
        # Calcular nuevo tamaño manteniendo aspect ratio
        if img.size[0] > img.size[1]:
            new_width = max_dimension
            new_height = int(img.size[1] * (max_dimension / img.size[0]))
        else:
            new_height = max_dimension
            new_width = int(img.size[0] * (max_dimension / img.size[1]))

        print(f"  Redimensionando a: {new_width}x{new_height} px")
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Guardar como JPEG con compresión
    current_quality = quality
    temp_path = output_path + '.temp.jpg'

    while current_quality > 50:
        img.save(temp_path, 'JPEG', quality=current_quality, optimize=True)
        file_size = os.path.getsize(temp_path) / 1024

        if file_size <= max_size_kb or current_quality <= 50:
            break

        current_quality -= 5

    # Renombrar archivo temporal al nombre final
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(temp_path, output_path)

    final_size = os.path.getsize(output_path) / 1024
    print(f"  [OK] Tamaño final: {final_size:.1f} KB (calidad: {current_quality})")
    print(f"  [OK] Reducción: {((original_size - final_size) / original_size * 100):.1f}%")
    print(f"  [OK] Guardado en: {output_path}")


if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'landing', 'static', 'landing', 'img', 'email')

    # Optimizar Vota_num2.png -> Vota_num2.jpg
    input_png = os.path.join(img_dir, 'Vota_num2.png')
    output_jpg = os.path.join(img_dir, 'Vota_num2.jpg')

    if os.path.exists(input_png):
        optimize_image(input_png, output_jpg, max_size_kb=200, quality=85)
    else:
        print(f"No se encontró: {input_png}")

    # Optimizar fechas_votacion.jpg
    input_fechas = os.path.join(img_dir, 'fechas_votacion.jpg')
    output_fechas = os.path.join(img_dir, 'fechas_votacion_optimized.jpg')

    if os.path.exists(input_fechas):
        optimize_image(input_fechas, output_fechas, max_size_kb=150, quality=85)
    else:
        print(f"No se encontró: {input_fechas}")

    print("\n[DONE] Optimizacion completada!")
    print("\nProximos pasos:")
    print("1. Verifica las imagenes optimizadas")
    print("2. Si te gustan, actualiza el codigo para usar las versiones .jpg")
