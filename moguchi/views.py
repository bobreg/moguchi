from django.views import View
from django.shortcuts import render
from moguchi_control import Moguchi

m_moguchi_controller = Moguchi()

def index(request):
    return render(request, 'index.html', m_moguchi_controller.get_data())