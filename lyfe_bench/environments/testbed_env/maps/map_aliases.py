import networkx as nx

from lyfe_bench.environments.testbed_env.maps.maps import create_L1_graph

no_place_map = nx.Graph()

example_adj = {
    "Park": {"Garden": {"weight": 2}, "Library": {"weight": 3}},
    "Garden": {"Park": {"weight": 2}, "Library": {"weight": 1}},
    "Library": {"Park": {"weight": 3}, "Garden": {"weight": 1}},
}
example_map = nx.Graph(example_adj)

vertices = [
    ('Park', (-6, -6)),
    ('Garden', (-7, 9)),
    ('Library', (-8, 5)),
    ('Museum', (-10, -9)),
    ('City Hall', (0, -2)),
    ('Community Center', (5, 6)),
    ('Aquarium', (5, 10)),
    ('School', (10, 10)),
    ('Cafe', (4, 6))
]

big_example_map = create_L1_graph(vertices)