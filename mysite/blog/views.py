from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Post

def post_list(request):
    post = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': post})

def post_detail(request, id):
    try:
        post = Post.published.get(id=id)
    except:
        raise Http404("No post found.")
    #inste of putting the try except block we can use a get_object_or_404(Post, id = id, status=Post.status.published)
    return render(request, 'blog/post/detail.html', {'post': post})


