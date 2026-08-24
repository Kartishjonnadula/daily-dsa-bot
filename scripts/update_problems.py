import json
from pathlib import Path
from urllib.request import urlopen


SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "neetcode-gh/leetcode/main/"
    ".problemSiteData.json"
)

OUTPUT_FILE = (
    Path(__file__).parent.parent
    / "neet_code"
    / "problems.json"
)


def download_problems():
    print("Downloading NeetCode problem data...")

    with urlopen(SOURCE_URL) as response:
        data = json.load(response)

    return data


def build_problems(data):
    problems = []

    for item in data:
        if not item.get("neetcode150"):
            continue

        slug = item.get("link")

        if not slug:
            continue

        slug = slug.strip("/")

        problem = {
            "id": slug,
            "title": item["problem"],
            "difficulty": item["difficulty"],
            "category": item["pattern"],
            "url": (
                f"https://leetcode.com/problems/"
                f"{slug}/"
            ),
        }

        problems.append(problem)

    return problems


def validate(problems):
    ids = {
        problem["id"]
        for problem in problems
    }

    if len(problems) != len(ids):
        raise ValueError(
            "Duplicate problem IDs found."
        )

    print(
        f"Found {len(problems)} "
        f"NeetCode 150 problems."
    )

    if len(problems) != 150:
        raise ValueError(
            f"Expected 150 problems, "
            f"found {len(problems)}."
        )


def save(problems):
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            problems,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write("\n")

    print(
        f"Saved to {OUTPUT_FILE}"
    )


def main():
    data = download_problems()

    problems = build_problems(data)

    validate(problems)

    save(problems)


if __name__ == "__main__":
    main()