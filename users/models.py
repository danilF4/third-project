from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from forum.models import Post, Subject
from django.utils.timezone import utc
from django.db import models
import datetime

#from django.db.models.signals import pre_save

class GradeUser(models.Model):
	grade = models.CharField(max_length=20, null=True, verbose_name="Grade")

	def __str__(self):
		return self.grade

class Country(models.Model):
	country = models.CharField(max_length=30, null=True)

	def __str__(self):
		return self.country

class UserManager(BaseUserManager):
	def create_user(self, email, username, password=None, is_staff=False, is_admin=False, is_active=False):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User msut have an password")
		user = self.model(
			email= self.normalize_email(email),
			username=username
			)
		user.staff  	= is_staff
		user.admin 		= is_admin
		user.active 	= is_active
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_staffuser(self, email, password=None):
		user = self.create_user(
			email,
			password=password,
			is_staff=True
			)
		return user

	def create_superuser(self, username, email, password=None):
		user = self.create_user(
			email,
			username,
			password=password,
			is_staff=True,
			is_admin=True,
			is_active=True
			)
		return user

Default = 'img/no_photo.png'

class MyUser(AbstractBaseUser):
	email 		= models.EmailField(max_length=255, unique=True)
	username 	= models.CharField(max_length=50, unique=True)
	active		= models.BooleanField(default=True)
	staff 		= models.BooleanField(default=False)
	admin 		= models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	objects = UserManager()

	def __str__(self):
		return self.email

	def get_short_name(self):
		return self.username

	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.staff

	@property
	def is_admin(self):
		return self.admin

	@property
	def is_active(self):
		return self.active


class UserProfile(models.Model):
	user			= models.OneToOneField(MyUser, on_delete=models.CASCADE)
	real_name 		= models.CharField(max_length=40, blank=True, null=True)
	grade 			= models.ForeignKey(GradeUser, on_delete=models.CASCADE,  blank=True, null=True)
	country 		= models.ForeignKey(Country, on_delete=models.CASCADE,  blank=True, null=True)
	about_me	 	= models.TextField(max_length=500,  blank=True, null=True)
	image 			= models.FileField(upload_to='users/image_storage', blank=True, null=True)
	reputation	 	= models.IntegerField(default=0)
	answers 		= models.IntegerField(default=0)
	questions	 	= models.IntegerField(default=0)
	sign_up_time	= models.DateTimeField(auto_now_add=True)
	profile_views	= models.ManyToManyField(MyUser, related_name='got_views', blank=True)
	fav_sub         = models.ForeignKey(Subject, on_delete=models.CASCADE, blank=True, null=True)
	liked_posts 	= models.ManyToManyField(Post, related_name='liked_posts', blank=True)

	def __str__(self):
		return str(self.user)

	def get_time_diff(self):
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		time_diff = now - self.sign_up_time
		days = time_diff.total_seconds()/(60*60*24)
		return days

def user_created_receiver(sender, instance, created, *args, **kwargs):
	if created and instance.email:
		UserProfile.objects.get_or_create(user=instance)

post_save.connect(user_created_receiver, sender=MyUser)
