from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import BlogPost, Comment, Category, Profile

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_date',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_date')
    list_filter = ('post_date', 'author', 'categories')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)
    date_hierarchy = 'post_date'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_date', 'is_active')
    list_filter = ('created_date', 'is_active')
    search_fields = ('content', 'author__username')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    search_fields = ('user__username', 'location', 'bio')
    readonly_fields = ('user',)  # Make user field read-only
    exclude = ('user',)  # Exclude user field from the form

    def has_add_permission(self, request):
        return False  # Prevent creating new profiles through admin

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting profiles through admin

# Unregister the default User admin
admin.site.unregister(User)

# Register User with custom admin
class CustomUserAdmin(UserAdmin):
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.register(User, CustomUserAdmin)
