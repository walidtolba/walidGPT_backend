from rest_framework.views import Response, APIView
from .models import Session, Message
from .serializers import SessionSerializer, MessageSerializer, RecordMessageSerializer
from users.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from users.custom_renderers import ImageRenderer
from django.http import HttpResponse
from rest_framework import generics
from .models import RecordMessage
from .tools import offline_chat
from openai import OpenAI

# add your key here
client = OpenAI(
  api_key=''
)


class SessionViews(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['patient'] = request.user.id
        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data)
        return Response({'error': "Can't add session", 'message': serializer.errors}, status=400)

    def get(self, request):
        print(request.user)
        sessions = Session.objects.filter(patient=request.user)
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

class DeleteSessionViews(APIView):
    def delete(self, request, id):
        instance = Session.objects.filter(id=id).first()
        if not instance:
            return Response({'error': 'there are no element with such id'})
        if (instance.patient.id == request.user.id):
            instance.delete()
            return Response({'id': id})
        else:
            return Response({'error': 'non authorized'})


class PatientSessionViews(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        sessions = Session.objects.filter(patient=id)
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

class CreateMessageViews(APIView):
    authentication_classes = [JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.data['sender'] = request.user.id
        serializer = MessageSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(): 
            serializer.save()
            if request.data.get('offline', False):
                answer = offline_chat(request.data['content'], request.data.get('arabic', False))
            else:
                try:
                    response = client.chat.completions.create(
                        messages=[
                                    {
                                        "role": "user",
                                        "content": request.data['content']
                                    }
                                ],
                        model="gpt-3.5-turbo",
                        temperature=0,
                        max_tokens=1024,
                        n=1,
                        stop=None
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = 'Sorry you Quota is limited'
            serializer2 = MessageSerializer(data={'session': request.data['session'],'content': answer})
            if serializer2.is_valid():
                serializer2.save()
            return Response({'sender': 'bot', 'content': answer})
        return Response({'sender': 'error', 'content': 'Error !!!'}, status=400)

class ListMessageViews(APIView):
    def get(self, request, id):
        sessions = Message.objects.filter(session=id)
        serializer = MessageSerializer(sessions, many=True)
        temp = serializer.data.copy()
        for message in temp:
            print(message)
            message['sender'] = 'patient' if message['sender'] else 'bot'
        return Response(temp)


class CreateRecordView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]
    
    def post(self, request):
        data = dict(request.data)
        data['session'] = data['session'][0]
        data['image'] = data['image'][0]
        data['sender'] = request.user.id
        print(data)
        serializer = RecordMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=200)
        print(serializer.errors)
        return Response(data=serializer.errors, status=500)

class RecordImageView(generics.RetrieveAPIView):
    renderers_classes = [ImageRenderer]
    def get(self, request, id):
        queryset = RecordMessage.objects.get(id=id).image
        data = queryset
        return HttpResponse(data, content_type='image/' + data.path.split(".")[-1])