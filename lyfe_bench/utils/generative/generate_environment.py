"""Code for automatically generate layout of the environment."""
from omegaconf import OmegaConf, DictConfig
import random
from shapely.geometry import Polygon, Point, LineString
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from openai.embeddings_utils import get_embedding

from agent.embedding_utils import match_query_idx
from generative.generate_utils import DATABASEPATH, AGENTCONFIGPATH, UNITYWORLDPATH
from generative.generate_utils import get_resource_embeddings


def generate_street_layout(cfg: DictConfig, village_boundary):
    """Generate the main streets and connecting roads as buildings:"""
    xmin, ymin, xmax, ymax = village_boundary.bounds
    streets = []

    # Create main streets
    main_street_width = cfg.main_street_width
    main_street_spacing = (ymax - ymin) / (cfg.main_streets + 1)
    for i in range(1, cfg.main_streets + 1):
        y = ymin + i * main_street_spacing
        p1 = (xmin, y - main_street_width / 2)
        p2 = (xmin, y + main_street_width / 2)
        p3 = (xmax, y + main_street_width / 2)
        p4 = (xmax, y - main_street_width / 2)
        streets.append(Polygon([p1, p2, p3, p4]))

    # Create connecting roads
    connecting_street_width = cfg.connecting_street_width
    road_spacing = (xmax - xmin) / (cfg.connecting_roads + 1)
    for i in range(1, cfg.connecting_roads + 1):
        x = xmin + i * road_spacing
        p1 = (x - connecting_street_width / 2, ymin)
        p2 = (x + connecting_street_width / 2, ymin)
        p3 = (x + connecting_street_width / 2, ymax)
        p4 = (x - connecting_street_width / 2, ymax)
        streets.append(Polygon([p1, p2, p3, p4]))

    return streets


def generate_buildings(cfg: DictConfig, building_names, street_gpd, village_boundary):
    """Building placements."""
    buildings = []

    for _ in range(len(building_names)):
        building_placed = False

        i_attempt = 0
        while not building_placed:
            i_attempt += 1
            width = cfg.size
            height = cfg.size
            scaling_factor = 0.8  # When smaller than 2, place buildings farther from boundary
            x = random.uniform(village_boundary.bounds[0] + width / scaling_factor,
                               village_boundary.bounds[2] - width / scaling_factor)
            y = random.uniform(village_boundary.bounds[1] + height / scaling_factor,
                               village_boundary.bounds[3] - height / scaling_factor)
            building = Polygon([(x - width / 2, y - height / 2), (x - width / 2, y + height / 2),
                                (x + width / 2, y + height / 2), (x + width / 2, y - height / 2)])

            if (village_boundary.contains(building) and  # # Check if the building is within the village boundary
                    not any(street_gpd.intersects(building).tolist()) and  # not intersecting with any streets
                    not any(building.intersects(b) for b in buildings)):  # not intersecting with any building
                buildings.append(building)
                building_placed = True

            if i_attempt > 100:
                # print('Maximum attempt reached')
                raise ValueError('Maximum attempt reached')

    return buildings


def generate_environment_layout(cfg):
    """Generate environment layout.

    Generate a environment from a basic description of the buildings in the environment
    Outputs a GeoJSON file storing the village information directly to the Unity folder
    Also outputs a copy in the database folder for easier access
    """
    # Create the village boundary
    print(f'Generate {cfg.name} environment layout based on cfg:')
    print(cfg)

    print('Generating environment boundary')
    half_size_x = cfg.area.size_x / 2
    half_size_y = cfg.area.size_y / 2
    village_boundary = Polygon([(-half_size_x, -half_size_y), (-half_size_x, half_size_y),
                                (half_size_x, half_size_y), (half_size_x, -half_size_y)])
    village_gpd = gpd.GeoDataFrame(geometry=[village_boundary])

    # Create streets
    print('Generating street layout')
    streets = generate_street_layout(cfg.streets, village_boundary)
    street_gpd = gpd.GeoDataFrame(geometry=streets)

    # Create buildings
    print('Generating building layout')
    building_names = [list(building_dict.keys())[0] for building_dict in cfg.buildings.list]
    buildings = generate_buildings(cfg.buildings, building_names, street_gpd, village_boundary)
    building_gpd = gpd.GeoDataFrame(geometry=buildings)
    building_gpd['name'] = building_names

    print("Matching building names to prefabs")
    prefab_paths = list()
    resource_df = get_resource_embeddings()
    buildings_df = resource_df[resource_df["type"] == "Buildings"]
    embeddings = list()
    for name in building_names:
        name = name.replace("_", " ")
        query = name
        query_embedding = get_embedding(query, engine="text-embedding-ada-002")
        embeddings.append(query_embedding)
        idx, _ = match_query_idx(buildings_df, query_embedding)
        print(query, buildings_df.iloc[idx]["path"])
        prefab_paths.append(buildings_df.iloc[idx]["path"])

    # Storing the dataframe with the building names (not the prefab names) and their embeddings
    buildings_df = pd.DataFrame(data={"name": building_names, "embedding": embeddings})
    buildings_df.to_csv(DATABASEPATH / f'{cfg.name}_building_embeddings.csv')

    building_gpd["prefab_path"] = prefab_paths

    street_gpd['feature_type'] = 'street'
    building_gpd['feature_type'] = 'building'

    # Add village boundary feature
    village_boundary_gpd = gpd.GeoDataFrame(geometry=[village_boundary])
    village_boundary_gpd['feature_type'] = 'ground'
    village_boundary_gpd['name'] = 'ground'

    village_layout = gpd.GeoDataFrame(pd.concat([street_gpd, building_gpd, village_boundary_gpd], ignore_index=True))

    # save to unity folder
    if not UNITYWORLDPATH.exists():
        UNITYWORLDPATH.mkdir(parents=True, exist_ok=True)
    village_layout.to_file(UNITYWORLDPATH / f"{cfg.name}_layout.geojson", driver='GeoJSON')
    village_layout.to_file(DATABASEPATH / f"{cfg.name}_layout_copy.geojson", driver='GeoJSON')

    # Plot the village layout:
    fig, ax = plt.subplots(figsize=(10, 10))
    village_gpd.boundary.plot(ax=ax, color='k')
    street_gpd.plot(ax=ax, facecolor='grey', edgecolor='grey')
    building_gpd.plot(ax=ax, facecolor='brown', edgecolor='brown')
    plt.savefig(DATABASEPATH / f'{cfg.name}_layout.png', dpi=300, bbox_inches='tight')
