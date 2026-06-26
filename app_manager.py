import winreg
import subprocess

def get_installed_apps():
    apps = []
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path)
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    
                    try:
                        uninstall_cmd = winreg.QueryValueEx(subkey, "UninstallString")[0]
                    except OSError:
                        uninstall_cmd = None
                        
                    try:
                        install_loc = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                    except OSError:
                        install_loc = ""
                        
                    try:
                        # الحجم يكون بالـ كيلوبايت في السجل
                        size_kb = winreg.QueryValueEx(subkey, "EstimatedSize")[0]
                        size_mb = size_kb / 1024
                    except OSError:
                        size_mb = 0.0

                    if name and uninstall_cmd:
                        apps.append({
                            "name": name,
                            "uninstall_cmd": uninstall_cmd,
                            "install_location": install_loc,
                            "size_mb": size_mb
                        })
                except OSError:
                    continue
        except OSError:
            continue
            
    # إزالة التكرارات بناءً على الاسم
    unique_apps = {app['name']: app for app in apps}.values()
    return sorted(list(unique_apps), key=lambda x: x['name'].lower())

def uninstall_app(uninstall_cmd):
    try:
        # تنفيذ أمر الإزالة 
        subprocess.Popen(uninstall_cmd, shell=True)
    except Exception as e:
        print(f"Error uninstalling: {e}")
