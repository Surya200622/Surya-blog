from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),
    path('<str:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<str:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('<str:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('<str:slug>/comment/', views.add_comment, name='add_comment'),
    path('<str:slug>/like/', views.toggle_like, name='toggle_like'),
]
