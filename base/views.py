from typing import ContextManager
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from .models import Message, Post, Topic, User
from .forms import PostForm, UserForm, MyUserCreationForm


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        if '@' in username:
            email = username
            username = None
        password = request.POST.get('password')

        try:
            if username != None:
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
            return redirect('login')

        username = user.username
        user = authenticate(request, username=username, password=password)
 
        if user != None:
            login(request, user)
            messages.success(request, f'Logged in as {username}')
            return redirect('home')
        else:
            messages.error(request, 'Username or password are wrong')

    context = {
        'page': page
    }

    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    messages.success(request, f'Logged out')

    return redirect('home')

def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)

            messages.success(request, 'Successfully created user')
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    context = {
        'page': page,
        'form': form
    }

    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') 
    if q == None: q = ''

    posts = Post.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
    )
    topics = Topic.objects.all()[:5]
    post_count = posts.count()
    
    if not request.user.is_anonymous:
        saved_posts = request.user.saved.all()
        saved_posts_ids = [post.id for post in saved_posts]
        posts_messages = Message.objects.filter(
            Q(post__topic__name__icontains=q) |
            Q(post__host__username__icontains=request.user.username) |
            Q(post__id__in=saved_posts_ids)
        )[:7]
    else:
        posts_messages = []

    context = {
        'posts': posts,
        'topics': topics,
        'post_count': post_count,
        'posts_messages': posts_messages,
    }

    return render(request, 'base/home.html', context)
    
def post(request, id):
    post = Post.objects.get(id=id)
    post_messages = post.message_set.all()
    participants = post.participants.all()

    # new message handling
    if request.method == "POST":
        Message.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body'),
        )
        participants_list = post.participants.all()
        if request.user not in participants_list:
            post.participants.add(request.user)

        return redirect('post', id=post.id)

    context = {
        'post': post,
        'post_messages': post_messages,
        'participants': participants,
    }

    return render(request, 'base/post.html', context)

@login_required(login_url='login')
def createPost(request):
    form = PostForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)

        post = Post.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        
        post.save()
        post.participants.add(request.user)
        return redirect('post', id = post.id)

    context = {
        'form': form,
        'topics': topics,
    }
    
    return render(request, 'base/post_form.html', context)

@login_required(login_url='login')
def updatePost(request, id):
    post = Post.objects.get(id=id)
    form = PostForm(instance=post)
    topics = Topic.objects.all()

    if request.user != post.host:
        return HttpResponse('Not enough permissions')

    if request.method == 'POST':
        request_POST = request.POST.copy()
        topic_name = request_POST.get('topic')
        topic, _ = Topic.objects.get_or_create(name=topic_name)
        request_POST['topic'] = topic

        form = PostForm(request_POST, instance=post)
        if form.is_valid():
            model_instance = form.save()
            return redirect('post', id=model_instance.id)
        else:
            messages.error(request, 'An error occurred')
            return redirect('post', id=post.id)

    context = {
        'form': form,
        'topics': topics,
        'post': post,
    }
    
    return render(request, 'base/post_form.html', context)

@login_required(login_url='login')
def deletePost(request, id):
    post = Post.objects.get(id=id)
    
    if request.user != post.host:
        return HttpResponse('Not enough permissions')
    
    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': post})

@login_required(login_url='login')
def deleteMessage(request, id):
    message = Message.objects.get(id=id)
    
    if request.user != message.user:
        return HttpResponse('Not enough permissions')
    
    if request.method == 'POST':
        post = message.post
        message.delete()
        return redirect('post', id=post.id)

    return render(request, 'base/delete.html', {'obj': message})

def userProfile(request, id):
    user = User.objects.get(id=id)
    posts = user.post_set.all()
    post_count = Post.objects.all().count
    posts_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        'user': user,
        'posts': posts,
        'post_count': post_count,
        'posts_messages': posts_messages,
        'topics': topics,
    }

    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', id=user.id)
            
    context = {'form': form}

    return render(request, 'base/update_user.html', context)

@login_required(login_url='login')
def savePost(request, id):
    post = Post.objects.get(id=id)
    user = request.user

    # increment saves
    user.saved.add(post)
    post.saves_counter += 1

    # add to participants list
    participants_list = post.participants.all()
    if request.user not in participants_list:
        post.participants.add(request.user)
    
    post.save()
    user.save()

    return redirect('post', id=post.id)

@login_required(login_url='login')
def unsavePost(request, id):
    post = Post.objects.get(id=id)
    user = request.user

    # increment saves
    user.saved.remove(post)
    post.saves_counter -= 1

    # remove from participants list if no messages
    if not Message.objects.filter(user=user, post=post).exists():
        post.participants.remove(request.user)

    post.save()
    user.save()

    return redirect('post', id=post.id)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    post_count = Post.objects.all().count

    context = {
        'topics': topics,
        'post_count': post_count,
    }

    return render(request, 'base/topics.html', context)