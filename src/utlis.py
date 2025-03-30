from data_structures import BusStop, Connection
from tabulate import tabulate 
import math
import pandas as pd

def extract_first_connection(graph: dict[str, BusStop], stop_name: str):
    try:
        for next_stop, connections in graph[stop_name].connections.items():
            if connections: 
                return connections[0]
    except (KeyError, IndexError):
        pass
    return None


def euclidean_distance(x1, x2, y1, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c

    return distance


def display_results(route, totaltime, visited_nodes, visited_connections):
    processed_route = []
    current_line = None
    start_time = None
    start_stop_name = None

    for conn in route:
        line, departure, arrival, start_stop, end_stop = (
            conn.line, conn.departure_time, conn.arrival_time, conn.end_stop, conn.end_stop
        )
        
        if line != current_line:
            if current_line is not None:
                processed_route.append((current_line, start_time.strftime('%H:%M:%S'), prev_arrival.strftime('%H:%M:%S'), start_stop_name, prev_stop))
            current_line, start_time, start_stop_name = line, departure, start_stop

        prev_arrival, prev_stop = arrival, end_stop

    if current_line is not None:
        processed_route.append((current_line, start_time.strftime('%H:%M:%S'), prev_arrival.strftime('%H:%M:%S'), start_stop_name, prev_stop))

    df_route = pd.DataFrame(processed_route, columns=["Linia", "Start", "Koniec", "Przystanek początkowy", "Przystanek końcowy"])

    print(f"Całkowity czas podróży: {totaltime} min")
    print(f"Odwiedzone węzły: {visited_nodes}")
    print(f"Odwiedzone połączenia: {visited_connections}")
    print(tabulate(df_route, headers='keys', tablefmt='grid'))
