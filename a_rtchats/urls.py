from django.urls import path
from a_rtchats.views import *


urlpatterns = [
    path('', chat_view, name="home")
]
