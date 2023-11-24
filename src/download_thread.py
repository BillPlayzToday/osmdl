import requests

def download_images(list,folder):
    session = requests.Session()
    for image_pair in list:
        response = session.request(
            method = "GET",
            url = image_pair[0],
            headers = {
                "User-Agent": "_ / 1.0 _"
            }
        )
        if (not response.ok):
            print(f"Failed tile: {image_pair[0]} Status code: {response.status_code}")