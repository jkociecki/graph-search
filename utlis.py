from data_structures import BusStop, Connection
import math

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