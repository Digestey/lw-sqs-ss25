import pytest

@pytest.fixture(scope="function")
def no_asyncio(monkeypatch):
    monkeypatch.setattr("pytest_asyncio.plugin.pytest_pyfunc_call", lambda *a, **kw: None)
