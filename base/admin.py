from django.contrib import admin
from .models import Post, Topic, Message, User

admin.site.register(Post)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(User)