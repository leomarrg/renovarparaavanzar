from django.urls import path
from . import views
from .dashboard_views import (
    DashboardView,
    DashboardChartDataView,
    SendEmailView,
    SendSMSView,
    ExportCSVView
)

app_name = 'landing'

urlpatterns = [
    # Página principal
    path('', views.IndexView.as_view(), name='index'),
    
    # Registro integrado en index pero con URL propia
    path('registro/', views.RegisterView.as_view(), name='register'),
    
    # Páginas informativas
    path('equipo/', views.TeamView.as_view(), name='team'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
    
    # Donación
    path('api/save-donation/', views.SaveDonationView.as_view(), name='save-donation'),

    # Términos
    path('terminos/', views.TermsView.as_view(), name='terms'),

    # API endpoints
    path('api/countdown/', views.CountdownAPIView.as_view(), name='countdown-api'),
    path('api/register/', views.RegisterAPIView.as_view(), name='register-api'),
    
    # ===== DASHBOARD URLS =====
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/chart-data/', DashboardChartDataView.as_view(), name='dashboard-chart-data'),
    path('dashboard/send-email/', SendEmailView.as_view(), name='send-email'),
    path('dashboard/send-sms/', SendSMSView.as_view(), name='send-sms'),
    path('dashboard/export-csv/', ExportCSVView.as_view(), name='export-csv'),
]