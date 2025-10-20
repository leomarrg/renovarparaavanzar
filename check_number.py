#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client

print("=" * 70)
print("VERIFICAR NÚMERO DE TWILIO")
print("=" * 70)

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

print(f"\nNúmero configurado: {settings.TWILIO_PHONE_NUMBER}")
print()

try:
    # Buscar el número en la cuenta
    phone_numbers = client.incoming_phone_numbers.list(
        phone_number=settings.TWILIO_PHONE_NUMBER
    )
    
    if not phone_numbers:
        print("❌ PROBLEMA: Este número no está en tu cuenta de Twilio")
        print()
        print("Números disponibles en tu cuenta:")
        all_numbers = client.incoming_phone_numbers.list(limit=20)
        
        if all_numbers:
            for num in all_numbers:
                print(f"  • {num.phone_number}")
                print(f"    - Friendly Name: {num.friendly_name}")
                print(f"    - SMS Enabled: {num.capabilities['sms']}")
                print()
        else:
            print("  No tienes números activos")
            print()
            print("Necesitas comprar un número:")
            print("👉 https://console.twilio.com/us1/develop/phone-numbers/manage/search")
        
    else:
        number_info = phone_numbers[0]
        
        print("✓ Número encontrado")
        print()
        print("Información del número:")
        print(f"  • Phone Number: {number_info.phone_number}")
        print(f"  • Friendly Name: {number_info.friendly_name}")
        print(f"  • SID: {number_info.sid}")
        print()
        print("Capacidades:")
        print(f"  • Voice: {'✓' if number_info.capabilities['voice'] else '✗'}")
        print(f"  • SMS: {'✓' if number_info.capabilities['sms'] else '✗'}")
        print(f"  • MMS: {'✓' if number_info.capabilities['mms'] else '✗'}")
        print()
        
        if not number_info.capabilities['sms']:
            print("❌ PROBLEMA: SMS NO está habilitado en este número")
            print()
            print("Solución:")
            print("1. Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
            print(f"2. Busca el número: {settings.TWILIO_PHONE_NUMBER}")
            print("3. Verifica que tenga capacidad de SMS")
            print("4. O compra un nuevo número con SMS habilitado")
        else:
            print("✓ SMS está habilitado")
            print()
            print("❌ Pero hay error 30034 - Posibles causas:")
            print()
            print("1. CONFIGURACIÓN DE MESSAGING SERVICE")
            print("   El número necesita estar en un Messaging Service")
            print("   👉 https://console.twilio.com/us1/develop/sms/services")
            print()
            print("2. REGISTRO A2P (Application-to-Person)")
            print("   Para enviar SMS masivos necesitas registro A2P")
            print("   👉 https://console.twilio.com/us1/develop/sms/settings/a2p-registration")
            print()
            print("3. GEO PERMISSIONS (Puerto Rico)")
            print("   Verifica que puedes enviar a Puerto Rico")
            print("   👉 https://console.twilio.com/us1/develop/sms/settings/geo-permissions")
            print()
            print("4. TIPO DE NÚMERO")
            print("   Usa un número local de Puerto Rico (787/939)")
            print("   👉 https://console.twilio.com/us1/develop/phone-numbers/manage/search")

except Exception as e:
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("RECOMENDACIÓN")
print("=" * 70)
print()
print("Para enviar SMS a Puerto Rico necesitas:")
print()
print("1. Un número local de PR (787 o 939)")
print("2. Configurar Messaging Service")
print("3. Habilitar Puerto Rico en Geo Permissions")
print()
print("Pasos detallados:")
print("👉 https://support.twilio.com/hc/en-us/articles/223181868")
print("=" * 70)