from src.shortest_path import *
from math import ceil
from datetime import datetime, timedelta
from src.utils import euclidean_distance, extract_first_connection, display_route_statistics
import pickle


class TSaSolver:

    def __init__(self, graph):
        self.graph = graph
        self.route_solver = RoutePlaner(graph)
            
    def extract_first_connection(self, stop_name: str):
        try:
            for next_stop, connections in self.graph[stop_name].connections.items():
                if connections: 
                    return connections[0]
        except (KeyError, IndexError):
            pass
        return None

    def initial_solution_nn(self, start, stops):
        
        def calculate_distance(stop1, stop2):
            c1 = self.extract_first_connection(stop1)
            c2 = self.extract_first_connection(stop2)
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
        coordinates = [(self.extract_first_connection(x).start_latitude, 
                        self.extract_first_connection(x).start_longitude) 
                        for x in path]
        
        return path, coordinates

    def evaluate_solution(self, path, departure_time):
        total_time = 0
        total_route = []
        current_time = datetime.strptime(departure_time, '%H:%M:%S')
        
        for i in range(len(path) - 1):
            connection_time, route, _, _ = self.route_solver.astar(path[i], 
                                                             path[i+1], 
                                                             current_time.strftime('%H:%M:%S'),
                                                             heuristic_function=self.route_solver.zero_heuristic)

            total_time += connection_time
            total_route += route
            current_time += timedelta(minutes=connection_time)
        
        return total_time, total_route
    
    def calculate_number_of_changes(self, path):
        total_changes = 0
        current_line = None

        for conn in path:
            if conn.line != current_line:
                total_changes += 1
                current_line = conn.line

        return total_changes - 1 if total_changes > 0 else 0
    
    def evaluate_solution_based_on_changes(self, path, departure_time):
        total_changes = 0
        total_route = []
        current_time = datetime.strptime(departure_time, '%H:%M:%S')

        for i in range(len(path) - 1):
            connection_time, route, _, _ = self.route_solver.astar_changes(
                path[i],
                path[i+1],
                current_time.strftime('%H:%M:%S')
            )

            total_changes += self.calculate_number_of_changes(route)
            total_route += route
            current_time += timedelta(minutes=connection_time)

        return total_changes, total_route

            
    def generate_neighbourhood(self, path):
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


    def tabu_search(self, start, stops, departure_time, minimize="time", max_iterations=30, inner_iterations=10):

        current_solution, _ = self.initial_solution_nn(start, stops)
        best_solution = current_solution.copy()
        
        tabu_list = {}
        
        # Dynamiczny rozmiar tablicy tabu zależny od rozmiaru problemu
        tabu_size = len(stops) * 2
        
        if minimize == "time":
            best_cost, best_route = self.evaluate_solution(current_solution, departure_time)
        else:
            best_cost, best_route = self.evaluate_solution_based_on_changes(current_solution, departure_time)
        
        sampling_rate = 1.0
        
        for k in range(max_iterations):
            # Adaptacja strategii próbkowania w zależności od postępu
            if k > max_iterations // 2:
                # W drugiej połowie algorytmu intensyfikujemy przeszukiwanie
                sampling_rate = max(0.3, 1.0 - (k / max_iterations))
            
            for i in range(inner_iterations):
                full_neighbourhood = self.generate_neighbourhood(current_solution)
                
                # Adaptacyjne próbkowanie sąsiedztwa
                import random
                sample_size = max(1, int(len(full_neighbourhood) * sampling_rate))
                neighbourhood = random.sample(full_neighbourhood, min(sample_size, len(full_neighbourhood)))
                
                best_neighbour = None
                best_neighbour_cost = float('inf')
                best_neighbour_route = []
                
                # Aktualizacja listy tabu - usuwanie wygasłych zakazów
                current_iteration = k * inner_iterations + i
                expired_moves = [move for move, expiry in tabu_list.items() if expiry <= current_iteration]
                for move in expired_moves:
                    del tabu_list[move]
                
                # Przeszukiwanie sąsiedztwa
                for neighbour in neighbourhood:
                    neighbour_tuple = tuple(neighbour)
                    
                    is_tabu = neighbour_tuple in tabu_list
                    
                    if minimize == "time":
                        total_cost, total_route = self.evaluate_solution(neighbour, departure_time)
                    else:
                        total_cost, total_route = self.evaluate_solution_based_on_changes(neighbour, departure_time)
                    
                    # Mechanizm aspiracji - akceptujemy rozwiązanie z tabu, jeśli jest lepsze niż globalnie najlepsze
                    if is_tabu and total_cost < best_cost:
                        is_tabu = False
                    
                    if not is_tabu and total_cost < best_neighbour_cost:
                        best_neighbour_cost = total_cost
                        best_neighbour = neighbour
                        best_neighbour_route = total_route
                
                if best_neighbour is None:
                    break
                
                tabu_tenure = random.randint(5, 10)
                tabu_list[tuple(best_neighbour)] = current_iteration + tabu_tenure
                
                if len(tabu_list) > tabu_size:
                    # Usuń najstarszy zakaz
                    oldest_move = min(tabu_list, key=tabu_list.get)
                    del tabu_list[oldest_move]
                
                if best_neighbour_cost < best_cost:
                    best_solution = best_neighbour.copy()
                    best_cost = best_neighbour_cost
                    best_route = best_neighbour_route.copy()
                    
                    sampling_rate = min(1.0, sampling_rate + 0.1)
                else:
                    sampling_rate = max(0.3, sampling_rate - 0.05)
                
                current_solution = best_neighbour.copy()
            
            if k % 10 == 9:
                # Losowo zamieniamy pozycje w bieżącym rozwiązaniu
                solution_copy = current_solution.copy()
                indices = list(range(1, len(solution_copy) - 1))
                if len(indices) >= 2:
                    idx1, idx2 = random.sample(indices, 2)
                    solution_copy[idx1], solution_copy[idx2] = solution_copy[idx2], solution_copy[idx1]
                    current_solution = solution_copy
        
        return best_solution, best_cost, best_route
    

if __name__ == "__main__":
    with open("src/mpk_graph.pickle", "rb") as f:
        graph = pickle.load(f)
    
    tsa_solver = TSaSolver(graph)

    start_station = "Stalowa"
    #start_station= "Jagodzińska"
    #stations_string = "PL. GRUNWALDZKI;KRZYKI"
    #stations_string = "most Grunwaldzki;Kochanowskiego;Wiśniowa;PL. JANA PAWŁA II"
    #stations_string = "GRABISZYŃSKA (Cmentarz);ZOO;Urząd Wojewódzki (Muzeum Narodowe);most Grunwaldzki;Kochanowskiego;Wiśniowa;PL. JANA PAWŁA II"
    #stations_string = "GRABISZYŃSKA (Cmentarz);Fiołkowa;FAT;Hutmen;Bzowa (Centrum Historii Zajezdnia)"
    stations_string = "Kliniki - Politechnika Wrocławska;BISKUPIN;Stalowa;Krucza;rondo Św. Ojca Pio;most Grunwaldzki;SĘPOLNO"
    #stations_string = "Tarczyński Arena (Lotnicza);Niedźwiedzia;Bujwida;PARK POŁUDNIOWY;Na Niskich Łąkach;BISKUPIN"

    best_solution, best_cost, best_route = tsa_solver.tabu_search(start=start_station, 
                                                                stops=stations_string.split(';'), 
                                                                departure_time="12:00:00")
    display_route_statistics(best_solution, best_cost, best_route, start_stop_str=start_station)