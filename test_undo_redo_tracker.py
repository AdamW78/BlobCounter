from collections import namedtuple

import undo_redo_tracker
import pytest

import utils

MockKeypoint = namedtuple('MockKeypoint', ['pt'])

def test_undo_redo_tracker():
    # Test the UndoRedoTracker class
    tracker = undo_redo_tracker.UndoRedoTracker(max_stack_size=5)

    # Create some mock actions
    action1 = undo_redo_tracker.Action(undo_redo_tracker.ActionType.ADD, MockKeypoint((1, 2)))
    action2 = undo_redo_tracker.Action(undo_redo_tracker.ActionType.REMOVE, MockKeypoint((3, 4)))
    action3 = undo_redo_tracker.Action(undo_redo_tracker.ActionType.ADD, MockKeypoint((5, 6)))

    # Perform actions
    tracker.perform_action(action1)
    tracker.perform_action(action2)
    tracker.perform_action(action3)

    # Check the undo stack size
    assert len(tracker.undo_stack) == 3

    # Undo an action
    undone_action = tracker.undo()
    assert undone_action == action3
    assert len(tracker.undo_stack) == 2
    assert len(tracker.redo_stack) == 1

    # Redo an action
    redone_action = tracker.redo()
    assert redone_action == action3
    assert len(tracker.undo_stack) == 3
    assert len(tracker.redo_stack) == 0

def test_undo_redo_tracker_max_stack_size():
    # Test the UndoRedoTracker class with max stack size
    tracker = undo_redo_tracker.UndoRedoTracker(max_stack_size=5)
    # Create some mock actions
    for i in range(10):
        action = undo_redo_tracker.Action(undo_redo_tracker.ActionType.ADD, MockKeypoint((i, i)))
        tracker.perform_action(action)
    # Check the undo stack size
    assert len(tracker.undo_stack) == 5
    # Check the redo stack size
    assert len(tracker.redo_stack) == 0
    # Undo all actions
    for _ in range(5):
        tracker.undo()
    # Check the undo stack size
    assert len(tracker.undo_stack) == 0
    # Check the redo stack size
    assert len(tracker.redo_stack) == 5
    # Redo all actions
    for _ in range(5):
        tracker.redo()
    # Check the undo stack size
    assert len(tracker.undo_stack) == 5
    # Check the redo stack size
    assert len(tracker.redo_stack) == 0

