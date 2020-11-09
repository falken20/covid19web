# by Richi Rod AKA @richionline / falken20

from django.urls import path

from . import views

urlpatterns = [
    path('', views.map_view, name='Heat map'),
    path('heatmap/', views.heatmap_view, name='Heat Map'),
]
