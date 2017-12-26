import sys
from geohash_signature import intersects, GeohashSignature

SHAPE = {
    "type": "Polygon",
    "coordinates": [
        [
            [-73.96015129, 40.71760539],
            [-73.96010271, 40.71757684],
            [-73.95967347, 40.71797882],
            [-73.95972105, 40.71800437]
        ]
    ]
}

OUTPUT_FILE = sys.argv[1]
GEOHASHES = intersects(SHAPE, 10)
GeohashSignature.geohash_feature_collection(GEOHASHES, OUTPUT_FILE)
