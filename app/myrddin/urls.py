from django.contrib import admin
from django.urls import include, path

from django.shortcuts import redirect

from . import views

app_name = 'myrddin'

handler404 = (views.custom_page_not_found_view)

urlpatterns = [
    path('poem-view/<slug:myrddin_id>/', views.PoemView, name='poem-view'),   



    # path('', lambda req: redirect('/home/')),
    path('', views.SiteRoot, name='site-root'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]
