# GeohashSignature [![CircleCI](https://circleci.com/gh/chasenicholl/geohash-signature/tree/master.svg?style=shield&circle-token=dbc7604505279b5d15f8bf3152bfcf58a27fee17)](https://circleci.com/gh/chasenicholl/geohash-signature/tree/master)

Do you need to know what Geohashes make up a Polygon, or run along a LineString _**fast**_? Generate a **Geohash Signature** from _any_ shape using the `geohash_signature` module!

Supports Python 2.7 and 3.5+ _(but please use 3, come on now people)_

Signatures Visualized:

<img src="/examples/signature-9.jpg" width="250" style="display:inline-block;" />
<img src="/examples/signature-10.jpg" width="250" style="display:inline-block;" />
<img src="/examples/signature-11.jpg" width="250" style="display:inline-block;" />

### Requirements
`shapley`, `python-geohash`, `geojson`

### Installation
```python
python setup.py install
```

### Using the Module
```python
import geohash_signature
from geohash_signature import GeohashSignature
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

# Returns a set() of Geohashes
GEOHASHES = geohash_signature.intersects(SHAPE, geohash_level=10)
GEOHASHES_WITHIN = geohash_signature.within(SHAPE, geohash_level=10)

# Optionally you can compress the response using their common prefix.
# (geohash_prefix, (part, part, part))
# ("dr5rspj", {"tzg", "tzp", "tzq", "tzr"})

# intersects & within accept an optional compress attribute
# PREFIX, COMPONENTS = geohash_signature.intersects(SHAPE,
                                                    geohash_level=10,
                                                    compress=True)

# Or manually compress the results
PREFIX, COMPONENTS = GeohashSignature.compress_hashes(GEOHASHES)
```

### Using the CLI

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
