# melaps — Python SDK

[![PyPI](https://img.shields.io/pypi/v/melaps)](https://pypi.org/project/melaps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

Python SDK for the [Melaps System](https://melaps.xyz) API — submit training jobs,
stream GPU telemetry, and manage reservations on H100 clusters.

- Website: <https://melaps.xyz>
- Documentation: <https://docs.melaps.xyz>
- API reference: <https://docs.melaps.xyz/api>
- X: <https://x.com/melaps_system>

## Install

```bash
pip install melaps
```

## Quickstart

```python
from melaps import Melaps

client = Melaps("sk_live_...")

job = client.jobs.submit({
    "name": "qwen2.5-7b-sft",
    "cluster": "m1",
    "gpus": 8,
    "image": "nvcr.io/nvidia/pytorch:24.10-py3",
    "command": ["python", "train.py", "--epochs", "3"],
})
job = client.jobs.wait(job.id)
print(job.status, client.jobs.metrics(job.id))
```

See [`examples/quickstart.py`](examples/quickstart.py) and
[`examples/reserved.py`](examples/reserved.py).

## What is in the SDK

| Module | Contents |
| --- | --- |
| `melaps.Melaps` | Client: `jobs`, `clusters`, `reservations`, `usage`, `status` |
| `melaps.models` | Typed `Job`, `Cluster`, `Reservation` dataclasses |
| `melaps.webhooks` | `verify_signature()` for `job.*` webhook events |
| `melaps.pagination` | `iter_all()` cursor helper for list endpoints |

Reads are limited to 600/min, job creation to 10/min; the client backs off on
HTTP 429 using the `Retry-After` header. Mutating calls send an idempotency
key (replayed for 24h), so a retried submit never creates a duplicate job.

## Errors

`AuthenticationError` (401), `ValidationError` (400/422), `NotFoundError`
(404), `RateLimitError` (429, has `.retry_after`), all subclass `MelapsError`.

## License

MIT — see [LICENSE](LICENSE).

---

**Melaps System** — GPU racks you can hold by the hour.

- Website: <https://melaps.xyz>
- Documentation: <https://docs.melaps.xyz>
- X: <https://x.com/melaps_system>
- Status: <https://melaps.xyz/status>
