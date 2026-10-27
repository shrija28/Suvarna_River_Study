from backend.gee_map import GEEMap

gmap = GEEMap()

m = gmap.create_map()

m.to_html("gee_map.html")

print("Map created successfully!")