from data_structures import *
import heapq
from datetime import timedelta
import heapq
from datetime import datetime
from typing import Callable, List, Dict, Optional, Tuple
import math
from utils import euclidean_distance, haversine_distance
import heapq
from datetime import datetime, timedelta
from typing import Dict, Callable
import math

class RoutePlaner:

    def __init__(self, graph: dict[str, BusStop]):
        self.graph = graph

    def find_earliest_connection(
        self,
        connections: List[Connection], 
        current_time: datetime, 
        previous_line: Optional[str] = None, 
        transfer_time: int = 1, 
        criteria: str = "earliest"
    ) -> Optional['Connection']:
        
        def is_valid_connection(connection):
            required_time = (
                current_time + timedelta(minutes=transfer_time) 
                if previous_line and connection.line != previous_line 
                else current_time
            )
            return connection.departure_time >= required_time

    
        valid_connections = [conn for conn in connections if is_valid_connection(conn)]
        
        if not valid_connections:
            return None

        valid_connections.sort(key=lambda x: x.departure_time)

        if criteria == "no_change":
            same_line_connections = [
                conn for conn in valid_connections 
                if previous_line == conn.line
            ]
            return same_line_connections[0] if same_line_connections else valid_connections[0]
        
        return valid_connections[0]
    

    def dijkstra(self, start_stop: str, end_stop: str, departure_time: str, transfer_time: int = 1):
        if start_stop not in self.graph or end_stop not in self.graph:
            return None, []

        start_time = self.convert_time(departure_time)

        distances = {stop: float('inf') for stop in self.graph}
        previous = {stop: None for stop in self.graph}
        arrival_times = {stop: None for stop in self.graph}
        previous_lines = {stop: None for stop in self.graph}

        distances[start_stop] = 0
        arrival_times[start_stop] = start_time

        priority_queue = [(0, start_stop)]

        visited_nodes = 0
        visited_connections = 0

        while priority_queue:
            current_distance, current_stop = heapq.heappop(priority_queue)

            if current_stop == end_stop:
                break

            if current_distance > distances[current_stop]:
                continue

            visited_nodes += 1 

            current_time = arrival_times[current_stop]
            current_line = previous_lines[current_stop]

            for next_stop, connections in self.graph[current_stop].connections.items():
                visited_connections += 1  

                earliest_conn = self.find_earliest_connection(
                    connections, 
                    current_time, 
                    previous_line=current_line, 
                    transfer_time=transfer_time
                )

                if earliest_conn is None:
                    continue

                travel_time = (earliest_conn.arrival_time - current_time).total_seconds() / 60

                if distances[current_stop] + travel_time < distances[next_stop]:
                    distances[next_stop] = distances[current_stop] + travel_time
                    previous[next_stop] = (current_stop, earliest_conn)
                    arrival_times[next_stop] = earliest_conn.arrival_time
                    previous_lines[next_stop] = earliest_conn.line

                    heapq.heappush(priority_queue, (distances[next_stop], next_stop))

        route = []
        current_stop = end_stop
        while current_stop and previous[current_stop]:
            prev_stop, conn = previous[current_stop]
            route.append(conn)
            current_stop = prev_stop

        route.reverse()

        total_time = distances[end_stop] if distances[end_stop] != float('inf') else None
        return total_time, route

    def print_path(self, total_time, route):
        for conn in route:
            print(f"{conn.line} {conn.departure_time.strftime('%H:%M:%S')} -> {conn.arrival_time.strftime('%H:%M:%S')} {conn.end_stop}")

    def astar(
        self, 
        start_stop: str, 
        end_stop: str, 
        departure_time: str, 
        heuristic_function: Callable[[str, str, Dict[str, BusStop]], float],
        transfer_time: int = 1,
        connection_finder_type: str = "earliest"
    ):
        if start_stop not in self.graph:
            return None, []
        if end_stop not in self.graph:
            return None, []

        
        start_time = self.convert_time(departure_time)

        distances = {stop: float('inf') for stop in self.graph}
        previous = {stop: None for stop in self.graph}
        arrival_times = {stop: None for stop in self.graph}
        previous_lines = {stop: None for stop in self.graph}

        distances[start_stop] = 0
        arrival_times[start_stop] = start_time

        priority_queue = [(0 + heuristic_function(start_stop, end_stop), start_stop)]
        discovered = set()
        visited_nodes = 0
        visited_connections = 0

        while priority_queue:
            current_f_score, current_stop = heapq.heappop(priority_queue)

            if current_stop == end_stop:
                break

            current_h_score = heuristic_function(current_stop, end_stop)
            current_g_score = current_f_score - current_h_score
            
            if current_g_score > distances[current_stop] or current_stop in discovered:
                continue

            visited_nodes += 1
            discovered.add(current_stop)
            current_time = arrival_times[current_stop]
            current_line = previous_lines[current_stop]

            for next_stop, connections in self.graph[current_stop].connections.items():

                visited_connections += 1

                earliest_conn = self.find_earliest_connection(
                    connections=connections, 
                    current_time=current_time, 
                    previous_line=current_line, 
                    transfer_time=transfer_time,
                    criteria=connection_finder_type
                )

                if earliest_conn is None or next_stop in discovered:
                    continue


                travel_time = (earliest_conn.arrival_time - current_time).total_seconds() / 60

                change = False
                if current_line and earliest_conn.line != current_line:
                    change = True

                if distances[current_stop] + travel_time < distances[next_stop]:
                    distances[next_stop] = distances[current_stop] + travel_time
                    previous[next_stop] = (current_stop, earliest_conn)
                    arrival_times[next_stop] = earliest_conn.arrival_time
                    previous_lines[next_stop] = earliest_conn.line

                    next_h_score = heuristic_function(next_stop, end_stop, 
                                                    current_stop=current_stop,
                                                    change=change
                                                    )
                    heapq.heappush(priority_queue, (distances[next_stop] + next_h_score, next_stop))

        if distances[end_stop] == float('inf') or previous[end_stop] is None:
            return None, [], visited_nodes, visited_connections

        route = []
        current_stop = end_stop
        while current_stop and previous[current_stop]:
            prev_stop, conn = previous[current_stop]
            route.append(conn)
            current_stop = prev_stop

        route.reverse()

        total_time = distances[end_stop] if distances[end_stop] != float('inf') else None
        return total_time, route, visited_nodes, visited_connections
    

    def convert_time(self, time_str: str) -> datetime:
        hour = int(time_str[:2])
        if hour >= 24:
            hour -= 24
            return datetime.strptime(f'2025-01-02 {hour:02}{time_str[2:]}', datetime_format)
        else:
            return datetime.strptime(f'2025-01-01 {time_str}', datetime_format)
        

    def zero_heuristic(self, next_stop: str, target_stop: str, change=None, current_stop=None) -> float:
        return 0
    

    def extract_first_connection(self, stop_name: str):
        try:
            for _, connections in self.graph[stop_name].connections.items():
                if connections: 
                    return connections[0]
        except (KeyError, IndexError):
            pass
        return None



    def euclidean_distance_heuristic(self, next_stop: str, target_stop: str, current_stop=None, change=None) -> float:
            first_next_conn = self.extract_first_connection(next_stop)
            first_target_conn = self.extract_first_connection(target_stop)

            if first_next_conn is None or first_target_conn is None:
                return 0
            
            dist = euclidean_distance(
                first_next_conn.start_latitude, first_target_conn.start_latitude,
                first_next_conn.start_longitude, first_target_conn.start_longitude
            )
            
            travel_time_estimate = dist * 111 / 0.4
            return travel_time_estimate * 0.8



    def euclidean_distance_heuristic_2(self, next_stop: str, target_stop: str, current_stop=None, change=None) -> float:
        first_next_conn = self.extract_first_connection(next_stop)
        first_target_conn = self.extract_first_connection(target_stop)
        
        if first_next_conn is None or first_target_conn is None:
            return 0
        
        dist = euclidean_distance(
            first_next_conn.start_latitude, first_target_conn.start_latitude,
            first_next_conn.start_longitude, first_target_conn.start_longitude
        )
        
        travel_time_estimate = dist * 111 / 0.4
        
        if change:
            return travel_time_estimate * 0.5
        else:
            return 0


    def angle_between_heuristic(self, next_stop: str, target_stop: str, current_stop=None, change=None) -> float:
        try:
            if not change:
                return 0

            first_next_conn = self.extract_first_connection(next_stop)
            first_target_conn = self.extract_first_connection(target_stop)
            first_current_conn = self.extract_first_connection(current_stop)

            curr_target_dist = euclidean_distance(first_current_conn.start_latitude, first_target_conn.start_latitude,
                                                first_current_conn.start_longitude, first_target_conn.start_longitude)
            
            curr_next_dist = euclidean_distance(first_current_conn.start_latitude, first_next_conn.start_latitude,
                                                first_current_conn.start_longitude, first_next_conn.start_longitude)
            
            next_target_dist = euclidean_distance(first_target_conn.start_latitude, first_next_conn.start_latitude,
                                                first_target_conn.start_longitude, first_next_conn.start_longitude)
            
            cos = (next_target_dist**2 - curr_target_dist**2 - curr_next_dist**2) / (-2.0 * curr_target_dist * curr_next_dist)

            if cos < 0.5:
                return (2.5 - cos)
            return 0    
        except Exception as e:
            return 0
        
    def haversine_distance_heuristic(
        self,
        next_stop: str, 
        target_stop: str, 
        current_stop: str = None, 
        change: bool = False
        ) -> float:

        first_next_conn = self.extract_first_connection(next_stop)
        first_target_conn = self.extract_first_connection(target_stop)

        if first_next_conn is None or first_target_conn is None:
            return 0

        base_distance = haversine_distance(
            first_next_conn.start_latitude, first_next_conn.start_longitude,
            first_target_conn.start_latitude, first_target_conn.start_longitude
        ) 

        transfer_penalty = 0 if change else 15

        return base_distance + transfer_penalty
        
    def astar_changes(
        self, 
        start_stop: str, 
        end_stop: str, 
        departure_time: str, 
        transfer_time: int = 1,
        ):

        start_time = self.convert_time(departure_time)

        if start_stop not in self.graph or end_stop not in self.graph:
            return None, [], 0, 0

        distances = {stop: float('inf') for stop in self.graph}
        arrival_times = {stop: None for stop in self.graph}
        previous = {stop: None for stop in self.graph}
        previous_lines = {stop: None for stop in self.graph}
        transfer_counts = {stop: 0 for stop in self.graph}

        distances[start_stop] = 0
        arrival_times[start_stop] = start_time   

        priority_queue = [(self.haversine_distance_heuristic(start_stop, end_stop), 0, 0, start_stop)]
        visited_nodes = 0
        visited_connections = 0
        closed_set = set()
        
        while priority_queue:
            _, current_g_score, current_transfer_count, current_stop = heapq.heappop(priority_queue)
            
            if current_stop == end_stop:
                break
            
            if current_stop in closed_set:
                continue
            
            closed_set.add(current_stop)
            visited_nodes += 1
            
            current_time = arrival_times[current_stop]
            current_line = previous_lines[current_stop]
            
            for next_stop, connections in self.graph[current_stop].connections.items():
                if next_stop in closed_set:
                    continue
                
                visited_connections += 1
                
                earliest_conn = self.find_earliest_connection(
                    connections, 
                    current_time, 
                    previous_line=current_line, 
                    transfer_time=transfer_time,
                    criteria="change"
                )
                
                if earliest_conn is None:
                    continue
                
                travel_time = (earliest_conn.arrival_time - current_time).total_seconds() / 60
                
                change = False
                new_transfer_count = current_transfer_count
                if current_line and current_line != earliest_conn.line:
                    change = True
                    new_transfer_count += 1
                
                new_g_score = current_g_score + travel_time + (100 if change else 0)
                
                heuristic_cost = self.haversine_distance_heuristic(next_stop, end_stop, current_stop, change)
                
                
                f_cost = new_g_score + heuristic_cost
                
                if new_g_score < distances[next_stop]:
                    distances[next_stop] = new_g_score
                    previous[next_stop] = (current_stop, earliest_conn)
                    arrival_times[next_stop] = earliest_conn.arrival_time
                    previous_lines[next_stop] = earliest_conn.line
                    transfer_counts[next_stop] = new_transfer_count
                    
                    heapq.heappush(priority_queue, (f_cost, new_g_score, new_transfer_count, next_stop))
            
        
        if distances[end_stop] == float('inf'):
            return None, [], visited_nodes, visited_connections
        
        route = []
        current_stop = end_stop
        while current_stop and previous[current_stop]:
            prev_stop, conn = previous[current_stop]
            route.append(conn)
            current_stop = prev_stop
        route.reverse()
        
        total_time = distances[end_stop] if distances[end_stop] != float('inf') else None
        
        return total_time, route, visited_nodes, visited_connections
    

    def astar_min_transfers(
            self, 
            start_stop: str, 
            end_stop: str, 
            departure_time: str, 
            transfer_time: int = 1,
            ):



            start_time = self.convert_time(departure_time)

            if start_stop not in self.graph or end_stop not in self.graph:
                return None, [], 0, 0


            distances = {}
            arrival_times = {}
            previous = {}
            transfer_counts = {}
            
            distances[(start_stop, None)] = 0
            arrival_times[(start_stop, None)] = start_time   
            previous[(start_stop, None)] = None
            transfer_counts[(start_stop, None)] = 0


            entry_count = 0
            priority_queue = [(0, self.haversine_heuristic(start_stop, end_stop), entry_count, start_stop, None)]
            visited_nodes = 0
            visited_connections = 0
            closed_set = set()  
            
            while priority_queue:
                current_transfer_count, _, _, current_stop, current_line = heapq.heappop(priority_queue)
                
                current_key = (current_stop, current_line)
                
                if current_stop == end_stop:
                    break
                
                if current_key in closed_set:
                    continue
                
                closed_set.add(current_key)
                visited_nodes += 1
                
                current_time = arrival_times[current_key]
                
                for next_stop, connections in self.graph[current_stop].connections.items():
                    visited_connections += 1
                    
                    if current_line:
                        same_line_connections = self.find_same_line_connections(
                            connections, 
                            current_time, 
                            current_line
                        )
                        
                        if same_line_connections:
                            earliest_conn = same_line_connections[0]
                            new_transfer_count = current_transfer_count
                            
                            travel_time = (earliest_conn.arrival_time - current_time).total_seconds() / 60
                            new_key = (next_stop, earliest_conn.line)
                            
                            if new_key not in transfer_counts or new_transfer_count < transfer_counts[new_key]:
                                transfer_counts[new_key] = new_transfer_count
                                distances[new_key] = distances[current_key] + travel_time
                                arrival_times[new_key] = earliest_conn.arrival_time
                                previous[new_key] = (current_key, earliest_conn)
                                
                                heuristic = self.haversine_heuristic(next_stop, end_stop)
                                
                                if new_key not in closed_set:
                                    entry_count += 1
                                    heapq.heappush(priority_queue, (
                                        new_transfer_count, 
                                        heuristic,
                                        entry_count,
                                        next_stop, 
                                        earliest_conn.line
                                    ))
                    
                    all_valid_connections = self.find_valid_connections(
                        connections, 
                        current_time, 
                        current_line, 
                        transfer_time
                    )
                    
                    for conn in all_valid_connections:
                        is_transfer = current_line and conn.line != current_line
                        new_transfer_count = current_transfer_count + (1 if is_transfer else 0)
                        
                        travel_time = (conn.arrival_time - current_time).total_seconds() / 60
                        if is_transfer:
                            travel_time += transfer_time
                        
                        new_key = (next_stop, conn.line)
                        
                        if new_key not in transfer_counts or new_transfer_count < transfer_counts[new_key]:
                            transfer_counts[new_key] = new_transfer_count
                            distances[new_key] = distances[current_key] + travel_time
                            arrival_times[new_key] = conn.arrival_time
                            previous[new_key] = (current_key, conn)
                            
                            heuristic = self.haversine_heuristic(next_stop, end_stop)
                            
                            if new_key not in closed_set:
                                entry_count += 1
                                heapq.heappush(priority_queue, (
                                    new_transfer_count, 
                                    heuristic,
                                    entry_count,
                                    next_stop, 
                                    conn.line
                                ))
            
            best_path = None
            min_transfers = float('inf')
            
            for key, count in transfer_counts.items():
                stop, line = key
                if stop == end_stop and count < min_transfers:
                    min_transfers = count
                    best_path = key
            
            if best_path is None:
                return None, [], visited_nodes, visited_connections
            
            route = []
            current_key = best_path
            
            while current_key and previous.get(current_key):
                prev_key, conn = previous[current_key]
                route.append(conn)
                current_key = prev_key
                
            route.reverse()
            
            total_time = distances.get(best_path, float('inf'))
            if total_time == float('inf'):
                total_time = None
            
            return total_time, route, visited_nodes, visited_connections
    

    def haversine_heuristic(
        self,
        current_stop: str, 
        target_stop: str
    ) -> float:
            first_current_conn = self.extract_first_connection(current_stop)
            first_target_conn = self.extract_first_connection(target_stop)

            if first_current_conn is None or first_target_conn is None:
                return 0

            distance = haversine_distance(
                first_current_conn.start_latitude, first_current_conn.start_longitude,
                first_target_conn.start_latitude, first_target_conn.start_longitude
            )

            return distance

    def find_same_line_connections(
            self,
            connections: List[Connection], 
            current_time: datetime, 
            current_line: str
        ) -> List[Connection]:
            """Znajduje wszystkie połączenia tą samą linią i sortuje je według czasu odjazdu."""
            same_line_connections = [
                conn for conn in connections 
                if conn.line == current_line and conn.departure_time >= current_time
            ]
            return sorted(same_line_connections, key=lambda x: x.departure_time)

    def find_valid_connections(
            self,
            connections: List[Connection], 
            current_time: datetime, 
            current_line: Optional[str] = None, 
            transfer_time: int = 1
        ) -> List[Connection]:
            """Znajduje wszystkie ważne połączenia i sortuje je według czasu odjazdu."""
            valid_connections = []
            
            for conn in connections:
                required_time = current_time
                
                if current_line and conn.line != current_line:
                    required_time += timedelta(minutes=transfer_time)
                    
                if conn.departure_time >= required_time:
                    valid_connections.append(conn)
                    
            return sorted(valid_connections, key=lambda x: x.departure_time)
