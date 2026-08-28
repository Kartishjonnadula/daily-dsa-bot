import json
from pathlib import Path

PROBLEMS_FILE = Path(__file__).parent / "problems.json"

def load_problems():
    with PROBLEMS_FILE.open("r", encoding="utf-8") as file: problems = json.load(file)
    validate_problems(problems)
    return problems

def validate_problems(problems):
    if not isinstance(problems, list) or len(problems) < 2: raise ValueError("problems.json must contain a JSON array with atleast two problems.") #not needed
    required_fields = {"id","title","difficulty","category","url"} # not needed
    seen_ids = set()
    for problem in problems:
        if (missing := required_fields - problem.keys()): raise ValueError(f"Problem '{problem.get('title', 'unknown')}' is missing: {missing}") #not needed
        raise ValueError(f"Duplicate problem ID: {pid}") if (pid := problem["id"]) in seen_ids else seen_ids.add(pid)