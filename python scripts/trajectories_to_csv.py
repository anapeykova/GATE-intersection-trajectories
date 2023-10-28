"""Decode osef file in from ALB in ITS application and output csv of tracked objects"""
# Standard imports
from argparse import ArgumentParser
from datetime import datetime

# Third party imports
from osef import osef_frame
from osef import types

# Local imports
from alb_output.common.csv_maker import make_csv


def list_tracked_object(frame: dict):
    """Iterator that return tracked objects' trajectories in a frame.
    Can be used as a callback of make_csv to generate a csv file
    with all the tracked objects in a file or stream.

    :param frame: dictionary containing the parsed values of a tlv scan frame.
    :return: a dictionary (raw of the csv) with the tracked objects' trajectories of the lidar.
    """
    tracked_objects = osef_frame.TrackedObjects(frame)

    object_ids = tracked_objects.object_ids
    for i in range(tracked_objects.number_of_objects):
        object_id = object_ids[i]
        coords = tracked_objects.poses[i].translation

        row = {
            "timestamp": datetime.utcfromtimestamp(tracked_objects.timestamp),
            "object_id": object_id,
            "class": tracked_objects.object_classes[i]["class_name"],
            "class_id": tracked_objects.object_classes[i]["class_code"],
            "x": coords[0],
            "y": coords[1],
        }

        yield row


# # As a script, will unpack all the files passed as command line arguments
if __name__ == "__main__":
    parser = ArgumentParser(
        description="Decode osef file in from ALB "
        "in ITS application and output csv of detected objects"
    )
    parser.add_argument(
        "input",
        metavar="file.osef",
        type=str,
        help="File to be decoded. Tcp stream are "
        "accepted on the form of tcp://host:port.",
    )
    parser.add_argument(
        "output",
        metavar="output.csv",
        type=str,
        nargs="?",
        help="Path to csv file to save the output. " "Printed to stdout if omitted.",
    )
    args = parser.parse_args()


    make_csv(args.input, list_tracked_object, args.output)
