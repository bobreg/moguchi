from django.views import View
from django.shortcuts import render
from moguchi_control import Moguchi


class MoguchiServer(View):
    m_moguchi_controller = Moguchi()

    def index(request):

        contex = {
            't_temperature': MoguchiServer.m_moguchi_controller.get_temperature()
        }

        return render(request, 'index.html', contex)