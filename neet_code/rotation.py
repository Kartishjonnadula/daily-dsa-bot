import random

from .database import (
    complete_rotation,
    create_rotation,
    get_current_rotation,
    get_daily_problems,
    get_used_problem_ids,
    mark_problems_used,
    save_daily_problems,
)
from .problems import load_problems


PROBLEMS_PER_DAY = 2


def get_or_create_rotation():
    rotation = get_current_rotation()

    if rotation is not None:
        return rotation["id"]

    return create_rotation()


def select_daily_problems(
    problem_date,
):
    problems = load_problems()

    existing_daily = get_daily_problems(
        problem_date
    )

    problem_map = {
        problem["id"]: problem
        for problem in problems
    }

    # Already selected today.
    # Return the exact same pair.
    if existing_daily is not None:
        problem_1 = problem_map.get(
            existing_daily["problem_1_id"]
        )

        problem_2 = problem_map.get(
            existing_daily["problem_2_id"]
        )

        if problem_1 and problem_2:
            return [
                problem_1,
                problem_2,
            ]

    rotation_id = get_or_create_rotation()

    used_ids = get_used_problem_ids(
        rotation_id
    )

    available = [
        problem
        for problem in problems
        if problem["id"] not in used_ids
    ]

    # If fewer than two problems remain,
    # complete the rotation and start another.
    if len(available) < PROBLEMS_PER_DAY:
        complete_rotation(
            rotation_id
        )

        rotation_id = create_rotation()

        available = problems.copy()

    selected = random.sample(
        available,
        PROBLEMS_PER_DAY,
    )

    mark_problems_used(
        rotation_id,
        selected,
    )

    save_daily_problems(
        problem_date=problem_date,
        rotation_id=rotation_id,
        problem_1_id=selected[0]["id"],
        problem_2_id=selected[1]["id"],
    )

    return selected