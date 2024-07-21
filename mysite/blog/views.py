from django.contrib.postgres.search import SearchVector
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.views.generic import ListView
from . forms import EmailPostForm
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm, SearchForm
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count

#class PostListView(ListView):
#    queryset = Post.published.all()
#    context_object_name = 'posts'
#    paginate_by = 3
#    template_name = 'blog/post/list.html' #this replace (1)
    
#this is (1) the explanation is in the book in the page 36
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag=None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tag__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        post = paginator.page(page_number)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        post = paginator.page(1)     
    return render(request, 'blog/post/list.html', {'posts': post, 'tag': tag})

def post_detail(request, year, month,day, post):
    """
     post = get_object_or_404(Post,
                            status=Post.Status.PUBLISHED,
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day=day
                            )
    """
    try:
        post = Post.published.get(
            status=Post.Status.PUBLISHED,
            slug=post,
            publish__year=year,
            publish__month=month,
            publish__day=day
        )
    except:
        raise Http404("No post found.")
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tag.values_list('id', flat=True)
    similar_post = Post.published.filter(tag__in=post_tags_ids)\
                                 .exclude(id=post.id)
    similar_post = similar_post.annotate(same_tags=Count('tag'))\
                            .order_by('-same_tags', '-publish')[:4]
    #inste of putting the try except block we can use a get_object_or_404(Post, id = id, status=Post.status.published)
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_post': similar_post})


def post_share(request, post_id):
# Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
    # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'ingenierocivil.jmm@outlook.com',[cd['to'],'jesusmanuelv1989@gmail.com'])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,'form': form,'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
       form = SearchForm()
       query = None
       results = []
       if 'query' in request.GET:
           form = SearchForm(request.GET)
           if form.is_valid():
               query = form.cleaned_data['query']
               results = Post.published.annotate(
                   search=SearchVector('title', 'body'),
               ).filter(search=query)
       return render(request,'blog/post/search.html',{'form': form,'query': query,'results': results})
