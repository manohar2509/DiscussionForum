from rest_framework import serializers

from .models import Discussion, Tag, Post



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tag
        fields='__all__'

class PostSerializer(serializers.ModelSerializer):
    tag = TagSerializer(many=True)
    class Meta:
        model = Post
        fields = '__all__'
class DiscussionSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    class Meta:
        model=Discussion
        fields='__all__'
        # get tags from many to many field
    def get_tags(self, obj):
        # get all posts for this discussion
        posts = Post.objects.filter(discussion=obj)
        # get all tags for these posts. Each post contains one tag and one discussion
        tags = [post.tag for post in posts]
        # serialize each tag and return
        result=[]
        for tag in tags:
            serializer = TagSerializer(tag)
            result.append(serializer.data)
        return result