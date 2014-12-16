Catan-Pathfinder
================

A custom implementation of Dijkstra's algorithm to find an optimal path between settlements in Catan using graph theory.

Customized Weights:
Vertex weight assignment involved using a 6 element resource list. Each resource type is assigned an index in the list. For example the first element could be the value for wood on the vertex. The value is the roll number squared. If there are multiple hexagons with the same resource type surrounding one vertex then the value is the square of the sums of their roll values. We did this because we wanted the algorithm to value diversity of resources. 
(x + y)2 > x2 + y2
2 hexagons with the same resource > 2 hexagons with different resources

We have some issues with desert spaces and the borders. We made the sixth index to count these. However, we are not sure what value to put in for this. We ended up just putting in 14 as the value in the desert/water column for each resourceless hexagon. In future work we should look into this more.

To run:
```python src/main.py```

1. Click Start Node
2. Click near a starting node
3. Click End Node
4. Click near a ending node
5. Click Verify Paths to show results of verification method

Red settlements represent chosen settlements. Green settlements represent verification chosen path. Grey settlements represent considered verification paths. 

Selecting start node again will clear the existing drawn objects. 



Modularity:
Algorithms module contains different Dijkstra implementations. 
Evaluation module contains different Evaluation methods for vertices based on resources. 
    Most of the evaluation is now also contained in the algorithms within Dijkstra implementaions. 

view / model modules are simply for constructing and displaying the game board. 