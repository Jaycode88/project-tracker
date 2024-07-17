from django.core.management.base import BaseCommand
from tracking.models import Project, Commit
import git
from datetime import datetime
import os
from django.utils.timezone import make_aware, get_current_timezone

class Command(BaseCommand):
    help = 'Fetch commits from all projects'

    def handle(self, *args, **kwargs):
        projects = Project.objects.all()
        for project in projects:
            repo_path = f'/tmp/{project.name}'
            if not os.path.exists(repo_path):
                repo = git.Repo.clone_from(project.repository_url, to_path=repo_path)
            else:
                repo = git.Repo(repo_path)
                repo.remote().pull()

            last_commit_time = None
            for commit in reversed(list(repo.iter_commits())):
                commit_time = datetime.fromtimestamp(commit.committed_date)
                commit_time = make_aware(commit_time, get_current_timezone())
                time_since_last_commit = None
                if last_commit_time:
                    time_since_last_commit = commit_time - last_commit_time
                last_commit_time = commit_time

                Commit.objects.update_or_create(
                    project=project,
                    commit_hash=commit.hexsha,
                    defaults={
                        'commit_message': commit.message,
                        'commit_time': commit_time,
                        'time_since_last_commit': time_since_last_commit
                    }
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched commits for {project.name}'))
