from django.contrib import admin
from django.urls import path
from . import views as v
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token


app_name = "blogapp"

urlpatterns = [
    path('',v.home,name='homepage'),
    path('profiles/',v.AddListUserProfile.as_view(),name='profiles'),
    path('profile/<int:pk>/',v.EditDelProfile.as_view(),name='edit_del_profile'),
    path('login/',v.LoginView.as_view(),name='login_view'),
    path('refresh-token/',refresh_jwt_token),
    path('token-verify/',verify_jwt_token),
    path('blogs/',v.BlogView.as_view(),name='list_create_blogs'),
    path('blogpost/<str:slug>/',v.BlogDetailsView.as_view(),name='blog_details'),
    path('<int:pk>/blogs/',v.UserBlogs.as_view(),name='blogs_by_user'),
    path('blog/<str:slug>/comments/',v.BlogCommentsView.as_view(),name='blog_comments'),
    path('blog/<str:slug>/comments/<int:comment_id>/',v.CommentDetail.as_view(),name='comment'),
    path('comments/all/',v.AdminAllComments.as_view(),name='all_comments'),
]
