from django.db import migrations

def creer_prestations(apps, schema_editor):
    Prestation = apps.get_model('reservation', 'Prestation')

    prestations = [
        {"nom": "Coupe simple", "prix": 9, "duree_minutes": 30},
        {"nom": "Coupe stylée", "prix": 18, "duree_minutes": 60},
        {"nom": "Coupe beau gosse", "prix": 36, "duree_minutes": 120},
        {"nom": "Super coupe", "prix": 54, "duree_minutes": 180},
    ]

    for p in prestations:
        Prestation.objects.create(**p)

class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0001_initial'),  # remplace par la dernière migration précédente
    ]

    operations = [
        migrations.RunPython(creer_prestations),
    ]
