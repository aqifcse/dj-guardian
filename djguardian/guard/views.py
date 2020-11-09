from django.shortcuts import render
from django.template import RequestContext
from guard.models import Task, Post
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_objects_for_user

def user_dashboard(request, template_name='dashboard.html'):
    guard = get_objects_for_user(request.user, 'projects.view_project')
    return render(request, template_name, {'guard': guard},
        RequestContext(request))


