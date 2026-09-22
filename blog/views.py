from django.shortcuts import get_object_or_404, render

from .models import Blog


def list(request):
    posts = Blog.objects.all()
    return render(request, "blog/list.html", {"posts": posts})


def detail(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    return render(request, "blog/detail.html", {"post": post})
