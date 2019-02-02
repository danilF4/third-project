from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import UserProfile, MyUser

class LoginForm(forms.Form):
	email    = forms.EmailField(label='Почта')
	password = forms.CharField(label='Пароль',widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
	password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
	email = forms.EmailField(label='Почта')
	username = forms.CharField(label='Никнейм')

	class Meta:
		model = MyUser
		fields = ('email', 'username')

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		user = super(RegisterForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.email = self.cleaned_data['email']
		user.username = self.cleaned_data['username']
		if commit:
			user.save()
		return user

class UserAdminCreationForm(forms.ModelForm):
	password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

	class Meta:
		model = MyUser
		fields = ('email', 'username')

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords don't match")
		return password2

	def save(self, commit=True):
		user = super(UserAdminCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.active = False
		if commit:
			user.save()
		return user

class UserAdminChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = MyUser
		fields = ('email', 'username', 'password', 'active', 'admin')

	def clean_password(self):
		return self.initial["password"]

class ChangeProfile(forms.ModelForm):
	real_name = forms.CharField(required=False, label='Настоящее имя')
	#grade = forms.ChoiceField(choices=c, label='Класс')
	about_me = forms.CharField(widget=forms.Textarea, required=False, label='Обо мне')
	class Meta:
		model = UserProfile
		fields = ['real_name', 'grade', 'country', 'fav_sub', 'about_me', 'image']
		labels = {"grade":"Класс", "country":"Страна", 'fav_sub':"Любимый Предмет"}
