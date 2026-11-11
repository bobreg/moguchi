import threading
import sys
import time
import os
import signal

from django.contrib import admin
from django.urls import path
from .views import m_moguchi_controller
from .views import index
from django.conf import settings
from django.conf.urls.static import static
from .views import get_boiler_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('get-boiler-data/', get_boiler_data, name='get_boiler_data'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT or (settings.BASE_DIR / "static"))

def stop_controller_poll(signum, frame):
    print("Server shutdown!")

    m_moguchi_controller.m_work = False

    if thread and thread.is_alive():
        thread.join(timeout=3)
    
    sys.exit(0)

if 'runserver' in sys.argv:
    signal.signal(signal.SIGINT, stop_controller_poll)   # Handles Ctrl+C
    signal.signal(signal.SIGTERM, stop_controller_poll)  # Handles Linux systemctl stop

# 2. Fire the thread
thread = threading.Thread(target=m_moguchi_controller.work, daemon=True)
thread.start()