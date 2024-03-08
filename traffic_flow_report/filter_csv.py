from argparse import ArgumentParser
import os

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import Point
from shapely.geometry import LineString


def points(df):
    '''
    Creates a geodataframe with shapely.Point objects from 'x' and 'y' coordinates.

    :param df: pandas.DataFrame with 'x' and 'y' columns
    :return: geopandas dataframe with Point as geometry column.
    '''
    df['geometry'] = df.apply(lambda row: Point(row['x'], row['y']), axis=1)

    # Create a geodataframe & set CRS to avoid CRS mismatch issues later
    # (NOTE: this may not be the real CRS of the trajectories) 
    points_df = gpd.GeoDataFrame(df, geometry='geometry')
    points_df.crs = 'EPSG:3857'
    return points_df

def linestrings(df):
    '''
    Groups data by 'object_id' and creates shapely.Linestring objects in a new geodataframe.

    :param df: pandas.DataFrame with 'object_id', 'x' and 'y' columns
    :return: geopandas dataframe with Linestring as geometry column.
    '''
    linestring_df = gpd.GeoDataFrame(geometry=gpd.GeoSeries())

    for i, group in df.groupby('object_id'):
        geometry = LineString([xy for xy in zip(group.x, group.y)])
        linestring_df.loc[i,'geometry'] = geometry
        linestring_df.loc[i,'object_id'] = i

    # Create a geodataframe & set CRS to avoid CRS mismatch issues later
    # (NOTE: this may not be the real CRS of the trajectories)      
    linestring_df.crs = 'EPSG:3857'
    # print(linestring_df.info())
    return linestring_df

def locate(df, zones="C:/Users/anape/Downloads/outsight/resources/QGIS/lanes_and_int.geojson"):
    gdf = points(df)
    zones = gpd.read_file(zones)

    joined_gdf = gpd.sjoin(gdf, zones[['id','geometry','direction','to_inter']], how="left")

    # print(joined_gdf.info())
    return joined_gdf


def complete_trajectories(gdf):
    complete = []
    for i, group in gdf.groupby('object_id'):
    
    # Filtering out objects tracked for less than 5 seconds, given frame rate = 20 f/s
        if len(group) > 100:

            ids = set(group['id'])
            to_inter = set(group['to_inter'])
            
            # If the object is detected both in lanes coming and leaving the intersection.
            if (0 in ids or 6 in ids) and (1 in to_inter and 0 in to_inter):
                complete.append(i)
                
    return gdf[gdf['object_id'].isin(complete)]


def filter(csv_file):
    df = pd.read_csv(csv_file)
    gdf = locate(df)
    gdf = complete_trajectories(gdf)  
    gdf = linestrings(gdf)

    #print(gdf.info())
    return gdf

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Filter complete trajectories from a .csv file with x,y coordinates. Returns a dataframe with shapely.Linestring objects."
    )
    
    parser.add_argument(
        "input",
        metavar="file.csv",
        type=str,
        help="File to be analyzed.",
    )
    args = parser.parse_args()

    filter(args.input)

