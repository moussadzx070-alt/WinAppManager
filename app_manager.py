import winreg
import subprocess
import os
import shutil
import time

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
                        display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                        display_icon = display_icon.split(',')[0].strip('"')
                    except OSError:
                        display_icon = ""
                        
                    try:
                        size_kb = winreg.QueryValueEx(subkey, "EstimatedSize")[0]
                        size_mb = size_kb / 1024
                    except OSError:
                        size_mb = 0.0

                    if name and uninstall_cmd:
                        apps.append({
                            "name": name,
                            "uninstall_cmd": uninstall_cmd,
                            "install_location": install_loc,
                            "display_icon": display_icon,
                            "size_mb": size_mb
                        })
                except OSError:
                    continue
        except OSError:
            continue
            
    unique_apps = {app['name']: app for app in apps}.values()
    return sorted(list(unique_apps), key=lambda x: x['name'].lower())

def uninstall_and_deep_clean(app_data):
    # 1. تنفيذ أمر الإزالة العادي أولاً
    try:
        process = subprocess.Popen(app_data['uninstall_cmd'], shell=True)
        # ننتظر قليلاً ليعمل ملف الإزالة
        time.sleep(3) 
    except Exception as e:
        print(f"Error executing uninstaller: {e}")

    app_name = app_data['name']
    install_loc = app_data['install_location']

    # 2. تنظيف مسار التثبيت بقوة (إذا كان آمناً ومحدداً)
    if install_loc and os.path.exists(install_loc):
        if len(install_loc) > 10 and app_name.split()[0].lower() in install_loc.lower():
            try:
                shutil.rmtree(install_loc, ignore_errors=True)
            except:
                pass

    # 3. تنظيف الداتا من AppData
    appdata_paths = [os.environ.get('APPDATA'), os.environ.get('LOCALAPPDATA')]
    for path in appdata_paths:
        if path:
            target_folder = os.path.join(path, app_name.split()[0])
            if os.path.exists(target_folder) and len(app_name) > 2:
                try:
                    shutil.rmtree(target_folder, ignore_errors=True)
                except:
                    pass

    # 4. تنظيف اختصارات سطح المكتب
    desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
    if os.path.exists(desktop):
        for file in os.listdir(desktop):
            if file.endswith('.lnk') and app_name.split()[0].lower() in file.lower():
                try:
                    os.remove(os.path.join(desktop, file))
                except:
                    pass
