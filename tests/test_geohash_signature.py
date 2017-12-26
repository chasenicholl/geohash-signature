# PYTHONPATH=$PYTHONPATH:../ python3 -m unittest discover -p 'test_*.py'
"""Unit tests for geohash_signature Module"""
import unittest
from geohash_signature import intersects, within
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
        geojson = {
            'type': 'Polygon',
            'coordinates': self.coords
        }
        shape = ShapelyShape(geojson)
        self.assertTrue(isinstance(shape, shapely.geometry.Polygon))

        geohashes = intersects(shape, 10)
        self.assertEqual(len(geohashes),
                         821,
                         'Geohash intersects count not correct')

    def test_intersects(self):
        geohashes = intersects(self.shape, 11)
        self.assertEqual(len(geohashes),
                         24448,
                         'Geohash intersects count not correct')
        geohashes = intersects(self.shape, 10)
        self.assertEqual(len(geohashes),
                         821,
                         'Geohash intersects count not correct')

    def test_within(self):
        geohashes = within(self.shape, 11)        
        self.assertEqual(len(geohashes),
                         23634,
                         'Geohash within count not correct')
        geohashes = within(self.shape, 10)        
        self.assertEqual(len(geohashes),
                         683,
                         'Geohash within count not correct')
