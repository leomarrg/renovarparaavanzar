# extraer_registros_mbox.py
import mailbox
import re
import csv
from email import policy
from email.parser import BytesParser

# Abre el archivo mbox
mbox = mailbox.mbox('tu_archivo.mbox')

registros = []

for message in mbox:
    # Filtrar solo correos enviados desde "Renovar para avanzar"
    from_header = message.get('From', '')
    subject = message.get('Subject', '')
    
    # Ajusta este filtro según tu caso
    if 'renovar' in from_header.lower() or 'renovar' in subject.lower():
        # Extraer destinatario
        to_email = message.get('To', '')
        
        # Extraer cuerpo del mensaje
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(part.get_payload())
                    break
        else:
            try:
                body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(message.get_payload())
        
        # Extraer email del destinatario
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', to_email)
        
        if email_match:
            email_dest = email_match.group(0)
            
            # Extraer nombre si está en el cuerpo (ajusta según tu formato)
            nombre = ""
            nombre_match = re.search(r'Hola\s+([^\n,]+)', body)
            if nombre_match:
                nombre = nombre_match.group(1).strip()
            
            registros.append({
                'email': email_dest,
                'nombre': nombre,
                'asunto': subject,
                'fecha': message.get('Date', '')
            })
            
            print(f"Encontrado: {email_dest} - {nombre}")

# Guardar en CSV
with open('registros_recuperados.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['email', 'nombre', 'asunto', 'fecha'])
    writer.writeheader()
    writer.writerows(registros)

print(f"\n✅ Total extraídos: {len(registros)} registros")
print("Archivo guardado: registros_recuperados.csv")