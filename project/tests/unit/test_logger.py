import pytest
import logging

from app.util.logger import get_logger


@pytest.fixture
def logger(caplog):
    log = get_logger("test_logger", level=logging.DEBUG)
    log.propagate = False
    log.handlers.clear()
    log.addHandler(caplog.handler)
    caplog.handler.setLevel(logging.DEBUG)
    return log


def test_info_logging(logger, caplog):
    with caplog.at_level(logging.INFO):
        logger.info("Info message")
    assert "Info message" in caplog.text


def test_debug_enabled(logger, caplog):
    logger.debug_enable = True
    with caplog.at_level(logging.DEBUG):
        logger.debug("Debug message")
    assert "Debug message" in caplog.text


def test_debug_disabled(logger, caplog):
    logger.debug_enable = False
    with caplog.at_level(logging.DEBUG):
        logger.debug("Should not appear")
    assert "Should not appear" not in caplog.text


def test_warn_and_error(logger, caplog):
    with caplog.at_level(logging.WARNING):
        logger.warn("This is a warning")
        logger.error("This is an error")
    assert "This is a warning" in caplog.text
    assert "This is an error" in caplog.text
    assert "CRITICAL" in caplog.text  # Your error method uses .critical


def test_extra_info(logger, caplog):
    logger.set_extra_info({"key": "value"})
    with caplog.at_level(logging.INFO, logger="test_logger"):
        logger.info("Extra info test", xtra={"key": "override"})
    assert "Extra info test" in caplog.text
