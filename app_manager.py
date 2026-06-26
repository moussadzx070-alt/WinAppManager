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

def convert_to_silent_cmd(cmd):
    """
    دالة ذكية لتحويل أمر الحذف العادي إلى أمر صامت مخفي تماماً
    بناءً على نوع حزمة التثبيت المستخدمة للبرنامج.
    """
    if not cmd:
        return ""
    
    cmd_lower = cmd.lower()
    
    # 1. إذا كان البرنامج عبارة عن حزمة نظام ويندوز القياسية (MSI)
    if "msiexec" in cmd_lower:
        # تحويل خيار التثبيت /I إلى حذف /X إن وجد، وإضافة خيارات الصمت المطلق
        if "/i" in cmd_lower:
            cmd = cmd.replace("/I", "/X").replace("/i", "/x")
        if "/qn" not in cmd_lower:
            cmd += " /qn /norestart"
        return cmd
        
    # 2. إذا كان المثبت من نوع Inno Setup (مشهور جداً وينتج ملفات unins000.exe)
    if "unins000" in cmd_lower:
        if "/verysilent" not in cmd_lower:
            cmd += " /VERYSILENT /SUPPRESSMSGBOXES /NORESTART"
        return cmd
        
    # 3. إذا كان المثبت من نوع Nullsoft (NSIS) (ينتج ملفات uninstall.exe الافتراضية)
    if "uninstall.exe" in cmd_lower or "uninst.exe" in cmd_lower:
        if "/s" not in cmd_lower:
            cmd += " /S"
        return cmd
        
    # 4. محاولة عامة حذرة للمثبتات الأخرى (مثل Advanced Installer أو InstallShield)
    if "/s" not in cmd_lower and "/silent" not in cmd_lower and "/q" not in cmd_lower:
        if "setup" in cmd_lower:
            cmd += " /s /v/qn"
        else:
            cmd += " /S" # إضافة علامة الحذف الصامت العامة القياسية
            
    return cmd

def uninstall_and_deep_clean(app_data):
    raw_cmd = app_data['uninstall_cmd']
    
    # تحويل الأمر ليعمل في الخلفية بدون نوافذ Next
    silent_cmd = convert_to_silent_cmd(raw_cmd)
    
    # 1. تنفيذ أمر الإزالة الصامت في الخلفية
    try:
        # تشغيل العملية مع إخفاء نافذة الـ CMD تماماً (CREATE_NO_WINDOW)
        process = subprocess.Popen(
            silent_cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        # ننتظر حتى ينتهي الحذف الصامت تماماً (بحد أقصى 20 ثانية) لكي لا نقوم بالمسح العميق والملفات لا تزال قيد الاستخدام
        process.wait(timeout=20) 
    except Exception as e:
        print(f"Error executing silent uninstaller: {e}")

    app_name = app_data['name']
    install_loc = app_data['install_location']

    # 2. تنظيف مسار التثبيت المتبقي بقوة بصلاحيات الأدمن
    if install_loc and os.path.exists(install_loc):
        if len(install_loc) > 10 and app_name.split()[0].lower() in install_loc.lower():
            try:
                shutil.rmtree(install_loc, ignore_errors=True)
            except:
                pass

    # 3. تنظيف الداتا المتبقية من مجلدات النظام المخفية AppData (Local / Roaming)
    appdata_paths = [os.environ.get('APPDATA'), os.environ.get('LOCALAPPDATA')]
    for path in appdata_paths:
        if path:
            target_folder = os.path.join(path, app_name.split()[0])
            if os.path.exists(target_folder) and len(app_name) > 2:
                try:
                    shutil.rmtree(target_folder, ignore_errors=True)
                except:
                    pass

    # 4. تنظيف اختصارات سطح المكتب نهائياً
    desktop = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
    if os.path.exists(desktop):
        for file in os.listdir(desktop):
            if file.endswith('.lnk') and app_name.split()[0].lower() in file.lower():
                try:
                    os.remove(os.path.join(desktop, file))
                except:
                    pass
