from django import template
register = template.Library() 

@register.filter()
def get_select_id(row: dict, field: str) -> str:
    """Return HTML select id for record"""
    
    try:
        field_id = row[field + '_id']
    except:
        field_id = ''
    return field_id