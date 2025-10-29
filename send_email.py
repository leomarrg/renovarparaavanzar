#!/usr/bin/env python
"""
Script para enviar email blast sobre transparencia electoral
Uso: python send_email.py [--test] [--dry-run] [--to email@ejemplo.com]
"""

import os
import sys
import django
import time
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from landing.models import Registration

# ============================================
# CONFIGURACIÓN
# ============================================

SUBJECT = 'URGE TRANSPARENCIA EN EL PROCESO ELECTORAL DEL COLEGIO DE MÉDICOS'
FROM_EMAIL = settings.EMAIL_HOST_USER
BASE_URL = settings.SITE_URL

# Email de contacto para solicitudes de baja
CONTACT_EMAIL = "info@drmendezsexto.com"  # Email donde recibirás las solicitudes de baja

# URLs de las imágenes del email (desde landing/static/landing/img/email/)
IMAGE_URL_1 = f"{BASE_URL}/static/landing/img/email/1transparencia.jpg"
IMAGE_URL_2 = f"{BASE_URL}/static/landing/img/email/2transparencia.jpg"
IMAGE_URL_3 = f"{BASE_URL}/static/landing/img/email/3transparencia.jpg"
IMAGE_URL_4 = f"{BASE_URL}/static/landing/img/email/4transparencia.jpg"
LOGO_URL = f"{BASE_URL}/static/landing/img/DR_x_RPA@4x.png"

# ============================================
# FUNCIONES
# ============================================

def get_argument_value(arg_name):
    """Obtiene el valor de un argumento de línea de comandos"""
    try:
        idx = sys.argv.index(arg_name)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    except ValueError:
        pass
    return None

def load_template():
    """Carga el template HTML del email"""
    # Ruta correcta: landing/templates/landing/emails/
    template_path = os.path.join(BASE_DIR, 'landing', 'templates', 'landing', 'emails', 'email_transparencia.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_text_version(nombre_completo):
    """Genera versión texto plano del email"""
    return f"""
URGE TRANSPARENCIA EN EL PROCESO ELECTORAL DEL COLEGIO DE MÉDICOS

Estimado/a {nombre_completo},

¡Nuestro colegio y nuestros médicos merecen más!

Hoy hacemos público nuestro reclamo de apertura y transparencia al proceso electoral dentro del Colegio de Médicos Cirujanos de Puerto Rico. Exigimos un proceso transparente, justo y que se aleje de los escándalos y exabruptos del Presidente saliente. #RenovarParaAvanzar

Juntos renovamos, juntos avanzamos

Dr. Méndez Sexto
Candidato a la Presidencia
Colegio de Médicos y Cirujanos de Puerto Rico

#RenovarParaAvanzar

Visita: {BASE_URL}

---
Pagado por el Comité Dr. Méndez Sexto
    """.strip()

def send_email(registro, html_template, dry_run=False):
    """Envía un email a un registro específico"""
    # Preparar datos
    nombre_completo = f"{registro.name} {registro.last_name}"
    
    # Reemplazar variables en el template
    html_content = html_template
    html_content = html_content.replace('{{ nombre_completo }}', nombre_completo)
    html_content = html_content.replace('{{ email_destinatario }}', registro.email)
    html_content = html_content.replace('{{ url_imagen_1 }}', IMAGE_URL_1)
    html_content = html_content.replace('{{ url_imagen_2 }}', IMAGE_URL_2)
    html_content = html_content.replace('{{ url_imagen_3 }}', IMAGE_URL_3)
    html_content = html_content.replace('{{ url_imagen_4 }}', IMAGE_URL_4)
    html_content = html_content.replace('{{ url_logo }}', LOGO_URL)
    html_content = html_content.replace('{{ url_sitio_web }}', BASE_URL)
    html_content = html_content.replace('{{ email_contacto }}', CONTACT_EMAIL)
    
    # Generar versión texto
    text_content = generate_text_version(nombre_completo)
    
    if dry_run:
        return True  # Solo simular
    
    # Enviar email
    email = EmailMultiAlternatives(
        subject=SUBJECT,
        body=text_content,
        from_email=FROM_EMAIL,
        to=[registro.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    return True

def send_test_email_direct(email_destino, html_template, nombre="Dr. Juan Pérez"):
    """Envía un email de prueba directo a un email específico (sin registro en BD)"""
    
    # Reemplazar variables en el template
    html_content = html_template
    html_content = html_content.replace('{{ nombre_completo }}', nombre)
    html_content = html_content.replace('{{ url_imagen_1 }}', IMAGE_URL_1)
    html_content = html_content.replace('{{ url_imagen_2 }}', IMAGE_URL_2)
    html_content = html_content.replace('{{ url_imagen_3 }}', IMAGE_URL_3)
    html_content = html_content.replace('{{ url_imagen_4 }}', IMAGE_URL_4)
    html_content = html_content.replace('{{ url_logo }}', LOGO_URL)
    html_content = html_content.replace('{{ url_sitio_web }}', BASE_URL)
    html_content = html_content.replace('{{ email_contacto }}', CONTACT_EMAIL)
    html_content = html_content.replace('{{ email_destinatario }}', email_destino)
    
    # Generar versión texto
    text_content = generate_text_version(nombre)
    
    # Enviar email
    email = EmailMultiAlternatives(
        subject=f"[PRUEBA] {SUBJECT}",
        body=text_content,
        from_email=FROM_EMAIL,
        to=[email_destino]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    
    return True

# ============================================
# MAIN
# ============================================

def main():
    # Detectar modo
    is_test = '--test' in sys.argv
    is_dry_run = '--dry-run' in sys.argv
    test_email = get_argument_value('--to')
    
    # Banner
    print('=' * 70)
    print('📧 EMAIL BLAST - TRANSPARENCIA ELECTORAL')
    print('=' * 70)
    
    if test_email:
        print(f'🎯 MODO PRUEBA INDIVIDUAL - Enviando solo a: {test_email}')
    elif is_dry_run:
        print('⚠️  MODO SIMULACIÓN - No se enviarán emails reales')
    elif is_test:
        print('🧪 MODO PRUEBA - Solo primeros 5 emails')
    
    print()
    
    # Cargar template
    try:
        html_template = load_template()
        print('✅ Template HTML cargado correctamente')
        print(f'   Ubicación: landing/templates/landing/emails/email_transparencia.html')
    except FileNotFoundError as e:
        print('❌ ERROR: No se encontró el template email_transparencia.html')
        print('   Asegúrate de que está en: landing/templates/landing/emails/email_transparencia.html')
        print(f'   Error: {e}')
        return
    
    # Verificar configuración
    print()
    print('📋 Configuración:')
    print(f'   Subject: {SUBJECT}')
    print(f'   From: {FROM_EMAIL}')
    print(f'   Imagen 1: {IMAGE_URL_1}')
    print(f'   Imagen 2: {IMAGE_URL_2}')
    print(f'   Imagen 3: {IMAGE_URL_3}')
    print(f'   Imagen 4: {IMAGE_URL_4}')
    print(f'   Logo: {LOGO_URL}')
    print()
    
    # MODO: Enviar a un email específico
    if test_email:
        print(f'📊 Destinatario: {test_email}')
        print()
        
        confirm = input(f'¿Confirmas enviar email de prueba a {test_email}? (S/N): ')
        if confirm.upper() not in ['S', 'SI', 'YES', 'Y']:
            print('❌ Envío cancelado')
            return
        
        print()
        print('Enviando email de prueba...')
        
        try:
            send_test_email_direct(test_email, html_template)
            print()
            print('=' * 70)
            print('✅ ¡Email de prueba enviado exitosamente!')
            print('=' * 70)
            print()
            print(f'📬 Revisa tu bandeja de entrada en: {test_email}')
            print('💡 TIP: Si no lo ves, revisa la carpeta de spam/promociones')
            print()
            print('Checklist de verificación:')
            print('  ☐ El subject es correcto')
            print('  ☐ El banner amarillo se ve bien')
            print('  ☐ La imagen principal carga correctamente')
            print('  ☐ El texto es legible y está bien formateado')
            print('  ☐ El logo aparece al final')
            print('  ☐ Los enlaces de redes sociales funcionan')
            print('  ☐ El diseño se ve bien en móvil y desktop')
            print()
            print('Si todo está correcto, ejecuta sin --to para enviar a todos')
            
        except Exception as e:
            print()
            print('=' * 70)
            print(f'❌ Error al enviar el email de prueba: {e}')
            print('=' * 70)
        
        return
    
    # MODO: Enviar a todos los registros
    # Obtener registros
    registros = Registration.objects.exclude(email__isnull=True).exclude(email='')
    
    if is_test:
        registros = registros[:5]
    
    total = registros.count()
    
    if total == 0:
        print('❌ No hay registros con email en la base de datos')
        return
    
    print(f'📊 Total de destinatarios: {total}')
    print()
    
    # Confirmar (solo en modo producción)
    if not is_dry_run and not is_test:
        confirm = input(f'¿Confirmas enviar {total} emails? (escribe SI para confirmar): ')
        if confirm != 'SI':
            print('❌ Envío cancelado')
            return
    
    # Enviar emails
    enviados = 0
    fallidos = 0
    errores = []
    
    print()
    print('Iniciando envío...')
    print()
    
    for i, registro in enumerate(registros, 1):
        try:
            if is_dry_run:
                print(f'[{i}/{total}] 📧 SIMULARÍA envío a: {registro.email} ({registro.name} {registro.last_name})')
                enviados += 1
            else:
                send_email(registro, html_template, dry_run=False)
                enviados += 1
                print(f'[{i}/{total}] ✅ Enviado a: {registro.email}')
                
                # Pausa para no sobrecargar el servidor SMTP
                if not is_test:
                    time.sleep(0.5)
                
        except Exception as e:
            fallidos += 1
            error_msg = f'{registro.email}: {str(e)}'
            errores.append(error_msg)
            print(f'[{i}/{total}] ❌ Error en: {registro.email}')
            print(f'    Motivo: {str(e)}')
    
    # Reporte final
    print()
    print('=' * 70)
    print('📊 REPORTE FINAL')
    print('=' * 70)
    print(f'✅ Emails enviados exitosamente: {enviados}')
    print(f'❌ Emails fallidos: {fallidos}')
    
    if errores:
        print()
        print('Errores detallados:')
        for error in errores:
            print(f'  - {error}')
    
    print('=' * 70)
    print()
    
    if is_test and enviados > 0:
        print('💡 TIP: Revisa tu email para verificar que se ve bien.')
        print('   Si todo está correcto, ejecuta sin --test para enviar a todos.')
    elif is_dry_run and enviados > 0:
        print('💡 TIP: Esta fue una simulación. Ejecuta con --test para probar con 5 emails reales.')
    elif not is_dry_run and not is_test and enviados > 0:
        print('🎉 ¡Email blast completado exitosamente!')

if __name__ == '__main__':
    # Ayuda
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Uso: python send_email.py [OPCIONES]

Opciones:
  --to EMAIL   Enviar email de prueba a un destinatario específico
  --dry-run    Modo simulación (no envía emails reales)
  --test       Modo prueba (solo envía a los primeros 5 emails)
  --help, -h   Muestra esta ayuda

Ejemplos:
  python send_email.py --to tu-email@ejemplo.com    # Prueba individual
  python send_email.py --dry-run                    # Simular sin enviar
  python send_email.py --test                       # Probar con 5 emails
  python send_email.py                              # Enviar a todos

Flujo recomendado:
  1. python send_email.py --to tu-email@ejemplo.com  # Verificar diseño
  2. python send_email.py --test                     # Probar con 5 reales
  3. python send_email.py                            # Enviar a todos
        """)
        sys.exit(0)
    
    main()