import enum
import logging
from collections import namedtuple

from utils import DEFAULT_MAX_UNDO_REDO_STACK_SIZE

Action = namedtuple('Action', ['action_type', 'keypoint'])

class UndoRedoTracker:
    def __init__(self, max_stack_size=DEFAULT_MAX_UNDO_REDO_STACK_SIZE):
        self.undo_stack = []
        self.redo_stack = []
        self.max_stack_size = max_stack_size

    def perform_action(self, action: Action):
        """Perform an action and add it to the undo stack."""
        if action is None:
            return # No action to perform
        if len(self.undo_stack) + 1 > self.max_stack_size:
            self.undo_stack.pop(0)  # Remove the oldest action if the stack exceeds the maximum size
        self.redo_stack.clear()  # Clear the redo stack as new action invalidates the redo history
        self.undo_stack.append(action)
        logging.debug(f"Action performed: Action[ActionType={action.action_type}, Keypoint=(x={action.keypoint.pt[0]}, y={action.keypoint.pt[1]})]")

    def undo(self):
        """Undo the last action."""
        if not self.undo_stack:
            logging.debug("No undo stack")
            return  # No action to undo
        action = self.__undo_redo_helper(self.undo_stack, self.redo_stack)
        logging.debug(f"Undoing action: Action[ActionType={action.action_type}, Keypoint=(x={action.keypoint.pt[0]}, y={action.keypoint.pt[1]})]")
        return action

    def redo(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            logging.debug("No redo stack")
            return  # No action to redo
        action = self.__undo_redo_helper(self.redo_stack, self.undo_stack)
        logging.debug(f"Redoing action: Action[ActionType={action.action_type}, Keypoint=(x={action.keypoint.pt[0]}, y={action.keypoint.pt[1]})]")
        return action

    def __undo_redo_helper(self, pop_stack: list[Action], push_stack: list[Action]) -> Action:
        action = pop_stack.pop()
        if len(push_stack) + 1 > self.max_stack_size:
            push_stack.pop(0)  # Remove the oldest action if the stack exceeds the maximum size
        push_stack.append(action)
        return action

class ActionType(enum.Enum):
    ADD = 0,
    REMOVE = 1
