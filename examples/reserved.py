"""Reserve a full rack (8x H100) for 6 months."""

import os

from melaps import Melaps

client = Melaps(os.environ["MELAPS_API_KEY"])
res = client.reservations.create(gpus=8, months=6, cluster="m1")
print(f"Reservation {res.id}: {res.gpus} GPUs for {res.months} months "
      f"at ${res.price_per_gpu_hour}/GPU-hour")
