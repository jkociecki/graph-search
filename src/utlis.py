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


def display_route_statistics(best_solution, best_time, best_route):
    num_transfers = len(set(conn.line for conn in best_route)) - 1
    total_stops = len(best_solution)

    total_time = (best_route[-1].arrival_time - best_route[0].departure_time).total_seconds() / 60  # w minutach
    #print time in hours and minutes
    hours, minutes = divmod(total_time, 60)
    total_time = f"{int(hours)}:{int(minutes):02d}"

    
    print("\nPodsumowanie podróży")
    print("+------------------------+---------+")
    print(f"| {'Parametr':<22}| {'Wartość':<7}|")
    print("+------------------------+---------+")
    print(f"| {'Liczba przesiadek':<22}| {num_transfers:<7}|")
    print(f"| {'Liczba przystanków':<22}| {total_stops:<7}|")
    print(f"| {'Łączny czas podróży':<22}| {total_time:<7} |")
    print("+------------------------+---------+")


import pandas as pd
from datetime import datetime
from collections import defaultdict

def display_route_statistics(best_solution, best_distance, best_route):
    # Group connections by line
    line_groups = []
    current_line = None
    current_group = []
    
    for conn in best_route:
        if current_line is None or conn.line != current_line:
            if current_group:
                line_groups.append(current_group)
            current_group = [conn]
            current_line = conn.line
        else:
            current_group.append(conn)
    
    if current_group:
        line_groups.append(current_group)
    
    # Calculate statistics
    num_transfers = len(line_groups) - 1
    total_stops = len(best_solution)
    
    # Calculate total time
    total_time_minutes = (best_route[-1].arrival_time - best_route[0].departure_time).total_seconds() / 60
    hours, minutes = divmod(total_time_minutes, 60)
    total_time = f"{int(hours)}:{int(minutes):02d}"
    
    # Print summary header
    print(f"\nCałkowity czas podróży: {total_time} ({int(total_time_minutes)} min)")
    print(f"Liczba przesiadek: {num_transfers}")
    print(f"Liczba przystanków: {total_stops}")
    
    # Print route table header
    print("\n" + "+" + "-"*4 + "+" + "-"*9 + "+" + "-"*10 + "+" + "-"*10 + "+" + "-"*30 + "+" + "-"*30 + "+")
    print(f"| {'#':<2} | {'Linia':<7} | {'Start':<8} | {'Koniec':<8} | {'Przystanek początkowy':<28} | {'Przystanek końcowy':<28} |")
    print("+" + "="*4 + "+" + "="*9 + "+" + "="*10 + "+" + "="*10 + "+" + "="*30 + "+" + "="*30 + "+")
    
    # Print each line segment
    for i, group in enumerate(line_groups):
        first_conn = group[0]
        last_conn = group[-1]
        
        line = first_conn.line
        start_time = first_conn.departure_time.strftime("%H:%M:%S")
        end_time = last_conn.arrival_time.strftime("%H:%M:%S")
        start_stop = first_conn.stop_name if hasattr(first_conn, 'stop_name') else group[0].end_stop
        end_stop = last_conn.stop_name if hasattr(last_conn, 'stop_name') else group[-1].end_stop
        
        print(f"| {i:<2} | {line:<7} | {start_time} | {end_time} | {start_stop:<28} | {end_stop:<28} |")
        print("+" + "-"*4 + "+" + "-"*9 + "+" + "-"*10 + "+" + "-"*10 + "+" + "-"*30 + "+" + "-"*30 + "+")
    
    # Optional: Print starting and ending locations
    if best_solution:
        print(f"\nTrasa: {best_solution[0]} → {best_solution[-1]}")