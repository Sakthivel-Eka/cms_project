from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Blog,Profile,Comment
from drf_writable_nested import WritableNestedModelSerializer
from datetime import datetime

class UserSerializer(WritableNestedModelSerializer):

    class Meta:
        model = User
        write_only_fields = ('email','password','first_name','last_name')
        fields = ('email','first_name','last_name','username','password','is_superuser','is_staff')
        extra_kwargs = {'password':{'write_only': True}}


class ProfileSerializer(WritableNestedModelSerializer):

    user = UserSerializer()

    def get_serializer(self,*args,**kwargs):
        kwargs['partial'] = True
        return super(ProfileSerializer, self).get_serializer(*args, **kwargs)
    
    def create(self,validated_data):
        user_data = validated_data.pop('user',None)
        if user_data:
            password = user_data.pop('password')
            user = User.objects.get_or_create(**user_data)[0]
            user.set_password(password)
            user.save()
            validated_data['user']=user
        profile = Profile.objects.create(**validated_data)
        return profile

    def update(self, instance, validated_data):
        instance.user = validated_data.get('username',instance.user.username)
        print(instance.user)
        # instance.username = validated_data.get('username',instance.username)
        # instance.save()
        return instance

    class Meta:
        model = Profile
        write_only_fields = ('password',)
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):

    created_by = ProfileSerializer
    # read_only_fields = ('blogid')
    slug = serializers.CharField(required=False)
    date_of_upload = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = '__all__'
    
    def get_date_of_upload(self,obj):
        return str(obj.date_of_upload.strftime("%d-%m-%Y %H:%M:%S"))

    def get_comments(self,obj):
        print("SSSSSSSSSSS",obj.blog_referred.filter(approved=True))
        request = self.context.get('request', None)
        if request:
            print("Request object::::",request)
            if request.user.is_superuser==True:
                print("SUPER USER!")
                comments = CommentSerializer(obj.blog_referred.all(),many=True)
        else:
            comments = CommentSerializer(obj.blog_referred.filter(approved=True),many=True)

        print(comments)
        return comments.data


class CommentSerializer(serializers.ModelSerializer):

    created_by = ProfileSerializer
    blog_referred = BlogSerializer
    approved = serializers.BooleanField(required=False)
    date_of_comment = serializers.SerializerMethodField()
    blog_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_date_of_comment(self,obj):
        return str(obj.date_of_comment.strftime("%d-%m-%Y %H:%M:%S"))

    def get_blog_url(self,obj):
        return "/blogpost/"+str(obj.blog_referred.slug)+"/"
