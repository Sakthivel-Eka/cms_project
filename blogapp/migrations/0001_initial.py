# Generated by Django 3.1.6 on 2021-02-04 05:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('sno', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('title', models.CharField(max_length=200)),
                ('blog_file', models.FileField(upload_to='blogfiles/')),
                ('date_of_upload', models.DateTimeField(auto_now_add=True)),
                ('slug', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_comment', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('approved', models.BooleanField(default=False)),
                ('blog_referred', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_referred', to='blogapp.blog')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_blog_comment', to='blogapp.profile')),
            ],
        ),
        migrations.AddField(
            model_name='blog',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_user_id', to='blogapp.profile'),
        ),
    ]
