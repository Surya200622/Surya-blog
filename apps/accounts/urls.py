from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile_view'),
    path('u/<str:username>/', views.PublicProfileView.as_view(), name='public_profile'),
]
