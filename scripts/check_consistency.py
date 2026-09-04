#!/usr/bin/env python3
"""Run dependency-free consistency checks for the goal-orchestrator Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SKILL_NAME = "goal-orchestrator"
POSITIONING = "目标实现推演"
REQUEST_MODES = (
    "solution_design",
    "goal_realization",
    "implementation_orchestration",
)
ORGANIZATION_DEPTHS = (
    "none",
    "responsibility_map",
    "simulated_team",
)
SOLUTION_DEPTHS = (
    "concise",
    "standard",
    "deep",
)
PLANNING_DEPTHS = (
    "light",
    "standard",
    "deep",
)
SIMULATION_DEPTHS = (
    "none",
    "light",
    "structured",
)
SOLUTION_STATUSES = (
    "to_design",
    "partially_defined",
    "fixed",
)
IMPLEMENTATION_DEPTHS = (
    "none",
    "light",
    "detailed",
)
ROLE_TYPES = (
    "orchestrator",
    "specialist",
    "integrator",
    "evaluator",
    "challenger",
)
ROLE_LIFECYCLES = ("persistent", "phase-bound", "on-demand")
DECISION_RIGHT_KEYS = ("can_decide", "must_consult", "must_escalate")
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
    "evals/evals.json",
    "evals/trigger-evals.json",
    "references/examples.md",
    "references/goal-planning-protocol.md",
    "references/output-contracts.md",
    "references/role-schema.md",
    "references/role.schema.json",
    "references/sample-role.json",
    "references/simulation-protocol.md",
    "scripts/check_consistency.py",
)
EXPECTED_EVAL_SCENARIOS = {
    1: ("笔记", "同步", "冲突"),
    2: ("RAW", "Sony", "Nikon", "Fujifilm"),
    3: ("React Native", "Supabase", "Stripe", "十二周"),
    4: ("游泳", "三个月", "四百米"),
    5: ("完整团队", "糖尿病", "用药提醒"),
    6: ("Electron", "Tauri", "明确推荐"),
    9: ("2000", "事业部"),
    10: ("2000", "事业部", "不要实施计划"),
    11: ("重大客诉", "销售", "交付", "产品"),
    12: ("老人", "诈骗", "App"),
    13: ("咖啡店", "三个月", "增长"),
    14: ("考试", "没告诉"),
    15: ("2000", "员工数据", "导入"),
}
DEPTH_EVALS = {
    "concise": (7, "简要"),
    "standard": (1, "给我一份"),
    "deep": (8, "详细"),
}
IGNORED_DIRECTORY_NAMES = {".git", "__pycache__", ".pytest_cache", "node_modules"}


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


def is_ignored(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return any(part in IGNORED_DIRECTORY_NAMES for part in relative.parts)


def check_required_files(root: Path, results: Results) -> None:
    missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    for relative in missing:
        results.fail(f"missing required file: {relative}")
    if not missing:
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
    start_errors = len(results.errors)

    if set(fields) != {"name", "description"}:
        results.fail("SKILL.md frontmatter must contain only name and description")
    if fields.get("name") != SKILL_NAME:
        results.fail(f"SKILL.md name must be {SKILL_NAME!r}")

    description = fields.get("description", "")
    if re.search(r"[A-Za-z]", description):
        results.fail("SKILL.md frontmatter description must be entirely Chinese and contain no Latin letters")
    for phrase in ("一句", "主动理解", "可规划意图", "具体方案", "目标规划", "问题复杂度", "模拟团队", "不替代真实执行", "普通事实问答", "数据导入"):
        if phrase not in description:
            results.fail(f"SKILL.md description is missing intent-and-trigger phrase {phrase!r}")

    if len(text.splitlines()) >= 500:
        results.fail("SKILL.md must remain under 500 lines")
    for concept in (
        *REQUEST_MODES,
        *SOLUTION_STATUSES,
        *SOLUTION_DEPTHS,
        *PLANNING_DEPTHS,
        *SIMULATION_DEPTHS,
        *IMPLEMENTATION_DEPTHS,
        *ORGANIZATION_DEPTHS,
    ):
        if concept not in text:
            results.fail(f"SKILL.md is missing routing concept {concept!r}")
    for concept in (
        "先构造可规划意图",
        "再判断交付意图",
        "Goal Brief",
        "默认下限",
        "短输入不是低复杂度",
        "规模、涉及人员与利益相关者、组织层级、系统耦合、风险、时间跨度、可逆性和持续运营复杂度",
        "推演是对目标、路径或运行机制的前向模拟",
        "风险清单",
        "分清三种组织概念",
        "请求类型不直接决定是否需要组织",
        "未选择 `simulated_team` 时，不创建 `R0`，不补完整角色表，也不意味着不做目标或场景推演",
        "自然表达不等于简略",
        "普通“给我一份方案”的默认值",
        "边界提示不是固定开场",
        'schema_version: "3.3"',
        'schema_version: "3.0"',
        "目标规划的信息价值门",
    ):
        if concept not in text:
            results.fail(f"SKILL.md is missing adaptive invariant {concept!r}")

    required_links = (
        "references/output-contracts.md",
        "references/goal-planning-protocol.md",
        "references/role-schema.md",
        "references/role.schema.json",
        "references/simulation-protocol.md",
        "references/examples.md",
        "assets/orchestration-report-template.md",
    )
    for relative in required_links:
        if f"]({relative})" not in text:
            results.fail(f"SKILL.md must link to {relative}")

    if len(results.errors) == start_errors:
        results.passed("SKILL.md has Chinese discovery metadata plus intent construction, planning, and simulation routing")


def extract_yaml_value(text: str, key: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(key)}:\s*"([^"]*)"\s*$', text, re.MULTILINE)
    return match.group(1) if match else None


def check_openai_yaml(root: Path, results: Results) -> None:
    text = read_text(root / "agents/openai.yaml", results)
    display_name = extract_yaml_value(text, "display_name")
    short_description = extract_yaml_value(text, "short_description")
    default_prompt = extract_yaml_value(text, "default_prompt")
    start_errors = len(results.errors)

    if display_name != POSITIONING:
        results.fail(f"agents/openai.yaml display_name must be {POSITIONING!r}")
    if short_description is None or not 25 <= len(short_description) <= 64:
        results.fail("agents/openai.yaml short_description must contain 25-64 characters")
    if short_description and (
        "理解" not in short_description
        or "方案" not in short_description
        or "可规划意图" not in short_description
        or "专业完整" not in short_description
    ):
        results.fail("agents/openai.yaml short_description must reflect intent-first delivery with adaptive depth")
    if default_prompt is None or "$" + SKILL_NAME not in default_prompt:
        results.fail("agents/openai.yaml default_prompt must mention $" + SKILL_NAME)
    if default_prompt and (
        "自然表达" not in default_prompt
        or "可规划目标" not in default_prompt
        or "直接给出" not in default_prompt
        or "交付物分类或问卷" not in default_prompt
        or "组织只在" not in default_prompt
    ):
        results.fail("agents/openai.yaml default_prompt must drive intent construction before routing without a questionnaire")
    if len(results.errors) == start_errors:
        results.passed("agents/openai.yaml exposes the adaptive Chinese interface")


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
    start_errors = len(results.errors)

    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        results.fail("role.schema.json root must be a closed object schema")
    if tuple(schema.get("required", [])) != ROLE_REQUIRED_FIELDS:
        results.fail("role.schema.json required fields do not match the v3.0 role contract")
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "3.0":
        results.fail("role.schema.json schema_version must remain 3.0")
    if tuple(schema.get("properties", {}).get("role_type", {}).get("enum", ())) != ROLE_TYPES:
        results.fail("role.schema.json role types do not match the canonical v3.0 set")
    if tuple(schema.get("properties", {}).get("lifecycle", {}).get("enum", ())) != ROLE_LIFECYCLES:
        results.fail("role.schema.json role lifecycles do not match the canonical v3.0 set")
    if enum_values(schema, "lifecycle_stages") != LIFECYCLE_STAGES:
        results.fail("role.schema.json lifecycle stages do not match the canonical sequence")
    if enum_values(schema, "contribution_modes") != CONTRIBUTION_MODES:
        results.fail("role.schema.json contribution modes do not match the canonical set")
    decision_schema = schema.get("properties", {}).get("decision_rights", {})
    if tuple(decision_schema.get("required", ())) != DECISION_RIGHT_KEYS:
        results.fail("role.schema.json decision rights do not match the canonical v3.0 keys")

    validation_errors: list[str] = []
    validate_instance(sample, schema, "sample-role", validation_errors)
    for error in validation_errors:
        results.fail(error)
    if sample.get("schema_version") != "3.0":
        results.fail("sample-role.json schema_version must remain 3.0")
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
    role_type_section = role_doc.split("## 角色类型与贡献方式", 1)[-1].split("贡献方式必须来自", 1)[0]
    documented_types = tuple(re.findall(r"^- `([^`]+)`：", role_type_section, re.MULTILINE))
    if documented_types != ROLE_TYPES:
        results.fail(f"role-schema.md role_type list {documented_types!r} does not match schema {ROLE_TYPES!r}")
    for invalid_type in ("planner", "validator", "operator"):
        if f"- `{invalid_type}`：" in role_doc:
            results.fail(f"role-schema.md documents invalid role_type {invalid_type!r}")
    for lifecycle, meaning in (
        ("persistent", "持续参与到最终整合或停止"),
        ("phase-bound", "一个或一组相邻阶段激活"),
        ("on-demand", "质量门、异常、争议、挑战或特定条件触发"),
    ):
        if f"`{lifecycle}`" not in role_doc or meaning not in role_doc:
            results.fail(f"role-schema.md does not accurately document lifecycle {lifecycle!r}")
    for key in DECISION_RIGHT_KEYS:
        if f"- `{key}`：" not in role_doc:
            results.fail(f"role-schema.md does not document decision_rights key {key!r}")
    for concept in ("只在组织深度为 `simulated_team` 时读取", "不创建这里定义的角色对象或 `R0`", "根结构化输出升级到 3.3 不改变角色契约", "真实组织方案，本身不触发本角色协议"):
        if concept not in role_doc:
            results.fail(f"role-schema.md is missing conditional-use concept {concept!r}")

    if len(results.errors) == start_errors:
        results.passed("v3.0 role schema remains valid and is conditional on simulated_team")


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
    allowed = re.compile(r"^(flowchart (LR|RL|TD|TB)|sequenceDiagram|stateDiagram-v2)$")
    total = 0
    start_errors = len(results.errors)
    for path in sorted(root.rglob("*.md")):
        if is_ignored(path, root):
            continue
        relative = str(path.relative_to(root))
        blocks = extract_mermaid_blocks(read_text(path, results), relative, results)
        total += len(blocks)
        for index, block in enumerate(blocks, start=1):
            first = next((line.strip() for line in block.splitlines() if line.strip()), "")
            if not allowed.fullmatch(first):
                results.fail(f"{relative}: Mermaid block {index} has unsupported first line {first!r}")
            if "%%{init" in block or "<br" in block.lower():
                results.fail(f"{relative}: Mermaid block {index} uses fragile renderer-specific syntax")
    if total == 0:
        results.fail("package should retain at least one valid optional Mermaid example")
    elif len(results.errors) == start_errors:
        results.passed(f"{total} optional Mermaid examples use supported fenced syntax")


def check_adaptive_contracts(root: Path, results: Results) -> None:
    paths = (
        "SKILL.md",
        "README.md",
        "assets/orchestration-report-template.md",
        "references/output-contracts.md",
        "references/goal-planning-protocol.md",
        "references/examples.md",
        "references/simulation-protocol.md",
    )
    texts = {relative: read_text(root / relative, results) for relative in paths}
    start_errors = len(results.errors)

    for relative, text in texts.items():
        placeholder = "TO" + "DO"
        if placeholder in text.upper():
            results.fail(f"{relative} contains an unfinished placeholder marker")

    for relative in ("SKILL.md", "assets/orchestration-report-template.md", "references/output-contracts.md"):
        text = texts[relative]
        for mode in REQUEST_MODES:
            if mode not in text:
                results.fail(f"{relative} is missing request mode {mode!r}")
        for depth in SOLUTION_DEPTHS:
            if depth not in text:
                results.fail(f"{relative} is missing solution depth {depth!r}")
        for depth in PLANNING_DEPTHS:
            if depth not in text:
                results.fail(f"{relative} is missing planning depth {depth!r}")
        for depth in SIMULATION_DEPTHS:
            if depth not in text:
                results.fail(f"{relative} is missing simulation depth {depth!r}")
        for depth in ORGANIZATION_DEPTHS:
            if depth not in text:
                results.fail(f"{relative} is missing organization depth {depth!r}")

    contracts = texts["references/output-contracts.md"]
    for label in EVIDENCE_LABELS:
        if label not in contracts:
            results.fail(f"references/output-contracts.md is missing evidence label {label}")
    for phrase in (
        'schema_version: "3.3"',
        'schema_version: "3.0"',
        "普通技术方案、架构比较和简单个人计划不需要固定边界开场",
        "两三步的简单计划直接写出来",
        "仅在用户询问可行性",
        "普通“给我一份方案”的默认值",
        "实施或组织从轻时，应把篇幅保留给用户要的方案",
        "先形成暂定 Goal Brief，再判断交付模式",
        "只有未知会导致完全不同路线、重大不可逆成本或安全、法律、资金风险时，才先问一个问题",
        "`planning_depth`",
        "`simulation_depth` 与 `organization_depth` 独立",
        "风险清单不是推演",
    ):
        if phrase not in contracts:
            results.fail(f"references/output-contracts.md is missing conditional output rule {phrase!r}")

    template = texts["assets/orchestration-report-template.md"]
    for phrase in (
        "模块库，不是固定大纲",
        "删除所有无关模块",
        "方案模块",
        "深入方案扩展模块（按需）",
        "既有方案实施模块",
        "目标实现模块",
        "情景推演带来的修订",
        "完整模拟组织模块（严格按需）",
    ):
        if phrase not in template:
            results.fail(f"report template is missing modular-output phrase {phrase!r}")

    planning_protocol = texts["references/goal-planning-protocol.md"]
    for phrase in ("用于所有 `goal_realization` 请求", "默认先交付再校准", "短输入", "目标状态和运营模型", "向前推演代表性场景", "将发现变成方案修订", "现实第一步"):
        if phrase not in planning_protocol:
            results.fail(f"goal-planning-protocol.md is missing planning invariant {phrase!r}")

    protocol = texts["references/simulation-protocol.md"]
    for phrase in ("仅当组织深度为 `simulated_team` 时使用", "不是目标规划与情景推演的全部协议", "没有选择 `simulated_team` 时不执行本协作协议", "方案或实施重点应先出现"):
        if phrase not in protocol:
            results.fail(f"simulation-protocol.md is missing adaptive boundary {phrase!r}")

    invariant_phrases = {
        "comparison prototype discipline": (
            "运行表现、兼容性或体验",
            "同一代表性真实数据集",
            "保持或切换阈值",
            "最终选型前完成最小可比垂直切片",
            "双候选对照",
            "候选轴",
            "平台轴",
            "两者结果齐备后",
            "初步或倾向性推荐",
            "待填预算变量",
            "全部硬门通过则保持",
            "另一候选",
        ),
        "concise decision closure": (
            "适用边界或升级条件",
            "关键验证门",
        ),
        "visible coordinator and independent validation": (
            "R0",
            "独立验证者",
            "设计者",
            "实现者",
        ),
        "intent construction and scenario revision": (
            "可规划意图",
            "planning_depth",
            "simulation_depth",
            "风险清单",
            "具体修订",
            "现实第一步",
        ),
    }
    invariant_sources = {
        "comparison prototype discipline": (
            "SKILL.md",
            "references/output-contracts.md",
            "references/examples.md",
            "assets/orchestration-report-template.md",
        ),
        "concise decision closure": (
            "SKILL.md",
            "references/output-contracts.md",
            "references/examples.md",
            "assets/orchestration-report-template.md",
        ),
        "visible coordinator and independent validation": (
            "SKILL.md",
            "references/output-contracts.md",
            "references/role-schema.md",
            "references/simulation-protocol.md",
            "references/examples.md",
            "assets/orchestration-report-template.md",
        ),
        "intent construction and scenario revision": (
            "SKILL.md",
            "references/goal-planning-protocol.md",
            "references/output-contracts.md",
        ),
    }
    for invariant, phrases in invariant_phrases.items():
        for relative in invariant_sources[invariant]:
            text = texts.get(relative)
            if text is None:
                text = read_text(root / relative, results)
            missing = [phrase for phrase in phrases if phrase not in text]
            if missing:
                results.fail(
                    f"{relative} is missing {invariant} evidence: {', '.join(repr(item) for item in missing)}"
                )

    if len(results.errors) == start_errors:
        results.passed("cross-file contracts preserve intent-first planning, scenario revision, adaptive routing, concise closure, comparison discipline, and independent validation")


def check_evals(root: Path, results: Results) -> None:
    data = load_json(root / "evals/evals.json", results)
    if not isinstance(data, dict):
        return
    start_errors = len(results.errors)

    if set(data) != {"skill_name", "evals"}:
        results.fail("evals/evals.json top level must contain exactly skill_name and evals")
    if data.get("skill_name") != SKILL_NAME:
        results.fail("evals/evals.json skill_name must be goal-orchestrator")
    evals = data.get("evals")
    if not isinstance(evals, list):
        results.fail("evals/evals.json evals must be an array")
        return
    if len(evals) < 15:
        results.fail("evals/evals.json must retain the original eight cases and add at least seven planning/trigger-boundary scenarios")

    seen_ids: set[int] = set()
    expected_fields = {"id", "prompt", "expected_output", "files", "expectations"}
    for index, eval_case in enumerate(evals):
        location = f"evals/evals.json evals[{index}]"
        if not isinstance(eval_case, dict):
            results.fail(f"{location} must be an object")
            continue
        if set(eval_case) != expected_fields:
            results.fail(f"{location} must contain exactly {sorted(expected_fields)!r}")
        eval_id = eval_case.get("id")
        if not isinstance(eval_id, int) or isinstance(eval_id, bool):
            results.fail(f"{location} id must be an integer")
        elif eval_id in seen_ids:
            results.fail(f"{location} duplicates id {eval_id!r}")
        else:
            seen_ids.add(eval_id)

        prompt = eval_case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip() or "$goal-orchestrator" not in prompt:
            results.fail(f"{location} prompt must be realistic and mention $goal-orchestrator")
        expected_output = eval_case.get("expected_output")
        if not isinstance(expected_output, str) or not expected_output.strip():
            results.fail(f"{location} expected_output must be a non-empty string")
        files = eval_case.get("files")
        if not isinstance(files, list) or not all(isinstance(item, str) and item for item in files):
            results.fail(f"{location} files must be an array of relative file paths")
        elif any(Path(item).is_absolute() for item in files):
            results.fail(f"{location} files must use relative paths")
        else:
            for relative in files:
                if not (root / relative).is_file():
                    results.fail(f"{location} references missing input file {relative!r}")
        expectations = eval_case.get("expectations")
        if not isinstance(expectations, list) or len(expectations) < 4 or not all(
            isinstance(item, str) and item.strip() for item in expectations
        ):
            results.fail(f"{location} expectations must contain at least four verifiable statements")
        elif not any(not re.search(r"不得|不应|不能|无需|不需要|不创建|不引入", item) for item in expectations):
            results.fail(f"{location} must include at least one verifiable positive expectation")

        if isinstance(eval_id, int) and not isinstance(eval_id, bool) and isinstance(prompt, str):
            for term in EXPECTED_EVAL_SCENARIOS.get(eval_id, ()):
                if term not in prompt:
                    results.fail(f"{location} does not preserve scenario term {term!r}")

    cases_by_id = {case.get("id"): case for case in evals if isinstance(case, dict)}
    for depth, (eval_id, prompt_marker) in DEPTH_EVALS.items():
        case = cases_by_id.get(eval_id)
        if not isinstance(case, dict):
            results.fail(f"evals/evals.json must include a {depth} depth scenario with id {eval_id}")
            continue
        if prompt_marker not in case.get("prompt", ""):
            results.fail(f"{depth} depth eval {eval_id} must preserve prompt marker {prompt_marker!r}")

    for depth in ("standard", "deep"):
        eval_id, _ = DEPTH_EVALS[depth]
        expectations = cases_by_id.get(eval_id, {}).get("expectations", [])
        if not any(
            any(term in expectation for term in ("模块", "数据", "接口", "状态", "流程", "架构", "验证"))
            for expectation in expectations
            if isinstance(expectation, str)
        ):
            results.fail(f"{depth} depth eval {eval_id} must include a mechanism-completeness expectation")

    standard_expectations = cases_by_id.get(DEPTH_EVALS["standard"][0], {}).get("expectations", [])
    if not any(
        isinstance(expectation, str) and re.search(r"不得.*(摘要|短答|名词|方向)", expectation)
        for expectation in standard_expectations
    ):
        results.fail("standard depth eval must fail a default solution that is only a short summary")

    team_expectations = cases_by_id.get(5, {}).get("expectations", [])
    for phrase in ("首次提到协调者时明确标识唯一 `R0`", "领域自然的专业职称", "独立验证者不同于其设计者和实现者", "R0 不担任独立验证者"):
        if not any(isinstance(expectation, str) and phrase in expectation for expectation in team_expectations):
            results.fail(f"team eval must cover {phrase!r} without prescribing a domain role name")

    comparison_expectations = cases_by_id.get(6, {}).get("expectations", [])
    for phrase in ("两种候选", "同一代表性真实数据集", "同一目标 Windows 和 macOS", "同一任务与预算", "Electron/Tauri 是候选轴", "Windows/macOS 是两者共同覆盖的平台轴", "最终选型前完成最小可比垂直切片", "不得只验证推荐候选并把另一候选推迟到失败后", "逐项列出 Electron 与 Tauri 各自完成同一端到端任务", "两者结果齐备后才应用阈值", "第二候选设为第一候选失败后的备选", "原型开始前以用户给定值或待填预算变量", "不虚构固定数值", "当前候选全部硬门通过则保持", "另一候选在相同条件下通过", "新增关键兼容或维护阻碍", "初步或倾向性推荐", "不得声称已经证实最终选型"):
        if not any(isinstance(expectation, str) and phrase in expectation for expectation in comparison_expectations):
            results.fail(f"comparison eval must cover prototype control {phrase!r}")

    concise_expectations = cases_by_id.get(7, {}).get("expectations", [])
    for phrase in ("不可省略至少一个适用边界或升级条件", "不可省略一个最关键的原型或验证条件", "一页式简要形态"):
        if not any(isinstance(expectation, str) and phrase in expectation for expectation in concise_expectations):
            results.fail(f"concise eval must cover closure without bloat: {phrase!r}")

    planning_eval_requirements = {
        9: ("不以前置问卷", "深度规划", "阶段成果", "代表性场景", "具体方案修订", "真实组织", "现实第一步"),
        10: ("组织划分", "管理跨度", "真实组织", "不要实施计划", "完整虚拟"),
        11: ("决策链", "具体缺口", "修改", "真实组织运行推演", "不需要创建完整模拟团队"),
        12: ("暂定受益者", "产品方案", "阶段成果", "推演", "修改产品或权限方案"),
        13: ("稳定增长的暂定定义", "领域机制", "判断门", "失败路线", "修改增长指标或促销规则"),
        14: ("一个", "完全不同", "不得连续询问", "不得",),
        15: ("数据导入操作", "不因为出现 2000 条", "不得展开产品方案", "不得创建模拟团队"),
    }
    for eval_id, required_phrases in planning_eval_requirements.items():
        expectations = cases_by_id.get(eval_id, {}).get("expectations", [])
        joined = "\n".join(item for item in expectations if isinstance(item, str))
        for phrase in required_phrases:
            if phrase not in joined:
                results.fail(f"planning eval {eval_id} must cover {phrase!r}")

    if len(results.errors) == start_errors:
        results.passed("canonical behavior evals cover adaptive routing, all solution depths, intent construction, goal planning, scenario revision, and near-neighbor boundaries")


def check_trigger_evals(root: Path, results: Results) -> None:
    cases = load_json(root / "evals/trigger-evals.json", results)
    start_errors = len(results.errors)

    if not isinstance(cases, list):
        results.fail("trigger-evals.json must use the Skill Creator top-level JSON array format")
        return
    if not 18 <= len(cases) <= 24:
        results.fail("trigger-evals.json should contain approximately twenty cases")

    expected_fields = {"query", "should_trigger"}
    positive_prompts: list[str] = []
    negative_prompts: list[str] = []
    for index, case in enumerate(cases):
        location = f"trigger-evals.json[{index}]"
        if not isinstance(case, dict) or set(case) != expected_fields:
            results.fail(f"{location} must contain exactly {sorted(expected_fields)!r}")
            continue
        prompt = case.get("query")
        should_trigger = case.get("should_trigger")
        if not isinstance(prompt, str) or not prompt.strip():
            results.fail(f"{location} query must be a non-empty string")
        elif "$goal-orchestrator" in prompt:
            results.fail(f"{location} must test natural triggering without an explicit skill mention")
        if not isinstance(should_trigger, bool):
            results.fail(f"{location} should_trigger must be boolean")
        elif isinstance(prompt, str):
            (positive_prompts if should_trigger else negative_prompts).append(prompt)

    if not 8 <= len(positive_prompts) <= 12 or not 8 <= len(negative_prompts) <= 12:
        results.fail("trigger-evals.json must include 8-12 positive and 8-12 negative cases")

    positive_text = "\n".join(positive_prompts)
    for phrase in ("我要", "我想", "我的目标是", "事业部", "咖啡店", "App", "组织变革", "游泳", "技术方案", "已经定了"):
        if phrase not in positive_text:
            results.fail(f"positive trigger cases are missing coverage marker {phrase!r}")

    negative_text = "\n".join(negative_prompts)
    for phrase in ("2000 条员工数据", "字段改名", "首都", "单元测试", "翻译", "天气", "迁移脚本", "邮件", "Excel", "报错"):
        if phrase not in negative_text:
            results.fail(f"negative trigger cases are missing near-neighbor marker {phrase!r}")

    if len(results.errors) == start_errors:
        results.passed("Skill Creator trigger evals use the standard array format with balanced goal/solution positives and execution/fact negatives")


def check_relative_links(root: Path, results: Results) -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if is_ignored(path, root):
            continue
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
        if len(text.splitlines()) > 100 and "## Contents" not in text and "## 目录" not in text:
            missing_contents.append(str(path.relative_to(root)))
    for relative in missing_contents:
        results.fail(f"{relative} exceeds 100 lines but has no contents section")
    if not missing_contents:
        results.passed("long reference documents expose a contents section")


def check_empty_files(root: Path, results: Results) -> None:
    empty = [
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and not is_ignored(path, root) and path.stat().st_size == 0
    ]
    for path in empty:
        results.fail(f"empty file: {path}")
    if not empty:
        results.passed("package contains no empty files outside ignored directories")


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
    check_adaptive_contracts(root, results)
    check_evals(root, results)
    check_trigger_evals(root, results)
    check_relative_links(root, results)
    check_reference_structure(root, results)
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
