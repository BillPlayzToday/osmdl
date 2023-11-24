import requests
import time

def download_images(download_list,folder,process_name):
    session = requests.Session()
    current_index = 0
    for image_pair in download_list:
        current_index = (current_index + 1)
        while True:
            response = session.request(
                method = "GET",
                url = image_pair[0],
                headers = {
                    "User-Agent": "_ / 1.0 _"
                }
            )
            if (response.status_code == 429):
                print(f"[{process_name}] Rate limit! Waiting...")
                time.sleep(10)
                continue
            elif (not response.ok):
                print(f"[{process_name}] Failed tile: {image_pair[0]} Status code: {response.status_code}")
            break
        print(f"[{process_name}] Progress: {str(current_index)}/{str(len(download_list))}")
        file_path = f"{folder}/{image_pair[1]}"
        open_file = open(file_path,"ab")
        open_file.write(response.content)
        open_file.close()

    print(f"[{process_name}] Finished.")