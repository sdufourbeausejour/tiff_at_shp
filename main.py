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
# from this project
import tiff_at_shp

results_dir = "results/"
pairs_path = "pairs.csv"
band_names = ["HH","HV","VH","VV","HH/VV","HH/HV","VV/VH"]
band_index_to_dB = [0, 1, 2, 3]
overwrite = 0 # overwrite result text files or not

# batch over many pairs of files
with open(pairs_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for i, row in enumerate(csv_reader):
        image_path = row["image_path"]
        shapefile_path = row["shapefile_path"]

        # Get pixel values at each shapefile point feature
        # Check if files already there
        save_name = os.path.basename(shapefile_path)[-23] + "_" + os.path.basename(image_path)[4:12] + ".csv"
        if not overwrite and os.path.exists(results_dir+save_name):
            print("pixel values already written to text file: " + save_name)
        else:
            data = tiff_at_shp.pixel_values(image_path, shapefile_path, results_dir,
                                        band_names, band_index_to_dB=band_index_to_dB)
            # Save to txt
            data.to_csv(results_dir+save_name)