from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from .models import Registration
import csv

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """Administración de registros de simpatizantes"""
    
    list_display = (
        'unique_id',
        'full_name', 
        'phone_number',
        'is_doctor_display',
        'is_licensed_display',
        'needs_voting_help_display',
        'created_at'
    )
    
    list_filter = (
        'is_doctor',
        'is_licensed', 
        'needs_voting_help',
        'created_at'
    )
    
    search_fields = (
        'name', 
        'last_name', 
        'email', 
        'phone_number',
        'unique_id',
        'postal_address'
    )
    
    readonly_fields = ('unique_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('name', 'last_name', 'postal_address', 'phone_number', 'email')
        }),
        ('Información Profesional', {
            'fields': ('is_doctor', 'service_location', 'years_practicing', 'is_licensed')
        }),
        ('Asistencia Electoral', {
            'fields': ('needs_voting_help',)
        }),
        ('Información del Sistema', {
            'fields': ('unique_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['export_to_csv', 'export_doctors_only', 'export_voting_help']
    
    def full_name(self, obj):
        """Mostrar nombre completo"""
        return f"{obj.name} {obj.last_name}"
    full_name.short_description = "Nombre Completo"
    full_name.admin_order_field = 'name'
    
    def is_doctor_display(self, obj):
        """Mostrar si es médico con ícono"""
        if obj.is_doctor:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html('<span style="color: gray;">No</span>')
    is_doctor_display.short_description = "¿Médico?"
    is_doctor_display.admin_order_field = 'is_doctor'
    
    def is_licensed_display(self, obj):
        """Mostrar si está colegiado con ícono"""
        if obj.is_licensed:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html('<span style="color: gray;">No</span>')
    is_licensed_display.short_description = "¿Colegiado?"
    is_licensed_display.admin_order_field = 'is_licensed'
    
    def needs_voting_help_display(self, obj):
        """Mostrar si necesita ayuda con voto adelantado"""
        if obj.needs_voting_help:
            return format_html(
                '<span style="color: orange;">⚠ Sí</span>'
            )
        return format_html('<span style="color: gray;">No</span>')
    needs_voting_help_display.short_description = "¿Necesita Ayuda Voto?"
    needs_voting_help_display.admin_order_field = 'needs_voting_help'
    
    def export_to_csv(self, request, queryset):
        """Exportar registros seleccionados a CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="registros_campana.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Código', 'Nombre', 'Apellidos', 'Dirección', 'Teléfono', 
            'Email', '¿Médico?', 'Lugar de Servicios', 'Años Ejerciendo', 
            '¿Colegiado?', '¿Necesita Ayuda Voto?', 'Fecha Registro'
        ])
        
        for reg in queryset:
            writer.writerow([
                reg.unique_id,
                reg.name,
                reg.last_name,
                reg.postal_address,
                reg.phone_number,
                reg.email or '',
                'Sí' if reg.is_doctor else 'No',
                reg.service_location or '',
                reg.years_practicing or '',
                'Sí' if reg.is_licensed else 'No',
                'Sí' if reg.needs_voting_help else 'No',
                reg.created_at.strftime('%d/%m/%Y %H:%M')
            ])
        
        return response
    export_to_csv.short_description = "Exportar seleccionados a CSV"
    
    def export_doctors_only(self, request, queryset):
        """Exportar solo médicos a CSV"""
        doctors = queryset.filter(is_doctor=True)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="medicos_registrados.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Código', 'Nombre', 'Apellidos', 'Teléfono', 'Email',
            'Lugar de Servicios', 'Años Ejerciendo', '¿Colegiado?'
        ])
        
        for doc in doctors:
            writer.writerow([
                doc.unique_id,
                doc.name,
                doc.last_name,
                doc.phone_number,
                doc.email or '',
                doc.service_location,
                doc.years_practicing,
                'Sí' if doc.is_licensed else 'No'
            ])
        
        return response
    export_doctors_only.short_description = "Exportar médicos a CSV"
    
    def export_voting_help(self, request, queryset):
        """Exportar personas que necesitan ayuda con voto adelantado"""
        need_help = queryset.filter(needs_voting_help=True)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ayuda_voto_adelantado.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Código', 'Nombre', 'Apellidos', 'Dirección', 'Teléfono', 'Email'
        ])
        
        for person in need_help:
            writer.writerow([
                person.unique_id,
                person.name,
                person.last_name,
                person.postal_address,
                person.phone_number,
                person.email or ''
            ])
        
        return response
    export_voting_help.short_description = "Exportar lista de ayuda voto adelantado"
    
    def changelist_view(self, request, extra_context=None):
        """Vista personalizada del listado con estadísticas"""
        extra_context = extra_context or {}
        
        # Estadísticas
        total_registros = Registration.objects.count()
        total_medicos = Registration.objects.filter(is_doctor=True).count()
        total_colegiados = Registration.objects.filter(is_licensed=True).count()
        total_necesitan_ayuda = Registration.objects.filter(needs_voting_help=True).count()
        
        extra_context.update({
            'total_registros': total_registros,
            'total_medicos': total_medicos,
            'total_colegiados': total_colegiados,
            'total_necesitan_ayuda': total_necesitan_ayuda,
            'porcentaje_medicos': round((total_medicos / total_registros * 100), 1) if total_registros > 0 else 0,
            'porcentaje_ayuda': round((total_necesitan_ayuda / total_registros * 100), 1) if total_registros > 0 else 0,
        })
        
        return super().changelist_view(request, extra_context=extra_context)