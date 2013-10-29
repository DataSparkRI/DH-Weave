import re
from django.template.defaultfilters import slugify
import warnings
from weave.models import *
import os, json
from indicators.models import Indicator

# http://www.djangosnippets.org/snippets/690/
def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc



def get_related_items_entity_id(object_id=None,year=None, dataTable=None, name=None, title=None):
    """ Deduce the entity id of these weave items"""
    if object_id:
        obj = WeaveMetaPublic.objects.get(meta_name='object_id', meta_value=object_id)
        print obj.entity_id

    if year:
        obj = WeaveMetaPublic.objects.get(meta_name='year', meta_value=year)
        print obj.entity_id

    if dataTable:
        obj = WeaveMetaPublic.objects.get(meta_name='dataTable', meta_value=dataTable)
        print obj.entity_id

    if name:
        obj = WeaveMetaPublic.objects.get(meta_name='name', meta_value=name)
        print obj.entity_id

    if title:
        obj = WeaveMetaPublic.objects.get(meta_name='title', meta_value=title)
        print obj.entity_id


def default_xml_generator(public=True):

    head = u'''<WeaveDataSource name="WeaveDataSource">
    <attributeHierarchy encoding="xml">
    <hierarchy name="Weave Data Service">
    <category title="Data Tables" name="Data Tables">
    '''
    yield head
    w_categories = WeaveFlatPublicMeta.objects.all().only('dataTable').distinct('dataTable')
    for cat in w_categories:
        cat_head = u'''<category title="{0}" weaveEntityId="">'''.format(cat.dataTable)
        yield cat_head
        #attr_str = u''
        #for wobj in WeaveFlatPublicMeta.objects.filter(dataTable=cat.dataTable):
        #    attr_str += wobj.to_xml_attr()
        #    yield attr_str
        yield u'''</category>'''

    tail = u'''
    </category>
    </hierarchy>
    </attributeHierarchy>
    </WeaveDataSource>'''
    yield tail

def default_json_generator(data_table, user):
    """ Generate a attirbute set for a given data_table and user"""
    pub_inds = [str(i.id) for i in Indicator.objects.get_for_user(user).only('id')]

    for wobj in WeaveFlatPublicMeta.objects.filter(dataTable=data_table, object_id__in=pub_inds):
        yield wobj.to_ds_dict()

def generate_xml_file(public=True, path="/tmp/default.xml"):
    """ Generate a special default xml for a given user OR a public version with no unpublished indicators in it"""
    with open(path, "w+") as xml_file:
        for s in default_json_generator(public):
            xml_file.write(s.encode("utf8"))

    return "Wrote %s" % path

