from collections import defaultdict
from operator import methodcaller
import math

import networkx as nx


class TransformedDigraph(nx.DiGraph):
    """
    Creates a transformed version of a weighted digraph G=(V,A,c). The transformation is carried on by `exploding` each
    node v into d+1 vertices, where d is the in-degree of v. One of these vertices, v_. , represents the case where the
    path starts at v. Let N_in(v) and N_out(v) be the in_neighbourhood and out-neighbourhood of v, respectively.
    Then, for each u in N_in(v), the vertex v_u represents the case where v is visited after visiting u.

    For each v in V, for each w in N_out(v), in the transformed digraph T there is an arc (v_.,w_v) with cost equal to
    that of arc (v,w) in A. Let u,v,w in V such that (u,v) and (v,w) belong to A, then there is an arc
    (v_u, w_v) in T with cost equal to (v,w) plus the penalty of the turn u->v->w.

    This class inherits from networkx.DiGraph and adds the attribute exploded_nodes to map each original node to
    its corresponding nodes in the transformed digraph.
    """


    def __init__(self,incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)
        self._exploded_nodes = {}

    @classmethod
    def transform(cls, G, fpaths, turn_penalty, weight, allow_u_turns=False, dead_ends=None, **kwargs):
        """
        Creates T, the transformation of digraph G by exploding its nodes in such way that any path in T
        represents a unique path in G without forbidden paths. Even more, the cost of a path in T is equal to the
        cost of its represented path in G plus the turn penalties.
        
        Forbidden paths must be sequences of exactly 3 nodes (u,v,w) of V(G).
        
        :param G: digraph to be transformed
        :type G: networkx.DiGraph
        :param fpaths: a dictionary that maps node v to the set of forbidden paths of which v is the second
        node. For instance, if (a,b,c), (d,b,f) and (e,f,g) are the forbidden paths, then fpaths should be
        the dictionary: {b: {(a,b,c), (d,b,f)}, f: (e,f,g)}.
        :type fpaths: dict[int | str: set[tuple[int | str]]]
        :param turn_penalty: a function that determines the turn penalty of a 3-vertex path.
        :type turn_penalty: function
        :param weight: arc weights will be accessed via the edge attribute with this key
        :type weight: str
        :param allow_u_turns: indicates if U-turns are allowed.
        :type allow_u_turns: bool
        :param dead_ends: set of nodes where U-turns are allowed (in case allow_u_turns is False)
        :type dead_ends: None | set[int] | set[str]
        :param kwargs: keyword arguments for turn_penalty function
        :type kwargs: dict
        :return: transformation of digraph G
        :rtype: TransformedDigraph
        """
        
        # Dictionary to map every original node to the its exploded nodes in T
        exploded_nodes = defaultdict(set)

        # Initialize the transformed digraph and add its nodes
        T = cls()
        for n in G.nodes:
            T.add_node(f'{n}_.')
            exploded_nodes[n].add(f'{n}_.')
            for a in G.predecessors(n):
                T.add_node(f'{n}_{a}')
                exploded_nodes[n].add(f'{n}_{a}')

        # Add the arcs with their corresponding weights
        for n in G.nodes:
            for a in G.predecessors(n):
                for m in G.predecessors(a):
                    if ((allow_u_turns or (not allow_u_turns and (m != n or a in dead_ends))) and (m, a, n)
                            not in fpaths.get(a, set())) :
                        T.add_edge(f'{a}_{m}', f'{n}_{a}',
                                             weight=G.edges[a, n][weight] + turn_penalty(m, a, n, **kwargs))
                T.add_edge(f'{a}_.', f'{n}_{a}', cost=G.edges[a, n][weight])

        T._exploded_nodes = exploded_nodes

        return T

    def shortest_penalised_paths(self, source, only_to=None):
        """
        Given a source node s in V(G), this method applies the Dijkstra algorithm in the transformed digraph T to
        calculate a shortest penalised path without forbidden turns (SPPFP) to every other node in V(G) (or to every
        node in the set `only_to`).
        If such path doesn't exist, this method returns an empty path with infinit cost.

        :param source: node of the original digraph to use as source
        :type source: int | str
        :param only_to: set of nodes in V(G) to which the SPPFP is to be calculated. If it is None, the SPPFP to all
        nodes in V(G) are calculated.
        :type only_to: None | set[int] | set[str]
        :return: a dictionary mapping each node to the cost of the SPPFP from source and a dictionary mapping each
        node to the SPPFP from source represented as a sequence of nodes.
        :rtype: tuple[dict[int|str:int|float], dict[int|str:list[int|str]]]
        """
        conv_f = type(source)

        t_cost, t_path = nx.shortest_paths.single_source_dijkstra(self, f'{source}_.', weight='cost')

        cost = {}
        path = {}
        nodes = self._exploded_nodes if only_to is None else only_to
        for u in nodes:
            u_son = min(self._exploded_nodes[u], key=lambda x: t_cost.get(x, math.inf))
            try:
                cost[u] = t_cost[u_son]
                path[u] = [conv_f(n[0]) for n in map(methodcaller('split', '_'), t_path[u_son])]
            except KeyError:  # No existe camino minimo
                cost[u] = math.inf
                path[u] = []

        return cost, path