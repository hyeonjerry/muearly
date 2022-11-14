from django.urls import path

from muearly import views

urlpatterns = [
    path('', views.index, name='index'),
]
