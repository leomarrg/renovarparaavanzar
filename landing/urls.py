from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    # Página principal
    path('', views.IndexView.as_view(), name='index'),
    
    # Páginas informativas
    path('equipo/', views.TeamView.as_view(), name='team'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
    
    # Funcionalidades
    path('donar/', views.DonateView.as_view(), name='donate'),
    path('registro/', views.RegisterView.as_view(), name='register'),
    
    # API endpoints
    path('api/countdown/', views.CountdownAPIView.as_view(), name='countdown-api'),
]