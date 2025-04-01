from datetime import datetime
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
datetime_format = '%Y-%m-%d %H:%M:%S'


class Connection:
    """Class to represent a graph edge - connection between two bus stops"""

    def __init__(self, line, departure_time, arrival_time, start_latitude, start_longitude, end_latitude, end_longitude, end_stop):
        self.line: str = line
        self.departure_time: datetime = departure_time
        self.arrival_time: datetime = arrival_time
        self.start_latitude: float = start_latitude
        self.start_longitude: float = start_longitude
        self.end_latitude: float = end_latitude
        self.end_longitude: float = end_longitude
        self.end_stop: str = end_stop
        
    def __repr__(self):
        return f"Connection({self.line}, {self.departure_time.strftime('%H:%M:%S')} -> {self.arrival_time.strftime('%H:%M:%S')}, {self.end_stop})"


    def toDict(self):
        return {
            'line': self.line,
            'departure_time': self.departure_time.strftime('%H:%M:%S'),
            'arrival_time': self.arrival_time.strftime('%H:%M:%S'),
            'start_latitude': self.start_latitude,
            'start_longitude': self.start_longitude,
            'end_latitude': self.end_latitude,
            'end_longitude': self.end_longitude,
            'end_stop': self.end_stop
        }


class BusStop:
    """Class to represent a graph node - bus stop"""

    def __init__(self, name: str):
        self.name: str = name
        self.connections: dict[str, list[Connection]] = {}

    def add_connection(self, end_stop: str, connection: Connection):
        if end_stop not in self.connections:
            self.connections[end_stop] = [connection]
        else:
            self.connections[end_stop].append(connection)
    
    def __repr__(self):
        return f"BusStop({self.name}, {len(self.connections)} connections)"
    
    def toDict(self):
        return {
            'name': self.name,
            'connections': {k: [x.toDict() for x in v] for k, v in self.connections.items()}
        }


def convert_time(time: str) -> datetime:
    """cleaning and converting time to datetime object"""

    hour = int(time[:2])
    if hour >= 24:
        hour -= 24
        return datetime.strptime(f'2025-01-02 {hour:02}{time[2:]}', datetime_format)
    else:
        return datetime.strptime(f'2025-01-01 {time}', datetime_format)


def add_connection(graph: dict[str, BusStop], start_stop: str,
                   end_stop: str, connection: Connection):
    """adds a connection to a given stop in the graph"""
    
    if start_stop not in graph:
        graph[start_stop] = BusStop(name=start_stop)
    if end_stop not in graph:
        graph[end_stop] = BusStop(name=end_stop)
    graph[start_stop].add_connection(end_stop, connection)


def load_csv_data(filename: str):
    """loading csv data into a graph"""

    df = pd.read_csv(filename)
    graph: dict[str, BusStop] = {}

    for index, row in df.iterrows():
        start_stop = row['start_stop']
        end_stop = row['end_stop']
        departure_time = convert_time(row['departure_time'])
        arrival_time = convert_time(row['arrival_time'])
        start_lat = row['start_stop_lat']
        start_lon = row['start_stop_lon']
        end_lat = row['end_stop_lat']
        end_lon = row['end_stop_lon']
        connection = Connection(
            line=row['line'],
            departure_time=departure_time,
            arrival_time=arrival_time,
            start_latitude=start_lat,
            start_longitude=start_lon,
            end_latitude=end_lat,
            end_longitude=end_lon,
            end_stop=end_stop
        )
        add_connection(graph, start_stop, end_stop, connection)
    
    return graph