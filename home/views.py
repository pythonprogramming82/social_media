from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Post, Comment, Like
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PostCreatUpdateForm, CreatFormComment, CommentReolyForm, SearchForm
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

class HomeView(View):
    form_class = SearchForm

    def get(self, request):
        posts = Post.objects.all()
        if request.GET.get("search"):
            posts = posts.filter(body__contains=request.GET["search"])
        return render(request, 'home/home.html', {"posts":posts, "form":self.form_class})
    
class PostDetailView(View):
    from_class =CreatFormComment
    form_class_reply = CommentReolyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(id=kwargs['post_id'], slug=kwargs['slug_post'])
        return super().setup(request, *args, **kwargs)
    

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomment.filter(is_reply = False)
        can_like = False
        if request.user.is_authenticated and self.post_instance.user_can_like(request.user):
            can_like = True
        return render(request, "home/detail.html", {"post":self.post_instance, "comments":comments,
             "form":self.from_class, "reply_form":self.form_class_reply, "can_like":can_like})
    
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.from_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.post = self.post_instance
            new_post.save()
            messages.success(request, 'your comment is submit successfuly', 'success')
            return redirect("home:post_detail", self.post_instance.id, self.post_instance.slug) 


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id): 
        post = Post.objects.get(id=post_id)
        if post.user.id == request.user.id:
            post.delete()
            messages.success(request, "your post is delete successfuly", "success")
        else:
            messages.error(request, "you can not delete the post", "error")
        return redirect("home:home")
    

class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreatUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(id=kwargs["post_id"])
        return super().setup(request, *args, **kwargs)
    

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(request, "you can not update this form", "error")
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    
    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, "home/update.html", {"form":form})


    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data["body"][:30])
            new_post.save()
            messages.success(request, "you post is update successfuly", "success")
            return redirect("home:post_detail", post.id, post.slug)
    

class PostCreatView(LoginRequiredMixin, View):
    form_class = PostCreatUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, "home/creat.html", {"form":form})
    

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data["body"][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, "you creat a new post", "success")
            return redirect("home:post_detail", new_post.id, new_post.slug)
        

class PostReplyView(LoginRequiredMixin, View):
    form_class = CommentReolyForm

    def post(self, request, post_id, comment_id):
        post = Post.objects.get(id=post_id)
        comment = Comment.objects.get(id=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request, "your reply submit successfuly", "success")
        return redirect("home:post_detail", post.id, post.slug)
    


class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        like = Like.objects.filter(post=post, user=request.user)
        if like.exists():
            messages.error(request, 'you have alredy like this post', 'error')
        else:
            Like.objects.create(post=post, user=request.user)
            messages.success(request, "you like this post successfuly", "success")
        return redirect("home:post_detail", post.id, post.slug)