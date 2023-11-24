import math
import os
import sys
import PIL.Image
import requests

download_zoom = 16
download_region = [
    [53.7406,9.7284],
    [53.3571,10.3038]
]

def get_tile_coord(lat_lon,zoom):
    latitude_radians = math.radians(lat_lon[0])
    tile_size = (1 << zoom)
    x = int((lat_lon[1] + 180.0) / 360.0 * tile_size)
    y = int((1.0 - math.asinh(math.tan(latitude_radians)) / math.pi) / 2.0 * tile_size)
    return x,y

def get_lat_lon(tile_coord,zoom):
    tile_size = (1 << zoom)
    lon_deg = (tile_coord[0] / tile_size * 360.0 - 180.0)
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_coord[1] / tile_size)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg,lon_deg

def create_cache_location():
    iteration = 0
    while True:
        current_path = f"cache/cache{iteration}/"
        if (os.path.exists(current_path)):
            iteration = (iteration + 1)
            continue
        os.mkdir(current_path)
        return (os.path.abspath(current_path))

def start_download():
    start_tile = get_tile_coord(download_region[0],download_zoom)
    end_tile = get_tile_coord(download_region[1],download_zoom)
    tile_difference = [
        (end_tile[0] - start_tile[0]),
        (end_tile[1] - start_tile[1])
    ]
    final_resolution = (
        (tile_difference[0] * 256),
        (tile_difference[1] * 256)
    )
    download_tiles = []
    for x_tile in range(start_tile[0],end_tile[0]):
        for y_tile in range(start_tile[1],end_tile[1]):
            download_tiles.append(tuple([x_tile,y_tile]))

    print("--- PREDOWNLOAD ---")
    print(f"Starting Tile: {start_tile[0]},{start_tile[1]}")
    print(f"Ending Tile: {end_tile[0]},{end_tile[1]}")
    print(f"Download Tiles: {str(tile_difference[0] * tile_difference[1])}")
    print(f"Image Resolution: {str(final_resolution[0])}px * {str(final_resolution[0])}px")

    print("Continue? [Y]es or [n]o")
    if (input() != "Y"):
        print("Cancelling.")
        sys.exit()

    print("--- DOWNLOADING ---")
    cache_location = create_cache_location()
    session = requests.Session()

    current_index = 0
    for current_tile in download_tiles:
        current_index = (current_index + 1)

        response = session.request(
            method = "GET",
            url = (f"https://tile.openstreetmap.org/{download_zoom}/{current_tile[0]}/{current_tile[1]}.png"),
            headers = {
                "User-Agent": "_ / 1.0 _"
            }
        )
        if (not response.ok):
            print(f"Failed Tile: {current_tile[0]},{current_tile[1]} Status: {str(response.status_code)}")
            sys.exit(1)
        print(f"Download Progress: {str(current_index)}/{str(len(download_tiles))}")
        relative_position = (
            (current_tile[0] - start_tile[0]),
            (current_tile[1] - start_tile[1])
        )
        file_path = f"{cache_location}/{str(relative_position[0])}-{str(relative_position[1])}.tmppng"
        open_file = open(file_path,"ab")
        open_file.write(response.content)
        open_file.flush()
        open_file.close()

    merge_tiles(final_resolution,cache_location,False)

    print("--- FINISHED ---")

def merge_tiles(final_resolution,cache,remove_processed):
    print("--- ALLOCATING ---")
    final_image = PIL.Image.new("RGB",final_resolution,(0,0,0))
    print("--- MERGING ---")
    current_index = 0
    for current_tile in os.listdir(cache):
        current_index = (current_index + 1)
        split_name = current_tile.split("-")
        split_name[1] = split_name[1][:-7]
        current_tile = f"{cache}/{current_tile}"
        current_image = PIL.Image.open(current_tile,"r")
        final_image.paste(current_image,(
            (int(split_name[0]) * 256),
            (int(split_name[1]) * 256)
        ))
        current_image.close()
        if (remove_processed):
            os.remove(current_tile)
        print(f"Merging Progress: {str(current_index)}/?")
    print("--- SAVING ---")
    final_image.save(f"{cache}/final.jpg")

start_download()
