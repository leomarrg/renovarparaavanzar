from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
import json
import csv
from datetime import datetime, timedelta
from twilio.rest import Client
from .models import Registration
from .filters import RegistrationFilter


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vista principal del dashboard"""
    template_name = 'landing/dashboard/index.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Aplicar filtros
        filterset = RegistrationFilter(self.request.GET, queryset=Registration.objects.all())
        registrations = filterset.qs
        
        # Estadísticas generales
        context['total_registros'] = registrations.count()
        context['total_medicos'] = registrations.filter(is_doctor=True).count()
        context['total_colegiados'] = registrations.filter(is_licensed=True).count()
        context['total_ayuda_voto'] = registrations.filter(needs_voting_help=True).count()
        context['total_acepto_promociones'] = registrations.filter(accepts_promotions=True).count()

        # Estadísticas de suscripción
        context['total_con_email'] = registrations.filter(email__isnull=False).exclude(email='').count()
        context['total_suscritos'] = registrations.filter(unsubscribed=False, email__isnull=False).exclude(email='').count()
        context['total_dados_baja'] = registrations.filter(unsubscribed=True).count()

        # Registros recientes (últimos 7 días)
        seven_days_ago = datetime.now() - timedelta(days=7)
        context['registros_recientes'] = registrations.filter(created_at__gte=seven_days_ago).count()
        
        # Paginación
        page = self.request.GET.get('page', 1)
        paginator = Paginator(registrations.order_by('-created_at'), settings.DASHBOARD_ITEMS_PER_PAGE)
        context['registrations'] = paginator.get_page(page)
        
        # Filtros
        context['filter'] = filterset
        
        return context


class DashboardChartDataView(LoginRequiredMixin, View):
    """API para obtener datos del gráfico de tendencias"""
    login_url = '/admin/login/'
    
    def get(self, request):
        # Obtener el rango de fechas
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        registrations = Registration.objects.all()
        
        if start_date:
            registrations = registrations.filter(created_at__gte=start_date)
        if end_date:
            registrations = registrations.filter(created_at__lte=end_date)
        
        # Agrupar por fecha
        daily_registrations = registrations.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Formatear datos para Chart.js
        labels = []
        data = []
        
        for item in daily_registrations:
            labels.append(item['date'].strftime('%Y-%m-%d'))
            data.append(item['count'])
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': 'Registros por día',
                'data': data,
                'borderColor': '#377e7c',
                'backgroundColor': 'rgba(55, 126, 124, 0.1)',
                'tension': 0.4
            }]
        })


class SendEmailView(LoginRequiredMixin, View):
    """Vista para enviar emails masivos"""
    login_url = '/admin/login/'
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            recipient_ids = data.get('recipients', [])
            subject = data.get('subject', '')
            message_html = data.get('message', '')
            
            if not recipient_ids or not subject or not message_html:
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan datos requeridos'
                }, status=400)
            
            # Obtener destinatarios que aceptaron promociones
            recipients = Registration.objects.filter(
                id__in=recipient_ids,
                accepts_promotions=True,
                email__isnull=False
            ).exclude(email='')
            
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients:
                try:
                    # Crear email
                    from_email = settings.EMAIL_HOST_USER
                    to_email = recipient.email
                    
                    text_content = strip_tags(message_html)
                    
                    email = EmailMultiAlternatives(
                        subject,
                        text_content,
                        from_email,
                        [to_email]
                    )
                    
                    email.attach_alternative(message_html, "text/html")
                    email.send()
                    
                    sent_count += 1
                    
                except Exception as e:
                    print(f"Error enviando email a {recipient.email}: {e}")
                    failed_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Emails enviados: {sent_count}. Fallidos: {failed_count}',
                'sent': sent_count,
                'failed': failed_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)


class SendSMSView(LoginRequiredMixin, View):
    """Vista para enviar SMS masivos usando Twilio"""
    login_url = '/admin/login/'
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            recipient_ids = data.get('recipients', [])
            message_text = data.get('message', '')
            
            if not recipient_ids or not message_text:
                return JsonResponse({
                    'success': False,
                    'message': 'Faltan datos requeridos'
                }, status=400)
            
            # Verificar configuración de Twilio
            if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
                return JsonResponse({
                    'success': False,
                    'message': 'Twilio no está configurado correctamente'
                }, status=500)
            
            # Inicializar cliente de Twilio
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            # Obtener destinatarios que aceptaron promociones
            recipients = Registration.objects.filter(
                id__in=recipient_ids,
                accepts_promotions=True,
                phone_number__isnull=False
            ).exclude(phone_number='')
            
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients:
                try:
                    # Limpiar número de teléfono
                    phone = recipient.phone_number.strip()
                    
                    # Asegurarse que tenga formato internacional
                    if not phone.startswith('+'):
                        phone = '+1' + phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
                    
                    # Enviar SMS
                    message = client.messages.create(
                        body=message_text,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=phone
                    )
                    
                    sent_count += 1
                    
                except Exception as e:
                    print(f"Error enviando SMS a {recipient.phone_number}: {e}")
                    failed_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'SMS enviados: {sent_count}. Fallidos: {failed_count}',
                'sent': sent_count,
                'failed': failed_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)


class ExportCSVView(LoginRequiredMixin, View):
    """Vista para exportar registros a CSV"""
    login_url = '/admin/login/'
    
    def get(self, request):
        # Aplicar los mismos filtros que en el dashboard
        filterset = RegistrationFilter(request.GET, queryset=Registration.objects.all())
        registrations = filterset.qs.order_by('-created_at')
        
        # Crear respuesta CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="registros_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Encabezados
        writer.writerow([
            'Código',
            'Nombre',
            'Apellidos',
            'Email',
            'Teléfono',
            'Dirección',
            '¿Médico?',
            'Especialidad',
            'Años Ejerciendo',
            'Lugar Servicios',
            '¿Colegiado?',
            '¿Necesita Ayuda Voto?',
            '¿Acepta Promociones?',
            'Fecha Registro'
        ])
        
        # Datos
        for reg in registrations:
            writer.writerow([
                reg.unique_id,
                reg.name,
                reg.last_name,
                reg.email or '',
                reg.phone_number,
                reg.postal_address,
                'Sí' if reg.is_doctor else 'No',
                reg.specialty or '',
                reg.years_practicing or '',
                reg.service_location or '',
                'Sí' if reg.is_licensed else 'No',
                'Sí' if reg.needs_voting_help else 'No',
                'Sí' if reg.accepts_promotions else 'No',
                reg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response


class MarkUnsubscribedView(LoginRequiredMixin, View):
    """Vista para marcar usuarios seleccionados como dados de baja"""
    login_url = '/admin/login/'

    def post(self, request):
        try:
            data = json.loads(request.body)
            registration_ids = data.get('registration_ids', [])

            if not registration_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No se seleccionaron registros'
                }, status=400)

            # Marcar registros como dados de baja
            updated = Registration.objects.filter(
                id__in=registration_ids
            ).update(
                unsubscribed=True,
                unsubscribed_at=timezone.now()
            )

            return JsonResponse({
                'success': True,
                'message': f'{updated} usuario(s) marcado(s) como dado(s) de baja. No recibirán más emails.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)


class MarkSubscribedView(LoginRequiredMixin, View):
    """Vista para re-suscribir usuarios seleccionados"""
    login_url = '/admin/login/'

    def post(self, request):
        try:
            data = json.loads(request.body)
            registration_ids = data.get('registration_ids', [])

            if not registration_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No se seleccionaron registros'
                }, status=400)

            # Re-suscribir usuarios
            updated = Registration.objects.filter(
                id__in=registration_ids
            ).update(
                unsubscribed=False,
                unsubscribed_at=None
            )

            return JsonResponse({
                'success': True,
                'message': f'{updated} usuario(s) re-suscrito(s). Volverán a recibir emails.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)