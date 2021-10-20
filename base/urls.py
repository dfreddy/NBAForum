from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),

    path('', views.home, name='home'),
    
    path('post/<int:id>/', views.post, name='post'),
    path('create-post', views.createPost, name='create-post'),
    path('update-post/<int:id>', views.updatePost, name='update-post'),
    path('delete-post/<int:id>', views.deletePost, name='delete-post'),
    path('delete-message/<int:id>', views.deleteMessage, name='delete-message'),

    path('profile/<int:id>/', views.userProfile, name='user-profile'),
    path('update-user/', views.updateUser, name='update-user'),
    path('save-post/<int:id>', views.savePost, name='save-post'),
    path('unsave-post/<int:id>', views.unsavePost, name='unsave-post'),
    
    path('topics/', views.topicsPage, name="topics"),
]