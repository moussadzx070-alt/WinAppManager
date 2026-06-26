import psutil
import os

def check_app_status(install_location):
    if not install_location or not os.path.exists(install_location):
        return {"active": False, "ram": 0, "pids": []}

    active = False
    total_ram = 0
    pids = []
    
    install_location = os.path.normpath(install_location).lower()

    for proc in psutil.process_iter(['pid', 'exe', 'memory_info']):
        try:
            exe_path = proc.info.get('exe')
            if exe_path and os.path.normpath(exe_path).lower().startswith(install_location):
                active = True
                total_ram += proc.info['memory_info'].rss
                pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # تحويل الرام من بايت إلى ميغابايت
    ram_mb = total_ram / (1024 * 1024)
    return {"active": active, "ram": ram_mb, "pids": pids}

def kill_processes(pids):
    for pid in pids:
        try:
            p = psutil.Process(pid)
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
