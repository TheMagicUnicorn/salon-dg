from django.contrib import admin
from django.urls import path, include
from utilisateurs.views import connexion_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', connexion_view, name='connexion'),  # 👈 Page d’entrée
    path('', include('utilisateurs.urls')),      # routes inscription/connexion (redirigées ici aussi)
    path('reservation/', include('reservation.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)