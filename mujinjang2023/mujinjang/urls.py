from django.urls import path
from mujinjang import views
from django.views.generic import RedirectView

app_name = 'mujinjang'

urlpatterns = [
    path('', RedirectView.as_view(url='/00')),
    path('<str:time>/', views.index, name='index'),
]
