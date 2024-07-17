from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Commit
from collections import defaultdict
from django.utils.timezone import localtime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.views.decorators.http import require_POST

def project_list(request):
    projects = Project.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        repository_url = request.POST.get('repository_url')
        if name and repository_url:
            Project.objects.create(name=name, repository_url=repository_url)
            return redirect('project_list')
    return render(request, 'tracking/project_list.html', {'projects': projects})

def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    commits = Commit.objects.filter(project=project).order_by('commit_time')

    grouped_commits = defaultdict(list)
    daily_work_times = {}
    total_estimated_hours = 0
    
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
        total_estimated_hours += times['daily_hours']

    context = {
        'project': project,
        'grouped_commits': sorted(grouped_commits.items()),
        'daily_work_times': daily_work_times,
        'total_estimated_hours': total_estimated_hours
    }
    return render(request, 'tracking/project_detail.html', context)

@csrf_exempt
@require_POST
def fetch_commits(request, project_id):
    try:
        call_command('fetch_commits', str(project_id))  # Ensure project_id is passed as string
        return JsonResponse({'status': 'success', 'message': f'Fetched commits for project {project_id}'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
