def colour_graph(graph):
    """
        input    dict of {int: list}
        output:  dict of {int: int}

        Greedy colouring with ordering by degree heurustic for optimisation
        (max degree + 1 is max colours)
    """
    if len(list(graph.keys())) == 0:
        return {}
    deg_sorted = sorted(list(graph.keys()),
                        key=(lambda vertex: len(graph[vertex])),    # sort by degree
                        reverse=True                                # descending
                        )
    max_deg = len(graph[deg_sorted[0]])
    
    colours = {vertex: None for vertex in deg_sorted}

    def _colour_vertex(key: int):
        adj_colours = set([colours[neighbor] for neighbor in graph[key]])
        for i in range(max_deg + 1):
            if i not in adj_colours:
                colours[key] = i
                break
    
    for vertex in deg_sorted:
        _colour_vertex(vertex)

    assert all([colour is not None for colour in colours.values()])

    return colours


if __name__ == '__main__':
    graph = {
        0: [1, 3],
        1: [0, 4],
        2: [3],
        3: [0, 2, 4],
        4: [1, 3],
        5: [6, 7],
        6: [5, 7],
        7: [5, 6]
    }
    print(colour_graph(graph))  # {3: 0, 0: 1, 1: 0, 4: 1, 5: 0, 6: 1, 7: 2, 2: 1}
    
    
