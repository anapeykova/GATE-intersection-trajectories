from argparse import ArgumentParser
#import sys

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


class_map = {
    0: 'UNKNOWN',
    1: 'PERSON',
    2: 'LUGGAGE',
    3: 'TROLLEY',
    4: 'DEPRECATED',
    5: 'TRUCK',
    6: 'CAR',
    7: 'VAN',
    8: 'TWO_WHEELER',
    9: 'MASK',
    10: 'NO_MASK',
    11: 'LANDMARK'}

def csv_preprocess(csv_data):
    '''
    1. Turns 'timestamp' column from str to datetime object
    2. Adds a column to the dataframe, counting the class_id's per unique object_id.
    3. Adds a geometry column and assigns zones
    '''
    df = pd.read_csv(csv_data, dtype={'class_id': int})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['classes_per_id'] = df.groupby('object_id')['class_id'].transform('nunique')

    df['geometry'] = df.apply(lambda row: Point(row['x'], row['y']), axis=1)

    # Create a geodataframe & set CRS to avoid CRS mismatch issues later
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.crs = 'EPSG:3857'

    # Create another geodataframe from the .geoJSON file
    # zones = gpd.read_file("C:/Users/anape/Downloads/outsight/resources/QGIS/main-lanes.geojson")

    # # Join the geodataframes. The resulting geodataframe has all entries from the trajectories one with an added column, id of the zone it is in, NaN otherwise.
    # joined_gdf = gpd.sjoin(gdf, zones[['id','geometry']], how="left")
    # return joined_gdf
    return gdf

def make_object_classes_dict(df):
    '''
    Create a dictionary with object_id as keys and lists of class_id as values.
    '''
    result = {}
    for object_id, group in df.groupby('object_id'):
        result[object_id] = group['class_id'].unique().tolist()
    return result


def df_info(csv_data, to_txt=False):
    df = csv_preprocess(csv_data)

    tdelta = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
    frames = df['frame_number'].iloc[-1] - df['frame_number'].iloc[0] + 1

    # constant objects (where class remains the same throughout)
    const_obj = df[df.classes_per_id == 1].groupby('class')['object_id'].nunique()

    # recognized objects (where class is UNKNOWN and one other)
    rec_df = df[df.classes_per_id == 2]
    rec_dict = make_object_classes_dict(rec_df)
    a = [j for j, v in rec_dict.items() if 0 not in v]
    rec_df.drop(rec_df.loc[rec_df['object_id'].isin(a)].index, inplace=True)
    rec_obj = rec_df[rec_df.class_id != 0].groupby('class')['object_id'].nunique()

    # objects that change class outside of UNKNNOWN
    unident_count = df[df.classes_per_id > 2]['object_id'].nunique() + len(a)

    # zones
    if 'id' in df.columns:
        zones_flow = {}
        for zone, group in df.groupby('id'):
            zones_flow[int(zone)] = group['object_id'].nunique()

    #sys.stdout.write()
    print('FILE OVERVIEW \n ---',
    '\n START:', df['timestamp'].iloc[0],
    '\n END:', df['timestamp'].iloc[-1],
    '\n TIMEDELTA:', tdelta,
    '\n FRAMES:', frames,
    '\n F/S:', (frames/tdelta.total_seconds()).round(), '\n \n')

    print('OBJECT CLASSES OVERVIEW \n ---',
    '\n TRACKED OBJECTS:', df['object_id'].nunique(),
    '\n DETECTED CLASSES:', df['class'].unique(),
    f'\n \n CONSISTENT OBJECTS: {sum(const_obj.values)} \n --- \n',
    const_obj.to_string(),
    f'\n \n RECOGNIZED OBJECTS: {sum(rec_obj.values)} \n --- \n',
    rec_obj.to_string(),
    f'\n \n UNIDENTIFIED OBJECTS: {unident_count} \n \n')

    # print('ZONES OVERVIEW \n ---')
    # for lane, count in zones_flow.items():
    #     print(f'LANE {lane}: {count} objects')



# As a script, will unpack all the files passed as command line arguments
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Analyze a .csv file and output summary of detected objects' class and zones"
    )
    
    parser.add_argument(
        "input",
        metavar="file.csv",
        type=str,
        help=".csv file to be analyzed. The file should contain columns 'x' and 'y' describing the location of the points.",
    )
    args = parser.parse_args()


    df_info(args.input)


