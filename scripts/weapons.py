from scripts.skills import ALL_SKILLS

class Weapon:
    """무기 기본 클래스"""
    def __init__(self, id_, name, grade, max_durability, skill_ids, description="", image_path=""):
        self.id = id_
        self.name = name
        self.grade = grade  # 등급: "일반", "고급", "희귀", "전설" 등
        self.max_durability = max_durability
        self.durability = max_durability  # 현재 내구도
        self.skill_ids = skill_ids  # 이 무기가 사용할 수 있는 스킬 ID 리스트
        self.description = description
        self.image_path = image_path  # 무기 이미지 경로
    
    def get_skills(self):
        """무기가 사용 가능한 스킬 객체 리스트 반환"""
        return [ALL_SKILLS[skill_id] for skill_id in self.skill_ids if skill_id in ALL_SKILLS]
    
    def use_skill(self, skill):
        """스킬 사용 시 내구도 감소"""
        if self.durability >= skill.durability_cost:
            self.durability -= skill.durability_cost
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

# ==================== 무기 정의 ====================

WOODEN_STICK = Weapon(
    id_="wooden_stick",
    name="나무 막대기",
    grade="일반",
    max_durability=50,
    skill_ids=["swing"],
    description="평범한 나무 막대기. 기본적인 공격만 가능하다.",
    image_path="resources/png/weapon/wooden_stick.png"
)

IRON_SWORD = Weapon(
    id_="iron_sword",
    name="철 검",
    grade="고급",
    max_durability=100,
    skill_ids=["pierce", "slash"],
    description="잘 벼려진 철 검. 다양한 공격 기술을 사용할 수 있다.",
    image_path="resources/png/weapon/iron_sword.png"
)

# ==================== 몬스터 전용 무기 ====================

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

# ==================== 향후 확장용 무기 예시 ====================

RUSTY_DAGGER = Weapon(
    id_="rusty_dagger",
    name="녹슨 단검",
    grade="일반",
    max_durability=30,
    skill_ids=["pierce"],
    description="오래되어 녹슨 단검. 빠른 공격에 특화되어 있다.",
    image_path="resources/png/weapon/rusty_dagger.png"
)

# 무기 딕셔너리 (ID로 접근 가능)
ALL_WEAPONS = {
    "wooden_stick": WOODEN_STICK,
    "slime1": SLIME_BODY,
    "slime2": RED_SLIME_BODY,
    "slime3": YELLOW_SLIME_BODY,
    "slime4": BLUE_SLIME_BODY,
    "slime5": MAGMA_SLIME_BODY,
    "slime6": SWORD_SLIME_BODY,
    "iron_sword": IRON_SWORD,
    "rusty_dagger": RUSTY_DAGGER,
}

def create_weapon(weapon_id):
    """새로운 무기 인스턴스 생성 (내구도 초기화됨)"""
    if weapon_id not in ALL_WEAPONS:
        return None
    
    template = ALL_WEAPONS[weapon_id]
    return Weapon(
        id_=template.id,
        name=template.name,
        grade=template.grade,
        max_durability=template.max_durability,
        skill_ids=template.skill_ids.copy(),
        description=template.description,
        image_path=template.image_path
    )