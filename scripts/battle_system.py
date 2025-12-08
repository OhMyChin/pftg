import pygame
import random
from scripts.weapons import create_weapon
from scripts.floor import get_floor_monsters, get_max_floor, get_floor_background

# --- 한글 폰트 설정 ---
FONT_PATH = None
FONT_MAIN = None
FONT_SMALL = None

# --- 전투 상태 변수 ---
battle_player = None
battle_enemy = None
battle_message = ""
selected_skill_index = None

# --- 던전 진행 상태 ---
current_floor = 1
floor_monsters = []
current_monster_index = 0
current_monster_data = None  # 현재 몬스터 데이터 (드롭용)
current_bg_image = None  # 현재 층 배경 이미지 캐시

# --- 전투 상태 제어 ---
battle_state = {
    "turn_phase": "menu",
    "action_queue": [],
    "action_index": 0,
    "stage": "announce",
    "current_text": "",
    "waiting_for_click": False,
    "text_box_rect": None,
    "selected_row": 0,  # 선택된 행
    "selected_col": 0,  # 선택된 열
    "consumable_message": "",  # 소모품 사용 메시지
    "showing_consumable_message": False,  # 소모품 메시지 표시 중
    "drop_message": "",  # 드롭 메시지
    "showing_drop": False,  # 드롭 표시 중
}

# --- 플레이어 전용 클래스 ---
class Player:
    """전투용 플레이어 클래스"""
    def __init__(self, name, hp, speed, max_hp=None, weapon=None):
        self.name = name
        self.max_hp = max_hp if max_hp is not None else hp
        self.hp = hp
        self.speed = speed
        self.weapon = weapon
        self.image = None
    
    def get_available_skills(self):
        """현재 장착한 무기에서 사용 가능한 스킬 반환"""
        from scripts.skills import ALL_SKILLS
        
        if self.weapon:
            skills = self.weapon.get_skills()
            usable = [s for s in skills if self.weapon.durability >= s.durability_cost]
            if not usable:
                print(f"{self.name}의 {self.weapon.name}이(가) 부서졌습니다!")
                self.weapon = None
                return [ALL_SKILLS["struggle"]]
            return skills
        else:
            return [ALL_SKILLS["struggle"]]
    
    def equip_weapon(self, weapon):
        """무기 장착"""
        self.weapon = weapon


# --- 전투 헬퍼 함수들 ---
def decide_order(player, p_skill, enemy, e_skill):
    """스킬 우선순위 > 속도 > 랜덤 순으로 턴 결정"""
    if p_skill.priority != e_skill.priority:
        return [("player", p_skill), ("enemy", e_skill)] if p_skill.priority > e_skill.priority else [("enemy", e_skill), ("player", p_skill)]
    if player.speed != enemy.speed:
        return [("player", p_skill), ("enemy", e_skill)] if player.speed > enemy.speed else [("enemy", e_skill), ("player", p_skill)]
    order = [("player", p_skill), ("enemy", e_skill)]
    random.shuffle(order)
    return order


def calc_damage(attacker, skill, defender):
    """단순 데미지 계산"""
    return max(1, skill.power)


def wrap_battle_text(text, font, max_width):
    """전투 메시지 텍스트 줄바꿈"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def start_battle(game_state_ref, player_name):
    """던전 진입 시 전투 시작"""
    global battle_player, battle_enemy, battle_message, selected_skill_index
    global current_floor, floor_monsters, current_monster_index, current_bg_image

    if not battle_player:
        print("Error: battle_player not initialized.")
        return

    battle_player.speed = 12

    current_floor = 1
    floor_monsters = get_floor_monsters(current_floor)
    current_monster_index = 0
    
    # 배경 이미지 로드
    current_bg_image = load_floor_background(current_floor)

    spawn_next_monster()

    selected_skill_index = None
    battle_message = f"{battle_enemy.name}(이)가 나타났다!"
    game_state_ref["state"] = "battle"

    battle_state.update({
        "turn_phase": "text",
        "action_queue": [],
        "action_index": 0,
        "stage": "monster_appear",
        "current_text": f"{battle_enemy.name}(이)가 나타났다!",
        "waiting_for_click": True,
        "text_box_rect": None,
        "selected_row": 0,
        "selected_col": 0,
    })


def spawn_next_monster():
    """다음 몬스터 생성 - floor.py의 MonsterData를 복사해서 사용"""
    global battle_enemy, floor_monsters, current_monster_index, current_monster_data
    
    if current_monster_index < len(floor_monsters):
        monster_data = floor_monsters[current_monster_index]
        current_monster_data = monster_data  # 드롭 계산용 저장
        
        class Monster:
            pass
        
        battle_enemy = Monster()
        battle_enemy.name = monster_data.name
        battle_enemy.hp = monster_data.hp
        battle_enemy.max_hp = monster_data.hp
        battle_enemy.speed = monster_data.speed
        battle_enemy.weapon = create_weapon(monster_data.weapon_id)
        battle_enemy.image_size = getattr(monster_data, 'image_size', 160)  # 기본값 160
        
        try:
            battle_enemy.image = pygame.transform.scale(
                pygame.image.load(monster_data.image_path).convert_alpha(),
                (battle_enemy.image_size, battle_enemy.image_size)
            )
        except:
            print(f"Failed to load image: {monster_data.image_path}")
            battle_enemy.image = None
        
        def get_skills():
            from scripts.skills import ALL_SKILLS
            if battle_enemy.weapon:
                skills = battle_enemy.weapon.get_skills()
                # 무기가 부서졌거나 내구도가 부족하면 발버둥치기 사용
                if battle_enemy.weapon.is_broken():
                    return [ALL_SKILLS["struggle"]]
                usable = [s for s in skills if battle_enemy.weapon.durability >= s.durability_cost]
                if not usable:
                    return [ALL_SKILLS["struggle"]]
                return usable  # skills가 아닌 usable 반환
            else:
                return [ALL_SKILLS["struggle"]]
        
        battle_enemy.get_available_skills = get_skills
        
        current_monster_index += 1
        return True
    return False


def advance_floor():
    """다음 층으로 진행"""
    global current_floor, floor_monsters, current_monster_index, current_bg_image
    
    current_floor += 1
    floor_monsters = get_floor_monsters(current_floor)
    current_monster_index = 0
    
    # 배경 이미지 업데이트 (10층마다 변경)
    current_bg_image = load_floor_background(current_floor)
    
    spawn_next_monster()


def load_floor_background(floor_num):
    """층에 맞는 배경 이미지 로드"""
    try:
        bg_path = get_floor_background(floor_num)
        bg_image = pygame.image.load(bg_path).convert()
        return bg_image
    except:
        return None


def move_battle_selection(d_row, d_col):
    """전투 중 선택 이동"""
    new_row = battle_state["selected_row"] + d_row
    new_col = battle_state["selected_col"] + d_col
    
    # 2x2 그리드 범위 체크
    if 0 <= new_row <= 1:
        battle_state["selected_row"] = new_row
    if 0 <= new_col <= 1:
        battle_state["selected_col"] = new_col


def execute_battle_action(game_state_ref):
    """엔터키로 현재 선택된 액션 실행"""
    global battle_state, battle_player, battle_enemy
    
    # 텍스트 진행 중이면 텍스트 넘기기
    # 소모품 메시지 확인
    if battle_state["showing_consumable_message"] and battle_state["waiting_for_click"]:
        battle_state["showing_consumable_message"] = False
        battle_state["waiting_for_click"] = False
        battle_state["consumable_message"] = ""
        return False
    
    if battle_state["turn_phase"] == "text" and battle_state["waiting_for_click"]:
        if battle_state["stage"] == "announce" and battle_state["action_queue"]:
            # announce -> calculate
            actor_tag, skill_obj = battle_state["action_queue"][battle_state["action_index"]]
            if actor_tag == "player":
                attacker, defender = battle_player, battle_enemy
            else:
                attacker, defender = battle_enemy, battle_player

            if attacker.weapon and skill_obj.durability_cost > 0:
                attacker.weapon.use_skill(skill_obj)

            dmg = calc_damage(attacker, skill_obj, defender)
            defender.hp = max(0, defender.hp - dmg)
            battle_state["current_text"] = f"{defender.name}이(가) {dmg} 데미지를 입었다!"
            battle_state["stage"] = "calculate"
            
            if defender.hp <= 0:
                battle_state["action_queue"].clear()
            
        elif battle_state["stage"] == "calculate":
            # 다음 action으로 이동
            battle_state["action_index"] += 1
            if battle_state["action_index"] < len(battle_state["action_queue"]):
                actor_tag, skill_obj = battle_state["action_queue"][battle_state["action_index"]]
                who = battle_player.name if actor_tag == "player" else battle_enemy.name
                battle_state["current_text"] = f"{who}이(가) {skill_obj.name}을(를) 사용했다!"
                battle_state["stage"] = "announce"
            else:
                # 모든 행동 완료 → HP 체크
                if battle_player.hp <= 0:
                    battle_state["current_text"] = "플레이어 패배..."
                    battle_state["stage"] = "player_defeat"
                elif battle_enemy.hp <= 0:
                    battle_state["current_text"] = f"{battle_enemy.name}을(를) 격파했다!"
                    battle_state["stage"] = "enemy_defeat"
                else:
                    # 턴 종료
                    battle_state["turn_phase"] = "menu"
                    battle_state["waiting_for_click"] = False
                    battle_state["current_text"] = ""
                    battle_state["action_queue"].clear()
                    battle_state["action_index"] = 0
                    battle_state["stage"] = "announce"
                    battle_state["selected_row"] = 0
                    battle_state["selected_col"] = 0
        
        elif battle_state["stage"] == "player_defeat":
            battle_state["turn_phase"] = "end"
            battle_state["waiting_for_click"] = False
            battle_state["current_text"] = "플레이어 패배..."
            battle_state["action_queue"].clear()
        
        elif battle_state["stage"] == "enemy_defeat":
            # 드롭 처리
            if current_monster_data and not battle_state["showing_drop"]:
                drops = current_monster_data.get_drops()
                drop_msgs = []
                
                for drop in drops:
                    if drop["type"] == "gold":
                        game_state_ref["gold"] = game_state_ref.get("gold", 0) + drop["amount"]
                        drop_msgs.append(f"{drop['amount']}G")
                    elif drop["type"] == "weapon":
                        from scripts.inventory import player_inventory
                        player_inventory["weapons"].append(drop["item"])
                        drop_msgs.append(f"[{drop['item'].grade}] {drop['item'].name}")
                
                if drop_msgs:
                    battle_state["drop_message"] = "획득: " + ", ".join(drop_msgs)
                    battle_state["showing_drop"] = True
                    battle_state["current_text"] = battle_state["drop_message"]
                    return False
            
            # 드롭 메시지 확인 후 다음 진행
            battle_state["showing_drop"] = False
            battle_state["drop_message"] = ""
            
            if current_monster_index < len(floor_monsters):
                spawn_next_monster()
                battle_state["current_text"] = f"{battle_enemy.name}(이)가 나타났다!"
                battle_state["stage"] = "monster_appear"
            else:
                battle_state["turn_phase"] = "floor_clear"
                battle_state["waiting_for_click"] = False
                battle_state["current_text"] = f"{current_floor}층 클리어!"
                battle_state["action_queue"].clear()
        
        elif battle_state["stage"] == "monster_appear":
            battle_state["turn_phase"] = "menu"
            battle_state["waiting_for_click"] = False
            battle_state["current_text"] = ""
            battle_state["action_queue"].clear()
            battle_state["action_index"] = 0
            battle_state["stage"] = "announce"
            battle_state["selected_row"] = 0
            battle_state["selected_col"] = 0
        else:
            battle_state["turn_phase"] = "menu"
            battle_state["waiting_for_click"] = False
            battle_state["current_text"] = ""
            battle_state["selected_row"] = 0
            battle_state["selected_col"] = 0
        return False
    
    # 메뉴 버튼 클릭
    if battle_state["turn_phase"] == "menu" and not battle_state["current_text"]:
        selected_button = battle_state["selected_row"] * 2 + battle_state["selected_col"]
        
        if selected_button == 0:  # 전투
            battle_state["turn_phase"] = "skill_select"
            battle_state["current_text"] = ""
            battle_state["selected_row"] = 0
            battle_state["selected_col"] = 0
        elif selected_button == 1:  # 소비
            # 소모품 사용 화면으로 전환
            from scripts import consume_battle
            consume_battle.reset_consume_battle_state()
            game_state_ref["state"] = "consume_battle"
            return True
        elif selected_button == 2:  # 교체
            from scripts.inventory import player_inventory
            from scripts import weapon_swap
            if len(player_inventory["equipped_weapons"]) > 1:
                # 무기 교체 화면으로 전환
                weapon_swap.swap_state["selected_index"] = 0
                game_state_ref["state"] = "weapon_swap"
                return True
            else:
                battle_state["current_text"] = "교체할 무기가 없습니다!"
                battle_state["turn_phase"] = "text"
                battle_state["waiting_for_click"] = True
        elif selected_button == 3:  # 도망
            game_state_ref["state"] = "town"
            return True  # 마을로 돌아갔음을 표시
    
    # 스킬 선택
    elif battle_state["turn_phase"] == "skill_select":
        selected_button = battle_state["selected_row"] * 2 + battle_state["selected_col"]
        available_skills = battle_player.get_available_skills() if battle_player else []
        
        if selected_button < len(available_skills):
            selected_skill = available_skills[selected_button]
            
            if battle_player.weapon and selected_skill.durability_cost > 0:
                can_use = battle_player.weapon.durability >= selected_skill.durability_cost
            else:
                can_use = True
            
            if not can_use:
                battle_state["current_text"] = "무기의 내구도가 부족합니다!"
                battle_state["turn_phase"] = "text"
                battle_state["waiting_for_click"] = True
            else:
                enemy_skills = battle_enemy.get_available_skills() if battle_enemy else []
                if enemy_skills:
                    enemy_skill = random.choice(enemy_skills)

                    order = decide_order(battle_player, selected_skill, battle_enemy, enemy_skill)
                    battle_state["action_queue"] = order.copy()
                    battle_state["action_index"] = 0
                    battle_state["stage"] = "announce"
                    
                    actor_tag, skill_obj = battle_state["action_queue"][0]
                    who = battle_player.name if actor_tag == "player" else battle_enemy.name
                    battle_state["current_text"] = f"{who}이(가) {skill_obj.name}을(를) 사용했다!"
                    battle_state["turn_phase"] = "text"
                    battle_state["waiting_for_click"] = True
    
    return False  # 도망치지 않았음


def update_battle(screen, font, WIDTH, HEIGHT, game_state_ref, events):
    """전투 화면 업데이트"""
    global battle_player, battle_enemy, battle_state
    
    # weapon_swap에서 돌아왔으면 메뉴로 초기화
    if battle_state.get("returning_from_swap", False):
        battle_state["turn_phase"] = "menu"
        battle_state["selected_row"] = 0
        battle_state["selected_col"] = 0
        battle_state["returning_from_swap"] = False

    # ---------- 레이아웃 설정 ----------
    # 배경 이미지 그리기
    if current_bg_image:
        scaled_bg = pygame.transform.scale(current_bg_image, (WIDTH, HEIGHT))
        screen.blit(scaled_bg, (0, 0))
    else:
        screen.fill((30, 30, 60))

    # --- 몬스터 표시 (오른쪽, 중심 기준으로 확대) ---
    # 기본 크기 (160px)를 기준으로 중심점 설정
    base_size = 160  # 기본 몬스터 크기
    enemy_center_x = WIDTH - 300 + (base_size // 2)  # 기본 크기 기준 중심 X
    enemy_base_y = 280  # 바닥 기준 Y

    # 층 진행도 (왼쪽 위)
    floor_info_text = font.render(
        f"{current_floor}층 - {current_monster_index}/{len(floor_monsters)}", 
        True, (200, 200, 200)
    )
    screen.blit(floor_info_text, (20, 20))

    if battle_enemy and battle_enemy.image:
        # 몬스터 이미지 크기 가져오기
        enemy_image_width = battle_enemy.image.get_width()
        enemy_image_height = battle_enemy.image.get_height()
        
        # 체력바 설정 (이미지 가로 길이에 맞춤)
        hp_bar_width = enemy_image_width
        hp_bar_height = 25
        name_hp_gap = 5  # 이름과 체력바 사이 간격
        hp_image_gap = 5  # 체력바와 이미지 사이 간격
        
        # 체력바 최대 높이 제한 (이 Y 좌표 아래로만 체력바 표시)
        max_hp_bar_y = 50  # 화면 상단에서 최소 50px 여유
        
        # 중심 기준으로 이미지 위치 계산 (8방향 확대 효과)
        enemy_x = enemy_center_x - (enemy_image_width // 2)  # 중심에서 좌우로 확대
        enemy_y = enemy_base_y - enemy_image_height  # 바닥에서 위로 확대
        
        # 체력바 위치 계산 (이미지 바로 위)
        hp_bar_y = enemy_y - hp_image_gap - hp_bar_height
        
        # 체력바가 최대 높이를 넘으면 기준점을 아래로 내림
        if hp_bar_y < max_hp_bar_y:
            # 체력바를 max_hp_bar_y에 맞추고, 그에 따라 이미지도 아래로 이동
            hp_bar_y = max_hp_bar_y
            enemy_y = hp_bar_y + hp_bar_height + hp_image_gap
        
        # 체력바 X 위치도 이미지 중심에 맞춤
        hp_bar_x = enemy_center_x - (hp_bar_width // 2)
        
        # 이름 폰트 크기 자동 조절 (체력바 너비에 맞춤)
        name_font_size = 32  # 기본 폰트 크기
        if FONT_PATH:
            name_font = pygame.font.Font(FONT_PATH, name_font_size)
        else:
            name_font = pygame.font.Font(None, name_font_size)
        
        # 이름이 체력바보다 길면 폰트 크기 줄이기
        while name_font.size(battle_enemy.name)[0] > hp_bar_width and name_font_size > 16:
            name_font_size -= 2
            if FONT_PATH:
                name_font = pygame.font.Font(FONT_PATH, name_font_size)
            else:
                name_font = pygame.font.Font(None, name_font_size)
        
        # 이름 위치 (체력바 바로 위, 중앙 정렬)
        name_y = hp_bar_y - name_hp_gap - name_font_size
        
        # 이미지 그리기
        screen.blit(battle_enemy.image, (enemy_x, enemy_y))

        # 이름 그리기 (중앙 정렬, 자동 조절된 폰트)
        enemy_name_text = name_font.render(f"{battle_enemy.name}", True, (255, 255, 255))
        name_x = enemy_center_x - (enemy_name_text.get_width() // 2)
        screen.blit(enemy_name_text, (name_x, name_y))

        # 체력바 그리기
        hp_ratio = max(0, battle_enemy.hp) / (battle_enemy.max_hp if battle_enemy.max_hp else 1)
        hp_back = pygame.Rect(hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height)
        pygame.draw.rect(screen, (60, 60, 60), hp_back)
        hp_fill = pygame.Rect(hp_bar_x, hp_bar_y, int(hp_bar_width * hp_ratio), hp_bar_height)
        pygame.draw.rect(screen, (200, 50, 50), hp_fill)
        pygame.draw.rect(screen, (100, 100, 100), hp_back, 2)  # 테두리
        
        # 체력바 안에 HP 수치 표시
        hp_text = font.render(f"{max(0, battle_enemy.hp)}/{battle_enemy.max_hp}", True, (255, 255, 255))
        hp_text_rect = hp_text.get_rect(center=(hp_bar_x + hp_bar_width // 2, hp_bar_y + hp_bar_height // 2))
        screen.blit(hp_text, hp_text_rect)


    # 플레이어 정보 (왼쪽 하단)
    player_x = 100
    player_y = HEIGHT - 360

    if battle_player and battle_player.image:
        # 플레이어 이미지 크기 가져오기
        player_image_width = battle_player.image.get_width()
        
        # 체력바 설정 (이미지 가로 길이에 맞춤)
        hp_bar_width_p = player_image_width
        hp_bar_height_p = 25
        name_hp_gap_p = 5  # 이름과 체력바 사이 간격
        hp_image_gap_p = 5  # 체력바와 이미지 사이 간격
        
        # 체력바 위치 (이미지 바로 위)
        hp_bar_y_p = player_y - hp_image_gap_p - hp_bar_height_p
        
        # 이름 위치 (체력바 바로 위)
        name_y_p = hp_bar_y_p - name_hp_gap_p - 30  # 폰트 높이 약 30px
        
        # 이미지 그리기
        screen.blit(battle_player.image, (player_x, player_y))
        
        # 이름 그리기
        player_name_text = font.render(f"{battle_player.name}", True, (255, 255, 255))
        screen.blit(player_name_text, (player_x, name_y_p))

        # 체력바 그리기
        hp_ratio_p = max(0, battle_player.hp) / (battle_player.max_hp if battle_player.max_hp else 1)
        hp_back_p = pygame.Rect(player_x, hp_bar_y_p, hp_bar_width_p, hp_bar_height_p)
        pygame.draw.rect(screen, (60, 60, 60), hp_back_p)
        hp_fill_p = pygame.Rect(player_x, hp_bar_y_p, int(hp_bar_width_p * hp_ratio_p), hp_bar_height_p)
        pygame.draw.rect(screen, (50, 200, 50), hp_fill_p)
        pygame.draw.rect(screen, (100, 100, 100), hp_back_p, 2)  # 테두리
        
        # 체력바 안에 HP 수치 표시
        hp_text_p = font.render(f"{max(0, battle_player.hp)}/{battle_player.max_hp}", True, (255, 255, 255))
        hp_text_rect_p = hp_text_p.get_rect(center=(player_x + hp_bar_width_p // 2, hp_bar_y_p + hp_bar_height_p // 2))
        screen.blit(hp_text_p, hp_text_rect_p)


    # --- 무기 정보 박스 (왼쪽 하단) ---
    weapon_box_size = 120
    weapon_box_x = 20
    weapon_box_y = HEIGHT - 180
    
    pygame.draw.rect(screen, (40, 40, 60), (weapon_box_x, weapon_box_y, weapon_box_size, weapon_box_size))
    pygame.draw.rect(screen, (100, 100, 150), (weapon_box_x, weapon_box_y, weapon_box_size, weapon_box_size), 2)
    
    weapon_img_size = 70
    weapon_img_x = weapon_box_x + (weapon_box_size - weapon_img_size) // 2
    weapon_img_y = weapon_box_y + 10
    
    if battle_player and battle_player.weapon:
        try:
            weapon_image_path = f"resources/png/weapon/{battle_player.weapon.id}.png"
            weapon_img = pygame.image.load(weapon_image_path).convert_alpha()
            weapon_img = pygame.transform.scale(weapon_img, (weapon_img_size, weapon_img_size))
            screen.blit(weapon_img, (weapon_img_x, weapon_img_y))
        except:
            pygame.draw.rect(screen, (60, 60, 80), (weapon_img_x, weapon_img_y, weapon_img_size, weapon_img_size))
            pygame.draw.rect(screen, (120, 120, 140), (weapon_img_x, weapon_img_y, weapon_img_size, weapon_img_size), 1)
    else:
        pygame.draw.rect(screen, (60, 60, 80), (weapon_img_x, weapon_img_y, weapon_img_size, weapon_img_size))
        pygame.draw.rect(screen, (120, 120, 140), (weapon_img_x, weapon_img_y, weapon_img_size, weapon_img_size), 1)
    
    if battle_player:
        if battle_player.weapon:
            durability_text = font.render(
                f"{battle_player.weapon.durability}/{battle_player.weapon.max_durability}",
                True, (200, 200, 200)
            )
            durability_rect = durability_text.get_rect(centerx=weapon_box_x + weapon_box_size // 2, 
                                                       y=weapon_img_y + weapon_img_size + 8)
            screen.blit(durability_text, durability_rect)
        else:
            no_weapon_text = font.render("맨손", True, (150, 150, 150))
            no_weapon_rect = no_weapon_text.get_rect(centerx=weapon_box_x + weapon_box_size // 2,
                                                      y=weapon_img_y + weapon_img_size + 8)
            screen.blit(no_weapon_text, no_weapon_rect)

    # ---------- 전투 종료 상태 처리 ----------
    if battle_state["turn_phase"] == "floor_clear":
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        pygame.draw.rect(screen, (255, 255, 255), text_box, 2)
        text_surface = font.render(battle_state["current_text"], True, (255, 255, 255))
        screen.blit(text_surface, (text_box.x + 20, text_box.y + 30))

        btn_w, btn_h = 180, 50
        gap = 40
        
        has_next_floor = current_floor < get_max_floor()
        
        if has_next_floor:
            next_rect = pygame.Rect(WIDTH//2 - btn_w - gap//2, HEIGHT//2, btn_w, btn_h)
            town_rect = pygame.Rect(WIDTH//2 + gap//2, HEIGHT//2, btn_w, btn_h)
            
            # 선택 표시 (0: 다음 층, 1: 마을)
            if battle_state["selected_col"] == 0:
                pygame.draw.rect(screen, (120, 200, 120), next_rect)
                pygame.draw.rect(screen, (100, 150, 255), next_rect, 4)
            else:
                pygame.draw.rect(screen, (80, 150, 80), next_rect)
            
            if battle_state["selected_col"] == 1:
                pygame.draw.rect(screen, (200, 120, 120), town_rect)
                pygame.draw.rect(screen, (100, 150, 255), town_rect, 4)
            else:
                pygame.draw.rect(screen, (150, 80, 80), town_rect)

            next_txt = font.render(f"{current_floor + 1}층으로", True, (255, 255, 255))
            town_txt = font.render("돌아가기", True, (255, 255, 255))
            screen.blit(next_txt, next_txt.get_rect(center=next_rect.center))
            screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        battle_state["selected_col"] = 0
                    elif event.key == pygame.K_d:
                        battle_state["selected_col"] = 1
                    elif event.key == pygame.K_RETURN:
                        if battle_state["selected_col"] == 0:
                            advance_floor()
                            battle_state["turn_phase"] = "menu"
                            battle_state["waiting_for_click"] = False
                            battle_state["current_text"] = ""
                            battle_state["selected_row"] = 0
                            battle_state["selected_col"] = 0
                            return
                        else:
                            game_state_ref["state"] = "town"
                            return
        else:
            town_rect = pygame.Rect(WIDTH//2 - btn_w//2, HEIGHT//2, btn_w, btn_h)
            pygame.draw.rect(screen, (200, 120, 120), town_rect)
            pygame.draw.rect(screen, (100, 150, 255), town_rect, 4)
            town_txt = font.render("돌아가기", True, (255, 255, 255))
            screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_state_ref["state"] = "town"
                        return
        
        return

    if battle_state["turn_phase"] == "end":
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        pygame.draw.rect(screen, (255, 255, 255), text_box, 2)
        text_surface = font.render(battle_state["current_text"], True, (255, 255, 255))
        screen.blit(text_surface, (text_box.x + 20, text_box.y + 30))

        btn_w, btn_h = 180, 50
        town_rect = pygame.Rect(WIDTH//2 - btn_w//2, HEIGHT//2, btn_w, btn_h)
        pygame.draw.rect(screen, (200, 120, 120), town_rect)
        pygame.draw.rect(screen, (100, 150, 255), town_rect, 4)
        town_txt = font.render("돌아가기", True, (255, 255, 255))
        screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state_ref["state"] = "town"
                    return
        
        return

    # ---------- 버튼 위치 계산 ----------
    button_w = 240
    button_h = 60
    gap = 15
    
    start_x = (WIDTH - (button_w * 2 + gap)) // 2
    start_y = HEIGHT - 180

    skill_button_rects = []
    available_skills = battle_player.get_available_skills() if battle_player else []
    
    for i in range(4):
        bx = start_x + (i % 2) * (button_w + gap)
        by = start_y + (i // 2) * (button_h + gap)
        skill_button_rects.append(pygame.Rect(bx, by, button_w, button_h))

    menu_button_rects = []
    for i in range(4):
        bx = start_x + (i % 2) * (button_w + gap)
        by = start_y + (i // 2) * (button_h + gap)
        menu_button_rects.append(pygame.Rect(bx, by, button_w, button_h))

    # ---------- 버튼 그리기 ----------
    if battle_state["turn_phase"] == "skill_select":
        for i, rect in enumerate(skill_button_rects):
            row = i // 2
            col = i % 2
            is_selected = (battle_state["selected_row"] == row and 
                          battle_state["selected_col"] == col)
            
            if battle_player and i < len(available_skills):
                skill = available_skills[i]
                label = skill.name
                
                can_use = True
                if battle_player.weapon and skill.durability_cost > 0:
                    can_use = battle_player.weapon.durability >= skill.durability_cost
                
                if is_selected:
                    color = (100, 100, 120) if not can_use else (200, 200, 255)
                else:
                    color = (80, 80, 80) if not can_use else (150, 150, 250)
            else:
                label = "—"
                color = (80, 80, 80)

            pygame.draw.rect(screen, color, rect)
            
            # 선택된 버튼 하이라이트
            if is_selected:
                pygame.draw.rect(screen, (100, 150, 255), rect, 4)
            
            txt = font.render(label, True, (0, 0, 0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
    
    elif battle_state["turn_phase"] in ["menu", "text"]:
        menu_labels = ["전투", "소비", "교체", "도망"]
        menu_colors = [(150, 150, 250), (100, 200, 100), (200, 150, 100), (200, 100, 100)]
        
        for i, rect in enumerate(menu_button_rects):
            row = i // 2
            col = i % 2
            is_selected = (battle_state["selected_row"] == row and 
                          battle_state["selected_col"] == col and
                          battle_state["turn_phase"] == "menu")
            
            if is_selected:
                # 선택된 버튼은 더 밝게
                r, g, b = menu_colors[i]
                color = (min(255, r + 50), min(255, g + 50), min(255, b + 50))
            else:
                color = menu_colors[i]
            
            pygame.draw.rect(screen, color, rect)
            
            # 선택된 버튼 하이라이트
            if is_selected:
                pygame.draw.rect(screen, (100, 150, 255), rect, 4)
            
            txt = font.render(menu_labels[i], True, (0, 0, 0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

    # ---------- 키보드 이벤트 처리 ----------
    for event in events:
        if event.type == pygame.KEYDOWN:
            # ESC: 도망 또는 뒤로가기
            if event.key == pygame.K_ESCAPE:
                if battle_state["turn_phase"] == "skill_select":
                    battle_state["turn_phase"] = "menu"
                    battle_state["selected_row"] = 0
                    battle_state["selected_col"] = 0
                elif battle_state["turn_phase"] == "menu":
                    game_state_ref["state"] = "town"
                    return
            
            # 텍스트 진행 중이 아닐 때만 이동 가능
            elif battle_state["turn_phase"] != "text":
                if event.key == pygame.K_w:
                    move_battle_selection(-1, 0)
                elif event.key == pygame.K_s:
                    move_battle_selection(1, 0)
                elif event.key == pygame.K_a:
                    move_battle_selection(0, -1)
                elif event.key == pygame.K_d:
                    move_battle_selection(0, 1)
            
            # 엔터: 액션 실행
            if event.key == pygame.K_RETURN:
                if execute_battle_action(game_state_ref):
                    return  # 도망쳤으면 즉시 종료

    # ---------- 소모품 메시지 박스 렌더 (우선순위) ----------
    if battle_state["showing_consumable_message"]:
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        battle_state["text_box_rect"] = text_box
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        pygame.draw.rect(screen, (255, 255, 255), text_box, 2)

        # 텍스트 줄바꿈 처리
        max_text_width = text_box.width - 40
        lines = wrap_battle_text(battle_state["consumable_message"], font, max_text_width)
        
        # 여러 줄 렌더링
        y_offset = text_box.y + 20
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (text_box.x + 20, y_offset))
            y_offset += 30
        
        # 엔터 대기 화살표
        if battle_state["waiting_for_click"]:
            arrow_text = pygame.font.SysFont("consolas", 30).render("▼", True, (255, 255, 255))
            screen.blit(arrow_text, (text_box.x + text_box.width - 40, text_box.y + text_box.height - 40))
    
    # ---------- 전투 텍스트 박스 렌더 ----------
    elif battle_state["current_text"] and battle_state["turn_phase"] not in ["end", "floor_clear"]:
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        battle_state["text_box_rect"] = text_box
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        
        # 드롭 메시지면 금색 테두리
        if battle_state["showing_drop"]:
            pygame.draw.rect(screen, (255, 215, 0), text_box, 2)
            text_color = (255, 215, 0)
        else:
            pygame.draw.rect(screen, (255, 255, 255), text_box, 2)
            text_color = (255, 255, 255)

        # 텍스트 줄바꿈 처리
        max_text_width = text_box.width - 40
        lines = wrap_battle_text(battle_state["current_text"], font, max_text_width)
        
        # 여러 줄 렌더링
        y_offset = text_box.y + 20
        for line in lines:
            text_surface = font.render(line, True, text_color)
            screen.blit(text_surface, (text_box.x + 20, y_offset))
            y_offset += 30
        
        # 클릭 안내 화살표
        if battle_state["waiting_for_click"]:
            arrow_text = pygame.font.SysFont("consolas", 30).render("▼", True, text_color)
            screen.blit(arrow_text, (text_box.x + text_box.width - 40, text_box.y + text_box.height - 40))
    else:
        battle_state["text_box_rect"] = None