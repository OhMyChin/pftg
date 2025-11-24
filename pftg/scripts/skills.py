# scripts/skills.py

class Skill:
    """스킬 기본 클래스"""
    def __init__(self, id_, name, power, priority=0, durability_cost=0, description=""):
        self.id = id_
        self.name = name
        self.power = power
        self.priority = priority
        self.durability_cost = durability_cost  # 내구도 소모량
        self.description = description

# ==================== 기본 무기 스킬 ====================

SWING = Skill(
    id_="swing",
    name="휘두르기",
    power=10,
    priority=10,
    durability_cost=10,
    description="무기를 휘둘러 적을 공격한다"
)

# ==================== 맨손 스킬 ====================

STRUGGLE = Skill(
    id_="struggle",
    name="발버둥치기",
    power=3,
    priority=10,
    durability_cost=0,
    description="무기가 없을 때 필사적으로 공격한다"
)

# ==================== 몬스터 전용 스킬 ====================

BODY_SLAM = Skill(
    id_="body_slam",
    name="몸통박치기",
    power=8,
    priority=5,
    durability_cost=0,  # 몬스터의 신체 공격은 내구도 소모 없음
    description="온몸으로 적에게 부딪친다"
)

# ==================== 향후 확장용 스킬 예시 ====================

PIERCE = Skill(
    id_="pierce",
    name="찌르기",
    power=12,
    priority=8,
    durability_cost=8,
    description="날카로운 공격으로 적을 찌른다"
)

SLASH = Skill(
    id_="slash",
    name="베기",
    power=15,
    priority=5,
    durability_cost=15,
    description="강력하게 베어 큰 피해를 준다"
)

QUICK_STRIKE = Skill(
    id_="quick_strike",
    name="빠른 일격",
    power=6,
    priority=15,
    durability_cost=5,
    description="빠르게 공격하여 선제권을 잡는다"
)

# 스킬 딕셔너리 (ID로 접근 가능)
ALL_SKILLS = {
    "swing": SWING,
    "struggle": STRUGGLE,
    "body_slam": BODY_SLAM,
    "pierce": PIERCE,
    "slash": SLASH,
    "quick_strike": QUICK_STRIKE,
}