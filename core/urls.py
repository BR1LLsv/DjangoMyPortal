from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notes/', views.notes, name='notes'),
    path('notes/toggle/<int:note_id>/', views.toggle_note, name='toggle_note'),
    path('notes/delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('messages/', views.inbox_view, name='inbox'),
    path('messages/<int:user_id>/', views.chat_view, name='chat'),
    path('messages/users/', views.user_list_view, name='user_list'),
]