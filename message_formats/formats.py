# ---- MESSAGE FORMAT ----
def build_problem_message(problems):
    lines = ["🧠 **NeetCode Daily**","","Today's two problems:",""]
    for index, problem in enumerate(problems,start=1):
        lines.append(f"**{index}.[{problem['title']}]({problem['url']})**")
        lines.append(f"Difficulty: `{problem['difficulty']}`")
        lines.append(f"Category: ||`{problem['category']}`||")
        lines.append("")
    lines.append("Good luck! 💪")
    return "\n".join(lines)