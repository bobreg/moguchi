import threading
import sys
import time
import os
import signal

from django.contrib import admin
from django.urls import path
from .views import MoguchiServer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MoguchiServer.index, name='index')
]

def stop_controller_poll(signum, frame):
    print("Server shutdown!")

    MoguchiServer.m_moguchi_controller.m_work = False

    time.sleep(2) 
    
    sys.exit(0)

if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('DJANGO_SETTINGS_MODULE'):    
    signal.signal(signal.SIGINT, stop_controller_poll)   # Handles Ctrl+C
    signal.signal(signal.SIGTERM, stop_controller_poll)  # Handles Linux systemctl stop

    # 2. Fire the thread
    thread = threading.Thread(target=MoguchiServer.m_moguchi_controller.work, daemon=True)
    thread.start()