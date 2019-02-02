from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from forum.views import guidebook
from users.views import about_us, helping

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('forum.urls')),
    url(r'^user/', include('users.urls')),
    #url(r'^test/', include('test_conf.urls'))
    url(r'^guidebook/$', guidebook, name='guidebook'),
    url(r'^about-us/$', about_us, name='about-us'),
    url(r'^help/$', helping, name='help')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''
Top Users

About Us

GuideBook

Help


'''
