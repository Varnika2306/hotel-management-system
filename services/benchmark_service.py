import time
import random
from datetime import datetime, timedelta
from data_structures.interval_tree import IntervalTree, Interval

class BenchmarkService:
    
    @staticmethod
    def naive_search(bookings, query_start, query_end, room_id):
        """Naive O(n) approach - check every booking"""
        overlaps = []
        for booking in bookings:
            if booking['room_id'] == room_id:
                if booking['start'] < query_end and query_start < booking['end']:
                    overlaps.append(booking)
        return overlaps
    
    @staticmethod
    def generate_random_bookings(num_bookings, room_id="R101"):
        """Generate random bookings for testing"""
        bookings = []
        start_date = datetime(2026, 1, 1)
        
        for i in range(num_bookings):
            days_offset = random.randint(0, 365)
            duration = random.randint(1, 7)
            
            check_in = start_date + timedelta(days=days_offset)
            check_out = check_in + timedelta(days=duration)
            
            bookings.append({
                'booking_id': f"BK{i:05d}",
                'room_id': room_id,
                'start': check_in,
                'end': check_out
            })
        
        return bookings
    
    @staticmethod
    def benchmark_interval_tree(bookings, num_queries=100):
        """Benchmark interval tree approach"""
        # Build tree
        tree = IntervalTree()
        
        start_build = time.time()
        for booking in bookings:
            interval = Interval(booking['start'], booking['end'], 
                              booking['booking_id'], booking['room_id'])
            tree.insert(interval)
        build_time = time.time() - start_build
        
        # Test searches
        query_times = []
        for _ in range(num_queries):
            query_start = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 365))
            query_end = query_start + timedelta(days=random.randint(1, 7))
            query = Interval(query_start, query_end, "QUERY", bookings[0]['room_id'])
            
            start_search = time.time()
            overlaps = tree.search_overlaps(query)
            query_times.append(time.time() - start_search)
        
        avg_query_time = sum(query_times) / len(query_times)
        
        return {
            'build_time': build_time,
            'avg_query_time': avg_query_time,
            'total_time': build_time + sum(query_times)
        }
    
    @staticmethod
    def benchmark_naive(bookings, num_queries=100):
        """Benchmark naive O(n) approach"""
        query_times = []
        
        for _ in range(num_queries):
            query_start = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 365))
            query_end = query_start + timedelta(days=random.randint(1, 7))
            
            start_search = time.time()
            overlaps = BenchmarkService.naive_search(bookings, query_start, query_end, bookings[0]['room_id'])
            query_times.append(time.time() - start_search)
        
        avg_query_time = sum(query_times) / len(query_times)
        
        return {
            'build_time': 0,  # No build time for naive
            'avg_query_time': avg_query_time,
            'total_time': sum(query_times)
        }
    
    @staticmethod
    def run_comparison(booking_counts=[100, 500, 1000, 5000, 10000]):
        """Run complete comparison"""
        results = []
        
        for count in booking_counts:
            bookings = BenchmarkService.generate_random_bookings(count)
            
            tree_results = BenchmarkService.benchmark_interval_tree(bookings)
            naive_results = BenchmarkService.benchmark_naive(bookings)
            
            speedup = naive_results['avg_query_time'] / tree_results['avg_query_time']
            
            results.append({
                'count': count,
                'tree': tree_results,
                'naive': naive_results,
                'speedup': speedup
            })
        
        return results