# SP3TP: Shortest Paths with Turn Penalties

An implementation of an algorithm to find shortest paths with turn penalties and forbidden paths in directed graphs. Based on the paper "A solution approach to districting modification and route optimization in waste collection" by D'Aloisio, Duran, and Faillace Mullen.

## What It Does

SP3TP transforms a weighted directed graph by "exploding" nodes to handle turn penalties and forbidden paths. This allows you to compute shortest paths that consider:

- **Turn penalties**: Costs associated with making specific turns at intersections
- **Forbidden paths**: Sequences of exactly 3 vertices that should not appear in any computed path
- **U-turn restrictions**: Control which nodes allow U-turns

The algorithm uses node transformation combined with Dijkstra's algorithm to efficiently compute shortest penalized paths.

This is particularly useful for route optimization and logistic problems with real-life applications where traffic 
laws forbid certain turns and/or simple routes are needed in order to achieve solutions that are easier to implement. 

## Installation

So far the algorithm is implemented to be used with the popular Python graph library `networkx`. It order to install 
it, simply run:
```bash
pip install networkx
```

Then add `SP3TP_networkx.py` to your project:

```bash
git clone https://github.com/nz-fm/SP3TP.git
cd SP3TP
```

## Quick Start

Here's a simple example of finding shortest paths with turn penalties:

```python
import networkx as nx
from SP3TP_networkx import TransformedDigraph

# Create a directed graph
G = nx.DiGraph()
G.add_edge('A', 'B', weight=10)
G.add_edge('B', 'C', weight=8)
G.add_edge('C', 'D', weight=12)
G.add_edge('A', 'D', weight=25)

# Define a turn penalty function
def my_turn_penalty(u, v, w):
    """Return penalty for turn u->v->w"""
    # Example: penalize right-angle turns
    return 5  # flat penalty for demonstration
    
# Define forbidden paths (if any)
# Maps node v to set of forbidden 3-vertex paths where v is the middle node
forbidden_paths = {}  # Empty for this example

# Transform the graph
T = TransformedDigraph.transform(
    G, 
    forbidden_paths, 
    turn_penalty=my_turn_penalty,
    weight='weight'
)

# Compute shortest penalized paths from node 'A'
costs, paths = T.shortest_penalised_paths('A')

print("Costs:", costs)
print("Paths:", paths)
# Output:
# Costs: {'A': 0, 'B': 10, 'C': 23, 'D': 35}
# Paths: {'A': ['A'], 'B': ['A', 'B'], 'C': ['A', 'B', 'C'], 'D': ['A', 'B', 'C', 'D']}
```

### More advanced example

See [examples/example_1.py](https://github.com/nz-fm/SP3TP/blob/main/examples/example_1.py) for a complete example including:

* Turn penalties based on angles
* Forbidden path constraints
* U-turn allowances at specific nodes
* Visualization of the graph structure (see [examples/example_1_digraph.pdf](https://github.com/nz-fm/SP3TP/blob/main/examples/example_1_digraph.pdf))

Run it with:
```bash
python examples/example_1.py
```

## Usage

### TransformedDigraph.transform()

Transforms a graph to handle turn penalties and forbidden paths:

```python
T = TransformedDigraph.transform(
    G,                  # networkx.DiGraph: original graph
    fpaths,             # dict: forbidden paths by middle node
    turn_penalty,       # function: computes penalty for turn (u,v,w)
    weight,             # str: edge attribute key for weights
    allow_u_turns=None, # None | set: nodes where U-turns allowed
    **kwargs            # additional args passed to turn_penalty function
)
```

### shortest_penalised_paths()

Computes shortest penalized paths from a source node:

```python
costs, paths = T.shortest_penalised_paths(
    source,     # node: starting node
    only_to=None # None | set: restrict destinations (None = all nodes)
)
# Returns:
#   costs: dict mapping nodes to path penalised costs
#   paths: dict mapping nodes to path sequences
```

## How it works

The algorithm transforms the original digraph by:

1. Node Explosion: Each node `v` with in-degree `d` is split into `d+1` nodes:
    * `v_.` represents paths starting at `v`
    * `v_u` represents paths arriving at `v` from predecessor `u`

2. Edge Creation: directed edges are added with costs that include turn penalties

3. Shortest Path Computation: Dijkstra's algorithm finds shortest paths in the transformed digraph

4. Path Reconstruction: Results are mapped back to the original digraph

For detailed algorithm explanation, please refer to 
[this article](https://www.sciencedirect.com/science/article/pii/S1877050925036427).

## Examples

See the [`examples`](https://github.com/nz-fm/SP3TP/tree/main/examples) directory for working examples.

🚧 WIP: More examples yet to come 🚧

## 🚧 Work in progress 🚧

* Add more examples
* Include more functionalities such as all-pair shortest penalised paths.
* Add `networkx`-free implementation.

## License

This implementation is based on the research presented in:

> Camilo D’Aloisio, Guillermo Durán, Nazareno A. Faillace Mullen,
A solution approach to districting modification and route optimization in waste collection,
Procedia Computer Science,
Volume 273,
2025,
Pages 169-176,
ISSN 1877-0509,
https://doi.org/10.1016/j.procs.2025.10.295

Please cite the original paper in your work.