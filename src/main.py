import math
import os
import sys
import multiprocessing
import PIL.Image
import time

import download_thread

download_zoom = 18
download_region = [
    [40.8951,-74.0516],
    [40.6884,-73.8621]
]
download_processes = 4

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

def get_split_list(split_list,chunks):
    chunk_size = math.ceil(len(split_list) / chunks)
    final_list = []

    for part in range(0,len(split_list),chunk_size):
        final_list.append(split_list[part:part + chunk_size])

    return final_list

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
    download_list = []

    for current_tile in download_tiles:
        relative_position = (
            (current_tile[0] - start_tile[0]),
            (current_tile[1] - start_tile[1])
        )
        download_list.append([
            f"https://tile.openstreetmap.org/{download_zoom}/{current_tile[0]}/{current_tile[1]}.png",
            f"{str(relative_position[0])}-{str(relative_position[1])}.tmppng"
        ])

    download_splits = get_split_list(download_list,download_processes)

    current_index = -1
    active_download_processes = []
    for download_task in download_splits:
        current_index = (current_index + 1)
        new_process = multiprocessing.Process(
            target = download_thread.download_images,
            args = (download_task,cache_location,f"Process Index {str(current_index)}")
        )
        active_download_processes.append(new_process)
        new_process.start()
    
    while True:
        for running_process in active_download_processes:
            if (not running_process.is_alive()):
                active_download_processes.remove(running_process)
                print("--- DEAD DOWNLOAD PROCESS ---")

        if (len(active_download_processes) == 0):
            break

        time.sleep(1)

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
