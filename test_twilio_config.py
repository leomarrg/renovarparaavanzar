#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("DIAGNÓSTICO DE TWILIO")
print("=" * 70)
print()

configs = {
    'TWILIO_ACCOUNT_SID': getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
    'TWILIO_AUTH_TOKEN': getattr(settings, 'TWILIO_AUTH_TOKEN', ''),
    'TWILIO_PHONE_NUMBER': getattr(settings, 'TWILIO_PHONE_NUMBER', ''),
}

all_configured = True

for key, value in configs.items():
    if value:
        if len(str(value)) > 10:
            masked = str(value)[:4] + "*" * 8 + str(value)[-4:]
        else:
            masked = "***"
        print(f"   ✓ {key}: {masked}")
    else:
        print(f"   ✗ {key}: NO CONFIGURADO")
        all_configured = False

print()

if not all_configured:
    print("=" * 70)
    print("🔴 TWILIO NO ESTÁ CONFIGURADO")
    print("=" * 70)
    print()
    print("📝 Edita tu archivo .env y agrega:")
    print()
    print("TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx")
    print("TWILIO_AUTH_TOKEN=tu_auth_token_aqui")
    print("TWILIO_PHONE_NUMBER=+15551234567")
    print()
    print("📚 Obtén credenciales en: https://console.twilio.com/")
    print("=" * 70)
else:
    print("✅ TWILIO CONFIGURADO")
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        print(f"✓ Conexión exitosa - Status: {account.status}")
    except Exception as e:
        print(f"✗ Error: {e}")

print()