from shortest_path import *
from math import ceil
from datetime import datetime, timedelta
from utlis import euclidean_distance, extract_first_connection


def extract_first_connection(self, stop_name: str):
    try:
        for next_stop, connections in self.graph[stop_name].connections.items():
            if connections: 
                return connections[0]
    except (KeyError, IndexError):
        pass
    return None

def initial_solution_nn(graph, start, stops):

    def calculate_distance(stop1, stop2):
        c1 = extract_first_connection(stop1, graph)
        c2 = extract_first_connection(stop2, graph)
        return euclidean_distance(c1.start_latitude, c2.start_latitude, 
                                  c1.start_longitude, c2.start_longitude)
    path = [start]
    unvisited = set(stops) - {start}

    current_stop = start
    while unvisited:
        next_stop = min(unvisited, key=lambda stop: calculate_distance(current_stop, stop))
        path.append(next_stop)
        unvisited.remove(next_stop)
        current_stop = next_stop

    path.append(start)
    cordinates = [(extract_first_connection(x, graph).start_latitude, extract_first_connection(x, graph).start_longitude) for x in path]
    return (path, cordinates)



def evaluate_solution(graph, path, departure_time):
    total_time = 0
    total_route = []

    current_time = datetime.strptime(departure_time, '%H:%M:%S')
    for i in range(len(path) - 1):
        

        connection_time, route = astar(path[i], path[i+1], current_time.strftime('%H:%M:%S'), graph, zero_heuristic)
        total_time += connection_time
        total_route += route
        current_time += timedelta(minutes=connection_time)

    return total_time, total_route
        

def generate_neighbourhood(path):
    neighborhood = set()
    mid_index = ceil(len(path) / 2)
    lower_half = path[:mid_index]
    
    for i in range(1, len(lower_half)):
        similar_solution = path[:]
        temp = similar_solution[len(similar_solution) - 1 - i]
        similar_solution[len(similar_solution) - 1 - i] = lower_half[i]
        similar_solution[i] = temp
        neighborhood.add(tuple(similar_solution))
    
    return [list(sol) for sol in neighborhood]



def tabu_search(graph, start, stops, departure_time):
    current_solution, _ = initial_solution_nn(graph, start, stops)
    best_solution = current_solution
    tabu_list = set()
    best_time, best_route = evaluate_solution(graph, best_solution, departure_time)

    k = 0
    while k < 30:
        i = 0
        while i < 10:
            neighbourhood = generate_neighbourhood(current_solution)
            best_neighbour = None
            best_neighbour_time = float('inf')
            best_neighbour_route = []

            neighbourhood = [neighbour for neighbour in neighbourhood if tuple(neighbour) not in tabu_list]

            for neighbour in neighbourhood:
                total_time, total_route = evaluate_solution(graph, neighbour, departure_time)
                if total_time < best_neighbour_time:
                    best_neighbour_time = total_time
                    best_neighbour = neighbour
                    best_neighbour_route = total_route

            if best_neighbour is None:
                break

            tabu_list.add(tuple(best_neighbour))

            if best_neighbour_time < best_time:
                best_solution = best_neighbour
                best_time = best_neighbour_time
                best_route = best_neighbour_route

            current_solution = best_neighbour

            i += 1
        k += 1
    
    return best_solution, best_time, best_route
       