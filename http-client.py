import requests
from tqdm import tqdm
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import chardet

headers = {"Authorization": "Bearer simpleToken"}
url = "http://100.79.4.20:5001/upload"
path = "video.MP4"

encoder = MultipartEncoder(
    fields={
        "rel_dir": "images/",
        "file": ("video.MP4", open(path, "rb"), "video/mp4")
    }
)

progress = tqdm(total=encoder.len, unit="B", unit_scale=True, desc="Uploading")

def callback(monitor):
    progress.update(monitor.bytes_read - progress.n)
    
monitor = MultipartEncoderMonitor(encoder, callback)

headers["Content-Type"] = monitor.content_type

response = requests.post(url, headers=headers, data=monitor)
progress.close()

print(response.status_code, response.text)
