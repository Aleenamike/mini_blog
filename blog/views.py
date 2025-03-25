from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BlogPost, Comment, Category, Profile
from .forms import CommentForm, UserRegistrationForm, BlogPostForm, ProfileForm
from django.core.paginator import Paginator
from django.http import JsonResponse

# Create your views here.

def home(request):
    """Home page view"""
    posts = BlogPost.objects.all().order_by('-post_date')
    categories = Category.objects.all()
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'categories': categories,
        'is_paginated': posts.has_other_pages(),
        'page_obj': posts
    })

@login_required
def all_blogs(request):
    """All blogs view that requires login"""
    posts = BlogPost.objects.all().order_by('-post_date')
    categories = Category.objects.all()
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/all_blogs.html', {
        'posts': posts,
        'categories': categories,
        'is_paginated': posts.has_other_pages(),
        'page_obj': posts
    })

class PostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.all()

class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

class BlogListView(LoginRequiredMixin, ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    login_url = 'login'

    def get_queryset(self):
        return BlogPost.objects.all().order_by('-post_date')

class BlogDetailView(LoginRequiredMixin, DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    login_url = 'login'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get comments ordered by created_date (oldest first)
        context['comments'] = self.object.comments.all().order_by('created_date')
        context['comment_form'] = CommentForm()
        return context

class AuthorDetailView(DetailView):
    model = User
    template_name = 'blog/author_detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = BlogPost.objects.filter(author=self.object)
        return context

class BloggerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'blog/blogger_list.html'
    context_object_name = 'bloggers'
    login_url = 'login'

    def get_queryset(self):
        return User.objects.filter(blogpost__isnull=False).distinct()

class BloggerDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/blogger_detail.html'
    context_object_name = 'blogger'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = BlogPost.objects.filter(author=self.object).order_by('-post_date')
        # Calculate total likes and comments for each post
        for post in posts:
            post.total_likes_count = post.total_likes()
            post.total_comments_count = post.comments.count()
        context['posts'] = posts
        # Calculate overall statistics
        context['total_likes'] = sum(post.total_likes() for post in posts)
        context['total_comments'] = sum(post.comments.count() for post in posts)
        return context

@login_required
def add_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return redirect('blog:post_detail', pk=post.pk)
    return redirect('blog:post_detail', pk=post.pk)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def post_list(request):
    posts = BlogPost.objects.all().order_by('-post_date')
    categories = Category.objects.all()
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'categories': categories,
        'is_paginated': posts.has_other_pages(),
        'page_obj': posts
    })

@login_required
def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    # Get only parent comments (no replies) and order them by creation date
    comments = post.comments.filter(parent=None).order_by('created_date')
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            return redirect('blog:post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'new_comment': new_comment
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Your post has been created!')
            return redirect('blog:post_detail', pk=post.pk)
        else:
            print("❌ Form errors:", form.errors)  # Debugging

    else:
        form = BlogPostForm()

    categories = Category.objects.all()  # ✅ Fetch categories for the form
    return render(request, 'blog/post_form.html', {'form': form, 'categories': categories})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user != post.author:
        messages.error(request, "You can only edit your own posts!")
        return redirect("blog:post_detail", pk=pk)

    if request.method == "POST":
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # Save the many-to-many relationships if the form has them
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            messages.success(request, "Your post has been updated!")
            return redirect("blog:post_detail", pk=post.pk)
        else:
            print("Form errors:", form.errors)  # Debug form errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm(instance=post)
    
    # Get all categories for the form if needed
    categories = Category.objects.all()
    return render(request, 'blog/post_edit.html', {
        'form': form,
        'post': post,
        'categories': categories
    })

@login_required
def post_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You can only delete your own posts!')
        return redirect('blog:post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted!')
        return redirect('blog:all_blogs')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {'categories': categories})

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    posts = category.posts.all()
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts
    })

@login_required
def add_reply(request, pk):
    """Add a reply to a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create reply
            reply = Comment.objects.create(
                post=comment.post,
                author=request.user,
                content=content,
                parent=comment
            )
            
            # Return JSON response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'author': reply.author.username,
                    'content': reply.content,
                    'date': reply.created_date.strftime('%B %d, %Y'),
                    'id': reply.pk
                })
            
            # Redirect for non-AJAX
            return redirect('blog:post_detail', pk=comment.post.pk)
    
    # Redirect if not POST
    return redirect('blog:post_detail', pk=comment.post.pk)

@login_required
def delete_comment(request, pk):
    try:
        comment = get_object_or_404(Comment, pk=pk)
        if request.user == comment.author:
            post_pk = comment.post.pk
            comment.delete()
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Comment deleted successfully!'
                })
            
            # Regular redirect for non-AJAX requests
            messages.success(request, 'Comment deleted successfully!')
            return redirect('blog:post_detail', pk=post_pk)
        
        # Handle unauthorized deletion
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'You can only delete your own comments!'
            }, status=403)
        
        messages.error(request, 'You can only delete your own comments!')
        return redirect('blog:post_detail', pk=comment.post.pk)
    except Exception as e:
        print(f"Error deleting comment {pk}: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
        messages.error(request, f'Error deleting comment: {str(e)}')
        return redirect('blog:post_detail', pk=comment.post.pk)

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = BlogPost.objects.filter(author=user)
    total_likes = sum(post.total_likes() for post in posts)
    total_comments = sum(post.comments.count() for post in posts)
    return render(request, 'blog/profile.html', {
        'profile': user.profile,
        'user': request.user,
        'posts': posts,
        'total_likes': total_likes,
        'total_comments': total_comments
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('blog:profile_view', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'blog/profile_edit.html', {'form': form})

@login_required
def post_like(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        post.dislikes.remove(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': post.total_likes(),
        'dislikes_count': post.total_dislikes()
    })

@login_required
def post_dislike(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
        disliked = False
    else:
        post.dislikes.add(request.user)
        post.likes.remove(request.user)
        disliked = True
    return JsonResponse({
        'disliked': disliked,
        'likes_count': post.total_likes(),
        'dislikes_count': post.total_dislikes()
    })

@login_required
def like_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('blog:post_detail', pk=pk)
