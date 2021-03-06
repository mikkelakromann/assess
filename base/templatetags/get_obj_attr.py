from django import template
register = template.Library() 

@register.filter
def get_obj_attr(model, name):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(model, str(name)):
        return getattr(model, name)
    else:
        return ""
