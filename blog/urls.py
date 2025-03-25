from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.all_blogs, name='all_blogs'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    
    # Category URLs
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/', views.category_list, name='category_list'),
    
    # Blogger URLs
    path('bloggers/', views.BloggerListView.as_view(), name='blogger_list'),
    path('blogger/<int:pk>/', views.BloggerDetailView.as_view(), name='blogger_detail'),
    
    # Comment URLs
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Profile URLs
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    
    # Like/Dislike URLs
    path('post/<int:pk>/like/', views.post_like, name='post_like'),
    path('post/<int:pk>/dislike/', views.post_dislike, name='post_dislike'),
    
    # Registration URL (if not already defined in project urls.py)
    path('register/', views.register, name='register'),
] 