# pylint: disable=E1101
"""
GeohashSignature for generating GeoHash signatures of shapes
"""

from concurrent.futures import ProcessPoolExecutor
import json
import os
import multiprocessing
import geojson
import geohash
import shapely
from shapely.geometry import shape as ShapelyShape


class GeohashSignature:
    """GeohashSignature for generating GeoHash signatures of shapes"""

    def __init__(self):
        """Initiallize the instance with empty members"""
        self._hashes = set()
        self._checked = set()
        self._to_check = set()
        self._workers = multiprocessing.cpu_count()
        self.shape = None
        self.geohash_level = 10
        self.conditions = ['intersects']

    def generate(self, shape, geohash_level=10, conditions=None):
        """Generate Geohash Signature"""
        if 'shapely.geometry' not in str(type(shape)):
            raise TypeError('"encode(<shapely.geometry...>) '
                            'expects a shapely.geometry.<Shape>')

        self.shape = shape
        self.geohash_level = geohash_level
        if conditions is not None:
            self.conditions = conditions

        # Start with the center most Geohash
        start_point = self.representative_point
        ghash = geohash.encode(start_point[1],
                               start_point[0],
                               self.geohash_level)
        self._to_check.add(ghash)

        with ProcessPoolExecutor(max_workers=self._workers) as executor:
            while True:
                check_neighbors = set()
                for ghash in self._to_check:
                    if ghash in self._checked:
                        continue
                    self._checked.add(ghash)
                    for neighbor in geohash.neighbors(ghash):
                        if neighbor in self._to_check:
                            continue
                        check_neighbors.add(neighbor)
                # If none of the neighbors are added stop
                if self.add_hashes(self._to_check, executor) == 0:
                    break
                self._to_check = check_neighbors
        return self._hashes

    def add_hashes(self, hash_set, executor=None):
        """Add hash set to hashes if condition is met"""
        added = 0
        # Single Process
        if executor is None:
            for ghash in hash_set:
                if self.geohash_signature_match(ghash) is True:
                    self._hashes.add(ghash)
                    added = added + 1
            return added

        # Multiprocess
        futures = []
        chunks = self.chunk_set(hash_set, int(len(hash_set) / self._workers))
        for chunk in chunks:
            futures.append(executor.submit(GeohashSignature._condition,
                                           chunk,
                                           self.shape,
                                           self.conditions))
        for future in futures:
            ghashes = future.result()
            added = added + len(ghashes)
            self._hashes.update(ghashes)
        return added

    def geohash_signature_match(self, ghash):
        """Check if Geohash matches configured conditions"""
        polygon = GeohashSignature.geohash_to_polygon(ghash)
        return self.condition(polygon)

    @staticmethod
    def _condition(chunk, shape, conditions):
        """Multiprocessing signature check on chunk"""
        passed = []
        for ghash in chunk:
            polygon = GeohashSignature.geohash_to_polygon(ghash)
            for condition in conditions:
                if condition == 'within':
                    result = getattr(polygon, condition)(shape)
                else:
                    result = getattr(shape, condition)(polygon)
                if result is True:
                    passed.append(ghash)
                    break
        return passed

    def condition(self, polygon):
        """
        Dynamically check conditions
        """
        for condition in self.conditions:
            if condition == 'within':
                result = getattr(polygon, condition)(self.shape)
            else:
                result = getattr(self.shape, condition)(polygon)
            if result is True:
                return True
        return False

    @staticmethod
    def geohash_to_polygon(neighbor):
        """Convert a Geohash to a shapely polygon"""
        bbox = geohash.bbox(neighbor)
        geom = {'coordinates': [[[bbox['w'], bbox['s']],
                                 [bbox['w'], bbox['n']],
                                 [bbox['e'], bbox['n']],
                                 [bbox['e'], bbox['s']]]],
                'type': 'Polygon'}
        return ShapelyShape(geom)

    @staticmethod
    def chunk_set(data_set, size):
        """
        Seperate a list into a list of lists n size
        """
        lst = list(data_set)
        if len(lst) == 1:
            return [data_set]
        if size == 0:
            size = 1
        return [set(lst[x:x+size]) for x in range(0, len(lst), size)]

    @property
    def representative_point(self):
        """Shortcut to Shapely representative_point"""
        return self.shape.representative_point().coords[0]

    @staticmethod
    def geohash_feature_collection(hashes, save_to=None):
        """Method to save geohashes to GeoJSON file"""
        features = []
        for ghash in sorted(hashes):
            bbox = geohash.bbox(ghash)
            coordinates = [[[bbox['w'], bbox['s']],
                            [bbox['w'], bbox['n']],
                            [bbox['e'], bbox['n']],
                            [bbox['e'], bbox['s']]]]
            poly = geojson.Polygon(coordinates)
            features.append(geojson.Feature(geometry=poly))
        feature_collection = geojson.FeatureCollection(features)
        if save_to is None:
            return feature_collection

        if not os.path.exists(os.path.dirname(save_to)):
            os.makedirs(os.path.dirname(save_to))

        with open(save_to, 'w') as file:
            json.dump(feature_collection, file)

    @staticmethod
    def compress_hashes(hashes):
        """Compress hashes to common_prefix:partical,partical"""
        sorted_hashes = sorted(hashes)
        prefix = os.path.commonprefix(sorted_hashes)
        entities = [ghash.replace(prefix, '') for ghash in sorted_hashes]
        return (prefix, set(sorted(entities)))


def intersects(shape, geohash_level=10, compress=False):
    """Return Geohashes at intersect shape"""
    result = GeohashSignature().generate(get_shape(shape),
                                         geohash_level)
    if compress is False:
        return result
    return GeohashSignature.compress_hashes(result)


def within(shape, geohash_level=10, compress=False):
    """Return Geohashes that are within the shape"""
    result = GeohashSignature().generate(get_shape(shape),
                                         geohash_level,
                                         conditions=['within'])
    if compress is False:
        return result
    return GeohashSignature.compress_hashes(result)


def get_shape(shape):
    """Convert GeoJSON to Shapely shape, or pass the shapely shape back"""
    if isinstance(shape, dict) is True:
        shape = ShapelyShape(geojson)
    return shape


def geohash_signature():
    """Access to static methods"""
    return GeohashSignature
