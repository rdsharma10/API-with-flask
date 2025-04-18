from flask import Flask, request, jsonify
import heapq

app = Flask(__name__)

# Warehouse stock data
center_stock = {
    "C1": {"A": 3, "B": 2, "C": 8},
    "C2": {"D": 12, "E": 25, "F": 15},
    "C3": {"G": 0.5, "H": 1, "I": 2}
}

# Graph distances (unit distances)
graph = {
    "C1": {"C2": 4, "C3": 3, "L1": 2},
    "C2": {"C1": 4, "C3": 2.5, "L1": 3},
    "C3": {"C1": 3, "C2": 2.5, "L1": 3},
    "L1": {"C1": 2, "C2": 3, "C3": 3}
}

# Weight cost rules
def cost_per_unit(weight):
    if weight <= 5:
        return 10
    else:
        return 10 * 5 + ((weight - 5 + 4) // 5) * 8

# Find shortest path using Dijkstra’s algorithm
def dijkstra(start, locations):
    heap = [(0, start, [])]
    visited = set()

    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        if all(loc in path for loc in locations + ['L1']):
            return path
        for neighbor, weight in graph.get(node, {}).items():
            if neighbor not in visited:
                heapq.heappush(heap, (cost + weight, neighbor, path))

    return []

# Main calculation
def calculate_cost(start_center, order):
    total_weight = 0
    needed_centers = set()

    for product, qty in order.items():
        found = False
        for center, stock in center_stock.items():
            if product in stock:
                total_weight += stock[product] * qty
                needed_centers.add(center)
                found = True
                break
        if not found:
            return float('inf')  # product not found

    path = dijkstra(start_center, list(needed_centers))
    if not path:
        return float('inf')

    # Calculate total distance
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += graph[path[i]][path[i+1]]

    cost = total_distance * cost_per_unit(total_weight)
    return cost

@app.route('/calculate', methods=['POST'])
def calculate_minimum_cost():
    try:
        order = request.get_json()

        if not order:
            return jsonify({"error": "Invalid or empty request body"}), 400

        min_cost = float('inf')
        best_center = None

        for center in center_stock:
            cost = calculate_cost(center, order)
            if cost < min_cost:
                min_cost = cost
                best_center = center

        return jsonify({
            "minimum_cost": min_cost,
            "starting_center": best_center
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
