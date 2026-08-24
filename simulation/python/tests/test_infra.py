"""Minimal pytest infrastructure test — verifies Python env is functional."""

def test_arithmetic():
    assert 1 + 1 == 2

def test_numpy_available():
    import numpy as np
    a = np.array([1.0, 2.0, 3.0])
    assert np.isclose(a.mean(), 2.0)

def test_scipy_available():
    import scipy
    assert scipy.__version__  # noqa: S101

def test_pint_available():
    import pint
    ureg = pint.UnitRegistry()
    v = 5.0 * ureg.volt
    assert v.magnitude == 5.0
