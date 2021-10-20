from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Post, User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['topic', 'name', 'description']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'email', 'bio']