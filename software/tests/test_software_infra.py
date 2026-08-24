"""Minimal pytest infrastructure test — software/tests."""

def test_basic():
    assert True

def test_pyvisa_import():
    import pyvisa
    # Should import even without hardware; enumerate resources gracefully
    rm = pyvisa.ResourceManager("@py")
    resources = rm.list_resources()
    assert isinstance(resources, tuple)
