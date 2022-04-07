from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect

from .forms import CommentForm, PostForm
from .models import Follow, Post, Group, User


def get_page_obj(request, post_list):
    return Paginator(
        post_list,
        settings.POSTS_ON_PAGE).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_page_obj(request, Post.objects.all())
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page_obj(request, group.posts.all())
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    context = {
        'page_obj': get_page_obj(request, author.posts.all()),
        'author': author
    }
    if request.user.is_authenticated and username != request.user.username:
        following = Follow.objects.filter(
            author=author, user=request.user
        ).exists()
        context['following'] = following
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    return render(request, 'posts/post_detail.html', {
        'post': get_object_or_404(Post, id=post_id),
        'form': CommentForm(request.POST or None)
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(
            request, 'posts/create_post.html', {'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True,
        'post': post
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts:post_detail', {
        'form': form,
        'post': post
    })


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': get_page_obj(
            request,
            Post.objects.filter(author__following__user=request.user)
        )
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    redirect_page = redirect('posts:profile', username)
    if author == user:
        return redirect_page
    try:
        Follow.objects.create(user=user, author=author)
    except IntegrityError:
        return redirect_page
    return redirect_page


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username
    ).delete()
    return redirect('posts:profile', username)
