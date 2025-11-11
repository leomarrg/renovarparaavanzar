#!/usr/bin/env python
"""
Script para verificar si Gravatar está configurado correctamente.
"""

import hashlib

def get_gravatar_url(email):
    """
    Genera la URL de Gravatar para un email.
    """
    # Normalizar email (lowercase y strip)
    email = email.lower().strip()

    # Crear hash MD5
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()

    # Generar URL
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}"
    gravatar_url_with_size = f"https://www.gravatar.com/avatar/{email_hash}?s=200&d=404"

    return gravatar_url, gravatar_url_with_size, email_hash


def main():
    emails = [
        'registro@renovarparaavanzar.com',
    ]

    print("=" * 70)
    print("VERIFICACIÓN DE GRAVATAR")
    print("=" * 70)
    print()

    for email in emails:
        url, url_with_size, email_hash = get_gravatar_url(email)

        print(f"Email: {email}")
        print(f"Hash MD5: {email_hash}")
        print(f"URL básica: {url}")
        print(f"URL de verificación: {url_with_size}")
        print()
        print("Para verificar:")
        print(f"1. Abre esta URL en tu navegador:")
        print(f"   {url_with_size}")
        print()
        print("2. Si ves la foto del doctor → ✓ Gravatar configurado correctamente")
        print("3. Si ves un error 404 → ✗ No hay imagen configurada para este email")
        print()
        print("-" * 70)
        print()

    print("NOTA IMPORTANTE:")
    print("- Gravatar puede tardar 15-30 minutos en propagarse")
    print("- Gmail y otros clientes hacen caché de fotos (puede tardar horas)")
    print("- Para forzar actualización en Gmail: envía desde un email nuevo")
    print("- Asegúrate de usar EXACTAMENTE el mismo email en Gravatar")
    print()
    print("Si la imagen aparece en la URL de Gravatar pero no en Gmail:")
    print("- Espera 1-2 horas para que el caché de Gmail se actualice")
    print("- O envía desde otro email diferente como prueba")
    print()


if __name__ == "__main__":
    main()
