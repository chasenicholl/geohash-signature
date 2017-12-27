# pylint: disable=E1101
"""
GeohashSignature for generating GeoHash signatures of shapes
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import json
import os
import multiprocessing
import geojson
import geohash
import shapely
from shapely.geometry import box, shape as ShapelyShape


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

    def generate_intersect(self, shape, geohash_level=10, conditions=None):
        """Cut up Shape and Generate Geohash Signature in multiple procs"""
        if 'shapely.geometry' not in str(type(shape)):
            raise TypeError('"encode(<shapely.geometry...>) '
                            'expects a shapely.geometry.<Shape>')
        futures = []
        with ProcessPoolExecutor(max_workers=self._workers) as process:
            for part in GeohashSignature.fishnet(shape):
                child = process.submit(GeohashSignature.static_generator,
                                       part,
                                       geohash_level,
                                       conditions)
                futures.append(child)
        for future in futures:
            self._hashes = self._hashes.union(future.result())
        return self._hashes

    @staticmethod
    def static_generator(shape, geohash_level=10, conditions=None):
        """Static generator"""
        instance = GeohashSignature()
        return instance.generate(shape, geohash_level, conditions)

    def generate(self, shape, geohash_level=10, conditions=None):
        """Generate Geohash Signature"""
        if 'shapely.geometry' not in str(type(shape)):
            raise TypeError('"encode(<shapely.geometry...>) '
                            'expects a shapely.geometry.<Shape>')

        self.shape = shape
        self.geohash_level = geohash_level
        if conditions is not None:
            self.conditions = conditions

        # Start with the center of the Shape
        starting_geohashes = [self.representative_point_ghash()]
        # starting_geohashes.extend(self.bounds_geohashes())
        self._to_check.update(starting_geohashes)

        with ProcessPoolExecutor(max_workers=self._workers) as process:
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
                if self.add_hashes(self._to_check, process) == 0:
                    break
                self._to_check = check_neighbors
        return self._hashes

    def add_hashes(self, hash_set, process=None):
        """Add hash set to hashes if condition is met"""
        added = 0
        # Single Process
        if process is None:
            for ghash in hash_set:
                if self.geohash_signature_match(ghash) is True:
                    self._hashes.add(ghash)
                    added = added + 1
            return added

        # Multiprocess
        futures = []
        chunks = self.chunk_set(hash_set, int(len(hash_set) / self._workers))
        for chunk in chunks:
            futures.append(process.submit(GeohashSignature._condition,
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

    def representative_point_ghash(self):
        """Geohash of representative point"""
        start_point = self.representative_point
        return geohash.encode(start_point[1],
                              start_point[0],
                              self.geohash_level)

    def bounds_geohashes(self):
        """Return list of Geohashes of bounds"""
        lon1, lat1, lon2, lat2 = self.shape.bounds
        bounds_ghash1 = geohash.encode(lat1,
                                       lon1,
                                       self.geohash_level)
        bounds_ghash2 = geohash.encode(lat2,
                                       lon2,
                                       self.geohash_level)
        return [bounds_ghash1, bounds_ghash2]

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
    def compress_geohashes(hashes):
        """Compress hashes to common_prefix:partical,partical"""
        sorted_hashes = sorted(hashes)
        prefix = os.path.commonprefix(sorted_hashes)
        entities = [ghash.replace(prefix, '') for ghash in sorted_hashes]
        return (prefix, set(sorted(entities)))

    @staticmethod
    def fishnet(shape, threshold=0.001):
        """Split shape up using the fishnet algo"""
        bounds = shape.bounds
        xmin = int(bounds[0] // threshold)
        xmax = int(bounds[2] // threshold)
        ymin = int(bounds[1] // threshold)
        ymax = int(bounds[3] // threshold)
        # ncols = int(xmax - xmin + 1)
        # nrows = int(ymax - ymin + 1)
        result = []
        for i in range(xmin, xmax+1):
            for j in range(ymin, ymax+1):
                _box = box(i*threshold,
                           j*threshold,
                           (i+1)*threshold,
                           (j+1)*threshold)
                _geom = shape.intersection(_box)
                if _geom.is_empty:
                    continue
                result.append(_geom)
        return result


def intersects(shape, geohash_level=10, compress=False):
    """Return Geohashes at intersect shape"""
    result = GeohashSignature().generate_intersect(get_shape(shape),
                                                   geohash_level)
    if compress is False:
        return result
    return GeohashSignature.compress_geohashes(result)


def within(shape, geohash_level=10, compress=False):
    """Return Geohashes that are within the shape"""
    result = GeohashSignature().generate(get_shape(shape),
                                         geohash_level,
                                         conditions=['within'])
    if compress is False:
        return result
    return GeohashSignature.compress_geohashes(result)


def geohash_feature_collection(hashes, save_to=None):
    """Shortcut to geohash_feature_collection"""
    return GeohashSignature.geohash_feature_collection(hashes, save_to)


def compress_geohashes(hashes):
    """Shortcut to compress_geohashes"""
    return GeohashSignature.compress_geohashes(hashes)


def get_shape(shape):
    """Convert GeoJSON to Shapely shape, or pass the shapely shape back"""
    if isinstance(shape, dict) is True:
        shape = ShapelyShape(shape)
    return shape
