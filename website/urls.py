from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('institution/', views.institution, name='institution'),
    path('province/', views.province, name='province'),
    path('province/ypg-fellowship/', views.ypg_fellowship, name='ypg_fellowship'),
    path('province/capacity-building-program/', views.capacity_building, name='capacity_building'),
    path('constitution/', views.constitution, name='constitution'),
    path('archives/', views.archives, name='archives'),
    path('support-us/', views.support_us, name='support_us'),
    path('team/<slug:slug>/', views.team_member, name='team_member'),
    path('publications/', views.publications, name='publications'),
    path('events/', views.events, name='events'),
]