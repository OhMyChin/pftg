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

SLASH1 = Skill(
    id_="slash1",
    name="세로 베기",
    power=15,
    priority=0,
    durability_cost=15,
    description="강력하게 세로로 베어 큰 피해를 준다"
)

SLASH2 = Skill(
    id_="slash2",
    name="가로 베기",
    power=15,
    priority=0,
    durability_cost=15,
    description="강력하게 가로로 베어 큰 피해를 준다"
)

PIERCE = Skill(
    id_="pierce",
    name="찌르기",
    power=8,
    priority=1,
    durability_cost=8,
    description="날카로운 공격으로 빠르게 적을 찌른다"
)

RAPID_STAB = Skill(
    id_="rapid_stab",
    name="연속 찌르기",
    power=16,
    priority=0,
    durability_cost=16,
    description="연속으로 찌른다"
)

PRECISE_SHOT = Skill(
    id_="precise_shot",
    name="정밀 사격",
    power=18,
    priority=1,
    durability_cost=15,
    description="정확하게 조준하여 급소를 노린다"
)

MAGIC_BOLT = Skill(
    id_="magic_bolt",
    name="마력탄",
    power=16,
    priority=0,
    durability_cost=12,
    description="마력을 응축하여 발사한다"
)

SWEEP = Skill(
    id_="sweep",
    name="휩쓸기",
    power=20,
    priority=0,
    durability_cost=18,
    description="긴 창으로 넓게 휩쓴다"
)

# ==================== 영웅 무기 스킬 ====================

# 불의 검 스킬
FLAME_SLASH = Skill(
    id_="flame_slash",
    name="화염 베기",
    power=25,
    priority=0,
    durability_cost=20,
    description="불꽃을 두른 검으로 적을 베어버린다"
)

BURNING_BLADE = Skill(
    id_="burning_blade",
    name="작열의 칼날",
    power=30,
    priority=0,
    durability_cost=25,
    description="타오르는 칼날로 적을 불태운다"
)

# 바람의 활 스킬
WIND_ARROW = Skill(
    id_="wind_arrow",
    name="바람 화살",
    power=20,
    priority=2,
    durability_cost=15,
    description="바람을 실은 화살로 빠르게 사격한다"
)

GALE_SHOT = Skill(
    id_="gale_shot",
    name="질풍 사격",
    power=28,
    priority=1,
    durability_cost=22,
    description="강풍을 일으키며 화살을 연사한다"
)

# 물의 지팡이 스킬
AQUA_BURST = Skill(
    id_="aqua_burst",
    name="물의 폭발",
    power=22,
    priority=0,
    durability_cost=18,
    description="물의 힘을 집중시켜 폭발시킨다"
)

TIDAL_WAVE = Skill(
    id_="tidal_wave",
    name="해일",
    power=32,
    priority=0,
    durability_cost=28,
    description="거대한 파도를 일으켜 적을 덮친다"
)

# 대지의 창 스킬
EARTH_THRUST = Skill(
    id_="earth_thrust",
    name="대지 찌르기",
    power=24,
    priority=0,
    durability_cost=20,
    description="대지의 힘을 담아 강하게 찌른다"
)

QUAKE_STRIKE = Skill(
    id_="quake_strike",
    name="지진 강타",
    power=35,
    priority=-1,
    durability_cost=30,
    description="땅을 흔드는 강력한 일격을 가한다"
)

# ==================== 초월 스킬 ====================

POWER_STRIKE = Skill(
    id_="power_strike",
    name="강타",
    power=25,
    priority=0,
    durability_cost=20,
    description="[초월] 온 힘을 실어 강하게 내리친다"
)

DEEP_WOUND = Skill(
    id_="deep_wound",
    name="깊은 상처",
    power=30,
    priority=0,
    durability_cost=30,
    description="[초월] 정교한 상처를 입힌다."
)

SPIN_SLASH = Skill(
    id_="spin_slash",
    name="회전 베기",
    power=40,
    priority=0,
    durability_cost=30,
    description="[초월] 몸을 회전하며 주변을 베어버린다"
)

FAST_PIERCE = Skill(
    id_="fast_pierce",
    name="초고속 찌르기",
    power=25,
    priority=3,
    durability_cost=15,
    description="[초월] 날카로운 공격으로 적을 찌른다"
)

SLIME_BURST = Skill(
    id_="slime_burst",
    name="슬라임 폭발",
    power=50,
    priority=0,
    durability_cost=30,
    description="[초월] 슬라임의 힘을 폭발시켜 강력한 피해를 입힌다"
)

# 영웅 무기 초월 스킬
INFERNO = Skill(
    id_="inferno",
    name="인페르노",
    power=55,
    priority=0,
    durability_cost=35,
    description="[초월] 지옥의 불꽃으로 모든 것을 태워버린다"
)

STORM_ARROW = Skill(
    id_="storm_arrow",
    name="폭풍의 화살",
    power=45,
    priority=3,
    durability_cost=30,
    description="[초월] 폭풍을 관통하는 궁극의 화살"
)

TSUNAMI = Skill(
    id_="tsunami",
    name="쓰나미",
    power=50,
    priority=0,
    durability_cost=35,
    description="[초월] 모든 것을 집어삼키는 거대한 파도"
)

CONTINENTAL_CRUSH = Skill(
    id_="continental_crush",
    name="대륙 분쇄",
    power=60,
    priority=-2,
    durability_cost=40,
    description="[초월] 대륙을 가를 듯한 궁극의 일격"
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
    "rapid_stab": RAPID_STAB,
    "slash1": SLASH1,
    "slash2": SLASH2,
    "rainbow_attack": RAINBOW_ATTACK,
    "kings_slam": KINGS_SLAM,
    # 영웅 무기 기본 스킬
    "precise_shot": PRECISE_SHOT,
    "magic_bolt": MAGIC_BOLT,
    "sweep": SWEEP,
    # 영웅 무기 스킬
    "flame_slash": FLAME_SLASH,
    "burning_blade": BURNING_BLADE,
    "wind_arrow": WIND_ARROW,
    "gale_shot": GALE_SHOT,
    "aqua_burst": AQUA_BURST,
    "tidal_wave": TIDAL_WAVE,
    "earth_thrust": EARTH_THRUST,
    "quake_strike": QUAKE_STRIKE,
    # 초월 스킬
    "deep_wound": DEEP_WOUND,
    "power_strike": POWER_STRIKE,
    "spin_slash": SPIN_SLASH,
    "fast_pierce": FAST_PIERCE,
    "slime_burst": SLIME_BURST,
    "inferno": INFERNO,
    "storm_arrow": STORM_ARROW,
    "tsunami": TSUNAMI,
    "continental_crush": CONTINENTAL_CRUSH,
}