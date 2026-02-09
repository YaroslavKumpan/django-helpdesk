from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PingView(APIView):
    def get(self, request):
        return Response({"ok": True}, status=status.HTTP_200_OK)
