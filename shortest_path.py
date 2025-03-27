from data_structures import *
import heapq
from datetime import timedelta
import heapq
from datetime import datetime
from typing import Callable, List, Dict, Optional, Tuple
import math
from utlis import euclidean_distance, haversine_distance
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
        transfer_time: int = 2, 
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

    def dijkstra(self, start_stop: str, end_stop: str, departure_time: str, transfer_time: int = 2):
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
        transfer_time: int = 2,
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

        visited_nodes = 0
        visited_connections = 0

        while priority_queue:
            current_f_score, current_stop = heapq.heappop(priority_queue)

            if current_stop == end_stop:
                break

            current_h_score = heuristic_function(current_stop, end_stop)
            current_g_score = current_f_score - current_h_score
            
            if current_g_score > distances[current_stop]:
                continue

            visited_nodes += 1

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

                if earliest_conn is None:
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
            return None, []

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
            for next_stop, connections in self.graph[stop_name].connections.items():
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
            return travel_time_estimate * 0.2



    def euclidean_distance_heuristic_2(self, next_stop: str, target_stop: str, current_stop=None, change=None) -> float:
        first_next_conn = self.extract_first_connection(next_stop)
        first_target_conn = self.extract_first_connection(target_stop)
        
        if first_next_conn is None or first_target_conn is None:
            return 0
        
        dist = self.euclidean_distance(
            first_next_conn.start_latitude, first_target_conn.start_latitude,
            first_next_conn.start_longitude, first_target_conn.start_longitude
        )
        
        # Konwersja do minut podróży
        # 1 stopień szerokości/długości geograficznej to około 111 km
        # średnia prędkość 30 km/h -> 0.5 km/min
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

        base_distance = haversine_distance(
            first_next_conn.start_latitude, first_next_conn.start_longitude,
            first_target_conn.start_latitude, first_target_conn.start_longitude
        ) 

        transfer_penalty = 0 if change else 15

        return base_distance + transfer_penalty