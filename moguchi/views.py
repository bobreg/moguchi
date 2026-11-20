from django.views import View
from django.shortcuts import render
from moguchi_control import Moguchi
from django.http import JsonResponse
import json

m_moguchi_controller = Moguchi()

def index(request):
    return render(request, 'index.html', m_moguchi_controller.get_data())


def get_boiler_data(request):
    return JsonResponse(m_moguchi_controller.get_data())


def set_target_temp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_temp = int(data.get('target_temp'))
            if m_moguchi_controller.set_target_temperature(new_temp):
                return JsonResponse({'status': 'ok', 'target_temp': new_temp})
            else:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def set_water_temp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_temp = int(data.get('water_temp'))
            if m_moguchi_controller.set_water_temp(new_temp):
                return JsonResponse({'status': 'ok', 'water_temp': new_temp})
            return JsonResponse({'status': 'error', 'message': 'Modbus write failed'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def set_flow_temp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_temp = float(data.get('flow_temp'))
            if m_moguchi_controller.set_flow_temp(new_temp):
                return JsonResponse({'status': 'ok', 'flow_temp': new_temp})
            return JsonResponse({'status': 'error', 'message': 'Modbus write failed'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



def set_home_heating(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            flag = bool(data.get('heat_house'))
            m_moguchi_controller.set_home_heating(flag)
            return JsonResponse({'status': 'ok', 'heat_house': flag})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        