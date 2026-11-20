import threading
import sys
import time
import os
import signal
import atexit

from django.contrib import admin
from django.urls import path
from .views import m_moguchi_controller
from .views import index
from django.conf import settings
from django.conf.urls.static import static
from .views import get_boiler_data, set_target_temp, set_home_heating, set_water_temp, set_flow_temp

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('get-boiler-data/', get_boiler_data, name='get_boiler_data'),
    path('set-target-temp/', set_target_temp, name='set_target_temp'),
    path('set-home-heating/', set_home_heating, name='set_home_heating'),
    path('set-water-temp/', set_water_temp, name='set_water_temp'),
    path('set-flow-temp/', set_flow_temp, name='set_flow_temp'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT or (settings.BASE_DIR / "static"))

def stop_controller_poll():
    print("Server shutdown!")
    m_moguchi_controller.m_work = False
    if thread and thread.is_alive():
        thread.join(timeout=3)
    
    sys.exit(0)

atexit.register(stop_controller_poll)

# 2. Fire the thread
thread = threading.Thread(target=m_moguchi_controller.work, daemon=True)
thread.start()