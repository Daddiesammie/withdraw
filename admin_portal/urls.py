from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('documents/', views.document_review, name='document_review'),
    path('login-as-user/<int:user_id>/', views.login_as_user, name='login_as_user'),

]
