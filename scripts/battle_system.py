# scripts/battle_system.py
import pygame
import random
from scripts.weapons import create_weapon
from scripts.floor import get_floor_monsters, get_max_floor

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

# --- 전투 상태 제어 ---
battle_state = {
    "turn_phase": "menu",
    "action_queue": [],
    "action_index": 0,
    "stage": "announce",
    "current_text": "",
    "waiting_for_click": False,
    "text_box_rect": None
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


def start_battle(game_state_ref, player_name):
    """던전 진입 시 전투 시작"""
    global battle_player, battle_enemy, battle_message, selected_skill_index
    global current_floor, floor_monsters, current_monster_index

    if not battle_player:
        print("Error: battle_player not initialized.")
        return

    # ✅ 무기 상태 그대로 유지 (맨손이면 맨손으로 전투)
    # 무기 자동 장착 로직 제거
    
    battle_player.speed = 12

    current_floor = 1
    floor_monsters = get_floor_monsters(current_floor)
    current_monster_index = 0

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
        "text_box_rect": None
    })


def spawn_next_monster():
    """다음 몬스터 생성 - floor.py의 MonsterData를 복사해서 사용"""
    global battle_enemy, floor_monsters, current_monster_index
    
    if current_monster_index < len(floor_monsters):
        monster_data = floor_monsters[current_monster_index]
        
        # ✅ 새로운 객체 생성 (원본 데이터 보호)
        class Monster:
            pass
        
        battle_enemy = Monster()
        battle_enemy.name = monster_data.name
        battle_enemy.hp = monster_data.hp  # ✅ 복사
        battle_enemy.max_hp = monster_data.hp
        battle_enemy.speed = monster_data.speed
        battle_enemy.weapon = create_weapon(monster_data.weapon_id)
        
        # 이미지 로드
        try:
            battle_enemy.image = pygame.transform.scale(
                pygame.image.load(monster_data.image_path).convert_alpha(),
                (160, 160)
            )
        except:
            print(f"Failed to load image: {monster_data.image_path}")
            battle_enemy.image = None
        
        # get_available_skills 메서드 추가
        def get_skills():
            from scripts.skills import ALL_SKILLS
            if battle_enemy.weapon:
                skills = battle_enemy.weapon.get_skills()
                usable = [s for s in skills if battle_enemy.weapon.durability >= s.durability_cost]
                if not usable:
                    return [ALL_SKILLS["struggle"]]
                return skills
            else:
                return [ALL_SKILLS["struggle"]]
        
        battle_enemy.get_available_skills = get_skills
        
        current_monster_index += 1
        return True
    return False


def advance_floor():
    """다음 층으로 진행"""
    global current_floor, floor_monsters, current_monster_index
    
    current_floor += 1
    floor_monsters = get_floor_monsters(current_floor)
    current_monster_index = 0
    
    spawn_next_monster()


def update_battle(screen, font, WIDTH, HEIGHT, game_state_ref, events):
    """전투 화면 업데이트"""
    global battle_player, battle_enemy, battle_state

    # ---------- 레이아웃 설정 ----------
    screen.fill((30, 30, 60))

    # --- 몬스터 표시 (오른쪽 위) ---
    enemy_x = WIDTH - 300
    enemy_y = 120

    if battle_enemy and battle_enemy.image:
        screen.blit(battle_enemy.image, (enemy_x, enemy_y))

        floor_info_text = font.render(
            f"{current_floor}층 - {current_monster_index}/{len(floor_monsters)}", 
            True, (200, 200, 200)
        )
        screen.blit(floor_info_text, (enemy_x, enemy_y - 70))

        enemy_name_text = font.render(f"{battle_enemy.name}  HP: {battle_enemy.hp}/{battle_enemy.max_hp}", True, (255, 255, 255))
        screen.blit(enemy_name_text, (enemy_x, enemy_y - 40))

        hp_ratio = max(0, battle_enemy.hp) / (battle_enemy.max_hp if battle_enemy.max_hp else 1)
        hp_back = pygame.Rect(enemy_x, enemy_y - 10, 160, 10)
        pygame.draw.rect(screen, (60, 60, 60), hp_back)
        hp_fill = pygame.Rect(enemy_x, enemy_y - 10, int(160 * hp_ratio), 10)
        pygame.draw.rect(screen, (200, 50, 50), hp_fill)

    # 플레이어 정보 (왼쪽 하단)
    player_x = 100
    player_y = HEIGHT - 360

    if battle_player and battle_player.image:
        screen.blit(battle_player.image, (player_x, player_y))
        
        player_name_text = font.render(f"{battle_player.name}  HP: {battle_player.hp}/{battle_player.max_hp}", True, (255, 255, 255))
        screen.blit(player_name_text, (player_x, player_y - 45))

        hp_ratio_p = max(0, battle_player.hp) / (battle_player.max_hp if battle_player.max_hp else 1)
        hp_back_p = pygame.Rect(player_x, player_y - 15, 160, 10)
        pygame.draw.rect(screen, (60, 60, 60), hp_back_p)
        hp_fill_p = pygame.Rect(player_x, player_y - 15, int(160 * hp_ratio_p), 10)
        pygame.draw.rect(screen, (50, 200, 50), hp_fill_p)

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

    # ---------- 전투 종료 체크 ----------
    # HP 0 체크는 데미지 계산 직후에만 수행

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
            
            pygame.draw.rect(screen, (80, 150, 80), next_rect)
            pygame.draw.rect(screen, (150, 80, 80), town_rect)

            next_txt = font.render(f"{current_floor + 1}층으로", True, (255, 255, 255))
            town_txt = font.render("마을로 돌아가기", True, (255, 255, 255))
            screen.blit(next_txt, next_txt.get_rect(center=next_rect.center))
            screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if next_rect.collidepoint(mouse_pos):
                        advance_floor()
                        battle_state["turn_phase"] = "menu"
                        battle_state["waiting_for_click"] = False
                        battle_state["current_text"] = ""
                        return
                    elif town_rect.collidepoint(mouse_pos):
                        game_state_ref["state"] = "town"
                        return
        else:
            town_rect = pygame.Rect(WIDTH//2 - btn_w//2, HEIGHT//2, btn_w, btn_h)
            pygame.draw.rect(screen, (150, 80, 80), town_rect)
            town_txt = font.render("마을로 돌아가기", True, (255, 255, 255))
            screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if town_rect.collidepoint(mouse_pos):
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
        pygame.draw.rect(screen, (150, 80, 80), town_rect)
        town_txt = font.render("마을로 돌아가기", True, (255, 255, 255))
        screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if town_rect.collidepoint(mouse_pos):
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

    # ---------- 버튼 그리기 (텍스트박스 있어도 항상 그리기) ----------
    if battle_state["turn_phase"] == "skill_select":
        for i, rect in enumerate(skill_button_rects):
            if battle_player and i < len(available_skills):
                skill = available_skills[i]
                label = skill.name
                
                can_use = True
                if battle_player.weapon and skill.durability_cost > 0:
                    can_use = battle_player.weapon.durability >= skill.durability_cost
                
                color = (80, 80, 80) if not can_use else (150, 150, 250)
            else:
                label = "—"
                color = (80, 80, 80)

            pygame.draw.rect(screen, color, rect)
            txt = font.render(label, True, (0, 0, 0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
    
    elif battle_state["turn_phase"] in ["menu", "text"]:
        # ✅ 텍스트 상태에서도 버튼 그리기
        menu_labels = ["전투", "소비", "교체", "도망"]
        menu_colors = [(150, 150, 250), (100, 200, 100), (200, 150, 100), (200, 100, 100)]
        
        for i, rect in enumerate(menu_button_rects):
            pygame.draw.rect(screen, menu_colors[i], rect)
            txt = font.render(menu_labels[i], True, (0, 0, 0))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

    # ---------- 이벤트 처리 ----------
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # ✅ 1) 텍스트 진행 중이면 텍스트박스 클릭 체크
            if battle_state["turn_phase"] == "text" and battle_state["waiting_for_click"]:
                # 텍스트박스 영역 클릭 시에만 진행
                if battle_state["text_box_rect"] and battle_state["text_box_rect"].collidepoint(mouse_pos):
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
                        
                        # ✅ 데미지 계산 직후 HP 체크
                        if defender.hp <= 0:
                            battle_state["action_queue"].clear()  # 남은 행동 취소
                        
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
                    
                    elif battle_state["stage"] == "player_defeat":
                        # 플레이어 패배 확정
                        battle_state["turn_phase"] = "end"
                        battle_state["waiting_for_click"] = False
                        battle_state["current_text"] = "플레이어 패배..."
                        battle_state["action_queue"].clear()
                    
                    elif battle_state["stage"] == "enemy_defeat":
                        # 몬스터 처치 확정 - 다음 몬스터 소환
                        if current_monster_index < len(floor_monsters):
                            spawn_next_monster()
                            battle_state["current_text"] = f"{battle_enemy.name}(이)가 나타났다!"
                            battle_state["stage"] = "monster_appear"
                        else:
                            # 층 클리어
                            battle_state["turn_phase"] = "floor_clear"
                            battle_state["waiting_for_click"] = False
                            battle_state["current_text"] = f"{current_floor}층 클리어!"
                            battle_state["action_queue"].clear()
                    
                    elif battle_state["stage"] == "monster_appear":
                        # 몬스터 등장 후 메뉴로
                        battle_state["turn_phase"] = "menu"
                        battle_state["waiting_for_click"] = False
                        battle_state["current_text"] = ""
                        battle_state["action_queue"].clear()
                        battle_state["action_index"] = 0
                        battle_state["stage"] = "announce"
                    else:
                        # ✅ 단순 알림 메시지는 바로 메뉴로
                        battle_state["turn_phase"] = "menu"
                        battle_state["waiting_for_click"] = False
                        battle_state["current_text"] = ""
            
            # ✅ 2) 메뉴 버튼 클릭 처리
            elif battle_state["turn_phase"] == "menu" and not battle_state["current_text"]:
                clicked_button = None
                for i, rect in enumerate(menu_button_rects):
                    if rect.collidepoint(mouse_pos):
                        clicked_button = i
                        break
                
                if clicked_button == 0:  # 전투 버튼
                    battle_state["turn_phase"] = "skill_select"
                    battle_state["current_text"] = ""
                elif clicked_button == 1:  # 소비 버튼
                    battle_state["current_text"] = "아직 구현되지 않은 기능입니다."
                    battle_state["turn_phase"] = "text"
                    battle_state["waiting_for_click"] = True
                elif clicked_button == 2:  # 교체 버튼
                    battle_state["current_text"] = "아직 구현되지 않은 기능입니다."
                    battle_state["turn_phase"] = "text"
                    battle_state["waiting_for_click"] = True
                elif clicked_button == 3:  # 도망 버튼
                    game_state_ref["state"] = "town"
                    return
            
            # ✅ 3) 스킬 선택 상태
            elif battle_state["turn_phase"] == "skill_select":
                clicked_button = None
                for i, rect in enumerate(skill_button_rects):
                    if rect.collidepoint(mouse_pos):
                        clicked_button = i
                        break
                
                if clicked_button is not None and battle_player and clicked_button < len(available_skills):
                    selected_skill = available_skills[clicked_button]
                    
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

    # ---------- 전투 텍스트 박스 렌더 (버튼 위에 그리기) ----------
    if battle_state["current_text"] and battle_state["turn_phase"] not in ["end", "floor_clear"]:
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        battle_state["text_box_rect"] = text_box
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        pygame.draw.rect(screen, (255, 255, 255), text_box, 2)

        text_surface = font.render(battle_state["current_text"], True, (255, 255, 255))
        screen.blit(text_surface, (text_box.x + 20, text_box.y + 30))
        
        # ✅ 클릭 안내 화살표 (더 큰 폰트 사용)
        if battle_state["waiting_for_click"]:
            if FONT_MAIN:  # 더 큰 폰트 사용
                arrow_text = FONT_MAIN.render("▼", True, (255, 255, 100))
            else:
                arrow_text = font.render(">>", True, (255, 255, 100))  # 폰트 없으면 대체
            screen.blit(arrow_text, (text_box.x + text_box.width - 60, text_box.y + text_box.height - 50))
    else:
        battle_state["text_box_rect"] = None