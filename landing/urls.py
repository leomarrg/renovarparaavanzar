from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    # Página principal
    path('', views.IndexView.as_view(), name='index'),
    
     # Registro integrado en index pero con URL propia
    path('registro/', views.RegisterView.as_view(), name='register'),
    
    # Páginas informativas
    path('equipo/', views.TeamView.as_view(), name='team'),
    path('contacto/', views.ContactView.as_view(), name='contact'),
    
    # # Donación
    # path('donar/', views.DonateView.as_view(), name='donate'),
    # path('donacion-confirmada/', views.DonationConfirmationView.as_view(), name='donation_confirmation'),
    
    # API endpoints de ATH Móvil
    path('api/ath/payment/', views.ATHPaymentView.as_view(), name='ath-payment'),
    path('api/ath/update-phone/', views.ATHUpdatePhoneView.as_view(), name='ath-update-phone'),
    path('api/ath/authorization/', views.ATHAuthorizationView.as_view(), name='ath-authorization'),
    path('api/ath/find-payment/', views.ATHFindPaymentView.as_view(), name='ath-find-payment'),

    # Términos
    path('terminos/', views.TermsView.as_view(), name='terms'),

    # API endpoints
    path('api/countdown/', views.CountdownAPIView.as_view(), name='countdown-api'),
    path('api/register/', views.RegisterAPIView.as_view(), name='register-api'),

    path('terminos/', views.TermsView.as_view(), name='terms'),
]