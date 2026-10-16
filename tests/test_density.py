import pytest

from crowd_detection.density import Level, classify, grid_counts


def test_classify_levels():
    assert classify(0, 5, 10) == Level.LOW
    assert classify(4, 5, 10) == Level.LOW
    assert classify(5, 5, 10) == Level.MEDIUM
    assert classify(9, 5, 10) == Level.MEDIUM
    assert classify(10, 5, 10) == Level.HIGH


def test_classify_rejects_negative():
    with pytest.raises(ValueError):
        classify(-1, 5, 10)


def test_grid_counts_places_people_in_right_cell():
    boxes = [(0, 0, 10, 10), (90, 90, 10, 10), (45, 45, 10, 10)]
    grid = grid_counts(boxes, 100, 100, 3, 3)
    assert grid[0, 0] == 1
    assert grid[2, 2] == 1
    assert grid[1, 1] == 1
    assert grid.sum() == 3


def test_grid_counts_ignores_boxes_outside_frame():
    grid = grid_counts([(500, 500, 10, 10)], 100, 100, 3, 3)
    assert grid.sum() == 0


def test_roi_keeps_only_boxes_inside():
    from crowd_detection.density import filter_by_roi

    boxes = [(10, 10, 10, 10), (60, 60, 10, 10)]
    kept = filter_by_roi(boxes, [0.5, 0.5, 1.0, 1.0], 100, 100)
    assert kept == [(60, 60, 10, 10)]


def test_roi_none_keeps_everything():
    from crowd_detection.density import filter_by_roi

    boxes = [(10, 10, 10, 10), (60, 60, 10, 10)]
    assert filter_by_roi(boxes, None, 100, 100) == boxes
