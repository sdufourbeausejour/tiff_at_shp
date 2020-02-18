# -*- coding: utf-8 -*-

# Sophie Dufour-Beauséjour
# s.dufour.beausejour@gmail.com
# Université INRS
# Québec, Canada

# Get image band values for pixels overlapping point features from a shapefile.
# The shapefile may include more than one point.
# Images expected in tiff format.
# The shapefile and image should have the same coordinate system, and no projection
# Absolute paths to image and shapefile should be put in pairs.csv (there can be more than one pair of image and shapefile)
# Requirements: fiona, rasterio
# Other files:
# - tiff_at_shp.py
# Input:
# - pairs_path (csv file with pairs of absolute paths image_path and shapefile_path (as column names in uncommented first row)
# - band_names (in the order that they appear in the TIFF files)
# - band_index_to_dB (indices of bands to convert from linear to dB before writing their values in result/)
# - overwrite (True or False to overwrite in results/)

from __future__ import print_function
__author__ = "Sophie Dufour-Beauséjour"

import os
import csv
import numpy as np
import pandas as pd
# from this project
import tiff_at_shp

results_dir = "results/nearest_neighbour/"
pairs_path = "pairs.csv"
band_names = ["HH","HV","VH","VV","HH/VV","HH/HV","VV/VH"]
band_index_to_dB = [0, 1, 2, 3]
overwrite = 0 # overwrite result text files or not
box = 5 # box for spatial mean

# batch over many pairs of files
with open(pairs_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for i, row in enumerate(csv_reader):
        image_path = row["image_path"]
        shapefile_path = row["shapefile_path"]
        if "#" in shapefile_path:
            continue

        # if not "20170416" in image_path:
        #     continue
        # Save name
        preffix = ""
        for s in ["_D_", "_S_", "_K_"]:
            if s in shapefile_path:
                preffix = s[1]+"_"
        suffix = ""
        for s in ["transect_noship", "notransect", "nopolynia", "no_33-34"]:
            if s in shapefile_path:
                suffix = "_" + s
        save_name = os.path.basename(preffix + os.path.basename(image_path)[4:12] + suffix + ".csv")

        # Get pixel values at each shapefile point feature
        # Check if files already there
        if not overwrite and os.path.exists(results_dir+save_name):
            print("pixel values already written to text file: " + save_name)
        else:
            # print("Computing mean in " + str(box) + "x" + str(box) + " box")
            data = tiff_at_shp.pixel_values(image_path, shapefile_path, results_dir,
                                        band_names, band_index_to_dB=band_index_to_dB)
            ## Some data wrangling
            # Replace n/a by nan
            data = data.replace("n/a", np.nan)
            # Remove inf rows
            data = data[data["HH"] != "-inf"]
            data = data[data["HH"] != float("-inf")]
            # Replace ice == 0 by nan
            key_ice = [x for x in data.keys() if "Ice" in x][0]
            data = data.replace({key_ice: 0}, np.nan)
            # Remove track point in D_1704
            if "D_20170419_notransect" in save_name:
                data = data[data[key_ice] != "43.0"]
            # Remove 33-34 from K 1801
            if "K_20180129" in save_name:
                data = data[data["ID_Map"] != "K_33"]
                data = data[data["ID_Map"] != "K_34"]

            # Save to txt with a comment at the end
            data.to_csv(results_dir+save_name)
            with open(results_dir+save_name, 'a') as f:
                # f.write("# Polarimetric parameter values are a mean over a "+str(box)+"x"+str(box)+" box\n")
                f.write("# Image: "+image_path+"\n")
                f.write("# Shp: "+shapefile_path+"\n")
            print(shapefile_path)