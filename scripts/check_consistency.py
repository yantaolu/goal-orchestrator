#!/usr/bin/env python3
"""Run dependency-free consistency checks for the Goal Implementation Simulation Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_NAME = "goal-orchestrator"
POSITIONING = "目标实现推演"
TAGLINE = "把一个简单目标转化为经过模拟验证、可用于现实执行的方案"
FRIENDLY_NOTICE = "以下方案通过模拟协作和方案级验证形成，可作为现实实施指南；尚未执行任何现实操作，标注的现实验证事项仍需完成。"
LEGACY_POSITIONING = "虚拟现实"
LEGACY_NOTICE = "SIMULATION ONLY — no external action was performed."
EVIDENCE_LABELS = (
    "USER_FACT",
    "ASSUMPTION",
    "DERIVED",
    "SIMULATED",
    "UNKNOWN",
)
LIFECYCLE_STAGES = (
    "understand",
    "plan",
    "design",
    "produce",
    "validate",
    "integrate",
    "deliver",
    "operate",
    "learn",
)
CONTRIBUTION_MODES = (
    "coordinate",
    "decide",
    "design",
    "produce",
    "validate",
    "integrate",
    "deliver",
    "operate",
    "challenge",
)
ROLE_REQUIRED_FIELDS = (
    "schema_version",
    "role_id",
    "name",
    "role_type",
    "mission",
    "lifecycle",
    "lifecycle_stages",
    "contribution_modes",
    "activation_conditions",
    "deactivation_conditions",
    "responsibilities",
    "capability_ids",
    "subgoal_ids",
    "inputs",
    "expected_outputs",
    "dependencies",
    "collaboration_targets",
    "decision_rights",
    "simulation_actions",
    "forbidden_real_actions",
    "constraints",
    "success_criteria",
    "assumptions",
    "confidence",
)
REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "assets/orchestration-report-template.md",
    "references/examples.md",
    "references/output-contracts.md",
    "references/role-schema.md",
    "references/role.schema.json",
    "references/sample-role.json",
    "references/simulation-protocol.md",
    "scripts/check_consistency.py",
)
TEMPLATE_HEADINGS = (
    "# 目标实现推演",
    "## 我理解的目标",
    "## 先给结论",
    "## 这件事怎样落地",
    "## 需要哪些专业角色",
    "## 方案怎样经过审查",
    "## 现实实施指南",
    "## 必须在现实中验证",
    "## 你现在需要决定",
    "## 结构化附录（可选）",
)


class Results:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.passes: list[str] = []

    def fail(self, message: str) -> None:
        self.errors.append(message)

    def passed(self, message: str) -> None:
        self.passes.append(message)


def read_text(path: Path, results: Results) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        results.fail(f"{path}: not valid UTF-8 ({exc})")
    except OSError as exc:
        results.fail(f"{path}: cannot read ({exc})")
    return ""


def load_json(path: Path, results: Results) -> Any:
    try:
        return json.loads(read_text(path, results))
    except json.JSONDecodeError as exc:
        results.fail(f"{path}: invalid JSON ({exc})")
        return None


def check_required_files(root: Path, results: Results) -> None:
    missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    if missing:
        for relative in missing:
            results.fail(f"missing required file: {relative}")
        return
    results.passed(f"all {len(REQUIRED_FILES)} required files exist")


def parse_frontmatter(text: str, path: Path, results: Results) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        results.fail(f"{path}: frontmatter must start on line 1")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        results.fail(f"{path}: missing closing frontmatter delimiter")
        return {}

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.+)", line)
        if not match:
            results.fail(f"{path}: unsupported frontmatter line: {line!r}")
            continue
        fields[match.group(1)] = match.group(2).strip().strip('"')
    return fields


def check_skill(root: Path, results: Results) -> None:
    path = root / "SKILL.md"
    text = read_text(path, results)
    fields = parse_frontmatter(text, path, results)
    if set(fields) != {"name", "description"}:
        results.fail("SKILL.md frontmatter must contain only name and description")
    if fields.get("name") != SKILL_NAME:
        results.fail(f"SKILL.md name must be {SKILL_NAME!r}")

    description = fields.get("description", "")
    if POSITIONING not in description:
        results.fail(f"SKILL.md description must contain the Chinese positioning {POSITIONING!r}")
    for term in ("goal", "capabilit", "role", "simulat", "implementation", "feasib"):
        if term not in description.lower():
            results.fail(f"SKILL.md description must include trigger concept {term!r}")
    if len(text.splitlines()) >= 500:
        results.fail("SKILL.md must remain under 500 lines")
    if TAGLINE not in text or FRIENDLY_NOTICE not in text:
        results.fail("SKILL.md must contain the Goal Implementation Simulation tagline and friendly boundary")
    for required in (
        "Lifecycle coverage",
        "Production ownership",
        "Validation ownership",
        "Mermaid",
        "Feasibility integrity",
        "Guide usability",
        "execution_mode: simulation",
        "simulation_only: true",
        "deliverable_type: implementation_guide",
        "external_actions_performed: []",
        "plan-viable",
        "conditionally-viable",
        "not-yet-viable",
    ):
        if required not in text:
            results.fail(f"SKILL.md is missing required v3 concept {required!r}")

    required_links = (
        "references/output-contracts.md",
        "references/role-schema.md",
        "references/role.schema.json",
        "references/simulation-protocol.md",
        "references/examples.md",
        "assets/orchestration-report-template.md",
    )
    for relative in required_links:
        if f"]({relative})" not in text:
            results.fail(f"SKILL.md must link to {relative}")

    if not any(message.startswith("SKILL.md") for message in results.errors):
        results.passed("SKILL.md metadata, positioning, routing, and v3 gates are valid")


def extract_yaml_value(text: str, key: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(key)}:\s*"([^"]*)"\s*$', text, re.MULTILINE)
    return match.group(1) if match else None


def check_openai_yaml(root: Path, results: Results) -> None:
    path = root / "agents/openai.yaml"
    text = read_text(path, results)
    display_name = extract_yaml_value(text, "display_name")
    short_description = extract_yaml_value(text, "short_description")
    default_prompt = extract_yaml_value(text, "default_prompt")
    if display_name != POSITIONING:
        results.fail(f"agents/openai.yaml display_name must be {POSITIONING!r}")
    if short_description is None or not 25 <= len(short_description) <= 64:
        results.fail("agents/openai.yaml short_description must contain 25–64 characters")
    if default_prompt is None or "$" + SKILL_NAME not in default_prompt:
        results.fail("agents/openai.yaml default_prompt must mention $" + SKILL_NAME)
    if display_name and short_description and default_prompt:
        results.passed("agents/openai.yaml exposes the Goal Implementation Simulation interface")


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_instance(value: Any, schema: dict[str, Any], location: str, errors: list[str]) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: {value!r} is not in the allowed enum")

    expected_type = schema.get("type")
    if expected_type and not type_matches(value, expected_type):
        errors.append(f"{location}: expected {expected_type}, got {type(value).__name__}")
        return

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{location}: string is shorter than minLength")
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(f"{location}: {value!r} does not match {pattern!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{location}: value is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{location}: value is above maximum")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: array has fewer than minItems")
        if schema.get("uniqueItems"):
            serial = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(serial) != len(set(serial)):
                errors.append(f"{location}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_instance(item, item_schema, f"{location}[{index}]", errors)

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{location}: missing required property {required!r}")
        if schema.get("additionalProperties") is False:
            for key in sorted(set(value) - set(properties)):
                errors.append(f"{location}: unexpected property {key!r}")
        for key, child in value.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                validate_instance(child, child_schema, f"{location}.{key}", errors)


def enum_values(schema: dict[str, Any], property_name: str) -> tuple[str, ...]:
    property_schema = schema.get("properties", {}).get(property_name, {})
    item_schema = property_schema.get("items", {})
    return tuple(item_schema.get("enum", ()))


def check_role_contract(root: Path, results: Results) -> None:
    schema = load_json(root / "references/role.schema.json", results)
    sample = load_json(root / "references/sample-role.json", results)
    if not isinstance(schema, dict) or not isinstance(sample, dict):
        return

    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        results.fail("role.schema.json root must be a closed object schema")
    if tuple(schema.get("required", [])) != ROLE_REQUIRED_FIELDS:
        results.fail("role.schema.json required fields do not match the v3 role contract")
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "3.0":
        results.fail("role.schema.json schema_version must be 3.0")
    if enum_values(schema, "lifecycle_stages") != LIFECYCLE_STAGES:
        results.fail("role.schema.json lifecycle stages do not match the canonical sequence")
    if enum_values(schema, "contribution_modes") != CONTRIBUTION_MODES:
        results.fail("role.schema.json contribution modes do not match the canonical set")

    validation_errors: list[str] = []
    validate_instance(sample, schema, "sample-role", validation_errors)
    for error in validation_errors:
        results.fail(error)
    if not validation_errors:
        results.passed("sample-role.json validates against the v3 role schema")

    if "produce" not in sample.get("lifecycle_stages", []):
        results.fail("sample-role.json must demonstrate lifecycle production")
    if "produce" not in sample.get("contribution_modes", []):
        results.fail("sample-role.json must demonstrate a producer role")
    if not sample.get("simulation_actions") or not sample.get("forbidden_real_actions"):
        results.fail("sample-role.json must distinguish simulation and forbidden real actions")
    outputs = sample.get("expected_outputs", [])
    if not outputs or not outputs[0].get("independent_validator_ids"):
        results.fail("sample-role.json must demonstrate independent validation ownership")
    if not outputs or outputs[0].get("created_in_simulation") is not True:
        results.fail("sample-role.json output must be marked created_in_simulation")

    role_doc = read_text(root / "references/role-schema.md", results)
    for field in ROLE_REQUIRED_FIELDS:
        if f"`{field}`" not in role_doc:
            results.fail(f"role-schema.md does not document field {field}")
    if all(f"`{field}`" in role_doc for field in ROLE_REQUIRED_FIELDS):
        results.passed("role-schema.md documents every canonical v3 role field")


def extract_mermaid_blocks(text: str, source: str, results: Results) -> list[str]:
    blocks: list[str] = []
    active: list[str] | None = None
    start_line = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if active is None:
            if line.strip() == "```mermaid":
                active = []
                start_line = line_number
            continue
        if line.strip() == "```":
            blocks.append("\n".join(active).strip())
            active = None
            continue
        if line.strip().startswith("```"):
            results.fail(f"{source}:{line_number}: nested code fence inside Mermaid block")
        active.append(line)
    if active is not None:
        results.fail(f"{source}:{start_line}: unclosed Mermaid block")
    return blocks


def check_mermaid(root: Path, results: Results) -> None:
    requirements = {
        "README.md": 1,
        "assets/orchestration-report-template.md": 2,
        "references/examples.md": 3,
        "references/output-contracts.md": 1,
        "references/role-schema.md": 1,
        "references/simulation-protocol.md": 2,
    }
    allowed = re.compile(r"^(flowchart (LR|RL|TD|TB)|sequenceDiagram|stateDiagram-v2)$")
    total = 0
    mermaid_error_count = len(results.errors)
    for relative, minimum in requirements.items():
        text = read_text(root / relative, results)
        blocks = extract_mermaid_blocks(text, relative, results)
        if len(blocks) < minimum:
            results.fail(f"{relative}: expected at least {minimum} Mermaid block(s)")
        total += len(blocks)
        for index, block in enumerate(blocks, start=1):
            first = next((line.strip() for line in block.splitlines() if line.strip()), "")
            if not allowed.fullmatch(first):
                results.fail(f"{relative}: Mermaid block {index} has unsupported first line {first!r}")
            if "%%{init" in block or "<br" in block.lower():
                results.fail(f"{relative}: Mermaid block {index} uses fragile renderer-specific syntax")
    if total and len(results.errors) == mermaid_error_count:
        results.passed(f"{total} Mermaid diagrams use supported fenced syntax")


def check_user_layer(root: Path, results: Results) -> None:
    template = read_text(root / "assets/orchestration-report-template.md", results)
    positions: list[int] = []
    for heading in TEMPLATE_HEADINGS:
        index = template.find(heading)
        if index < 0:
            results.fail(f"report template is missing heading {heading!r}")
        positions.append(index)
    if all(index >= 0 for index in positions) and positions != sorted(positions):
        results.fail("report template headings are not in the user-first order")

    appendix_marker = "## 结构化附录（可选）"
    frontstage = template.split(appendix_marker, 1)[0]
    internal_id = re.search(r"\b(?:SG|CAP|ART|EV|RSK)[1-9][0-9]*\b", frontstage)
    if internal_id:
        results.fail(f"report frontstage exposes internal ID {internal_id.group(0)!r}")
    table_lines = [line for line in frontstage.splitlines() if line.lstrip().startswith("|")]
    if table_lines:
        results.fail("report frontstage must not use tables; reserve them for the optional appendix")
    if FRIENDLY_NOTICE not in frontstage:
        results.fail("report frontstage is missing the friendly localized notice")
    if frontstage.count(FRIENDLY_NOTICE) != 1:
        results.fail("report frontstage must contain the friendly localized notice exactly once")
    for discouraged in ("虚拟团队", "虚拟开发", "虚拟测试", "虚拟角色"):
        if discouraged in frontstage:
            results.fail(f"report frontstage repeats legacy wording {discouraged!r}")

    contracts = read_text(root / "references/output-contracts.md", results)
    for concept in (
        "Frontstage user contract",
        "Progressive disclosure",
        "Mermaid contract",
        "feasibility_assessment",
        "implementation_guide",
        "reality_checks_required",
        "execution_mode: simulation",
        "simulation_only: true",
        "deliverable_type: implementation_guide",
        "external_actions_performed: []",
    ):
        if concept not in contracts:
            results.fail(f"output-contracts.md is missing user-layer concept {concept!r}")
    if not any("frontstage" in message.lower() or "template" in message.lower() for message in results.errors):
        results.passed("frontstage output is plan-first, plain-language, visual, and separated from audit data")


def check_raw_regression_example(root: Path, results: Results) -> None:
    text = read_text(root / "references/examples.md", results)
    required = (
        "macOS",
        "Sony",
        "Nikon",
        "Fujifilm",
        "macOS 应用开发工程师",
        "质量与相机兼容性测试工程师",
        "发布与持续兼容负责人",
        "目标实现协调者",
        "有条件可行",
        "现实实施指南",
        "退回",
        "尚未执行任何现实操作",
    )
    missing = [term for term in required if term not in text]
    for term in missing:
        results.fail(f"RAW regression example is missing {term!r}")
    if not missing:
        results.passed("RAW app regression example includes a verdict, guide, complete roles, and target brands")


def check_mt5_regression_example(root: Path, results: Results) -> None:
    text = read_text(root / "references/examples.md", results)
    required = (
        "MT5",
        "MQL5 developer",
        "independent data and backtest validator",
        "risk engineer",
        "deployment and monitoring owner",
        "conditionally-viable",
        "cannot claim profitability",
        "前向测试",
        "停机门",
    )
    missing = [term for term in required if term not in text]
    for term in missing:
        results.fail(f"MT5 regression example is missing {term!r}")
    if not missing:
        results.passed("MT5 example preserves development, independent validation, risk, operations, and evidence boundaries")


def check_relative_links(root: Path, results: Results) -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []
    for path in sorted(root.rglob("*.md")):
        text = read_text(path, results)
        for raw_target in pattern.findall(text):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith("#"):
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            file_target = target.split("#", 1)[0]
            if not (path.parent / file_target).resolve().is_file():
                broken.append(f"{path.relative_to(root)} -> {target}")
    for item in broken:
        results.fail(f"broken relative link: {item}")
    if not broken:
        results.passed("all relative Markdown links resolve")


def check_reference_structure(root: Path, results: Results) -> None:
    missing_contents: list[str] = []
    for path in sorted((root / "references").glob("*.md")):
        text = read_text(path, results)
        if len(text.splitlines()) > 100 and "## Contents" not in text:
            missing_contents.append(str(path.relative_to(root)))
    for relative in missing_contents:
        results.fail(f"{relative} exceeds 100 lines but has no Contents section")
    if not missing_contents:
        results.passed("long reference documents expose a Contents section")


def check_cross_file_contracts(root: Path, results: Results) -> None:
    core = (
        "SKILL.md",
        "README.md",
        "assets/orchestration-report-template.md",
        "references/output-contracts.md",
        "references/examples.md",
        "references/simulation-protocol.md",
    )
    texts = {relative: read_text(root / relative, results) for relative in core}
    cross_error_count = len(results.errors)
    for relative, text in texts.items():
        if POSITIONING not in text:
            results.fail(f"{relative} is missing the positioning {POSITIONING!r}")
        if LEGACY_POSITIONING in text:
            results.fail(f"{relative} still contains the legacy positioning {LEGACY_POSITIONING!r}")
        if LEGACY_NOTICE in text:
            results.fail(f"{relative} still contains the legacy fixed English notice")
        if "simulated_outcome" in text:
            results.fail(f"{relative} still uses legacy root field 'simulated_outcome'")

    for relative in ("references/output-contracts.md",):
        for label in EVIDENCE_LABELS:
            if label not in texts[relative]:
                results.fail(f"{relative} is missing evidence label {label}")

    docs = "\n".join(texts.values())
    for stage in LIFECYCLE_STAGES:
        if stage not in docs:
            results.fail(f"cross-file lifecycle contract is missing {stage!r}")

    placeholder = "TO" + "DO"
    for relative, text in texts.items():
        if placeholder in text.upper():
            results.fail(f"{relative} contains an unfinished placeholder marker")

    if len(results.errors) == cross_error_count:
        results.passed("positioning, feasibility language, lifecycle model, evidence, and boundary are consistent")


def check_empty_files(root: Path, results: Results) -> None:
    empty = [path.relative_to(root) for path in root.rglob("*") if path.is_file() and path.stat().st_size == 0]
    for path in empty:
        results.fail(f"empty file: {path}")
    if not empty:
        results.passed("package contains no empty files")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the goal-orchestrator Skill directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.skill_root.expanduser().resolve()
    results = Results()

    if not root.is_dir():
        print(f"[FAIL] Skill root is not a directory: {root}", file=sys.stderr)
        return 2

    check_required_files(root, results)
    check_skill(root, results)
    check_openai_yaml(root, results)
    check_role_contract(root, results)
    check_mermaid(root, results)
    check_user_layer(root, results)
    check_raw_regression_example(root, results)
    check_mt5_regression_example(root, results)
    check_relative_links(root, results)
    check_reference_structure(root, results)
    check_cross_file_contracts(root, results)
    check_empty_files(root, results)

    for message in results.passes:
        print(f"[PASS] {message}")
    if results.errors:
        for message in results.errors:
            print(f"[FAIL] {message}", file=sys.stderr)
        print(f"Consistency check failed with {len(results.errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Consistency check passed: {len(results.passes)} check groups, 0 errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
