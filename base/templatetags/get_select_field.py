from django import template
register = template.Library() 

@register.filter()
def get_select_field(selected: str, labels: list) -> str:
    """Return HTML select <option>  list for record"""
    
    options = ''
    # First pick the possible value labels from the template context
#    try: 
#        labels = context['value_labels']
#    except:
#        labels = ['No labels',]
    # Pick the value of the field from the row dict
#    try:
#        selected = row[field]
#    except:
#        selected = ''
    # Construct a HTML <select> field for the row's mappings value
    for label in labels:
        if label == selected:
            select = label + '" selected>' + label
        else:
            select = label + '">' + label 
        options += '<option value="' + select + '</option>'
    return options
