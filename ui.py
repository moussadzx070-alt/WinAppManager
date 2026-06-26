import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor, QPalette
from app_manager import get_installed_apps, uninstall_app
from process_manager import check_app_status, kill_processes

class AppRow(QWidget):
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.pids = []
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("border-bottom: 1px solid #ccc; padding: 5px;")
        
        # الأيقونة (استخراج افتراضي من النظام)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        # إذا كان هناك مسار، نحاول جلب الأيقونة منه
        layout.addWidget(self.icon_label)
        
        # الاسم والحجم
        info_text = f"<b>{app_data['name']}</b><br>Size: {app_data['size_mb']:.2f} MB"
        self.info_label = QLabel(info_text)
        self.info_label.setMinimumWidth(250)
        layout.addWidget(self.info_label)
        
        # الرام المستهلكة
        self.ram_label = QLabel("RAM: 0.00 MB")
        self.ram_label.setMinimumWidth(100)
        layout.addWidget(self.ram_label)
        
        # الحالة (Active / Inactive)
        self.status_label = QLabel("Inactive")
        self.status_label.setMinimumWidth(80)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # زر إيقاف التنشيط
        self.kill_btn = QPushButton("إيقاف (Kill)")
        self.kill_btn.setEnabled(False)
        self.kill_btn.clicked.connect(self.kill_app)
        layout.addWidget(self.kill_btn)
        
        # زر إزالة التثبيت
        self.uninstall_btn = QPushButton("Uninstall")
        self.uninstall_btn.clicked.connect(self.uninstall)
        layout.addWidget(self.uninstall_btn)
        
        self.update_status()

    def update_status(self):
        status = check_app_status(self.app_data['install_location'])
        self.pids = status['pids']
        self.ram_label.setText(f"RAM: {status['ram']:.2f} MB")
        
        if status['active']:
            self.status_label.setText("Active")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.kill_btn.setEnabled(True)
        else:
            self.status_label.setText("Inactive")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.kill_btn.setEnabled(False)

    def kill_app(self):
        kill_processes(self.pids)
        self.update_status()

    def uninstall(self):
        confirm = QMessageBox.question(self, 'تأكيد', 
                                       f"هل أنت متأكد من إزالة {self.app_data['name']}؟",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            uninstall_app(self.app_data['uninstall_cmd'])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinAppManager - Administrator")
        self.setGeometry(100, 100, 800, 600)
        
        # ضبط أيقونة البرنامج العلوية
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # منطقة التمرير (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        scroll.setWidget(self.scroll_content)
        
        self.app_rows = []
        self.load_apps()
        
        # تحديث الحالة كل 5 ثواني
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_statuses)
        self.timer.start(5000)

    def load_apps(self):
        apps = get_installed_apps()
        for app in apps:
            row = AppRow(app)
            self.scroll_layout.addWidget(row)
            self.app_rows.append(row)
            
        self.scroll_layout.addStretch()

    def refresh_statuses(self):
        for row in self.app_rows:
            row.update_status()
