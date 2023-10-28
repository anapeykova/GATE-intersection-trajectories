import numpy as np
from scipy.spatial import ConvexHull
import pandas as pd
from argparse import ArgumentParser
import shapely as shp
import matplotlib.pyplot as plt

from datetime import datetime



def traj_features(csv_file, file_name=None):
    '''
    Calculates trajectories features: convex hull volume, displacement, ...

    :param csv_file: path to csv file with object's x, y coords.
    :return: a dataframe with the tracked objects' trajectories' features.
    '''
    # Open input csv and create a new dataframe to store features
    source_df = pd.read_csv(csv_file)


    df = pd.DataFrame()

    # Filter out object which appear for less than 2 sec (given 20 f/s)
    df['object_id'] = source_df['object_id'].unique()
    grouped_data = source_df.groupby('object_id').filter(lambda group: len(group) >= 40)

    for i, group in grouped_data.groupby('object_id'):
#        # Calculate convex hull volume
        # group = group.sample(10)
        traj_points = list(zip(group['x'], group['y']))
        convex = ConvexHull(traj_points)
        df.loc[df['object_id'] == i, 'convex_hull_volume'] = convex.volume # Add results to df


        df.loc[df['object_id'] == i, 'max_speed'] = group['speed_kmh'].max()
        # Calculate displacement
        displ = np.sqrt((traj_points[-1][0]-traj_points[0][0])**2 + (traj_points[-1][1]-traj_points[0][1])**2)
        df.loc[df['object_id'] == i, 'displacement'] = displ # Add results to df

        # Calculate total distance
        group['delta_dist'] = np.sqrt(group['x'].diff()**2 + group['y'].diff()**2)
        df.loc[df['object_id'] == i, 'total_distance'] = group['delta_dist'].sum()

        # Calculate sum curvature (total turning)
        # group['angle'] = np.arctan2(group['y'].diff(), group['x'].diff())
        # df.loc[df['object_id'] == i, 'total_turning'] = group['angle'].sum()

        # On mainroad
        df.loc[df['object_id'] == i, 'start'] = round(shp.points(traj_points[0]))
        df.loc[df['object_id'] == i, 'end'] = round(shp.points(traj_points[-1]))



    df.fillna({'convex_hull_volume': 0, 'displacement': 0}, inplace=True)  # Change NaN values to 0 if any
    df['ratio'] = df['displacement']/df['total_distance']
    if file_name != None:
        df.to_csv(file_name, encoding='utf-8', index=False)
    #print(grouped_data.head())

    return df



# As a script, will unpack all the files passed as command line arguments
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Decode osef file in from ALB "
        "in ITS application and output csv of detected objects"
    )
    parser.add_argument(
        "input",
        metavar="file.csv",
        type=str,
        help="File to extract trajectories from.",
    )
    parser.add_argument(
        "output",
        metavar="output.csv",
        type=str,
        nargs="?",
        help="Path to csv file to save the output. " "Printed to stdout if omitted.",
    )
    args = parser.parse_args()


    traj_features(args.input, args.output)