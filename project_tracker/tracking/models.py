from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    repository_url = models.URLField()
    start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Commit(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    commit_message = models.TextField()
    commit_hash = models.CharField(max_length=40)
    commit_time = models.DateTimeField()
    time_since_last_commit = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.project.name}: {self.commit_hash}"
