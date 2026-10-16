from crowd_detection.alerts import AlertManager
from crowd_detection.density import Level


def test_no_alert_below_high():
    am = AlertManager(10)
    assert am.check(Level.LOW, 2, 0) is False
    assert am.check(Level.MEDIUM, 6, 1) is False


def test_alert_fires_once_during_cooldown():
    am = AlertManager(10)
    assert am.check(Level.HIGH, 12, 0) is True
    assert am.check(Level.HIGH, 13, 5) is False


def test_alert_fires_again_after_cooldown():
    am = AlertManager(10)
    assert am.check(Level.HIGH, 12, 0) is True
    assert am.check(Level.HIGH, 12, 10) is True
