from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser

from weave.models import ClientConfiguration
from weave.util import deprecated
import simplejson as json
import elementtree.ElementTree as ET
from django.views.decorators.csrf import csrf_exempt, csrf_protect

@deprecated
def client_config(request, config_slug):
    config = get_object_or_404(ClientConfiguration, slug=config_slug)
    return HttpResponse(config.get_xml(), mimetype="application/xml")

@deprecated
def get_user_configs(request):
    # get a list of user configurations
    results = {}
    if request.user.is_authenticated():
        configs = ClientConfiguration.objects.filter(user=request.user).only('slug', 'name')
        for conf in configs:
            print conf
    else:
        pass
    return HttpResponse(json.dumps(results), mimetype="application/json")



def get_client_config(request, config_id):
    """ Return client configs storede in the database
        NOTE: Right now all client configs are of content_format 'json'
    """
    try:
        # find the client config by id, if its public continue else, check
        # for to see if the user is the right one
        config = ClientConfiguration.objects.defer('content').get(id=config_id)

        if not config.is_public: # this config is not public so only the creator can see it.
            if request.user.is_authenticated():
                config = get_object_or_404(ClientConfiguration, id=config_id, userprofile=request.user.userprofile)
            else:
                raise Http404
        # if the config is public, we just finish the request
        if config.content_format == 'xml':
            return HttpResponse(config.content, mimetype="application/xml")
        elif config.content_format == 'json':
            result = json.dumps({'cc_name': config.name})
            result = result.replace("}", ', "content":%s}' % config.content)
            return HttpResponse(result, mimetype="application/json")

    except ClientConfiguration.DoesNotExist:
        raise Http404

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_client_config(request):
    from random import randrange
    """ Save a client config from a POST request
        We can ovewrite or create a new one. Name defaults to Unititled + random junk
        TODO: This requires Client Configurations to be attached to a userprofile. Its too tightly coupled to Datahub.
    """
    cc_name = request.POST.get('cc_name', 'Untitled_%010x' % randrange(256**15))
    data = request.POST.get('cc_data', None)
    action = 'fail'

    try:
        config = request.user.userprofile.client_configs.get(name=cc_name)
        action = 'update'

    except ClientConfiguration.DoesNotExist:
        #create a new one
        config = ClientConfiguration(content_object=request.user.userprofile, name=cc_name)
        action = 'create'

    # because we are gonna be transitioning everyones client configs to JSON,
    # we need to do some validation here

    if data:
        try:
            json.loads(data)
            # its valid json
            config.content=data
            config.content_format = 'json'
            config.save()
            result = {'status':'success-json','cc-slug':config.slug, 'action':action}
        except json.JSONDecodeError:
            # try some basic xml validation
            try:
                ET.fromstring(data)
                config.content=data
                config.content_format = 'xml'
                config.save()
                result = {'status':'success-xml', 'cc-slug':config.slug, 'action':action}
            except Error:
                result = {'status':'error'}


    return HttpResponse(json.dumps(result), mimetype="application/json")

def embed_weave(request):
    """ A view that loads a Weave Instance.
        if there is a wf (a weave file on disk) we ignore an client configs what may also be passed to the view.
        Also we check to see where the referer is coming from. If its from datahub then we want to display some extra ui, if not we can display links to datahub.
    """
    ctx = {}
    ctx['authenticated'] = request.user.is_authenticated()
    viz = request.GET.get('viz', None)
    title = request.GET.get('ttl', None)
    width = request.GET.get('w', None)
    height = request.GET.get('h', None)
    editable = request.GET.get('e', "false") # If the user is logged in should we display controls?
    if editable == "true":
        editable = True
    else:
        editable = False

    c_config = request.GET.get('cc', None)
    referer = request.GET.get('ref', None)

    if referer == settings.DATAHUB_HOST:
        dh_refered = True
    else:
        dh_refered = False

    ctx['weave_root'] = getattr(settings,'WEAVE_ROOT', "http://127.0.0.1:8081/") # SETTING
    ctx['weave_allowed_domain'] = getattr(settings, 'WEAVE_ALLOWED_DOMAIN', "127.0.0.1")
    ctx['dh_refered'] = dh_refered
    ctx['height'] = height
    ctx['width'] = width
    ctx['ttl'] = title
    ctx['host'] = request.get_host()
    ctx['editable'] = editable

    if c_config is not None:
        ctx['client_config'] = c_config

    return render_to_response('weave.html', ctx, context_instance=RequestContext(request))




