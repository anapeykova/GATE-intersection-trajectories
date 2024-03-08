from argparse import ArgumentParser

import folium
import pandas as pd
import geopandas as gpd
from filter_csv import filter
from classify import classify_trajectory
from collections import Counter
import matplotlib
matplotlib.use('TkAgg')  # Use Tkinter backend
import matplotlib.pyplot as plt


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


    # get start and end timestamps
    df = pd.read_csv(args.input)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    start = df['timestamp'].iloc[0]
    end = df['timestamp'].iloc[-1]

    # # filter and classify trajectories
    gdf = filter(args.input)
    predictions = classify_trajectory(gdf, 100,  'model_weights.h5')
    
    x = dict(Counter(predictions))

    print(f'\n For the period {start} to {end}: \n')
    for i in sorted(x.items()):
        print(f'Path {i[0]}: {i[1]} vehicles detected')   

    means = gpd.read_file("means.geoJSON")

    means['flow'] = means['cluster'].map(x)

    m = folium.Map(location=[42.659395820532694, 23.3165594735582],zoom_start=50,tiles=None)

    # folium.GeoJson(means).add_to(m)
    m = means.explore(column='flow', tooltip='flow', cmap='turbo',zoom_start=50, tiles=None)
    # basemap satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    map_title = f'Traffic flow from {start} till {end}'
    title_html = f'''
                <h3 align="center" style="font-size:20px"><b>{map_title}</b></h3>
                '''
    m.get_root().html.add_child(folium.Element(title_html))
    m.show_in_browser()

