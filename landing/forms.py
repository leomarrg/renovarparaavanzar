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
    
    # Campo para "¿Eres colegiado?" como radio buttons - NO REQUERIDO
    is_licensed = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Eres colegiado?',
        initial=False,
        required=False
    )
    
    # Campo para "¿Necesitará ayuda con voto adelantado?" como radio buttons
    needs_voting_help = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Necesitará ayuda con voto adelantado?',
        initial=False,
        required=False
    )
    
    # NUEVOS CAMPOS - Checkboxes de términos y promociones
    accepts_terms = forms.BooleanField(
        required=True,
        initial=True,
        label='Acepto los términos y condiciones',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'checked': 'checked'
        })
    )
    
    accepts_promotions = forms.BooleanField(
        required=False,
        initial=True,
        label='Acepto recibir información sobre la campaña',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'checked': 'checked'
        })
    )
    
    class Meta:
        model = Registration
        fields = [
            'name', 
            'last_name', 
            'postal_address', 
            'phone_number',
            'service_location',
            'specialty',
            'is_doctor',
            'years_practicing',
            'is_licensed',
            'needs_voting_help',
            'email',
            'accepts_terms',
            'accepts_promotions'
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
            'specialty': forms.TextInput(attrs={
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
    
    def clean_accepts_terms(self):
        """Validar que los términos hayan sido aceptados"""
        accepts_terms = self.cleaned_data.get('accepts_terms')
        if not accepts_terms:
            raise forms.ValidationError("Debe aceptar los términos y condiciones para continuar.")
        return accepts_terms
    
    def _to_bool(self, value):
        """
        Convertir cualquier valor a booleano de forma robusta.
        Maneja: strings ('True', 'False', 'true', 'false'), booleanos, None, etc.
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ('true', '1', 'yes', 'sí', 'si')
        return bool(value)

def clean(self):
    """Validación general del formulario"""
    cleaned_data = super().clean()
    
    # DEBUG: Imprimir valores recibidos (puedes remover después)
    print("=" * 60)
    print("🔍 DEBUG - Valores recibidos:")
    print(f"  is_doctor: {cleaned_data.get('is_doctor')} (type: {type(cleaned_data.get('is_doctor'))})")
    print(f"  service_location: '{cleaned_data.get('service_location')}'")
    print("=" * 60)
    
    # 🔧 Conversión ROBUSTA de strings/booleanos
    cleaned_data['is_doctor'] = self._to_bool(cleaned_data.get('is_doctor', False))
    cleaned_data['is_licensed'] = self._to_bool(cleaned_data.get('is_licensed', False))
    cleaned_data['needs_voting_help'] = self._to_bool(cleaned_data.get('needs_voting_help', False))
    
    is_doctor = cleaned_data['is_doctor']
    
    print(f"✅ is_doctor convertido a: {is_doctor}")
    
    # SOLO validar campos de médico SI es médico
    if is_doctor:
        print("👨‍⚕️ Usuario ES médico - validando campos")
        
        service_location = cleaned_data.get('service_location', '').strip()
        
        if not service_location:
            self.add_error('service_location', 
                          'Por favor indique dónde provee servicios médicos.')
    else:
        print("👤 Usuario NO es médico - limpiando campos")
        # Si NO es médico, limpiar campos médicos
        cleaned_data['service_location'] = ''
        cleaned_data['specialty'] = ''
        cleaned_data['is_licensed'] = False
        cleaned_data['years_practicing'] = None
    
    print("=" * 60)
    
    return cleaned_data