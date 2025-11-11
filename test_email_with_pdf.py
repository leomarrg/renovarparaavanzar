#!/usr/bin/env python
"""
Script simple para probar el envío de email con PDF adjunto.
Verifica Gravatar y el adjunto al mismo tiempo.
"""

import os
import sys
import base64

# Verificar que SendGrid esté instalado
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Category, Attachment, FileContent, FileName, FileType, Disposition
except ImportError:
    print("ERROR: SendGrid no está instalado.")
    print("Ejecuta: pip install sendgrid")
    sys.exit(1)

# Configuración
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = 'registro@renovarparaavanzar.com'
PDF_PATH = r"C:\Users\Leomar\Documents\Proyectos\renovarparaavanzar\landing\static\landing\img\Flyer_Renovar_Para_Avanzar.pdf"

if not SENDGRID_API_KEY:
    print("ERROR: SENDGRID_API_KEY no está configurado.")
    print()
    print("Por favor, ejecuta:")
    print('  $env:SENDGRID_API_KEY="TU_API_KEY_AQUI"')
    print()
    print("O configura la variable de entorno SENDGRID_API_KEY")
    sys.exit(1)

if not os.path.exists(PDF_PATH):
    print(f"ERROR: No se encontró el archivo PDF en: {PDF_PATH}")
    sys.exit(1)

# Solicitar email de destino
print()
print("=" * 70)
print("PRUEBA DE EMAIL CON FLYER PDF Y GRAVATAR")
print("=" * 70)
print()
print("Este script enviara un email de prueba que incluye:")
print("  - El diseno actual con fondo teal y tipografia Montserrat")
print("  - La foto de Gravatar (si ya esta propagada)")
print("  - El flyer PDF adjunto")
print()

TEST_EMAIL = input("Ingresa el email de destino: ").strip()

if not TEST_EMAIL:
    print("ERROR: Debes proporcionar un email de destino.")
    sys.exit(1)

print()
print(f"Preparando email para: {TEST_EMAIL}")
print(f"Adjunto: {os.path.basename(PDF_PATH)} ({os.path.getsize(PDF_PATH) / 1024 / 1024:.2f} MB)")
print()

# HTML del email (mismo diseño que usamos en send_email_sendgrid.py)
html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Un frente común por la clase médica</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Forzar colores en dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #377e7c !important;
                color: white !important;
            }}
            .container {{
                background-color: #377e7c !important;
            }}
            .header {{
                background-color: #377e7c !important;
            }}
            .content {{
                background-color: #377e7c !important;
            }}
            .footer {{
                background-color: #2a615f !important;
            }}
        }}

        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #377e7c !important;
            color: white !important;
            -webkit-text-size-adjust: 100%;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #377e7c !important;
        }}
        .header {{
            background-color: #377e7c !important;
            padding: 40px 30px;
            text-align: center;
        }}
        .header img {{
            max-width: 250px;
            height: auto;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: white !important;
            font-size: 28px;
            margin: 0;
            font-weight: 700;
            line-height: 1.3;
            font-family: 'Montserrat', sans-serif;
        }}
        .content {{
            padding: 40px 30px;
            background-color: #377e7c !important;
        }}
        .greeting {{
            font-size: 20px;
            color: white !important;
            margin-bottom: 25px;
            font-weight: 600;
            font-family: 'Montserrat', sans-serif;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.8;
            color: white !important;
            margin-bottom: 25px;
            font-family: 'Montserrat', sans-serif;
        }}
        .message strong {{
            color: white !important;
            font-weight: 700;
        }}
        .highlight {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            padding: 25px;
            border-left: 4px solid white;
            margin: 30px 0;
            border-radius: 5px;
        }}
        .highlight p {{
            margin: 0;
            font-size: 17px;
            color: white !important;
            line-height: 1.6;
            font-weight: 500;
            font-family: 'Montserrat', sans-serif;
        }}
        .cta-section {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            padding: 30px;
            text-align: center;
            margin: 30px 0;
            border-radius: 8px;
            border: 2px solid white;
        }}
        .cta-text {{
            font-size: 24px;
            color: white !important;
            font-weight: 700;
            margin: 20px 0;
            font-family: 'Montserrat', sans-serif;
        }}
        .hashtag {{
            font-size: 22px;
            color: white !important;
            font-weight: 700;
            margin-top: 20px;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer {{
            background-color: #2a615f !important;
            color: white !important;
            padding: 30px;
            text-align: center;
        }}
        .footer-content {{
            margin-bottom: 20px;
        }}
        .footer-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 10px;
            color: white !important;
            font-family: 'Montserrat', sans-serif;
        }}
        .footer-subtitle {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9) !important;
            margin-bottom: 10px;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe {{
            margin-top: 20px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8) !important;
            font-family: 'Montserrat', sans-serif;
        }}
        .unsubscribe a {{
            color: white !important;
            text-decoration: underline;
        }}
        .legal {{
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7) !important;
            margin-top: 15px;
            font-family: 'Montserrat', sans-serif;
        }}
        .signature {{
            text-align: center;
            padding: 25px;
            font-style: italic;
            color: white !important;
            font-size: 18px;
            font-weight: 500;
            background-color: rgba(255, 255, 255, 0.1) !important;
            font-family: 'Montserrat', sans-serif;
        }}

        /* Gmail dark mode específico */
        [data-ogsc] body {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .container {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .header {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .content {{
            background-color: #377e7c !important;
        }}
        [data-ogsc] .footer {{
            background-color: #2a615f !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://www.renovarparaavanzar.com/static/landing/img/email/DR_x_RPA@4x.png" alt="Renovar para Avanzar" />
            <h1>Un frente común por la clase médica</h1>
        </div>

        <div class="content">
            <p class="greeting">Estimado colega,</p>

            <p class="message">
                <strong>No más promesas vacías ni comités sin resultados.</strong> Es momento de
                unirnos en un frente común para poner fin al dilema de los planes médicos y
                lograr incentivos contributivos que hagan justicia a nuestra clase médica.
            </p>

            <div class="highlight">
                <p>
                    El Dr. Méndez Sexto y su equipo representan una nueva visión:
                    <strong>resultados reales, diálogo efectivo y una defensa firme</strong>
                    en favor de los médicos y la salud de Puerto Rico.
                </p>
            </div>

            <p class="message">
                Te invitamos a ser parte del cambio.
            </p>

            <div class="cta-section">
                <p class="cta-text">
                    Vota por el Dr. Méndez Sexto y su equipo
                </p>
                <p class="hashtag">#RenovarParaAvanzar</p>
            </div>
        </div>

        <div class="signature">
            "Juntos renovamos, juntos avanzamos"
        </div>

        <div class="footer">
            <div class="footer-content">
                <div class="footer-title">Dr. Méndez Sexto</div>
                <div class="footer-subtitle">Candidato a la Presidencia del Colegio de Médicos</div>
                <div class="footer-subtitle">#RenovarParaAvanzar</div>
            </div>

            <div class="legal">
                Pagado por el Comité Dr. Méndez Sexto
            </div>

            <div class="unsubscribe">
                Si no deseas recibir más comunicaciones, puedes
                <a href="mailto:support@renovarparaavanzar.com?subject=Solicitud de baja">
                    darte de baja aquí
                </a>
            </div>
        </div>
    </div>
</body>
</html>
"""

text_content = """
EMAIL DE PRUEBA - Renovar para Avanzar

Estimado colega,

No más promesas vacías ni comités sin resultados. Es momento de unirnos en un frente común.

El Dr. Méndez Sexto y su equipo representan una nueva visión: resultados reales, diálogo efectivo y una defensa firme.

Te invitamos a ser parte del cambio.

¡Vota por el Dr. Méndez Sexto y su equipo!

#RenovarParaAvanzar

📎 Adjunto: Flyer_Renovar_Para_Avanzar.pdf

---
Dr. Méndez Sexto
Candidato a la Presidencia del Colegio de Médicos

Pagado por el Comité Dr. Méndez Sexto
"""

try:
    # Crear el mensaje
    message = Mail(
        from_email=(FROM_EMAIL, 'Dr. Méndez Sexto - Renovar para Avanzar'),
        to_emails=TEST_EMAIL,
        subject='[PRUEBA] Un frente común por la clase médica — ¡Renovar para avanzar!',
        plain_text_content=text_content,
        html_content=html_content
    )

    # Configurar Reply-To
    message.reply_to = 'support@renovarparaavanzar.com'

    # Agregar categorías
    message.add_category(Category('test'))
    message.add_category(Category('flyer_test'))

    # Leer y adjuntar el PDF
    print("Adjuntando PDF...")
    with open(PDF_PATH, 'rb') as f:
        data = f.read()
        encoded_file = base64.b64encode(data).decode()

    attached_file = Attachment(
        FileContent(encoded_file),
        FileName('Flyer_Renovar_Para_Avanzar.pdf'),
        FileType('application/pdf'),
        Disposition('attachment')
    )
    message.attachment = attached_file

    # Enviar
    print("Enviando email...")
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)

    print()
    print("=" * 70)
    print("RESULTADO")
    print("=" * 70)
    print()
    print(f"Status Code: {response.status_code}")

    if response.status_code in [200, 201, 202]:
        print()
        print("EMAIL ENVIADO EXITOSAMENTE")
        print()
        print("Ahora verifica:")
        print(f"  1. Tu bandeja de entrada en: {TEST_EMAIL}")
        print("  2. Aparece la foto del doctor en el remitente?")
        print("  3. El diseno tiene fondo teal y texto blanco?")
        print("  4. Esta adjunto el PDF del flyer?")
        print()
        print("Si no lo ves en el Inbox, revisa la carpeta de Promociones.")
        print()
        print("Puedes ver el estado del envio en:")
        print("  https://app.sendgrid.com/email_activity")
        print()
    else:
        print()
        print("ERROR AL ENVIAR")
        print(f"Response: {response.body}")
        print(f"Headers: {response.headers}")

except Exception as e:
    print()
    print("=" * 70)
    print("ERROR")
    print("=" * 70)
    print()
    print(f"Ocurrió un error: {e}")
    print()
    import traceback
    traceback.print_exc()
