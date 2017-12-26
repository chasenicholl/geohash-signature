# import geohash
# import geojson
# from shapely.geometry import Polygon
# import geohash_signature

# COORDINATES = [[-73.99678637, 40.73719356],
#                [-73.99657715, 40.73745370],
#                [-73.99367500, 40.73620583],
#                [-73.99385739, 40.73594569]]
# SHAPE = Polygon(COORDINATES)
# POLY = geojson.Polygon(COORDINATES)
# print(geojson.FeatureCollection(geojson.Feature(geometry=POLY)))
# # SHAPE = Polygon([[-84.4878736498574625, 42.7258620338422190],
# #                  [-84.4878657867977267, 42.7258618486300890],
# #                  [-84.4878970506964038, 42.7258601643061198]])

# # GHASHES = []
# # for GHASH in HASHES:
# #     GHASHES.extend(geohash.neighbors(GHASH))

# # print(len(HASHES))
# # print(len(GHASHES))
# # print(len(list(set(GHASHES) - set(HASHES))))

# GEO = geohash_signature.GeohashSignature()
# HASHES = GEO.generate(SHAPE, 9)
# print(len(HASHES))

# GEO.geohash_feature_collection('/Users/chasenicholl/Desktop/hashes.geojson')

# #geohash_feature_collection

# # res = geo._add_hashes(HASHES)
# # print(geo._)
# # RES = geohash_signature.covers(SHAPE, 9)

# # print(len(RES))

