from django import template

register = template.Library()

@register.filter('modF')
def modF(value, arg):
    print (not (int( value)%int(arg)))
    return not (int( value)%int(arg))