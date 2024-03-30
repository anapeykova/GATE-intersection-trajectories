import os

from argparse import ArgumentParser

import pandas as pd
from datetime import datetime
import geopandas as gpd

from filter_csv import filter
from classify import classify_trajectory
from visualize import plot_clusters, interactive_map
from visualize import busiest

from collections import Counter
import matplotlib
matplotlib.use('TkAgg')  # Use Tkinter backend
import matplotlib.pyplot as plt

from fpdf import FPDF

def pdf_report(start, end, x, filename):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_left_margin(20)
    pdf.set_top_margin(10)
    pdf.set_right_margin(10)

    pdf.set_font('arial', 'B', 12.0)  # Setting font to bold
    pdf.cell(20, 5, txt=f'START: {start}', ln=True)  # Adjusted x-value
    pdf.cell(20, 5, txt=f'END:     {end}', ln=True)  # Adjusted x-value

    # table header
    pdf.ln()
    pdf.cell(20, 10, txt='Path', border=1)  # Adjusted x-value
    pdf.cell(30, 10, txt='Vehicle count', border=1)
    pdf.ln()

    # table rows
    pdf.set_font('arial', '', 10.0)  # Setting the font to regular
    for i in sorted(x.items()):
        pdf.cell(20, 5, txt=str(i[0]), border=1)  # Adjusted x-value
        pdf.cell(30, 5, txt=str(i[1]), border=1)
        pdf.ln(5)

    # visualize clusters next to table
    clusters_url = os.path.join(os.getcwd(), 'output', 'clusters.png')
    pdf.image(clusters_url, x=90, y=5, w=105)  # Adjusted x-value

    # new lines for space
    pdf.ln()
    pdf.ln()

    # busiest origin
    borigin_url = os.path.join(os.getcwd(), 'output', 'busiest_origin.png')
    pdf.image(borigin_url, x=15, y=pdf.get_y(), w=180)  # Adjusted x-value

    pdf.ln()
    pdf.ln()

    # busiest destination
    bdest_url = os.path.join(os.getcwd(), 'output', 'busiest_destination.png')
    pdf.image(bdest_url, x=15, y=pdf.get_y() + 90, w=180)  # Adjusted x-value

    # Output the PDF to a file
    pdf.output(filename, 'F')


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Filters complete vehicle trajectories from source .csv file and classifies them into 11 possible paths. Outputs counts per path and an interactive "
    )
    
    parser.add_argument(
        "input",
        metavar="file.csv",
        type=str,
        help="File to be analyzed.",
    )

    parser.add_argument(
        "--output",
        metavar = "file.pdf",
        type=str,
        default = 'output/report.pdf',
        help = "Path to .pdf file to save report.",
    )

    args = parser.parse_args()

    # Open .csv file as DataFrame
    df = pd.read_csv(args.input)

    # Get start and end timestamps of data sample
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp']
    start = df['timestamp'].iloc[0].strftime('%m.%d.%Y %H:%M:%S')
    end = df['timestamp'].iloc[-1].strftime('%m.%d.%Y %H:%M:%S')

    # Filter and classify trajectories
    gdf = filter(args.input)
    predictions = classify_trajectory(gdf, 100,  'resources/model_weights.h5')

    # Count instances for each path and add values to 'means' (model intersection)
    x = dict(Counter(predictions))
    means = gpd.read_file("resources/means.geoJSON")
    means['flow'] = means['cluster'].map(x)

    # Generate images
    plot_clusters(gdf,predictions,'clusters.png')
    busiest(gdf,means,'origin','busiest_origin.png')
    busiest(gdf,means,'destination','busiest_destination.png')

    # Generate pdf report
    pdf_report(start,end,x, args.output)

    # Generate interactive browser map
    interactive_map(means,start,end,'clusters.png')

