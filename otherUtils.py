"""Reusable input helpers for the POS project."""

from __future__ import annotations

import copy


def ansCage(choices: list, query: str, mode: int = 0) -> str:
    """Keep prompting until the user provides a valid value."""
    choices_copy = copy.deepcopy(choices)

    match mode:
        case 0:
            return ansCageMode0(choices_copy, query)
        case 1:
            return ansCageMode1(query)
        case 2:
            return ansCageMode2(choices_copy, query)
        case 3:
            return ansCageMode3(choices_copy, query)
        case _:
            raise ValueError(f"Unsupported mode: {mode}")


def ansCageMode0(choices1, query):
    """Allow only values from a visible list of choices."""
    while True:
        user_answer = input(f"{query}\n({', '.join(str(item) for item in choices1)}): ").strip().upper()
        if user_answer not in {str(choice).upper() for choice in choices1}:
            print(f"Please choose between {', '.join(str(item) for item in choices1)}")
            continue
        return user_answer


def ansCageMode1(query: str):
    """Allow an integer or float value from the user."""
    while True:
        user_answer = input(f"{query}: ").strip()
        try:
            float(user_answer)
        except ValueError:
            print("Please enter a valid integer or float value.")
            continue
        return user_answer


def ansCageMode2(choices1: list | dict, query: str):
    """Allow only values from a hidden list without showing them."""
    valid_values = {str(value).upper() for value in choices1}
    while True:
        user_answer = input(f"{query}: ").strip().upper()
        if user_answer not in valid_values:
            print("Invalid Value!")
            continue
        return user_answer


def ansCageMode3(choices1: list | dict, query: str):
    """Restrict input to a value not greater than a supplied max."""
    limit = int(choices1[0])
    while True:
        user_answer = int(ansCageMode1(f"(0 - {limit}) {query}"))
        if user_answer > limit:
            print("Invalid Value!")
            continue
        return user_answer
