import requests
from tqdm import tqdm
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import chardet
import mimetypes



headers = {"Authorization": "Bearer simpleToken"}
url = "http://100.79.4.20:5001/upload"
path = "video.MP4"
mime_type, _ = mimetypes.guess_type(path)

encoder = MultipartEncoder(
    fields={
        "rel_dir": "images/",
        "file": ("video.MP4", open(path, "rb"), mime_type or "application/octet-stream")
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
