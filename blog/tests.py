from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment
from django.utils import timezone

# Create your tests here.

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            slug='test-post',
            status='published'
        )

    def test_post_model_fields(self):
        """Test that Post model fields have correct labels and lengths"""
        self.assertEqual(self.post._meta.get_field('title').max_length, 200)
        self.assertEqual(self.post._meta.get_field('slug').max_length, 200)
        self.assertEqual(self.post._meta.get_field('status').max_length, 10)

    def test_post_str(self):
        """Test that Post model returns correct string representation"""
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_get_absolute_url(self):
        """Test that Post model returns correct URL"""
        expected_url = reverse('blog:blog_detail', kwargs={'slug': self.post.slug})
        self.assertEqual(self.post.get_absolute_url(), expected_url)

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            slug='test-post',
            status='published'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )

    def test_comment_str(self):
        """Test that Comment model returns correct string representation"""
        self.assertEqual(str(self.comment), 'Test comment')

    def test_comment_str_truncation(self):
        """Test that Comment model truncates long content in string representation"""
        long_comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a very long comment that should be truncated to 75 characters when displayed as a string representation'
        )
        self.assertEqual(str(long_comment), 'This is a very long comment that should be truncated to 75 characters...')

class BlogListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        # Create 6 published posts
        for i in range(6):
            Post.objects.create(
                title=f'Test Post {i}',
                content=f'Test content {i}',
                author=self.user,
                slug=f'test-post-{i}',
                status='published',
                created_date=timezone.now()
            )
        # Create 1 draft post
        Post.objects.create(
            title='Draft Post',
            content='Draft content',
            author=self.user,
            slug='draft-post',
            status='draft'
        )

    def test_blog_list_view_url(self):
        """Test that blog list view is accessible at the expected URL"""
        response = self.client.get('/blog/all/')
        self.assertEqual(response.status_code, 200)

    def test_blog_list_view_named_url(self):
        """Test that blog list view is accessible using the named URL"""
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(response.status_code, 200)

    def test_blog_list_view_template(self):
        """Test that blog list view uses the expected template"""
        response = self.client.get(reverse('blog:blog_list'))
        self.assertTemplateUsed(response, 'blog/blog_list.html')

    def test_blog_list_view_pagination(self):
        """Test that blog list view paginates records by 5"""
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(len(response.context['posts']), 5)

    def test_blog_list_view_only_published(self):
        """Test that blog list view only shows published posts"""
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(response.context['posts'].count(), 5)
        self.assertNotIn('Draft Post', [post.title for post in response.context['posts']])

    def test_blog_list_view_ordering(self):
        """Test that blog list view orders posts by date (newest first)"""
        response = self.client.get(reverse('blog:blog_list'))
        posts = response.context['posts']
        for i in range(len(posts) - 1):
            self.assertGreaterEqual(posts[i].created_date, posts[i + 1].created_date)

class BloggerListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test users
        self.user1 = User.objects.create_user(username='blogger1', password='testpass123')
        self.user2 = User.objects.create_user(username='blogger2', password='testpass123')
        # Create some posts for the first user to ensure they show up as a blogger
        Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user1,
            slug='test-post',
            status='published'
        )

    def test_blogger_list_view_url(self):
        """Test that blogger list view is accessible at the expected URL"""
        response = self.client.get('/blog/bloggers/')
        self.assertEqual(response.status_code, 200)

    def test_blogger_list_view_named_url(self):
        """Test that blogger list view is accessible using the named URL"""
        response = self.client.get(reverse('blog:blogger_list'))
        self.assertEqual(response.status_code, 200)

    def test_blogger_list_view_template(self):
        """Test that blogger list view uses the expected template"""
        response = self.client.get(reverse('blog:blogger_list'))
        self.assertTemplateUsed(response, 'blog/blogger_list.html')

    def test_blogger_list_view_content(self):
        """Test that blogger list view shows only users with posts"""
        response = self.client.get(reverse('blog:blogger_list'))
        self.assertContains(response, 'blogger1')  # User with posts should be listed
        self.assertNotContains(response, 'blogger2')  # User without posts should not be listed

class BlogDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            slug='test-post',
            status='published',
            created_date=timezone.now()
        )
        # Create comments with different timestamps
        self.comment1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='First comment',
            created_date=timezone.now() - timezone.timedelta(hours=2)
        )
        self.comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Second comment',
            created_date=timezone.now() - timezone.timedelta(hours=1)
        )

    def test_blog_detail_view_url(self):
        """Test that blog detail view is accessible at the expected URL"""
        response = self.client.get(f'/blog/blog/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_view_template(self):
        """Test that blog detail view uses the expected template"""
        response = self.client.get(reverse('blog:blog_detail', kwargs={'slug': self.post.slug}))
        self.assertTemplateUsed(response, 'blog/blog_detail.html')

    def test_blog_detail_view_content(self):
        """Test that blog detail view shows correct content"""
        response = self.client.get(reverse('blog:blog_detail', kwargs={'slug': self.post.slug}))
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertContains(response, self.post.author.username)
        self.assertContains(response, 'Post date')
        self.assertContains(response, 'Author:')
        self.assertContains(response, 'Description:')

    def test_blog_detail_view_comments_ordering(self):
        """Test that comments are ordered from oldest to newest"""
        response = self.client.get(reverse('blog:blog_detail', kwargs={'slug': self.post.slug}))
        comments = list(response.context['comments'])
        self.assertEqual(comments[0], self.comment1)  # First comment should be oldest
        self.assertEqual(comments[1], self.comment2)  # Second comment should be newer

    def test_blog_detail_view_login_state(self):
        """Test that appropriate comment link is shown based on login state"""
        # Test when user is not logged in
        response = self.client.get(reverse('blog:blog_detail', kwargs={'slug': self.post.slug}))
        self.assertContains(response, 'Login to add a new comment')
        self.assertNotContains(response, 'Add a new comment</a>')

        # Test when user is logged in
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:blog_detail', kwargs={'slug': self.post.slug}))
        self.assertContains(response, 'Add a new comment</a>')
        self.assertNotContains(response, 'Login to add a new comment')

class CommentFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            slug='test-post',
            status='published'
        )

    def test_comment_form_page(self):
        """Test that comment form page shows correct content"""
        # Login required to access form
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:add_comment', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Post your comment for:')
        self.assertContains(response, self.post.title)
        self.assertContains(response, 'Enter comment about blog here.')
        self.assertContains(response, 'Submit')

    def test_comment_form_redirect(self):
        """Test that successful comment submission redirects to blog post"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('blog:add_comment', kwargs={'slug': self.post.slug}),
            {'content': 'Test comment content'}
        )
        self.assertRedirects(response, reverse('blog:blog_detail', kwargs={'slug': self.post.slug}))

    def test_comment_form_login_required(self):
        """Test that comment form requires login"""
        response = self.client.get(reverse('blog:add_comment', kwargs={'slug': self.post.slug}))
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={reverse("blog:add_comment", kwargs={"slug": self.post.slug})}')

class BloggerDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='dr_evil', password='testpass123')
        # Create some posts
        for i in range(3):
            Post.objects.create(
                title=f'Test Post {i}',
                content=f'Test content {i}',
                author=self.user,
                slug=f'test-post-{i}',
                status='published',
                created_date=timezone.now() - timezone.timedelta(days=i)
            )

    def test_blogger_detail_view_url(self):
        """Test that blogger detail view is accessible at the expected URL"""
        response = self.client.get(f'/blog/blogger/{self.user.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_blogger_detail_view_template(self):
        """Test that blogger detail view uses the expected template"""
        response = self.client.get(reverse('blog:blogger_detail', kwargs={'pk': self.user.pk}))
        self.assertTemplateUsed(response, 'blog/blogger_detail.html')

    def test_blogger_detail_view_content(self):
        """Test that blogger detail view shows correct content"""
        response = self.client.get(reverse('blog:blogger_detail', kwargs={'pk': self.user.pk}))
        self.assertContains(response, f'Blogger: {self.user.username}')
        self.assertContains(response, 'Bio')
        self.assertContains(response, 'Blogs list')
        # Check all posts are listed
        for post in Post.objects.filter(author=self.user):
            self.assertContains(response, post.title)

    def test_blogger_detail_view_post_ordering(self):
        """Test that posts are ordered by date"""
        response = self.client.get(reverse('blog:blogger_detail', kwargs={'pk': self.user.pk}))
        posts = response.context['posts']
        for i in range(len(posts) - 1):
            self.assertGreaterEqual(posts[i].created_date, posts[i + 1].created_date)

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_profile_creation(self):
        """Test that profile is created automatically when user is created"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.bio, '')

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page(self):
        """Test that login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, '/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_failure(self):
        """Test failed login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Your username and password didn't match")

    def test_logout(self):
        """Test logout functionality"""
        # First login
        self.client.login(username='testuser', password='testpass123')
        # Then logout
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class RegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_page(self):
        """Test that registration page is accessible"""
        response = self.client.get(reverse('blog:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_registration_success(self):
        """Test successful registration"""
        response = self.client.post(reverse('blog:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_failure_password_mismatch(self):
        """Test registration failure due to password mismatch"""
        response = self.client.post(reverse('blog:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
        self.assertContains(response, "The two password fields didn't match")
