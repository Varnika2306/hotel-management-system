class BSTNode:
    """Binary Search Tree Node"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    """Binary Search Tree for price-based queries"""
    
    def __init__(self):
        self.root = None
    
    def insert(self, key, value):
        """Insert key-value pair"""
        self.root = self._insert_recursive(self.root, key, value)
    
    def _insert_recursive(self, node, key, value):
        if node is None:
            return BSTNode(key, value)
        
        if key < node.key:
            node.left = self._insert_recursive(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_recursive(node.right, key, value)
        else:
            node.value = value
        
        return node
    
    def search(self, key):
        """Search for a key"""
        return self._search_recursive(self.root, key)
    
    def _search_recursive(self, node, key):
        if node is None:
            return None
        if key == node.key:
            return node.value
        elif key < node.key:
            return self._search_recursive(node.left, key)
        else:
            return self._search_recursive(node.right, key)
    
    def range_query(self, min_key, max_key):
        """Find all values in key range"""
        results = []
        self._range_query_recursive(self.root, min_key, max_key, results)
        return results
    
    def _range_query_recursive(self, node, min_key, max_key, results):
        if node is None:
            return
        
        if min_key < node.key:
            self._range_query_recursive(node.left, min_key, max_key, results)
        
        if min_key <= node.key <= max_key:
            results.append(node.value)
        
        if node.key < max_key:
            self._range_query_recursive(node.right, min_key, max_key, results)