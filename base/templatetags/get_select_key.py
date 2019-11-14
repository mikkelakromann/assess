from django import template
register = template.Library() 

@register.filter()
def get_select_key(row: dict, field: str) -> str:
    """Return HTML select id for record"""
    
    try:
        field_key = row[field + '_key']
    # TODO: Make up test to get to this exception
    except:             # pragma: nocover
        field_key = ''
    return field_key