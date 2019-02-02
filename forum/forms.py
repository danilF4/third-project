from django import forms
from .models import Post

class CreatePost(forms.ModelForm):
	class Meta:
		model = Post
		fields = ('title', 'subject', 'grade', 'content')
		labels = {'subject':'Предмет', 'title':'Заголовок', 'grade':'Класс', 'content':'Текст'}

class CommentForm(forms.Form):
	content_type = forms.CharField(widget=forms.HiddenInput)
	object_id = forms.IntegerField(widget=forms.HiddenInput)
	content = forms.CharField(label='', widget=forms.Textarea)

class PostChangeForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['subject', 'title', 'grade', 'content']
		labels = {'subject':'Предмет', 'title':'Заголовок', 'grade':'Класс', 'content':'Текст'}
