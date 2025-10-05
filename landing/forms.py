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
        initial=False
    )
    
    # Campo para "¿Eres colegiado?" como radio buttons
    is_licensed = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Eres colegiado?',
        initial=False
    )
    
    # Campo para "¿Necesitará ayuda con voto adelantado?" como radio buttons
    needs_voting_help = forms.ChoiceField(
        choices=[(True, 'Sí'), (False, 'No')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='¿Necesitará ayuda con voto adelantado?',
        initial=False
    )
    
    class Meta:
        model = Registration
        fields = [
            'name', 
            'last_name', 
            'postal_address', 
            'phone_number',
            'service_location',
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
            'service_location': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Indique los lugares donde provee servicios médicos (hospitales, clínicas, etc.)',
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
            'service_location': '¿Dónde provee servicios?',
            'years_practicing': 'Años ejerciendo',
            'email': 'Correo electrónico (opcional)'
        }
    
    def clean_phone_number(self):
        """Validación y formateo del número de teléfono"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            import re
            # Remover caracteres no numéricos excepto + al inicio
            phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone)
            
            # Verificar que tiene al menos 10 dígitos
            digits_only = re.sub(r'[^\d]', '', phone)
            if len(digits_only) < 10:
                raise forms.ValidationError("El número de teléfono debe tener al menos 10 dígitos.")
                
            return phone
        return phone
    
    def clean_years_practicing(self):
        """Validación para años ejerciendo - solo si es médico"""
        years = self.cleaned_data.get('years_practicing')
        is_doctor = self.cleaned_data.get('is_doctor')
        
        # Convertir el string a booleano si es necesario
        if isinstance(is_doctor, str):
            is_doctor = is_doctor.lower() == 'true'
        
        if is_doctor and not years:
            raise forms.ValidationError("Por favor indique los años ejerciendo la medicina.")
            
        return years
    
    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        
        # Convertir strings a booleanos para los campos de radio buttons
        for field in ['is_doctor', 'is_licensed', 'needs_voting_help']:
            if field in cleaned_data:
                value = cleaned_data[field]
                if isinstance(value, str):
                    cleaned_data[field] = value.lower() == 'true'
        
        is_doctor = cleaned_data.get('is_doctor')
        is_licensed = cleaned_data.get('is_licensed')
        service_location = cleaned_data.get('service_location')
        
        # Si es médico, debe indicar dónde provee servicios
        if is_doctor and not service_location:
            self.add_error('service_location', 
                          'Por favor indique dónde provee servicios médicos.')
        
        # Si dice ser colegiado, debe ser médico
        if is_licensed and not is_doctor:
            self.add_error('is_licensed', 
                          'Solo los médicos pueden estar colegiados.')
        
        return cleaned_data