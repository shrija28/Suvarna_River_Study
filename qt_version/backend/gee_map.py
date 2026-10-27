import ee
import geemap


class GEEMap:

    def __init__(self):

        ee.Initialize(project="majpro")

    def create_map(self):

        # Center on Suvarna River (Malpe area)
        m = geemap.Map(center=[13.46, 74.69], zoom=13)

        return m