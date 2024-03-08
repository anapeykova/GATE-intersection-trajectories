from argparse import ArgumentParser

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import tensorflow as tf


def interpolate_gdf(gdf, n):
    '''
    Interpolates shapely.Linestring geometries in a GeoDataFrame.

    :param gdf: geopandas.DataFrame with Linestring geometry column
    :param n: target points for interpolation
    :return: geopandas.DataFrame with Linestring geometry column with n-number of points each.
    '''
    interpolated_trajectories = []
    trajectories = list(gdf['geometry'])

    for trajectory in trajectories:
        interpolated_points = [trajectory.interpolate(i / (n - 1), normalized=True) for i in range(n)]
        interpolated_trajectory = LineString(interpolated_points)
        interpolated_trajectories.append(interpolated_trajectory)

    interpolated_gdf = gpd.GeoDataFrame({'geometry': interpolated_trajectories, 'object_id':gdf['object_id']})

    return interpolated_gdf


def initiate_model(n, weights):
    '''
    Initiates a simple RNN model

    :param n: input dimension
    :param weights: pre-trained weights for the model
    :return: model.
    '''

    seq_length = n
    input_dim = 2 # x and y

    model = tf.keras.Sequential([
        tf.keras.layers.SimpleRNN(10, input_shape=(input_dim, seq_length), activation='relu'),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(11, activation='softmax') 
    ])

    # Compile the model
    model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

    # Load the saved weights
    model.load_weights(weights)

    return model


def classify_trajectory(gdf, n, weights):
    model = initiate_model(n, weights)
    gdf = interpolate_gdf(gdf,n)

    input_data = np.array([gdf['geometry'].iloc[k].xy for k in range(len(gdf))])

    predictions = np.argmax(model.predict(input_data), axis=1)

    return predictions

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Filter complete trajectories from a .csv file with x,y coordinates. Returns a dataframe with shapely.Linestring objects."
    )
    
    parser.add_argument(
        "input",
        metavar="gdf",
        type=gpd.GeoDataFrame,
        help="File to be analyzed.",
    )
    args = parser.parse_args()

    classify_trajectory(args.input)