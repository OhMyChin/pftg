class Skill:
    """스킬 기본 클래스"""
    def __init__(self, id_, name, power, priority=0, durability_cost=0, description=""):
        self.id = id_ # 스킬 ID
        self.name = name # 스킬 이름
        self.power = power # 스킬 위력
        self.priority = priority # 스킬 우선도
        self.durability_cost = durability_cost  # 내구도 소모량
        self.description = description # 스킬 설명


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                              맨손 스킬                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

STRUGGLE = Skill(
    id_="struggle",
    name="발버둥치기",
    power=3,
    priority=0,
    durability_cost=0,
    description="무기가 없을 때 필사적으로 공격한다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                            테스트 스킬                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

TEST_SLASH = Skill(
    id_="test_slash",
    name="킹왕짱얼티밋베기",
    power=9999,
    priority=9999,
    durability_cost=0,
    description="강인! 무적! 최강!"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         일반 등급 무기 스킬                                 ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  무기: 나무 막대기, 녹슨 단검, 기본 창, 소박한 지팡이, 수제 활               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# 나무 막대기 스킬
SWING = Skill(
    id_="swing",
    name="휘두르기",
    power=10,
    priority=0,
    durability_cost=10,
    description="무기를 휘둘러 적을 공격한다"
)

# 녹슨 단검 스킬
PIERCE = Skill(
    id_="pierce",
    name="찌르기",
    power=8,
    priority=1,
    durability_cost=8,
    description="날카로운 공격으로 빠르게 적을 찌른다"
)

# 기본 창 스킬
SWEEP = Skill(
    id_="sweep",
    name="휩쓸기",
    power=20,
    priority=0,
    durability_cost=18,
    description="긴 창으로 넓게 휩쓴다"
)

# 소박한 지팡이 스킬
MAGIC_BOLT = Skill(
    id_="magic_bolt",
    name="마력탄",
    power=16,
    priority=0,
    durability_cost=12,
    description="마력을 응축하여 발사한다"
)

# 수제 활 스킬
PRECISE_SHOT = Skill(
    id_="precise_shot",
    name="정밀 사격",
    power=18,
    priority=1,
    durability_cost=15,
    description="정확하게 조준하여 급소를 노린다"
)

# -------------------- 일반 무기 초월 스킬 --------------------

# 나무 막대기 초월
POWER_STRIKE = Skill(
    id_="power_strike",
    name="강타",
    power=25,
    priority=0,
    durability_cost=20,
    description="[초월] 온 힘을 실어 강하게 내리친다"
)

# 녹슨 단검 초월
DEEP_WOUND = Skill(
    id_="deep_wound",
    name="깊은 상처",
    power=30,
    priority=0,
    durability_cost=30,
    description="[초월] 정교한 상처를 입힌다."
)

# 기본 창 초월
SPEAR_CHARGE = Skill(
    id_="spear_charge",
    name="창 돌진",
    power=30,
    priority=1,
    durability_cost=25,
    description="[초월] 창을 앞세워 적에게 돌진한다"
)

# 소박한 지팡이 초월
MANA_BURST = Skill(
    id_="mana_burst",
    name="마나 폭발",
    power=28,
    priority=0,
    durability_cost=20,
    description="[초월] 마력을 폭발시켜 적에게 큰 피해를 입힌다"
)

# 수제 활 초월
ARROW_RAIN = Skill(
    id_="arrow_rain",
    name="화살비",
    power=32,
    priority=0,
    durability_cost=25,
    description="[초월] 하늘에서 화살비를 쏟아붓는다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         희귀 등급 무기 스킬                                 ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  무기: 철 검, 레이피어                                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# 철 검 스킬
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

# 레이피어 스킬 (pierce는 일반에서 정의됨)
RAPID_STAB = Skill(
    id_="rapid_stab",
    name="연속 찌르기",
    power=16,
    priority=0,
    durability_cost=16,
    description="연속으로 찌른다"
)

# -------------------- 희귀 무기 초월 스킬 --------------------

# 철 검 초월
SPIN_SLASH = Skill(
    id_="spin_slash",
    name="회전 베기",
    power=40,
    priority=0,
    durability_cost=30,
    description="[초월] 몸을 회전하며 주변을 베어버린다"
)

# 레이피어 초월
FAST_PIERCE = Skill(
    id_="fast_pierce",
    name="초고속 찌르기",
    power=25,
    priority=3,
    durability_cost=15,
    description="[초월] 날카로운 공격으로 적을 찌른다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         영웅 등급 무기 스킬                                 ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  무기: 불의 검, 바람의 활, 물의 지팡이, 대지의 폴암                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# -------------------- 불의 검 스킬 --------------------
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

# 불의 검 초월
INFERNO = Skill(
    id_="inferno",
    name="인페르노",
    power=55,
    priority=0,
    durability_cost=35,
    description="[초월] 지옥의 불꽃으로 모든 것을 태워버린다"
)

# -------------------- 바람의 활 스킬 --------------------
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

# 바람의 활 초월
STORM_ARROW = Skill(
    id_="storm_arrow",
    name="폭풍의 화살",
    power=45,
    priority=3,
    durability_cost=30,
    description="[초월] 폭풍을 관통하는 궁극의 화살"
)

# -------------------- 물의 지팡이 스킬 --------------------
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

# 물의 지팡이 초월
TSUNAMI = Skill(
    id_="tsunami",
    name="쓰나미",
    power=50,
    priority=0,
    durability_cost=35,
    description="[초월] 모든 것을 집어삼키는 거대한 파도"
)

# -------------------- 대지의 폴암 스킬 --------------------
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

# 대지의 폴암 초월
CONTINENTAL_CRUSH = Skill(
    id_="continental_crush",
    name="대륙 분쇄",
    power=60,
    priority=-2,
    durability_cost=40,
    description="[초월] 대륙을 가를 듯한 궁극의 일격"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                     영웅 등급 보스 드롭 무기 스킬                            ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  무기: 킹 슬라임의 지팡이, 황금왕의 검, 뮤턴트의 대도끼                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# -------------------- 킹 슬라임의 지팡이 스킬 --------------------
# blood_bite, magma_shot, slime_slash는 몬스터 스킬에서 정의

# 킹 슬라임의 지팡이 초월
SLIME_BURST = Skill(
    id_="slime_burst",
    name="슬라임 폭발",
    power=50,
    priority=0,
    durability_cost=30,
    description="[초월] 슬라임의 힘을 폭발시켜 강력한 피해를 입힌다"
)

# -------------------- 황금왕의 검 스킬 --------------------
# golden_slash, sword_rain, kings_judgment는 몬스터 스킬에서 정의

# 황금왕의 검 초월
GOLDEN_RULE = Skill(
    id_="golden_rule",
    name="황금률",
    power=0,
    priority=2,
    durability_cost=-50,
    description="[초월] 검에 부여된 황금의 축복으로 내구도를 회복시킨다."
)

# -------------------- 뮤턴트의 대도끼 스킬 --------------------
GIANT_CLEAVE = Skill(
    id_="giant_cleave",
    name="거인 가르기",
    power=28,
    priority=0,
    durability_cost=22,
    description="거대한 도끼로 적을 위에서 아래로 내려찍는다"
)

WHIRLWIND_AXE = Skill(
    id_="whirlwind_axe",
    name="선풍 도끼",
    power=32,
    priority=0,
    durability_cost=25,
    description="도끼를 회전시켜 주변을 휩쓴다"
)

EXECUTIONER = Skill(
    id_="executioner",
    name="처형자의 일격",
    power=38,
    priority=-1,
    durability_cost=30,
    description="처형자처럼 목을 노리는 강력한 일격"
)

# 뮤턴트의 대도끼 초월
TITAN_CRUSH = Skill(
    id_="titan_crush",
    name="타이탄 크러쉬",
    power=55,
    priority=-2,
    durability_cost=40,
    description="[초월] 거인의 힘을 담아 대지를 박살낸다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         전설 등급 무기 스킬                                 ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  무기: 엑스칼리버, 마공학 해머                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# -------------------- 엑스칼리버 스킬 --------------------
HOLY_SLASH = Skill(
    id_="holy_slash",
    name="성스러운 베기",
    power=40,
    priority=1,
    durability_cost=30,
    description="신성한 빛을 담은 검으로 적을 베어낸다"
)

LIGHT_BURST = Skill(
    id_="light_burst",
    name="빛의 폭발",
    power=50,
    priority=0,
    durability_cost=40,
    description="검에서 눈부신 빛을 폭발시켜 적을 공격한다"
)

DIVINE_JUDGMENT = Skill(
    id_="divine_judgment",
    name="신성한 심판",
    power=65,
    priority=0,
    durability_cost=55,
    description="하늘의 심판을 내려 적을 정화한다"
)

# 엑스칼리버 초월 (패시브 - 내구도 회복)
BLESSING_OF_LIGHT = Skill(
    id_="blessing_of_light",
    name="빛의 축복",
    power=0,
    priority=2,
    durability_cost=-30,
    description="성스러운 빛으로 검을 정화하여 내구도를 회복한다"
)

# -------------------- 마공학 해머 스킬 --------------------
HEXTECH_STRIKE = Skill(
    id_="hextech_strike",
    name="헥스텍 스트라이크",
    power=35,
    priority=0,
    durability_cost=25,
    description="마법 기술이 깃든 해머로 적을 강타한다"
)

ENERGY_WAVE = Skill(
    id_="energy_wave",
    name="에너지 파동",
    power=42,
    priority=0,
    durability_cost=30,
    description="해머에서 에너지 파동을 발사한다"
)

OVERCHARGE_SMASH = Skill(
    id_="overcharge_smash",
    name="과충전 스매시",
    power=50,
    priority=-1,
    durability_cost=38,
    description="과충전된 에너지로 강력하게 내리친다"
)

# 마공학 해머 내구도 회복 스킬
CORE_CHARGE = Skill(
    id_="core_charge",
    name="코어 충전",
    power=0,
    priority=2,
    durability_cost=-40,
    description="헥스텍 코어의 에너지를 충전하여 내구도를 회복한다"
)

# ※ 전설 무기는 초월 시 액티브 스킬이 아닌 패시브를 얻음
# 마공학 해머 초월 패시브: "overcharge" (내구도 70% 이하 시 공격력 증가)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       몬스터 전용 스킬 (슬라임)                             ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  슬라임, 빨간/노란/파란 슬라임, 블러드/마그마/소드/무지개 슬라임, 킹 슬라임   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

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


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       몬스터 전용 스킬 (고블린)                             ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  고블린, 궁수/도적/전사/마법사 고블린, 뮤턴트 고블린                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

CLUB_SWING = Skill(
    id_="club_swing",
    name="몽둥이 휘두르기",
    power=12,
    priority=0,
    durability_cost=8,
    description="몽둥이로 적을 휘둘러 친다"
)

GOBLIN_ARROW = Skill(
    id_="goblin_arrow",
    name="고블린 화살",
    power=14,
    priority=1,
    durability_cost=10,
    description="조잡한 화살을 빠르게 쏜다"
)

SNEAK_ATTACK = Skill(
    id_="sneak_attack",
    name="기습",
    power=16,
    priority=2,
    durability_cost=12,
    description="그림자에서 뛰쳐나와 기습한다"
)

STEAL = Skill(
    id_="steal",
    name="훔치기",
    power=8,
    priority=1,
    durability_cost=5,
    description="적의 물건을 훔치려 한다"
)

AXE_SLASH = Skill(
    id_="axe_slash",
    name="도끼 베기",
    power=18,
    priority=0,
    durability_cost=15,
    description="날카로운 도끼로 적을 벤다"
)

SHIELD_BASH = Skill(
    id_="shield_bash",
    name="방패 강타",
    power=14,
    priority=0,
    durability_cost=10,
    description="방패로 적을 강타한다"
)

FIREBALL = Skill(
    id_="fireball",
    name="파이어볼",
    power=20,
    priority=0,
    durability_cost=15,
    description="불꽃 구체를 발사한다"
)

DARK_MAGIC = Skill(
    id_="dark_magic",
    name="암흑 마법",
    power=16,
    priority=1,
    durability_cost=12,
    description="어둠의 마법으로 공격한다"
)

# 뮤턴트 고블린 보스 스킬
MUTANT_SMASH = Skill(
    id_="mutant_smash",
    name="뮤턴트 스매시",
    power=30,
    priority=0,
    durability_cost=20,
    description="거대한 주먹으로 내리친다"
)

BERSERK_RAGE = Skill(
    id_="berserk_rage",
    name="광폭화",
    power=40,
    priority=-1,
    durability_cost=30,
    description="광기에 휩싸여 폭주한다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      몬스터 전용 스킬 (스켈레톤)                            ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  스켈레톤, 머슬/사이킥/다크/윙 스켈레톤, 황금왕                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

BONE_STRIKE = Skill(
    id_="bone_strike",
    name="뼈 후려치기",
    power=18,
    priority=0,
    durability_cost=10,
    description="뼈를 휘둘러 적을 공격한다"
)

MUSCLE_PUNCH = Skill(
    id_="muscle_punch",
    name="머슬 펀치",
    power=25,
    priority=0,
    durability_cost=15,
    description="근육의 힘을 담은 강력한 주먹"
)

MUSCLE_CHARGE = Skill(
    id_="muscle_charge",
    name="머슬 돌진",
    power=30,
    priority=-1,
    durability_cost=20,
    description="온 몸의 근육으로 돌진한다"
)

PSYCHIC_WAVE = Skill(
    id_="psychic_wave",
    name="사이킥 웨이브",
    power=22,
    priority=1,
    durability_cost=12,
    description="염동력으로 충격파를 발사한다"
)

MIND_CRUSH = Skill(
    id_="mind_crush",
    name="마인드 크러쉬",
    power=28,
    priority=0,
    durability_cost=18,
    description="정신력으로 적을 압박한다"
)

DARK_CLAW = Skill(
    id_="dark_claw",
    name="다크 클로",
    power=24,
    priority=0,
    durability_cost=15,
    description="어둠의 손톱으로 적을 할퀸다"
)

SHADOW_BOLT = Skill(
    id_="shadow_bolt",
    name="섀도우 볼트",
    power=30,
    priority=0,
    durability_cost=20,
    description="어둠의 탄환을 발사한다"
)

WING_SLASH = Skill(
    id_="wing_slash",
    name="윙 슬래시",
    power=26,
    priority=1,
    durability_cost=15,
    description="날개로 적을 베어버린다"
)

DIVE_ATTACK = Skill(
    id_="dive_attack",
    name="급강하 공격",
    power=35,
    priority=0,
    durability_cost=25,
    description="하늘에서 급강하하여 공격한다"
)

# 황금왕 보스 스킬
GOLDEN_SLASH = Skill(
    id_="golden_slash",
    name="황금 베기",
    power=40,
    priority=1,
    durability_cost=50,
    description="황금 검으로 적을 베어버린다"
)

SWORD_RAIN = Skill(
    id_="sword_rain",
    name="검의 비",
    power=50,
    priority=0,
    durability_cost=60,
    description="무수한 황금 검을 소환하여 비처럼 쏟아붓는다"
)

KINGS_JUDGMENT = Skill(
    id_="kings_judgment",
    name="왕의 심판",
    power=60,
    priority=-1,
    durability_cost=70,
    description="왕의 권능으로 심판을 내린다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       몬스터 전용 스킬 (골렘)                              ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  골렘, 푸른/붉은/검은/킬러 골렘, 마공학 골렘                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

STONE_PUNCH = Skill(
    id_="stone_punch",
    name="돌 주먹",
    power=28,
    priority=0,
    durability_cost=15,
    description="단단한 돌 주먹으로 적을 가격한다"
)

ROCK_THROW = Skill(
    id_="rock_throw",
    name="바위 던지기",
    power=32,
    priority=0,
    durability_cost=20,
    description="거대한 바위를 던져 적을 공격한다"
)

ICE_PUNCH = Skill(
    id_="ice_punch",
    name="얼음 주먹",
    power=30,
    priority=0,
    durability_cost=18,
    description="얼어붙은 주먹으로 적을 가격한다"
)

FROST_BREATH = Skill(
    id_="frost_breath",
    name="냉기 브레스",
    power=35,
    priority=0,
    durability_cost=22,
    description="차가운 냉기를 내뿜는다"
)

LAVA_FIST = Skill(
    id_="lava_fist",
    name="용암 주먹",
    power=32,
    priority=0,
    durability_cost=20,
    description="불타는 용암 주먹으로 적을 가격한다"
)

ERUPTION = Skill(
    id_="eruption",
    name="분화",
    power=40,
    priority=-1,
    durability_cost=28,
    description="몸에서 용암을 분출시킨다"
)

SHADOW_FIST = Skill(
    id_="shadow_fist",
    name="어둠의 주먹",
    power=34,
    priority=0,
    durability_cost=22,
    description="어둠에 물든 주먹으로 적을 가격한다"
)

VOID_CRUSH = Skill(
    id_="void_crush",
    name="공허의 분쇄",
    power=42,
    priority=0,
    durability_cost=28,
    description="공허의 힘으로 적을 분쇄한다"
)

BLOODY_RAMPAGE = Skill(
    id_="bloody_rampage",
    name="피의 광란",
    power=50,
    priority=0,
    durability_cost=35,
    description="피로 물든 채 광란에 빠져 난동을 부린다"
)

HAMMER_CRUSH = Skill(
    id_="hammer_crush",
    name="해머 분쇄",
    power=60,
    priority=-2,
    durability_cost=45,
    description="거대한 해머로 모든 것을 분쇄한다"
)

# 마공학 골렘 보스 스킬
HEXTECH_BEAM = Skill(
    id_="hextech_beam",
    name="헥스텍 빔",
    power=45,
    priority=1,
    durability_cost=30,
    description="마법 기술로 강력한 빔을 발사한다"
)

CORE_OVERLOAD = Skill(
    id_="core_overload",
    name="코어 과부하",
    power=55,
    priority=-1,
    durability_cost=40,
    description="코어의 에너지를 폭발시킨다"
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          스킬 딕셔너리 (ALL_SKILLS)                        ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  모든 스킬을 ID로 접근 가능하도록 등록                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

ALL_SKILLS = {
    # ==================== 맨손 / 테스트 ====================
    "struggle": STRUGGLE,
    "test_slash": TEST_SLASH,
    
    # ==================== 일반 등급 무기 스킬 ====================
    # 기본 스킬
    "swing": SWING,                    # 나무 막대기
    "pierce": PIERCE,                  # 녹슨 단검
    "sweep": SWEEP,                    # 기본 창
    "magic_bolt": MAGIC_BOLT,          # 소박한 지팡이
    "precise_shot": PRECISE_SHOT,      # 수제 활
    # 초월 스킬
    "power_strike": POWER_STRIKE,      # 나무 막대기 초월
    "deep_wound": DEEP_WOUND,          # 녹슨 단검 초월
    "spear_charge": SPEAR_CHARGE,      # 기본 창 초월
    "mana_burst": MANA_BURST,          # 소박한 지팡이 초월
    "arrow_rain": ARROW_RAIN,          # 수제 활 초월
    
    # ==================== 희귀 등급 무기 스킬 ====================
    # 기본 스킬
    "slash1": SLASH1,                  # 철 검
    "slash2": SLASH2,                  # 철 검
    "rapid_stab": RAPID_STAB,          # 레이피어
    # 초월 스킬
    "spin_slash": SPIN_SLASH,          # 철 검 초월
    "fast_pierce": FAST_PIERCE,        # 레이피어 초월
    
    # ==================== 영웅 등급 무기 스킬 ====================
    # 불의 검
    "flame_slash": FLAME_SLASH,
    "burning_blade": BURNING_BLADE,
    "inferno": INFERNO,                # 초월
    # 바람의 활
    "wind_arrow": WIND_ARROW,
    "gale_shot": GALE_SHOT,
    "storm_arrow": STORM_ARROW,        # 초월
    # 물의 지팡이
    "aqua_burst": AQUA_BURST,
    "tidal_wave": TIDAL_WAVE,
    "tsunami": TSUNAMI,                # 초월
    # 대지의 폴암
    "earth_thrust": EARTH_THRUST,
    "quake_strike": QUAKE_STRIKE,
    "continental_crush": CONTINENTAL_CRUSH,  # 초월
    
    # ==================== 영웅 보스 드롭 무기 스킬 ====================
    # 킹 슬라임의 지팡이 (blood_bite, magma_shot, slime_slash는 몬스터 스킬)
    "slime_burst": SLIME_BURST,        # 초월
    # 황금왕의 검 (golden_slash, sword_rain, kings_judgment는 몬스터 스킬)
    "golden_rule": GOLDEN_RULE,        # 초월
    # 뮤턴트의 대도끼
    "giant_cleave": GIANT_CLEAVE,
    "whirlwind_axe": WHIRLWIND_AXE,
    "executioner": EXECUTIONER,
    "titan_crush": TITAN_CRUSH,        # 초월
    
    # ==================== 전설 등급 무기 스킬 ====================
    # 엑스칼리버
    "holy_slash": HOLY_SLASH,
    "light_burst": LIGHT_BURST,
    "divine_judgment": DIVINE_JUDGMENT,
    "blessing_of_light": BLESSING_OF_LIGHT,  # 내구도 회복
    # 마공학 해머
    "hextech_strike": HEXTECH_STRIKE,
    "energy_wave": ENERGY_WAVE,
    "overcharge_smash": OVERCHARGE_SMASH,
    "core_charge": CORE_CHARGE,        # 내구도 회복
    # ※ 전설 무기 초월 = 패시브 (스킬 아님)
    
    # ==================== 몬스터 스킬 (슬라임) ====================
    "body_slam": BODY_SLAM,
    "red_attack": RED_ATTACK,
    "yellow_attack": YELLOW_ATTACK,
    "blue_attack": BLUE_ATTACK,
    "blood_bite": BLOOD_BITE,
    "magma_shot": MAGMA_SHOT,
    "slime_slash": SLIME_SLASH,
    "rainbow_attack": RAINBOW_ATTACK,
    "kings_slam": KINGS_SLAM,
    
    # ==================== 몬스터 스킬 (고블린) ====================
    "club_swing": CLUB_SWING,
    "goblin_arrow": GOBLIN_ARROW,
    "sneak_attack": SNEAK_ATTACK,
    "steal": STEAL,
    "axe_slash": AXE_SLASH,
    "shield_bash": SHIELD_BASH,
    "fireball": FIREBALL,
    "dark_magic": DARK_MAGIC,
    "mutant_smash": MUTANT_SMASH,
    "berserk_rage": BERSERK_RAGE,
    
    # ==================== 몬스터 스킬 (스켈레톤) ====================
    "bone_strike": BONE_STRIKE,
    "muscle_punch": MUSCLE_PUNCH,
    "muscle_charge": MUSCLE_CHARGE,
    "psychic_wave": PSYCHIC_WAVE,
    "mind_crush": MIND_CRUSH,
    "dark_claw": DARK_CLAW,
    "shadow_bolt": SHADOW_BOLT,
    "wing_slash": WING_SLASH,
    "dive_attack": DIVE_ATTACK,
    "golden_slash": GOLDEN_SLASH,
    "sword_rain": SWORD_RAIN,
    "kings_judgment": KINGS_JUDGMENT,
    
    # ==================== 몬스터 스킬 (골렘) ====================
    "stone_punch": STONE_PUNCH,
    "rock_throw": ROCK_THROW,
    "ice_punch": ICE_PUNCH,
    "frost_breath": FROST_BREATH,
    "lava_fist": LAVA_FIST,
    "eruption": ERUPTION,
    "shadow_fist": SHADOW_FIST,
    "void_crush": VOID_CRUSH,
    "bloody_rampage": BLOODY_RAMPAGE,
    "hammer_crush": HAMMER_CRUSH,
    "hextech_beam": HEXTECH_BEAM,
    "core_overload": CORE_OVERLOAD,
}