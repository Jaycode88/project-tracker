# fetch_commits
from django.core.management.base import BaseCommand
from tracking.models import Project, Commit
import git
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Fetch commits for a specific project'

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int, help='ID of the project to fetch commits for')

    def handle(self, *args, **kwargs):
        project_id = kwargs['project_id']
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Project with id {project_id} does not exist'))
            return

        repo_path = f'/tmp/{project.name}'
        if not os.path.exists(repo_path):
            repo = git.Repo.clone_from(project.repository_url, to_path=repo_path)
        else:
            repo = git.Repo(repo_path)
            repo.remote().pull()

        last_commit_time = None
        first_commit_time = None
        for commit in reversed(list(repo.iter_commits())):
            commit_time = datetime.fromtimestamp(commit.committed_date)
            if not first_commit_time:
                first_commit_time = commit_time

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

        if not project.start_date and first_commit_time:
            project.start_date = first_commit_time.date()
            project.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully fetched commits for {project.name}'))
