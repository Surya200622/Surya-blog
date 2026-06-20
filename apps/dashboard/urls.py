from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('posts/', views.DashboardPostsView.as_view(), name='posts'),
    path('analytics/', views.DashboardAnalyticsView.as_view(), name='analytics'),
    path('payments/', views.DashboardPaymentsView.as_view(), name='payments'),
    path('settings/', views.DashboardSettingsView.as_view(), name='settings'),
    path('saved/', views.DashboardSavedItemsView.as_view(), name='saved'),
]
