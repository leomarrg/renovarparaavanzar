from django.db import models
from django.utils import timezone
import uuid

class Registration(models.Model):
    """Modelo para registros de simpatizantes del Dr. Méndez Sexto"""
    
    # Información personal básica
    name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellidos")
    postal_address = models.TextField(verbose_name="Dirección Postal")
    phone_number = models.CharField(max_length=20, verbose_name="Número Telefónico")
    
    # Información profesional
    service_location = models.TextField(
        verbose_name="¿Dónde provee servicios?",
        help_text="Indique los lugares donde provee servicios médicos"
    )
    is_doctor = models.BooleanField(
        verbose_name="¿Eres médico?",
        default=False
    )
    years_practicing = models.IntegerField(
        verbose_name="Años ejerciendo",
        null=True,
        blank=True,
        help_text="Número de años ejerciendo la medicina"
    )
    is_licensed = models.BooleanField(
        verbose_name="¿Eres colegiado?",
        null=True,
        blank=True,
        default=False
    )
    
    # Asistencia electoral
    needs_voting_help = models.BooleanField(
        verbose_name="¿Necesitará ayuda con voto adelantado?",
        default=False,
        null=True,
        blank=True
    )

    accepts_terms = models.BooleanField(
        verbose_name="Acepta términos y condiciones",
        default=False,
        help_text="El usuario acepta los términos de servicio"
    )
    
    accepts_promotions = models.BooleanField(
        verbose_name="Acepta recibir promociones",
        default=False,
        help_text="El usuario acepta recibir comunicaciones promocionales"
    )
    
    # Campos del sistema
    unique_id = models.CharField(max_length=6, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    specialty = models.CharField(max_length=200, blank=True, null=True, verbose_name="Especialidad")
    
    # Email opcional para enviar confirmaciones
    email = models.EmailField(
        verbose_name="Correo electrónico (opcional)",
        blank=True,
        null=True
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Registro de Simpatizante"
        verbose_name_plural = "Registros de Simpatizantes"
    
    def __str__(self):
        return f"{self.name} {self.last_name} - {'Médico' if self.is_doctor else 'Simpatizante'}"
    
    def generate_unique_id(self):
        """Generate a 6-digit unique identifier"""
        import random
        import string
        while True:
            unique_id = ''.join(random.choices(string.digits, k=6))
            if not Registration.objects.filter(unique_id=unique_id).exists():
                return unique_id
    
    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        super().save(*args, **kwargs)

class PlanEstrategico(models.Model):
    titulo = models.CharField(max_length=200, default="Descarga el Plan de Acción!")
    archivo_pdf = models.FileField(upload_to='plan_estrategico/', help_text="Archivo PDF del Plan Estratégico")
    descripcion = models.TextField(blank=True, help_text="Descripción breve del plan")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plan Estratégico'
        verbose_name_plural = 'Planes Estratégicos'
    
    def __str__(self):
        return self.titulo