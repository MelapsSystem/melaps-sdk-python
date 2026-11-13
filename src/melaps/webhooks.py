"""Verify webhook signatures from Melaps (``job.*`` events)."""

import hashlib
import hmac


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Return True when ``signature`` matches the HMAC-SHA256 of ``payload``.

    Melaps signs every webhook with the endpoint secret shown in the console.
    The signature header is ``Melaps-Signature``.
    """
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
