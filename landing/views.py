from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import datetime, timedelta
import traceback


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
            'og_image': 'landing/img/og-image.jpg'
        }
        
        return context


class IndexWithRegistrationView(IndexView):
    """Vista que muestra index pero salta directamente a la sección de registro"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scroll_to_register'] = True  # Flag para hacer scroll automático
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
                
                # Intentar enviar email si se proporcionó
                email_sent = False
                if registration.email:
                    try:
                        # Usar el método de la clase RegisterView
                        register_view = RegisterView()
                        email_sent = register_view.send_confirmation_email(registration)
                    except Exception as e:
                        print(f"Error enviando email: {e}")
                
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


class RegisterView(View):
    """Vista para registro de voluntarios y simpatizantes - adaptada de ponchapr_app"""
    template_name = 'landing/register.html'
    
    def get(self, request):
        # Importar el formulario aquí para evitar errores de importación circular
        try:
            from .forms import RegistrationForm
        except ImportError:
            # Si el formulario no existe aún, crear contexto básico
            context = {
                'page_title': 'Únete al Movimiento - Renovar para Avanzar',
                'candidate': {
                    'name': 'Dr. Méndez Sexto',
                    'campaign_slogan': 'Renovar para Avanzar',
                }
            }
            return render(request, self.template_name, context)
        
        form = RegistrationForm()
        context = {
            'page_title': 'Únete al Movimiento - Renovar para Avanzar',
            'form': form,
            'candidate': {
                'name': 'Dr. Méndez Sexto',
                'campaign_slogan': 'Renovar para Avanzar',
            }
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Importar el formulario y modelo
        try:
            from .forms import RegistrationForm
            from .models import Registration
        except ImportError as e:
            messages.error(request, f"Error de configuración: {str(e)}")
            return redirect('landing:register')
        
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                # Guardar el registro (similar a front_desk_register en ponchapr)
                registration = form.save(commit=False)
                
                # El unique_id se genera automáticamente en el método save del modelo
                registration.save()
                
                # Intentar enviar correo de confirmación si se proporcionó email
                email_sent = False
                email_status = ""
                
                if registration.email:
                    try:
                        email_sent = self.send_confirmation_email(registration)
                        if email_sent:
                            email_status = "Se ha enviado un correo de confirmación a tu email."
                        else:
                            email_status = ""
                    except Exception as email_error:
                        print(f"Error enviando correo: {email_error}")
                        email_status = ""
                
                # Mensaje de éxito con el código único
                success_message = f'''
                ¡Registro exitoso! {registration.name} {registration.last_name} ha sido registrado. 
                <br><br>
                <div style="background: #FFF3CD; border: 2px solid #FFC107; border-radius: 10px; padding: 15px; margin: 10px 0;">
                    <strong style="font-size: 1.2em;">Tu código de confirmación es:</strong><br>
                    <span style="font-size: 2em; color: #FF7043; font-weight: bold;">{registration.unique_id}</span><br>
                    <small>Por favor guárdalo para futuras referencias</small>
                </div>
                {email_status}
                '''
                
                messages.success(request, success_message)
                
                # Crear un nuevo formulario vacío para el siguiente registro
                form = RegistrationForm()
                
            except Exception as e:
                print(f"Error en el registro: {str(e)}")
                traceback.print_exc()
                messages.error(request, f"Hubo un problema con el registro. Por favor intenta de nuevo.")
        else:
            # Procesar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    # Obtener el nombre legible del campo
                    if field in form.fields:
                        field_name = form.fields[field].label
                    else:
                        field_name = field.replace('_', ' ').title()
                    messages.error(request, f"{field_name}: {error}")
        
        context = {
            'page_title': 'Únete al Movimiento - Renovar para Avanzar',
            'form': form,
            'candidate': {
                'name': 'Dr. Méndez Sexto',
                'campaign_slogan': 'Renovar para Avanzar',
            }
        }
        return render(request, self.template_name, context)
    
    def send_confirmation_email(self, registration):
        """Enviar email de confirmación - adaptado de ponchapr_app"""
        try:
            subject = 'Confirmación de Registro - Renovar para Avanzar'
            from_email = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@renovarparaavanzar.com'
            to_email = registration.email
            
            # Contenido HTML del email
            html_content = self.generate_email_html(registration)
            
            # Generar versión de texto plano
            text_content = strip_tags(html_content)
            
            # Crear el email
            email = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to_email]
            )
            
            # Adjuntar el contenido HTML
            email.attach_alternative(html_content, "text/html")
            
            # Enviar el email
            email.send()
            print(f"Email de confirmación enviado exitosamente a {to_email}")
            
            return True
            
        except Exception as e:
            print(f"Error enviando email de confirmación: {e}")
            traceback.print_exc()
            return False
    
    def generate_email_html(self, registration):
        """Generar el HTML del email de confirmación"""
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #4DB6AC, #00897B);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .code-box {{
                    background: #fff;
                    border: 2px solid #FF7043;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #FF7043;
                    letter-spacing: 2px;
                }}
                .info-row {{
                    margin: 10px 0;
                    padding: 8px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .label {{
                    font-weight: bold;
                    color: #00897B;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>¡Bienvenido a Renovar para Avanzar!</h1>
                <p>Campaña Dr. Méndez Sexto</p>
            </div>
            
            <div class="content">
                <p>Estimado/a <strong>{registration.name} {registration.last_name}</strong>,</p>
                
                <p>¡Gracias por unirte a nuestro movimiento! Tu registro ha sido confirmado exitosamente.</p>
                
                <div class="code-box">
                    <p>Tu Código Único de Registro:</p>
                    <div class="code">{registration.unique_id}</div>
                    <p style="font-size: 12px; color: #666;">Por favor guarda este código para futuras referencias</p>
                </div>
                
                <h3>Información Registrada:</h3>
                
                <div class="info-row">
                    <span class="label">Nombre Completo:</span> {registration.name} {registration.last_name}
                </div>
                
                <div class="info-row">
                    <span class="label">Teléfono:</span> {registration.phone_number}
                </div>
                
                <div class="info-row">
                    <span class="label">Dirección:</span> {registration.postal_address}
                </div>
                
                <div class="info-row">
                    <span class="label">¿Es médico?:</span> {'Sí' if registration.is_doctor else 'No'}
                </div>
                
                {'<div class="info-row"><span class="label">Años ejerciendo:</span> ' + str(registration.years_practicing) + ' años</div>' if registration.years_practicing else ''}
                
                {'<div class="info-row"><span class="label">Lugar donde provee servicios:</span> ' + str(registration.service_location) + '</div>' if registration.service_location else ''}
                
                <div class="info-row">
                    <span class="label">¿Es colegiado?:</span> {'Sí' if registration.is_licensed else 'No'}
                </div>
                
                <div class="info-row">
                    <span class="label">¿Necesita ayuda con voto adelantado?:</span> {'Sí' if registration.needs_voting_help else 'No'}
                </div>
                
                <p style="margin-top: 30px;">
                    {'Nuestro equipo se pondrá en contacto contigo próximamente para coordinar la asistencia con el voto adelantado.' if registration.needs_voting_help else 'Pronto recibirás más información sobre eventos y actividades de la campaña.'}
                </p>
                
                <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                
                <p style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0;">
                    <strong>Atentamente,</strong><br>
                    Equipo de Campaña<br>
                    <strong style="color: #4DB6AC;">Dr. Méndez Sexto</strong><br>
                    <em>Renovar para Avanzar - Colegio de Médicos y Cirujanos de Puerto Rico</em>
                </p>
            </div>
        </body>
        </html>
        """


class DonateView(View):
    """Vista para procesar donaciones (redirige a ATH Móvil)"""
    
    def get(self, request):
        # Aquí puedes registrar el intento de donación
        return redirect('https://athmovilpr.com/pay/comitedrmendezsexto')
    
    def post(self, request):
        # Para procesar donaciones vía formulario si es necesario
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            donor_email = data.get('email')
            
            # Aquí puedes guardar la información en la base de datos
            # Por ahora solo retornamos success
            
            return JsonResponse({
                'success': True,
                'message': 'Gracias por tu apoyo. Serás redirigido a ATH Móvil.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Hubo un error procesando tu solicitud.'
            })


class TeamView(TemplateView):
    """Vista detallada del equipo"""
    template_name = 'landing/team.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Nuestro Equipo'
        
        # Aquí puedes agregar información más detallada del equipo
        context['team_details'] = {
            'leader': {
                'name': 'Dr. Méndez Sexto',
                'title': 'Candidato a Presidente',
                'bio': 'Con más de 25 años de experiencia en el campo de la medicina...',
                'image': 'landing/img/dr-mendez.png'
            },
            'members': []  # Lista completa de miembros
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
        # Procesar formulario de contacto
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'Consulta desde el sitio web')
        message = request.POST.get('message')
        
        try:
            # Enviar email
            email_message = f"""
            Nuevo mensaje de contacto:
            
            Nombre: {name}
            Email: {email}
            Asunto: {subject}
            
            Mensaje:
            {message}
            """
            
            # send_mail(
            #     subject=f'Contacto Web: {subject}',
            #     message=email_message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=['info@renovarparaavanzar.com'],
            #     fail_silently=False,
            # )
            
            messages.success(request, '¡Mensaje enviado! Te responderemos pronto.')
            return redirect('landing:contact')
            
        except Exception as e:
            messages.error(request, 'Error al enviar el mensaje. Intenta de nuevo.')
            return redirect('landing:contact')


class CountdownAPIView(View):
    """API endpoint para obtener el countdown actualizado"""
    
    def get(self, request):
        election_date = datetime(2024, 3, 15, 18, 0, 0)  # Fecha de elección
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