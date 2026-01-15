from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
from models.room import Room, RoomType
from models.guest import Guest
from services.booking_service import BookingService
from services.allocation_service import AllocationService
from services.pricing_service import PricingService
from services.analytics_service import AnalyticsService
import json
import os

class ModernButton(QPushButton):
    """Custom animated button with hover effects"""
    def __init__(self, text, color="#4CAF50", parent=None):
        super().__init__(text, parent)
        self.default_color = color
        self.hover_color = self.lighten_color(color)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def lighten_color(self, hex_color):
        """Lighten a hex color"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        return QColor.fromHsl(h, s, min(255, l + 20), a).name()
    
    def darken_color(self, hex_color):
        """Darken a hex color"""
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        return QColor.fromHsl(h, s, max(0, l - 20), a).name()

class GlassCard(QFrame):
    """Glassmorphism card widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

class StatCard(QFrame):
    """Animated statistics card"""
    def __init__(self, icon, title, value, color="#4CAF50", parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 140)
        self.color = color
        
        # Setup UI
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 40px; color: {color};")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Style
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self.lighten_color(color)});
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def lighten_color(self, hex_color):
        color = QColor(hex_color)
        h, s, l, a = color.getHsl()
        return QColor.fromHsl(h, max(0, s - 30), min(255, l + 30), a).name()
    
    def update_value(self, new_value):
        """Animate value change"""
        self.value_label.setText(str(new_value))
    
    def enterEvent(self, event):
        """Hover effect"""
        self.setCursor(Qt.PointingHandCursor)
        current = self.geometry()
        self.animation.setStartValue(current)
        self.animation.setEndValue(current.adjusted(-5, -5, 5, 5))
        self.animation.start()
    
    def leaveEvent(self, event):
        """Hover off effect"""
        self.setCursor(Qt.ArrowCursor)
        current = self.geometry()
        self.animation.setStartValue(current)
        self.animation.setEndValue(current.adjusted(5, 5, -5, -5))
        self.animation.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏨 Luxe Hotel - Smart Management System")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Set gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 12px 24px;
                margin: 2px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: rgba(255, 255, 255, 0.9);
                color: #667eea;
            }
            QTabBar::tab:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        # Initialize services
        self.booking_service = BookingService()
        self.pricing_service = PricingService()
        
        # Initialize data
        self.rooms = []
        self.guests = {}
        self.guest_counter = 1
        
        # Load data
        self.load_data()
        
        # Initialize other services
        self.allocation_service = AllocationService(self.booking_service)
        self.allocation_service.build_room_graph(self.rooms)
        self.analytics_service = AnalyticsService(self.booking_service, self.rooms)
        
        # Setup UI
        self.setup_ui()
        
        # Start animations
        self.setup_animations()
    
    def setup_animations(self):
        """Setup continuous animations"""
        # Pulse animation for title
        self.title_animation = QPropertyAnimation(self.title_label, b"geometry")
        self.title_animation.setDuration(2000)
        self.title_animation.setLoopCount(-1)  # Infinite loop
        self.title_animation.setEasingCurve(QEasingCurve.InOutSine)
        
    def setup_ui(self):
        """Setup modern UI"""
        # Central widget with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.setCentralWidget(scroll)
        
        central_widget = QWidget()
        scroll.setWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        central_widget.setLayout(main_layout)
        
        # Animated Title
        title_container = QWidget()
        title_layout = QVBoxLayout()
        title_container.setLayout(title_layout)
        
        self.title_label = QLabel("🏨 LUXE HOTEL SUITE")
        self.title_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: white;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.1), 
                stop:0.5 rgba(255, 255, 255, 0.2), 
                stop:1 rgba(255, 255, 255, 0.1));
            border-radius: 15px;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.title_label)
        
        subtitle = QLabel("✨ Powered by AI & Interval Trees | Next-Gen Management System")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            padding: 10px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle)
        
        main_layout.addWidget(title_container)
        
        # Quick Stats Dashboard
        stats_card = GlassCard()
        stats_layout = QVBoxLayout()
        stats_card.setLayout(stats_layout)
        
        stats_title = QLabel("📊 LIVE DASHBOARD")
        stats_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #667eea; padding: 10px;")
        stats_layout.addWidget(stats_title)
        
        # Stats grid
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(20)
        
        # Create stat cards
        bookings = self.booking_service.get_all_bookings()
        active_bookings = sum(1 for b in bookings if b.status.value == "Confirmed")
        total_revenue = sum(b.total_price for b in bookings if b.status.value != "Cancelled")
        
        self.stat_rooms = StatCard("🏠", "Total Rooms", len(self.rooms), "#667eea")
        self.stat_bookings = StatCard("📅", "Active Bookings", active_bookings, "#f093fb")
        self.stat_guests = StatCard("👥", "Total Guests", len(self.guests), "#4facfe")
        self.stat_revenue = StatCard("💰", f"${total_revenue:.0f}", "Revenue", "#43e97b")
        
        stats_grid.addWidget(self.stat_rooms)
        stats_grid.addWidget(self.stat_bookings)
        stats_grid.addWidget(self.stat_guests)
        stats_grid.addWidget(self.stat_revenue)
        
        stats_layout.addLayout(stats_grid)
        main_layout.addWidget(stats_card)
        
        # Tab widget with modern style
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        main_layout.addWidget(tabs)
        
        # Create tabs with icons
        tabs.addTab(self.create_modern_booking_tab(), "🎯 Quick Booking")
        tabs.addTab(self.create_modern_manage_tab(), "📋 Reservations")
        tabs.addTab(self.create_modern_guests_tab(), "👥 VIP Guests")
        tabs.addTab(self.create_modern_rooms_tab(), "🏠 Room Gallery")
        tabs.addTab(self.create_modern_analytics_tab(), "📊 Analytics Pro")
        tabs.addTab(self.create_visualization_tab(), "🌲 Tech View")
        tabs.addTab(self.create_game_tab(), "🎮 Fun Zone")
    
    def create_modern_booking_tab(self):
        """Create modern booking tab with animations"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Header
        header = QLabel("🎯 LIGHTNING FAST BOOKING")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        """)
        layout.addWidget(header)
        
        # Main card
        card = GlassCard()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        
        # Form in grid
        form_grid = QGridLayout()
        form_grid.setSpacing(15)
        
        # Styled labels
        label_style = "font-size: 14px; font-weight: bold; color: #667eea;"
        
        # Guest selection with modern combo
        guest_label = QLabel("👤 Select Guest:")
        guest_label.setStyleSheet(label_style)
        form_grid.addWidget(guest_label, 0, 0)
        
        self.guest_combo = QComboBox()
        self.guest_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #667eea;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
            }
            QComboBox:hover {
                border: 2px solid #764ba2;
            }
        """)
        self.update_guest_combo()
        form_grid.addWidget(self.guest_combo, 0, 1)
        
        # New guest button
        new_guest_btn = ModernButton("➕ Add New Guest", "#43e97b")
        new_guest_btn.clicked.connect(self.add_new_guest)
        form_grid.addWidget(new_guest_btn, 0, 2)
        
        # Room type
        room_label = QLabel("🏠 Room Type:")
        room_label.setStyleSheet(label_style)
        form_grid.addWidget(room_label, 1, 0)
        
        self.room_type_combo = QComboBox()
        self.room_type_combo.addItems([rt.value for rt in RoomType])
        self.room_type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #667eea;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
            }
        """)
        self.room_type_combo.currentTextChanged.connect(self.update_available_rooms)
        form_grid.addWidget(self.room_type_combo, 1, 1, 1, 2)
        
        # Dates
        date_label1 = QLabel("📅 Check-in:")
        date_label1.setStyleSheet(label_style)
        form_grid.addWidget(date_label1, 2, 0)
        
        self.checkin_date = QDateEdit()
        self.checkin_date.setDate(QDate.currentDate())
        self.checkin_date.setCalendarPopup(True)
        self.checkin_date.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 2px solid #667eea;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
            }
        """)
        self.checkin_date.dateChanged.connect(self.update_available_rooms)
        form_grid.addWidget(self.checkin_date, 2, 1, 1, 2)
        
        date_label2 = QLabel("📅 Check-out:")
        date_label2.setStyleSheet(label_style)
        form_grid.addWidget(date_label2, 3, 0)
        
        self.checkout_date = QDateEdit()
        self.checkout_date.setDate(QDate.currentDate().addDays(1))
        self.checkout_date.setCalendarPopup(True)
        self.checkout_date.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                border: 2px solid #667eea;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
            }
        """)
        self.checkout_date.dateChanged.connect(self.update_available_rooms)
        form_grid.addWidget(self.checkout_date, 3, 1, 1, 2)
        
        card_layout.addLayout(form_grid)
        
        # Available rooms list
        rooms_label = QLabel("🏨 Available Rooms:")
        rooms_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #667eea; margin-top: 20px;")
        card_layout.addWidget(rooms_label)
        
        self.available_rooms_list = QListWidget()
        self.available_rooms_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                background-color: white;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 5px;
                margin: 3px;
            }
            QListWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(102, 126, 234, 0.2);
            }
        """)
        self.available_rooms_list.itemClicked.connect(self.calculate_price)
        card_layout.addWidget(self.available_rooms_list)
        
        # Price display
        self.price_label = QLabel("💵 Select a room to see pricing")
        self.price_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #43e97b;
            padding: 20px;
            background: rgba(67, 233, 123, 0.1);
            border-radius: 10px;
            border: 2px solid #43e97b;
        """)
        self.price_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.price_label)
        
        # Book button
        book_btn = ModernButton("🚀 BOOK NOW!", "#667eea")
        book_btn.setMinimumHeight(60)
        book_btn.clicked.connect(self.create_booking)
        card_layout.addWidget(book_btn)
        
        layout.addWidget(card)
        self.update_available_rooms()
        
        return widget
    
    def create_modern_manage_tab(self):
        """Create modern manage bookings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("📋 RESERVATION CONTROL CENTER")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        header_layout.addWidget(header)
        
        refresh_btn = ModernButton("🔄 Refresh", "#4facfe")
        refresh_btn.clicked.connect(self.update_bookings_table)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Table card
        card = GlassCard()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(8)
        self.bookings_table.setHorizontalHeaderLabels([
            "ID", "Guest", "Room", "Check-in", "Check-out", "Price", "Status", "Actions"
        ])
        self.bookings_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 10px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #667eea;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: rgba(102, 126, 234, 0.3);
            }
        """)
        self.bookings_table.horizontalHeader().setStretchLastSection(True)
        self.bookings_table.setAlternatingRowColors(True)
        
        card_layout.addWidget(self.bookings_table)
        layout.addWidget(card)
        
        self.update_bookings_table()
        
        return widget
    
    def create_modern_guests_tab(self):
        """Create modern guests tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Header
        header = QLabel("👥 VIP GUEST LOUNGE")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        layout.addWidget(header)
        
        # Table card
        card = GlassCard()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        
        self.guests_table = QTableWidget()
        self.guests_table.setColumnCount(6)
        self.guests_table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Phone", "Tier", "Points"
        ])
        self.guests_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 10px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f093fb;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        
        card_layout.addWidget(self.guests_table)
        layout.addWidget(card)
        
        self.update_guests_table()
        
        return widget
    
    def create_modern_rooms_tab(self):
        """Create modern rooms tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Header
        header = QLabel("🏠 LUXURY ROOM GALLERY")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        layout.addWidget(header)
        
        # Table card
        card = GlassCard()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        
        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(6)
        self.rooms_table.setHorizontalHeaderLabels([
            "ID", "Number", "Type", "Floor", "Price", "Features"
        ])
        self.rooms_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 10px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #43e97b;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        
        card_layout.addWidget(self.rooms_table)
        layout.addWidget(card)
        
        self.update_rooms_table()
        
        return widget
    
    def create_modern_analytics_tab(self):
        """Create modern analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Header
        header = QLabel("📊 BUSINESS INTELLIGENCE")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        layout.addWidget(header)
        
        # Date range card
        date_card = GlassCard()
        date_layout = QHBoxLayout()
        date_card.setLayout(date_layout)
        
        date_layout.addWidget(QLabel("From:"))
        self.analytics_start = QDateEdit()
        self.analytics_start.setDate(QDate.currentDate().addMonths(-1))
        self.analytics_start.setCalendarPopup(True)
        date_layout.addWidget(self.analytics_start)
        
        date_layout.addWidget(QLabel("To:"))
        self.analytics_end = QDateEdit()
        self.analytics_end.setDate(QDate.currentDate())
        self.analytics_end.setCalendarPopup(True)
        date_layout.addWidget(self.analytics_end)
        
        calc_btn = ModernButton("Calculate", "#667eea")
        calc_btn.clicked.connect(self.update_analytics)
        date_layout.addWidget(calc_btn)
        
        layout.addWidget(date_card)
        
        # Stats display
        stats_card = GlassCard()
        stats_layout = QVBoxLayout()
        stats_card.setLayout(stats_layout)
        
        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        self.analytics_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                border-radius: 10px;
                padding: 20px;
                font-size: 14px;
            }
        """)
        stats_layout.addWidget(self.analytics_text)
        
        layout.addWidget(stats_card)
        
        self.update_analytics()
        
        return widget
    
    def create_game_tab(self):
        """Create fun game tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        widget.setLayout(layout)
        
        # Header
        header = QLabel("🎮 BOOKING MASTER GAME")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f093fb, stop:1 #f5576c);
            border-radius: 15px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Game card
        game_card = GlassCard()
        game_layout = QVBoxLayout()
        game_card.setLayout(game_layout)
        
        instructions = QLabel("""
        🎯 CHALLENGE: Book as many rooms as possible in 60 seconds!
        
        Rules:
        • Click 'Start Game' to begin
        • Quickly select guests, room types, and dates
        • Complete bookings for points
        • Beat your high score!
        """)
        instructions.setStyleSheet("""
            font-size: 16px;
            color: #333;
            padding: 20px;
            background-color: rgba(67, 233, 123, 0.1);
            border-radius: 10px;
        """)
        game_layout.addWidget(instructions)
        
        # Score display
        self.score_label = QLabel("Score: 0 | High Score: 0")
        self.score_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            padding: 15px;
            text-align: center;
        """)
        self.score_label.setAlignment(Qt.AlignCenter)
        game_layout.addWidget(self.score_label)
        
        # Timer
        self.timer_label = QLabel("⏱️ 60s")
        self.timer_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #f5576c;
            padding: 20px;
        """)
        self.timer_label.setAlignment(Qt.AlignCenter)
        game_layout.addWidget(self.timer_label)
        
        # Start button
        self.game_btn = ModernButton("🚀 START GAME", "#f5576c")
        self.game_btn.setMinimumHeight(80)
        self.game_btn.clicked.connect(self.start_game)
        game_layout.addWidget(self.game_btn)
        
        layout.addWidget(game_card)
        
        # Game state
        self.game_score = 0
        self.game_high_score = 0
        self.game_time = 60
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game_timer)
        
        return widget
    
    def start_game(self):
        """Start the booking game"""
        self.game_score = 0
        self.game_time = 60
        self.game_btn.setEnabled(False)
        self.game_timer.start(1000)
        self.update_score()
        QMessageBox.information(self, "Game Started!", "Book as many rooms as you can in 60 seconds!\nGo to the Booking tab to make bookings!")
    
    def update_game_timer(self):
        """Update game timer"""
        self.game_time -= 1
        self.timer_label.setText(f"⏱️ {self.game_time}s")
        
        if self.game_time <= 0:
            self.game_timer.stop()
            self.game_btn.setEnabled(True)
            self.timer_label.setText("⏱️ 60s")
            
            if self.game_score > self.game_high_score:
                self.game_high_score = self.game_score
                QMessageBox.information(self, "New High Score!", 
                    f"🎉 Congratulations! New high score: {self.game_high_score} bookings!")
            else:
                QMessageBox.information(self, "Game Over", 
                    f"Final Score: {self.game_score} bookings\nHigh Score: {self.game_high_score}")
            
            self.update_score()
    
    def update_score(self):
        """Update score display"""
        self.score_label.setText(f"Score: {self.game_score} | High Score: {self.game_high_score}")
    
    # Include all other methods from the previous version...
    # (load_data, save_data, create_sample_rooms, etc.)
    
    def load_data(self):
        """Load data from JSON files or create sample data"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        rooms_file = os.path.join(data_dir, "rooms.json")
        if os.path.exists(rooms_file):
            try:
                with open(rooms_file, 'r') as f:
                    rooms_data = json.load(f)
                    self.rooms = [Room.from_dict(r) for r in rooms_data]
            except:
                self.create_sample_rooms()
        else:
            self.create_sample_rooms()
        
        guests_file = os.path.join(data_dir, "guests.json")
        if os.path.exists(guests_file):
            try:
                with open(guests_file, 'r') as f:
                    guests_data = json.load(f)
                    self.guests = {g['guest_id']: Guest.from_dict(g) for g in guests_data}
                    if self.guests:
                        max_id = max([int(gid[1:]) for gid in self.guests.keys()])
                        self.guest_counter = max_id + 1
            except:
                self.create_sample_guests()
        else:
            self.create_sample_guests()
        
        bookings_file = os.path.join(data_dir, "bookings.json")
        if os.path.exists(bookings_file):
            try:
                with open(bookings_file, 'r') as f:
                    bookings_data = json.load(f)
                    self.booking_service.load_bookings(bookings_data)
            except:
                pass
    
    def save_data(self):
        """Save data to JSON files"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        try:
            rooms_file = os.path.join(data_dir, "rooms.json")
            with open(rooms_file, 'w') as f:
                rooms_data = [r.to_dict() for r in self.rooms]
                json.dump(rooms_data, f, indent=2)
        except:
            pass
        
        try:
            guests_file = os.path.join(data_dir, "guests.json")
            with open(guests_file, 'w') as f:
                guests_data = [g.to_dict() for g in self.guests.values()]
                json.dump(guests_data, f, indent=2)
        except:
            pass
        
        try:
            bookings_file = os.path.join(data_dir, "bookings.json")
            with open(bookings_file, 'w') as f:
                bookings_data = self.booking_service.get_bookings_data()
                json.dump(bookings_data, f, indent=2)
        except:
            pass
    
    def create_sample_rooms(self):
        """Create sample rooms"""
        self.rooms = []
        room_id = 1
        
        for i in range(1, 11):
            self.rooms.append(Room(
                room_id=f"R{room_id:03d}",
                room_number=100 + i,
                room_type=RoomType.STANDARD,
                floor=1,
                base_price=100.0,
                features=["WiFi", "TV", "Mini Bar"]
            ))
            room_id += 1
        
        for i in range(1, 9):
            self.rooms.append(Room(
                room_id=f"R{room_id:03d}",
                room_number=200 + i,
                room_type=RoomType.DELUXE,
                floor=2,
                base_price=150.0,
                features=["WiFi", "TV", "Mini Bar", "Balcony"]
            ))
            room_id += 1
        
        for i in range(1, 6):
            self.rooms.append(Room(
                room_id=f"R{room_id:03d}",
                room_number=300 + i,
                room_type=RoomType.SUITE,
                floor=3,
                base_price=250.0,
                features=["WiFi", "TV", "Mini Bar", "Kitchen"]
            ))
            room_id += 1
        
        self.rooms.append(Room(
            room_id=f"R{room_id:03d}",
            room_number=401,
            room_type=RoomType.PRESIDENTIAL,
            floor=4,
            base_price=500.0,
            features=["WiFi", "TV", "Mini Bar", "Pool"]
        ))
        
        self.save_data()
    
    def create_sample_guests(self):
        """Create sample guests"""
        sample_guests = [
            {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890", "id_proof": "DL123456"},
            {"name": "Jane Smith", "email": "jane@example.com", "phone": "+1234567891", "id_proof": "PP987654"},
            {"name": "Bob Wilson", "email": "bob@example.com", "phone": "+1234567892", "id_proof": "DL789012"},
        ]
        
        for guest_data in sample_guests:
            guest_id = f"G{self.guest_counter:04d}"
            self.guest_counter += 1
            guest = Guest(
                guest_id=guest_id,
                name=guest_data["name"],
                email=guest_data["email"],
                phone=guest_data["phone"],
                id_proof=guest_data["id_proof"]
            )
            self.guests[guest_id] = guest
        
        self.save_data()
    
    def update_guest_combo(self):
        """Update guest dropdown"""
        self.guest_combo.clear()
        for guest in self.guests.values():
            self.guest_combo.addItem(f"{guest.name} ({guest.guest_id})", guest.guest_id)
    
    def add_new_guest(self):
        """Add new guest with modern dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("✨ Add VIP Guest")
        dialog.setModal(True)
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid white;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        
        layout = QFormLayout()
        dialog.setLayout(layout)
        
        name_input = QLineEdit()
        email_input = QLineEdit()
        phone_input = QLineEdit()
        id_input = QLineEdit()
        
        layout.addRow("Name:", name_input)
        layout.addRow("Email:", email_input)
        layout.addRow("Phone:", phone_input)
        layout.addRow("ID Proof:", id_input)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        if dialog.exec_() == QDialog.Accepted:
            guest_id = f"G{self.guest_counter:04d}"
            self.guest_counter += 1
            
            guest = Guest(
                guest_id=guest_id,
                name=name_input.text(),
                email=email_input.text(),
                phone=phone_input.text(),
                id_proof=id_input.text()
            )
            
            self.guests[guest_id] = guest
            self.update_guest_combo()
            self.update_guests_table()
            self.save_data()
            
            # Update stats
            self.stat_guests.update_value(len(self.guests))
            
            QMessageBox.information(self, "Success!", f"🎉 Guest {guest.name} added successfully!")
    
    def update_available_rooms(self):
        """Update available rooms list"""
        self.available_rooms_list.clear()
        
        room_type = RoomType(self.room_type_combo.currentText())
        check_in = self.checkin_date.date().toPyDate()
        check_out = self.checkout_date.date().toPyDate()
        
        if check_in >= check_out:
            self.available_rooms_list.addItem("❌ Invalid dates")
            return
        
        check_in_dt = datetime.combine(check_in, datetime.min.time())
        check_out_dt = datetime.combine(check_out, datetime.min.time())
        
        filtered_rooms = [r for r in self.rooms if r.room_type == room_type]
        available = self.booking_service.find_available_rooms(check_in_dt, check_out_dt, filtered_rooms)
        
        if not available:
            self.available_rooms_list.addItem("😔 No rooms available")
        else:
            for room in available:
                features_str = ", ".join(room.features[:3]) if room.features else "Standard"
                item_text = f"🏠 Room {room.room_number} - Floor {room.floor} | {features_str}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, room)
                self.available_rooms_list.addItem(item)
    
    def calculate_price(self):
        """Calculate price for selected room"""
        current_item = self.available_rooms_list.currentItem()
        if not current_item:
            return
        
        room = current_item.data(Qt.UserRole)
        check_in = datetime.combine(self.checkin_date.date().toPyDate(), datetime.min.time())
        check_out = datetime.combine(self.checkout_date.date().toPyDate(), datetime.min.time())
        
        price = self.pricing_service.calculate_price(room, check_in, check_out)
        
        guest_id = self.guest_combo.currentData()
        if guest_id:
            guest = self.guests[guest_id]
            original_price = price
            price = self.pricing_service.apply_loyalty_discount(price, guest.loyalty_tier.value)
            
            if price < original_price:
                self.price_label.setText(f"💰 ${price:.2f} 🎉 (Was ${original_price:.2f})")
            else:
                self.price_label.setText(f"💰 ${price:.2f}")
        else:
            self.price_label.setText(f"💰 ${price:.2f}")
    
    def create_booking(self):
        """Create new booking with celebration"""
        try:
            guest_id = self.guest_combo.currentData()
            if not guest_id:
                QMessageBox.warning(self, "Oops!", "Please select a guest first!")
                return
            
            current_item = self.available_rooms_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Oops!", "Please select a room first!")
                return
            
            room = current_item.data(Qt.UserRole)
            check_in = datetime.combine(self.checkin_date.date().toPyDate(), datetime.min.time())
            check_out = datetime.combine(self.checkout_date.date().toPyDate(), datetime.min.time())
            
            price = self.pricing_service.calculate_price(room, check_in, check_out)
            guest = self.guests[guest_id]
            price = self.pricing_service.apply_loyalty_discount(price, guest.loyalty_tier.value)
            
            booking = self.booking_service.create_booking(guest_id, room.room_id, check_in, check_out, price)
            
            points = int(price)
            guest.add_loyalty_points(points)
            guest.booking_history.append(booking.booking_id)
            
            self.save_data()
            self.update_available_rooms()
            self.update_bookings_table()
            
            # Update stats
            bookings = self.booking_service.get_all_bookings()
            active = sum(1 for b in bookings if b.status.value == "Confirmed")
            revenue = sum(b.total_price for b in bookings if b.status.value != "Cancelled")
            self.stat_bookings.update_value(active)
            self.stat_revenue.update_value(f"${revenue:.0f}")
            
            # Update game score if playing
            if self.game_timer.isActive():
                self.game_score += 1
                self.update_score()
            
            QMessageBox.information(self, "🎉 Success!", 
                f"Booking #{booking.booking_id} confirmed!\n\n"
                f"💰 Total: ${price:.2f}\n"
                f"⭐ Points earned: {points}\n"
                f"🏆 Guest tier: {guest.loyalty_tier.value}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def update_bookings_table(self):
        """Update bookings table"""
        bookings = self.booking_service.get_all_bookings()
        self.bookings_table.setRowCount(len(bookings))
        
        for i, booking in enumerate(bookings):
            guest = self.guests.get(booking.guest_id)
            guest_name = guest.name if guest else "Unknown"
            
            room = next((r for r in self.rooms if r.room_id == booking.room_id), None)
            room_num = room.room_number if room else "Unknown"
            
            self.bookings_table.setItem(i, 0, QTableWidgetItem(booking.booking_id))
            self.bookings_table.setItem(i, 1, QTableWidgetItem(guest_name))
            self.bookings_table.setItem(i, 2, QTableWidgetItem(str(room_num)))
            self.bookings_table.setItem(i, 3, QTableWidgetItem(booking.check_in.strftime("%Y-%m-%d")))
            self.bookings_table.setItem(i, 4, QTableWidgetItem(booking.check_out.strftime("%Y-%m-%d")))
            self.bookings_table.setItem(i, 5, QTableWidgetItem(f"${booking.total_price:.2f}"))
            self.bookings_table.setItem(i, 6, QTableWidgetItem(booking.status.value))
            
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_widget.setLayout(btn_layout)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            if booking.status.value == "Confirmed":
                cancel_btn = ModernButton("Cancel", "#f5576c")
                cancel_btn.clicked.connect(lambda checked, bid=booking.booking_id: self.cancel_booking(bid))
                btn_layout.addWidget(cancel_btn)
            
            self.bookings_table.setCellWidget(i, 7, btn_widget)
        
        self.bookings_table.resizeColumnsToContents()
    
    def cancel_booking(self, booking_id):
        """Cancel booking"""
        reply = QMessageBox.question(self, "Confirm Cancellation", 
            "Are you sure you want to cancel this booking?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.booking_service.cancel_booking(booking_id)
                self.save_data()
                self.update_bookings_table()
                self.update_available_rooms()
                
                # Update stats
                bookings = self.booking_service.get_all_bookings()
                active = sum(1 for b in bookings if b.status.value == "Confirmed")
                self.stat_bookings.update_value(active)
                
                QMessageBox.information(self, "Cancelled", "Booking cancelled successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    def update_guests_table(self):
        """Update guests table"""
        self.guests_table.setRowCount(len(self.guests))
        
        for i, guest in enumerate(self.guests.values()):
            self.guests_table.setItem(i, 0, QTableWidgetItem(guest.guest_id))
            self.guests_table.setItem(i, 1, QTableWidgetItem(guest.name))
            self.guests_table.setItem(i, 2, QTableWidgetItem(guest.email))
            self.guests_table.setItem(i, 3, QTableWidgetItem(guest.phone))
            self.guests_table.setItem(i, 4, QTableWidgetItem(guest.loyalty_tier.value))
            self.guests_table.setItem(i, 5, QTableWidgetItem(str(guest.loyalty_points)))
        
        self.guests_table.resizeColumnsToContents()
    
    def update_rooms_table(self):
        """Update rooms table"""
        self.rooms_table.setRowCount(len(self.rooms))
        
        for i, room in enumerate(self.rooms):
            self.rooms_table.setItem(i, 0, QTableWidgetItem(room.room_id))
            self.rooms_table.setItem(i, 1, QTableWidgetItem(str(room.room_number)))
            self.rooms_table.setItem(i, 2, QTableWidgetItem(room.room_type.value))
            self.rooms_table.setItem(i, 3, QTableWidgetItem(str(room.floor)))
            self.rooms_table.setItem(i, 4, QTableWidgetItem(f"${room.base_price:.2f}"))
            self.rooms_table.setItem(i, 5, QTableWidgetItem(", ".join(room.features)))
        
        self.rooms_table.resizeColumnsToContents()
    
    def update_analytics(self):
        """Update analytics display"""
        start_date = datetime.combine(self.analytics_start.date().toPyDate(), datetime.min.time())
        end_date = datetime.combine(self.analytics_end.date().toPyDate(), datetime.min.time())
        
        occupancy = self.analytics_service.get_occupancy_rate(start_date, end_date)
        revenue = self.analytics_service.get_revenue(start_date, end_date)
        room_dist = self.analytics_service.get_room_type_distribution()
        stats = self.analytics_service.get_booking_stats()
        
        text = "<h1 style='color: #667eea;'>📊 Analytics Dashboard</h1>"
        text += f"<p><b>Period:</b> {start_date.date()} to {end_date.date()}</p><hr>"
        text += "<h2 style='color: #43e97b;'>💎 Key Metrics</h2>"
        text += f"<p style='font-size: 18px;'>• <b>Occupancy Rate:</b> {occupancy:.1f}%</p>"
        text += f"<p style='font-size: 18px;'>• <b>Total Revenue:</b> ${revenue:.2f}</p>"
        text += f"<p style='font-size: 18px;'>• <b>Total Bookings:</b> {stats['total']}</p><hr>"
        text += "<h2 style='color: #f093fb;'>📋 Booking Status</h2>"
        text += f"<p>• ✅ <b>Confirmed:</b> {stats['confirmed']}</p>"
        text += f"<p>• 🏨 <b>Checked In:</b> {stats['checked_in']}</p>"
        text += f"<p>• ❌ <b>Cancelled:</b> {stats['cancelled']}</p><hr>"
        text += "<h2 style='color: #4facfe;'>🏠 Room Distribution</h2>"
        for room_type, count in room_dist.items():
            text += f"<p>• <b>{room_type}:</b> {count} bookings</p>"
        
        self.analytics_text.setHtml(text)
    
    def create_visualization_tab(self):
        """Keep the tree visualization tab from original"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        header = QLabel("🌲 INTERVAL TREE VISUALIZATION")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 15px;
        """)
        layout.addWidget(header)
        
        card = GlassCard()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        
        info = QLabel("Select a room to visualize its interval tree structure")
        info.setStyleSheet("font-size: 14px; padding: 10px;")
        card_layout.addWidget(info)
        
        room_layout = QHBoxLayout()
        room_layout.addWidget(QLabel("Select Room:"))
        
        self.viz_room_combo = QComboBox()
        for room in self.rooms:
            self.viz_room_combo.addItem(f"Room {room.room_number} ({room.room_type.value})", room.room_id)
        room_layout.addWidget(self.viz_room_combo)
        
        viz_btn = ModernButton("🌲 Visualize", "#4facfe")
        viz_btn.clicked.connect(self.show_tree_visualization)
        room_layout.addWidget(viz_btn)
        
        room_layout.addStretch()
        card_layout.addLayout(room_layout)
        
        self.tree_stats_text = QTextEdit()
        self.tree_stats_text.setReadOnly(True)
        self.tree_stats_text.setMaximumHeight(200)
        card_layout.addWidget(self.tree_stats_text)
        
        layout.addWidget(card)
        layout.addStretch()
        
        self.update_tree_stats()
        
        return widget
    
    def show_tree_visualization(self):
        """Show tree visualization"""
        try:
            from ui.tree_visualization import TreeVisualizationDialog
            
            room_id = self.viz_room_combo.currentData()
            
            if room_id not in self.booking_service.room_trees:
                QMessageBox.information(self, "No Data", "No bookings for this room yet!")
                return
            
            tree = self.booking_service.room_trees[room_id]
            
            if tree.size == 0:
                QMessageBox.information(self, "Empty", "This room's tree is empty!")
                return
            
            dialog = TreeVisualizationDialog(tree, room_id, self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not visualize tree: {e}")
    
    def update_tree_stats(self):
        """Update tree statistics"""
        total_bookings = len(self.booking_service.get_all_bookings())
        active_bookings = sum(1 for b in self.booking_service.get_all_bookings() if b.status.value != "Cancelled")
        num_trees = len(self.booking_service.room_trees)
        
        stats = "<h3>Interval Tree Statistics</h3>"
        stats += f"<p>• <b>Total Bookings:</b> {total_bookings}</p>"
        stats += f"<p>• <b>Active Bookings:</b> {active_bookings}</p>"
        stats += f"<p>• <b>Active Trees:</b> {num_trees}</p>"
        stats += f"<p>• <b>Avg Tree Size:</b> {active_bookings / num_trees if num_trees > 0 else 0:.1f}</p>"
        
        self.tree_stats_text.setHtml(stats)