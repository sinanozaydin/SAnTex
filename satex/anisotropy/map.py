import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import numpy as np
from scipy.interpolate import griddata

def plot_data_with_interpolation_in_defined_box(lon_points, lat_points, values, interp_box, method='linear', full_map=False):
    """
    Plot interpolated values within a defined box on a map of South Australia, with an option for full map display.
    
    Parameters:
    - lon_points: Array-like, longitudes of the data points.
    - lat_points: Array-like, latitudes of the data points.
    - values: Array-like, values at the given data points.
    - interp_box: Tuple, defining the interpolation box (left_lon, bottom_lat, right_lon, top_lat).
    - method: String, interpolation method ('linear', 'nearest', etc.).
    - full_map: Boolean, if True, the full global map is displayed; otherwise, focus on the data points' region.
    """
    left_lon, bottom_lat, right_lon, top_lat = interp_box
    
    lon_grid, lat_grid = np.meshgrid(
        np.linspace(left_lon, right_lon, 100),
        np.linspace(bottom_lat, top_lat, 100)
    )
    
    interp_values = griddata(
        (lon_points, lat_points), values, (lon_grid, lat_grid), method=method
    )
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    
    if full_map:
        ax.set_global()
    else:
        ax.set_extent([left_lon, right_lon, bottom_lat, top_lat], crs=ccrs.PlateCarree())
    
    ax.coastlines(resolution='10m')
    ax.add_feature(cartopy.feature.LAND)
    ax.add_feature(cartopy.feature.OCEAN)
    
    contourf = ax.contourf(lon_grid, lat_grid, interp_values, transform=ccrs.PlateCarree(), cmap='viridis', alpha=0.6)
    plt.colorbar(contourf, ax=ax, shrink=0.5, label='Interpolated Value')
    
    ax.plot(lon_points, lat_points, 'ro', markersize=5, transform=ccrs.Geodetic(), label='Data Points')
    
    plt.legend()
    plt.title("Interpolated Data Map")
    plt.show()

lon_points = np.array([138.58, 138.60, 138.62, 138.64, 138.66, 138.68, 138.70, 138.72, 138.74, 138.76])
lat_points = np.array([-34.92, -34.93, -34.94, -34.95, -34.96, -34.97, -34.98, -34.99, -35.00, -35.01])
values = np.random.randint(100, 500, size=10)  # Random sample values for demonstration

interp_box = (138.5, -35.0, 139.0, -34.5)  # Defined as (left_lon, bottom_lat, right_lon, top_lat)

if __name__ == "__main__":
    plot_data_with_interpolation_in_defined_box(lon_points, lat_points, values, interp_box, method='nearest', full_map=False)
