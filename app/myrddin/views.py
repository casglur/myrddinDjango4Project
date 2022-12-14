from django.shortcuts import render



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import TextField 
from pip._vendor.packaging.version import _parse_letter_version

app_url_path = '/myrddin'

exist_path = 'http://localhost:8080'

def custom_page_not_found_view(request, exception):
    response = render(request, "emco/errors/404.html", {})
    response.status_code = 404
    return response

def Location(request, location_id): 

    if request.method == 'GET' and 'q' in request.GET:
        keyword = request.GET['q']
    else:
        keyword = ""

    context = {
        'exist_path': exist_path, 
        'location_id': location_id,
        }    
    return render(request, 'myrddin/location.html', context)

def Poem(request, myrddin_id): 

    if request.method == 'GET' and 'q' in request.GET:
        keyword = request.GET['q']
    else:
        keyword = ""

    context = {
        'exist_path': exist_path, 
        'myrddin_id': myrddin_id,
        }    
    return render(request, 'myrddin/poem.html', context)

def SiteRoot(request):
    context = {}    
    return render(request, 'myrddin/base.html', context)
