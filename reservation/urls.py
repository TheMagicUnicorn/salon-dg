from django.urls import path
from . import views

urlpatterns = [
    path('reservation/', views.reservation_view, name='reservation'),
    path('creneaux/', views.creneaux_proches, name='creneaux_proches'),  # ← VÉRIFIE BIEN CETTE LIGNE
    path('enregistrer/', views.enregistrer_reservation, name='enregistrer_reservation'),
    path('api/creneaux/jour/', views.creneaux_pour_jour, name='creneaux_pour_jour'),
    path('api/jours-disponibles/', views.jours_disponibles, name='jours_disponibles'),
]