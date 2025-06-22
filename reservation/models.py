from django.db import models
from django.conf import settings

class Prestation(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    duree_minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nom} - {self.prix}€ - {self.duree_minutes} min"


class Reservation(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prestation = models.ForeignKey(Prestation, on_delete=models.CASCADE)
    date = models.DateField()
    heure = models.TimeField()

    def __str__(self):
        return f"{self.utilisateur.email} - {self.prestation.nom} le {self.date} à {self.heure}"

