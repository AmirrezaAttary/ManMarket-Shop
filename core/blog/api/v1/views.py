from rest_framework.decorators import api_view
from rest_framework.response import Response
from blog.api.v1.serializers import PostSerializer
from blog.models import Post

data = {
    "id":1,
    "title" : "hello"
}


@api_view(['GET',"POST"])
def postList(requests):
    posts = Post.objects.filter(status=True)
    serializer = PostSerializer(posts,many=True)
    return Response(serializer.data)



@api_view(['GET',"PUT"])
def postDetail(requests,id):
    post = Post.objects.get(pk=id)
    serializer = PostSerializer(post)
    return Response(serializer.data)