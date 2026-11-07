from django.views import View
from django.shortcuts import render
from moguchi_control import Moguchi
from django.http import JsonResponse

m_moguchi_controller = Moguchi()

def index(request):
    return render(request, 'index.html', m_moguchi_controller.get_data())

def get_boiler_data(request):
    return JsonResponse(m_moguchi_controller.get_data())