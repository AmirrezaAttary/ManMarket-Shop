from django.shortcuts import render
from django.views.generic import ListView, DetailView
from blog.models import Post, Category
# Create your views here.

class BlogListView(ListView):
    template_name = 'blog/blog.html'
    queryset = Post.objects.filter(status=True)  # This should be replaced with actual queryset logic