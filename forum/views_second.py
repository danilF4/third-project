from django.shortcuts import get_object_or_404, redirect
# User Model and Profile Model
from users.models import UserProfile, MyUser
from .models import Comment, Post
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

def make_right(request, pk, pk_comment):
	instance = get_object_or_404(Post, pk=pk)
	comment = get_object_or_404(Comment, pk=pk_comment)
	user =  comment.user.userprofile
	#related_comments = instance.comments
	comm_with_ans = Comment.objects.filter(object_id=instance.id, right_answer=True).first()
	if instance.right_answer == False:
		instance.right_answer = True
		comment.right_answer = True
		instance.save()
		comment.save()
		if not comment.user == instance.user:
			user.reputation += 15
			user.save()
			return redirect('/post/{}/{}/'.format(instance.pk, instance.slug))
		if comment.user == instance.user:
			#Nothing
			return redirect('/post/{}/{}/'.format(instance.pk, instance.slug))
	if instance.right_answer == True:
		if comment == comm_with_ans:
			comment.right_answer = False
			instance.right_answer = False
			instance.save()
			comment.save()
			if comment.user == instance.user:
				return redirect('/post/{}/{}/'.format(instance.pk, instance.slug))
			else:
				user = comm_with_ans.user.userprofile
				user.reputation -= 15
				user.save()
		if comment != comm_with_ans:
			comm_with_ans.right_answer = False
			comm_with_ans.save()
			comment.right_answer = True
			comment.save()
			if instance.user == comm_with_ans.user:
				user = comment.user.userprofile
				user.reputation += 0
				user.save()
			if not instance.user == comm_with_ans.user:
				user_right = comm_with_ans.user.userprofile
				user_right.reputation -= 15
				user_right.save()
			if instance.user == comment.user:
				return redirect('/post/{}/{}/'.format(instance.pk, instance.slug))
			if not instance.user == comment.user:
				user = comment.user.userprofile
				user.reputation += 15
				user.save()
	return redirect('/post/{}/{}/'.format(instance.pk, instance.slug))



@login_required()
def post_flag(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if not request.user in post.flags.all():
		post.flags.add(request.user)
		post.save()
		return redirect("/post/{}/{}".format(post.pk, post.slug))
	else:
		post.flags.remove(request.user)
		post.save()
		return redirect("/post/{}/{}".format(post.pk, post.slug))
	return redirect("/post/{}/{}".format(post.pk, post.slug))

def comment_flag(request, pk):
	comment = get_object_or_404(Comment, pk=pk)
	post = get_object_or_404(Post, pk=comment.object_id)
	if not request.user in comment.flags.all():
		comment.flags.add(request.user)
	else:
		comment.flags.remove(request.user)
	return redirect("/post/{}/{}".format(post.pk, post.slug))




def like_post_redirect(request, pk, slug, user_pk):
	post 	= Post.objects.filter(pk=pk, slug=slug).first()
	user 	= MyUser.objects.filter(pk=user_pk).first()
	user_profile = UserProfile.objects.filter(user=user).first()
	if post.likes.filter(id=request.user.id).exists():
		post.likes.remove(request.user)
		user_profile.liked_posts.remove(post)
	else:
		post.likes.add(request.user)
		user_profile.liked_posts.add(post)
	return redirect('/post/{}/{}/'.format(post.id, post.slug))

def like_comment(request, pk):
	comment = Comment.objects.filter(pk=pk).first()
	post 	= get_object_or_404(Post, pk=comment.object_id)
	user_p  = UserProfile.objects.filter(user=comment.user).first()
	if request.user in comment.likes.all():
		comment.likes.remove(request.user)
		user_p.reputation += 15
		user_p.save()
	else:
		comment.likes.add(request.user)
		user_p.reputation -= 15
		user_p.save()
	return HttpResponseRedirect(post.get_absolute_url())



def delete_post(request, pk):
	post = Post.objects.filter(pk=pk).first()
	post.delete()
	return redirect('/posts/')

def delete_comment(request, pk):
	comment = get_object_or_404(Comment, pk=pk)
	comment.delete()
	post = get_object_or_404(Post, pk=comment.object_id)
	post.answers -= 1
	post.save()
	return redirect('/post/{}/{}'.format(post.pk, post.slug))

