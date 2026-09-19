"""Game controls, key mapping definitions, and conflict validation."""

from typing import Dict, List, Optional, Tuple

ACTION_UP = "up"
ACTION_DOWN = "down"
ACTION_LEFT = "left"
ACTION_RIGHT = "right"
ACTION_REVEAL = "reveal"
ACTION_FLAG = "flag"
ACTION_CHORD = "chord"
ACTION_RESTART = "restart"
ACTION_QUIT = "quit"

ALL_ACTIONS = [
    ACTION_UP,
    ACTION_DOWN,
    ACTION_LEFT,
    ACTION_RIGHT,
    ACTION_REVEAL,
    ACTION_FLAG,
    ACTION_CHORD,
    ACTION_RESTART,
    ACTION_QUIT,
]

ACTION_LABELS = {
    ACTION_UP: "Move Up",
    ACTION_DOWN: "Move Down",
    ACTION_LEFT: "Move Left",
    ACTION_RIGHT: "Move Right",
    ACTION_REVEAL: "Reveal Cell",
    ACTION_FLAG: "Place / Remove Flag",
    ACTION_CHORD: "Chord Reveal (Quick Open)",
    ACTION_RESTART: "Restart Game",
    ACTION_QUIT: "Quit to Menu",
}

DEFAULT_KEY_BINDINGS: Dict[str, List[str]] = {
    ACTION_UP: ["w", "up"],
    ACTION_DOWN: ["s", "down"],
    ACTION_LEFT: ["a", "left"],
    ACTION_RIGHT: ["d", "right"],
    ACTION_REVEAL: ["enter", "space"],
    ACTION_FLAG: ["f"],
    ACTION_CHORD: ["c"],
    ACTION_RESTART: ["r"],
    ACTION_QUIT: ["q", "escape"],
}


def normalize_key(key: str) -> str:
    """Normalize key string representation for comparison."""
    if not key:
        return ""
    mapping = {
        "\r": "enter",
        "\n": "enter",
        " ": "space",
        "\x1b": "escape",
        "esc": "escape",
    }
    if key in mapping:
        return mapping[key]
    cleaned = key.strip().lower()
    return mapping.get(cleaned, cleaned)


def validate_key_bindings(bindings: Dict[str, List[str]]) -> Tuple[bool, Optional[str]]:
    """Verify that every action has at least one key and no key is assigned to multiple actions."""
    for action in ALL_ACTIONS:
        if action not in bindings or not bindings[action]:
            return False, f"Action '{ACTION_LABELS.get(action, action)}' must have at least one key assigned."

    seen_keys: Dict[str, str] = {}
    for action, keys in bindings.items():
        for k in keys:
            norm = normalize_key(k)
            if not norm:
                continue
            if norm in seen_keys and seen_keys[norm] != action:
                existing_action = ACTION_LABELS.get(seen_keys[norm], seen_keys[norm])
                new_action = ACTION_LABELS.get(action, action)
                return False, f"Key '{norm}' conflicts between '{existing_action}' and '{new_action}'."
            seen_keys[norm] = action

    return True, None


def get_action_for_key(key: str, bindings: Dict[str, List[str]]) -> Optional[str]:
    """Resolve normalized key string into an action name."""
    normalized = normalize_key(key)
    for action, keys in bindings.items():
        for k in keys:
            if normalize_key(k) == normalized:
                return action
    return None
