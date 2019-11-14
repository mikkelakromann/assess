from django.test import TestCase
from django.template import Context, Template
from base.models import Version,TestItemA, TestItemB, TestItemC, TestMappings


class TemplateTagsTest(TestCase):
    """Testing Table()."""    

    def setUp(self):
        self.context = []

        v1 = Version()
        v1.set_version_id("")
        v1.save()
        v2 = Version()
        v2.set_version_id("")
        v2.save()

        TestItemA.objects.create(label='a1',version_first=v1)
        TestItemB.objects.create(label='b1',version_first=v1)
        TestItemC.objects.create(label='c1',version_first=v1)

        a1 = TestItemA.objects.get(label='a1')
        b1 = TestItemB.objects.get(label='b1')
        c1 = TestItemC.objects.get(label='c1')

        TestMappings.objects.create(testitema=a1,testitemb=b1,testitemc=c1,version_first=v1)


    def test_get_dict_val_valid(self):
        """Template tag get_dict_val: get value from dict by key, valid."""
        row = {'field1': 'value1', 'field2': 'value2'}
        fields = row.keys()
        context = Context({'row': row, 'fields': fields })
        template_to_render = Template(
            '{% load get_dict_val %}'
            '{%for field in fields%}<td>{{row|get_dict_val:field}}{%endfor%}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('<td>value1<td>value2', rendered_template)
        
    def test_get_dict_val_invalid(self):
        """Template tag get_dict_val: get value from dict by key, invalid."""
        row = {'field1': 'value1', 'field2': 'value2'}
        # The field list has keys not in the row dict
        fields = ['field3','field4']
        context = Context({'row': row, 'fields': fields })
        template_to_render = Template(
            '{% load get_dict_val %}'
            '{%for field in fields%}<td>{{row|get_dict_val:field}}{%endfor%}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('<td><td>', rendered_template)
        
    def test_get_obj_attr_valid(self):
        """Template tag get_obj_attr: get object by property, valid."""
        # The field list is valid object properties (i.e index_fields)
        fields = ['testitema','testitemb','testitemc']
        query = TestMappings.objects.all()
        context = Context({'rows': query, 'fields': fields })
        template_to_render = Template(
            '{% load get_obj_attr %}'
            '{%for row in rows%}{%for field in fields%}<td>{{row|get_obj_attr:field}}{%endfor%}{%endfor%}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('<td>a1<td>b1<td>c1', rendered_template)
        
    def test_get_obj_attr_invalid(self):
        """Template tag get_obj_attr: get object by property, invalid."""
        # The field list has an item which is not an object property
        fields = ['testitema','testitemb','testitemc','invalid_field']
        query = TestMappings.objects.all()
        context = Context({'rows': query, 'fields': fields })
        template_to_render = Template(
            '{% load get_obj_attr %}'
            '{%for row in rows%}{%for field in fields%}<td>{{row|get_obj_attr:field}}{%endfor%}{%endfor%}'
        )
        rendered_template = template_to_render.render(context)
        self.assertInHTML('<td>a1<td>b1<td>c1<td>', rendered_template)
    
    def test_get_select_field_valid(self):
        """Template tag get_select_field: write HTML <SELECT>, invalid."""
        # The field list has an item which is not an object property
        fields = ['testitemc']
        row_list = [{ 'testitema': 'a1', 'testitemb': 'b1', 'testitemc': 'c1', 'testitemc_key': '(a1, b1, testitemc)'}]
        value_dict = { 'c1': 'c1', 'c2': 'c2' }
        context = Context({'row_list': row_list, 'header_list_items': fields, 'value_dict': value_dict })
        template_to_render = Template(
            '{% for row in row_list %}'
            ' {% for field in header_list_items %}'
            '  {% load get_select_field %}{% load get_select_key %}{% load get_dict_val %}'
            '  <select name="{% autoescape off %}{{ row|get_select_key:field }}{% endautoescape %}">'
            '   {% autoescape off %}{{ row|get_dict_val:field|get_select_field:value_dict }}{% endautoescape %}'
            '  </select>'
            ' {% endfor %}'
            '{% endfor %}'
        )
        rendered_template = template_to_render.render(context)
        html_exp ="""<select name="(a1, b1, testitemc)">
        <option value="c1" selected>c1</option><option value="c2">c2</option>
        </select>"""
        self.assertHTMLEqual(html_exp, rendered_template)

#   def test_get_select_key()    