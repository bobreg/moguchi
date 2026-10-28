import threading
import sys
import time
import os
import signal

from django.contrib import admin
from django.urls import path
from .views import m_moguchi_controller
from .views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index')
]

def stop_controller_poll(signum, frame):
    print("Server shutdown!")

    m_moguchi_controller.m_work = False

    if thread and thread.is_alive():
        thread.join(timeout=3)
    
    sys.exit(0)
    
signal.signal(signal.SIGINT, stop_controller_poll)   # Handles Ctrl+C
signal.signal(signal.SIGTERM, stop_controller_poll)  # Handles Linux systemctl stop

# 2. Fire the thread
thread = threading.Thread(target=m_moguchi_controller.work, daemon=True)
thread.start()