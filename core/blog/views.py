from django.shortcuts import render
from django.views.generic import ListView, DetailView
from blog.models import Post, Category
from django.db.models import Count
# Create your views here.

class BlogListView(ListView):
    template_name = 'blog/blog.html'
    queryset = Post.objects.filter(status=True)  # This should be replaced with actual queryset logic
    

class BlogDetailView(DetailView):
    template_name = 'blog/blog_detail.html'
      # This should be replaced with actual queryset logic
    
    def get_queryset(self):
        queryset = Post.objects.filter(status=True)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context