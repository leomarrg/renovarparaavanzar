from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    """Formulario de registro para simpatizantes del Dr. Méndez Sexto"""
    
    # Campo para "¿Eres médico?" como radio buttons
    is_doctor = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Eres médico?',
        initial=False,
        required=True
    )
    
    # Campo para "¿Eres colegiado?" como radio buttons - AHORA NO REQUERIDO
    is_licensed = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Eres colegiado?',
        initial=False,
        required=False  # CAMBIO AQUÍ
    )
    
    # Campo para "¿Necesitará ayuda con voto adelantado?" como radio buttons
    needs_voting_help = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Necesitará ayuda con voto adelantado?',
        initial=False,
        required=True
    )
    
    class Meta:
        model = Registration
        fields = [
            'name', 
            'last_name', 
            'postal_address', 
            'phone_number',
            'service_location',
            'specialty',  # AGREGAR ESTO
            'is_doctor',
            'years_practicing',
            'is_licensed',
            'needs_voting_help',
            'email'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre',
                'required': True,
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese sus apellidos',
                'required': True,
            }),
            'postal_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su dirección postal completa',
                'required': True,
                'rows': 3,
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(787) 123-4567',
                'required': True,
            }),
            'specialty': forms.TextInput(attrs={  # AGREGAR ESTO
                'class': 'form-control',
                'placeholder': 'Especialidad médica',
            }),
            'service_location': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Indique los lugares donde provee servicios médicos',
                'rows': 3,
            }),
            'years_practicing': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de años',
                'min': '0',
                'max': '100',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com (opcional)',
            })
        }
        
        labels = {
            'name': 'Nombre',
            'last_name': 'Apellidos', 
            'postal_address': 'Dirección Postal',
            'phone_number': 'Número Telefónico',
            'specialty': 'Especialidad',
            'service_location': '¿Dónde provee servicios?',
            'years_practicing': 'Años ejerciendo',
            'email': 'Correo electrónico (opcional)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que los campos de médico NO sean requeridos por defecto
        self.fields['service_location'].required = False
        self.fields['specialty'].required = False
        self.fields['years_practicing'].required = False
        self.fields['is_licensed'].required = False
    
    def clean_phone_number(self):
        """Validación y formateo del número de teléfono"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            import re
            phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone)
            digits_only = re.sub(r'[^\d]', '', phone)
            if len(digits_only) < 10:
                raise forms.ValidationError("El número de teléfono debe tener al menos 10 dígitos.")
            return phone
        return phone
    
    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        
        # Convertir strings a booleanos
        for field in ['is_doctor', 'is_licensed', 'needs_voting_help']:
            if field in cleaned_data:
                value = cleaned_data[field]
                if isinstance(value, str):
                    cleaned_data[field] = value.lower() == 'true'
        
        is_doctor = cleaned_data.get('is_doctor')
        
        # SOLO validar campos de médico SI es médico
        if is_doctor:
            service_location = cleaned_data.get('service_location')
            is_licensed = cleaned_data.get('is_licensed')
            
            if not service_location:
                self.add_error('service_location', 
                              'Por favor indique dónde provee servicios médicos.')
            
            if is_licensed is None:
                self.add_error('is_licensed', 
                              'Por favor indique si está colegiado.')
        else:
            # Si NO es médico, establecer valores por defecto
            cleaned_data['service_location'] = ''
            cleaned_data['specialty'] = ''
            cleaned_data['is_licensed'] = False
            cleaned_data['years_practicing'] = None
        
        return cleaned_data