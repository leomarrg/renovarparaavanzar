#!/usr/bin/env python
"""
Script para verificar el estado de SendGrid y diagnosticar problemas de envío.
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from sendgrid import SendGridAPIClient
except ImportError:
    print("ERROR: SendGrid no está instalado.")
    print("Ejecuta: pip install sendgrid")
    sys.exit(1)

# Configuración
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

if not SENDGRID_API_KEY:
    print("ERROR: SENDGRID_API_KEY no está configurado.")
    print("Configura la variable de entorno:")
    print("  export SENDGRID_API_KEY='SG.xxxxx.yyyyy'")
    sys.exit(1)


def check_sender_verification():
    """Verifica los senders verificados en SendGrid."""
    print("=" * 60)
    print("VERIFICANDO SENDERS AUTENTICADOS")
    print("=" * 60)
    print()

    sg = SendGridAPIClient(SENDGRID_API_KEY)

    try:
        # Verificar sender identity
        response = sg.client.verified_senders.get()

        if response.status_code == 200:
            import json
            data = json.loads(response.body)

            print(f"Senders verificados: {len(data.get('results', []))}")
            print()

            for sender in data.get('results', []):
                print(f"Email: {sender.get('from_email')}")
                print(f"  Nombre: {sender.get('from_name')}")
                print(f"  Verificado: {'Sí' if sender.get('verified') else 'NO - ESTE ES EL PROBLEMA'}")
                print(f"  Locked: {sender.get('locked')}")
                print()
        else:
            print(f"Status code: {response.status_code}")
            print(f"Body: {response.body}")
    except Exception as e:
        print(f"Error al verificar senders: {e}")
        print()


def check_domain_authentication():
    """Verifica la autenticación de dominio."""
    print("=" * 60)
    print("VERIFICANDO AUTENTICACIÓN DE DOMINIO")
    print("=" * 60)
    print()

    sg = SendGridAPIClient(SENDGRID_API_KEY)

    try:
        # Verificar dominios autenticados
        response = sg.client.whitelabel.domains.get()

        if response.status_code == 200:
            import json
            data = json.loads(response.body)

            if len(data) == 0:
                print("⚠️  NO HAY DOMINIOS AUTENTICADOS")
                print("Esto puede causar que los emails caigan en spam o no se entreguen.")
                print()
                print("Para autenticar tu dominio:")
                print("1. Ve a https://app.sendgrid.com/settings/sender_auth")
                print("2. Click en 'Authenticate Your Domain'")
                print("3. Sigue las instrucciones para agregar registros DNS")
                print()
            else:
                print(f"Dominios autenticados: {len(data)}")
                print()

                for domain in data:
                    print(f"Dominio: {domain.get('domain')}")
                    print(f"  Válido: {'Sí' if domain.get('valid') else 'NO'}")
                    print(f"  DNS válido: {'Sí' if domain.get('dns', {}).get('valid') else 'NO'}")
                    print()
        else:
            print(f"Status code: {response.status_code}")
    except Exception as e:
        print(f"Error al verificar dominios: {e}")
        print()


def check_recent_activity():
    """Verifica actividad reciente de emails."""
    print("=" * 60)
    print("ACTIVIDAD RECIENTE DE EMAILS")
    print("=" * 60)
    print()

    sg = SendGridAPIClient(SENDGRID_API_KEY)

    try:
        # Obtener estadísticas recientes
        params = {
            'start_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
        }

        response = sg.client.stats.get(query_params=params)

        if response.status_code == 200:
            import json
            data = json.loads(response.body)

            if len(data) > 0:
                latest = data[0]
                stats = latest.get('stats', [{}])[0]
                metrics = stats.get('metrics', {})

                print(f"Fecha: {latest.get('date')}")
                print(f"  Requests: {metrics.get('requests', 0)}")
                print(f"  Delivered: {metrics.get('delivered', 0)}")
                print(f"  Bounces: {metrics.get('bounces', 0)}")
                print(f"  Spam Reports: {metrics.get('spam_reports', 0)}")
                print(f"  Opens: {metrics.get('opens', 0)}")
                print(f"  Clicks: {metrics.get('clicks', 0)}")
                print()

                # Diagnóstico
                requests = metrics.get('requests', 0)
                delivered = metrics.get('delivered', 0)

                if requests > 0 and delivered == 0:
                    print("⚠️  PROBLEMA DETECTADO:")
                    print("Se enviaron emails pero NINGUNO fue entregado.")
                    print("Posibles causas:")
                    print("  1. Sender no verificado")
                    print("  2. Dominio no autenticado")
                    print("  3. IP en proceso de warm-up")
                    print()
                elif requests > delivered:
                    ratio = (delivered / requests) * 100
                    print(f"Tasa de entrega: {ratio:.1f}%")
                    if ratio < 95:
                        print("⚠️  Tasa de entrega baja. Revisa:")
                        print("  - Autenticación de dominio")
                        print("  - Lista de emails (evita bounces)")
                        print()
            else:
                print("No hay actividad reciente en las últimas 24 horas.")
                print()
        else:
            print(f"Status code: {response.status_code}")
    except Exception as e:
        print(f"Error al verificar actividad: {e}")
        print()


def check_suppression_lists():
    """Verifica listas de supresión."""
    print("=" * 60)
    print("LISTAS DE SUPRESIÓN")
    print("=" * 60)
    print()

    sg = SendGridAPIClient(SENDGRID_API_KEY)

    # Verificar bounces
    try:
        response = sg.client.suppression.bounces.get()
        if response.status_code == 200:
            import json
            bounces = json.loads(response.body)
            print(f"Bounces: {len(bounces)}")
        else:
            print(f"Bounces: Error {response.status_code}")
    except Exception as e:
        print(f"Bounces: Error - {e}")

    # Verificar blocks
    try:
        response = sg.client.suppression.blocks.get()
        if response.status_code == 200:
            import json
            blocks = json.loads(response.body)
            print(f"Blocks: {len(blocks)}")
        else:
            print(f"Blocks: Error {response.status_code}")
    except Exception as e:
        print(f"Blocks: Error - {e}")

    # Verificar spam reports
    try:
        response = sg.client.suppression.spam_reports.get()
        if response.status_code == 200:
            import json
            spam = json.loads(response.body)
            print(f"Spam Reports: {len(spam)}")
        else:
            print(f"Spam Reports: Error {response.status_code}")
    except Exception as e:
        print(f"Spam Reports: Error - {e}")

    print()


def main():
    print()
    print("DIAGNÓSTICO DE SENDGRID")
    print("=" * 60)
    print()

    # Verificar API Key
    print(f"API Key configurada: {'Sí' if SENDGRID_API_KEY else 'No'}")
    if SENDGRID_API_KEY:
        print(f"API Key (primeros 10 chars): {SENDGRID_API_KEY[:10]}...")
    print()

    # Ejecutar diagnósticos
    check_sender_verification()
    check_domain_authentication()
    check_recent_activity()
    check_suppression_lists()

    # Recomendaciones finales
    print("=" * 60)
    print("RECOMENDACIONES")
    print("=" * 60)
    print()
    print("Para evitar problemas de entrega:")
    print()
    print("1. ✅ Verifica tu sender email en SendGrid:")
    print("   https://app.sendgrid.com/settings/sender_auth/senders")
    print()
    print("2. ✅ Autentica tu dominio (SPF/DKIM):")
    print("   https://app.sendgrid.com/settings/sender_auth")
    print()
    print("3. ✅ Monitorea la actividad de emails:")
    print("   https://app.sendgrid.com/email_activity")
    print()
    print("4. ✅ Revisa estadísticas:")
    print("   https://app.sendgrid.com/statistics")
    print()


if __name__ == "__main__":
    main()
