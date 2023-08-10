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
    path('poem-manuscript/<slug:myrddin_id>/', views.PoemManuscript, name='poem_manuscript'),
    # path('', lambda req: redirect('/home/')),
    path('test', views.Test, name='test'),
    
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]
