import numpy as np
from math import radians, sin, cos, asin, acos, sqrt
import pandas as pd
import pyproj as proj
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

# [START program]
"""Capacited Vehicles Routing Problem (CVRP)."""


def create_data_model(distance_matrixx, demand_and_location):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_matrixx[0:42][0:42]
    # [START demands_capacities]
    data['demands'] = demand_and_location.demand.astype(int).tolist()[0:42]
    data['vehicle_capacities'] = [128]*40
    # [END demands_capacities]
    data['num_vehicles'] = 40
    data['depot'] = 0
    return data
    # [END data_model]

# [START solution_printer]


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
#     print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
#         print(plan_output)
        total_distance += route_distance
        total_load += route_load
#     print('Total distance of all routes: {}m'.format(total_distance))
#     print('Total load of all routes: {}'.format(total_load))
    return total_distance
    # [END solution_printer]


def get_edges(data, manager, routing, solution):
    """Prints solution on console."""

    route_vehicles = [[0]]*40

    for vehicle_id in range(data['num_vehicles']):

        index = routing.Start(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            if node_index != 0:
                route_vehicles[vehicle_id] = route_vehicles[vehicle_id] + [node_index]

            previous_index = index
            index = solution.Value(routing.NextVar(index))

        manager.IndexToNode(index)

    return route_vehicles


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    # [START data]
    data = create_data_model()
    # [END data]

    # Create the routing index manager.
    # [START index_manager]
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    # [END index_manager]

    # Create Routing Model.
    # [START routing_model]
    routing = pywrapcp.RoutingModel(manager)

    # [END routing_model]

    # Create and register a transit callback.
    # [START transit_callback]
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # [END transit_callback]

    # Define cost of each arc.
    # [START arc_cost]
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # [END arc_cost]

    # Add Capacity constraint.
    # [START capacity_constraint]
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    # [END capacity_constraint]

    # Setting first solution heuristic.
    # [START parameters]
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)
    # [END parameters]

    # Solve the problem.
    # [START solve]
    solution = routing.SolveWithParameters(search_parameters)
    # [END solve]

    # Print solution on console.

    # [START print_solution]
    if solution:

        total_distance = print_solution(data, manager, routing, solution)

        print('----------****---------')

        resul = get_edges(data, manager, routing, solution)

        return resul, total_distance
    else:
        print('bugged')
    # [END print_solution]
