from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class TreeVisualizationDialog(QDialog):
    def __init__(self, interval_tree, room_id, parent=None):
        super().__init__(parent)
        self.interval_tree = interval_tree
        self.room_id = room_id
        self.setWindowTitle(f"Interval Tree Visualization - Room {room_id}")
        self.setGeometry(100, 100, 1000, 700)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Info label
        info = QLabel(f"Interval Tree Structure for Room {room_id}")
        info.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(info)
        
        # Canvas for drawing
        self.canvas = TreeCanvas(interval_tree)
        layout.addWidget(self.canvas)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


class TreeCanvas(QWidget):
    def __init__(self, interval_tree):
        super().__init__()
        self.tree = interval_tree
        self.setMinimumSize(900, 600)
        self.node_positions = {}
        self.calculate_positions()
    
    def calculate_positions(self):
        """Calculate x,y positions for each node"""
        if not self.tree.root:
            return
        
        self.node_positions = {}
        self._calculate_positions_recursive(self.tree.root, 450, 50, 200, 0)
    
    def _calculate_positions_recursive(self, node, x, y, x_offset, depth):
        if node is None:
            return
        
        # Store position
        self.node_positions[id(node)] = (x, y)
        
        # Calculate positions for children
        new_offset = x_offset / 2
        if node.left:
            self._calculate_positions_recursive(node.left, x - x_offset, y + 80, new_offset, depth + 1)
        if node.right:
            self._calculate_positions_recursive(node.right, x + x_offset, y + 80, new_offset, depth + 1)
    
    def paintEvent(self, event):
        if not self.tree.root:
            painter = QPainter(self)
            painter.drawText(self.rect(), Qt.AlignCenter, "No bookings in this tree")
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw edges first
        self._draw_edges(painter, self.tree.root)
        
        # Draw nodes on top
        self._draw_nodes(painter, self.tree.root)
    
    def _draw_edges(self, painter, node):
        if node is None:
            return
        
        if id(node) not in self.node_positions:
            return
        
        x, y = self.node_positions[id(node)]
        
        # Draw line to left child
        if node.left and id(node.left) in self.node_positions:
            left_x, left_y = self.node_positions[id(node.left)]
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawLine(x, y + 20, left_x, left_y - 20)
            self._draw_edges(painter, node.left)
        
        # Draw line to right child
        if node.right and id(node.right) in self.node_positions:
            right_x, right_y = self.node_positions[id(node.right)]
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawLine(x, y + 20, right_x, right_y - 20)
            self._draw_edges(painter, node.right)
    
    def _draw_nodes(self, painter, node):
        if node is None:
            return
        
        if id(node) not in self.node_positions:
            return
        
        x, y = self.node_positions[id(node)]
        
        # Draw circle
        painter.setBrush(QBrush(QColor(70, 130, 180)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(x - 30, y - 20, 60, 40)
        
        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 8))
        
        start_str = node.interval.start.strftime("%m/%d")
        end_str = node.interval.end.strftime("%m/%d")
        text = f"{start_str}\n{end_str}"
        
        text_rect = QRect(x - 30, y - 20, 60, 40)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        # Draw max_end below
        painter.setPen(QPen(QColor(255, 0, 0)))
        painter.setFont(QFont("Arial", 7))
        max_end_str = node.max_end.strftime("%m/%d")
        painter.drawText(x - 20, y + 35, f"max:{max_end_str}")
        
        # Recursively draw children
        self._draw_nodes(painter, node.left)
        self._draw_nodes(painter, node.right)