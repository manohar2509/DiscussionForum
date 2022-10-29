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
    # get tags
    def get_tags(self, obj):
        posts = Post.objects.filter(discussion=obj)
        tags = [post.tag for post in posts]
        result=[]
        for tag in tags:
            serializer = TagSerializer(tag)
            result.append(serializer.data)
        return result