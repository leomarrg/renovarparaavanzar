from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import json
from datetime import datetime, timedelta

class IndexView(TemplateView):
    """Vista principal del landing page - Dr. Méndez Sexto"""
    template_name = 'landing/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
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
            'qr_code': 'landing/img/qr-donation.png',  # Placeholder para QR
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
        election_date = datetime(2024, 3, 15, 18, 0, 0)  # Fecha ejemplo
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


class RegisterView(View):
    """Vista para registro de voluntarios y simpatizantes"""
    template_name = 'landing/register.html'
    
    def get(self, request):
        context = {
            'page_title': 'Únete al Movimiento',
            'districts': [
                'San Juan 1', 'San Juan 2', 'Bayamón', 'Caguas',
                'Arecibo', 'Ponce', 'Mayagüez', 'Humacao'
            ]
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Procesar registro
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        district = request.POST.get('district')
        volunteer = request.POST.get('volunteer', False)
        
        try:
            # Aquí guardarías en la base de datos
            # Por ahora enviamos email de confirmación
            
            email_message = f"""
            Nuevo registro en Renovar para Avanzar:
            
            Nombre: {name}
            Email: {email}
            Teléfono: {phone}
            Distrito: {district}
            Voluntario: {'Sí' if volunteer else 'No'}
            """
            
            # send_mail(
            #     subject='Nuevo Registro - Renovar para Avanzar',
            #     message=email_message,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=['info@renovarparaavanzar.com'],
            #     fail_silently=False,
            # )
            
            messages.success(
                request, 
                '¡Gracias por unirte! Te contactaremos pronto con más información.'
            )
            return redirect('landing:index')
            
        except Exception as e:
            messages.error(
                request,
                'Hubo un error procesando tu registro. Por favor intenta de nuevo.'
            )
            return redirect('landing:register')


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