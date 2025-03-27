from flask import Flask, request, jsonify
from flask_cors import CORS
from data_structures import *
from shortest_path import * 
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

    print(get_suggestions)
    return jsonify(get_suggestions)


@app.route("/api/shortest_path", methods=["POST"])
def get_shortest_path():
    data = request.get_json()

    source = data.get('source')  
    target = data.get('target')  
    time = data.get('time')  

    if source not in graph or target not in graph or time is None or source == target:
        return jsonify({"error": "Nie znaleziono przystanku"}), 404  

    total_time, route = wroclaw_route_planer.astar(
        start_stop=source,
        end_stop=target,
        departure_time=time,
        heuristic_function=RoutePlaner.angle_between_heuristic 
    )

    connections = []
    for x in route:
        connections.append(x.toDict())

    return jsonify({
        "total_time": total_time,
        "route": connections
    })
   

if __name__ == "__main__":
    app.run(debug=True)


