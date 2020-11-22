# by Richi Rod AKA @richionline / falken20

from django.urls import path

from . import views

urlpatterns = [
    path('', views.resume_view, name='Resume Data'),
    path('global/', views.global_view, name='Global Rank'),
    path('detail/<str:country>/', views.detail_view, name='Resume Spain Areas'),
    path('heatmap/', views.heatmap_view, name='Heat Map'),
    path('graph/<str:graph_type>/', views.graph_view, name='Graph'),
]
