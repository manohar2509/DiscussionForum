from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from authenticate.models import User
from discussions.models import Discussion, Post, Tag
from .serializers import DiscussionSerializer
import jwt,datetime

# Create your views here.
class AddDiscussion(APIView):
    def post(self,request):
            # if no token is sent, return error
            if 'jwt' not in request.headers:
                return Response({'error':'no token','status':'failure'})
            token=request.headers['jwt']
            try:
                payload=jwt.decode(token,'secret',algorithms=['HS256'])
            except:
                return Response({'error':'invalid token','status':'failure'})
            user=User.objects.filter(id=payload['id']).first()
            request.data['user']=user.id
            # get list of tags from request and send it to serializer
            tags=request.data['tags']
            # here tags is a list of tags sent in request send this list to serializer
            serializer=DiscussionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # get discussion object from serializer
                discussion=serializer.instance
                # create post object for each tag
                for tag in tags:
                    temp = Tag(tagField = tag)
                    temp.save()
                    post = Post(discussion=discussion,tag=temp)
                    post.save()
                return Response({'status':'success','data':serializer.data})
            return Response({'status':'failure','error':serializer.errors})


class GetDiscussions(APIView):
    def get(self,request):
        discussions=Discussion.objects.all()
        serializer=DiscussionSerializer(discussions,many=True)
        return Response(serializer.data)

class UpdateDiscussion(APIView):
    def put(self,request):
        try:
            # if no token is sent, return error
            if 'jwt' not in request.headers:
                return Response({'error':'no token','status':'failure'})
            token=request.headers['jwt']
            try:
                payload=jwt.decode(token,'secret',algorithms=['HS256'])
            except:
                return Response({'error':'invalid token','status':'failure'})
            user=User.objects.filter(id=payload['id']).first()
            # if user is not found, return error
            if user is None:
                return Response({'error':'user not found','status':'failure'})
            discussion=Discussion.objects.filter(id=request.headers['discussid']).first()
            # if discussion is not found, return error
            if discussion is None:
                return Response({'error':'discussion not found','status':'failure'})
            if (discussion.user.id == user.id):
                discussion.discussionField=request.data['discussionField']
                tags=request.data['tags']
                # delete all posts for this discussion
                posts=Post.objects.filter(discussion=discussion)
                posts.delete()
                # create post object for each tag
                for tag in tags:
                    temp = Tag(tagField = tag)
                    temp.save()
                    post = Post(discussion=discussion,tag=temp)
                    post.save()
                discussion.save()
                # return updated discussion
                serializer=DiscussionSerializer(discussion)
                return Response({'status':'success','data':serializer.data})

            else:
                return Response({'error':'not authorized','status':'failure'})
        except:
            return Response({'error':'error updating discussion','status':'failure'})

class DeleteDiscussion(APIView):
    def delete(self,request):
        # if no token is sent, return error
        if 'jwt' not in request.headers:
            return Response({'error':'no token','status':'failure'})
        token=request.headers['jwt']
        try:
            payload=jwt.decode(token,'secret',algorithms=['HS256'])
        except:
            return Response({'error':'invalid token','status':'failure'})
        user=User.objects.filter(id=payload['id']).first()

        # if user is not found, return error
        if user is None:
            return Response({'error':'user not found','status':'failure'})

        discussion=Discussion.objects.filter(id=request.headers['discussid']).first()

        # if discussion is not found, return error
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


# get discussions by tag using django filters
class GetDiscussionsByTag(APIView):
    def get(self,request):
        try:
            # if tag is not sent, return error
            if 'tag' not in request.query_params:
                return Response({'error':'tag is missing','status':'failure'})
            tag=request.query_params['tag']
            # get all posts with this tag
            posts=Post.objects.filter(tag__tagField=tag)
            # get all discussions from these posts
            discussions=[]
            for post in posts:
                # send each discussion to serializer
                serializer=DiscussionSerializer(post.discussion)
                discussions.append(serializer.data)
                
            return Response({'status':'success','data':discussions})
        except:
            return Response({'error':'Some error occured','status':'failure'})

# get discussions based on a filter between two certain dates
class GetDiscussionsByDate(APIView):
    def get(self,request):
        try:
            # startdate format: 2020-12-31
            # enddate format: 2020-12-31
            startdate=request.query_params['startdate']
            enddate=request.query_params['enddate']

            #if startdate is not sent, return error
            if 'startdate' not in request.query_params:
                return Response({'error':'startdate is missing','status':'failure'})

            #if enddate is not sent, return error
            if 'enddate' not in request.query_params:
                return Response({'error':'enddate is missing','status':'failure'})

            #if date format is not correct, return error
            try:
                datetime.datetime.strptime(startdate, '%Y-%m-%d')
            except:
                return Response({'error':'start date format is wrong','status':'failure'})
            try:
                datetime.datetime.strptime(enddate, '%Y-%m-%d')
            except:
                return Response({'error':'end date format is wrong','status':'failure'})

            # if startdate is greater than enddate, return error
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
        # keep it in try catch block
        try:
            # if text is not sent, return error
            if 'text' not in request.query_params:
                return Response({'error':'text is missing','status':'failure'})
            
            text=request.query_params['text']
            discussions=Discussion.objects.filter(discussionField__icontains=text)
            serializer=DiscussionSerializer(discussions,many=True)
            return Response(serializer.data)
        except:
            return Response({'error':'Some error occured','status':'failure'})