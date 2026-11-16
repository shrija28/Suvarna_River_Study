import rasterio.warp

# 1989
xs, ys = rasterio.warp.transform("EPSG:4326", "EPSG:32643", [74.69438961, 74.69438961, 74.69522141, 74.69522209], [13.45161931, 13.45161931, 13.45134905, 13.45080652])
print(f"1989: x={xs[0]:.2f}, y={ys[0]:.2f}")
print(f"1990: x={xs[1]:.2f}, y={ys[1]:.2f}")
print(f"1991: x={xs[2]:.2f}, y={ys[2]:.2f}")
print(f"Shift 1990->1991: dx={xs[2]-xs[1]:.2f}, dy={ys[2]-ys[1]:.2f}")
print(f"Shift 1991->1992: dx={xs[3]-xs[2]:.2f}, dy={ys[3]-ys[2]:.2f}")
