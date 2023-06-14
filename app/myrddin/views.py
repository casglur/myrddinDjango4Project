from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import TextField 
from pip._vendor.packaging.version import _parse_letter_version

import requests
import xmltodict
import json

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

"""
Function to load main poem user interface based on poem number parameter.

Gets keyword and version parameters from URL

Queries XML server via xpath to get title and version information

Passes results to page template

"""
def Poem(request, myrddin_id): 

    # Is there a keyword search parameter in the URL?
    if request.method == 'GET' and 'q' in request.GET:
        keyword = request.GET['q']
    else:
        keyword = ""

    # Is there a version number parameter in the URL?
    if request.method == 'GET' and 'v' in request.GET:
        version = request.GET['v']
    else:
        version = "1"    
    
    # Get the title of the poem
    title = ''
    
    title_xpath_query_url ='https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22myrddin' + myrddin_id + '_' + version + '_top%22]/tei:head'
    title_xpath_query_xml_response = requests.get(title_xpath_query_url)
    
    # Convert XML to a dictionary    
    title_dictionary = xmltodict.parse(title_xpath_query_xml_response.content)
    
    # Get the value the the title key from the dictionary
    title = title_dictionary['exist:result']['head'].get('#text')
      
    # Get the versions of the poem
    versions = ""        
    # previous_versions_xpath_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;declare%20variable%20$results%20:=%20doc(%27/db/apps/myrddin/data/myrddin_%s.xml%27)//tei:div[@type=%22lev0%22];%3Csections%3E{for%20$result%20in%20$results%20return%20%3Csection%3E{$result/@xml:id/string()}%3C/section%3E}%3C/sections%3E' % myrddin_id
    versions_xpath_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei%3D%22http%3A%2F%2Fwww.tei-c.org%2Fns%2F1.0%22%3Bdeclare%20variable%20%24results%20%3A%3D%20doc(%27%2Fdb%2Fapps%2Fmyrddin%2Fdata%2Fmyrddin_' + myrddin_id + '.xml%27)%2F%2Ftei%3Adiv%5B%40type%3D%22lev0%22%5D%3B%3Cexist:ids%3E%7Bfor%20%24result%20in%20%24results%20return%20%3Cexist:id%3E%7B%24result%2F%40xml%3Aid%2Fstring()%7D%3C%2Fexist:id%3E%7D%3C%2Fexist:ids%3E%09%0A' 
    versions_xpath_query_xml_response = requests.get(versions_xpath_query_url)
    
    # Convert XML to a dictionary    
    versions_dictionary = xmltodict.parse(versions_xpath_query_xml_response.content)
    
    # Get only the elements of the dictionary that contain the version ids      
    versions = versions_dictionary['exist:result']['exist:ids']['exist:id']

    # Is the versions xpath query a list?   
    if isinstance(versions, list):
        
        # Remove the characters from each key except for the poem number
        versions = [version[11:] for version in versions]
        versions = [version.replace("_top", "") for version in versions]         
    else:     
        #  If not a list, create one and insert the single value and remove the characters from each key except for the poem number 
        versions = []
        versions.insert(0, versions_dictionary['exist:result']['exist:ids']['exist:id'])
        versions = [version[11:] for version in versions]
        versions = [version.replace("_top", "") for version in versions]          
                        
    context = {
        'exist_path': exist_path,
        'myrddin_id': myrddin_id,
        'request': request,
        'title': title,
        'versions': versions,
        'version': version,
        }    
    return render(request, 'myrddin/poem-base.html', context)

def SiteRoot(request):
    context = {}    
    return render(request, 'myrddin/base.html', context)

def Test(request):
    context = {}    
    return render(request, 'myrddin/base-test.html', context)