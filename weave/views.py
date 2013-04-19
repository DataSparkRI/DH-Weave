from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required

from weave.models import ClientConfiguration
from weave.util import deprecated
import simplejson as json
import elementtree.ElementTree as ET

@deprecated
def client_config(request, config_slug):
    config = get_object_or_404(ClientConfiguration, slug=config_slug)
    return HttpResponse(config.get_xml(), mimetype="application/xml")


def get_client_config(request, config_slug):
    """ Return client configs stored in the database """
    try:
        # find the client config by slug, if its public continue else, check
        # for to see if the user is the right one
        config = ClientConfiguration.objects.defer('content').get(slug=config_slug)

        if not config.is_public:
            config = get_object_or_404(ClientConfiguration, slug=config_slug, user=request.user)

        if config.content_format == 'xml':
            return HttpResponse(config.content, mimetype="application/xml")
        elif config.content_format == 'json':
            return HttpResponse(config.content, mimetype="application/json")

    except ClientConfiguration.DoesNotExist:
        raise Http404


@login_required
def save_client_config(request, config_slug):
    from random import randrange
    """ Save a client config from a POST request
        We can ovewrite or create a new one. Name defaults to Unititled + random junk
    """
    cc_name = request.POST.get('cc_name', 'Untitled_%010x' % randrange(256**15))
    data = request.POST.get('cc_data', None)

    try:
        config = ClientConfiguration.objects.get(user=request.user, slug=config_slug)

    except ClientConfiguration.DoesNotExist:
        # create a new one
        config = ClientConfiguration(user=request.user, name=cc_name)

    # because we are gonna be transitioning everyones client configs to JSON,
    # we need to do some validation here
    if data:
        try:
            json.loads(data)
            # its valid json
            config.content=data
            config.content_format = 'json'
            config.save()
            result = {'status':'success-json','cc-slug':config.slug}
        except json.JSONDecodeError:
            # try some basic xml validation
            try:
                ET.fromstring(data)
                config.content=data
                config.content_format = 'xml'
                config.save()
                result = {'status':'success-xml', 'cc-slug':config.slug}
            except Error:
                result = {'status':'error'}


    return HttpResponse(json.dumps(result), mimetype="application/json")

def embed_weave(request):
    """ A view that loads a Weave Instance.
        if there is a wf (a weave file on disk) we ignore an client configs what may also be passed to the view.
    """
    ctx = {}
    ctx['authenicated'] = request.user.is_authenticated()
    viz = request.GET.get('viz', None)
    #weave_config = request.GET.get('wf', "default.xml") # what is default?
    #c_config = request.GET.get('cc', None)
    referer = request.GET.get('ref', None)

    #ctx['weave_config'] = weave_config
    #ctx['client_config'] = c_config
    ctx['weave_root'] = getattr(settings,'WEAVE_ROOT', "http://127.0.0.1:8080/") # SETTING
    ctx['referer'] = referer

    return render_to_response('weave.html', ctx, context_instance=RequestContext(request))




