# -*- coding: utf-8 -*-

# Sophie Dufour-Beauséjour
# s.dufour.beausejour@gmail.com
# Doctorante en sciences de l"eau
# INRS-ETE
# Québec

# Get image band values for pixels overlapping point features from a shapefile.
# The shapefile may include more than one point.
# Images expected in tiff format.
# Requirements: fiona, rasterio
# This file is imported in main.py
# Contents:
# - pixel_values: get pixel values at shp feature coordinates
# - mean_pixel_values: get mean pixel values at shp feature coordinates for box

from __future__ import print_function

import os
import fiona
import rasterio
import numpy as np
import pandas as pd


def pixel_values(image_path, shapefile_path, results_dir, band_names, band_index_to_dB=False, overwrite=0):
    """From a tiff image (path: image_path) and for each point feature in a
    shapefile (path: shapefile_path), return coordinates, field and pixel values (pandas dataframe)
    optional : indices of bands to convert from linear to dB,
    optional : overwrite if file already there"""

    # Open image
    image = rasterio.open(image_path)
    print("Image crs:")
    print(image.crs.wkt)
    if band_index_to_dB:
        names = [band_names[x] for x in band_index_to_dB]
        print("Converting bands " + " ".join(names) + " from linear to dB")

    # Open shapefile
    shapefile = fiona.open(shapefile_path, "r")
    print("Shp crs:")
    print(shapefile.crs_wkt)
    print("There are "+str(len(shapefile))+" data points.")
    field_names = next(shapefile)["properties"].keys()

    data = list()
    column_names = np.concatenate([["long","lat"], field_names, band_names])
    for i,feature in enumerate(shapefile):
        # Read feature field values
        fields = [feature["properties"][f] for f in field_names]
        # Get feature coordinates
        geoms = [feature["geometry"]].pop()
        try:
            lx, ly = geoms["coordinates"]
        except ValueError:
            lx, ly, discard = geoms["coordinates"]

        # Sample src at coordinates
        pixels = next(image.sample([(lx, ly)]))
        if band_index_to_dB:
            for n in band_index_to_dB:
                pixels[n] = 10*np.log10(pixels[n])
        data.append(np.concatenate([[lx, ly], fields, pixels]))

    # Close shapefile and image
    shapefile.close()
    image.close()

    data = pd.DataFrame(data, columns=column_names)
    return data


def mean_pixel_values(image_path, shapefile_path, results_dir, band_names, box, band_index_to_dB=False, overwrite=0):
    """From a tiff image (path: image_path) and for each point feature in a
    shapefile (path: shapefile_path), return coordinates, field and mean pixel
    values in box centered on point features (pandas dataframe)
    optional : indices of bands to convert from linear to dB,
    optional : overwrite if file already there"""

    # Open image
    image = rasterio.open(image_path)
    print("Image crs:")
    print(image.crs.wkt)
    if band_index_to_dB:
        names = [band_names[x] for x in band_index_to_dB]
        print("Converting bands " + " ".join(names) + " from linear to dB")

    # Open shapefile
    shapefile = fiona.open(shapefile_path, "r")
    print("Shp crs:")
    print(shapefile.crs_wkt)
    print("There are "+str(len(shapefile))+" data points.")
    field_names = next(shapefile)["properties"].keys()

    data = list()
    column_names = np.concatenate([["long","lat"], field_names, band_names])
    for i,feature in enumerate(shapefile):
        # Read feature field values
        fields = [feature["properties"][f] for f in field_names]
        # Get feature coordinates
        geoms = [feature["geometry"]].pop()
        try:
            lx, ly = geoms["coordinates"]
        except ValueError:
            lx, ly, discard = geoms["coordinates"]
        # Target box
        half = (box-1)/2
        pix_long_lat = image.index(lx, ly)
        print(pix_long_lat)
        # long / lat is y / x; invert
        top_left_x = pix_long_lat[1]-half
        top_left_y = pix_long_lat[0]-half
        width = box
        height = box
        window = rasterio.windows.Window(top_left_x, top_left_y, width, height)
        pixels = image.read(window=window)
        mean_pixels = [np.mean(x) for x in pixels]
        print(mean_pixels)
        if band_index_to_dB:
            for n in band_index_to_dB:
                mean_pixels[n] = 10*np.log10(mean_pixels[n])
        data.append(np.concatenate([[lx, ly], fields, mean_pixels]))

    # Close shapefile and image
    shapefile.close()
    image.close()

    data = pd.DataFrame(data, columns=column_names)
    return data
