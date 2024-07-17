from django.shortcuts import render, get_object_or_404
from .models import Project, Commit
from collections import defaultdict
from django.utils.timezone import localtime

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'tracking/project_list.html', {'projects': projects})

def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    commits = Commit.objects.filter(project=project).order_by('commit_time')

    grouped_commits = defaultdict(list)
    daily_work_times = {}
    
    for commit in commits:
        commit_date = localtime(commit.commit_time).date()
        grouped_commits[commit_date].append(commit)
        if commit_date not in daily_work_times:
            daily_work_times[commit_date] = {
                'first_commit': commit.commit_time,
                'last_commit': commit.commit_time,
                'daily_hours': 0
            }
        else:
            if commit.commit_time < daily_work_times[commit_date]['first_commit']:
                daily_work_times[commit_date]['first_commit'] = commit.commit_time
            if commit.commit_time > daily_work_times[commit_date]['last_commit']:
                daily_work_times[commit_date]['last_commit'] = commit.commit_time

    for date, times in daily_work_times.items():
        times['daily_hours'] = (times['last_commit'] - times['first_commit']).total_seconds() / 3600

    context = {
        'project': project,
        'grouped_commits': sorted(grouped_commits.items()),
        'daily_work_times': daily_work_times
    }
    return render(request, 'tracking/project_detail.html', context)
