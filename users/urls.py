from . import views
from django.conf.urls import url
from django.urls import path

app_name = 'users'

urlpatterns = [
	path('login/', views.LoginView.as_view(), name='login'),
	path('register/', views.RegisterView.as_view(), name='register'),
	path('logout/', views.logout_view, name='logout'),

	url(r'^profile-edit/(?P<username_>[\w-]+)/$', views.edit_profile, name='profile-edit'),
	url(r'^profile/f/liked_posts/$', views.liked_posts, name='liked_posts'),
	url(r'^profile/(?P<username_>[\w-]+)/$', views.profile, name='profile'),

	url(r'^top-users/$', views.top_users, name='top-users'),
]