from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
#from django.contrib.auth.decorators import login_required

from .models import Post, Subject, GradePost, Comment  # models
from django.core.paginator import Paginator # Paginator
from .forms import CreatePost, CommentForm, PostChangeForm # Forms
from django.db.models import Q

from datetime import datetime, timedelta
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType
from django.contrib import messages


def create_post(request):
	form 		 = CreatePost()
	grades  	 = GradePost.objects.all()
	all_subjects = Subject.objects.all()
	posts        = Post.objects.all()
	query 	     = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(text__icontains=query)
			).distinct()
	if request.method == "POST":
		form = CreatePost(request.POST)
		if not request.user.is_authenticated:
		    messages.error(request, "Войдите как авторизованный пользователь")
		    return redirect("/create/")
		if form.is_valid() and request.user.is_authenticated:
			instance = form.save(commit=False)
			instance.user = request.user
			instance.timestamp = timezone.now()
			instance.save()
			return HttpResponseRedirect(instance.get_absolute_url())
	args = {'form':form, 'grades': grades, 'all_subjects': all_subjects}
	return render(request, 'create_post.html', args)



# EDIT POST
def post_update(request, pk):
	instance    = Post.objects.get(pk=pk)
	posts       = Post.objects.all()
	query 	        = request.GET.get('q')
	if request.user != instance.user:
		return redirect("/user/login/")
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	form = PostChangeForm(initial={ 'subject':instance.subject,
									'title'	 :instance.title,
									'grade'	 :instance.grade,
									'content':instance.content})
	if request.method == "POST":
		form = PostChangeForm(request.POST)
		if form.is_valid():
			form_ = form.save(commit=False)
			instance.title 		= form_.title
			instance.subject 	= form_.subject
			instance.grade 		= form_.grade
			instance.content 	= form_.content
			instance.save()
			return HttpResponseRedirect(instance.get_absolute_url())
	args = {'instance': instance, 'form': form}
	return render(request, 'edit_post.html', args)

#MAIN VIEWS#
def detail2(request, pk, slug):
	instance 		= Post.objects.filter(pk=pk).first()
	grades          = GradePost.objects.all()
	comments 		= instance.comments
	all_subjects 	= Subject.objects.all()
	posts 		  = Post.objects.all() # posts
	query 	      = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	if request.user.is_authenticated:
		if not request.user in instance.viewed.all():
			instance.viewed.add(request.user)
	initial_data = {
		"content_type": instance.get_content_type,
		"object_id": instance.id
	}
	form = CommentForm(request.POST or None, initial=initial_data)
	if form.is_valid() and request.user.is_authenticated:
		c_type = form.cleaned_data.get("content_type")
		content_type = ContentType.objects.get(model=c_type)
		obj_id = form.cleaned_data.get("object_id")
		content_data = form.cleaned_data.get("content")
		parent_id = request.POST.get("parent_id")
		instance.answers += 1
		instance.save()
		parent_obj = None
		try:
			parent_id = int(request.POST.get("parent_id"))
		except:
			parent_id = None
		if parent_id:
			parent_qs = Comment.objects.filter(id=parent_id)
			if parent_qs.exists():
				parent_obj = parent_qs.first()

		new_comment, created = Comment.objects.get_or_create(
			user = request.user,
			content_type = content_type,
			object_id = obj_id,
			content = content_data,
			parent = parent_obj
			)
		return HttpResponseRedirect(instance.get_absolute_url())
	args = {'post':instance,
	        'all_subjects':all_subjects,
	        'comments':comments,
	        'form':form,
	        'grades': grades,
	        }
	return render(request, 'detail_file.html', args)


def comment_edit(request, pk):
	posts = Post.objects.all()
	instance = Comment.objects.get(pk=pk)
	post = Post.objects.filter(pk=instance.object_id).first()
	query 	        = request.GET.get('q')
	if request.user != instance.user:
		return redirect("/user/login/")
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(text__icontains=query)
			).distinct()
		return render(request, 'posts.html', {'posts':posts})
	form = CommentForm(initial={'content_type':instance.content_type,
								'object_id'	 :instance.object_id,
								'content':instance.content})
	if request.method == "POST":
		form = CommentForm(request.POST)
		if form.is_valid():
			form.save()
	args = {"posts":posts, 'instance':instance, 'form':form, "post":post}
	return render(request, 'edit_comment.html', args)


def las_posts(request):
	grades 	  	  = GradePost.objects.all()
	posts 		  = Post.objects.all() # posts
	query 	      = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	all_subjects  = Subject.objects.all() # all subjects
	paginator     = Paginator(posts, 4 ) # PAGINATOR
	page          = request.GET.get('page') # PAGINATOR
	posts         = paginator.get_page(page) # PAGINATOR
	args          = {'posts':posts,'all_subjects':all_subjects, 'grades': grades}
	return render(request, 'posts.html', args)


def grade(request, slug):
	grade 	 	 = GradePost.objects.filter(slug=slug).first()#chosen subject
	title 		 = grade
	all_subjects = Subject.objects.all()#all subjects
	posts 		 = Post.objects.filter(grade=grade).order_by('-timestamp')# posts of subject
	query 	     = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	grades 	     = GradePost.objects.all()
	paginator    = Paginator(posts, 5 ) # PAGINATOR
	page         = request.GET.get('page') # PAGINATOR
	posts        = paginator.get_page(page) # PAGINATOR
	args 	 	 = {'subject':subject, 'all_subjects':all_subjects, 'posts':posts, 'grades':grades, 'title':title}
	return render(request, 'posts.html', args)


def subject(request, slug):
	subject 	 = Subject.objects.filter(slug=slug).first()#chosen subject
	title 		 = subject
	all_subjects = Subject.objects.all()#all subjects
	posts 		 = Post.objects.filter(subject=subject).order_by('-timestamp')# posts of subject
	query 	     = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	grades 	     = GradePost.objects.all()
	paginator    = Paginator(posts, 5 ) # PAGINATOR
	page         = request.GET.get('page') # PAGINATOR
	posts        = paginator.get_page(page) # PAGINATOR
	args 	 	 = {'subject':subject, 'all_subjects':all_subjects, 'posts':posts, 'grades':grades, 'title':title}
	return render(request, 'posts.html', args)


def hot_posts(request):
	all_subjects	= Subject.objects.all()
	title 			= "Hottest Posts"
	grades 			= GradePost.objects.all()
	one_week_ago 	= datetime.today() - timedelta(days=30) # time not later than 1 week
	posts 			= Post.objects.filter(timestamp__gte=one_week_ago).order_by('-viewed')
	query 	        = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	paginator    	= Paginator(posts, 5 ) # PAGINATOR
	page         	= request.GET.get('page') # PAGINATOR
	posts        	= paginator.get_page(page) # PAGINATOR
	args 			= {'all_subjects': all_subjects, 'grades': grades, 'posts':posts, 'title':title}
	return render(request, 'posts.html', args)


def unanswered(request):
	all_subjects	= Subject.objects.all()
	title			= "Ananswered Posts"
	grades 			= GradePost.objects.all()
	three_days_ago 	= datetime.today() - timedelta(days=3) # time not later than 3 days
	posts 			= Post.objects.filter(timestamp__gte=three_days_ago, right_answer=False)
	query 	        = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	paginator    	= Paginator(posts, 5 ) # PAGINATOR
	page         	= request.GET.get('page') # PAGINATOR
	posts        	= paginator.get_page(page) # PAGINATOR
	query 	        = request.GET.get('q')
	args		 	= {'all_subjects': all_subjects, 'grades': grades, 'posts':posts, 'title':title}
	return render(request, 'posts.html', args)


def most_liked(request):
	all_subjects	= Subject.objects.all().order_by()
	title 			= "The Most Popular Posts"
	grades 			= GradePost.objects.all()
	posts 			= Post.objects.all().order_by('-likes', '-timestamp')
	query 	      = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(title__icontains=query)|
			Q(content__icontains=query)
			).distinct()
	paginator 		= Paginator(posts, 5)
	page 			= request.GET.get('page')
	posts 			= paginator.get_page(page)
	args 			= {'all_subjects': all_subjects, 'grades': grades, 'posts':posts, 'title':title}
	return render(request, 'posts.html', args)


def guidebook(request):
	args = {}
	return render(request, 'guidebook.html', args)
