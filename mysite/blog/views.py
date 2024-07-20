from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.views.generic import ListView

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html' #this replace (1)
    
"""this is (1)
def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        post = paginator.page(page_number)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        post = paginator.page(1)
        
    return render(request, 'blog/post/list.html', {'posts': post})"""

def post_detail(request, year, month,day, post):
    try:
        post_ = Post.published.get(
            status=Post.Status.PUBLISHED,
            slug=post,
            publish__year=year,
            publish__month=month,
            publish__day=day
        )
    except:
        raise Http404("No post found.")
    #inste of putting the try except block we can use a get_object_or_404(Post, id = id, status=Post.status.published)
    return render(request, 'blog/post/detail.html', {'post': post_})


