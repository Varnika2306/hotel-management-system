from datetime import datetime

class Interval:
    """Represents a booking interval"""
    def __init__(self, start, end, booking_id, room_id):
        self.start = start
        self.end = end
        self.booking_id = booking_id
        self.room_id = room_id
    
    def overlaps(self, other):
        """Check if two intervals overlap"""
        return self.start < other.end and other.start < self.end
    
    def __repr__(self):
        return f"Interval({self.start.date()}-{self.end.date()}, Room:{self.room_id})"


class IntervalNode:
    """Node in interval tree"""
    def __init__(self, interval):
        self.interval = interval
        self.max_end = interval.end
        self.left = None
        self.right = None
        self.height = 1


class IntervalTree:
    """AVL-based interval tree for efficient booking management"""
    
    def __init__(self):
        self.root = None
        self.size = 0
    
    def insert(self, interval):
        """Insert an interval"""
        self.root = self._insert_recursive(self.root, interval)
        self.size += 1
    
    def _insert_recursive(self, node, interval):
        if node is None:
            return IntervalNode(interval)
        
        if interval.start < node.interval.start:
            node.left = self._insert_recursive(node.left, interval)
        else:
            node.right = self._insert_recursive(node.right, interval)
        
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.max_end = max(node.interval.end, 
                          self._get_max_end(node.left), 
                          self._get_max_end(node.right))
        
        balance = self._get_balance(node)
        
        # AVL rotations
        if balance > 1 and interval.start < node.left.interval.start:
            return self._rotate_right(node)
        if balance < -1 and interval.start >= node.right.interval.start:
            return self._rotate_left(node)
        if balance > 1 and interval.start >= node.left.interval.start:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and interval.start < node.right.interval.start:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    def search_overlaps(self, query_interval, room_id=None):
        """Find all overlapping intervals"""
        results = []
        self._search_recursive(self.root, query_interval, room_id, results)
        return results
    
    def _search_recursive(self, node, query, room_id, results):
        if node is None:
            return
        
        if node.interval.overlaps(query):
            if room_id is None or node.interval.room_id == room_id:
                results.append(node.interval)
        
        if node.left and node.left.max_end > query.start:
            self._search_recursive(node.left, query, room_id, results)
        
        if node.right and node.interval.start < query.end:
            self._search_recursive(node.right, query, room_id, results)
    
    def delete(self, interval):
        """Delete an interval"""
        self.root = self._delete_recursive(self.root, interval)
        if self.root:
            self.size -= 1
    
    def _delete_recursive(self, node, interval):
        if node is None:
            return node
        
        if interval.start < node.interval.start:
            node.left = self._delete_recursive(node.left, interval)
        elif interval.start > node.interval.start:
            node.right = self._delete_recursive(node.right, interval)
        else:
            if interval.booking_id == node.interval.booking_id:
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left
                
                temp = self._get_min_node(node.right)
                node.interval = temp.interval
                node.right = self._delete_recursive(node.right, temp.interval)
            else:
                node.right = self._delete_recursive(node.right, interval)
        
        if node is None:
            return node
        
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        node.max_end = max(node.interval.end,
                          self._get_max_end(node.left),
                          self._get_max_end(node.right))
        
        balance = self._get_balance(node)
        
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        
        return node
    
    def _get_height(self, node):
        return 0 if node is None else node.height
    
    def _get_max_end(self, node):
        return datetime.min if node is None else node.max_end
    
    def _get_balance(self, node):
        return 0 if node is None else self._get_height(node.left) - self._get_height(node.right)
    
    def _rotate_left(self, z):
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        z.max_end = max(z.interval.end, self._get_max_end(z.left), self._get_max_end(z.right))
        y.max_end = max(y.interval.end, self._get_max_end(y.left), self._get_max_end(y.right))
        
        return y
    
    def _rotate_right(self, z):
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        z.max_end = max(z.interval.end, self._get_max_end(z.left), self._get_max_end(z.right))
        y.max_end = max(y.interval.end, self._get_max_end(y.left), self._get_max_end(y.right))
        
        return y
    
    def _get_min_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current