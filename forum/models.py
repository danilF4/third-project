from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
#from django.utils.text import slugify
from django.urls import reverse
MyUser = settings.AUTH_USER_MODEL
#import datetime
#from django.utils.timesince import timesince
from django.utils import timezone
#from django.http import HttpResponseRedirect

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class GradePost(models.Model):
	grade 			= models.CharField(max_length=20, verbose_name="Gra")
	slug 			= models.SlugField(max_length=20)
	grade_img   	= models.ImageField(upload_to='forum/grade_img')

	class Meta:
		ordering = ['id']

	def __str__(self):
		return self.grade

class Subject(models.Model):
	subject 		= models.CharField(max_length=40)
	slug 			= models.SlugField(unique=True)
	sub_img 	 	= models.ImageField(upload_to='forum/sub_img_dir')

	def __str__(self):
		return self.subject

def upload_location(instance, filename):
    PostModel = instance.__class__
    new_id = PostModel.objects.order_by("id").last().id + 1
    """
    instance.__class__ gets the model Post. We must use this method because the model is defined below.
    Then create a queryset ordered by the "id"s of each object,
    Then we get the last object in the queryset with `.last()`
    Which will give us the most recently created Model instance
    We add 1 to it, so we get what should be the same id as the the post we are creating.
    """
    return "%s/%s" %(new_id, filename)

class PostQuerySet(models.query.QuerySet):
    def not_draft(self):
        return self.filter(draft=False)

    def published(self):
        return self.filter(publish__lte=timezone.now()).not_draft()

class PostManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return PostQuerySet(self.model, using=self._db)

    def active(self, *args, **kwargs):
        # Post.objects.all() = super(PostManager, self).all()
        return self.get_queryset().published()

class Post(models.Model):
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
	title 			= models.CharField(max_length=100)
	slug 			= models.SlugField(unique=True, allow_unicode=True, max_length=100)
	content 		= models.TextField()
	right_answer	= models.BooleanField(default=False)
	updated 		= models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True)
	subject 		= models.ForeignKey(Subject, on_delete=models.CASCADE)
	grade 			= models.ForeignKey(GradePost, on_delete=models.CASCADE)
	viewed 			= models.ManyToManyField(MyUser,related_name='post_viewed', blank=True)
	answers		 	= models.IntegerField(default=0)
	flags 			= models.ManyToManyField(MyUser, related_name='users_flags', blank=True)
	likes 			= models.ManyToManyField(MyUser, related_name="%(app_label)s_%(class)s_likes", blank=True)

	#publish 		= models.DateField(auto_now=False, auto_now_add=False)
	#draft 			= models.BooleanField(default=False)

	#image = models.ImageField(upload_to=upload_location, null=True, blank=True, width_field="width_field", height_field="height_field")
	#height_field	= models.IntegerField(default=0)
	#width_field 	= models.IntegerField(default=0)

	objects = PostManager()

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("forum:detail", kwargs={'pk':self.pk, 'slug':self.slug})

	def total_likes(self):
	    return self.likes.count()

	def total_viewed(self):
	    return self.viewed.count()

	def get_update_post(self):
	    return "/edit/{}/post".format(self.pk)

	def get_delete_post(self):
	    return "/post-pk/{}/delete/".format(self.pk)

	@property
	def comments(self):
		instance = self
		qs = Comment.objects.filter_by_instance(instance).order_by("id")
		return qs

	@property
	def get_content_type(self):
	    instance = self
	    content_type = ContentType.objects.get_for_model(instance.__class__)
	    return content_type

def international_slugify(str):
    str = str.replace(" ", "-")
    str = str.replace(",", "-")
    str = str.replace("(", "-")
    str = str.replace(")", "")
    str = str.replace("؟", "")
    str = str.replace("'", "")
    str = str.replace("№", "number")
    str = str.replace("?", "")
    str = str.replace(".", "")

    return str

def create_slug(instance, new_slug=None):
	slug_a = international_slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = Post.objects.filter(slug=slug_a).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug_a, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	return slug_a

def post_save_signal_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)


pre_save.connect(post_save_signal_receiver, sender=Post)




class CommentManager(models.Manager):
	def all(self):
		qs = super(CommentManager, self).filter(parent=None)
		return qs

	def filter_by_instance(self, instance):
		content_type = ContentType.objects.get_for_model(instance.__class__) # instance.__class__ = any existing model
		obj_id = instance.id
		qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent=None)
		return qs

class Comment(models.Model):
	content_type	= models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id 		= models.PositiveIntegerField()
	content_object 	= GenericForeignKey('content_type', 'object_id')
	parent 			= models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
	user 			= models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)

	content 		= models.TextField()
	timestamp 		= models.DateTimeField(auto_now_add=True)

	right_answer 	= models.BooleanField(default=False)
	likes 			= models.ManyToManyField(MyUser, related_name='comment_likes', blank=True)
	flags 			= models.ManyToManyField(MyUser, related_name='post_likes', blank=True)

	objects = CommentManager()

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		return self.content

	def children(self):
		return Comment.objects.filter(parent=self)

	@property
	def is_parent(self):
		if self.parent is not None:
			return False
		return True

	def total_comment_likes(self):
		return self.likes.count()