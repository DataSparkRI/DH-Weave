from django import template
from weave.api import get_hierarchy_as_xml, get_custom_hierarchy_as_xml

register = template.Library()

@register.simple_tag
def weave_data_hierarchy():
    return get_hierarchy_as_xml()

@register.simple_tag
def weave_custom_data_hierarchy(title, h_list):
    return get_custom_hierarchy_as_xml(title, h_list)
