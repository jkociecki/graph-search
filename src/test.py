from shortest_path import *



from    data_structures import *
from shortest_path import RoutePlaner
from src.utils import *
import pickle
import importlib
import pandas as pd
import os

with open("mpk_graph.pickle", "rb") as f:
    graph = pickle.load(f)

route_planer = RoutePlaner(graph)

start_stop = "Klęka"
end_stop = "Kątna"
time = "12:00:00"


totaltime, route, visited_nodes, visited_connections = route_planer.astar_min_transfers(start_stop=start_stop, 
                                                                          end_stop=end_stop, 
                                                                          departure_time=time)

print(route)
display_results(route=route, totaltime=totaltime, visited_nodes=visited_nodes, visited_connections=visited_connections, start_stop_str=start_stop)