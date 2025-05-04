#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import cv_bridge
import cv2
import numpy
import os
import rosbag
import sys
import tqdm
import argparse


def main():
    parser = argparse.ArgumentParser(description="Process ROS bag files containing sensor_msgs/Image messages.")
    parser.add_argument("bag_files", metavar="BAG_FILE", type=str, nargs="+", help="Path to one or more ROS bag files (.bag) to process.")
    args = parser.parse_args()

    for arg in args.bag_files:
        if not (os.path.isfile(arg) and arg.endswith(".bag")):
            raise Exception(f"{arg} is not a valid bag file.")

    for file in args.bag_files:
        output_path = f"{os.path.abspath(file)[:-4]}"
        os.system(f"mkdir -p {output_path}")

        bag = rosbag.Bag(file)
        topics = [key for (key, value) in bag.get_type_and_topic_info()[1].items() if value[0] == 'sensor_msgs/Image']
        for topic in topics:
            output_subpath = f"{output_path}/{(topic[1:] if topic[0] == '/' else topic).replace('/', '_')}"
            os.system(f"mkdir -p {output_subpath}")
            total_messages = bag.get_message_count(topic)
            progress = tqdm.tqdm(total=bag.get_message_count(topic), desc=f"{file} ({topic})", unit="message", colour="yellow")
            for msg in bag.read_messages(topic):
                progress.update(1)
                bridge = cv_bridge.CvBridge()
                cv_image = bridge.imgmsg_to_cv2(msg.message, msg.message.encoding)
                cv_image.astype(numpy.uint8)
                cv2.imwrite(f"{output_subpath}/{str(msg.timestamp)}.png", cv_image)
        bag.close()


if __name__ == "__main__":
    main()
