from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone
import json
from datetime import datetime, timedelta
import traceback
import threading
import requests
from .models import PlanEstrategico

def send_email_async(registration):
    """Enviar email - versión síncrona confiable"""
    try:
        print(f"📧 Enviando email a {registration.email}...")
        register_view = RegisterView()
        result = register_view.send_confirmation_email(registration)
        if result:
            print(f"✅ Email enviado a {registration.email}")
        else:
            print(f"❌ Email falló para {registration.email}")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False


class IndexView(TemplateView):
    """Vista principal del landing page - Dr. Méndez Sexto"""
    template_name = 'landing/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Importar el formulario
        try:
            from .forms import RegistrationForm
            context['registration_form'] = RegistrationForm()
        except ImportError:
            context['registration_form'] = None
        
        # Información del candidato
        context['candidate'] = {
            'name': 'Dr. Méndez Sexto',
            'title': 'PRESIDENTE DEL COLEGIO DE',
            'subtitle': 'MÉDICOS Y CIRUJANOS',
            'campaign_slogan': 'Renovar para Avanzar',
            'message': 'Tu apoyo impulsa la transformación del colegio y la salud de Puerto Rico'
        }
        
        # Información de donación
        context['donation'] = {
            'platform': 'Pay Business',
            'handle': '/comitedrmendezsexto',
            'qr_code': 'landing/img/qr-donation.png',
            'legal_text': 'Este comité está debidamente registrado como una entidad sin fines de lucro y en cumplimiento con las leyes aplicables.',
            'hashtag': '#RenovarParaAvanzar'
        }
        
        # Equipo de candidatos
        context['team_members'] = [
            {
                'id': 1,
                'name': 'Dr. Méndez Sexto',
                'role': 'Médico Generalista',
                'district': 'Presidente',
                'image': 'landing/img/miembros/'
            },
            {
                'id': 2,
                'name': 'Dra. Sharon Millán Aponte',
                'role': 'Médico Generalista', 
                'district': 'Secretaria',
                'image': 'landing/img/miembros/dra_sharon_milan.jpg'
            },
            {
                'id': 3,
                'name': 'Dra. Kimberly Ramos',
                'role': 'Médico Generalista',
                'district': 'Presidenta del Senado',
                'image': 'landing/img/team/member-3.jpg'
            },
            {
                'id': 4,
                'name': 'Dr. Juan Rodríguez Vélez',
                'role': 'Psiquiatra',
                'district': 'Tesorero',
                'image': 'landing/img/miembros/dr_juan_rivera.jpg'
            },
            {
                'id': 5,
                'name': 'Dr. Guillermo Pastrana',
                'role': 'Médico Generalista',
                'district': 'Presidente Fundación Médica',
                'image': 'landing/img/team/member-5.jpg'
            },
            {
                'id': 6,
                'name': 'Dr. Edgar Reyes',
                'role': 'Otorrinolaringólogo, Cirugía Plástica Facial',
                'district': 'Presidente Instituto de Educación Continua',
                'image': 'landing/img/miembros/rd_edgar_reyes.jpg'
            },
            {
                'id': 7,
                'name': 'Dr. Juan Rivera',
                'role': 'Médico Generalista',
                'district': 'Vicepresidente',
                'image': 'landing/img/team/member-7.jpg'
            },
            {
                'id': 8,
                'name': 'Dra. Érika Rentas',
                'role': 'Médica Generalista',
                'district': 'Presidenta del Fideicomiso de Ayuda al Colegiado',
                'image': 'landing/img/miembros/dra_erika.jpg'
            },
        ]
        
        # Miembro destacado (Juan del Pueblo - Vocal)
        context['featured_member'] = {
            'name': 'Dra. Ida R. Cordero',
            'role': 'Médico Generalista',
            'district': 'Presidenta de Investigación Clínica',
            'image': 'landing/img/miembros/dra_erika.jpg'
        }
        
        plan_estrategico = PlanEstrategico.objects.filter(activo=True).first()

        # DEBUG
        print("=" * 50)
        print(f"Plan Estratégico: {plan_estrategico}")
        if plan_estrategico:
            print(f"  ✓ Título: {plan_estrategico.titulo}")
            print(f"  ✓ PDF: {plan_estrategico.archivo_pdf}")
        print("=" * 50)

        context['plan_estrategico'] = plan_estrategico

        
        # Countdown para las elecciones
        election_date = datetime(2024, 3, 15, 18, 0, 0)
        now = datetime.now()
        time_remaining = election_date - now
        
        context['countdown'] = {
            'days': time_remaining.days,
            'hours': time_remaining.seconds // 3600,
            'minutes': (time_remaining.seconds % 3600) // 60,
            'seconds': time_remaining.seconds % 60
        }
        
        # Social Media Links
        context['social_media'] = {
            'facebook': 'https://facebook.com/renovarparaavanzar',
            'twitter': 'https://twitter.com/renovarparaavanzar',
            'instagram': 'https://instagram.com/renovarparaavanzar',
            'linkedin': 'https://linkedin.com/company/renovarparaavanzar'
        }
        
        # Meta tags para SEO
        context['meta'] = {
            'title': 'Dr. Méndez Sexto - Renovar para Avanzar',
            'description': 'Únete al movimiento de transformación del Colegio de Médicos y Cirujanos de Puerto Rico',
            'keywords': 'Dr. Méndez Sexto, Colegio de Médicos, Puerto Rico, elecciones, salud',
            'og_image': 'landing/img/logo-renovar.png',
        }
        
        return context


def donation_test(request):
    """Vista simple para probar ATH Móvil"""
    
    context = {
        'page_title': 'Test Donaciones ATH Móvil',
    }
    
    return render(request, 'landing/test_ath.html', context)

class IndexWithRegistrationView(IndexView):
    """Vista que muestra index pero salta directamente a la sección de registro"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scroll_to_register'] = True
        return context


class RegisterAPIView(View):
    """API para procesar el registro via AJAX desde index.html"""
    
    def post(self, request):
        try:
            from .forms import RegistrationForm
            from .models import Registration
        except ImportError as e:
            return JsonResponse({
                'success': False,
                'message': f"Error de configuración: {str(e)}"
            })
        
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Guardar el registro
                registration = form.save(commit=False)
                registration.save()
                
                # Enviar email de forma asíncrona si se proporcionó
                email_sent = False
                if registration.email:
                    send_email_async(registration)
                    email_sent = True
                
                return JsonResponse({
                    'success': True,
                    'message': f'¡Registro exitoso! Tu código de confirmación es: {registration.unique_id}',
                    'unique_id': registration.unique_id,
                    'name': f'{registration.name} {registration.last_name}',
                    'email_sent': email_sent
                })
                
            except Exception as e:
                print(f"Error guardando registro: {e}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error al guardar el registro. Por favor intenta de nuevo.'
                })
        else:
            # Recopilar errores del formulario
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            
            return JsonResponse({
                'success': False,
                'message': 'Por favor corrige los errores en el formulario.',
                'errors': errors
            })


class RegisterView(IndexView):
    """Vista para registro de voluntarios y simpatizantes"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scroll_to_register'] = True
        return context
    
    def post(self, request):
        try:
            from .forms import RegistrationForm
            from .models import Registration
        except ImportError as e:
            messages.error(request, f"Error de configuración: {str(e)}")
            return redirect('landing:index')
        
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                registration = form.save()
                
                # Enviar email de forma asíncrona
                if registration.email:
                    send_email_async(registration)
                    email_status = "Se ha enviado un correo de confirmación a tu email."
                else:
                    email_status = ""
                
                # Crear mensaje simple de éxito
                success_message = f'¡Registro exitoso! {registration.name} {registration.last_name} ha sido registrado.'
                if email_status:
                    success_message += f' {email_status}'
                
                messages.success(request, success_message)
                return redirect('landing:index')
                
            except Exception as e:
                print(f"Error en el registro: {str(e)}")
                traceback.print_exc()
                messages.error(request, "Hubo un problema con el registro. Por favor intenta de nuevo.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields[field].label if field in form.fields else field.replace('_', ' ').title()
                    messages.error(request, f"{field_name}: {error}")
        
        return redirect('landing:index')
    
    def send_confirmation_email(self, registration):
        """Enviar email de confirmación"""
        try:
            subject = 'Gracias por el apoyo - Renovar para Avanzar'
            from_email = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@renovarparaavanzar.com'
            to_email = registration.email
            
            html_content = self.generate_email_html(registration)
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to_email]
            )
            
            email.attach_alternative(html_content, "text/html")
            email.send()
            print(f"Email de confirmación enviado exitosamente a {to_email}")
            
            return True
        
        except Exception as e:
            print(f"Error enviando email de confirmación: {e}")
            traceback.print_exc()
            return False

    def generate_email_html(self, registration):
        """Generar el HTML del email de confirmación"""
        from django.conf import settings
        
        site_url = settings.SITE_URL.rstrip('/')
        logos_img = f"{site_url}/static/landing/img/dr_rpa.rev@2x.png"
        ath_logo = f"{site_url}/static/landing/img/ATHM-logo-horizontal.png"
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    background: #ffffff;
                    max-width: 600px;
                    margin: 0 auto;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #4DB6AC, #00897B);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 700;
                    color: white;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    color: white;
                }}
                .thank-you-box {{
                    background: #377e7c;
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .thank-you-box p {{
                    font-size: 16px;
                    line-height: 1.8;
                    margin: 0 0 25px 0;
                    font-weight: 500;
                    color: white;
                }}
                .thank-you-box img {{
                    max-width: 400px;
                    width: 100%;
                    height: auto;
                    margin-top: 20px;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .content {{
                    padding: 30px;
                }}
                .info-section {{
                    background: #f8f9fa;
                    border-left: 4px solid #377e7c;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .info-section h3 {{
                    color: #377e7c;
                    margin-top: 0;
                    margin-bottom: 15px;
                    font-size: 18px;
                }}
                .info-row {{
                    margin: 12px 0;
                    padding: 10px 0;
                    border-bottom: 1px solid #e0e0e0;
                    color: #333;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    font-weight: 700;
                    color: #377e7c;
                    display: inline-block;
                    min-width: 180px;
                }}
                .info-row span:not(.label) {{
                    color: #333;
                }}
                .ath-box {{
                    background: #377e7c;
                    color: white;
                    border-radius: 15px;
                    padding: 30px 25px;
                    margin: 25px 0;
                    text-align: center;
                }}
                .ath-box h3 {{
                    color: white;
                    margin: 0 0 15px 0;
                    font-size: 22px;
                    font-weight: 700;
                }}
                .ath-box p {{
                    color: white;
                    margin: 10px 0;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .ath-handle {{
                    font-size: 26px;
                    font-weight: bold;
                    color: #FFEB3B !important;
                    margin: 20px 0;
                    padding: 15px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    display: inline-block;
                }}
                .ath-logo {{
                    margin-top: 20px;
                }}
                .ath-logo img {{
                    max-width: 150px;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                }}
                .footer {{
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 25px;
                    text-align: center;
                }}
                .footer strong {{
                    color: #4DB6AC;
                }}
                .hashtag {{
                    color: #4DB6AC;
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 10px;
                    display: block;
                }}
                .next-steps-box {{
                    background: #e8f4f1;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #4DB6AC;
                    margin: 20px 0;
                }}
                .next-steps-box strong {{
                    color: #377e7c;
                }}
                
                /* Asegurar que todo el texto en boxes azules sea blanco */
                .thank-you-box * {{
                    color: white;
                }}
                .ath-box * {{
                    color: white;
                }}
                .ath-handle {{
                    color: #FFEB3B !important;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Renovar para Avanzar</h1>
                    <p>Dr. Méndez Sexto - Presidente del Colegio de Médicos</p>
                </div>
                
                <div class="thank-you-box">
                    <p>
                        Gracias por unirte para juntos renovar el Colegio de Médicos Cirujanos de Puerto Rico 
                        y avanzar por nuestra profesión y la salud de Puerto Rico.
                    </p>
                    <img src="{logos_img}" alt="Logos" style="max-width: 400px; width: 100%; height: auto;">
                </div>
                
                <div class="content">
                    <p style="font-size: 16px; margin-bottom: 15px;">
                        Estimado/a <strong>{registration.name} {registration.last_name}</strong>,
                    </p>
                    
                    <p style="margin-bottom: 20px;">
                        Tu registro ha sido confirmado exitosamente. Nos alegra contar contigo en este importante proceso de transformación.
                    </p>
                    
                    <div class="info-section">
                        <h3>Información Registrada</h3>
                        
                        <div class="info-row">
                            <span class="label">Nombre completo:</span>
                            <span>{registration.name} {registration.last_name}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Teléfono:</span>
                            <span>{registration.phone_number}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Dirección:</span>
                            <span>{registration.postal_address}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">¿Es médico?:</span>
                            <span>{'Sí' if registration.is_doctor else 'No'}</span>
                        </div>
                        
                        {f'''<div class="info-row">
                            <span class="label">Especialidad:</span>
                            <span>{registration.specialty}</span>
                        </div>''' if registration.specialty else ''}
                        
                        {f'''<div class="info-row">
                            <span class="label">Años ejerciendo:</span>
                            <span>{registration.years_practicing} años</span>
                        </div>''' if registration.years_practicing else ''}
                        
                        {f'''<div class="info-row">
                            <span class="label">Dónde ofrece servicios:</span>
                            <span>{registration.service_location}</span>
                        </div>''' if registration.service_location else ''}
                        
                        <div class="info-row">
                            <span class="label">¿Es colegiado?:</span>
                            <span>{'Sí' if registration.is_licensed else 'No'}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="label">Ayuda voto adelantado:</span>
                            <span>{'Sí necesita ayuda' if registration.needs_voting_help else 'No necesita ayuda'}</span>
                        </div>
                    </div>
                    
                    {f'''<div class="next-steps-box">
                        <strong>Próximos pasos:</strong><br>
                        Nuestro equipo se pondrá en contacto contigo próximamente para coordinar la asistencia con el voto adelantado.
                    </div>''' if registration.needs_voting_help else ''}
                    
                    <div class="ath-box">
                        <h3 style="color: white;">Apoya la campaña</h3>
                        <p style="color: white;">Puedes realizar tu donación a través de<br>ATH Móvil Pay Business</p>
                        <div class="ath-handle" style="color: #FFEB3B;">/comitedrmendezsexto</div>
                        <div class="ath-logo">
                            <img src="{ath_logo}" alt="ATH Móvil" style="max-width: 150px; height: auto;">
                        </div>
                    </div>
                    
                    <p style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                        Si tienes alguna pregunta, no dudes en contactarnos.
                    </p>
                </div>
                
                <div class="footer">
                    <strong>Dr. Méndez Sexto</strong><br>
                    <em>Renovar para Avanzar</em><br>
                    <small>Colegio de Médicos y Cirujanos de Puerto Rico</small>
                    <span class="hashtag">#RenovarParaAvanzar</span>
                    <p style="font-size: 11px; color: #95a5a6; margin-top: 20px;">
                        Pagado por el Comité Dr. Méndez Sexto
                    </p>
                </div>
            </div>
        </body>
        </html>
        """



class DonateView(TemplateView):
    """Vista principal de donación con ATH Móvil E-commerce"""
    template_name = 'landing/donate.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Configuración de ATH Móvil para el frontend
        context['ath_config'] = {
            'public_token': settings.ATH_MOVIL_PUBLIC_TOKEN,
            'env': settings.ATH_MOVIL_ENV,
            'timeout': settings.ATH_MOVIL_TIMEOUT,
            'site_url': settings.SITE_URL,
        }
        
        # Información de la campaña
        context['candidate'] = {
            'name': 'Dr. Méndez Sexto',
            'campaign_slogan': 'Renovar para Avanzar',
        }
        
        return context

@method_decorator(csrf_exempt, name='dispatch')
class SaveDonationView(View):
    """
    Endpoint opcional para guardar donaciones completadas en tu base de datos.
    ATH Móvil ya procesó el pago - esto es solo para tu registro interno.
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Extraer datos de la transacción
            reference_number = data.get('reference_number')
            amount = data.get('amount')
            transaction_date = data.get('transaction_date')
            ecommerce_id = data.get('ecommerce_id')
            metadata1 = data.get('metadata1')
            metadata2 = data.get('metadata2')
            
            # Aquí puedes guardar en tu modelo de Donation
            # Por ejemplo:
            # Donation.objects.create(
            #     reference_number=reference_number,
            #     amount=amount,
            #     transaction_date=transaction_date,
            #     ecommerce_id=ecommerce_id,
            #     metadata1=metadata1,
            #     metadata2=metadata2
            # )
            
            # Por ahora solo lo registramos en logs
            print(f"✅ Donación guardada: {reference_number} - ${amount}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Donación guardada correctamente'
            })
            
        except Exception as e:
            print(f"❌ Error guardando donación: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    



class TeamView(TemplateView):
    """Vista detallada del equipo"""
    template_name = 'landing/team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nuestro Equipo'
        
        context['team_details'] = {
            'leader': {
                'name': 'Dr. Méndez Sexto',
                'title': 'Candidato a Presidente',
                'bio': 'Con más de 25 años de experiencia en el campo de la medicina...',
                'image': 'landing/img/dr-mendez.png'
            },
            'members': []
        }
        
        return context


class ContactView(View):
    """Vista de contacto"""
    template_name = 'landing/contact.html'
    
    def get(self, request):
        context = {
            'page_title': 'Contacto',
            'contact_info': {
                'email': 'info@renovarparaavanzar.com',
                'phone': '+1 (787) 555-0123',
                'address': 'San Juan, Puerto Rico',
                'hours': 'Lun - Vie: 8:00 AM - 5:00 PM'
            }
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'Consulta desde el sitio web')
        message = request.POST.get('message')
        
        try:
            email_message = f"""
            Nuevo mensaje de contacto:
            
            Nombre: {name}
            Email: {email}
            Asunto: {subject}
            
            Mensaje:
            {message}
            """
            
            messages.success(request, '¡Mensaje enviado! Te responderemos pronto.')
            return redirect('landing:contact')
            
        except Exception as e:
            messages.error(request, 'Error al enviar el mensaje. Intenta de nuevo.')
            return redirect('landing:contact')


class CountdownAPIView(View):
    """API endpoint para obtener el countdown actualizado"""
    
    def get(self, request):
        election_date = datetime(2025, 12, 12, 12, 0, 0)
        now = datetime.now()
        time_remaining = election_date - now
        
        if time_remaining.total_seconds() <= 0:
            return JsonResponse({
                'ended': True,
                'message': '¡Las elecciones han comenzado!'
            })
        
        return JsonResponse({
            'ended': False,
            'days': time_remaining.days,
            'hours': time_remaining.seconds // 3600,
            'minutes': (time_remaining.seconds % 3600) // 60,
            'seconds': time_remaining.seconds % 60
        })
    

class TermsView(TemplateView):
    """Vista para Términos y Condiciones"""
    template_name = 'landing/terms.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Términos y Condiciones'
        return context
    
