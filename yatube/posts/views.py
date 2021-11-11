from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import PAGINATOR_SETINGS

from .forms import PostForm, CommentForm
from .models import Comment, Group, Post, User, Follow


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR_SETINGS['PAGE_SIZE'])
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    post_list = author.posts.all()
    is_following = Follow.objects.filter(author=author).exists()
    following = False
    if author != request.user and is_following:
        following = True
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.filter(post=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comment,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(
        request,
        template,
        {'form': form}
    )


@login_required
def post_edit(request, post_id):
    template = 'posts/create.html'
    edited_post = get_object_or_404(Post, pk=post_id)
    if edited_post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edited_post)
    if request.method == 'POST':
        if form.is_valid():
            edited_post = form.save()
            return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    is_following = Follow.objects.filter(author=author).exists()
    if author != request.user and not is_following:
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_following = Follow.objects.filter(author=author).exists()
    if author != request.user and is_following:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
