"""Offline verification of hosted-API attestations (pure-Python Ed25519, RFC 8032; no dependencies).

python -m diffbench.attest --url https://<api-host> states.json        # fetch the public key from /info
python -m diffbench.attest --pubkey <hex> states.json

`states.json` is the API response (states + `attestation`). Checks: (1) Ed25519 signature over the canonical JSON
(sorted keys, compact) of the attestation without `signature`/`hmac`; (2) the states in the file hash to
`attestation.states_sha256`. It proves that the service issued this attestation for these states; it does NOT prove the
engine ran unmodified (see docs/HOSTED_API.md). The reference implementation here is for verification only (not constant-time).
"""
from __future__ import annotations
import argparse, hashlib, json, sys, urllib.request

_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_I = pow(2, (_P - 1) // 4, _P)


def _inv(x): return pow(x, _P - 2, _P)


def _xrecover(y):
    xx = (y * y - 1) * _inv(_D * y * y + 1) % _P
    x = pow(xx, (_P + 3) // 8, _P)
    if (x * x - xx) % _P != 0: x = x * _I % _P
    return _P - x if x % 2 != 0 else x


_BY = 4 * _inv(5) % _P
_B = (_xrecover(_BY), _BY)


def _add(p, q):
    (x1, y1), (x2, y2) = p, q
    t = _D * x1 * x2 * y1 * y2 % _P
    return ((x1 * y2 + x2 * y1) * _inv(1 + t) % _P, (y1 * y2 + x1 * x2) * _inv(1 - t) % _P)


def _mul(p, e):
    r = (0, 1)
    while e:
        if e & 1: r = _add(r, p)
        p = _add(p, p); e >>= 1
    return r


def _decode(b: bytes):
    y = int.from_bytes(b, "little") & ((1 << 255) - 1)
    x = _xrecover(y)
    if (x & 1) != (b[31] >> 7): x = _P - x
    pt = (x, y)
    if (-pt[0] * pt[0] + pt[1] * pt[1] - 1 - _D * pt[0] ** 2 * pt[1] ** 2) % _P != 0: raise ValueError("point not on curve")
    return pt


def ed25519_verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    if len(pub) != 32 or len(sig) != 64: return False
    try:
        A = _decode(pub); R = _decode(sig[:32])
    except ValueError:
        return False
    S = int.from_bytes(sig[32:], "little")
    if S >= _L: return False
    h = int.from_bytes(hashlib.sha512(sig[:32] + pub + msg).digest(), "little") % _L
    return _mul(_B, S) == _add(R, _mul(A, h))


def canonical(v) -> str:
    if v is None or isinstance(v, (bool, int, str)): return json.dumps(v, ensure_ascii=False)
    if isinstance(v, float): return json.dumps(v)
    if isinstance(v, list): return "[" + ",".join(canonical(x) for x in v) + "]"
    return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + canonical(v[k]) for k in sorted(v)) + "}"


def js_num(x) -> str:
    """Number -> string exactly as ECMAScript Number::toString (the server hashes JSON.stringify output)."""
    from decimal import Decimal
    if isinstance(x, bool): return "true" if x else "false"
    if isinstance(x, int): return str(x)
    if x == 0: return "0"
    sign = "-" if x < 0 else ""; t = Decimal(repr(abs(x))).as_tuple()
    digits = "".join(map(str, t.digits)).rstrip("0") or "0"; k = len(digits)
    n = len("".join(map(str, t.digits))) + t.exponent  # position of the decimal point relative to the digit string start
    if k <= n <= 21: return sign + digits + "0" * (n - k)
    if 0 < n <= 21: return sign + digits[:n] + "." + digits[n:]
    if -6 < n <= 0: return sign + "0." + "0" * (-n) + digits
    e = n - 1; es = ("+" if e >= 0 else "-") + str(abs(e))
    return sign + (digits if k == 1 else digits[0] + "." + digits[1:]) + "e" + es


def js_json(v) -> str:
    if isinstance(v, list): return "[" + ",".join(js_json(x) for x in v) + "]"
    return js_num(v)


def verify_response(resp: dict, pubkey_hex: str) -> dict:
    att = dict(resp["attestation"]); sig = att.pop("signature", None); att.pop("hmac", None)
    out = {"signature_present": sig is not None}
    if sig is None: return out
    out["signature_ok"] = ed25519_verify(bytes.fromhex(pubkey_hex), canonical(att).encode(), bytes.fromhex(sig))
    st = {k: resp[k] for k in ("t", "pos", "quat", "vel", "angvel")}
    # server hashes JSON.stringify of the states object (insertion order t,pos,quat,vel,angvel; JS number formatting)
    body = "{" + ",".join(f'"{k}":{js_json(st[k])}' for k in ("t", "pos", "quat", "vel", "angvel")) + "}"
    out["states_sha256_ok"] = hashlib.sha256(body.encode()).hexdigest() == att["states_sha256"]
    out["key_id"] = att.get("key_id"); out["engine_build"] = att.get("engine_build")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("response"); ap.add_argument("--pubkey"); ap.add_argument("--url")
    a = ap.parse_args()
    pub = a.pubkey or json.loads(urllib.request.urlopen(a.url.rstrip("/") + "/api/public/diffbench/info", timeout=20).read())["attestation_public_key"]["public_key_hex"]
    r = verify_response(json.load(open(a.response)), pub); print(json.dumps(r, indent=1))
    sys.exit(0 if r.get("signature_ok") and r.get("states_sha256_ok") else 1)


if __name__ == "__main__":
    main()
