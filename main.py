import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui import MainWindow

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit()

    # تفعيل الدقة العالية للشاشات الحديثة
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    
    # تطبيق خط موحد للتطبيق
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
