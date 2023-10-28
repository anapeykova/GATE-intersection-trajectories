import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
from argparse import ArgumentParser

def add_geometry(csv_file):
    '''
    Creates a geodataframe with objects' trajectories from a .csv file. Objects must appear more than once or they're dropped.

    :param csv_file: pandas.DataFrame or path to csv file with object's x, y coords under columns 'x' and 'y'.
    :return: a geodataframe with the tracked objects' trajectories as a geometry and index corresponding to the object_id.
    
    '''

    # Import .csv file and check for x and y columns
    if type(csv_file) != pd.core.frame.DataFrame:
        df = pd.read_csv(csv_file)
    else:
        df = csv_file

    if 'x' not in df.columns or 'y' not in df.columns:
        raise TypeError('Make sure the .csv file stores coordinates under columns x and y.')
    
    # Create a geodataframe and set a geometry column
    gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries())

    # Group objects by object_id. LineString needs at least 2 points -> drop all object that appear only once
    for i, group in df.groupby('object_id'):
        if len(group) > 1:
            geometry = LineString([xy for xy in zip(group.x, group.y)])
            gdf.loc[i,'geometry'] = geometry
            gdf.loc[i,'object_id'] = i

    # Set CRS that is the same as the CRS of the zones file. (NOTE: this may not be the real CRS of the trajectories)       
    gdf.crs = 'EPSG:3857'

    return gdf

def locate(gdf, geojson_file):
    '''
    Creates a geodataframe with objects' trajectories and the zones they visit.

    :param gdf: a geodataframe with LineStrings.
    :return: a geodataframe with the tracked objects' trajectories and the corresponding zones they appear in
    '''

    # Create another geodataframe from the .geoJSON file
    zones = gpd.read_file(geojson_file)

    # Join the geodataframes. The resulting geodataframe has all entries from the trajectories one with an added column, id of the zone it is in, NaN otherwise.
    joined_gdf = gpd.sjoin(gdf, zones[['id','geometry']], how="left")
    joined_gdf = joined_gdf.drop(columns=['index_right'])


    return joined_gdf

# As a script, will unpack all the files passed as command line arguments
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Make .csv file into a geodatafrane with LineString classified by zones."
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