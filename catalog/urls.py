from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.MediaListView.as_view(), name='media_list'),
    path('add/', views.MediaCreateView.as_view(), name='media_add'),
    path('<slug:slug>/', views.MediaDetailView.as_view(), name='media_detail'),
    path('<slug:slug>/edit/', views.MediaUpdateView.as_view(), name='media_edit'),
    path('<slug:slug>/delete/', views.MediaDeleteView.as_view(), name='media_delete'),
]
