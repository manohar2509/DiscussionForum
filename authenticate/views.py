from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from authenticate.models import User
from .serializers import UserSerializer
import jwt,datetime

class RegisterView(APIView):
    def post(self,request):
        try:
            serializer= UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        except:
            return Response({'error':'error occured','status':'failure'})
class LoginView(APIView):
    def post(self,request):
        try:
            username=request.data['username']
            password=request.data['password']

            user=User.objects.filter(username=username).first()
            if user is None:
                return Response({'error':'User not found','status':'failure'})
            if not user.check_password(password):
                return Response({'error':'Wrong password','status':'failure'})

            payload={
                'id':user.id,
                # keep token valid for 1 day and refresh if a user logs in again
                'exp':datetime.datetime.utcnow()+datetime.timedelta(days=2),
                'iat':datetime.datetime.utcnow()
            }
            token=jwt.encode(payload,'secret',algorithm='HS256')
            response = Response()
            response.set_cookie(key='jwt',value=token,httponly=True)
            response.data={
                'jwt':token,
                'status':'success'
            }
            return response
        except:
            return Response({'error':'Something went wrong','status':'failure'})
class UserProfileView(APIView):
    def get(self,request):
        try:
            if 'jwt' not in request.headers:
                return Response({'error':'no token','status':'failure'})
            token=request.headers['jwt']
            try:
                payload=jwt.decode(token,'secret',algorithms=['HS256'])
            except:
                return Response({'error':'invalid token','status':'failure'})
            user=User.objects.filter(id=payload['id']).first()
            serializer=UserSerializer(user)
            return Response(serializer.data)
        except:
            return Response({'error':'Something went wrong','status':'failure'})

class LogoutView(APIView):
    def post(self,request):
        response=Response()
        try:
            response.delete_cookie('jwt')
            response.data={
                'message':'success'
            }
        except:
            response.data={
                'message':'failed'
            }
        return response
