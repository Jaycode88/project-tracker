from django.contrib import admin
from .models import Project, Commit

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'repository_url')

class CommitAdmin(admin.ModelAdmin):
    list_display = ('project', 'commit_hash', 'commit_message', 'commit_time')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Commit, CommitAdmin)
