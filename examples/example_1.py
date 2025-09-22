import math
import networkx as nx
from SP3TP_networkx import TransformedDigraph


def turn_angle(p, q, r):
    """
    Calculates the angle determined by segments (p,q) and (q,r). The resulting angle lies in the interval (-pi,pi]
    :param p: 2-dimensional coordinates
    :type p: list[float | int] | tuple[float | int]
    :param q: 2-dimensional coordinates
    :type q: list[float | int] | tuple[float | int]
    :param r: 2-dimensional coordinates
    :type r: list[float | int] | tuple[float | int]
    :return: angle between segments (p, q) and (q, r)
    :rtype: float
    """

    angle = math.atan2(r[1] - q[1], r[0] - q[0]) - math.atan2(p[1] - q[1], p[0] - q[0])

    # As -pi < atan2(y,x) <= pi, the value of 'angle' lies in the interval (-2*pi, 2*pi].
    # If needed, add or substact 2*pi so it lies in the interval (-pi, pi]

    if angle <= -math.pi:
        angle += 2*math.pi
    elif angle >= math.pi:
        angle -= 2*math.pi

    return angle


def turn_pen_function(u, v, w, node_coords):
    """ Turn penalty function: a flat penalty of 3 is imposed to any turn with an angle greater than 1/5*pi """
    if -math.pi + 1/5*math.pi < turn_angle(node_coords[u], node_coords[v], node_coords[w]) < math.pi - 1/5*math.pi:
        return 3
    return 0


def make_example_digraph():
    G = nx.DiGraph()

    # Adds nodes
    G.add_node('x', coords=(0,0))
    G.add_node('y', coords=(1,0))
    G.add_node('z', coords=(2,0))
    G.add_node('u', coords=(0,1))
    G.add_node('v', coords=(1,1))
    G.add_node('w', coords=(2,1))

    # Adds weighted arcs
    G.add_edge('x', 'y', cost=8)
    G.add_edge('y', 'x', cost=8)
    G.add_edge('z', 'y', cost=8)
    G.add_edge('y', 'z', cost=8)
    G.add_edge('x', 'u', cost=10)
    G.add_edge('u', 'v', cost=8)
    G.add_edge('v', 'w', cost=9)
    G.add_edge('v', 'y', cost=10)
    G.add_edge('w', 'z', cost=10)

    return G


def example_1():

    # Create the digraph of example 1
    G = make_example_digraph()

    # Forbidden paths
    forbidden_paths = {'y': {('v', 'y', 'x')}}

    # Calculate shortests paths using v as source, no U-turns allowed
    T = TransformedDigraph.transform(G, forbidden_paths, turn_pen_function, 'cost', None,
                                     node_coords=nx.get_node_attributes(G,'coords'))
    spp_v = T.shortest_penalised_paths('v')
    print('Shortest penalised paths and their costs from node v. No U-turns allowed.')
    print(spp_v)
    # Calculate shortests paths using x as source, no U-turns allowed
    spp_x = T.shortest_penalised_paths('x')
    print('Shortest penalised paths and their costs from node x. No U-turns allowed.')
    print(spp_x)

    # Calculate shortests paths using v as source, U-turn allowed at z
    T = TransformedDigraph.transform(G, forbidden_paths, turn_pen_function, 'cost', {'z'},
                                     node_coords=nx.get_node_attributes(G,'coords'))
    spp_v = T.shortest_penalised_paths('v')
    print('\nShortest penalised paths and their costs from node v. U-turn allowed at z.')
    print(spp_v)


if __name__ == '__main__':
    example_1()

