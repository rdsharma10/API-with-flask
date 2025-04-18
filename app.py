from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

# Product info: product -> (center, weight)
product_info = {
    'A': ('C1', 3),
    'B': ('C1', 2),
    'C': ('C1', 8),
    'D': ('C2', 12),
    'E': ('C2', 25),
    'F': ('C2', 15),
    'G': ('C2', 0.5),
    'H': ('C3', 1),
    'I': ('C3', 2),
}

# Distances between centers and L1
distances = {
    ('C1', 'L1'): 3,
    ('C2', 'L1'): 2.5,
    ('C3', 'L1'): 2,
    ('C1', 'C2'): 4,
    ('C1', 'C3'): 3,
    ('C2', 'C3'): 3,
}
# Add reverse distances
for (a, b), d in list(distances.items()):
    distances[(b, a)] = d

# Cost per unit distance function
def cost_per_distance(weight):
    if weight <= 5:
        return 10
    extra = weight - 5
    extra_cost_units = (extra + 4.9999) // 5  # Round up
    return 10 + 8 * int(extra_cost_units)

# Get all centers involved in the current order
def get_centers_from_order(order):
    centers = set()
    for product, qty in order.items():
        if qty > 0:
            center, _ = product_info[product]
            centers.add(center)
    return list(centers)

# Get total weight to deliver from a center
def get_weight_from_center(center, order):
    weight = 0
    for product, qty in order.items():
        if qty > 0 and product_info[product][0] == center:
            weight += product_info[product][1] * qty
    return weight

# Calculate total delivery cost for a route
def calculate_route_cost(route, order):
    total_cost = 0
    carried_items = []

    for i in range(len(route) - 1):
        current = route[i]
        nxt = route[i + 1]

        if current.startswith('C'):
            # Pick up items from this center
            for product, qty in order.items():
                if qty > 0 and product_info[product][0] == current:
                    carried_items += [product_info[product][1]] * qty

        if nxt == 'L1':
            weight = sum(carried_items)
            cost = cost_per_distance(weight)
            total_cost += distances[(current, nxt)] * cost
            carried_items = []  # Drop all at L1
        else:
            # Move without dropping
            weight = sum(carried_items)
            cost = cost_per_distance(weight)
            total_cost += distances[(current, nxt)] * cost

    return total_cost

@app.route('/calculate', methods=['POST'])
def calculate_min_cost():
    order = request.get_json()

    centers_needed = get_centers_from_order(order)
    possible_routes = []

    for start_center in centers_needed:
        # Add L1 once after each center pickup
        rest = [c for c in centers_needed if c != start_center]
        for perm in permutations(rest):
            route = [start_center]
            for c in perm:
                route += ['L1', c]
            route.append('L1')
            possible_routes.append(route)

    min_cost = float('inf')
    for route in possible_routes:
        cost = calculate_route_cost(route, order)
        min_cost = min(min_cost, cost)

    return jsonify({'minimum_cost': round(min_cost)})

if __name__ == '__main__':
    app.run(debug=True)
