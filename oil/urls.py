from django.urls import path
from . import views 
app_name = 'oil'

urlpatterns = [
    path('', views.dashboard, name='oil'),
   

]