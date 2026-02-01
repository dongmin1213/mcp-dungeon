"""v5.0 속성 시스템"""
from typing import Any, Optional

# 속성 아이콘
ELEMENT_ICONS = {
    "physical": "⚔️",
    "fire": "🔥",
    "ice": "🧊",
    "lightning": "⚡",
    "poison": "🟢",
    "holy": "✨",
    "dark": "💀",
}

# 속성 이름
ELEMENT_NAMES = {
    "physical": "물리",
    "fire": "화염",
    "ice": "냉기",
    "lightning": "번개",
    "poison": "독",
    "holy": "신성",
    "dark": "암흑",
}


def calculate_elemental_damage(
    base_damage: int,
    element: Optional[str],
    target: Any,
) -> tuple[int, str]:
    """
    속성 데미지 계산

    Args:
        base_damage: 기본 데미지
        element: 공격 속성 (None이면 무속성)
        target: 대상 (weaknesses, resistances, immunities 속성 필요)

    Returns:
        (최종 데미지, 메시지)
    """
    if not element:
        return base_damage, ""

    # 대상의 속성 정보 가져오기
    weaknesses = getattr(target, "weaknesses", []) or []
    resistances = getattr(target, "resistances", []) or []
    immunities = getattr(target, "immunities", []) or []

    icon = ELEMENT_ICONS.get(element, "")
    name = ELEMENT_NAMES.get(element, element)

    # 면역
    if element in immunities:
        return 0, f"{icon} {name} 면역! (무효)"

    # 약점 (1.5배)
    if element in weaknesses:
        damage = int(base_damage * 1.5)
        return damage, f"{icon} 약점! (+50%)"

    # 저항 (0.5배)
    if element in resistances:
        damage = int(base_damage * 0.5)
        return damage, f"{icon} 저항! (-50%)"

    # 일반
    return base_damage, ""


def get_element_icon(element: Optional[str]) -> str:
    """속성 아이콘 반환"""
    if not element:
        return ""
    return ELEMENT_ICONS.get(element, "")


def get_element_name(element: Optional[str]) -> str:
    """속성 이름 반환"""
    if not element:
        return "무속성"
    return ELEMENT_NAMES.get(element, element)


def get_weakness_hint(target: Any) -> str:
    """대상의 약점/저항 힌트 반환"""
    weaknesses = getattr(target, "weaknesses", []) or []
    resistances = getattr(target, "resistances", []) or []
    immunities = getattr(target, "immunities", []) or []

    hints = []

    if weaknesses:
        weak_names = [f"{ELEMENT_ICONS.get(e, '')} {ELEMENT_NAMES.get(e, e)}" for e in weaknesses]
        hints.append(f"약점: {', '.join(weak_names)}")

    if resistances:
        resist_names = [f"{ELEMENT_ICONS.get(e, '')} {ELEMENT_NAMES.get(e, e)}" for e in resistances]
        hints.append(f"저항: {', '.join(resist_names)}")

    if immunities:
        immune_names = [f"{ELEMENT_ICONS.get(e, '')} {ELEMENT_NAMES.get(e, e)}" for e in immunities]
        hints.append(f"면역: {', '.join(immune_names)}")

    return " | ".join(hints) if hints else ""
