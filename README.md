




https://github.com/user-attachments/assets/5a46c7ae-da08-4705-b7c5-2eaf87c515e5



## **Optimal Public Transport Routing**  

This project focuses on finding optimal routes in a public transportation network using graph-based search algorithms. By leveraging real-world data from Wrocław’s public transit system, it implements and compares different pathfinding strategies to balance travel time and transfer efficiency.  

### **Core Functionality**  

- **Graph Construction**: The dataset is processed to create a transit graph where bus stops are nodes, and routes between them are weighted edges.  
- **Pathfinding Algorithms**:  
  - **Dijkstra’s Algorithm** – Ensures optimal shortest path computation.  
  - **A\*** – Enhances Dijkstra’s method with heuristics to improve efficiency.  
  - **Modified A\*** – Designed for hybrid routing: it either finds **“comfortable” routes** with a low number of transfers while maintaining a good travel time, or it **strictly minimizes the number of transfers**, prioritizing direct connections.  
- **Travel Optimization**: Specialized adaptations of A\* to minimize transfers while maintaining reasonable travel time.  

### **Approach**  

- **Heuristic Design**: The project explores multiple heuristics, including Euclidean distance, Haversine distance, and directional constraints, to refine path selection.  
- **Algorithm Comparisons**: Experimental evaluations assess efficiency, comparing visited nodes, total travel time, and transfer count.  
- **Scalability Considerations**: Methods are tested on large-scale transit data to ensure practical feasibility.  

### **Results**  

The results illustrate different optimization approaches: time-based optimization minimizes total travel duration, transfer-based optimization reduces the number of transfers, and hybrid methods aim to balance both factors. Below are the performance comparisons of the different strategies:  

![alt text](image-1.png)

This project serves as a foundation for optimizing urban mobility, balancing computational efficiency with real-world usability in public transport navigation.
