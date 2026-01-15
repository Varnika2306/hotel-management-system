from data_structures.graph import Graph

class AllocationService:
    def __init__(self, booking_service):
        self.booking_service = booking_service
        self.room_graph = Graph()
    
    def build_room_graph(self, rooms):
        """Build adjacency graph"""
        # Group by floor
        floors = {}
        for room in rooms:
            if room.floor not in floors:
                floors[room.floor] = []
            floors[room.floor].append(room)
        
        # Connect adjacent rooms
        for floor_rooms in floors.values():
            floor_rooms.sort(key=lambda r: r.room_number)
            for i in range(len(floor_rooms) - 1):
                self.room_graph.add_edge(floor_rooms[i].room_id, floor_rooms[i+1].room_id)
    
    def allocate_group_booking(self, num_rooms, check_in, check_out, all_rooms):
        """Allocate rooms for group"""
        available = self.booking_service.find_available_rooms(check_in, check_out, all_rooms)
        
        if len(available) < num_rooms:
            return None
        
        available_ids = {room.room_id for room in available}
        
        # Find best connected component
        best_rooms = []
        for room in available:
            component = self.room_graph.find_connected_component(room.room_id, available_ids)
            if len(component) >= num_rooms:
                best_rooms = component[:num_rooms]
                break
        
        if not best_rooms:
            best_rooms = [r.room_id for r in available[:num_rooms]]
        
        return best_rooms