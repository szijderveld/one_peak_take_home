"""Peer-selection tests: dropping the unverifiable '1'-headcount sentinels.

`clean_employees` returns `(None, False)` *only* for the `<=1` sentinel with no
narrative figure to recover — so that pair is the precise drop signal. A genuinely
absent count is `(None, True)` and must survive."""

from app.models.domain import Company
from app.pipeline.pipeline import _select_peers


def _c(domain, sim, *, employees=100, reliable=True):
    return Company(
        domain=domain, display_name=domain, similarity=sim,
        employees=employees, employees_reliable=reliable,
    )


def test_drops_unverifiable_headcount_sentinel():
    seed = _c("seed.com", 1.0)
    cleaned = [
        _c("real.com", 0.8, employees=200),
        _c("sentinel.com", 0.8, employees=None, reliable=False),  # the "1" sentinel
    ]
    peers, quarantined, dropped = _select_peers(cleaned, seed, 0.6)
    assert [p.domain for p in peers] == ["real.com"]
    assert dropped == 1 and quarantined == 0


def test_keeps_unknown_but_not_sentinel_headcount():
    # employees absent is (None, True) — "unknown", NOT the dropped sentinel.
    seed = _c("seed.com", 1.0)
    cleaned = [_c("nodata.com", 0.8, employees=None, reliable=True)]
    peers, _, dropped = _select_peers(cleaned, seed, 0.6)
    assert [p.domain for p in peers] == ["nodata.com"] and dropped == 0
