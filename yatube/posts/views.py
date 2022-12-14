from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, PostForm
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .utils import pages_per_page

POST_PER_PAGE: int = 10


@cache_page(20 * 1, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = {
        'page_obj': pages_per_page(request, post_list, POST_PER_PAGE)
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group').all()
    context = {'group': group,
               'page_obj': pages_per_page(request, posts, POST_PER_PAGE)
               }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author').all()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'author': author,
        'page_obj': pages_per_page(request, posts, POST_PER_PAGE),
        'following': following
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments_all = Comment.objects.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments_all
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    cache.clear()
    is_edit = False
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form,
                  'is_edit': is_edit}
                  )


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', {'form': form,
                  'is_edit': is_edit, 'post_id': post.pk, 'post': post}
                  )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followings_posts = Post.objects.filter(
        author__following__user=request.user)
    context = {'page_obj': pages_per_page(
        request, followings_posts, POST_PER_PAGE)}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(
            user=request.user,
            author=author).exists() or request.user == author:
        return redirect('posts:follow_index')
    Follow.objects.create(
        user=request.user,
        author=get_object_or_404(User, username=username)
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user,
                                      author=author)
    if following.exists():
        following.delete()
    return redirect('posts:profile', username=username)
