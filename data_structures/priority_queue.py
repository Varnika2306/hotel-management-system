class PriorityQueue:
    """Min-heap based priority queue for waitlist management"""
    
    def __init__(self):
        self.heap = []
    
    def push(self, priority, item):
        """Add item with priority (lower = higher priority)"""
        self.heap.append((priority, item))
        self._heapify_up(len(self.heap) - 1)
    
    def pop(self):
        """Remove and return highest priority item"""
        if not self.heap:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()[1]
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root[1]
    
    def peek(self):
        """View highest priority item"""
        return self.heap[0][1] if self.heap else None
    
    def is_empty(self):
        return len(self.heap) == 0
    
    def _heapify_up(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)
    
    def _heapify_down(self, index):
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right
        
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)
    
    def __len__(self):
        return len(self.heap)