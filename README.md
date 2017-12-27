# Geohash Signature [![CircleCI](https://circleci.com/gh/chasenicholl/geohash-signature/tree/master.svg?style=shield&circle-token=dbc7604505279b5d15f8bf3152bfcf58a27fee17)](https://circleci.com/gh/chasenicholl/geohash-signature/tree/master)

Do you need to know what Geohashes make up a Polygon, or run along a LineString _**fast**_? Generate a **Geohash Signature** from _any_ shape using the `geohash_signature` module!

Supports Python 2.7 and 3.5+ _(but please use 3, come on now people)_

#### _Signatures Visualized_
<img src="/examples/signature-9.jpg" width="250"/> <img src="/examples/signature-10.jpg" width="250"/> <img src="/examples/signature-11.jpg" width="250"/>

## Requirements
- Python >=2.7 (including Python 3.x) (>=3.5 recommended)
- Shapely >= 1.6
- python-geohash >= 0.8.5
- geojson >= 2.3.0

## Installation
```python
python setup.py install
```

## Performance

`within` performances slightly slower then `intersects` because `intersects` uses the fishnet algorithm to chop up the shape so it can be calculated in parallel.

The larger the shape and/or smaller the Geohash Level will result in dramatic performance decreases. The sweet spot tends to be around a signature with a Geohash Level of 10.

#### Results:

Generating a Geohash Signature using the `intersects` method against a Polygon with dimensions of `152.9m x 152.4m` on an 8 core machine

- intersects(POLYGON, 10)
  - 0m1.806s
  - results in 33,540 geohashes

- intersects(POLYGON, 11)
  - 0m26.470s
  - results in 1,052,676 geohashes

- intersects(POLYGON, 12)
  - 19m55.589s
  - results in 33,579,012 geohashes

<img src="/examples/signature-performance.jpg" width="500"/>

## API
### **intersects**(shape, geohash_level=10, compress=False)

### **within**(shape, geohash_level=10, compress=False)

- shape: Shapely Shape or GeoJSON dictionary
- geohash_level: 1-12 [Default: 10]
- compress: True|False [Default: False]

Takes a Shapely Shape or GeoJSON dictionary, and returns a set of Geohashes that **intersect** _or are_ **within**. Defaults to Geohash level of 10. You can also optionally compress the response to its common prefix and components.

### **geohash_feature_collection**(geohashes, save_to=None)

- geohashes: A \<List\> or \<Set\> of Geohashes
- save_to: Optionally write the FeatureCollection to a file.

Helper function to generate a Feature Collection. Takes a \<List\> or \<Set\> of Geohashes are returns them as Feature Collection of Polygons. Optionally you can save that Feature Collection to a file.

### **compress_geohashes**(geohashes)

- geohashes: A \<List\> or \<Set\> of Geohashes

Helper function to compress hashes after the fact. Takes a \<List\> or \<Set\> of Geohashes and returns a tuple (common_prefix, set(parts)).

## Using the Module
```python
import geohash_signature
from shapely.geometry import Polygon

# Create a shapely shape
COORDINATES = [[-73.99603330, 40.73283237],
               [-73.99610310, 40.73287904],
               [-73.99604151, 40.73295838],
               [-73.99596555, 40.73293815],
               [-73.99578489, 40.73290082],
               [-73.99578489, 40.73290082],
               [-73.99576436, 40.73283704],
               [-73.99582184, 40.73275458],
               [-73.99591423, 40.73275147]]
SHAPE = Polygon(COORDINATES)

# OR pass GeoJSON dictionary
# SHAPE = {
#     "type": "Polygon",
#     "coordinates": [COORDINATES]
# }

# Returns a set() of Geohashes
GEOHASHES = geohash_signature.intersects(SHAPE, geohash_level=10)
GEOHASHES_WITHIN = geohash_signature.within(SHAPE, geohash_level=10)
```

Optionally you can compress the Geohash response. `intersects` and `within` have an optional `compress` property, or you can manually compress using `compress_geohashes` method.

This will return the Geohashes in a tuple (common_prefix, {"part", "part", "part"})

i.e. ```("dr5rspj", {"tzg", "tzp", "tzq", "tzr"})```

```python
import geohash_signature
from shapely.geometry import Polygon

# Create a shapely shape
COORDINATES = [[-73.99603330, 40.73283237],
               [-73.99610310, 40.73287904],
               [-73.99604151, 40.73295838],
               [-73.99596555, 40.73293815],
               [-73.99578489, 40.73290082],
               [-73.99578489, 40.73290082],
               [-73.99576436, 40.73283704],
               [-73.99582184, 40.73275458],
               [-73.99591423, 40.73275147]]
SHAPE = Polygon(COORDINATES)

# intersects & within accept an optional compress attribute
PREFIX, COMPONENTS = geohash_signature.intersects(SHAPE,
                                                  geohash_level=10,
                                                  compress=True)

# Or manually compress the results
PREFIX, COMPONENTS = geohash_signature.compress_geohashes(GEOHASHES)
```

## Using the CLI

You can pass GeoJSON as a string or a file path.

```
Usage:
    geohash-signature <geojson>
        [--geohash_level=<level>]
        [--filter=<filter>]
        [--compress]

Options:
    geojson                       Path to GeoJSON file or String. (required)
    --geohash_level=<1-12>        The resolution of the signature. (default: 9)
    --filter=<intersects|within>  Which signature filter to use. (default: intersects)
    --compress                    Compress the results (optional)
```

```
$ geohash-signature /path/to/poly.geojson \
      --geohash_level=10 \
      --filter=intersects \
      --compress
```

## References

[Geohash Levels](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html#_cell_dimensions_at_the_equator "Geohash Levels")

## License

This General Public License does not permit incorporating your program into
proprietary programs.

In simple words, if you are using this **NOT FOR PROFIT**, skies the limit. If you plan to use this in a commerical application, please reach out to me for licensing. Think how MySQL works.
