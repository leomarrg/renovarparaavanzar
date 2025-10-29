#!/usr/bin/env python
"""
Script para reintentar emails fallidos (SIN DUPLICADOS)
Uso: python retry_failed_unique.py
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
CONTACT_EMAIL = "info@drmendezsexto.com"

# URLs de las imágenes
IMAGE_URL_1 = f"{BASE_URL}/static/landing/img/email/1transparencia.jpg"
IMAGE_URL_2 = f"{BASE_URL}/static/landing/img/email/2transparencia.jpg"
IMAGE_URL_3 = f"{BASE_URL}/static/landing/img/email/3transparencia.jpg"
IMAGE_URL_4 = f"{BASE_URL}/static/landing/img/email/4transparencia.jpg"
LOGO_URL = f"{BASE_URL}/static/landing/img/DR_x_RPA@4x.png"

# Lista ÚNICA de emails que fallaron (sin duplicados)
FAILED_EMAILS_UNIQUE = [
    "erikarentas@yahoo.com",
    "johndanet@yahoo.com",
    "eurifernandeznunez@gmail.com",
    "yortiz78@hotmail.com",
    "neryriveramd@gmail.com",
    "h_cott@yahoo.com",
    "drjosegonzalez@msn.com",
    "ypizarro_fnp@yahoo.com",
    "kiimberlyramos@gmail.com",
    "womar1222@yahoo.com",
    "bernalaracelis@yahoo.com",
    "juanvicente.delriomartin@gmail.com",
    "juanc.martinez62@yahoo.com",
    "maggiepalacios@gmail.com",
    "luis.ruiz.instrumed@gmail.com",
    "isacolon13@gmail.com",
    "joseforinaalfonso@yahoo.com",
    "lopezrmd@gmail.com",
    "cristinalorenzopuesan@hotmail.com",
    "jjriveramd67@gmail.com",
    "drjjsi@gmail.com",
    "josebirrielpena@gmail.com",
    "joe_colpi@hotmail.com",
    "rv.carla511@gmail.com",
    "Cramosramos@hotmail.com",
    "evelynrodriguez20014@gmail.com",
    "lmdd231@gmail.com",
    "nancy.davila@upr.edu",
    "jjbrainmind@gmail.com",
    "DONQ0607@yahoo.com",
    "ayescmd@yahoo.com",
    "eravila1969@gmail.com",
    "jdominguezvillafanemd@yahoo.com",
    "andrea.pagan0404@gmail.com",
    "ang.roriz@outlook.com",
    "riveracinthia@hotmail.com",
    "majeren1946@gmail.com",
    "luisra12@hotmail.com",
    "sharon.millan.md@gmail.com",
    "ppkyque@yahoo.com",
    "dr.figueroa54@gmail.com",
    "creatudominiopr@gmail.com",
    "karlampr@yahoo.com",
    "ghadanaji90@gmail.com",
    "centropediatricolv@gmail.com",
    "paponoel2@gmail.com",
    "iniabelr@ysoo.com",
    "walisbeth.class@gmail.com",
    "javiertorresmd@outlook.com",
    "Ubimd@yahoo.com",
    "indiraallende@me.com",
    "abrahamdoc@gmail.com",
    "giraldezpsc@gmail.com",
    "vrsanchezquiles@yahoo.com",
    "garywehlert@gmail.com",
    "titapr12@gmail.com",
    "raulretina@gmail.com",
    "hrdmd@hotmail.com",
    "doctorfelixschmidt@gmail.com",
    "guillermopastrana@gmail.com",
    "beaumedics@gmail.com",
    "madelinesantosmd@yahoo.com",
    "albertcserrano0@gmail.com",
    "ejourdan711@gmail.com",
    "dr.alfonsomadridguzman@gmail.com",
    "rhaumd@yahoo.com",
    "roberto@robertoperez.com",
    "tatianadeleon3030@icloud.com",
    "moraimalandrau@yahoo.com",
    "rbetancourt@prmedcenter.com",
    "francmrm@aol.com",
    "jomarlisboa1@gmail.com",
    "aguilamorena203543@hotmail.com",
    "domingonevarez@outlook.com",
    "cibelletp@gmail.com",
    "e.bones@me.com",
    "robertocarlospagan@gmail.com",
]

# ============================================
# FUNCIONES
# ============================================

def load_template():
    """Carga el template HTML del email"""
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

def send_email_direct(email, nombre_completo, html_template):
    """Envía un email directamente a un destinatario"""
    
    # Reemplazar variables en el template
    html_content = html_template
    html_content = html_content.replace('{{ nombre_completo }}', nombre_completo)
    html_content = html_content.replace('{{ email_destinatario }}', email)
    html_content = html_content.replace('{{ url_imagen_1 }}', IMAGE_URL_1)
    html_content = html_content.replace('{{ url_imagen_2 }}', IMAGE_URL_2)
    html_content = html_content.replace('{{ url_imagen_3 }}', IMAGE_URL_3)
    html_content = html_content.replace('{{ url_imagen_4 }}', IMAGE_URL_4)
    html_content = html_content.replace('{{ url_logo }}', LOGO_URL)
    html_content = html_content.replace('{{ url_sitio_web }}', BASE_URL)
    html_content = html_content.replace('{{ email_contacto }}', CONTACT_EMAIL)
    
    # Generar versión texto
    text_content = generate_text_version(nombre_completo)
    
    # Enviar email
    email_msg = EmailMultiAlternatives(
        subject=SUBJECT,
        body=text_content,
        from_email=FROM_EMAIL,
        to=[email]
    )
    email_msg.attach_alternative(html_content, "text/html")
    email_msg.send()
    
    return True

# ============================================
# MAIN
# ============================================

def main():
    print('=' * 70)
    print('🔄 REINTENTO DE EMAILS FALLIDOS (ÚNICOS)')
    print('=' * 70)
    print()
    
    # Cargar template
    try:
        html_template = load_template()
        print('✅ Template HTML cargado correctamente')
    except FileNotFoundError as e:
        print(f'❌ ERROR: No se encontró el template: {e}')
        return
    
    print()
    
    # Crear diccionario de emails únicos con su info
    email_info = {}
    
    print('📋 Buscando información de los emails fallidos...')
    for email in FAILED_EMAILS_UNIQUE:
        # Buscar el primer registro con este email
        registro = Registration.objects.filter(email=email).first()
        if registro:
            email_info[email] = f"{registro.name} {registro.last_name}"
        else:
            email_info[email] = "Estimado/a Usuario"
    
    total = len(email_info)
    
    print()
    print(f'📊 Total de emails ÚNICOS a reintentar: {total}')
    print(f'⏱️  Pausa entre emails: 2 segundos (para evitar límites)')
    print()
    
    confirm = input(f'¿Confirmas reintentar {total} emails? (escribe SI para confirmar): ')
    if confirm != 'SI':
        print('❌ Reintento cancelado')
        return
    
    # Reintentar envíos
    enviados = 0
    fallidos = 0
    errores = []
    
    print()
    print('Iniciando reintento...')
    print()
    
    for i, (email, nombre_completo) in enumerate(email_info.items(), 1):
        try:
            send_email_direct(email, nombre_completo, html_template)
            enviados += 1
            print(f'[{i}/{total}] ✅ Enviado a: {email}')
            
            # Pausa más larga para evitar límites
            if i < total:
                time.sleep(2)
                
        except Exception as e:
            fallidos += 1
            error_msg = f'{email}: {str(e)}'
            errores.append(error_msg)
            print(f'[{i}/{total}] ❌ Error en: {email}')
            print(f'    Motivo: {str(e)}')
            
            # Si hay error de conexión, esperar más
            if 'Connection' in str(e):
                print('    ⏸️  Esperando 10 segundos antes de continuar...')
                time.sleep(10)
    
    # Reporte final
    print()
    print('=' * 70)
    print('📊 REPORTE FINAL DE REINTENTO')
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
    
    if enviados > 0:
        print('🎉 ¡Reintento completado!')
        print()
        print(f'📈 Resumen total del blast:')
        print(f'   - Primera ronda: 82 exitosos')
        print(f'   - Segunda ronda: {enviados} exitosos')
        print(f'   - TOTAL ENVIADOS: {82 + enviados} de 166')
        
        if fallidos > 0:
            print()
            print(f'⚠️  Aún hay {fallidos} emails fallidos.')
            print('   Puedes intentar enviarlos manualmente o esperar unas horas.')

if __name__ == '__main__':
    main()