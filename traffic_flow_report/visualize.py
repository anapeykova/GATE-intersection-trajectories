import os

import geopandas as gdp

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import folium
from folium.plugins import FloatImage

from branca.colormap import linear

color_map = {
        0: 'orange', 1: 'gray', 2: 'magenta', 3: 'goldenrod', 4: 'purple',
        5: 'crimson', 6: 'deepskyblue', 7: 'springgreen', 8: 'lightblue',
        9: 'greenyellow', 10: 'mediumslateblue'
    }

def plot_clusters(gdf, predictions, filename):
    '''
    Visualizes trajectory classifications and saves plot as a file.

    :param gdf: a geopandas.DataFrame
    :param predictions: a list with the same length as gdf; intended to be RNN model output
    :param filename: a path to .png file to save output

    :return: None
    '''
    gdf['cluster'] = predictions
    colors = gdf['cluster'].map(color_map)
    fig, ax = plt.subplots()
    gdf.plot(color = colors, ax = ax)
    ax.axis('off')

    legend_handles = [mpatches.Patch(color = color, label = f'{cluster}') for cluster, color in color_map.items()]
    ax.legend(
        handles = legend_handles,
        loc = 'lower right',
        ncol = 4,
        title = 'RNN paths classification',
        prop = {'size': 12})
    
    fig.tight_layout()
    fig.savefig('output/'+ filename)
    plt.close()

def busiest(gdf, means, direction,filename):
    '''
    Creates a histogram of vehicles per origin/destination direction and a visualization of busiest direction. Saves plot as a file.

    :param gdf: a geopandas.DataFrame
    :param means: model intersection file, geoJSON
    :param direction: str; 'origin' or 'destination'
    :param filename: a path to .png file to save output

    :return: None
    '''
    c = 'deepskyblue' if direction == 'origin' else 'salmon'
    gdf = gdf.merge(means[['cluster', 'origin', 'destination']], on='cluster', how='left')
    
    # 2x2 plot
    fig, axes = plt.subplots(1,2,
                             figsize=(12,6),
                             gridspec_kw={'width_ratios': [1, 2]})

    # first row, by origin street
    flow_sum = means.groupby(direction)['flow'].sum()
    max_val = flow_sum.idxmax()
    ax = axes[0]
    ax.margins()
    cs = [c if category == max_val else 'lightgray' for category in flow_sum.index]
    flow_sum.plot(
        kind='bar',
        color=cs,
        edgecolor='black',
        ax = ax)
    ax.tick_params(axis='x', rotation=10)
    ax.set_title(f'Vehicle counts by street of {direction}')

    ax = axes[1]
    for index, row in gdf.iterrows():
        if row[direction] == max_val:
            color = c
        else:
            color = 'lightgray'
        gdf[gdf.index == index].plot(ax=ax, color=color)
    ax.axis('off')
    ax.set_title(f'Busiest street of {direction}')
    
    ax.text(0, -2, 'Cherni Vruh Blvd N', rotation=45)
    ax.text(-45, -50, 'Cherni Vruh Blvd S', rotation=45)
    ax.text(-50, 0, 'Henrik Ibsen St', rotation=-2)
    ax.text(25, -28, 'Sreburna St', rotation=0)

    fig.tight_layout()
    fig.savefig('output/'+ filename)
    plt.close()


def interactive_map(means,start,end,filename = None):
    '''
    Creates an interactive browser map of vehicles per path. Opens map in browser.

    :param means: model intersection file, geoJSON
    :param start: timestamp, starttime of data sample
    :param end: timestamp, endtime of data sample
    :param filename: a path to .png, to be shown in the bottom left corner of the map

    :return: None
    '''    
    colormap = linear.Reds_07.scale(
        means.flow.min(), means.flow.max()
    )
    colormap.caption = "Vehicle count per path"

    m = folium.Map(location = [42.659395820532694, 23.3165594735582], zoom_start = 50, tiles = None)

    popup = folium.GeoJsonPopup(
        fields=['cluster','flow', 'origin', 'destination'],
        aliases=['Path', 'Count', 'origin street', 'destination street'],
        localize=True,
        labels=True,
    )

    tooltip = folium.GeoJsonTooltip(
        fields=['cluster','flow', 'origin', 'destination'],
        aliases=['Path', 'Count', 'origin street', 'destination street'],
        localize=True,
        sticky=False,
        labels=True,
        style='''
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        ''',
        max_width=800,
    )

    g = folium.GeoJson(
        means,
        style_function=lambda x: {
            'color': colormap(x['properties']['flow']),
            'weight': 7,
        },
        tooltip=tooltip,
        popup=popup,
    ).add_to(m)
    
    # basemap satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    colormap.add_to(m)

    if filename != None:
        url = 'file://' + os.path.abspath(os.path.join('output', filename))
        FloatImage(url, bottom = 5, left = 5, width = '300px').add_to(m)

    map_title = f'Traffic along paths from {start} till {end}'
    title_html = f'''
                <h3 align="center" style="font-size:20px"><b>{map_title}</b></h3>
                '''
    m.get_root().html.add_child(folium.Element(title_html))
    m.save("report_sample_output_map.html")
    m.show_in_browser()