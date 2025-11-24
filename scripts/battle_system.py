import pygame
import random
from scripts.weapons import create_weapon

# --- 한글 폰트 설정 ---
FONT_PATH = None
FONT_MAIN = None
FONT_SMALL = None

# --- 전투 상태 변수 ---
battle_player = None
battle_enemy = None
battle_message = ""
selected_skill_index = None

# --- 전투 상태 제어 ---
battle_state = {
    "turn_phase": "menu",  # menu, skill_select, text 등
    "action_queue": [],
    "action_index": 0,
    "stage": "announce",
    "current_text": "",
    "waiting_for_click": False
}

# --- 전투용 데이터 구조 ---
class Entity:
    def __init__(self, name, hp, speed, max_hp=None, weapon=None):
        self.name = name
        self.max_hp = max_hp if max_hp is not None else hp
        self.hp = hp
        self.speed = speed
        self.weapon = weapon  # 장착한 무기
        self.image = None
    
    def get_available_skills(self):
        """현재 장착한 무기에서 사용 가능한 스킬 반환"""
        from scripts.skills import ALL_SKILLS
        
        if self.weapon:
            skills = self.weapon.get_skills()
            # 모든 스킬의 내구도가 부족하면 무기 해제
            usable = [s for s in skills if self.weapon.durability >= s.durability_cost]
            if not usable:
                print(f"{self.name}의 {self.weapon.name}이(가) 부서졌습니다!")
                self.weapon = None
                return [ALL_SKILLS["struggle"]]  # 맨손 스킬
            return skills
        else:
            # 무기가 없으면 맨손 스킬
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

    if not battle_player:
        print("Error: battle_player not initialized.")
        return

    # 플레이어 무기 확인 및 기본 무기 장착
    if not battle_player.weapon:
        battle_player.equip_weapon(create_weapon("wooden_stick"))
    
    battle_player.speed = 12

    # 적은 매번 새로 생성 (슬라임 전용 무기 장착)
    enemy_weapon = create_weapon("slime")
    battle_enemy = Entity(
        "슬라임",
        hp=30,
        speed=8,
        max_hp=30,
        weapon=enemy_weapon
    )
    battle_enemy.image = pygame.transform.scale(
        pygame.image.load("resources/png/enemy/slime.png").convert_alpha(),
        (160, 160)
    )

    selected_skill_index = None
    battle_message = f"{battle_enemy.name}(이)가 나타났다!"
    game_state_ref["state"] = "battle"

    battle_state.update({
        "turn_phase": "menu",
        "action_queue": [],
        "action_index": 0,
        "stage": "announce",
        "current_text": "",
        "waiting_for_click": False,
    })


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
    weapon_box_size = 120  # 정사각형
    weapon_box_x = 20
    weapon_box_y = HEIGHT - weapon_box_size - 20
    
    # 박스 배경
    pygame.draw.rect(screen, (40, 40, 60), (weapon_box_x, weapon_box_y, weapon_box_size, weapon_box_size))
    pygame.draw.rect(screen, (100, 100, 150), (weapon_box_x, weapon_box_y, weapon_box_size, weapon_box_size), 2)
    
    # 무기 이미지 영역 (중앙 상단)
    weapon_img_size = 70
    weapon_img_x = weapon_box_x + (weapon_box_size - weapon_img_size) // 2
    weapon_img_y = weapon_box_y + 10
    pygame.draw.rect(screen, (60, 60, 80), (weapon_img_x, weapon_img_y, weapon_img_size, weapon_img_size))
    pygame.draw.rect(screen, (120, 120, 140), (weapon_img_x, weapon_img_y, weapon_img_size, weapon_img_size), 1)
    
    # 내구도 텍스트 (이미지 아래 중앙)
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

    # ---------- 전투 종료 체크 (먼저 처리) ----------
    if battle_player and battle_player.hp <= 0 and battle_state["turn_phase"] != "end":
        battle_state["current_text"] = "플레이어 패배..."
        battle_state["turn_phase"] = "end"
        battle_state["waiting_for_click"] = False
        battle_state["action_queue"].clear()
    elif battle_enemy and battle_enemy.hp <= 0 and battle_state["turn_phase"] != "end":
        battle_state["current_text"] = f"{battle_enemy.name}을(를) 격파했다!"
        battle_state["turn_phase"] = "end"
        battle_state["waiting_for_click"] = False
        battle_state["action_queue"].clear()

    # ---------- 전투 종료 상태 처리 ----------
    if battle_state["turn_phase"] == "end":
        # 종료 메시지 표시
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        pygame.draw.rect(screen, (255, 255, 255), text_box, 2)
        text_surface = font.render(battle_state["current_text"], True, (255, 255, 255))
        screen.blit(text_surface, (text_box.x + 20, text_box.y + 30))

        # 버튼 렌더링
        btn_w, btn_h = 180, 50
        gap = 40
        player_defeated = battle_player and battle_player.hp <= 0

        if not player_defeated:
            # 승리: 두 버튼 모두 표시
            next_rect = pygame.Rect(WIDTH//2 - btn_w - gap//2, HEIGHT//2, btn_w, btn_h)
            town_rect = pygame.Rect(WIDTH//2 + gap//2, HEIGHT//2, btn_w, btn_h)
            
            pygame.draw.rect(screen, (80, 150, 80), next_rect)
            pygame.draw.rect(screen, (150, 80, 80), town_rect)

            next_txt = font.render("다음 전투", True, (255, 255, 255))
            town_txt = font.render("마을로 돌아가기", True, (255, 255, 255))
            screen.blit(next_txt, next_txt.get_rect(center=next_rect.center))
            screen.blit(town_txt, town_txt.get_rect(center=town_rect.center))

            # 버튼 클릭 처리
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if next_rect.collidepoint(mouse_pos):
                        start_battle(game_state_ref, battle_player.name)
                        return
                    elif town_rect.collidepoint(mouse_pos):
                        game_state_ref["state"] = "town"
                        return
        else:
            # 패배: 마을로 돌아가기 버튼만
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
        
        return  # 전투 종료 상태에서는 여기서 함수 종료

    # ---------- 버튼 위치 계산 ----------
    button_w = 240
    button_h = 60
    gap = 15
    
    # 버튼을 중앙으로 배치
    start_x = (WIDTH - (button_w * 2 + gap)) // 2
    start_y = HEIGHT - 180

    # 스킬 버튼 위치 (2x2)
    skill_button_rects = []
    available_skills = battle_player.get_available_skills() if battle_player else []
    
    for i in range(4):
        bx = start_x + (i % 2) * (button_w + gap)
        by = start_y + (i // 2) * (button_h + gap)
        skill_button_rects.append(pygame.Rect(bx, by, button_w, button_h))

    # 메인 메뉴 버튼 위치 (2x2)
    menu_button_rects = []
    for i in range(4):
        bx = start_x + (i % 2) * (button_w + gap)
        by = start_y + (i // 2) * (button_h + gap)
        menu_button_rects.append(pygame.Rect(bx, by, button_w, button_h))

    # ---------- 버튼 그리기 ----------
    if battle_state["turn_phase"] == "skill_select":
        # 스킬 선택 화면
        for i, rect in enumerate(skill_button_rects):
            if battle_player and i < len(available_skills):
                skill = available_skills[i]
                label = skill.name
                
                # 내구도 부족 체크
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
    
    elif battle_state["turn_phase"] == "menu":
        # 메인 메뉴 화면
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
            
            # 1) 텍스트 진행 중이면 텍스트 넘김
            if battle_state["turn_phase"] == "text" and battle_state["waiting_for_click"]:
                if battle_state["stage"] == "announce":
                    # announce -> calculate
                    actor_tag, skill_obj = battle_state["action_queue"][battle_state["action_index"]]
                    if actor_tag == "player":
                        attacker, defender = battle_player, battle_enemy
                    else:
                        attacker, defender = battle_enemy, battle_player

                    # ✅ 실제 내구도 소모는 여기서!
                    if attacker.weapon and skill_obj.durability_cost > 0:
                        attacker.weapon.use_skill(skill_obj)

                    dmg = calc_damage(attacker, skill_obj, defender)
                    defender.hp = max(0, defender.hp - dmg)
                    battle_state["current_text"] = f"{defender.name}이(가) {dmg} 데미지를 입었다!"
                    battle_state["stage"] = "calculate"
                    
                elif battle_state["stage"] == "calculate":
                    # 다음 action으로 이동
                    battle_state["action_index"] += 1
                    if battle_state["action_index"] < len(battle_state["action_queue"]):
                        actor_tag, skill_obj = battle_state["action_queue"][battle_state["action_index"]]
                        who = battle_player.name if actor_tag == "player" else battle_enemy.name
                        battle_state["current_text"] = f"{who}이(가) {skill_obj.name}을(를) 사용했다!"
                        battle_state["stage"] = "announce"
                    else:
                        # 모든 행동 완료 → 턴 종료
                        battle_state["turn_phase"] = "menu"
                        battle_state["waiting_for_click"] = False
                        battle_state["current_text"] = ""
                        battle_state["action_queue"].clear()
                        battle_state["action_index"] = 0
                        battle_state["stage"] = "announce"
            
            # 2) 메인 메뉴 상태
            elif battle_state["turn_phase"] == "menu":
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
                elif clicked_button == 2:  # 교체 버튼
                    battle_state["current_text"] = "아직 구현되지 않은 기능입니다."
                elif clicked_button == 3:  # 도망 버튼
                    battle_state["current_text"] = "아직 구현되지 않은 기능입니다."
            
            # 3) 스킬 선택 상태
            elif battle_state["turn_phase"] == "skill_select":
                clicked_button = None
                for i, rect in enumerate(skill_button_rects):
                    if rect.collidepoint(mouse_pos):
                        clicked_button = i
                        break
                
                if clicked_button is not None and battle_player and clicked_button < len(available_skills):
                    selected_skill = available_skills[clicked_button]
                    
                    # 내구도 체크만 (소모는 나중에)
                    if battle_player.weapon and selected_skill.durability_cost > 0:
                        can_use = battle_player.weapon.durability >= selected_skill.durability_cost
                    else:
                        can_use = True
                    
                    if not can_use:
                        # 내구도 부족 메시지만 표시
                        battle_state["current_text"] = "무기의 내구도가 부족합니다!"
                    else:
                        # 몬스터 스킬 선택
                        enemy_skills = battle_enemy.get_available_skills() if battle_enemy else []
                        if enemy_skills:
                            enemy_skill = random.choice(enemy_skills)

                            # 턴 결정
                            order = decide_order(battle_player, selected_skill, battle_enemy, enemy_skill)
                            battle_state["action_queue"] = order.copy()
                            battle_state["action_index"] = 0
                            battle_state["stage"] = "announce"
                            
                            actor_tag, skill_obj = battle_state["action_queue"][0]
                            who = battle_player.name if actor_tag == "player" else battle_enemy.name
                            battle_state["current_text"] = f"{who}이(가) {skill_obj.name}을(를) 사용했다!"
                            battle_state["turn_phase"] = "text"
                            battle_state["waiting_for_click"] = True

    # ---------- 전투 텍스트 박스 렌더 ----------
    if battle_state["current_text"] and battle_state["turn_phase"] != "end":
        text_box = pygame.Rect(50, HEIGHT - 180, WIDTH - 100, 100)
        pygame.draw.rect(screen, (20, 20, 20), text_box)
        pygame.draw.rect(screen, (255, 255, 255), text_box, 2)

        text_surface = font.render(battle_state["current_text"], True, (255, 255, 255))
        screen.blit(text_surface, (text_box.x + 20, text_box.y + 30))