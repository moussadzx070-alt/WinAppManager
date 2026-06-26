import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QMessageBox, QLineEdit, QFileIconProvider)
from PyQt5.QtCore import Qt, QTimer, QFileInfo, QSize
from PyQt5.QtGui import QIcon
from app_manager import get_installed_apps, uninstall_and_deep_clean
from process_manager import check_app_status, kill_processes

# ستايل الواجهة العصري (Dark Mode)
STYLESHEET = """
QMainWindow { background-color: #11111b; }
QWidget { color: #cdd6f4; font-family: 'Segoe UI'; }
QLineEdit { 
    background-color: #1e1e2e; border: 1px solid #45475a; 
    border-radius: 8px; padding: 10px; font-size: 14px; color: #cdd6f4;
}
QLineEdit:focus { border: 1px solid #89b4fa; }
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { background: #181825; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; }
QPushButton { 
    border-radius: 6px; padding: 8px 15px; font-weight: bold; font-size: 12px; border: none;
}
QPushButton#kill_btn { background-color: #f38ba8; color: #11111b; }
QPushButton#kill_btn:hover { background-color: #eba0ac; }
QPushButton#kill_btn:disabled { background-color: #45475a; color: #6c7086; }
QPushButton#uninstall_btn { background-color: #89b4fa; color: #11111b; }
QPushButton#uninstall_btn:hover { background-color: #b4befe; }
"""

class AppRow(QWidget):
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.pids = []
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("QWidget { background-color: #1e1e2e; border-radius: 10px; margin-bottom: 5px; }"
                           "QWidget:hover { background-color: #313244; }")
        
        # استخراج الأيقونة الذكي
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setStyleSheet("background: transparent;")
        
        provider = QFileIconProvider()
        icon = None
        if app_data['display_icon'] and os.path.exists(app_data['display_icon']):
            icon = provider.icon(QFileInfo(app_data['display_icon']))
        elif app_data['install_location'] and os.path.exists(app_data['install_location']):
             icon = provider.icon(QFileInfo(app_data['install_location']))
             
        if icon and not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(QSize(32, 32)))
        
        layout.addWidget(self.icon_label)
        
        # الاسم والحجم
        info_text = f"<span style='font-size:14px; font-weight:bold;'>{app_data['name']}</span><br>" \
                    f"<span style='color:#a6adc8; font-size:11px;'>Size: {app_data['size_mb']:.2f} MB</span>"
        self.info_label = QLabel(info_text)
        self.info_label.setMinimumWidth(300)
        self.info_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.info_label)
        
        # الرام المستهلكة
        self.ram_label = QLabel("RAM: 0.00 MB")
        self.ram_label.setMinimumWidth(120)
        self.ram_label.setStyleSheet("background: transparent; color: #a6adc8;")
        layout.addWidget(self.ram_label)
        
        # الحالة
        self.status_label = QLabel("Inactive")
        self.status_label.setMinimumWidth(80)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background: transparent; color: #f38ba8; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # الأزرار
        self.kill_btn = QPushButton("إيقاف (Kill)")
        self.kill_btn.setObjectName("kill_btn")
        self.kill_btn.setEnabled(False)
        self.kill_btn.clicked.connect(self.kill_app)
        layout.addWidget(self.kill_btn)
        
        self.uninstall_btn = QPushButton("إزالة عميقة (Deep Uninstall)")
        self.uninstall_btn.setObjectName("uninstall_btn")
        self.uninstall_btn.clicked.connect(self.uninstall)
        layout.addWidget(self.uninstall_btn)
        
        self.update_status()

    def update_status(self):
        status = check_app_status(self.app_data['install_location'])
        self.pids = status['pids']
        self.ram_label.setText(f"RAM: {status['ram']:.2f} MB")
        
        if status['active']:
            self.status_label.setText("Active")
            self.status_label.setStyleSheet("background: transparent; color: #a6e3a1; font-weight: bold;")
            self.kill_btn.setEnabled(True)
        else:
            self.status_label.setText("Inactive")
            self.status_label.setStyleSheet("background: transparent; color: #f38ba8; font-weight: bold;")
            self.kill_btn.setEnabled(False)

    def kill_app(self):
        kill_processes(self.pids)
        self.update_status()

    def uninstall(self):
        confirm = QMessageBox.warning(self, 'تحذير الحذف العميق', 
                                       f"هل أنت متأكد من الإزالة العميقة لـ {self.app_data['name']}؟\n\n"
                                       "سيقوم هذا الخيار بحذف البرنامج، ومسح بياناته من AppData، وحذف أيقوناته من سطح المكتب نهائياً.",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            uninstall_and_deep_clean(self.app_data)
            self.hide() # إخفاء العنصر بعد بدء الحذف

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DZ Manager z - Administrator")
        self.setGeometry(100, 100, 950, 700)
        self.setStyleSheet(STYLESHEET)
        
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # شريط البحث
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 ابحث عن برنامج (مثال: Chrome, Spotify...)")
        self.search_bar.textChanged.connect(self.filter_apps)
        main_layout.addWidget(self.search_bar)
        
        # منطقة التمرير
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(2)
        scroll.setWidget(self.scroll_content)
        
        self.app_rows = []
        self.load_apps()
        
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

    def filter_apps(self, text):
        search_term = text.lower()
        for row in self.app_rows:
            if search_term in row.app_data['name'].lower():
                row.show()
            else:
                row.hide()

    def refresh_statuses(self):
        for row in self.app_rows:
            if not row.isHidden(): # تحديث البرامج الظاهرة فقط لتخفيف الضغط
                row.update_status()
