"""
Script simple para INSERTAR registros desde CSV
Solo inserta nuevos, salta los que ya existen

USO EN DJANGO SHELL (PythonAnywhere):
1. Subir CSV a: /home/tuusuario/registros_mendez_sexto_completos.csv
2. python manage.py shell
3. Copiar y pegar TODO el código de abajo
"""

import csv
from django.utils import timezone
from datetime import datetime
from tuapp.models import Registration  # ⚠️ CAMBIAR 'tuapp' por el nombre de tu app

# ⚠️ CAMBIAR la ruta a tu archivo CSV
CSV_PATH = 'registros_mendez_sexto_completos.csv'

print("🚀 Insertando registros...")
print("="*60)

created = 0
skipped = 0
errors = 0

with open(CSV_PATH, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        try:
            email = row['email'].strip()
            
            if not email:
                continue
            
            # Verificar si ya existe
            if Registration.objects.filter(email=email).exists():
                print(f'⏭️  Ya existe: {email}')
                skipped += 1
                continue
            
            # Parsear fecha
            try:
                fecha = datetime.strptime(row['fecha_registro'], '%Y-%m-%d %H:%M:%S')
                fecha = timezone.make_aware(fecha)
            except:
                fecha = timezone.now()
            
            # Preparar datos
            nombre = row.get('nombre', '').strip()
            apellidos = row.get('apellidos', '').strip()
            
            if not nombre and not apellidos:
                continue
            
            # Años ejerciendo
            años = row.get('años_ejerciendo', '').strip()
            años_ejerciendo = None
            if años and años != 'nan':
                try:
                    años_ejerciendo = int(float(años))
                except:
                    pass
            
            # Especialidad
            especialidad = row.get('especialidad', '').strip()
            if especialidad == 'nan':
                especialidad = ''
            
            # Booleanos
            es_medico = str(row.get('es_medico')).lower() in ['true', '1']
            es_colegiado = str(row.get('es_colegiado')).lower() in ['true', '1']
            ayuda_voto = str(row.get('necesita_ayuda_voto')).lower() in ['true', '1']
            
            # CREAR registro
            registration = Registration.objects.create(
                email=email,
                name=nombre,
                last_name=apellidos,
                postal_address=row.get('direccion_postal', '').strip(),
                phone_number=row.get('telefono', '').strip(),
                service_location=row.get('donde_provee_servicios', '').strip(),
                is_doctor=es_medico,
                years_practicing=años_ejerciendo,
                is_licensed=es_colegiado,
                specialty=especialidad,
                needs_voting_help=ayuda_voto,
                accepts_terms=True,
                accepts_promotions=True,
                created_at=fecha
            )
            
            print(f'✅ {nombre} {apellidos} ({email}) - ID: {registration.unique_id}')
            created += 1
            
        except Exception as e:
            print(f'❌ Error: {str(e)}')
            errors += 1

print("\n" + "="*60)
print("📊 RESUMEN")
print("="*60)
print(f"✅ Registros insertados: {created}")
print(f"⏭️  Ya existían (saltados): {skipped}")
print(f"❌ Errores: {errors}")
print("="*60)
print("✨ Completado")