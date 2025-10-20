#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client

print("=" * 70)
print("VERIFICAR ESTADO DE MENSAJES SMS")
print("=" * 70)

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Obtener los últimos 10 mensajes
print("\nÚltimos mensajes enviados:\n")

messages = client.messages.list(limit=10)

for msg in messages:
    print("-" * 70)
    print(f"SID:        {msg.sid}")
    print(f"To:         {msg.to}")
    print(f"From:       {msg.from_}")
    print(f"Status:     {msg.status}")
    print(f"Direction:  {msg.direction}")
    print(f"Date:       {msg.date_created}")
    print(f"Price:      {msg.price} {msg.price_unit}")
    
    if msg.error_code:
        print(f"❌ ERROR:    {msg.error_code}")
        print(f"   Message:  {msg.error_message}")
    
    # Mostrar mensaje truncado
    body_preview = msg.body[:50] + "..." if len(msg.body) > 50 else msg.body
    print(f"Body:       {body_preview}")

print("-" * 70)

# Verificar información de la cuenta
print("\n" + "=" * 70)
print("INFORMACIÓN DE LA CUENTA")
print("=" * 70)

account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
print(f"Status:     {account.status}")
print(f"Type:       {account.type}")

# Verificar si es cuenta de trial
if account.type == 'Trial':
    print("\n⚠️  CUENTA DE PRUEBA (TRIAL)")
    print("=" * 70)
    print("Con cuenta de prueba solo puedes enviar SMS a:")
    print("1. Números verificados en Twilio")
    print("2. El número que usaste para registrarte")
    print()
    print("Para verificar un número:")
    print("👉 https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print()
    print("Para enviar a cualquier número:")
    print("👉 Actualiza tu cuenta en: https://console.twilio.com/us1/billing/upgrade")
    print("=" * 70)

# Obtener números verificados
print("\n" + "=" * 70)
print("NÚMEROS VERIFICADOS")
print("=" * 70)

try:
    validated_numbers = client.validationRequests.list(limit=20)
    
    if validated_numbers:
        print("\nNúmeros que puedes usar para pruebas:")
        for vn in validated_numbers:
            print(f"  ✓ {vn.phone_number}")
    else:
        print("\n❌ No hay números verificados")
        print("\nPara verificar +19392570148:")
        print("1. Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        print("2. Click en 'Add a new Caller ID'")
        print("3. Ingresa: +19392570148")
        print("4. Recibirás un código por SMS o llamada")
        print("5. Ingrésalo para verificar")
        
except Exception as e:
    print(f"\nNo se pudieron obtener números verificados: {e}")

print("\n" + "=" * 70)
print("SOLUCIÓN")
print("=" * 70)
print("\nOPCIÓN 1: Verificar tu número +19392570148")
print("  👉 https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
print()
print("OPCIÓN 2: Actualizar a cuenta de pago ($20 mínimo)")
print("  👉 https://console.twilio.com/us1/billing/upgrade")
print()
print("OPCIÓN 3: Usar solo emails por ahora")
print("  Los emails funcionan sin limitaciones")
print("=" * 70)