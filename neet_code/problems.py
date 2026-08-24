import json
from pathlib import Path


PROBLEMS_FILE = Path(__file__).parent / "problems.json"


def load_problems():
    with PROBLEMS_FILE.open("r", encoding="utf-8") as file:
        problems = json.load(file)

    validate_problems(problems)

    return problems


def validate_problems(problems):
    if not isinstance(problems, list):
        raise ValueError(
            "problems.json must contain a JSON array."
        )

    if len(problems) < 2:
        raise ValueError(
            "At least two problems are required."
        )

    required_fields = {
        "id",
        "title",
        "difficulty",
        "category",
        "url",
    }

    seen_ids = set()

    for problem in problems:
        missing_fields = required_fields - problem.keys()

        if missing_fields:
            raise ValueError(
                f"Problem '{problem.get('title', 'unknown')}' "
                f"is missing: {missing_fields}"
            )

        problem_id = problem["id"]

        if problem_id in seen_ids:
            raise ValueError(
                f"Duplicate problem ID: {problem_id}"
            )

        seen_ids.add(problem_id)