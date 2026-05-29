from django.urls import path
from . import views

app_name = 'freelance'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('my-projects/', views.MyProjectsView.as_view(), name='my_projects'),
    path('project/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<slug:slug>/bid/', views.SubmitBidView.as_view(), name='submit_bid'),
    path('project/<slug:slug>/review/', views.CreateReviewView.as_view(), name='create_review'),
    path('bid/<int:bid_id>/accept/', views.AcceptBidView.as_view(), name='accept_bid'),
]
