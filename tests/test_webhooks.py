import hashlib
import hmac

from melaps.webhooks import verify_signature


def test_verify_signature():
    secret = "whsec_test"
    payload = b'{"type":"job.completed"}'
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_signature(payload, sig, secret)
    assert not verify_signature(payload, "0" * 64, secret)
