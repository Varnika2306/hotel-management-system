class Graph:
    """Undirected graph for room adjacency"""
    
    def __init__(self):
        self.adjacency_list = {}
    
    def add_vertex(self, room_id):
        if room_id not in self.adjacency_list:
            self.adjacency_list[room_id] = []
    
    def add_edge(self, room1, room2):
        """Add adjacency between rooms"""
        self.add_vertex(room1)
        self.add_vertex(room2)
        if room2 not in self.adjacency_list[room1]:
            self.adjacency_list[room1].append(room2)
        if room1 not in self.adjacency_list[room2]:
            self.adjacency_list[room2].append(room1)
    
    def get_neighbors(self, room_id):
        """Get adjacent rooms"""
        return self.adjacency_list.get(room_id, [])
    
    def find_connected_component(self, start_room, available_rooms):
        """Find connected available rooms (DFS)"""
        visited = set()
        component = []
        
        def dfs(room):
            if room in visited or room not in available_rooms:
                return
            visited.add(room)
            component.append(room)
            for neighbor in self.get_neighbors(room):
                dfs(neighbor)
        
        if start_room in available_rooms:
            dfs(start_room)
        return component