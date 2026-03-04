"""utils.py — helpers for list generation and input validation."""
import random


def generate_random_list(count: int, min_val: int, max_val: int) -> list[int]:
    return [random.randint(min_val, max_val) for _ in range(count)]


def parse_custom_input(text: str, min_val: int, max_val: int):
    try:
        tokens = text.replace(",", " ").split()
        values = [int(t) for t in tokens]
        if not values:
            return None
        if any(v < min_val or v > max_val for v in values):
            return None
        return values
    except ValueError:
        return None


def validate_inputs(min_val: str, max_val: str, count: str):
    try:
        mn  = int(min_val)
        mx  = int(max_val)
        cnt = int(count)
    except ValueError:
        return False, "All fields must be integers.", 0, 0, 0
    if mn > mx:
        return False, "Min must be ≤ Max.", 0, 0, 0
    if cnt <= 0:
        return False, "Count must be > 0.", 0, 0, 0
    if cnt > 300:
        return False, "Count must be ≤ 300.", 0, 0, 0
    return True, "", mn, mx, cnt
