from data_structures import *
import heapq
from datetime import timedelta
import heapq
from datetime import datetime
from typing import Callable, List, Dict, Optional, Tuple
import math

import heapq
from datetime import datetime, timedelta
from typing import Dict, Callable
import math

class RoutePlaner:
    def __init__(self, graph: dict[str, BusStop]):
        self.graph = graph

    def find_earliest_connection(self, connections: list[Connection], 
                                 current_time: datetime, previous_line=None, transfer_time=2
                                 ) -> Connection:
        earliest = None
        earliest_departure = None
        
        for conn in connections:
            required_time = current_time
            if previous_line is not None and conn.line != previous_line:
                required_time = current_time + timedelta(minutes=transfer_time)
            
            if conn.departure_time >= required_time and (earliest is None or conn.departure_time < earliest_departure):
                earliest = conn
                earliest_departure = conn.departure_time
        
        return earliest

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

        print(f"Odwiedzone węzły: {visited_nodes}, odwiedzone krawędzie: {visited_connections}")

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
        print(f"Czas przejazdu: {total_time} min")
        for conn in route:
            print(f"{conn.line} {conn.departure_time.strftime('%H:%M:%S')} -> {conn.arrival_time.strftime('%H:%M:%S')} {conn.end_stop}")

    def astar(
        self, 
        start_stop: str, 
        end_stop: str, 
        departure_time: str, 
        heuristic_function: Callable[[str, str, Dict[str, BusStop]], float],
        transfer_time: int = 2
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

        priority_queue = [(0 + heuristic_function(start_stop, end_stop, self.graph), start_stop)]

        visited_nodes = 0
        visited_connections = 0

        while priority_queue:
            current_f_score, current_stop = heapq.heappop(priority_queue)

            if current_stop == end_stop:
                break

            current_h_score = heuristic_function(current_stop, end_stop, self.graph)
            current_g_score = current_f_score - current_h_score
            
            if current_g_score > distances[current_stop]:
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

                change = False
                if current_line and earliest_conn.line != current_line:
                    change = True

                if distances[current_stop] + travel_time < distances[next_stop]:
                    distances[next_stop] = distances[current_stop] + travel_time
                    previous[next_stop] = (current_stop, earliest_conn)
                    arrival_times[next_stop] = earliest_conn.arrival_time
                    previous_lines[next_stop] = earliest_conn.line

                    next_h_score = heuristic_function(next_stop, end_stop, self.graph, 
                                                    current_stop=current_stop,
                                                    change=change
                                                    )
                    heapq.heappush(priority_queue, (distances[next_stop] + next_h_score, next_stop))

        if distances[end_stop] == float('inf') or previous[end_stop] is None:
            print("Nie znaleziono trasy.")
            return None, []

        route = []
        current_stop = end_stop
        while current_stop and previous[current_stop]:
            prev_stop, conn = previous[current_stop]
            route.append(conn)
            current_stop = prev_stop

        route.reverse()

        total_time = distances[end_stop] if distances[end_stop] != float('inf') else None
        return total_time, route

    def convert_time(self, time_str: str) -> datetime:
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        time_parts = list(map(int, time_str.split(':')))
        
        if len(time_parts) == 2:
            time_parts.append(0)
            
        return today.replace(hour=time_parts[0], minute=time_parts[1], second=time_parts[2])

    def zero_heuristic(self, next_stop: str, target_stop: str, change=None) -> float:
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
        
        dist = self.euclidean_distance(
            first_next_conn.start_latitude, first_target_conn.start_latitude,
            first_next_conn.start_longitude, first_target_conn.start_longitude
        )
        
        # Konwersja do minut podróży
        # 1 stopień szerokości/długości geograficznej to około 111 km
        # średnia prędkość 30 km/h -> 0.5 km/min
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


    @staticmethod
    def angle_between_heuristic(self, next_stop: str, target_stop: str, current_stop=None, change=None) -> float:
        try:
            first_next_conn = self.extract_first_connection(next_stop)
            first_target_conn = self.extract_first_connection(target_stop)
            first_current_conn = self.extract_first_connection(current_stop)

            curr_target_dist = self.euclidean_distance(first_current_conn.start_latitude, first_target_conn.start_latitude,
                                                first_current_conn.start_longitude, first_target_conn.start_longitude)
            
            curr_next_dist = self.euclidean_distance(first_current_conn.start_latitude, first_next_conn.start_latitude,
                                                first_current_conn.start_longitude, first_next_conn.start_longitude)
            
            next_target_dist = self.euclidean_distance(first_target_conn.start_latitude, first_next_conn.start_latitude,
                                                first_target_conn.start_longitude, first_next_conn.start_longitude)
            
            cos = (next_target_dist**2 - curr_target_dist**2 - curr_next_dist**2) / (-2.0 * curr_target_dist * curr_next_dist)

            if change and cos < 0.5:
                return (2.5 - cos)
            return 0    
        except:
            return 0