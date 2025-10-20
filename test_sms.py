#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client

print("PRUEBA DE ENVÍO DE SMS")
print("=" * 70)

# Tu número de teléfono para prueba
test_number = input("Ingresa tu número (formato: +17871234567): ")

if not test_number.startswith('+'):
    print("❌ El número debe empezar con + y código de país")
    exit()

message_text = "Prueba desde Renovar para Avanzar Dashboard ✅"

try:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=message_text,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=test_number
    )
    
    print(f"\n✅ SMS ENVIADO!")
    print(f"   SID: {message.sid}")
    print(f"   Status: {message.status}")
    print(f"   To: {message.to}")
    print(f"   From: {message.from_}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    
    if "unverified" in str(e).lower():
        print("\n⚠️  Número no verificado")
        print("Verifica tu número en:")
        print("https://console.twilio.com/us1/develop/phone-numbers/manage/verified")

print("=" * 70)