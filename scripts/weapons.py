from scripts.skills import ALL_SKILLS


class Weapon:
    """무기 기본 클래스"""
    def __init__(self, id_, name, grade, max_durability, skill_ids, description="", image_path="",
                 transcend_skill=None, is_boss_drop=False, transcend_passive=None):
        self.id = id_
        self.name = name
        self.grade = grade  # 등급: "일반", "희귀", "영웅", "전설" 등
        self.max_durability = max_durability
        self.durability = max_durability  # 현재 내구도
        self.skill_ids = skill_ids  # 이 무기가 사용할 수 있는 스킬 ID 리스트
        self.description = description
        self.image_path = image_path  # 무기 이미지 경로
        
        # 강화 관련
        self.upgrade_level = 0  # 강화 레벨 (0~5)
        self.bonus_power = 0  # 추가 공격력 (강화당 +1)
        self.is_transcended = False  # 초월 여부
        self.transcend_skill = transcend_skill  # 초월 시 해금되는 스킬 ID (영웅 이하)
        self.transcend_passive = transcend_passive  # 초월 시 해금되는 패시브 (전설)
        self.is_boss_drop = is_boss_drop  # 보스 드롭 무기 여부 (합성 불가)
        
        # 패시브 관련 (전설 무기용)
        self.passive_stacks = 0  # 패시브 스택 수
        self.charge_up_ready = False  # charge_up 패시브: 다음 스킬 2배 여부
    
    def get_skills(self):
        """무기가 사용 가능한 스킬 객체 리스트 반환"""
        return [ALL_SKILLS[skill_id] for skill_id in self.skill_ids if skill_id in ALL_SKILLS]
    
    def get_skill_power(self, skill_id):
        """강화 보너스 + 패시브 보너스가 적용된 스킬 위력 반환"""
        if skill_id not in ALL_SKILLS:
            return 0
        
        base_power = ALL_SKILLS[skill_id].power
        total_power = base_power + self.bonus_power + self.get_passive_bonus()
        
        # charge_up 패시브: 충전 완료 시 위력 2배
        if self.is_transcended and self.transcend_passive == "charge_up" and self.charge_up_ready:
            total_power *= 2
        
        return total_power
    
    def get_passive_bonus(self):
        """패시브로 인한 추가 공격력 반환"""
        if self.is_transcended and self.transcend_passive:
            # 패시브 타입에 따라 보너스 계산
            if self.transcend_passive == "stack_power":
                return self.passive_stacks  # 스택당 +1 공격력
            elif self.transcend_passive == "overcharge":
                # 내구도가 낮을수록 공격력 증가 (70% 이하부터, 10%일 때 최대 +20)
                ratio = self.durability / self.max_durability
                if ratio <= 0.7:
                    # 70%일 때 0, 10%일 때 20 (선형 증가)
                    bonus = int((0.7 - max(ratio, 0.1)) / 0.6 * 20)
                    return bonus
        return 0
    
    def on_skill_used(self):
        """스킬 사용 후 호출 (패시브 효과 적용)"""
        if self.is_transcended and self.transcend_passive:
            if self.transcend_passive == "stack_power":
                self.passive_stacks += 1  # 스킬 사용할 때마다 스택 증가
            elif self.transcend_passive == "charge_up":
                # 충전 패시브: 3스택 도달 시 다음 스킬 2배
                if self.charge_up_ready:
                    # 2배 공격 사용 후 초기화
                    self.charge_up_ready = False
                    self.passive_stacks = 0
                else:
                    self.passive_stacks += 1
                    if self.passive_stacks >= 3:
                        self.charge_up_ready = True
    
    def on_turn_start(self):
        """턴 시작 시 호출 (패시브 효과 적용)"""
        if self.is_transcended and self.transcend_passive == "sea_blessing":
            # 바다의 축복: 매 턴 내구도 +15 회복
            self.durability = min(self.max_durability, self.durability + 15)
            return 15  # 회복량 반환 (UI 표시용)
        return 0
    
    def reset_passive_stacks(self):
        """전투 종료 시 패시브 스택 초기화"""
        self.passive_stacks = 0
        self.charge_up_ready = False
    
    def get_passive_description(self):
        """패시브 설명 반환"""
        if not self.transcend_passive:
            return ""
        
        if self.transcend_passive == "stack_power":
            return f"성검의 각성: 스킬 사용 시 공격력 +1 (현재: +{self.passive_stacks})"
        elif self.transcend_passive == "overcharge":
            bonus = self.get_passive_bonus()
            return f"과부하: 내구도 70% 이하 시 공격력 증가 (현재: +{bonus})"
        elif self.transcend_passive == "charge_up":
            if self.charge_up_ready:
                return f"충전: 충전 완료! 다음 스킬 위력 2배"
            else:
                return f"충전: 스킬 3회 사용 시 다음 위력 2배 ({self.passive_stacks}/3)"
        elif self.transcend_passive == "sea_blessing":
            return f"바다의 축복: 매 턴 시작 시 내구도 +15 회복"
        return ""
    
    def use_skill(self, skill):
        """스킬 사용 시 내구도 감소 (음수 소모는 회복, 최대 내구도 제한)"""
        if self.durability >= skill.durability_cost:
            self.durability -= skill.durability_cost
            # 최대 내구도를 넘지 않도록 제한
            if self.durability > self.max_durability:
                self.durability = self.max_durability
            # 패시브 효과 적용
            self.on_skill_used()
            return True
        return False
    
    def is_broken(self):
        """무기가 부서졌는지 확인"""
        return self.durability <= 0
    
    def repair(self, amount=None):
        """무기 수리 (amount가 None이면 완전 수리)"""
        if amount is None:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def get_display_name(self):
        """강화 레벨이 포함된 표시용 이름"""
        name = self.name
        if self.upgrade_level > 0:
            name = f"+{self.upgrade_level} {name}"
        if self.is_transcended:
            name = f"[초월] {name}"
        return name


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                            테스트 무기                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

TESTER_SWORD = Weapon(
    id_="test_sword",
    name="킹왕짱얼티밋 소드",
    grade="테스트",
    max_durability=9999,
    skill_ids=["test_slash"],
    description="테스트용 무기입니다.",
    image_path="resources/png/weapon/test_sword.png",
    transcend_skill=None
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         일반 등급 무기                                     ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  나무 막대기, 녹슨 단검, 기본 창, 소박한 지팡이, 수제 활                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

WOODEN_STICK = Weapon(
    id_="wooden_stick",
    name="나무 막대기",
    grade="일반",
    max_durability=20,
    skill_ids=["swing"],
    description="평범한 나무 막대기. 기본적인 공격만 가능하다.",
    image_path="resources/png/weapon/wooden_stick.png",
    transcend_skill="power_strike"  # 초월: 강타
)

RUSTY_DAGGER = Weapon(
    id_="rusty_dagger",
    name="녹슨 단검",
    grade="일반",
    max_durability=30,
    skill_ids=["pierce"],
    description="오래되어 녹슨 단검. 빠른 공격에 특화되어 있다.",
    image_path="resources/png/weapon/rusty_dagger.png",
    transcend_skill="deep_wound"  # 초월: 깊은 상처
)

BASIC_SPEAR = Weapon(
    id_="basic_spear",
    name="기본 창",
    grade="일반",
    max_durability=35,
    skill_ids=["sweep"],
    description="간단하게 만든 창. 긴 사거리로 넓게 공격할 수 있다.",
    image_path="resources/png/weapon/basic_spear.png",
    transcend_skill="spear_charge"  # 초월: 창 돌진
)

SIMPLE_STAFF = Weapon(
    id_="simple_staff",
    name="소박한 지팡이",
    grade="일반",
    max_durability=25,
    skill_ids=["magic_bolt"],
    description="마력이 조금 깃든 지팡이. 기본적인 마법 공격이 가능하다.",
    image_path="resources/png/weapon/simple_staff.png",
    transcend_skill="mana_burst"  # 초월: 마나 폭발
)

HANDMADE_BOW = Weapon(
    id_="handmade_bow",
    name="수제 활",
    grade="일반",
    max_durability=30,
    skill_ids=["precise_shot"],
    description="손수 만든 활. 정확한 사격이 가능하다.",
    image_path="resources/png/weapon/handmade_bow.png",
    transcend_skill="arrow_rain"  # 초월: 화살비
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         희귀 등급 무기                                     ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  철 검, 레이피어, 살상용 낫, 칠지도, 맹독 단검                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

IRON_SWORD = Weapon(
    id_="iron_sword",
    name="철 검",
    grade="희귀",
    max_durability=100,
    skill_ids=["slash1", "slash2"],
    description="잘 벼려진 철 검. 든든한 국밥 같은 검이다.",
    image_path="resources/png/weapon/iron_sword.png",
    transcend_skill="spin_slash"  # 초월: 회전 베기
)

RAPIER = Weapon(
    id_="rapier",
    name="레이피어",
    grade="희귀",
    max_durability=80,
    skill_ids=["pierce", "rapid_stab"],
    description="보급형 레이피어. 고급진 찌르기 기술을 사용할 수 있다.",
    image_path="resources/png/weapon/rapier.png",
    transcend_skill="fast_pierce"  # 초월: 초고속 찌르기
)

KILLING_SCYTHE = Weapon(
    id_="killing_scythe",
    name="살상용 낫",
    grade="희귀",
    max_durability=90,
    skill_ids=["reap", "death_sweep"],
    description="수확이 아닌 살상을 위해 개조된 낫. 날카로운 곡선이 섬뜩하다.",
    image_path="resources/png/weapon/killing_scythe.png",
    transcend_skill="soul_harvest"  # 초월: 영혼 수확
)

SEVEN_BRANCH_SWORD = Weapon(
    id_="seven_branch_sword",
    name="칠지도",
    grade="희귀",
    max_durability=110,
    skill_ids=["seven_strike", "branch_slash"],
    description="일곱 개의 가지가 달린 신비로운 검. 고대의 힘이 깃들어 있다.",
    image_path="resources/png/weapon/seven_branch_sword.png",
    transcend_skill="seven_branched_fury"  # 초월: 칠지의 분노
)

POISON_DAGGER = Weapon(
    id_="poison_dagger",
    name="맹독 단검",
    grade="희귀",
    max_durability=70,
    skill_ids=["poison_stab", "venom_slash"],
    description="맹독이 발린 단검. 작은 상처로도 치명적인 피해를 입힌다.",
    image_path="resources/png/weapon/poison_dagger.png",
    transcend_skill="deadly_poison"  # 초월: 치명적인 독
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         영웅 등급 무기                                     ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  불의 검, 바람의 활, 물의 지팡이, 대지의 폴암                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

SWORD_OF_FIRE = Weapon(
    id_="sword_of_fire",
    name="불의 검",
    grade="영웅",
    max_durability=180,
    skill_ids=["slash1", "flame_slash", "burning_blade"],
    description="불꽃의 정령이 깃든 검. 타오르는 화염으로 적을 불태운다.",
    image_path="resources/png/weapon/sword_of_fire.png",
    transcend_skill="inferno"  # 초월: 인페르노
)

BOW_OF_WIND = Weapon(
    id_="bow_of_wind",
    name="바람의 활",
    grade="영웅",
    max_durability=150,
    skill_ids=["precise_shot", "wind_arrow", "gale_shot"],
    description="바람의 정령이 깃든 활. 질풍처럼 빠른 화살을 쏜다.",
    image_path="resources/png/weapon/bow_of_wind.png",
    transcend_skill="storm_arrow"  # 초월: 폭풍의 화살
)

STAFF_OF_WATER = Weapon(
    id_="staff_of_water",
    name="물의 지팡이",
    grade="영웅",
    max_durability=160,
    skill_ids=["magic_bolt", "aqua_burst", "tidal_wave"],
    description="물의 정령이 깃든 지팡이. 파도의 힘으로 적을 휩쓴다.",
    image_path="resources/png/weapon/staff_of_water.png",
    transcend_skill="tsunami"  # 초월: 쓰나미
)

POLEARM_OF_EARTH = Weapon(
    id_="polearm_of_earth",
    name="대지의 폴암",
    grade="영웅",
    max_durability=200,
    skill_ids=["sweep", "earth_thrust", "quake_strike"],
    description="대지의 정령이 깃든 폴암. 땅을 흔드는 강력한 일격을 가한다.",
    image_path="resources/png/weapon/polearm_of_earth.png",
    transcend_skill="continental_crush"  # 초월: 대륙 분쇄
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                     영웅 등급 보스 드롭 무기                                ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  킹 슬라임의 지팡이, 황금왕의 검, 뮤턴트의 대도끼                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

SLIME_WAND = Weapon(
    id_="slime_wand",
    name="킹 슬라임의 지팡이",
    grade="영웅",
    max_durability=400,
    skill_ids=["blood_bite", "magma_shot", "slime_slash"],
    description="킹 슬라임의 힘이 깃든 지팡이. 상위 슬라임들의 기술을 사용할 수 있다.",
    image_path="resources/png/weapon/slime_wand.png",
    transcend_skill="slime_burst",  # 초월: 슬라임 폭발
    is_boss_drop=True  # 보스 드롭 무기
)

GOLDEN_SWORD = Weapon(
    id_="golden_sword",
    name="황금왕의 검",
    grade="영웅",
    max_durability=300,
    skill_ids=["golden_slash", "sword_rain", "kings_judgment"],
    description="황금왕이 사용하던 전설의 검. 무한한 부와 권력의 상징이다.",
    image_path="resources/png/weapon/golden_sword.png",
    transcend_skill="golden_rule",  # 초월: 황금률
    is_boss_drop=True
)

GOBLIN_BIG_AXE = Weapon(
    id_="goblin_big_axe",
    name="뮤턴트의 대도끼",
    grade="영웅",
    max_durability=250,
    skill_ids=["giant_cleave", "whirlwind_axe", "executioner"],
    description="뮤턴트 고블린이 휘두르던 거대한 도끼. 그 무게만으로도 적을 압도한다.",
    image_path="resources/png/weapon/goblin_big_axe.png",
    transcend_skill="titan_crush",  # 초월: 타이탄 크러쉬
    is_boss_drop=True
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                         전설 등급 무기                                     ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  엑스칼리버, 마공학 해머, 제우스의 번개, 포세이돈의 삼지창                   ║
# ║  ※ 전설 무기는 초월 시 액티브 스킬이 아닌 패시브를 얻음                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

EXCALIBUR = Weapon(
    id_="excalibur",
    name="엑스칼리버",
    grade="전설",
    max_durability=500,
    skill_ids=["holy_slash", "light_burst", "divine_judgment", "blessing_of_light"],
    description="전설 속에만 존재하던 성스러운 검. 선택받은 자만이 그 진정한 힘을 발휘할 수 있다.",
    image_path="resources/png/weapon/excalibur.png",
    transcend_passive="stack_power",  # 초월 패시브: 스킬 사용 시 공격력 +1 스택
    is_boss_drop=False
)

HEXTECH_HAMMER = Weapon(
    id_="hextech_hammer",
    name="마공학 해머",
    grade="전설",
    max_durability=350,
    skill_ids=["hextech_strike", "energy_wave", "overcharge_smash", "core_charge"],
    description="마공학 골렘의 코어로 만든 전설의 해머. 마법 기술의 정수가 담겨있다.",
    image_path="resources/png/weapon/hextech_hammer.png",
    transcend_passive="overcharge",  # 초월 패시브: 내구도 70% 이하 시 공격력 증가
    is_boss_drop=True
)

ZEUS_THUNDERBOLT = Weapon(
    id_="zeus_thunderbolt",
    name="제우스의 번개",
    grade="전설",
    max_durability=400,
    skill_ids=["thunder_strike", "lightning_bolt", "chain_lightning", "divine_wrath"],
    description="천공의 신 제우스가 휘두르던 번개. 하늘의 심판을 내릴 수 있다.",
    image_path="resources/png/weapon/zeus_thunderbolt.png",
    transcend_passive="charge_up",  # 초월 패시브: 스킬 3회 사용 시 다음 스킬 위력 2배
    is_boss_drop=False
)

POSEIDON_TRIDENT = Weapon(
    id_="poseidon_trident",
    name="포세이돈의 삼지창",
    grade="전설",
    max_durability=450,
    skill_ids=["trident_thrust", "tidal_wave", "whirlpool", "abyssal_rage"],
    description="바다의 신 포세이돈이 휘두르던 삼지창. 대양의 힘이 깃들어 있다.",
    image_path="resources/png/weapon/poseidon_trident.png",
    transcend_passive="sea_blessing",  # 초월 패시브: 매 턴 내구도 +15 회복
    is_boss_drop=False
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       몬스터 전용 무기 (슬라임)                             ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  슬라임, 빨간/노란/파란 슬라임, 블러드/마그마/소드/무지개 슬라임, 킹 슬라임   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

SLIME_BODY = Weapon(
    id_="slime1",
    name="슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["body_slam"],
    image_path=""
)

RED_SLIME_BODY = Weapon(
    id_="slime2",
    name="빨간 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["red_attack"],
    image_path=""
)

YELLOW_SLIME_BODY = Weapon(
    id_="slime3",
    name="노란 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["yellow_attack"],
    image_path=""
)

BLUE_SLIME_BODY = Weapon(
    id_="slime4",
    name="파란 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["blue_attack"],
    image_path=""
)

BLOOD_SLIME_BODY = Weapon(
    id_="slime5",
    name="블러드 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["red_attack", "blood_bite"],
    image_path=""
)

MAGMA_SLIME_BODY = Weapon(
    id_="slime6",
    name="마그마 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["yellow_attack", "magma_shot"],
    image_path=""
)

SWORD_SLIME_BODY = Weapon(
    id_="slime7",
    name="소드 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["blue_attack", "slime_slash"],
    image_path=""
)

RAINBOW_SLIME_BODY = Weapon(
    id_="slime8",
    name="무지개 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["rainbow_attack"],
    image_path=""
)

KING_SLIME_BODY = Weapon(
    id_="slime9",
    name="킹 슬라임의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["body_slam", "kings_slam"],
    image_path=""
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       몬스터 전용 무기 (고블린)                             ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  고블린, 궁수/도적/전사/마법사 고블린, 뮤턴트 고블린                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

GOBLIN_CLUB = Weapon(
    id_="goblin1",
    name="고블린의 몽둥이",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["club_swing"],
    image_path=""
)

GOBLIN_BOW = Weapon(
    id_="goblin2",
    name="궁수 고블린의 활",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["goblin_arrow"],
    image_path=""
)

GOBLIN_DAGGER = Weapon(
    id_="goblin3",
    name="도적 고블린의 단검",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["sneak_attack", "steal"],
    image_path=""
)

GOBLIN_AXE = Weapon(
    id_="goblin4",
    name="전사 고블린의 도끼",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["axe_slash", "shield_bash"],
    image_path=""
)

GOBLIN_STAFF = Weapon(
    id_="goblin5",
    name="마법사 고블린의 지팡이",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["fireball", "dark_magic"],
    image_path=""
)

MUTANT_GOBLIN_FIST = Weapon(
    id_="goblin_boss",
    name="뮤턴트 고블린의 주먹",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["mutant_smash", "berserk_rage"],
    image_path=""
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      몬스터 전용 무기 (스켈레톤)                            ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  스켈레톤, 머슬/사이킥/다크/윙 스켈레톤, 황금왕                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

SKELETON_BONE = Weapon(
    id_="skeleton1",
    name="스켈레톤의 뼈",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["bone_strike"],
    image_path=""
)

MUSCLE_SKELETON_BODY = Weapon(
    id_="skeleton2",
    name="머슬 스켈레톤의 몸",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["muscle_punch", "muscle_charge"],
    image_path=""
)

PSYCHIC_SKELETON_MIND = Weapon(
    id_="skeleton3",
    name="사이킥 스켈레톤의 정신",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["psychic_wave", "mind_crush"],
    image_path=""
)

DARK_SKELETON_SHADOW = Weapon(
    id_="skeleton4",
    name="다크 스켈레톤의 그림자",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["dark_claw", "shadow_bolt"],
    image_path=""
)

WING_SKELETON_WINGS = Weapon(
    id_="skeleton5",
    name="윙 스켈레톤의 날개",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["wing_slash", "dive_attack"],
    image_path=""
)

RICH_KING_SWORD = Weapon(
    id_="skeleton_boss",
    name="황금왕의 무기",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["golden_slash", "sword_rain", "kings_judgment"],
    image_path=""
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       몬스터 전용 무기 (골렘)                              ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  골렘, 푸른/붉은/검은/킬러 골렘, 마공학 골렘                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

GOLEM_FIST = Weapon(
    id_="golem1",
    name="골렘의 주먹",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["stone_punch", "rock_throw"],
    image_path=""
)

BLUE_GOLEM_FIST = Weapon(
    id_="golem2",
    name="푸른 골렘의 주먹",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["ice_punch", "frost_breath"],
    image_path=""
)

RED_GOLEM_FIST = Weapon(
    id_="golem3",
    name="붉은 골렘의 주먹",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["lava_fist", "eruption"],
    image_path=""
)

BLACK_GOLEM_FIST = Weapon(
    id_="golem4",
    name="검은 골렘의 주먹",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["shadow_fist", "void_crush"],
    image_path=""
)

KILLER_GOLEM_HAMMER = Weapon(
    id_="golem5",
    name="킬러 골렘의 해머",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["bloody_rampage", "hammer_crush"],
    image_path=""
)

HEXTECH_GOLEM_CORE = Weapon(
    id_="golem_boss",
    name="마공학 골렘의 코어",
    grade="몬스터",
    max_durability=9999,
    skill_ids=["hextech_beam", "core_overload"],
    image_path=""
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                      최종 보스 전용 무기 (어둠의 신)                        ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  1페이즈: 어둠의 신, 2페이즈: 옛 용사, 3페이즈: 플레이어                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

DARK_GOD_WEAPON = Weapon(
    id_="dark_god_weapon",
    name="어둠의 힘",
    grade="보스",
    max_durability=9999,
    skill_ids=["dark_corruption", "void_blast", "shadow_chains"],
    image_path=""
)

OLD_HERO_WEAPON = Weapon(
    id_="old_hero_weapon",
    name="옛 용사의 검",
    grade="보스",
    max_durability=9999,
    skill_ids=["hero_slash", "light_of_hope", "desperate_strike", "corrupted_light"],
    image_path=""
)

FINAL_FORM_WEAPON = Weapon(
    id_="final_form_weapon",
    name="기억의 검",
    grade="보스",
    max_durability=9999,
    skill_ids=["final_farewell"],
    image_path=""
)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          무기 딕셔너리 (ALL_WEAPONS)                       ║
# ╠═══════════════════════════════════════════════════════════════════════════╣
# ║  모든 무기를 ID로 접근 가능하도록 등록                                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

ALL_WEAPONS = {
    # ==================== 테스트 ====================
    "test_sword": TESTER_SWORD,
    
    # ==================== 일반 등급 ====================
    "wooden_stick": WOODEN_STICK,      # 나무 막대기
    "rusty_dagger": RUSTY_DAGGER,      # 녹슨 단검
    "basic_spear": BASIC_SPEAR,        # 기본 창
    "simple_staff": SIMPLE_STAFF,      # 소박한 지팡이
    "handmade_bow": HANDMADE_BOW,      # 수제 활
    
    # ==================== 희귀 등급 ====================
    "iron_sword": IRON_SWORD,          # 철 검
    "rapier": RAPIER,                  # 레이피어
    "killing_scythe": KILLING_SCYTHE,  # 살상용 낫
    "seven_branch_sword": SEVEN_BRANCH_SWORD,  # 칠지도
    "poison_dagger": POISON_DAGGER,    # 맹독 단검
    
    # ==================== 영웅 등급 ====================
    "sword_of_fire": SWORD_OF_FIRE,    # 불의 검
    "bow_of_wind": BOW_OF_WIND,        # 바람의 활
    "staff_of_water": STAFF_OF_WATER,  # 물의 지팡이
    "polearm_of_earth": POLEARM_OF_EARTH,  # 대지의 폴암
    
    # ==================== 영웅 등급 (보스 드롭) ====================
    "slime_wand": SLIME_WAND,          # 킹 슬라임의 지팡이
    "golden_sword": GOLDEN_SWORD,      # 황금왕의 검
    "goblin_big_axe": GOBLIN_BIG_AXE,  # 뮤턴트의 대도끼
    
    # ==================== 전설 등급 ====================
    "excalibur": EXCALIBUR,            # 엑스칼리버
    "hextech_hammer": HEXTECH_HAMMER,  # 마공학 해머 (보스 드롭)
    "zeus_thunderbolt": ZEUS_THUNDERBOLT,  # 제우스의 번개
    "poseidon_trident": POSEIDON_TRIDENT,  # 포세이돈의 삼지창
    
    # ==================== 몬스터 무기 (슬라임) ====================
    "slime1": SLIME_BODY,              # 슬라임
    "slime2": RED_SLIME_BODY,          # 빨간 슬라임
    "slime3": YELLOW_SLIME_BODY,       # 노란 슬라임
    "slime4": BLUE_SLIME_BODY,         # 파란 슬라임
    "slime5": BLOOD_SLIME_BODY,        # 블러드 슬라임
    "slime6": MAGMA_SLIME_BODY,        # 마그마 슬라임
    "slime7": SWORD_SLIME_BODY,        # 소드 슬라임
    "slime8": RAINBOW_SLIME_BODY,      # 무지개 슬라임
    "slime9": KING_SLIME_BODY,         # 킹 슬라임
    
    # ==================== 몬스터 무기 (고블린) ====================
    "goblin1": GOBLIN_CLUB,            # 고블린
    "goblin2": GOBLIN_BOW,             # 궁수 고블린
    "goblin3": GOBLIN_DAGGER,          # 도적 고블린
    "goblin4": GOBLIN_AXE,             # 전사 고블린
    "goblin5": GOBLIN_STAFF,           # 마법사 고블린
    "goblin_boss": MUTANT_GOBLIN_FIST, # 뮤턴트 고블린
    
    # ==================== 몬스터 무기 (스켈레톤) ====================
    "skeleton1": SKELETON_BONE,        # 스켈레톤
    "skeleton2": MUSCLE_SKELETON_BODY, # 머슬 스켈레톤
    "skeleton3": PSYCHIC_SKELETON_MIND, # 사이킥 스켈레톤
    "skeleton4": DARK_SKELETON_SHADOW, # 다크 스켈레톤
    "skeleton5": WING_SKELETON_WINGS,  # 윙 스켈레톤
    "skeleton_boss": RICH_KING_SWORD,  # 황금왕
    
    # ==================== 몬스터 무기 (골렘) ====================
    "golem1": GOLEM_FIST,              # 골렘
    "golem2": BLUE_GOLEM_FIST,         # 푸른 골렘
    "golem3": RED_GOLEM_FIST,          # 붉은 골렘
    "golem4": BLACK_GOLEM_FIST,        # 검은 골렘
    "golem5": KILLER_GOLEM_HAMMER,     # 킬러 골렘
    "golem_boss": HEXTECH_GOLEM_CORE,  # 마공학 골렘
    
    # ==================== 최종 보스 무기 ====================
    "dark_god_weapon": DARK_GOD_WEAPON,      # 1페이즈: 어둠의 신
    "old_hero_weapon": OLD_HERO_WEAPON,      # 2페이즈: 옛 용사
    "final_form_weapon": FINAL_FORM_WEAPON,  # 3페이즈: 진짜 자신
}


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                            무기 생성 함수                                  ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def create_weapon(weapon_id):
    """새로운 무기 인스턴스 생성 (내구도 초기화됨)"""
    if weapon_id not in ALL_WEAPONS:
        return None
    
    template = ALL_WEAPONS[weapon_id]
    weapon = Weapon(
        id_=template.id,
        name=template.name,
        grade=template.grade,
        max_durability=template.max_durability,
        skill_ids=template.skill_ids.copy(),
        description=template.description,
        image_path=template.image_path,
        transcend_skill=template.transcend_skill,
        is_boss_drop=template.is_boss_drop,
        transcend_passive=template.transcend_passive
    )
    return weapon