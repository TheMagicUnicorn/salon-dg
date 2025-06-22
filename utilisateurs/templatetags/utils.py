from django import template

register = template.Library()

@register.filter
def prenom_depuis_email(email):
    try:
        prenom = email.split('@')[0].split('.')[0]
        return prenom.capitalize()
    except:
        return email