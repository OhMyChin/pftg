import random
from scripts.weapons import create_weapon

class MonsterData:
    """몬스터 데이터 클래스"""
    def __init__(self, name, hp, speed, weapon_id, image_path, 
                 gold=(5, 15), drop_weapon=None):
        """
        gold: (최소, 최대) 골드 드롭 범위
        drop_weapon: 드롭할 무기 ID (보스 전용, None이면 무기 안떨굼)
        """
        self.name = name
        self.hp = hp
        self.speed = speed
        self.weapon_id = weapon_id
        self.image_path = image_path
        self.gold = gold
        self.drop_weapon = drop_weapon
    
    def get_drops(self):
        """드롭 아이템 계산"""
        drops = []
        
        # 골드 드롭
        gold_amount = random.randint(self.gold[0], self.gold[1])
        drops.append({"type": "gold", "amount": gold_amount})
        
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
}


def get_floor_monsters(floor_num):
    """특정 층의 몬스터 리스트 반환"""
    if floor_num in FLOOR_DATA:
        return FLOOR_DATA[floor_num].copy()
    else:
        return [MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slimes/slime.png")]


def get_max_floor():
    """최대 층수 반환"""
    return max(FLOOR_DATA.keys()) if FLOOR_DATA else 1