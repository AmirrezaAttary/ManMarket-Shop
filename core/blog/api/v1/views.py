from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def postList(requests):
    return Response({"message":"blog api v1 post list"})