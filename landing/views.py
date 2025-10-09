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
import logging

logger = logging.getLogger(__name__)

def send_email_async(registration):
    """Enviar email en un thread separado para no bloquear la respuesta"""
    def _send_email():
        try:
            print(f"🚀 [THREAD START] Iniciando para {registration.email}")
            logger.info(f"Attempting to send email to {registration.email}")
            
            print(f"📧 [STEP 1] Creando RegisterView...")
            register_view = RegisterView()
            
            print(f"📧 [STEP 2] Llamando a send_confirmation_email...")
            result = register_view.send_confirmation_email(registration)
            
            print(f"📧 [STEP 3] Resultado de send_confirmation_email: {result}")
            
            if result:
                logger.info(f"Email sent successfully to {registration.email}")
                print(f"✅ [SUCCESS] Email enviado exitosamente a {registration.email}")
            else:
                print(f"❌ [FAILED] send_confirmation_email retornó False para {registration.email}")
                
        except Exception as e:
            logger.error(f"Error enviando email async: {e}")
            print(f"❌ [EXCEPTION] Error: {e}")
            print(f"❌ [EXCEPTION] Tipo: {type(e).__name__}")
            traceback.print_exc()
        
        print(f"🏁 [THREAD END] Thread terminado para {registration.email}")
    
    print(f"🔵 [MAIN] Creando thread para {registration.email}")
    thread = threading.Thread(target=_send_email)
    thread.daemon = False
    thread.start()
    print(f"🔵 [MAIN] Thread creado: daemon={thread.daemon}, alive={thread.is_alive()}")


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
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. San Juan 1',
                'image': 'landing/img/team/member-1.jpg'
            },
            {
                'id': 2,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado', 
                'district': 'Dist. San Juan 2',
                'image': 'landing/img/team/member-2.jpg'
            },
            {
                'id': 3,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. Bayamón',
                'image': 'landing/img/team/member-3.jpg'
            },
            {
                'id': 4,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. Caguas',
                'image': 'landing/img/team/member-4.jpg'
            },
            {
                'id': 5,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. Arecibo',
                'image': 'landing/img/team/member-5.jpg'
            },
            {
                'id': 6,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. Ponce',
                'image': 'landing/img/team/member-6.jpg'
            },
            {
                'id': 7,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. Mayagüez',
                'image': 'landing/img/team/member-7.jpg'
            },
            {
                'id': 8,
                'name': 'Juan del Pueblo',
                'role': 'Candidato a Delegado',
                'district': 'Dist. Humacao',
                'image': 'landing/img/team/member-8.jpg'
            }
        ]
        
        # Miembro destacado (Juan del Pueblo - Vocal)
        context['featured_member'] = {
            'name': 'Juan del Pueblo',
            'role': 'Candidato a Vocal',
            'district': 'Junta de Gobierno',
            'image': 'landing/img/team/juan-featured.jpg'
        }
        
        # Plan Estratégico
        context['strategic_plans'] = [
            {
                'title': 'Transformación Digital',
                'description': 'Modernización completa de los sistemas del Colegio de Médicos para brindar mejores servicios a nuestros colegiados.',
                'icon': 'digital'
            },
            {
                'title': 'Educación Continua',
                'description': 'Programa robusto de educación médica continua con alianzas internacionales para mantener a nuestros médicos actualizados.',
                'icon': 'education'
            }
        ]
        
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
            'og_image': 'landing/img/logo-renovar.png'
        }
        
        return context


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
            print(f"📨 [send_confirmation_email] INICIO para {registration.email}")
            
            subject = 'Gracias por el apoyo - Renovar para Avanzar'
            from_email = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@renovarparaavanzar.com'
            to_email = registration.email
            
            print(f"📨 [send_confirmation_email] From: {from_email}")
            print(f"📨 [send_confirmation_email] To: {to_email}")
            print(f"📨 [send_confirmation_email] Subject: {subject}")
            
            print(f"📨 [send_confirmation_email] Generando HTML...")
            html_content = self.generate_email_html(registration)
            text_content = strip_tags(html_content)
            
            print(f"📨 [send_confirmation_email] HTML generado: {len(html_content)} caracteres")
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to_email]
            )
            
            email.attach_alternative(html_content, "text/html")
            
            print(f"📨 [send_confirmation_email] Llamando a email.send()...")
            email.send()
            
            print(f"✅ [send_confirmation_email] Email enviado exitosamente a {to_email}")
            return True
        
        except Exception as e:
            print(f"❌ [send_confirmation_email] ERROR: {e}")
            print(f"❌ [send_confirmation_email] Tipo de error: {type(e).__name__}")
            traceback.print_exc()
            return False

    def generate_email_html(self, registration):
        """Generar el HTML del email de confirmación"""
        from django.conf import settings
        
        # URLs de las imágenes
        logos_img = f"{settings.SITE_URL}/static/landing/img/dr_rpa.rev@2x.png"
        ath_logo = f"{settings.SITE_URL}/static/landing/img/ATHM-logo-horizontal.png"
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
                    line-height: 1.6;
                    color: #fff;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background: #ffffff;
                    margin: 20px auto;
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
                }}
                .thank-you-box {{
                    background: #377e7c;
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    margin: 0;
                }}
                .thank-you-box p {{
                    font-size: 16px;
                    line-height: 1.8;
                    margin: 0 0 25px 0;
                    font-weight: 500;
                }}
                .thank-you-box img {{
                    max-width: 400px;
                    width: 100%;
                    height: auto;
                    margin-top: 20px;
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
                    font-size: 18px;
                }}
                .info-row {{
                    margin: 12px 0;
                    padding: 10px 0;
                    border-bottom: 1px solid #e0e0e0;
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
                    color: #fff;
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
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Renovar para Avanzar</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Dr. Méndez Sexto - Presidente del Colegio de Médicos</p>
                </div>
                
                <div class="thank-you-box">
                    <p>
                        Gracias por unirte para juntos renovar el Colegio de Médicos Cirujanos de Puerto Rico 
                        y avanzar por nuestra profesión y la salud de Puerto Rico.
                    </p>
                    <img src="{logos_img}" alt="Logos">
                </div>
                
                <div class="content">
                    <p style="font-size: 16px;">Estimado/a <strong>{registration.name} {registration.last_name}</strong>,</p>
                    
                    <p>Tu registro ha sido confirmado exitosamente. Nos alegra contar contigo en este importante proceso de transformación.</p>
                    
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
                    
                    {f'''<p style="background: #e8f4f1; padding: 15px; border-radius: 8px; border-left: 4px solid #4DB6AC;">
                        <strong style="color: #377e7c;">Próximos pasos:</strong><br>
                        Nuestro equipo se pondrá en contacto contigo próximamente para coordinar la asistencia con el voto adelantado.
                    </p>''' if registration.needs_voting_help else ''}
                    
                    <div class="ath-box">
                        <h3>Apoya la campaña</h3>
                        <p>Puedes realizar tu donación a través de<br>ATH Móvil Pay Business</p>
                        <div class="ath-handle">/comitedrmendezsexto</div>
                        <div class="ath-logo">
                            <img src="{ath_logo}" alt="ATH Móvil">
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
                    <div class="hashtag">#RenovarParaAvanzar</div>
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


# Al inicio del archivo, asegúrate de tener estos imports
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
import json

# ... tus otras vistas ...

# Después de tu IndexView, agrega estas vistas:

@method_decorator(csrf_exempt, name='dispatch')
class ATHPaymentView(View):
    """Endpoint para crear el pago en ATH Móvil"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            amount = float(data.get('amount', 0))
            metadata1 = data.get('metadata1', 'Donacion Campaña')
            metadata2 = data.get('metadata2', 'RenovarParaAvanzar')
            
            if amount <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Monto inválido'
                }, status=400)
            
            # Preparar datos para ATH Móvil
            payment_data = {
                'publicToken': settings.ATH_MOVIL_PUBLIC_TOKEN,
                'timeout': settings.ATH_MOVIL_TIMEOUT,
                'total': amount,
                'subtotal': amount,
                'tax': 0,
                'metadata1': metadata1,
                'metadata2': metadata2,
                'items': [{
                    'name': 'Donación Campaña',
                    'description': f'Donación para {metadata2}',
                    'quantity': 1,
                    'price': amount,
                    'tax': 0,
                    'metadata': metadata1
                }]
            }
            
            # Llamar a la API de ATH Móvil
            response = requests.post(
                'https://payments.athmovil.com/api/business-transaction/ecommerce/payment',
                json=payment_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return JsonResponse(result)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error al crear el pago',
                    'details': response.text
                }, status=response.status_code)
                
        except Exception as e:
            print(f"Error en ATHPaymentView: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ATHUpdatePhoneView(View):
    """Endpoint para actualizar el teléfono"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            ecommerce_id = data.get('ecommerceId')
            phone_number = data.get('phoneNumber')
            public_token = settings.ATH_MOVIL_PUBLIC_TOKEN
            
            update_data = {
                'ecommerceId': ecommerce_id,
                'phoneNumber': phone_number,
                'publicToken': public_token
            }
            
            response = requests.post(
                'https://payments.athmovil.com/api/business-transaction/ecommerce/update-phone-number',
                json=update_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error al actualizar teléfono'
                }, status=response.status_code)
                
        except Exception as e:
            print(f"Error en ATHUpdatePhoneView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ATHAuthorizationView(View):
    """Endpoint para autorizar el pago"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            ecommerce_id = data.get('ecommerceId')
            public_token = settings.ATH_MOVIL_PUBLIC_TOKEN
            
            auth_data = {
                'ecommerceId': ecommerce_id,
                'publicToken': public_token
            }
            
            response = requests.post(
                'https://payments.athmovil.com/api/business-transaction/ecommerce/authorization',
                json=auth_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Si el pago fue exitoso, log
                if result.get('status') == 'success':
                    payment_data = result.get('data', {})
                    print(f"✅ Pago exitoso: {payment_data.get('referenceNumber')}")
                
                return JsonResponse(result)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error al autorizar'
                }, status=response.status_code)
                
        except Exception as e:
            print(f"Error en ATHAuthorizationView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ATHFindPaymentView(View):
    """Endpoint para consultar estado del pago"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            ecommerce_id = data.get('ecommerceId')
            public_token = settings.ATH_MOVIL_PUBLIC_TOKEN
            
            find_data = {
                'ecommerceId': ecommerce_id,
                'publicToken': public_token
            }
            
            response = requests.post(
                'https://payments.athmovil.com/api/business-transaction/ecommerce/business/findPayment',
                json=find_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error al buscar pago'
                }, status=response.status_code)
                
        except Exception as e:
            print(f"Error en ATHFindPaymentView: {str(e)}")
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