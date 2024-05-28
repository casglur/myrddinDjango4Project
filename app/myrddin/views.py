from django.utils.translation import gettext as _
from django.shortcuts import render

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import TextField

from django.http import HttpResponseRedirect

from myrddin.models import Location

from pip._vendor.packaging.version import _parse_letter_version

import requests
import xmltodict
import json
import lxml

from lxml import etree
from io import StringIO, BytesIO

app_url_path = '/myrddin'

exist_path = 'http://localhost:8080'

def custom_page_not_found_view(request, exception):
    response = render(request, "myrddin/errors/404.html", {})
    response.status_code = 404
    return response

"""
Function to load data from table
"""
def DataList(request):
    objs = Location.objects.order_by('standard_form').all()

    return render(request,'myrddin/data-list-view.html',{'objs':objs})


"""
Function to test fetching manuscript details for a poem
"""
def PoemManuscript(request, myrddin_id="1"):

    # Is there a version number parameter in the URL?
    if request.method == 'GET' and 'v' in request.GET:
        poem_version = request.GET['v']
    else:
        poem_version = "1"
    print('poem version request: ' + poem_version)
        
    # Is there a manuscript version number parameter in the URL?
    manuscript = '1'
    if request.method == 'GET' and 'm' in request.GET:
        manuscript_version = request.GET['m']
    else:
        manuscript_version = '1'
    print('manuscript version request: ' + manuscript_version)
        
    # Is there a manuscript type parameter in the URL?
    manuscript_type = ''
    manuscript_type_text = 'mydryddol'
    
    if request.method == 'GET' and 'mt' in request.GET:
        manuscript_type = request.GET['mt']
        if manuscript_type == 'm':
            manuscript_type_text = 'mydryddol'
        else:
            manuscript_type_text = 'diplomatig' 
    print('manuscript type: ' + manuscript_type_text)
               
    ''' Get the title of the poem
    ====================================================
    '''
    title = ''
    title_xpath_query_url ='https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22myrddin_' + myrddin_id + '_' + poem_version + '_top%22]/tei:head'
    title_xpath_query_xml_response = requests.get(title_xpath_query_url)
    
    title_xml_root = lxml.etree.fromstring(title_xpath_query_xml_response.content)
    title_list = title_xml_root.xpath('//tei:head/text()', namespaces={ 'tei': 'http://www.tei-c.org/ns/1.0'})
    title = title_list[0]


    ''' Get the versions of the poem
    ====================================================
    '''    
    poem_versions = ""        
    # previous_versions_xpath_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;declare%20variable%20$results%20:=%20doc(%27/db/apps/myrddin/data/myrddin_%s.xml%27)//tei:div[@type=%22lev0%22];%3Csections%3E{for%20$result%20in%20$results%20return%20%3Csection%3E{$result/@xml:id/string()}%3C/section%3E}%3C/sections%3E' % myrddin_id
    poem_versions_xpath_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei%3D%22http%3A%2F%2Fwww.tei-c.org%2Fns%2F1.0%22%3Bdeclare%20variable%20%24results%20%3A%3D%20doc(%27%2Fdb%2Fapps%2Fmyrddin%2Fdata%2Fmyrddin_' + myrddin_id + '.xml%27)%2F%2Ftei%3Adiv%5B%40type%3D%22lev0%22%5D%3B%3Cexist:ids%3E%7Bfor%20%24result%20in%20%24results%20return%20%3Cexist:id%3E%7B%24result%2F%40xml%3Aid%2Fstring()%7D%3C%2Fexist:id%3E%7D%3C%2Fexist:ids%3E%09%0A' 
    poem_versions_xpath_query_xml_response = requests.get(poem_versions_xpath_query_url)
    
    poem_versions_xml_root = lxml.etree.fromstring(poem_versions_xpath_query_xml_response.content)
    poem_versions_list = poem_versions_xml_root.xpath('//exist:id/text()', namespaces={ 'exist': 'http://exist.sourceforge.net/NS/exist'})
    print('poem_versions_list: ' + str(poem_versions_list))
    
    print('versions_xpath_query_xml_response.content: ' + poem_versions_xpath_query_xml_response.content.decode())
    print('version list length: ' + str(len(poem_versions_list)))
    print(poem_versions_list)
    for v in poem_versions_list:
        print(v)

    # Remove the characters from each key except for the poem number
    poem_versions = [poem_version[11:] for poem_version in poem_versions_list]
    poem_versions = [poem_version.replace("_top", "") for poem_version in poem_versions]
    poem_versions = [poem_version.replace("_", "") for poem_version in poem_versions] 
          
        
    '''Get the manuscript ids for the selected poem version
    ====================================================
    '''    
    manuscripts_ids_list = []  
          
    manuscripts_ids_xpath_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22myrddin_' + myrddin_id + '_' + poem_version +'_top%22]//tei:div[@type=%22llawysgrifau%22]/tei:div[@xml:id]/string(@xml:id)&_howmany=20' 
    manuscripts_ids_xpath_query_xml_response = requests.get(manuscripts_ids_xpath_query_url)
    print(type(manuscripts_ids_xpath_query_xml_response))
    
    print('manuscripts_ids_xpath_query_xml_response.content: ' + manuscripts_ids_xpath_query_xml_response.content.decode())
    
    # Convert XML response to an XML tree
    manuscripts_ids_xml_root = lxml.etree.fromstring(manuscripts_ids_xpath_query_xml_response.content)
    
    # Create list from output of xpath query                             
    manuscripts_ids_list = manuscripts_ids_xml_root.xpath('//exist:value/text()', namespaces={ 'exist': 'http://exist.sourceforge.net/NS/exist'})
    
    # Create a count of manuscripts
    manuscripts_ids_count = len(manuscripts_ids_list)
    
    # Create range of manuscripts
    manuscripts_ids_range = range(0+1,manuscripts_ids_count+1)
    
    has_manuscripts = ''
    has_multiple_manuscripts = ''
    
    print(type(manuscripts_ids_list)) 
    
    print('manuscripts_ids_list length is: ' + str(len(manuscripts_ids_list)))
    
    for m in manuscripts_ids_list:
        print(m)     
        
    print('number of Manuscripts: ' + str(len(manuscripts_ids_list)))              
    
    # Set value of has_multiple_manuscripts variable if the list has more than one index
    if len(manuscripts_ids_list) == 0:
        has_multiple_manuscripts = 0    
    else:    
        if len(manuscripts_ids_list) < 2:
            has_multiple_manuscripts = 0
        else:
            has_multiple_manuscripts = 1            
            
    ''' Get the title of the current manuscript
    ============================================
    '''            
    manuscript_title = ''
    manuscript_title_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22' + manuscripts_ids_list[int(manuscript_version) - 1] + '_' + manuscript_type_text + '%22]/tei:head'
    manuscript_title_xpath_query_xml_response = requests.get(manuscript_title_query_url)
    
    manuscript_title_xml_root = lxml.etree.fromstring(manuscript_title_xpath_query_xml_response.content)
    manuscript_title_list = manuscript_title_xml_root.xpath('//tei:head/text()', namespaces={ 'tei': 'http://www.tei-c.org/ns/1.0'})
    manuscript_title = manuscript_title_list[0]
    print('manuscript title list: ' + str(manuscript_title_list))
    
    ''' Get the current manuscript xml:id
    ============================================
    '''               
    current_manuscript_xml_id = manuscripts_ids_list[int(manuscript_version) - 1]
            
    context = {
        'current_manuscript_type': manuscript_type_text,
        'current_manuscript_xml_id': current_manuscript_xml_id,
        'exist_path': exist_path,
        'has_multiple_manuscripts': has_multiple_manuscripts,
        'manuscripts_ids_count': manuscripts_ids_count,
        'manuscripts_ids_list': manuscripts_ids_list,
        'manuscripts_ids_range': manuscripts_ids_range,
        'manuscripts_ids_xpath_query_url': manuscripts_ids_xpath_query_url,
        'manuscript_version': manuscript_version,
        'manuscript_title': manuscript_title,      
        'manuscript_title_query_url': manuscript_title_query_url,
        'manuscript_title_list': manuscript_title_list,
        'myrddin_id': myrddin_id,
        'poem_versions': poem_versions,
        'poem_version': poem_version,
        'request': request,
        'title': title,
        'title_xpath_query_url': title_xpath_query_url
        }    
    return render(request, 'myrddin/poem-manuscript-test.html', context)                

"""
Function to load main poem user interface based on poem number parameter.

Gets keyword and version parameters from URL

Queries XML server via xpath to get title and version information

Passes results to page template

"""
def Poem(request, myrddin_id="1"):

    # Is there a version number parameter in the URL?
    if request.method == 'GET' and 'v' in request.GET:
        poem_version = request.GET['v']
    else:
        poem_version = "1"    
        
    # Is there a manuscript version number parameter in the URL?
    manuscript = '1'
    if request.method == 'GET' and 'm' in request.GET:
        manuscript_version = request.GET['m']
    else:
        manuscript_version = '1'  
        
    # Is there a manuscript type parameter in the URL?
    manuscript_type = ''
    manuscript_type_text = 'mydryddol'
    
    if request.method == 'GET' and 'mt' in request.GET:
        manuscript_type = request.GET['mt']
        if manuscript_type == 'm':
            manuscript_type_text = 'mydryddol'
        else:
            manuscript_type_text = 'diplomatig' 
    print('Manuscript type: ' + manuscript_type_text)
    
    # Has the user selected the modern view of the poem?
    modern_choice = ''
    if request.method == 'GET' and 'mod' in request.GET:
        modern_choice = request.GET['mod']
        print('Modern Version Selected')    
               
    ''' Get the title of the poem
    ====================================================
    '''
    title = ''
    title_xpath_query_url ='https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22myrddin_' + myrddin_id + '_' + poem_version + '_top%22]/tei:head'
    title_xpath_query_xml_response = requests.get(title_xpath_query_url)
    
    title_xml_root = lxml.etree.fromstring(title_xpath_query_xml_response.content)
    title_list = title_xml_root.xpath('//tei:head/text()', namespaces={ 'tei': 'http://www.tei-c.org/ns/1.0'})
    title = title_list[0]


    ''' Get the versions of the poem
    ====================================================
    '''    
    poem_versions = ""        
    # previous_versions_xpath_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;declare%20variable%20$results%20:=%20doc(%27/db/apps/myrddin/data/myrddin_%s.xml%27)//tei:div[@type=%22lev0%22];%3Csections%3E{for%20$result%20in%20$results%20return%20%3Csection%3E{$result/@xml:id/string()}%3C/section%3E}%3C/sections%3E' % myrddin_id
    poem_versions_xpath_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei%3D%22http%3A%2F%2Fwww.tei-c.org%2Fns%2F1.0%22%3Bdeclare%20variable%20%24results%20%3A%3D%20doc(%27%2Fdb%2Fapps%2Fmyrddin%2Fdata%2Fmyrddin_' + myrddin_id + '.xml%27)%2F%2Ftei%3Adiv%5B%40type%3D%22lev0%22%5D%3B%3Cexist:ids%3E%7Bfor%20%24result%20in%20%24results%20return%20%3Cexist:id%3E%7B%24result%2F%40xml%3Aid%2Fstring()%7D%3C%2Fexist:id%3E%7D%3C%2Fexist:ids%3E%09%0A' 
    poem_versions_xpath_query_xml_response = requests.get(poem_versions_xpath_query_url)
    
    poem_versions_xml_root = lxml.etree.fromstring(poem_versions_xpath_query_xml_response.content)
    poem_versions_list = poem_versions_xml_root.xpath('//exist:id/text()', namespaces={ 'exist': 'http://exist.sourceforge.net/NS/exist'})
    
    print('versions_xpath_query_xml_response.content: ' + poem_versions_xpath_query_xml_response.content.decode())
    print('version list length: ' + str(len(poem_versions_list)))
    print(poem_versions_list)
    for v in poem_versions_list:
        print(v)

    # Remove the characters from each key except for the poem number
    poem_versions = [poem_version[11:] for poem_version in poem_versions_list]
    poem_versions = [poem_version.replace("_top", "") for poem_version in poem_versions]
    poem_versions = [poem_version.replace("_", "") for poem_version in poem_versions] 
          
        
    '''Get the manuscript ids for the selected poem version
    ====================================================
    '''    
    manuscripts_ids_list = []  
          
    manuscripts_ids_xpath_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22myrddin_' + myrddin_id + '_' + poem_version +'_top%22]//tei:div[@type=%22llawysgrifau%22]/tei:div[@xml:id]/string(@xml:id)&_howmany=20' 
    manuscripts_ids_xpath_query_xml_response = requests.get(manuscripts_ids_xpath_query_url)
    print(type(manuscripts_ids_xpath_query_xml_response))
    
    print('manuscripts_ids_xpath_query_xml_response.content: ' + manuscripts_ids_xpath_query_xml_response.content.decode())
    
    # Convert XML response to an XML tree
    manuscripts_ids_xml_root = lxml.etree.fromstring(manuscripts_ids_xpath_query_xml_response.content)
    
    # Create list from output of xpath query                             
    manuscripts_ids_list = manuscripts_ids_xml_root.xpath('//exist:value/text()', namespaces={ 'exist': 'http://exist.sourceforge.net/NS/exist'})
    
    # Create a count of manuscripts
    manuscripts_ids_count = len(manuscripts_ids_list)
    
    # Create range of manuscripts
    manuscripts_ids_range = range(0+1,manuscripts_ids_count+1)
    
    has_manuscripts = ''
    has_multiple_manuscripts = ''
    
    print(type(manuscripts_ids_list)) 
    
    print('manuscripts_ids_list length is: ' + str(len(manuscripts_ids_list)))
    
    for m in manuscripts_ids_list:
        print(m)     
        
    print('number of Manuscripts: ' + str(len(manuscripts_ids_list)))              
    
    # Set value of has_multiple_manuscripts variable if the list has more than one index
    if len(manuscripts_ids_list) == 0:
        has_multiple_manuscripts = 0    
    else:    
        if len(manuscripts_ids_list) < 2:
            has_multiple_manuscripts = 0
        else:
            has_multiple_manuscripts = 1            
            
    ''' Get the title of the current manuscript
    ============================================
    '''            
    manuscript_title = ''
    manuscript_title_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)//tei:div[@xml:id=%22' + manuscripts_ids_list[int(manuscript_version) - 1] + '_' + manuscript_type_text + '%22]/tei:head'
    manuscript_title_xpath_query_xml_response = requests.get(manuscript_title_query_url)
    
    manuscript_title_xml_root = lxml.etree.fromstring(manuscript_title_xpath_query_xml_response.content)
    manuscript_title_list = manuscript_title_xml_root.xpath('//tei:head/text()', namespaces={ 'tei': 'http://www.tei-c.org/ns/1.0'})
    manuscript_title = manuscript_title_list[0]
    
    ''' Get the editor of the current poem
    ============================================
    '''            
    editor_name = ''
    editor_name_query_url = 'https://dh-existdb.swansea.ac.uk/exist/apps/myrddin/data?_query=declare%20namespace%20tei=%22http://www.tei-c.org/ns/1.0%22;doc(%27/db/apps/myrddin/data/myrddin_' + myrddin_id + '.xml%27)/tei:TEI/tei:text/tei:body/tei:div/tei:div[1]/tei:note[1]'
    editor_name_xpath_query_xml_response = requests.get(editor_name_query_url)
    
    editor_name_xml_root = lxml.etree.fromstring(editor_name_xpath_query_xml_response.content)
    editor_name_list = editor_name_xml_root.xpath('//tei:note/text()', namespaces={ 'tei': 'http://www.tei-c.org/ns/1.0'})
    editor_name = editor_name_list[0]
    
    ''' Get the current manuscript xml:id
    ============================================
    '''               
    current_manuscript_xml_id = manuscripts_ids_list[int(manuscript_version) - 1]
            
    context = {
        'current_manuscript_type': manuscript_type_text,
        'current_manuscript_xml_id': current_manuscript_xml_id,
        'editor_name': editor_name,
        'exist_path': exist_path,
        'has_multiple_manuscripts': has_multiple_manuscripts,
        'manuscripts_ids_count': manuscripts_ids_count,
        'manuscripts_ids_list': manuscripts_ids_list,
        'manuscripts_ids_range': manuscripts_ids_range,
        'manuscripts_ids_xpath_query_url': manuscripts_ids_xpath_query_url,
        'manuscript_version': manuscript_version,
        'manuscript_title': manuscript_title,
        'modern_choice': modern_choice,        
        'myrddin_id': myrddin_id,
        'poem_versions': poem_versions,
        'poem_version': poem_version,
        'request': request,
        'title': title
        }    

    return render(request, 'myrddin/poem-base.html', context)

def set_language(request):
    if request.GET.has_key('language_id'):  # Set language in Session variable
        # Redirect to home
        request.session['language_id'] = request.GET['language_id']
    return HttpResponseRedirect('/')

def Test(request):
    context = {}    
    return render(request, 'myrddin/base-test.html', context)
