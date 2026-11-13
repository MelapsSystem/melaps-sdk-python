from unittest.mock import Mock

import pytest

from melaps import Melaps
from melaps.errors import AuthenticationError, NotFoundError


def _client(status=200, payload=None):
    c = Melaps("sk_test_123")
    resp = Mock()
    resp.status_code = status
    resp.headers = {}
    resp.json.return_value = payload or {}
    resp.text = ""
    c._session.request = Mock(return_value=resp)
    return c


def test_requires_key():
    with pytest.raises(AuthenticationError):
        Melaps("")


def test_submit_returns_job():
    c = _client(payload={"id": "job-01k4", "status": "QUEUED", "gpus": 8})
    job = c.jobs.submit({"name": "train", "gpus": 8})
    assert job.id == "job-01k4"
    assert job.gpus == 8


def test_get_missing_job():
    c = _client(status=404)
    with pytest.raises(NotFoundError):
        c.jobs.get("job-nope")


def test_wait_returns_when_done(monkeypatch):
    states = [{"id": "job-1", "status": "RUNNING"}, {"id": "job-1", "status": "DONE"}]
    c = _client(payload=states[0])
    calls = {"n": 0}

    def fake_get(job_id):
        payload = states[min(calls["n"], 1)]
        calls["n"] += 1
        from melaps.models import Job
        return Job.from_dict(payload)

    monkeypatch.setattr(c.jobs, "get", fake_get)
    monkeypatch.setattr("melaps.client.time.sleep", lambda s: None)
    assert c.jobs.wait("job-1", poll_interval=0).status == "DONE"
