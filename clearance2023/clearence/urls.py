from django.urls import path

from clearence.views import index

app_name = 'clearence'

urlpatterns = [
    path('', index, name='index'),
]
