from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.dateparse import parse_date, parse_time
import json
from datetime import datetime, timedelta, time
from django.utils.timezone import localtime
from .models import Prestation, Reservation
import calendar


def generer_horaires_disponibles(reservations, duree_minutes=30, jours=10):
    """
    Génère les 4 créneaux disponibles les plus proches, en tenant compte :
    - des horaires du salon (lundi à vendredi, 8h-12h / 14h-17h)
    - des réservations existantes
    - de la durée de la prestation
    """
    plages_horaires = []
    now = timezone.localtime()
    horaires_salon = [
        (time(hour=8), time(hour=12)),
        (time(hour=14), time(hour=17))
    ]

    for i in range(jours):
        jour = now + timedelta(days=i)
        if jour.weekday() > 4:  # samedi et dimanche
            continue
        for debut, fin in horaires_salon:
            current = datetime.combine(jour.date(), debut)
            fin_datetime = datetime.combine(jour.date(), fin)

            while current + timedelta(minutes=duree_minutes) <= fin_datetime:
                # Vérifie qu'aucune réservation n'existe sur ce créneau
                conflit = reservations.filter(
                    date=current.date(),
                    heure__gte=current.time(),
                    heure__lt=(current + timedelta(minutes=duree_minutes)).time()
                ).exists()

                if not conflit:
                    plages_horaires.append({
                        'date': current.date().isoformat(),
                        'heure': current.time().strftime('%H:%M')
                    })

                current += timedelta(minutes=30)
                if len(plages_horaires) >= 4:
                    return plages_horaires

    return plages_horaires[:4]



@login_required
def reservation_view(request):
    """
    Affiche la page de réservation avec les prestations
    et les 4 créneaux disponibles les plus proches.
    """
    prestations = Prestation.objects.all()
    reservations_existantes = Reservation.objects.all()
    horaires = generer_horaires_disponibles(reservations_existantes)

    return render(request, 'reservation/page.html', {
        'prestations': prestations,
        'horaires': horaires
    })


@require_GET
@login_required
def creneaux_proches(request):
    prestation_id = request.GET.get('prestation_id')
    if not prestation_id:
        return JsonResponse({'error': 'prestation_id manquant'}, status=400)

    prestation = Prestation.objects.get(id=prestation_id)
    reservations = Reservation.objects.all()
    horaires = generer_horaires_disponibles(reservations, duree_minutes=prestation.duree_minutes)

    return JsonResponse(horaires, safe=False)



@login_required
def enregistrer_reservation(request):
    """
    Vue appelée via AJAX pour enregistrer une réservation.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prestation_id = data.get('prestation_id')
            date_str = data.get('date')
            heure_str = data.get('heure')

            if not (prestation_id and date_str and heure_str):
                return JsonResponse({'message': 'Données manquantes.'}, status=400)

            prestation = Prestation.objects.get(id=prestation_id)
            date = parse_date(date_str)
            heure = parse_time(heure_str)

            if not date or not heure:
                return JsonResponse({'message': 'Format de date ou d\'heure invalide.'}, status=400)

            conflit = Reservation.objects.filter(date=date, heure=heure).exists()
            if conflit:
                return JsonResponse({'message': 'Ce créneau est déjà réservé.'}, status=400)

            Reservation.objects.create(
                utilisateur=request.user,
                prestation=prestation,
                date=date,
                heure=heure
            )

            prenom = request.user.email.split('@')[0].split('.')[0].capitalize()

            # Envoi de l'e-mail
            send_mail(
                subject="Confirmation de votre réservation",
                message=(
                    f"Bonjour {prenom},\n\n"
                    f"Votre réservation pour la prestation \"{prestation.nom}\" le {date.strftime('%d/%m/%Y')} à {heure.strftime('%H:%M')} "
                    f"a bien été enregistrée.\n\nÀ bientôt au Salon DG !"
                ),
                from_email="Salon DG <noreply@salon-dg.local>",
                recipient_list=[request.user.email],
                fail_silently=False
            )

            return JsonResponse({
                'message': f"{prenom}, votre réservation du {date} à {heure.strftime('%H:%M')} est confirmée. "
                           f"Un mail récapitulatif va vous être envoyé."
            })

        except Exception as e:
            return JsonResponse({'message': f"Erreur interne : {str(e)}"}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

@require_GET
def creneaux_pour_jour(request):
    date_str = request.GET.get('date')
    prestation_id = request.GET.get('prestation_id')

    if not date_str or not prestation_id:
        return JsonResponse({'message': 'Paramètres manquants'}, status=400)

    date = parse_date(date_str)
    prestation = Prestation.objects.get(id=prestation_id)
    duree = prestation.duree_minutes

    if date.weekday() > 4:
        return JsonResponse({'jour_ferme': True, 'creneaux': []})

    # Plages horaires : matin (8h-12h) et après-midi (14h-17h)
    horaires_salon = [
        (time(8, 0), time(12, 0)),
        (time(14, 0), time(17, 0))
    ]

    creneaux_dispos = []
    reservations = Reservation.objects.filter(date=date)

    for debut, fin in horaires_salon:
        current = datetime.combine(date, debut)
        fin_datetime = datetime.combine(date, fin)
        while (current + timedelta(minutes=duree)) <= fin_datetime:
            conflit = reservations.filter(
                heure__gte=current.time(),
                heure__lt=(current + timedelta(minutes=duree)).time()
            ).exists()
            if not conflit:
                creneaux_dispos.append(current.time().strftime('%H:%M'))
            current += timedelta(minutes=30)

    return JsonResponse({'jour_ferme': False, 'creneaux': creneaux_dispos})

@require_GET
def jours_disponibles(request):
    """
    Retourne les dates dans les 30 prochains jours avec au moins un créneau libre.
    Utilisé pour désactiver les jours dans le calendrier.
    """
    reservations = Reservation.objects.all()
    disponibles = generer_horaires_disponibles(reservations, jours=30)
    dates_uniques = list({c['date'] for c in disponibles})
    return JsonResponse({'dates_disponibles': sorted(dates_uniques)})