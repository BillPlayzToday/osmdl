import os
import shutil

cache = "cache1"
start_tile = [138109,84434]
end_tile = [138610,84936]

print("--- MAPPING ---")
tile_names = {}
current_iteration = 0
for x in range(end_tile[0] - start_tile[0]):
    for y in range(end_tile[1] - start_tile[1]):
        current_iteration = (current_iteration + 1)
        tile_names[f"tile-{str(current_iteration)}.tmppng"] = f"{str(x)}-{str(y)}.tmppng"

print("--- MOVING ---")
cache_path = os.path.abspath(f"cache/{cache}")
for current_file in os.listdir(cache_path):
    found_rename = tile_names.get(current_file)
    if (found_rename):
        shutil.move(f"{cache_path}/{current_file}",f"{cache_path}/{found_rename}")
        continue
    print(f"[WARN] NOT FOUND FOR {current_file}")

print(f"--- RENAMED {str(len(tile_names))} FILES ---")