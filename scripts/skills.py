class Skill:
    """스킬 기본 클래스"""
    def __init__(self, id_, name, power, priority=0, durability_cost=0, description=""):
        self.id = id_ # 스킬 ID
        self.name = name # 스킬 이름
        self.power = power # 스킬 위력
        self.priority = priority # 스킬 우선도
        self.durability_cost = durability_cost  # 내구도 소모량
        self.description = description # 스킬 설명

# ==================== 맨손 스킬 ====================

STRUGGLE = Skill(
    id_="struggle",
    name="발버둥치기",
    power=3,
    priority=0,
    durability_cost=0,
    description="무기가 없을 때 필사적으로 공격한다"
)

# ==================== 무기 스킬 ====================

TEST_SLASH = Skill(
    id_="test_slash",
    name="킹왕짱얼티밋베기",
    power=9999,
    priority=9999,
    durability_cost=0,
    description="강인! 무적! 최강!"
)

SWING = Skill(
    id_="swing",
    name="휘두르기",
    power=10,
    priority=0,
    durability_cost=10,
    description="무기를 휘둘러 적을 공격한다"
)

PIERCE = Skill(
    id_="pierce",
    name="찌르기",
    power=12,
    priority=0,
    durability_cost=8,
    description="날카로운 공격으로 적을 찌른다"
)

SLASH = Skill(
    id_="slash",
    name="베기",
    power=15,
    priority=0,
    durability_cost=15,
    description="강력하게 베어 큰 피해를 준다"
)

# ==================== 초월 스킬 ====================

POWER_STRIKE = Skill(
    id_="power_strike",
    name="★강타",
    power=25,
    priority=0,
    durability_cost=20,
    description="[초월] 온 힘을 실어 강하게 내리친다"
)

RAPID_STAB = Skill(
    id_="rapid_stab",
    name="★연속 찌르기",
    power=18,
    priority=2,
    durability_cost=15,
    description="[초월] 빠르게 연속으로 찌른다"
)

SPIN_SLASH = Skill(
    id_="spin_slash",
    name="★회전 베기",
    power=20,
    priority=0,
    durability_cost=25,
    description="[초월] 몸을 회전하며 주변을 베어버린다"
)

SLIME_BURST = Skill(
    id_="slime_burst",
    name="★슬라임 폭발",
    power=35,
    priority=0,
    durability_cost=30,
    description="[초월] 슬라임의 힘을 폭발시켜 강력한 피해를 입힌다"
)

# ==================== 몬스터 전용 스킬 ====================

BODY_SLAM = Skill(
    id_="body_slam",
    name="몸통박치기",
    power=8,
    priority=0,
    durability_cost=5,
    description="온몸으로 적에게 부딪친다"
)
RED_ATTACK = Skill(
    id_="red_attack",
    name="빨강 어택",
    power=10,
    priority=0,
    durability_cost=8,
    description="빨간 힘으로 적을 공격한다"
)
YELLOW_ATTACK = Skill(
    id_="yellow_attack",
    name="노랑 어택",
    power=10,
    priority=0,
    durability_cost=8,
    description="노란 힘으로 적을 공격한다"
)
BLUE_ATTACK = Skill(
    id_="blue_attack",
    name="파랑 어택",
    power=10,
    priority=0,
    durability_cost=8,
    description="파란 힘으로 적을 공격한다"
)
BLOOD_BITE = Skill(
    id_="blood_bite",
    name="블러드 바이트",
    power=15,
    priority=0,
    durability_cost=12,
    description="피의 송곳니로 적을 물어뜯는다"
)
MAGMA_SHOT = Skill(
    id_="magma_shot",
    name="마그마 샷",
    power=15,
    priority=0,
    durability_cost=12,
    description="마그마 덩어리를 발사한다"
)
SLIME_SLASH = Skill(
    id_="slime_slash",
    name="슬라임 베기",
    power=15,
    priority=0,
    durability_cost=12,
    description="슬라임의 완력으로 적을 베어버린다"
)
RAINBOW_ATTACK = Skill(
    id_="rainbow_attack",
    name="무지개 어택",
    power=7,
    priority=7,
    durability_cost=7,
    description="무지개의 힘으로 매우 빠르게 공격한다."
)
KINGS_SLAM = Skill(
    id_="kings_slam",
    name="왕의 몸통박치기",
    power=30,
    priority=0,
    durability_cost=20,
    description="왕의 몸으로 적에게 강하게 부딪친다"
)

# 스킬 딕셔너리 (ID로 접근 가능)
ALL_SKILLS = {
    "test_slash": TEST_SLASH,
    "swing": SWING,
    "struggle": STRUGGLE,
    "body_slam": BODY_SLAM,
    "red_attack": RED_ATTACK,
    "yellow_attack": YELLOW_ATTACK,
    "blue_attack": BLUE_ATTACK,
    "blood_bite": BLOOD_BITE,
    "magma_shot": MAGMA_SHOT,
    "slime_slash": SLIME_SLASH,
    "pierce": PIERCE,
    "slash": SLASH,
    "rainbow_attack": RAINBOW_ATTACK,
    "kings_slam": KINGS_SLAM,
    # 초월 스킬
    "power_strike": POWER_STRIKE,
    "rapid_stab": RAPID_STAB,
    "spin_slash": SPIN_SLASH,
    "slime_burst": SLIME_BURST,
}