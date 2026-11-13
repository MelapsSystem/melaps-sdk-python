"""Submit a job and wait for it to finish."""

import os

from melaps import Melaps

client = Melaps(os.environ["MELAPS_API_KEY"])

job = client.jobs.submit({
    "name": "hello-gpu",
    "cluster": "m1",
    "gpus": 1,
    "image": "nvcr.io/nvidia/pytorch:24.10-py3",
    "command": ["python", "-c", "import torch; print(torch.cuda.get_device_name(0))"],
})
print("submitted", job.id)
job = client.jobs.wait(job.id)
print("final status:", job.status)
print(client.jobs.metrics(job.id))
