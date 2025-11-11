#!/usr/bin/env python
"""
Script para enviar email de prueba con el flyer PDF adjunto.
Esto probará tanto Gravatar como el adjunto PDF.
"""

import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar el módulo de envío
from send_email_sendgrid import send_test_email

# Configuración
TEST_EMAIL = input("Ingresa el email de destino para la prueba: ").strip()
PDF_PATH = r"C:\Users\Leomar\Documents\Proyectos\renovarparaavanzar\landing\static\landing\img\Flyer_Renovar_Para_Avanzar.pdf"

if not TEST_EMAIL:
    print("ERROR: Debes proporcionar un email de destino.")
    sys.exit(1)

if not os.path.exists(PDF_PATH):
    print(f"ERROR: No se encontró el archivo PDF en: {PDF_PATH}")
    sys.exit(1)

print()
print("=" * 60)
print("PRUEBA DE EMAIL CON FLYER PDF")
print("=" * 60)
print()
print(f"Destinatario: {TEST_EMAIL}")
print(f"Adjunto: {os.path.basename(PDF_PATH)}")
print(f"Tamaño del PDF: {os.path.getsize(PDF_PATH) / 1024 / 1024:.2f} MB")
print()
print("Esta prueba verificará:")
print("  1. Si la foto de Gravatar ahora aparece en el email")
print("  2. Si el adjunto PDF se envía correctamente")
print()
print("Nota: Verifica en tu bandeja de entrada (o Promociones)")
print()

# Enviar el email de prueba con el adjunto
send_test_email(TEST_EMAIL, PDF_PATH)

print()
print("=" * 60)
print("INSTRUCCIONES PARA VERIFICAR")
print("=" * 60)
print()
print("1. Revisa tu email en:", TEST_EMAIL)
print("2. Verifica si aparece la foto del doctor en el remitente")
print("3. Verifica si el archivo PDF está adjunto")
print("4. Si no lo ves en el Inbox, revisa la carpeta de Promociones")
print()
