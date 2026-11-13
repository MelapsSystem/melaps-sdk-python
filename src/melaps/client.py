"""The Melaps client — jobs, clusters, reservations, usage, webhooks."""

import time
import uuid

import requests

from .errors import (
    AuthenticationError,
    MelapsError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import Cluster, Job, Reservation

API_VERSION = "2026-06-22"


class Melaps:
    """Client for the Melaps API (``https://api.melaps.system/v1``).

    >>> from melaps import Melaps
    >>> client = Melaps("sk_live_...")
    >>> job = client.jobs.submit({"name": "train", "gpus": 8, "cluster": "m1",
    ...                           "image": "pytorch:2.5", "command": ["python", "train.py"]})
    >>> client.jobs.wait(job.id)
    """

    def __init__(self, api_key, base_url="https://api.melaps.system/v1", timeout=30):
        if not api_key:
            raise AuthenticationError("an API key is required")
        self._key = api_key
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self.jobs = _Jobs(self)
        self.clusters = _Clusters(self)
        self.reservations = _Reservations(self)

    def _request(self, method, path, json=None, idempotency_key=None):
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Melaps-Version": API_VERSION,
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        for attempt in range(4):
            resp = self._session.request(
                method, f"{self._base}{path}", json=json,
                headers=headers, timeout=self._timeout,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                if attempt < 3:
                    time.sleep(retry_after)
                    continue
                raise RateLimitError(retry_after=retry_after)
            if resp.status_code == 401:
                raise AuthenticationError("invalid API key")
            if resp.status_code == 404:
                raise NotFoundError(f"{method} {path}")
            if resp.status_code in (400, 422):
                raise ValidationError(resp.text[:300])
            if resp.status_code >= 400:
                raise MelapsError(f"{method} {path}: HTTP {resp.status_code}")
            return resp.json()
        raise MelapsError("request failed after retries")

    def usage(self, start, end):
        """Billed GPU-hours between two ISO dates."""
        return self._request("GET", f"/usage?start={start}&end={end}")

    def status(self):
        return self._request("GET", "/status")


class _Jobs:
    def __init__(self, client):
        self._c = client

    def submit(self, spec, idempotency_key=None):
        data = self._c._request("POST", "/jobs", json=spec,
                                idempotency_key=idempotency_key or str(uuid.uuid4()))
        return Job.from_dict(data)

    def get(self, job_id):
        return Job.from_dict(self._c._request("GET", f"/jobs/{job_id}"))

    def list(self, limit=20):
        data = self._c._request("GET", f"/jobs?limit={limit}")
        return [Job.from_dict(j) for j in data.get("data", [])]

    def cancel(self, job_id):
        return Job.from_dict(self._c._request("POST", f"/jobs/{job_id}/cancel"))

    def metrics(self, job_id):
        return self._c._request("GET", f"/jobs/{job_id}/metrics")

    def wait(self, job_id, poll_interval=15, timeout=3600):
        """Block until the job reaches a terminal state."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            job = self.get(job_id)
            if job.status in ("DONE", "FAILED", "CANCELLED", "PREEMPTED"):
                return job
            time.sleep(poll_interval)
        raise MelapsError(f"timed out waiting for {job_id}")


class _Clusters:
    def __init__(self, client):
        self._c = client

    def list(self):
        data = self._c._request("GET", "/clusters")
        return [Cluster.from_dict(c) for c in data.get("data", [])]


class _Reservations:
    def __init__(self, client):
        self._c = client

    def create(self, gpus=8, months=1, cluster="m1"):
        data = self._c._request(
            "POST", "/reservations",
            json={"gpus": gpus, "months": months, "cluster": cluster},
            idempotency_key=str(uuid.uuid4()),
        )
        return Reservation.from_dict(data)
