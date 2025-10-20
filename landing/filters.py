import django_filters
from django import forms
from .models import Registration

class RegistrationFilter(django_filters.FilterSet):
    """Filtros para el dashboard de registros"""
    
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre...'
        })
    )
    
    last_name = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por apellido...'
        })
    )
    
    email = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por email...'
        })
    )
    
    phone_number = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por teléfono...'
        })
    )
    
    is_doctor = django_filters.BooleanFilter(
        widget=forms.Select(
            choices=[('', 'Todos'), (True, 'Sí'), (False, 'No')],
            attrs={'class': 'form-control'}
        )
    )
    
    is_licensed = django_filters.BooleanFilter(
        widget=forms.Select(
            choices=[('', 'Todos'), (True, 'Sí'), (False, 'No')],
            attrs={'class': 'form-control'}
        )
    )
    
    needs_voting_help = django_filters.BooleanFilter(
        widget=forms.Select(
            choices=[('', 'Todos'), (True, 'Sí'), (False, 'No')],
            attrs={'class': 'form-control'}
        )
    )
    
    accepts_promotions = django_filters.BooleanFilter(
        widget=forms.Select(
            choices=[('', 'Todos'), (True, 'Sí'), (False, 'No')],
            attrs={'class': 'form-control'}
        )
    )
    
    created_at = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = Registration
        fields = ['name', 'last_name', 'email', 'phone_number', 
                  'is_doctor', 'is_licensed', 'needs_voting_help', 
                  'accepts_promotions', 'created_at']