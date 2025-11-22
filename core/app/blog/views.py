
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from .models import Post, Category,BlogStatusType
from taggit.models import Tag
# Create your views here.



class BlogListView(ListView):
    template_name = 'blog/blog.html'
    queryset = Post.objects.filter(status=True)  # This should be replaced with actual queryset logic
    paginate_by = 6
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        
        # Annotate تعداد پست‌های منتشر شده برای هر دسته
        context['categorys'] = Category.objects.annotate(
            post_count=Count('post', filter=Q(post__status=BlogStatusType.publish.value))
        )
        
        return context


class BlogDetailView(DetailView):
    template_name = 'blog/blog_detail.html'
      # This should be replaced with actual queryset logic
    
    def get_queryset(self):
        queryset = Post.objects.filter(status=True)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context