# tiff_at_shp

tiff_at_shp is a Python script to sample a TIFF image
at shapefile feature points using fiona and rasterio.

Version 1.0 used for analysis included in the following manuscript:

S. Dufour-Beauséjour, M Bernier, J. Simon, V. Gilbert, J Tuniq, A. Wendleder and A. Roth. (2020) "Snow-covered sea ice in Salluit, Deception Bay, and Kangiqsujuaq: in situ, RADARSAT-2 and TerraSAR-X observations". Manuscript in preparation.

## Usage

```python
import tiff_at_shp

tiff_at_shp.pixel_values(image_path, shapefile_path, results_dir, band_names) # get tiff values at all features in shp
```
## Required packages
fiona  
rasterio  
pandas  

## Contributing
Pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)
