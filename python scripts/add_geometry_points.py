import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from argparse import ArgumentParser
# import matplotlib.pyplot as plt
# import matplotlib.colors as colors

def add_geometry(csv_file):
    '''
    Calculates the zone of each datapoint/

    :param csv_file: path to csv file with object's x, y coords under columns 'x' and 'y'.
    :return: a geodataframe with the tracked objects' zones.
    
    '''
    # Import .csv file & add a geometry column
    df = pd.read_csv(csv_file)
    if 'x' not in df.columns or 'y' not in df.columns:
        raise TypeError('Make sure the .csv file stores coordinates under columns x and y.')

    df['geometry'] = df.apply(lambda row: Point(row['x'], row['y']), axis=1)


    # Create a geodataframe & set CRS to avoid CRS mismatch issues later
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.crs = 'EPSG:3857'

    return gdf

def locate(gdf, geojson_file):
    '''
    Creates a geodataframe with objects' trajectories and the zones they visit.

    :param gdf: a geodataframe with Points.
    :return: a geodataframe with the tracked objects' locations and the corresponding zones they are in.
    '''

    # Create another geodataframe from the .geoJSON file
    zones = gpd.read_file(geojson_file)

    # Join the geodataframes. The resulting geodataframe has all entries from the trajectories one with an added column, id of the zone it is in, NaN otherwise.
    joined_gdf = gpd.sjoin(gdf, zones[['id','geometry', 'to_inter']], how="left")

    return joined_gdf

# As a script, will unpack all the files passed as command line arguments
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Make .csv file into a geodatafrane with points classified by zones."
    )
    parser.add_argument(
        "input",
        metavar="file.csv",
        type=str,
        help="File to extract trajectories from.",
    )

    parser.add_argument(
        "input_2",
        metavar="file.geojson",
        type=str,
        default="resources/QGIS/main-lanes.geojson",
        help="File to extract zones from.",
    )
    
    args = parser.parse_args()

    gdf = add_geometry(args.input)
    locate(gdf,args.input_2)