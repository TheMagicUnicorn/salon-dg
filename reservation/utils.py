from datetime import datetime, timedelta
from datetime import datetime, timedelta, time

def generer_creneaux_disponibles(date_debut: datetime, duree_minutes: int):
    horaires_disponibles = []
    heures_ouverture = [(8, 12), (14, 17)]  # Matin et après-midi
    date_actuelle = date_debut.replace(hour=8, minute=0, second=0, microsecond=0)

    while len(horaires_disponibles) < 4:
        for debut, fin in heures_ouverture:
            heure = date_actuelle.replace(hour=debut, minute=0)
            while heure.hour < fin:
                horaire_fin = heure + timedelta(minutes=duree_minutes)
                if horaire_fin.hour + horaire_fin.minute / 60 <= fin:
                    horaires_disponibles.append(heure)
                    if len(horaires_disponibles) == 4:
                        break
                heure += timedelta(minutes=30)
            if len(horaires_disponibles) == 4:
                break
        date_actuelle += timedelta(days=1)

    return horaires_disponibles

def generer_creneaux(start_datetime, duree_minutes):
    creneaux = []
    date = start_datetime.date()
    heure = start_datetime.time()

    # Créneaux autorisés (jours & heures)
    horaires = [(time(8, 0), time(12, 0)), (time(14, 0), time(17, 0))]

    while len(creneaux) < 20:  # On génère jusqu’à 20 créneaux (on en affichera 4)
        if date.weekday() < 5:  # Lun à Ven
            for debut, fin in horaires:
                current = datetime.combine(date, debut)
                fin_dt = datetime.combine(date, fin)
                while current + timedelta(minutes=duree_minutes) <= fin_dt:
                    if current >= start_datetime:
                        creneaux.append(current)
                    current += timedelta(minutes=15)
        date += timedelta(days=1)
    return creneaux
