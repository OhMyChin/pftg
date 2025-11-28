class Consumable:
    """소모품 기본 클래스"""
    def __init__(self, id_, name, type_, effect_value, description="", image_path=""):
        self.id = id_
        self.name = name
        self.type = type_  # "potion" 또는 "repair_kit"
        self.effect_value = effect_value  # 회복량 또는 수리량
        self.description = description
        self.image_path = image_path  # 소모품 이미지 경로
    
    def use(self, target):
        """
        소모품 사용
        target: 사용 대상 (플레이어 또는 무기)
        반환: (성공 여부, 메시지)
        """
        if self.type == "potion":
            # 포션: 플레이어 HP 회복
            if hasattr(target, 'hp') and hasattr(target, 'max_hp'):
                old_hp = target.hp
                target.hp = min(target.max_hp, target.hp + self.effect_value)
                recovered = target.hp - old_hp
                return (True, f"HP {recovered} 회복! ({old_hp} → {target.hp})")
            else:
                return (False, "사용할 수 없습니다.")
        
        elif self.type == "repair_kit":
            # 수리 키트: 무기 내구도 회복
            if hasattr(target, 'durability') and hasattr(target, 'max_durability'):
                old_durability = target.durability
                target.durability = min(target.max_durability, target.durability + self.effect_value)
                repaired = target.durability - old_durability
                return (True, f"내구도 {repaired} 수리! ({old_durability} → {target.durability})")
            else:
                return (False, "무기에만 사용할 수 있습니다.")
        
        return (False, "알 수 없는 아이템입니다.")

# ==================== 포션 정의 ====================

HEALTH_POTION_SMALL = Consumable(
    id_="health_potion_small",
    name="작은 체력 물약",
    type_="potion",
    effect_value=30,
    description="체력을 30 회복한다.",
    image_path="resources/png/consumable/health_potion_small.png"
)

HEALTH_POTION_MEDIUM = Consumable(
    id_="health_potion_medium",
    name="중간 체력 물약",
    type_="potion",
    effect_value=50,
    description="체력을 50 회복한다.",
    image_path="resources/png/consumable/health_potion_medium.png"
)

HEALTH_POTION_LARGE = Consumable(
    id_="health_potion_large",
    name="큰 체력 물약",
    type_="potion",
    effect_value=100,
    description="체력을 100 회복한다.",
    image_path="resources/png/consumable/health_potion_large.png"
)

# ==================== 수리 키트 정의 ====================

REPAIR_KIT_BASIC = Consumable(
    id_="repair_kit_basic",
    name="초급 수리 키트",
    type_="repair_kit",
    effect_value=30,
    description="무기의 내구도를 30 회복한다.",
    image_path="resources/png/consumable/repair_kit_basic.png"
)

REPAIR_KIT_ADVANCED = Consumable(
    id_="repair_kit_advanced",
    name="중급 수리 키트",
    type_="repair_kit",
    effect_value=50,
    description="무기의 내구도를 50 회복한다.",
    image_path="resources/png/consumable/repair_kit_advanced.png"
)

REPAIR_KIT_MASTER = Consumable(
    id_="repair_kit_master",
    name="고급 수리 키트",
    type_="repair_kit",
    effect_value=100,
    description="무기의 내구도를 100 회복한다.",
    image_path="resources/png/consumable/repair_kit_master.png"
)

# ==================== 소모품 딕셔너리 ====================

ALL_CONSUMABLES = {
    "health_potion_small": HEALTH_POTION_SMALL,
    "health_potion_medium": HEALTH_POTION_MEDIUM,
    "health_potion_large": HEALTH_POTION_LARGE,
    "repair_kit_basic": REPAIR_KIT_BASIC,
    "repair_kit_advanced": REPAIR_KIT_ADVANCED,
    "repair_kit_master": REPAIR_KIT_MASTER,
}

def create_consumable(consumable_id):
    """새로운 소모품 인스턴스 생성"""
    if consumable_id not in ALL_CONSUMABLES:
        return None
    
    template = ALL_CONSUMABLES[consumable_id]
    return Consumable(
        id_=template.id,
        name=template.name,
        type_=template.type,
        effect_value=template.effect_value,
        description=template.description,
        image_path=template.image_path
    )