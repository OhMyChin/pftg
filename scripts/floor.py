from scripts.weapons import create_weapon

class MonsterData:
    """몬스터 데이터 클래스"""
    def __init__(self, name, hp, speed, weapon_id, image_path):
        self.name = name
        self.hp = hp
        self.speed = speed
        self.weapon_id = weapon_id
        self.image_path = image_path

# ==================== 층별 몬스터 배치 ====================

FLOOR_DATA = {
    1: [
        MonsterData("슬라임", 30, 8, "slime1", "resources/png/enemy/slime.png"),
    ],
    2: [
        MonsterData("빨간 슬라임", 35, 9, "slime2", "resources/png/enemy/slime.png"),
    ],
    3: [
        MonsterData("노랑 슬라임", 35, 9, "slime3", "resources/png/enemy/yellow_slime.png"),
        MonsterData("마그마 슬라임", 50, 15, "slime5", "resources/png/enemy/magma_slime.png"),
    ],
    4: [
        MonsterData("파란 슬라임", 35, 9, "slime4", "resources/png/enemy/blue_slime.png"),
        MonsterData("소드 슬라임", 50, 15, "slime6", "resources/png/enemy/sword_slime.png"),
    ],
    5: [
        MonsterData("빨간 슬라임", 35, 9, "slime2", "resources/png/enemy/slime.png"),
        MonsterData("노란 슬라임", 25, 15, "slime3", "resources/png/enemy/yellow_slime.png"),
        MonsterData("파란 슬라임", 35, 9, "slime4", "resources/png/enemy/blue_slime.png"),
    ]
}

def get_floor_monsters(floor_num):
    """특정 층의 몬스터 리스트 반환"""
    if floor_num in FLOOR_DATA:
        return FLOOR_DATA[floor_num].copy()
    else:
        # 층이 정의되지 않았으면 기본 몬스터 반환
        return [MonsterData("슬라임", 30, 8, "slime", "resources/png/enemy/slime.png")]

def get_max_floor():
    """최대 층수 반환"""
    return max(FLOOR_DATA.keys()) if FLOOR_DATA else 1