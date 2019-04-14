from django import template
register = template.Library() 

@register.filter
def get_dict_val(dictionary, key):
    """Gets an value from a dict by key"""
    if key in dictionary:
        return dictionary.get(key)
    else:
        return ""