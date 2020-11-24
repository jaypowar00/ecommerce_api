from django.urls import path
from .views import *

urlpatterns = [
    path('profile', profile, name='profile'),
    path('register', register, name='register'),
    path('auth/login', login, name='login'),
    path('auth/logout', logout, name='logout'),
    path('profile/address', user_address, name='user_address'),
    path('auth/delete-user', delete_user, name='delete_user'),
    path('auth/token-refresh', refresh_token, name='refresh_token'),
]