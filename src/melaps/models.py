"""Typed models for the resources the API returns."""

from dataclasses import dataclass, field


@dataclass
class Job:
    id: str
    status: str
    cluster: str = "m1"
    gpus: int = 1
    gpu_type: str = "H100"
    created_at: str = ""
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"], status=d["status"], cluster=d.get("cluster", "m1"),
            gpus=d.get("gpus", 1), gpu_type=d.get("gpu_type", "H100"),
            created_at=d.get("created_at", ""), raw=d,
        )


@dataclass
class Cluster:
    id: str
    region: str
    status: str
    gpus_total: int
    gpus_available: int

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"], region=d["region"], status=d["status"],
            gpus_total=d["gpus_total"], gpus_available=d["gpus_available"],
        )


@dataclass
class Reservation:
    id: str
    cluster: str
    gpus: int
    months: int
    price_per_gpu_hour: float = 1.89

    @classmethod
    def from_dict(cls, d):
        return cls(
            id=d["id"], cluster=d["cluster"], gpus=d["gpus"],
            months=d["months"], price_per_gpu_hour=d.get("price_per_gpu_hour", 1.89),
        )
