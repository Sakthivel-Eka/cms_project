from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Blog,Comment,Profile
from .serializers import BlogSerializer,ProfileSerializer,CommentSerializer
from rest_framework import status,authentication
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import update_last_login, User
from django.utils.decorators import method_decorator
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER





class LoginView(ObtainJSONWebToken):
    """
        Application Login Class
    """
    try:
        def post(self, request, *args, **kwargs):
            response = super(LoginView, self).post(request, *args, **kwargs)
            res = response.data
            token = res.get('token')
            password = request.data.get('password')
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
            except Exception as e:
                print("Loginview --Exception while fetching user:",str(e))
                return Response({'Status': False,
                                'StatusMessage': 'User not found.Please enter registered e-mail id.',
                                'StatusCode': 404},
                                status=status.HTTP_404_NOT_FOUND)
            
            if not user.is_active:
                return Response({'Status': False,
                                'StatusMessage': 'User is inactive. Please contact admin',
                                'StatusCode': 404},
                                status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):
                return Response({'Status': False,
                                'StatusMessage': 'Incorrect password.Please enter the correct password.',
                                'StatusCode': 403},
                                status=status.HTTP_403_FORBIDDEN)

            payload = jwt_payload_handler(user)
            first_name = user.first_name
            last_name = user.last_name
            profile_id = user.profile.id
            token = jwt_encode_handler(payload)
            update_last_login(None, user)
            return Response({'Status': True,
                            'StatusCode':200,
                            'StatusMessage': 'Successfully logged in',
                            'first_name' : first_name,
                            'last_name' : last_name,
                            'token': token,
                            'profile_id':profile_id},
                        status=status.HTTP_200_OK)

    except Exception as e:
        print("Exception occured at LoginView: ",str(e))



class AddListUserProfile(APIView):
    """
    API to create a User Profile. POST method, with 'user' key and dict object as value. 
    dict obj - 'username','first_name','last_name','password','email','is_superuser','is_staff'
    all fields set required.
    """
    def get(self,request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)


    def post(self,request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class EditDelProfile(APIView):

    def put(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        user = profile.user
        pro_user = request.data['user']
        print("pro_user:",pro_user)
        print()
        try:
            try:
                usern = pro_user['username']
            except Exception as e:
                usern = user.username
            try:
                firstn = pro_user['first_name']
            except Exception as e:
                firstn = user.first_name
            try:
                lastn = pro_user['last_name']
            except Exception as e:
                lastn = user.last_name
            try:
                issuper = pro_user['is_superuser']
            except Exception as e:
                issuper = user.is_superuser
            try:
                isstaff = pro_user['is_staff']
            except Exception as e:
                isstaff = user.is_staff
            try:
                email = pro_user['email']
            except Exception as e:
                email = user.email

            User.objects.filter(username=user.username).update(username=usern,email=email,first_name=firstn,last_name=lastn,is_superuser=issuper,is_staff=isstaff)
            profile = get_object_or_404(Profile,pk=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Exception as e:
            print("Exception while updating Profile::",str(e))

    def delete(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        user = profile.user
        profile.delete()
        user.is_active=False
        user.save()

        return Response({"StatusMessage":"Profile Deleted Successfully."},status=status.HTTP_204_NO_CONTENT)



class BlogView(APIView):
    """
    API to list all the blogs saved in the application and to create a new blog.
    """
    def get(self,request):
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        request.data['slug'] = slugify(request.data['title'])
        serializers = BlogSerializer(data=request.data)
        try:
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status = status.HTTP_201_CREATED)
        except IntegrityError:
            print("Please submit a new Blog. Blog already exists with this TITLE.")
            return Response({"StatusMessage":"Please submit a new Blog. Blog already exists with this TITLE."},status = status.HTTP_400_BAD_REQUEST)
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)


def home(request):
    return HttpResponse("This is the site's homepage!")


class UserBlogs(APIView):
    """
    Lists all the blogs made by the particular user(pk is the user-id).
    """
    permission_classes = (IsAuthenticated,)
    def get(self,request,pk):
        blogs = Blog.objects.filter(created_by=pk)
        serializer = BlogSerializer(blogs, many=True, context={'request':request})
        return Response(serializer.data)


class BlogDetailsView(APIView):

    """
    API to provide particular Blog Details
    """

    def get(self, request, slug):
        blog_ins = get_object_or_404(Blog, slug=slug)
        serializer = BlogSerializer(blog_ins)
        print(serializer.data)
        return Response(serializer.data)
    
    def put(self, request, slug):
        blog_put = get_object_or_404(Blog, slug=slug)
        serializers = BlogSerializer(blog_put,data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        if request.user.is_superuser or request.user == blog.created_by.user:
            blog.delete()
            return Response({"StatusMessage":"Blog Deleted Successfully."},status=status.HTTP_204_NO_CONTENT)
        return Response({"StatusMessage":"Cannot delete other's blogs"},status=status.HTTP_400_BAD_REQUEST)


class BlogCommentsView(APIView):
    
    """
    API to list all the blogs saved in the application and to create a new blog.
    """
    def get(self,request,slug):
        blog = Blog.objects.get(slug=slug)
        comments = Comment.objects.filter(blog_referred=blog.sno).order_by('date_of_comment')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self,request,slug):
        serializers = CommentSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status = status.HTTP_201_CREATED)
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)



class CommentDetail(APIView):
    """
    API to show, edit single Comment of Blog Post with comment_id only for admins and comment creator(cannot approve,unless admin)
    """
    def get(self,request,slug,comment_id):
        comment = get_object_or_404(Comment,pk=comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
 
    def put(self,request,slug,comment_id):
        comment = get_object_or_404(Comment,pk=comment_id,blog_referred__slug=slug)
        if request.user.is_superuser or request.user == comment.created_by.user:
            try:
                if request.data['approved']==True and not request.user.is_superuser:
                    return Response({"StatusMessage":"Only admins can approve comments."})
            except Exception as e:
                request.data["approved"] = comment.approved
                print("Exception occured while editing comment: ",e)
            serializer = CommentSerializer(comment,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"StatusMessage":"Only admins/comment maker can edit comments."})



class AdminAllComments(APIView):
    def get(self,request):
        comments = Comment.objects.all()
        if request.user.is_superuser:
            serializer = CommentSerializer(comments,many=True)
            return Response(serializer.data)
        else:
            return Response({"StatusMessage":"Not Authorized to view all comments"},status=status.HTTP_400_BAD_REQUEST)


