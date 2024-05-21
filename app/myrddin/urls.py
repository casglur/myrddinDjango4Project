"""
URL configuration for myrddin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.shortcuts import redirect

from . import views

app_name = 'myrddin'

handler404 = (views.custom_page_not_found_view)

urlpatterns = [
    path('',  RedirectView.as_view(url='poem/', permanent=False), name='index'),
    path('poem/', views.Poem, name='poem'),
    path('poem/<slug:myrddin_id>/', views.Poem, name='poem'),
    path('location/<slug:location_id>/', views.Location, name='location'), 
    path('locations-list/', views.DataList, name='locations_list'), 
    path('poem-manuscript/<slug:myrddin_id>/', views.PoemManuscript, name='poem_manuscript'),
    # path('', lambda req: redirect('/home/')),
    path('test', views.Test, name='test'),
    
    path('i18n/', include('django.conf.urls.i18n')),
    path('set_language/(?P<language_id>d+)/$', views.set_language, name='set_language'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]
