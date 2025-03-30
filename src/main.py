from flask import Flask, request, jsonify
from flask_cors import CORS
from data_structures import *
from shortest_path import * 
from tsa_solver import *
import requests
import pickle

app = Flask(__name__)
CORS(app)

with open("../mpk_graph.pickle", "rb") as f:
    graph = pickle.load(f)

bus_stop_names = graph.keys()
wroclaw_route_planer = RoutePlaner(graph) 


@app.route("/tasks", methods=["GET"])
def get_tasks():
    if "Iwiny - rondo" not in graph:
        return jsonify({"error": "Brak klucza 'Iwiny - rondo' w danych"}), 404
    return jsonify(graph["Iwiny - rondo"].toDict())


@app.route("/api/suggestions", methods=["GET"])
def get_suggestions():
    query = request.args.get("q", "").strip().lower()

    if not query:
        print("Empty query")
        return jsonify([])
    
    get_suggestions = [name for name in bus_stop_names if query in name.lower()]
    return jsonify(get_suggestions)


@app.route("/api/shortest_path", methods=["POST"])
def get_shortest_path():
    data = request.get_json()

    source = data.get('source')  
    target = data.get('target')  
    time = data.get('time')  
    num_routes = data.get('num_routes', 5)  # Domyślnie 5 tras
    print(source, target, time, num_routes)

    print(source, target, time)

    if source not in graph or target not in graph or time is None or source == target:
        return jsonify({"error": "Nie znaleziono przystanku"}), 404  

    all_routes = []
    current_time = time
    
    # Wykonuj wyszukiwanie kilka razy z przesunięciem czasowym
    for i in range(num_routes):
        print(f"Searching route {i+1} with time {current_time}")
        try:
            total_time, route, _, _ = wroclaw_route_planer.astar(
                start_stop=source,
                end_stop=target,
                departure_time=current_time,
                heuristic_function=wroclaw_route_planer.angle_between_heuristic 
            )
            
            connections = []
            for x in route:
                connections.append(x.toDict())
            
            all_routes.append({
                "total_time": total_time,
                "route": connections
            })
            
            # Przesuń czas o 10 minut dla kolejnego wyszukiwania
            # Zakładamy, że czas jest w formacie "HH:MM:SS"
            h, m, s = map(int, current_time.split(':'))
            m += 10  # Przesunięcie o 10 minut
            if m >= 60:
                h += 1
                m %= 60
            if h >= 24:
                h %= 24
            current_time = f"{h:02d}:{m:02d}:{s:02d}"
            
            print(all_routes)
        except Exception as e:
            print(f"Error finding route {i+1}: {e}")
            # Kontynuuj pętlę mimo błędu
            continue
    
    return jsonify({
        "routes": all_routes
    })

if __name__ == "__main__":
    app.run(debug=True)
    # tsa = TSaSolver(graph)

    # start_station = "Stalowa"
    # #start_station= "KRZYKI"
    # stations_string = "most Grunwaldzki;Kochanowskiego;Wiśniowa;PL. JANA PAWŁA II"
    # #stations_string = "GRABISZYŃSKA (Cmentarz);ZOO;Urząd Wojewódzki (Muzeum Narodowe);most Grunwaldzki;Kochanowskiego;Wiśniowa;PL. JANA PAWŁA II"
    # #stations_string = "GRABISZYŃSKA (Cmentarz);Fiołkowa;FAT;Hutmen;Bzowa (Centrum Historii Zajezdnia)"
    # #stations_string = "Kliniki - Politechnika Wrocławska;BISKUPIN;Stalowa;Krucza;rondo Św. Ojca Pio;most Grunwaldzki;SĘPOLNO"
    # stations_string = "Tarczyński Arena (Lotnicza);Niedźwiedzia;Bujwida;PARK POŁUDNIOWY;Na Niskich Łąkach;BISKUPIN"

    # best_solution, best_time, best_route = tsa.tabu_search(
    #     start=start_station,
    #     stops=stations_string.split(";"),
    #     departure_time='11:25:00'
    # )
    # print("Best solution:", best_solution)
    # print("Best time:", best_time)
    # print("Best route:", best_route)
    # print("Server is running...")


