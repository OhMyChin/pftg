import random
from scripts.weapons import create_weapon

class MonsterData:
    """몬스터 데이터 클래스"""
    def __init__(self, name, hp, speed, weapon_id, image_path, 
                 gold=(5, 15), drop_weapon=None, image_size=160, drop_material=None):
        """
        gold: (최소, 최대) 골드 드롭 범위, None이면 골드 안떨굼
        drop_weapon: 드롭할 무기 ID (보스 전용, None이면 무기 안떨굼)
        image_size: 몬스터 이미지 정사각형 한 변 길이 (기본 160)
        drop_material: 드롭할 재료 {"type": "normal/rare/hero/legend", "min": 1, "max": 3}
        """
        self.name = name
        self.hp = hp
        self.speed = speed
        self.weapon_id = weapon_id
        self.image_path = image_path
        self.gold = gold
        self.drop_weapon = drop_weapon
        self.image_size = image_size
        self.drop_material = drop_material
    
    def get_drops(self):
        """드롭 아이템 계산"""
        drops = []
        
        # 골드 드롭 (None이 아닐 때만)
        if self.gold:
            gold_amount = random.randint(self.gold[0], self.gold[1])
            drops.append({"type": "gold", "amount": gold_amount})
        
        # 재료 드롭
        if self.drop_material:
            mat_type = self.drop_material["type"]
            mat_amount = random.randint(self.drop_material["min"], self.drop_material["max"])
            drops.append({"type": "material", "material_type": mat_type, "amount": mat_amount})
        
        # 무기 드롭 (보스만)
        if self.drop_weapon:
            weapon = create_weapon(self.drop_weapon)
            if weapon:
                drops.append({"type": "weapon", "item": weapon})
        
        return drops


# ==================== 층별 배경 설정 (10층 단위) ====================

FLOOR_BACKGROUNDS = {
    1: "resources/png/battle_bg_1.png",   # 1~10층
    2: "resources/png/battle_bg_2.png",   # 11~20층
    3: "resources/png/battle_bg_3.png",   # 21~30층
    4: "resources/png/battle_bg_4.png",   # 31~40층
    5: "resources/png/battle_bg_5.png",   # 41~50층
}

# 기본 배경 (배경이 지정되지 않은 경우)
DEFAULT_BACKGROUND = "resources/png/battle_bg_1.png"


def get_floor_background(floor_num):
    """특정 층의 배경 이미지 경로 반환 (10층 단위)"""
    # 1~10층 → 1, 11~20층 → 2, ...
    bg_index = ((floor_num - 1) // 10) + 1
    return FLOOR_BACKGROUNDS.get(bg_index, DEFAULT_BACKGROUND)


# ==================== 층별 몬스터 배치 ====================

FLOOR_DATA = {
    # ==================== 1~10층: 슬라임 ====================
    1: [
        MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slimes/slime.png",
                    gold=(5, 15)),
    ],
    2: [
        MonsterData("빨간 슬라임", 30, 10, "slime2", "resources/png/enemy/slimes/red_slime.png",
                    gold=(8, 20)),
        MonsterData("블러드 슬라임", 50, 15, "slime5", "resources/png/enemy/slimes/blood_slime.png",
                    gold=(15, 35)),
    ],
    3: [
        MonsterData("노란 슬라임", 35, 8, "slime3", "resources/png/enemy/slimes/yellow_slime.png",
                    gold=(8, 20)),
        MonsterData("마그마 슬라임", 60, 10, "slime6", "resources/png/enemy/slimes/magma_slime.png",
                    gold=(15, 35)),
    ],
    4: [
        MonsterData("파란 슬라임", 32, 9, "slime4", "resources/png/enemy/slimes/blue_slime.png",
                    gold=(8, 20)),
        MonsterData("소드 슬라임", 55, 12, "slime7", "resources/png/enemy/slimes/sword_slime.png",
                    gold=(15, 35)),
    ],
    5: [
        MonsterData("빨간 슬라임", 30, 10, "slime2", "resources/png/enemy/slimes/red_slime.png",
                    gold=(8, 20)),
        MonsterData("노란 슬라임", 35, 8, "slime3", "resources/png/enemy/slimes/yellow_slime.png",
                    gold=(8, 20)),
        MonsterData("파란 슬라임", 32, 9, "slime4", "resources/png/enemy/slimes/blue_slime.png",
                    gold=(8, 20)),
    ],
    6: [
        MonsterData("블러드 슬라임", 50, 15, "slime5", "resources/png/enemy/slimes/blood_slime.png",
                    gold=(15, 35)),
        MonsterData("마그마 슬라임", 60, 10, "slime6", "resources/png/enemy/slimes/magma_slime.png",
                    gold=(15, 35)),
    ],
    7: [
        MonsterData("마그마 슬라임", 60, 10, "slime6", "resources/png/enemy/slimes/magma_slime.png",
                    gold=(15, 35)),
        MonsterData("소드 슬라임", 55, 12, "slime7", "resources/png/enemy/slimes/sword_slime.png",
                    gold=(15, 35)),
    ],
    8: [
        MonsterData("소드 슬라임", 55, 12, "slime7", "resources/png/enemy/slimes/sword_slime.png",
                    gold=(15, 35)),
        MonsterData("블러드 슬라임", 50, 15, "slime5", "resources/png/enemy/slimes/blood_slime.png",
                    gold=(15, 35)),
    ],
    9: [
        MonsterData("무지개 슬라임", 77, 77, "slime8", "resources/png/enemy/slimes/rainbow_slime.png",
                    gold=(50, 77)),
    ],
    10: [
        MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slimes/slime.png",
                    gold=(5, 15)),
        MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slimes/slime.png",
                    gold=(5, 15)),
        MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slimes/slime.png",
                    gold=(5, 15)),
        # 보스: 킹 슬라임 (무기 드롭)
        MonsterData("킹 슬라임", 100, 10, "slime9", "resources/png/enemy/slimes/king_slime.png",
                    gold=(100, 200), drop_weapon="slime_wand"),
    ],
    
    # ==================== 11~20층: 고블린 ====================
    11: [
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
    ],
    12: [
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
        MonsterData("궁수 고블린", 45, 14, "goblin2", "resources/png/enemy/goblins/archer_goblin.png",
                    gold=(20, 40), image_size=160),
    ],
    13: [
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
        MonsterData("도적 고블린", 40, 16, "goblin3", "resources/png/enemy/goblins/theif_goblin.png",
                    gold=(25, 50), image_size=160),
    ],
    14: [
        MonsterData("궁수 고블린", 45, 14, "goblin2", "resources/png/enemy/goblins/archer_goblin.png",
                    gold=(20, 40), image_size=160),
        MonsterData("도적 고블린", 40, 16, "goblin3", "resources/png/enemy/goblins/theif_goblin.png",
                    gold=(25, 50), image_size=160),
    ],
    15: [
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
        MonsterData("전사 고블린", 70, 10, "goblin4", "resources/png/enemy/goblins/worrier_goblin.png",
                    gold=(30, 55), image_size=180),
    ],
    16: [
        MonsterData("궁수 고블린", 45, 14, "goblin2", "resources/png/enemy/goblins/archer_goblin.png",
                    gold=(20, 40), image_size=160),
        MonsterData("전사 고블린", 70, 10, "goblin4", "resources/png/enemy/goblins/worrier_goblin.png",
                    gold=(30, 55), image_size=180),
    ],
    17: [
        MonsterData("도적 고블린", 40, 16, "goblin3", "resources/png/enemy/goblins/theif_goblin.png",
                    gold=(25, 50), image_size=160),
        MonsterData("마법사 고블린", 55, 12, "goblin5", "resources/png/enemy/goblins/wizard_goblin.png",
                    gold=(35, 60), image_size=160),
    ],
    18: [
        MonsterData("전사 고블린", 70, 10, "goblin4", "resources/png/enemy/goblins/worrier_goblin.png",
                    gold=(30, 55), image_size=180),
        MonsterData("마법사 고블린", 55, 12, "goblin5", "resources/png/enemy/goblins/wizard_goblin.png",
                    gold=(35, 60), image_size=160),
    ],
    19: [
        MonsterData("궁수 고블린", 45, 14, "goblin2", "resources/png/enemy/goblins/archer_goblin.png",
                    gold=(20, 40), image_size=160),
        MonsterData("도적 고블린", 40, 16, "goblin3", "resources/png/enemy/goblins/theif_goblin.png",
                    gold=(25, 50), image_size=160),
        MonsterData("전사 고블린", 70, 10, "goblin4", "resources/png/enemy/goblins/worrier_goblin.png",
                    gold=(30, 55), image_size=180),
        MonsterData("마법사 고블린", 55, 12, "goblin5", "resources/png/enemy/goblins/wizard_goblin.png",
                    gold=(35, 60), image_size=160),
    ],
    20: [
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
        MonsterData("고블린", 50, 11, "goblin1", "resources/png/enemy/goblins/goblin.png",
                    gold=(15, 30), image_size=160),
        # 보스: 뮤턴트 고블린
        MonsterData("뮤턴트 고블린", 200, 8, "goblin_boss", "resources/png/enemy/goblins/mutant_goblin.png",
                    gold=(200, 400), drop_weapon="goblin_big_axe", image_size=280),
    ],
    
    # ==================== 21~30층: 스켈레톤 ====================
    21: [
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
    ],
    22: [
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
        MonsterData("머슬 스켈레톤", 120, 10, "skeleton2", "resources/png/enemy/skeletons/muscle_skeleton.png",
                    gold=(40, 70)),
    ],
    23: [
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
        MonsterData("사이킥 스켈레톤", 100, 15, "skeleton3", "resources/png/enemy/skeletons/psychic_skeleton.png",
                    gold=(45, 75)),
    ],
    24: [
        MonsterData("머슬 스켈레톤", 120, 10, "skeleton2", "resources/png/enemy/skeletons/muscle_skeleton.png",
                    gold=(40, 70)),
        MonsterData("사이킥 스켈레톤", 100, 15, "skeleton3", "resources/png/enemy/skeletons/psychic_skeleton.png",
                    gold=(45, 75)),
    ],
    25: [
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
        MonsterData("다크 스켈레톤", 110, 14, "skeleton4", "resources/png/enemy/skeletons/dark_skeleton.png",
                    gold=(50, 80)),
    ],
    26: [
        MonsterData("머슬 스켈레톤", 120, 10, "skeleton2", "resources/png/enemy/skeletons/muscle_skeleton.png",
                    gold=(40, 70)),
        MonsterData("다크 스켈레톤", 110, 14, "skeleton4", "resources/png/enemy/skeletons/dark_skeleton.png",
                    gold=(50, 80)),
    ],
    27: [
        MonsterData("사이킥 스켈레톤", 100, 15, "skeleton3", "resources/png/enemy/skeletons/psychic_skeleton.png",
                    gold=(45, 75)),
        MonsterData("윙 스켈레톤", 95, 18, "skeleton5", "resources/png/enemy/skeletons/wing_skeleton.png",
                    gold=(55, 85)),
    ],
    28: [
        MonsterData("다크 스켈레톤", 110, 14, "skeleton4", "resources/png/enemy/skeletons/dark_skeleton.png",
                    gold=(50, 80)),
        MonsterData("윙 스켈레톤", 95, 18, "skeleton5", "resources/png/enemy/skeletons/wing_skeleton.png",
                    gold=(55, 85)),
    ],
    29: [
        MonsterData("머슬 스켈레톤", 120, 10, "skeleton2", "resources/png/enemy/skeletons/muscle_skeleton.png",
                    gold=(40, 70)),
        MonsterData("사이킥 스켈레톤", 100, 15, "skeleton3", "resources/png/enemy/skeletons/psychic_skeleton.png",
                    gold=(45, 75)),
        MonsterData("다크 스켈레톤", 110, 14, "skeleton4", "resources/png/enemy/skeletons/dark_skeleton.png",
                    gold=(50, 80)),
        MonsterData("윙 스켈레톤", 95, 18, "skeleton5", "resources/png/enemy/skeletons/wing_skeleton.png",
                    gold=(55, 85)),
    ],
    30: [
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
        MonsterData("스켈레톤", 80, 12, "skeleton1", "resources/png/enemy/skeletons/skeleton.png",
                    gold=(30, 50)),
        # 보스: 황금왕 (무기 드롭)
        MonsterData("황금왕", 300, 12, "skeleton_boss", "resources/png/enemy/skeletons/rich_king.png",
                    gold=(500, 1000), drop_weapon="golden_sword", image_size=240),
    ],
    
    # ==================== 31~40층: 골렘 ====================
    31: [
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
    ],
    32: [
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
        MonsterData("푸른 골렘", 140, 10, "golem2", "resources/png/enemy/golems/blue_golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 3, "max": 5}),
    ],
    33: [
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
        MonsterData("붉은 골렘", 160, 9, "golem3", "resources/png/enemy/golems/red_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 1, "max": 2}),
    ],
    34: [
        MonsterData("푸른 골렘", 140, 10, "golem2", "resources/png/enemy/golems/blue_golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 3, "max": 5}),
        MonsterData("붉은 골렘", 160, 9, "golem3", "resources/png/enemy/golems/red_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 1, "max": 2}),
    ],
    35: [
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
        MonsterData("검은 골렘", 180, 7, "golem4", "resources/png/enemy/golems/black_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 2, "max": 3}),
    ],
    36: [
        MonsterData("푸른 골렘", 140, 10, "golem2", "resources/png/enemy/golems/blue_golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 3, "max": 5}),
        MonsterData("검은 골렘", 180, 7, "golem4", "resources/png/enemy/golems/black_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 2, "max": 3}),
    ],
    37: [
        MonsterData("붉은 골렘", 160, 9, "golem3", "resources/png/enemy/golems/red_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 1, "max": 2}),
        MonsterData("킬러 골렘", 190, 11, "golem5", "resources/png/enemy/golems/killer_golem.png",
                    gold=None, image_size=200, drop_material={"type": "hero", "min": 1, "max": 2}),
    ],
    38: [
        MonsterData("검은 골렘", 180, 7, "golem4", "resources/png/enemy/golems/black_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 2, "max": 3}),
        MonsterData("킬러 골렘", 190, 11, "golem5", "resources/png/enemy/golems/killer_golem.png",
                    gold=None, image_size=200, drop_material={"type": "hero", "min": 1, "max": 2}),
    ],
    39: [
        MonsterData("푸른 골렘", 140, 10, "golem2", "resources/png/enemy/golems/blue_golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 3, "max": 5}),
        MonsterData("붉은 골렘", 160, 9, "golem3", "resources/png/enemy/golems/red_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 1, "max": 2}),
        MonsterData("검은 골렘", 180, 7, "golem4", "resources/png/enemy/golems/black_golem.png",
                    gold=None, image_size=200, drop_material={"type": "rare", "min": 2, "max": 3}),
        MonsterData("킬러 골렘", 190, 11, "golem5", "resources/png/enemy/golems/killer_golem.png",
                    gold=None, image_size=200, drop_material={"type": "hero", "min": 1, "max": 2}),
    ],
    40: [
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
        MonsterData("골렘", 150, 8, "golem1", "resources/png/enemy/golems/golem.png",
                    gold=None, image_size=200, drop_material={"type": "normal", "min": 2, "max": 4}),
        # 보스: 마공학 골렘 (전설 무기 + 전설 재료 드롭)
        MonsterData("마공학 골렘", 500, 12, "golem_boss", "resources/png/enemy/golems/hextech_golem.png",
                    gold=(800, 1500), drop_weapon="hextech_hammer", image_size=280, 
                    drop_material={"type": "legend", "min": 1, "max": 3}),
    ],
    
    # ==================== 41~45층: 사념 & 최종 보스 ====================
    41: [
        # 킹 슬라임의 사념 (무기 드롭 X, 골드만)
        MonsterData("킹 슬라임의 사념", 150, 12, "slime9", "resources/png/enemy/slimes/king_slime.png",
                    gold=(200, 400), drop_weapon=None, image_size=160),
    ],
    42: [
        # 뮤턴트 고블린의 사념 (무기 드롭 X, 골드만)
        MonsterData("뮤턴트 고블린의 사념", 300, 10, "goblin_boss", "resources/png/enemy/goblins/mutant_goblin.png",
                    gold=(300, 600), drop_weapon=None, image_size=280),
    ],
    43: [
        # 황금왕의 사념 (무기 드롭 X, 골드만)
        MonsterData("황금왕의 사념", 450, 14, "skeleton_boss", "resources/png/enemy/skeletons/rich_king.png",
                    gold=(600, 1200), drop_weapon=None, image_size=240),
    ],
    44: [
        # 마공학 골렘의 사념 (무기 드롭 X, 재료만)
        MonsterData("마공학 골렘의 사념", 700, 14, "golem_boss", "resources/png/enemy/golems/hextech_golem.png",
                    gold=None, drop_weapon=None, image_size=280,
                    drop_material={"type": "legend", "min": 2, "max": 5}),
    ],
    # 45층: 최종 보스 - 어둠의 신 (3페이즈 - boss_battle.py에서 처리)
    # 이 층은 특수 처리됨 (is_final_boss_floor() 함수로 체크)
    45: None,  # None이면 특수 보스전으로 처리
}


def get_floor_monsters(floor_num):
    """특정 층의 몬스터 리스트 반환"""
    if floor_num in FLOOR_DATA:
        monsters = FLOOR_DATA[floor_num]
        if monsters is None:
            # 45층 등 특수 보스전은 빈 리스트 반환
            return []
        return monsters.copy()
    else:
        return [MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slimes/slime.png")]


def is_final_boss_floor(floor_num):
    """최종 보스 층인지 확인 (45층)"""
    return floor_num == 45


def get_max_floor():
    """최대 층수 반환"""
    return max(FLOOR_DATA.keys()) if FLOOR_DATA else 1