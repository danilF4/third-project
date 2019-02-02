from django.contrib import admin
from .models import Post, GradePost, Subject, Comment

admin.site.register(Subject)
admin.site.register(GradePost)

class AdminCommentSchool(admin.ModelAdmin):
	list_display = ['content','content_type', 'user', 'right_answer', 'likes_', 'flags_']
	list_filter = ('timestamp', 'content', 'right_answer')
	search_fields = ('title', 'content')
	def likes_(self,instance):
		return instance.total_comment_likes()
	def flags_(self, instance):
		return instance.flags.all().count()
	ordering = ['-id']

admin.site.register(Comment, AdminCommentSchool)



class AdminPostSchool(admin.ModelAdmin):
	list_display = ['subject', 'title', 'grade', 'timestamp', 'user','count_of_likes' ,'viewed_times']
	list_filter = ('timestamp', 'updated', 'right_answer')
	search_fields = ('title', 'content')
	def count_of_likes(self,instance):
		return instance.total_likes()

	def viewed_times(self,instance):
		return instance.total_viewed()

	ordering = ['-id']

admin.site.register(Post, AdminPostSchool)
