from django.shortcuts import render, redirect
from django.views import generic
from .forms import RegisterForm, LoginForm, ChangeProfile
from django.contrib.auth import authenticate, login, logout
from .models import MyUser, UserProfile, Country, GradeUser
from forum.models import Post, GradePost, Subject
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

def logout_view(request):
    logout(request)
    return redirect('/user/login/')

# Create your views here.
class RegisterView(generic.CreateView):
	form_class = RegisterForm
	template_name = 'register.html'
	success_url = '/user/login/'

	def grades(self):
		return GradePost.objects.all()

	def all_subjects(self):
		return Subject.objects.all()

def account_redirect(request):
	return redirect("/users/profile/{}".format(request.user.id))

class LoginView(generic.FormView):
	form_class = LoginForm
	success_url = '/users/login/'
	template_name = 'login.html'

	def grades(self):
		return GradePost.objects.all()

	def all_subjects(self):
		return Subject.objects.all()

	def form_valid(self, form):
		request =self.request
		email = form.cleaned_data.get("email")
		password = form.cleaned_data.get("password")
		user = authenticate(request, username=email, password=password)
		print(user)
		if user is not None:
			login(request, user)
			return redirect("/posts/")
		else:
			messages.error(request, 'Что-то пошло не так, перепроверьте почту и пароль')
			return redirect('/user/login/')


def edit_profile(request, username_):
	user 		 = MyUser.objects.filter(username=username_).first()
	instance	 = UserProfile.objects.filter(user=user).first()
	grades 		 = GradeUser.objects.exclude(grade=instance.grade)
	all_subjects = Subject.objects.exclude(subject=instance.fav_sub)
	countries    = Country.objects.exclude(country=instance.country)
	posts 		 = Post.objects.all()
	query 	     = request.GET.get('q')
	if request.user != user:
		response = HttpResponse("You are not allowed to do this")
		response.status_code = 403
		return response
	form 		 = ChangeProfile(initial={
								'real_name':instance.real_name,
								'grade':instance.grade,
								'fav_sub':instance.fav_sub,
								'country': instance.country,
								'about_me': instance.about_me,
								'image': instance.image}
								)
	if query:
		posts = posts.filter(
			Q(topic__icontains=query)|
			Q(text__icontains=query)
			).distinct()
	if request.method == "POST":
		form = ChangeProfile(request.POST or None, request.FILES or None, instance=instance)
		if form.is_valid():
			form_ = form.save(commit=False)
			instance.real_name = form_.real_name
			instance.grade = form_.grade
			instance.real_name = form_.real_name
			instance.about_me = form_.about_me
			instance.fav_sub = form_.fav_sub
			instance.image = form_.image
			instance.save()
	args = {'user_profile': instance, 'user':user, 'posts': posts, 'form': form, 'grades':grades, 'all_subjects': all_subjects, 'countries': countries}
	return render(request, 'edit_profile.html', args)

def profile(request, username_):
	user = MyUser.objects.filter(username=username_).first()
	user_profile = UserProfile.objects.filter(pk=user.pk).first()
	posts = Post.objects.all()
	query = request.GET.get('q')
	if query:
		posts = posts.filter(
			Q(topic__icontains=query)|
			Q(text__icontains=query)
			).distinct()
	args = {'user_profile': user_profile, 'user':user}
	return render(request, 'profile.html', args)

def liked_posts(request):
	args = {}
	return render(request, 'liked_posts.html', args)

def top_users(request):
	return render(request, 'skoro.html', {})

def about_us(request):
	return render(request, 'skoro.html', {})

def helping(request):
	return render(request, 'skoro.html', {})

def guide_to_site(request):
	return render(request, 'skoro.html', {})