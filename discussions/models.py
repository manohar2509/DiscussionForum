from django.db import models

from authenticate.models import User

# Create your models here.
class Discussion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discussionField = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

class Tag(models.Model):
    tagField = models.CharField(max_length=20)

class Post(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)