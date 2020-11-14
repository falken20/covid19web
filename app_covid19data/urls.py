# by Richi Rod AKA @richionline / falken20

from django.urls import path

from . import views

urlpatterns = [
    # path('resume/', views.resume_view, name='Resume data'),
    path('heatmap/', views.heatmap_view, name='Heat Map'),
]
