from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from authenticate.models import User
from discussions.models import Discussion, Post, Tag
from .serializers import DiscussionSerializer
import jwt,datetime

#add discussion
class AddDiscussion(APIView):
    def post(self,request):
            if 'jwt' not in request.headers:
                return Response({'error':'no token','status':'failure'})
            token=request.headers['jwt']
            try:
                payload=jwt.decode(token,'secret',algorithms=['HS256'])
            except:
                return Response({'error':'invalid token','status':'failure'})
            user=User.objects.filter(id=payload['id']).first()
            request.data['user']=user.id
            tags=request.data['tags']
            serializer=DiscussionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                discussion=serializer.instance
                for tag in tags:
                    temp = Tag(tagField = tag)
                    temp.save()
                    post = Post(discussion=discussion,tag=temp)
                    post.save()
                return Response({'status':'success','data':serializer.data})
            return Response({'status':'failure','error':serializer.errors})

# get discussions
class GetDiscussions(APIView):
    def get(self,request):
        discussions=Discussion.objects.all()
        serializer=DiscussionSerializer(discussions,many=True)
        return Response(serializer.data)
# update discussion
class UpdateDiscussion(APIView):
    def put(self,request):
        try:
            if 'jwt' not in request.headers:
                return Response({'error':'no token','status':'failure'})
            token=request.headers['jwt']
            try:
                payload=jwt.decode(token,'secret',algorithms=['HS256'])
            except:
                return Response({'error':'invalid token','status':'failure'})
            user=User.objects.filter(id=payload['id']).first()
            if user is None:
                return Response({'error':'user not found','status':'failure'})
            discussion=Discussion.objects.filter(id=request.headers['discussid']).first()
            
            if discussion is None:
                return Response({'error':'discussion not found','status':'failure'})
            if (discussion.user.id == user.id):
                discussion.discussionField=request.data['discussionField']
                tags=request.data['tags']
                posts=Post.objects.filter(discussion=discussion)
                posts.delete()
                for tag in tags:
                    temp = Tag(tagField = tag)
                    temp.save()
                    post = Post(discussion=discussion,tag=temp)
                    post.save()
                discussion.save()
                serializer=DiscussionSerializer(discussion)
                return Response({'status':'success','data':serializer.data})

            else:
                return Response({'error':'not authorized','status':'failure'})
        except:
            return Response({'error':'error updating discussion','status':'failure'})
# delete discussion
class DeleteDiscussion(APIView):
    def delete(self,request):
        if 'jwt' not in request.headers:
            return Response({'error':'no token','status':'failure'})
        token=request.headers['jwt']
        try:
            payload=jwt.decode(token,'secret',algorithms=['HS256'])
        except:
            return Response({'error':'invalid token','status':'failure'})
        user=User.objects.filter(id=payload['id']).first()

        if user is None:
            return Response({'error':'user not found','status':'failure'})

        discussion=Discussion.objects.filter(id=request.headers['discussid']).first()

        if discussion is None:
            return Response({'error':'discussion not found','status':'failure'})

        if (discussion.user.id == user.id):
            try:
                discussion.delete()
                return Response({'status':'success'})
            except:
                return Response({'error':'error deleting discussion','status':'failure'})
        else:
            return Response({'error':'not authorized','status':'failure'})


# get discussions by tag
class GetDiscussionsByTag(APIView):
    def get(self,request):
        try:
            if 'tag' not in request.query_params:
                return Response({'error':'tag is missing','status':'failure'})
            tag=request.query_params['tag']
            posts=Post.objects.filter(tag__tagField=tag)
            discussions=[]
            for post in posts:
                serializer=DiscussionSerializer(post.discussion)
                discussions.append(serializer.data)
                
            return Response({'status':'success','data':discussions})
        except:
            return Response({'error':'Some error occured','status':'failure'})

# get discussions between two certain dates
class GetDiscussionsByDate(APIView):
    def get(self,request):
        try:
            # startdate format: 2020-12-31
            # enddate format: 2020-12-31
            startdate=request.query_params['startdate']
            enddate=request.query_params['enddate']

            if 'startdate' not in request.query_params:
                return Response({'error':'startdate is missing','status':'failure'})
            if 'enddate' not in request.query_params:
                return Response({'error':'enddate is missing','status':'failure'})
            try:
                datetime.datetime.strptime(startdate, '%Y-%m-%d')
            except:
                return Response({'error':'start date format is wrong','status':'failure'})
            try:
                datetime.datetime.strptime(enddate, '%Y-%m-%d')
            except:
                return Response({'error':'end date format is wrong','status':'failure'})

            if startdate > enddate:
                return Response({'error':'startdate is greater than enddate','status':'failure'})
            
            discussions=Discussion.objects.filter(created_on__range=[startdate,enddate])
            serializer=DiscussionSerializer(discussions,many=True)
            return Response(serializer.data)
        except:
            return Response({'error':'Some error occured','status':'failure'})


# get discussions based on a text present in the discussion
class GetDiscussionsByText(APIView):
    def get(self,request):
        try:
            if 'text' not in request.query_params:
                return Response({'error':'text is missing','status':'failure'})
            
            text=request.query_params['text']
            discussions=Discussion.objects.filter(discussionField__icontains=text)
            serializer=DiscussionSerializer(discussions,many=True)
            return Response(serializer.data)
        except:
            return Response({'error':'Some error occured','status':'failure'})