from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    # Página principal
    path('', views.IndexView.as_view(), name='index'),
    
     # Registro integrado en index pero con URL propia
    path('registro/', views.IndexWithRegistrationView.as_view(), name='register'),
    
    # Páginas informativas
    path('equipo/', views.TeamView.as_view(), name='team'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
    
    # Funcionalidades
    path('donar/', views.DonateView.as_view(), name='donate'),
    
    # API endpoints
    path('api/countdown/', views.CountdownAPIView.as_view(), name='countdown-api'),
    path('api/register/', views.RegisterAPIView.as_view(), name='register-api'),
]