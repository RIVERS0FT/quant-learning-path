#!/usr/bin/env python3
"""Flatten the learning-path repository structure.

Target layout:
repo/
├── README.md
├── stage-*/
│   ├── README.md
│   ├── week-*/
│   │   ├── README.md
│   │   └── day-*.md
│   └── ...
└── ...
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES_DIR = ROOT / "stages"

ROOT_TREE = """```text
Quant/
├── README.md
├── stage-01-python-numpy-financial-data/
│   ├── README.md
│   ├── week-01-python-environment-basics/
│   │   ├── README.md
│   │   ├── day-01-python-environment.md
│   │   └── ...
│   └── ...
├── stage-02-a-share-data-backtesting/
│   ├── README.md
│   └── week-01-data-sources-field-dictionary-calendar/
│       ├── README.md
│       └── ...
└── stage-12-personal-quant-platform/
    ├── README.md
    ├── week-01/
    │   ├── README.md
    │   └── ...
    └── week-13/
        └── README.md
```"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def merge_directory(source: Path, target: Path) -> None:
    """Move source into target without silently overwriting different files."""
    target.mkdir(parents=True, exist_ok=True)

    for item in sorted(source.iterdir(), key=lambda path: path.name):
        destination = target / item.name

        if item.is_dir():
            if destination.exists():
                if not destination.is_dir():
                    raise RuntimeError(f"Path collision: {item} -> {destination}")
                merge_directory(item, destination)
            else:
                shutil.move(str(item), str(destination))
        else:
            if destination.exists():
                if destination.is_dir():
                    raise RuntimeError(f"Path collision: {item} -> {destination}")
                if item.read_bytes() != destination.read_bytes():
                    raise RuntimeError(
                        f"File collision with different content: {destination}"
                    )
                item.unlink()
            else:
                shutil.move(str(item), str(destination))

    source.rmdir()


def remove_first_heading(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("# "):
            del lines[index]
            break

    while lines and not lines[0].strip():
        lines.pop(0)

    return "\n".join(lines).strip()


def merge_index(index_path: Path, parent_readme: Path, heading: str) -> None:
    if not index_path.exists():
        return

    index_content = remove_first_heading(read_text(index_path))
    base_content = read_text(parent_readme) if parent_readme.exists() else ""

    if index_content and index_content not in base_content:
        base_content = (
            base_content.rstrip()
            + f"\n\n## {heading}\n\n"
            + index_content
            + "\n"
        )
        write_text(parent_readme, base_content)

    index_path.unlink()


def flatten_named_container(container: Path, heading: str) -> None:
    parent = container.parent
    merge_index(container / "README.md", parent / "README.md", heading)

    for item in sorted(container.iterdir(), key=lambda path: path.name):
        destination = parent / item.name

        if item.is_dir():
            if destination.exists():
                merge_directory(item, destination)
            else:
                shutil.move(str(item), str(destination))
        else:
            if destination.exists():
                if item.read_bytes() != destination.read_bytes():
                    raise RuntimeError(
                        f"File collision with different content: {destination}"
                    )
                item.unlink()
            else:
                shutil.move(str(item), str(destination))

    container.rmdir()


def move_stages_to_root() -> None:
    if not STAGES_DIR.exists():
        return

    for stage in sorted(STAGES_DIR.iterdir(), key=lambda path: path.name):
        if not stage.is_dir() or not stage.name.startswith("stage-"):
            continue

        destination = ROOT / stage.name
        if destination.exists():
            merge_directory(stage, destination)
        else:
            shutil.move(str(stage), str(destination))

    if STAGES_DIR.exists():
        remaining = list(STAGES_DIR.iterdir())
        if remaining:
            raise RuntimeError(
                f"Unexpected files remain in {STAGES_DIR}: {remaining}"
            )
        STAGES_DIR.rmdir()


def flatten_course_containers() -> None:
    stage_dirs = [
        path
        for path in ROOT.iterdir()
        if path.is_dir() and path.name.startswith("stage-")
    ]

    # Flatten daily content first because days/ is nested inside weeks/.
    day_dirs = []
    for stage in stage_dirs:
        day_dirs.extend(
            path for path in stage.rglob("days") if path.is_dir()
        )

    for container in sorted(
        day_dirs,
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if container.exists():
            flatten_named_container(container, "每日学习路径")

    week_containers = [
        stage / "weeks"
        for stage in stage_dirs
        if (stage / "weeks").is_dir()
    ]

    for container in week_containers:
        flatten_named_container(container, "周学习计划")


def rewrite_markdown_paths() -> None:
    replacements = (
        (
            "[进入 13 周学习计划](weeks/README.md)",
            "各周学习计划见本目录下的 `week-*` 子目录。",
        ),
        (
            "[查看 7 天学习路径](days/README.md)",
            "每日学习内容与索引均直接保存在当前周目录。",
        ),
        ("stages/stage-", "stage-"),
        ("weeks/week-", "week-"),
        ("days/day-", "day-"),
        ("weeks/README.md", "README.md"),
        ("days/README.md", "README.md"),
    )

    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue

        text = read_text(path)
        updated = text

        for old, new in replacements:
            updated = updated.replace(old, new)

        updated = re.sub(r"(?<=\()stages/", "", updated)
        updated = re.sub(r"(?<=\()weeks/", "", updated)
        updated = re.sub(r"(?<=\()days/", "", updated)

        if updated != text:
            write_text(path, updated)


def rewrite_root_readme() -> None:
    path = ROOT / "README.md"
    text = read_text(path)

    pattern = re.compile(
        r"(## 仓库结构\s*\n\s*)```text.*?```",
        flags=re.DOTALL,
    )
    replacement = r"\1" + ROOT_TREE
    updated, count = pattern.subn(replacement, text, count=1)

    if count != 1:
        raise RuntimeError(
            "Could not locate the repository tree in README.md"
        )

    updated = updated.replace("stages/stage-", "stage-")
    updated = updated.replace(
        "5. 数学公式使用标准 Markdown：行内 `$R_t$`，独立公式使用 `$$...$$`。",
        "5. 数学公式使用标准 Markdown：行内 `$R_t$`，独立公式使用 `$$...$$`。\n"
        "6. 每日课程文件直接保存在对应周目录，不再创建 `days/` 中间目录。",
    )

    write_text(path, updated)


def remove_completed_generation_scaffolding() -> None:
    obsolete_files = (
        ROOT / ".github/workflows/generate-complete-learning-stages.yml",
        ROOT / "scripts/generate_stages_06_12.py",
    )

    for path in obsolete_files:
        if path.exists():
            path.unlink()


def validate() -> None:
    forbidden_directories = []

    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name in {"stages", "weeks", "days"}:
            forbidden_directories.append(path.relative_to(ROOT))

    if forbidden_directories:
        raise RuntimeError(
            "Forbidden container directories remain: "
            + ", ".join(map(str, forbidden_directories))
        )

    broken_references = []
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue

        text = read_text(path)
        if re.search(
            r"\]\((?:\./|\.\./)*(?:stages|weeks|days)/",
            text,
        ):
            broken_references.append(path.relative_to(ROOT))

    if broken_references:
        raise RuntimeError(
            "Legacy Markdown links remain: "
            + ", ".join(map(str, broken_references))
        )

    stage_dirs = sorted(
        path
        for path in ROOT.iterdir()
        if path.is_dir() and path.name.startswith("stage-")
    )

    if len(stage_dirs) != 12:
        raise RuntimeError(
            f"Expected 12 stage directories, found {len(stage_dirs)}"
        )

    for stage in stage_dirs:
        if not (stage / "README.md").exists():
            raise RuntimeError(f"Missing stage README: {stage}")

        for week in stage.glob("week-*"):
            if week.is_dir() and not (week / "README.md").exists():
                raise RuntimeError(f"Missing week README: {week}")


def main() -> None:
    move_stages_to_root()
    flatten_course_containers()
    rewrite_markdown_paths()
    rewrite_root_readme()
    remove_completed_generation_scaffolding()
    validate()
    print("Repository structure flattened successfully.")


if __name__ == "__main__":
    main()
