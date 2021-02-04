from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()


class Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="profile_user_id")
    content = models.TextField()
    title = models.CharField(max_length=200)
    blog_file = models.FileField(upload_to="blogfiles/")
    date_of_upload = models.DateTimeField(auto_now_add=True)
    slug = models.CharField(max_length=200,unique=True)

    def __str__(self):
        return str(self.slug)


class Comment(models.Model):
    created_by = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="user_blog_comment")
    blog_referred = models.ForeignKey(Blog,on_delete=models.CASCADE,related_name="blog_referred")
    date_of_comment = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return str(self.comment)[0:15]+"..."

