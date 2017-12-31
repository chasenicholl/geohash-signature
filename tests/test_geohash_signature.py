# PYTHONPATH=$PYTHONPATH:../ python3 -m unittest discover -p 'test_*.py'
"""Unit tests for geohash_signature Module"""
import unittest
import geohash_signature
import shapely
from shapely.geometry import Polygon, shape as ShapelyShape


class TestGeohashSignature(unittest.TestCase):
    """Unit tests for geohash_signature Module"""

    @classmethod
    def setUpClass(cls):
        super(TestGeohashSignature, cls).setUpClass()
        cls.coords = [[[-73.99603330, 40.73283237],
                       [-73.99610310, 40.73287904],
                       [-73.99604151, 40.73295838],
                       [-73.99596555, 40.73293815],
                       [-73.99578489, 40.73290082],
                       [-73.99578489, 40.73290082],
                       [-73.99576436, 40.73283704],
                       [-73.99582184, 40.73275458],
                       [-73.99591423, 40.73275147]]]
        cls.shape = Polygon(cls.coords[0])

    @classmethod
    def tearDownClass(cls):
        super(TestGeohashSignature, cls).tearDownClass()

    def test_geojson_to_shapely(self):
        """Test that we can create and use a Shapely Shape"""
        geojson = {
            'type': 'Polygon',
            'coordinates': self.coords
        }
        shape = ShapelyShape(geojson)
        self.assertTrue(isinstance(shape, shapely.geometry.Polygon))

        geohashes = geohash_signature.intersects(shape, 10)
        self.assertEqual(len(geohashes),
                         821,
                         'Geohash intersects count not correct')

    def test_intersects(self):
        """Test the intersects method"""
        geohashes = geohash_signature.intersects(self.shape, 11)
        self.assertEqual(len(geohashes),
                         24448,
                         'Geohash intersects count not correct')
        geohashes = geohash_signature.intersects(self.shape, 10)
        self.assertEqual(len(geohashes),
                         821,
                         'Geohash intersects count not correct')

    def test_within(self):
        """Test the within method"""
        geohashes = geohash_signature.within(self.shape, 11)
        self.assertEqual(len(geohashes),
                         23634,
                         'Geohash within count not correct')
        geohashes = geohash_signature.within(self.shape, 10)
        self.assertEqual(len(geohashes),
                         683,
                         'Geohash within count not correct')

    def test_geohash_feature_collection(self):
        """Test creating a Feature Collection from Geohashes"""
        geohashes = geohash_signature.within(self.shape, 10)
        feat_c = geohash_signature.geohash_feature_collection(geohashes)
        self.assertTrue('features' in feat_c)
        self.assertEqual(len(feat_c['features']), 683)

    def test_compress_geohashes(self):
        """Test compressing Geohashes"""
        prefix, components = geohash_signature.within(self.shape,
                                                      10,
                                                      compress=True)
        self.assertEqual(prefix, 'dr5rspj')
        self.assertEqual(len(components), 683)

        geohashes = geohash_signature.within(self.shape, 10)
        prefix, components = geohash_signature.compress_geohashes(geohashes)
        self.assertEqual(prefix, 'dr5rspj')
        self.assertEqual(len(components), 683)

        prefix, components = geohash_signature.intersects(self.shape,
                                                          10,
                                                          compress=True)
        self.assertEqual(prefix, 'dr5rspj')
        self.assertEqual(len(components), 821)

        geohashes = geohash_signature.intersects(self.shape, 10)
        prefix, components = geohash_signature.compress_geohashes(geohashes)
        self.assertEqual(prefix, 'dr5rspj')
        self.assertEqual(len(components), 821)

    def test_get_shape(self):
        """Test creating a Shapely Shape helper method"""
        geojson = {
            'coordinates': self.coords,
            'type': 'Polygon'
        }
        shape = geohash_signature.get_shape(geojson)
        self.assertTrue(isinstance(shape, shapely.geometry.Polygon))
        shape = geohash_signature.get_shape(shape)
        self.assertTrue(isinstance(shape, shapely.geometry.Polygon))
