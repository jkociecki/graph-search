from flask import Flask, request, jsonify
from flask_cors import CORS
from data_structures import *
from shortest_path import * 
from tsa_solver import *
from utils import *
import requests
import pickle

app = Flask(__name__)
CORS(app)

with open("mpk_graph.pickle", "rb") as f:
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
    num_routes = data.get('num_routes', 5) 
    print(source, target, time, num_routes)

    print(source, target, time)

    if source not in graph or target not in graph or time is None or source == target:
        return jsonify({"error": "Nie znaleziono przystanku"}), 404  

    all_routes = []
    current_time = time
    
    for i in range(num_routes):
        print(f"Searching route {i+1} with time {current_time}")
        try:
            total_time, route, _, _ = wroclaw_route_planer.astar_changes(
                start_stop=source,
                end_stop=target,
                departure_time=current_time
            )

            connections = []
            for x in route:
                connections.append(x.toDict())
            
            all_routes.append({
                "total_time": total_time,
                "route": connections
            })
            
            h, m, s = map(int, current_time.split(':'))
            m += 10  
            if m >= 60:
                h += 1
                m %= 60
            if h >= 24:
                h %= 24
            current_time = f"{h:02d}:{m:02d}:{s:02d}"
            
            print(all_routes)
        except Exception as e:
            print(f"Error finding route {i+1}: {e}")
            continue
    
    return jsonify({
        "routes": all_routes
    })



if __name__ == "__main__":
    app.run(debug=True)