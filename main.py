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

# results_dir = "TSX"
# pairs_path = "pairs_TSX_VH_HH.csv"
results_dir = "results/RS2_texture/"
pairs_path = "pairs_RS2.csv"
if "HAa" in results_dir:
    band_names = ["H", "A", "a"]
    band_index_to_dB = 0
    processing_done = "_sub_cal_C3_spk_HAa_TC2"
elif "ratios" in results_dir:
    band_names = ["HH", "HV", "VH", "VV", "VV/HH", "HV/HH", "VH/VV"]
    band_index_to_dB = [0, 1, 2, 3]
    processing_done = "_sub_cal_spk_rat2_TC2"
elif "texture" in results_dir:
    band_names = list()
    for band in ["HH","HV","VV"]:
        for tex in ["HOM","ASM","MEAN","VAR","COR"]:
            band_names.append(tex+"_"+band)
    band_index_to_dB = 0
    processing_done = "_tex2_TC2"
elif "TSX" in results_dir:
    band_names = ["VH"]
    band_index_to_dB = 0

overwrite = 0 # overwrite result text files or not
box = 5 # box for spatial mean

# batch over many pairs of files
with open(pairs_path, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for i, row in enumerate(csv_reader):
        shapefile_path = row["shapefile_path"]
        image_name = os.path.basename(row["image_path"])[0:12]
        image_path = os.path.join(os.path.dirname(row["image_path"]), image_name+processing_done+".tif")
        if "#" in shapefile_path:
            continue

        # if "orbit13"in image_path:
        #     results_dir = "results/TSX_HH_orbit13_5/"
        #     band_names = ["HH"]
        # elif "orbit21" in image_path:
        #     results_dir = "results/TSX_VH_orbit21_5/"
        #     band_names = ["VH"]
        # elif "orbit89" in image_path:
        #     results_dir = "results/TSX_VH_orbit89_5/"
        #     band_names = ["VH"]
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
        if "RS2" in image_path:
            save_name = os.path.basename(preffix + os.path.basename(image_path)[4:12] + suffix + ".csv")
        elif "orbit" in image_path:
            save_name = os.path.basename(preffix + os.path.basename(image_path)[8:16] + suffix + ".csv")

        # Get pixel values at each shapefile point feature
        # Check if files already there
        date = int(os.path.basename(image_path)[4:12])
        # date = int(os.path.basename(image_path)[8:16])
        if not overwrite and os.path.exists(results_dir+save_name):
            print("pixel values already written to text file: " + save_name)
        elif ("orbit21" in image_path) & (date >= 20170502) & (date < 20170911) & ("VV" not in save_name):
            print("No TSX VH orbit21 image for those dates")
            print(save_name)
            print(date)
        else:
            # print("Computing mean in " + str(box) + "x" + str(box) + " box")
            # data = tiff_at_shp.pixel_values(image_path, shapefile_path, results_dir,
            #                             band_names, band_index_to_dB=band_index_to_dB)
            if box:
                data = tiff_at_shp.mean_pixel_values(image_path, shapefile_path, results_dir,
                                                 band_names, box, band_index_to_dB=band_index_to_dB)
            ## Some data wrangling
            # Replace n/a by nan
            data = data.replace("n/a", np.nan)
            if "HH" in results_dir:
                # Remove inf rows
                data = data[data["HH"] != "-inf"]
                data = data[data["HH"] != float("-inf")]
            elif "VH" in results_dir:
                data = data[data["VH"] != "-inf"]
                data = data[data["VH"] != float("-inf")]
            elif "ratios" in results_dir:
                data = data[data["HH"] != "-inf"]
                data = data[data["HH"] != float("-inf")]
            elif "tex" in results_dir:
                data = data[data["MEAN_HH"] != "0.0"]
                data = data[data["MEAN_HH"] != 0]
            elif "HAa" in results_dir:
                data = data[data["H"] != "0.0"]
                data = data[data["H"] != 0]
            # Replace ice == 0 by nan
            key_ice = [x for x in data.keys() if "Ice" in x][0]
            data = data.replace({key_ice: 0}, np.nan)
            data = data.replace({key_ice: "0.0"}, np.nan)
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
                if box:
                    f.write("# Image values are a mean over a "+str(box)+"x"+str(box)+" box\n")
                f.write("# Image: "+image_path+"\n")
                f.write("# Shp: "+shapefile_path+"\n")

            # Also combine the two DB files when transect; notransect comes first in rows
            if "notransect" in shapefile_path:
                save_name = os.path.basename(preffix + os.path.basename(image_path)[4:12] + "_both" + ".csv")
                data.to_csv(results_dir+save_name,header=1)
            if "transect_noship" in shapefile_path:
                save_name = os.path.basename(preffix + os.path.basename(image_path)[4:12] + "_both" + ".csv")
                data.to_csv(results_dir+save_name, mode='a', header=0)
                with open(results_dir+save_name, 'a') as f:
                    if box:
                        f.write("# Image values are a mean over a "+str(box)+"x"+str(box)+" box\n")
                    f.write("# Image: "+image_path+"\n")
                    f.write("# Shp: "+shapefile_path+"\n")
                    f.write("# combined with notransect"+"\n")


