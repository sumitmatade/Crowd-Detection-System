from crowd_detection.density import Level
from crowd_detection.stats import RunStats


def test_empty_stats_do_not_crash():
    s = RunStats()
    assert s.average_count == 0.0
    assert s.fps == 0.0
    assert "Frames read: 0" in s.summary()


def test_update_tracks_peak_average_and_alerts():
    s = RunStats()
    s.update(2, Level.LOW, False)
    s.update(12, Level.HIGH, True)
    assert s.peak_count == 12
    assert s.average_count == 7.0
    assert s.alerts == 1
    assert s.level_checks["HIGH"] == 1
