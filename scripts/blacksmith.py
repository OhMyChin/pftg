import pygame
import random

# 대장간 상태
blacksmith_state = {
    "stage": "inside",  # "inside", "compose", "decompose", "upgrade"
    "selected_button": 0,  # 내부 버튼 선택 (0: 합성, 1: 분해, 2: 강화, 3: 대화, 4: 나가기)
    "is_talking": False,
    "dialog_index": 0,
    
    # 합성 관련
    "compose_slot1": None,  # 첫 번째 무기
    "compose_slot2": None,  # 두 번째 무기
    "compose_selected": 0,  # 선택된 슬롯 (0, 1)
    "compose_inventory_open": False,  # 인벤토리 선택 화면
    "compose_inventory_index": 0,
    
    # 분해 관련
    "decompose_slot": None,  # 분해할 무기
    "decompose_inventory_open": False,
    "decompose_inventory_index": 0,
    
    # 강화 관련
    "upgrade_slot": None,  # 강화할 무기
    "upgrade_inventory_open": False,
    "upgrade_inventory_index": 0,
    
    # 결과 표시
    "result_message": "",
    "result_timer": 0,
    "result_items": [],  # 분해 결과물 표시용
}

# 강화 재료 데이터
UPGRADE_MATERIALS = {
    "normal_material": {"name": "일반 강화석", "grade": "일반"},
    "rare_material": {"name": "희귀 강화석", "grade": "희귀"},
    "hero_material": {"name": "영웅 강화석", "grade": "영웅"},
    "legend_material": {"name": "전설 강화석", "grade": "전설"},
}

# 플레이어 재료 보유량 (inventory처럼 전역으로 관리)
player_materials = {
    "normal_material": 0,
    "rare_material": 0,
    "hero_material": 0,
    "legend_material": 0,
}

# 등급 순서 (합성용)
GRADE_ORDER = ["일반", "희귀", "영웅", "전설"]

# 등급별 색상
GRADE_COLORS = {
    "일반": (200, 200, 200),
    "희귀": (100, 150, 255),
    "영웅": (200, 100, 255),
    "전설": (255, 200, 50),
}


def get_next_grade(current_grade):
    """다음 등급 반환"""
    if current_grade in GRADE_ORDER:
        idx = GRADE_ORDER.index(current_grade)
        if idx < len(GRADE_ORDER) - 1:
            return GRADE_ORDER[idx + 1]
    return None


def can_compose(weapon):
    """합성 가능 여부 확인"""
    if weapon is None:
        return False
    # 전설, 보스 무기는 합성 불가
    if weapon.grade in ["전설", "몬스터"]:
        return False
    # 보스 드롭 무기 체크 (특수 무기들)
    if hasattr(weapon, 'is_boss_drop') and weapon.is_boss_drop:
        return False
    return True


def can_decompose(weapon):
    """분해 가능 여부 확인"""
    if weapon is None:
        return False
    # 몬스터 무기는 분해 불가
    if weapon.grade == "몬스터":
        return False
    return True


def can_upgrade(weapon):
    """강화 가능 여부 확인"""
    if weapon is None:
        return False
    if weapon.grade == "몬스터":
        return False
    # 최대 강화 체크
    upgrade_level = getattr(weapon, 'upgrade_level', 0)
    if upgrade_level >= 5:
        return False
    return True


def do_compose(weapon1, weapon2):
    """
    합성 실행
    반환: (성공여부, 결과무기, 메시지)
    """
    if weapon1.grade != weapon2.grade:
        return False, None, "같은 등급의 무기만 합성할 수 있습니다!"
    
    current_grade = weapon1.grade
    next_grade = get_next_grade(current_grade)
    
    if next_grade is None:
        return False, None, "더 이상 합성할 수 없는 등급입니다!"
    
    # 성공 확률 계산
    if current_grade == "영웅":
        success_rate = 0.10  # 영웅 → 전설: 10%
    else:
        success_rate = 0.30  # 일반/희귀: 30%
    
    # 합성 시도
    if random.random() < success_rate:
        # 성공: 상위 등급 랜덤 무기 생성
        result_weapon = create_random_weapon_by_grade(next_grade)
        if result_weapon:
            return True, result_weapon, f"합성 성공! {next_grade} 등급 무기 획득!"
        else:
            # 상위 등급 무기가 없으면 실패 처리
            return_weapon = random.choice([weapon1, weapon2])
            return False, return_weapon, "합성 실패... 무기 하나가 반환되었습니다."
    else:
        # 실패: 둘 중 하나 반환
        return_weapon = random.choice([weapon1, weapon2])
        return False, return_weapon, "합성 실패... 무기 하나가 반환되었습니다."


def create_random_weapon_by_grade(grade):
    """특정 등급의 랜덤 무기 생성"""
    from scripts.weapons import ALL_WEAPONS, create_weapon
    
    # 해당 등급의 무기 필터링 (몬스터 제외)
    available_weapons = []
    for weapon_id, weapon in ALL_WEAPONS.items():
        if weapon.grade == grade and weapon.grade != "몬스터":
            available_weapons.append(weapon_id)
    
    if available_weapons:
        selected_id = random.choice(available_weapons)
        return create_weapon(selected_id)
    return None


def do_decompose(weapon):
    """
    분해 실행
    반환: (골드, 재료딕셔너리, 메시지)
    """
    grade = weapon.grade
    gold = 0
    materials = {}
    
    if grade == "일반":
        gold = random.randint(10, 30)
        materials["normal_material"] = random.randint(2, 3)
        
    elif grade == "희귀":
        gold = random.randint(30, 60)
        # 일반 4~5개 또는 희귀 2~3개 (랜덤)
        if random.random() < 0.5:
            materials["normal_material"] = random.randint(4, 5)
        else:
            materials["rare_material"] = random.randint(2, 3)
            
    elif grade == "영웅":
        gold = random.randint(60, 120)
        # 희귀 4~5개 또는 영웅 2~3개 (랜덤)
        if random.random() < 0.5:
            materials["rare_material"] = random.randint(4, 5)
        else:
            materials["hero_material"] = random.randint(2, 3)
            
    elif grade == "전설":
        gold = random.randint(150, 300)
        # 영웅 4~5개 + 전설 2~3개 (둘 다)
        materials["hero_material"] = random.randint(4, 5)
        materials["legend_material"] = random.randint(2, 3)
    
    return gold, materials, f"{weapon.name} 분해 완료!"


def get_upgrade_cost(weapon):
    """강화에 필요한 재료 반환"""
    grade = weapon.grade
    upgrade_level = getattr(weapon, 'upgrade_level', 0)
    
    # 강화 단계별 재료 증가
    base_cost = 3 + upgrade_level  # 3, 4, 5, 6, 7개
    
    if grade == "일반":
        return {"normal_material": base_cost}
    elif grade == "희귀":
        return {"rare_material": base_cost}
    elif grade == "영웅":
        return {"hero_material": base_cost}
    elif grade == "전설":
        return {"legend_material": base_cost}
    
    return {}


def can_afford_upgrade(weapon):
    """강화 재료가 충분한지 확인"""
    cost = get_upgrade_cost(weapon)
    for mat_id, amount in cost.items():
        if player_materials.get(mat_id, 0) < amount:
            return False
    return True


def do_upgrade(weapon):
    """
    강화 실행
    반환: (성공여부, 메시지)
    """
    from scripts.skills import ALL_SKILLS
    
    if not can_afford_upgrade(weapon):
        return False, "강화 재료가 부족합니다!"
    
    # 재료 소모
    cost = get_upgrade_cost(weapon)
    for mat_id, amount in cost.items():
        player_materials[mat_id] -= amount
    
    # 강화 레벨 증가
    if not hasattr(weapon, 'upgrade_level'):
        weapon.upgrade_level = 0
    weapon.upgrade_level += 1
    
    # 내구도 최대치 증가
    durability_increase = random.randint(5, 15)
    weapon.max_durability += durability_increase
    weapon.durability = weapon.max_durability  # 풀 수리
    
    # 스킬 공격력 증가 (랜덤 스킬 하나)
    skill_power_increase = 0
    upgraded_skill_name = ""
    
    if weapon.skill_ids:
        # 강화할 스킬 랜덤 선택
        skill_id = random.choice(weapon.skill_ids)
        
        # 강화량 결정 (1=60%, 2=30%, 3=10%)
        roll = random.random()
        if roll < 0.60:
            skill_power_increase = 1
        elif roll < 0.90:
            skill_power_increase = 2
        else:
            skill_power_increase = 3
        
        # 스킬 강화 정보 저장 (무기별 스킬 강화 추적)
        if not hasattr(weapon, 'skill_upgrades'):
            weapon.skill_upgrades = {}
        
        if skill_id not in weapon.skill_upgrades:
            weapon.skill_upgrades[skill_id] = 0
        weapon.skill_upgrades[skill_id] += skill_power_increase
        
        if skill_id in ALL_SKILLS:
            upgraded_skill_name = ALL_SKILLS[skill_id].name
    
    # 5강 달성 시 초월 메시지
    if weapon.upgrade_level >= 5:
        if not hasattr(weapon, 'is_transcended'):
            weapon.is_transcended = True
            # 초월 스킬 추가
            if hasattr(weapon, 'transcend_skill') and weapon.transcend_skill:
                if weapon.transcend_skill not in weapon.skill_ids:
                    weapon.skill_ids.append(weapon.transcend_skill)
                return True, f"+{weapon.upgrade_level} 강화 성공! 초월 달성! 새로운 스킬 해금!"
        return True, f"+{weapon.upgrade_level} 강화 성공! (최대 강화)"
    
    msg = f"+{weapon.upgrade_level} 강화 성공! 내구도 +{durability_increase}"
    if upgraded_skill_name:
        msg += f", {upgraded_skill_name} 위력 +{skill_power_increase}"
    
    return True, msg


def get_weapon_display_name(weapon):
    """강화 레벨이 포함된 무기 이름 반환"""
    if weapon is None:
        return ""
    
    name = weapon.name
    upgrade_level = getattr(weapon, 'upgrade_level', 0)
    
    if upgrade_level > 0:
        name = f"+{upgrade_level} {name}"
    
    if getattr(weapon, 'is_transcended', False):
        name = f"[초월] {name}"
    
    return name


def draw_blacksmith(screen, font_main, font_small, WIDTH, HEIGHT, game_state, dt=0, font_path=None):
    """대장간 화면 그리기"""
    global blacksmith_state
    
    # 타이머 업데이트
    if blacksmith_state["result_message"] and dt > 0:
        blacksmith_state["result_timer"] += dt
        if blacksmith_state["result_timer"] > 3:
            blacksmith_state["result_message"] = ""
            blacksmith_state["result_timer"] = 0
            blacksmith_state["result_items"] = []
    
    if blacksmith_state["stage"] == "inside":
        draw_blacksmith_inside(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)
    elif blacksmith_state["stage"] == "compose":
        draw_compose_ui(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)
    elif blacksmith_state["stage"] == "decompose":
        draw_decompose_ui(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)
    elif blacksmith_state["stage"] == "upgrade":
        draw_upgrade_ui(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)


def draw_blacksmith_inside(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path=None):
    """대장간 내부 화면"""
    
    # 배경
    try:
        bg = pygame.image.load("resources/png/building/blacksmith_inside.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
        screen.blit(bg, (0, 0))
    except:
        screen.fill((60, 40, 30))
    
    # 대화 박스
    dialog_height = 200
    dialog_y = HEIGHT - dialog_height - 20
    dialog_rect = pygame.Rect(20, dialog_y, WIDTH - 40, dialog_height)
    
    dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
    dialog_surface.set_alpha(220)
    dialog_surface.fill((40, 30, 20))
    screen.blit(dialog_surface, dialog_rect)
    pygame.draw.rect(screen, (200, 150, 100), dialog_rect, 4)
    
    if blacksmith_state["is_talking"]:
        # 대화 내용
        npc_dialogs = [
            "대장장이: 좋은 무기를 만들려면 좋은 재료가 필요하지.",
            "대장장이: 합성은 같은 등급 무기 두 개가 필요해.",
            "대장장이: 강화는 재료를 모아서 하면 돼. 5강이 최대야.",
            "대장장이: 5강까지 올리면 초월이 열려서 새 기술이 생기지!",
        ]
        
        current_index = blacksmith_state["dialog_index"]
        if current_index < len(npc_dialogs):
            text = font_small.render(npc_dialogs[current_index], True, (255, 255, 255))
            screen.blit(text, (40, dialog_y + 30))
            
            arrow_text = pygame.font.SysFont("consolas", 30).render("▼", True, (255, 255, 255))
            screen.blit(arrow_text, (dialog_rect.right - 40, dialog_rect.bottom - 40))
    else:
        # NPC 대사
        npc_text = [
            "대장장이: 어서 와! 뭘 해줄까?",
            "합성, 분해, 강화를 할 수 있어.",
        ]
        
        text_y = dialog_y + 25
        for line in npc_text:
            text = font_small.render(line, True, (255, 255, 255))
            screen.blit(text, (40, text_y))
            text_y += 35
        
        # 버튼들
        button_width = 140
        button_height = 40
        button_gap = 8
        button_x = dialog_rect.right - button_width - 20
        
        buttons = ["합성", "분해", "강화", "대화", "나가기"]
        total_height = len(buttons) * button_height + (len(buttons) - 1) * button_gap
        button_start_y = dialog_y + (dialog_height - total_height) // 2
        
        for i, btn_text in enumerate(buttons):
            button_y = button_start_y + i * (button_height + button_gap)
            btn_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if i == blacksmith_state["selected_button"]:
                pygame.draw.rect(screen, (200, 150, 100), btn_rect)
                pygame.draw.rect(screen, (255, 200, 150), btn_rect, 3)
            else:
                pygame.draw.rect(screen, (80, 60, 50), btn_rect)
                pygame.draw.rect(screen, (150, 120, 100), btn_rect, 2)
            
            text = font_small.render(btn_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=btn_rect.center)
            screen.blit(text, text_rect)
    
    # 재료 보유량 표시 (우측 상단)
    draw_materials_info(screen, font_small, WIDTH, font_path)
    
    # 결과 메시지 표시
    if blacksmith_state["result_message"]:
        draw_result_message(screen, font_small, WIDTH, HEIGHT, font_path)


def draw_materials_info(screen, font_small, WIDTH, font_path=None):
    """재료 보유량 표시"""
    info_x = WIDTH - 200
    info_y = 20
    
    # 배경
    info_rect = pygame.Rect(info_x - 10, info_y - 5, 190, 120)
    pygame.draw.rect(screen, (40, 30, 20), info_rect)
    pygame.draw.rect(screen, (150, 120, 100), info_rect, 2)
    
    # 타이틀
    title = font_small.render("[ 강화 재료 ]", True, (255, 200, 150))
    screen.blit(title, (info_x, info_y))
    
    y = info_y + 25
    materials_order = ["normal_material", "rare_material", "hero_material", "legend_material"]
    
    for mat_id in materials_order:
        mat_data = UPGRADE_MATERIALS[mat_id]
        color = GRADE_COLORS.get(mat_data["grade"], (200, 200, 200))
        
        text = font_small.render(f"{mat_data['name']}: {player_materials[mat_id]}", True, color)
        screen.blit(text, (info_x, y))
        y += 22


def draw_compose_ui(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path=None):
    """합성 UI"""
    from scripts.inventory import player_inventory
    
    screen.fill((40, 30, 25))
    
    # 타이틀
    title = font_main.render("[ 무기 합성 ]", True, (255, 200, 150))
    title_rect = title.get_rect(center=(WIDTH // 2, 40))
    screen.blit(title, title_rect)
    
    # 설명
    desc = font_small.render("같은 등급 무기 2개 → 상위 등급 (30%, 영웅→전설은 10%)", True, (200, 200, 200))
    desc_rect = desc.get_rect(center=(WIDTH // 2, 80))
    screen.blit(desc, desc_rect)
    
    # 합성 UI 이미지 로드
    try:
        compose_img = pygame.image.load("resources/png/building/blacksmith_compose.png").convert_alpha()
        img_rect = compose_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(compose_img, img_rect)
    except:
        # 이미지 없으면 기본 그리기
        img_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
    
    # 슬롯 위치 계산 (이미지 기준)
    slot_size = 80
    slot1_rect = pygame.Rect(img_rect.x + 20, img_rect.y + 20, slot_size, slot_size)
    slot2_rect = pygame.Rect(img_rect.x + 120, img_rect.y + 20, slot_size, slot_size)
    result_rect = pygame.Rect(img_rect.x + 300, img_rect.y + 20, slot_size, slot_size)
    
    # 슬롯 선택 표시
    if not blacksmith_state["compose_inventory_open"]:
        if blacksmith_state["compose_selected"] == 0:
            pygame.draw.rect(screen, (255, 255, 100), slot1_rect, 4)
        else:
            pygame.draw.rect(screen, (255, 255, 100), slot2_rect, 4)
    
    # 슬롯에 무기 표시
    draw_weapon_in_slot(screen, blacksmith_state["compose_slot1"], slot1_rect, font_small)
    draw_weapon_in_slot(screen, blacksmith_state["compose_slot2"], slot2_rect, font_small)
    
    # 조작법
    help_y = HEIGHT - 120
    help_texts = [
        "A/D: 슬롯 선택  |  Enter: 무기 넣기/빼기  |  Space: 합성 실행  |  ESC: 돌아가기"
    ]
    for text in help_texts:
        help_surface = font_small.render(text, True, (180, 180, 180))
        help_rect = help_surface.get_rect(center=(WIDTH // 2, help_y))
        screen.blit(help_surface, help_rect)
        help_y += 25
    
    # 인벤토리 선택 화면
    if blacksmith_state["compose_inventory_open"]:
        draw_weapon_select_popup(screen, font_small, WIDTH, HEIGHT, 
                                 player_inventory["weapons"],
                                 blacksmith_state["compose_inventory_index"],
                                 "합성할 무기 선택", font_path,
                                 filter_func=can_compose)
    
    # 재료 정보
    draw_materials_info(screen, font_small, WIDTH, font_path)
    
    # 결과 메시지
    if blacksmith_state["result_message"]:
        draw_result_message(screen, font_small, WIDTH, HEIGHT, font_path)


def draw_decompose_ui(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path=None):
    """분해 UI"""
    from scripts.inventory import player_inventory
    
    screen.fill((40, 30, 25))
    
    # 타이틀
    title = font_main.render("[ 무기 분해 ]", True, (255, 200, 150))
    title_rect = title.get_rect(center=(WIDTH // 2, 40))
    screen.blit(title, title_rect)
    
    # 설명
    desc = font_small.render("무기를 분해하여 골드와 강화 재료를 얻습니다", True, (200, 200, 200))
    desc_rect = desc.get_rect(center=(WIDTH // 2, 80))
    screen.blit(desc, desc_rect)
    
    # 분해 UI 이미지
    try:
        decompose_img = pygame.image.load("resources/png/building/blacksmith_decompose.png").convert_alpha()
        img_rect = decompose_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(decompose_img, img_rect)
    except:
        img_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 200)
    
    # 슬롯
    slot_size = 80
    slot_rect = pygame.Rect(img_rect.x + 20, img_rect.y + 20, slot_size, slot_size)
    
    if not blacksmith_state["decompose_inventory_open"]:
        pygame.draw.rect(screen, (255, 255, 100), slot_rect, 4)
    
    draw_weapon_in_slot(screen, blacksmith_state["decompose_slot"], slot_rect, font_small)
    
    # 예상 보상 표시
    if blacksmith_state["decompose_slot"]:
        reward_y = img_rect.bottom + 20
        weapon = blacksmith_state["decompose_slot"]
        
        reward_text = font_small.render(f"예상 보상 ({weapon.grade} 등급):", True, (255, 200, 100))
        screen.blit(reward_text, (WIDTH // 2 - 150, reward_y))
        
        reward_y += 25
        if weapon.grade == "일반":
            text = "골드 10~30, 일반 강화석 2~3개"
        elif weapon.grade == "희귀":
            text = "골드 30~60, 일반 강화석 4~5개 또는 희귀 강화석 2~3개"
        elif weapon.grade == "영웅":
            text = "골드 60~120, 희귀 강화석 4~5개 또는 영웅 강화석 2~3개"
        elif weapon.grade == "전설":
            text = "골드 150~300, 영웅 강화석 4~5개 + 전설 강화석 2~3개"
        else:
            text = "분해 불가"
        
        reward_detail = font_small.render(text, True, (200, 200, 200))
        screen.blit(reward_detail, (WIDTH // 2 - 200, reward_y))
    
    # 조작법
    help_y = HEIGHT - 100
    help_text = "Enter: 무기 넣기/빼기  |  Space: 분해 실행  |  ESC: 돌아가기"
    help_surface = font_small.render(help_text, True, (180, 180, 180))
    help_rect = help_surface.get_rect(center=(WIDTH // 2, help_y))
    screen.blit(help_surface, help_rect)
    
    # 인벤토리
    if blacksmith_state["decompose_inventory_open"]:
        draw_weapon_select_popup(screen, font_small, WIDTH, HEIGHT,
                                 player_inventory["weapons"],
                                 blacksmith_state["decompose_inventory_index"],
                                 "분해할 무기 선택", font_path,
                                 filter_func=can_decompose)
    
    draw_materials_info(screen, font_small, WIDTH, font_path)
    
    if blacksmith_state["result_message"]:
        draw_result_message(screen, font_small, WIDTH, HEIGHT, font_path)


def draw_upgrade_ui(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path=None):
    """강화 UI"""
    from scripts.inventory import player_inventory
    
    screen.fill((40, 30, 25))
    
    # 타이틀
    title = font_main.render("[ 무기 강화 ]", True, (255, 200, 150))
    title_rect = title.get_rect(center=(WIDTH // 2, 40))
    screen.blit(title, title_rect)
    
    # 설명
    desc = font_small.render("강화 재료로 무기를 강화합니다 (최대 5강, 5강 시 초월 해금)", True, (200, 200, 200))
    desc_rect = desc.get_rect(center=(WIDTH // 2, 80))
    screen.blit(desc, desc_rect)
    
    # 강화 UI 이미지
    try:
        upgrade_img = pygame.image.load("resources/png/building/blacksmith_upgrade.png").convert_alpha()
        img_rect = upgrade_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(upgrade_img, img_rect)
    except:
        img_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 100, 200, 200)
    
    # 슬롯
    slot_size = 80
    slot_rect = pygame.Rect(img_rect.centerx - slot_size // 2, img_rect.y + 20, slot_size, slot_size)
    
    if not blacksmith_state["upgrade_inventory_open"]:
        pygame.draw.rect(screen, (255, 255, 100), slot_rect, 4)
    
    draw_weapon_in_slot(screen, blacksmith_state["upgrade_slot"], slot_rect, font_small)
    
    # 강화 정보 표시
    if blacksmith_state["upgrade_slot"]:
        weapon = blacksmith_state["upgrade_slot"]
        info_y = img_rect.bottom + 20
        
        # 현재 강화 레벨
        upgrade_level = getattr(weapon, 'upgrade_level', 0)
        level_text = font_small.render(f"현재 강화: +{upgrade_level}/5", True, (255, 200, 100))
        screen.blit(level_text, (WIDTH // 2 - 100, info_y))
        
        if upgrade_level < 5:
            # 필요 재료
            info_y += 30
            cost = get_upgrade_cost(weapon)
            cost_text = "필요 재료: "
            for mat_id, amount in cost.items():
                mat_name = UPGRADE_MATERIALS[mat_id]["name"]
                have = player_materials.get(mat_id, 0)
                cost_text += f"{mat_name} {amount}개 (보유: {have})  "
            
            can_afford = can_afford_upgrade(weapon)
            cost_color = (100, 255, 100) if can_afford else (255, 100, 100)
            cost_surface = font_small.render(cost_text, True, cost_color)
            screen.blit(cost_surface, (WIDTH // 2 - 200, info_y))
        else:
            info_y += 30
            if getattr(weapon, 'is_transcended', False):
                trans_text = font_small.render("★ 초월 완료! ★", True, (255, 200, 50))
            else:
                trans_text = font_small.render("최대 강화 도달!", True, (255, 200, 50))
            screen.blit(trans_text, (WIDTH // 2 - 60, info_y))
    
    # 조작법
    help_y = HEIGHT - 100
    help_text = "Enter: 무기 넣기/빼기  |  Space: 강화 실행  |  ESC: 돌아가기"
    help_surface = font_small.render(help_text, True, (180, 180, 180))
    help_rect = help_surface.get_rect(center=(WIDTH // 2, help_y))
    screen.blit(help_surface, help_rect)
    
    # 인벤토리
    if blacksmith_state["upgrade_inventory_open"]:
        draw_weapon_select_popup(screen, font_small, WIDTH, HEIGHT,
                                 player_inventory["weapons"],
                                 blacksmith_state["upgrade_inventory_index"],
                                 "강화할 무기 선택", font_path,
                                 filter_func=can_upgrade)
    
    draw_materials_info(screen, font_small, WIDTH, font_path)
    
    if blacksmith_state["result_message"]:
        draw_result_message(screen, font_small, WIDTH, HEIGHT, font_path)


def draw_weapon_in_slot(screen, weapon, slot_rect, font_small):
    """슬롯에 무기 그리기"""
    if weapon is None:
        return
    
    # 무기 이미지
    if weapon.image_path:
        try:
            img = pygame.image.load(weapon.image_path).convert_alpha()
            img = pygame.transform.scale(img, (slot_rect.width - 10, slot_rect.height - 10))
            img_rect = img.get_rect(center=slot_rect.center)
            screen.blit(img, img_rect)
        except:
            # 이미지 없으면 이름만
            pass
    
    # 등급 색상 테두리
    grade_color = GRADE_COLORS.get(weapon.grade, (200, 200, 200))
    pygame.draw.rect(screen, grade_color, slot_rect, 2)
    
    # 강화 레벨 표시
    upgrade_level = getattr(weapon, 'upgrade_level', 0)
    if upgrade_level > 0:
        level_text = font_small.render(f"+{upgrade_level}", True, (255, 255, 100))
        screen.blit(level_text, (slot_rect.x + 5, slot_rect.y + 5))


def draw_weapon_select_popup(screen, font_small, WIDTH, HEIGHT, weapons, selected_index, title, font_path=None, filter_func=None):
    """무기 선택 팝업"""
    # 필터링
    if filter_func:
        filtered_weapons = [(i, w) for i, w in enumerate(weapons) if filter_func(w)]
    else:
        filtered_weapons = [(i, w) for i, w in enumerate(weapons)]
    
    # 팝업 배경
    popup_width = 500
    popup_height = 400
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2
    
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, (50, 40, 35), popup_rect)
    pygame.draw.rect(screen, (200, 150, 100), popup_rect, 3)
    
    # 타이틀
    title_surface = font_small.render(title, True, (255, 200, 150))
    title_rect = title_surface.get_rect(center=(WIDTH // 2, popup_y + 25))
    screen.blit(title_surface, title_rect)
    
    # 무기 목록
    if not filtered_weapons:
        no_weapon_text = font_small.render("사용 가능한 무기가 없습니다", True, (180, 180, 180))
        no_weapon_rect = no_weapon_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(no_weapon_text, no_weapon_rect)
    else:
        list_y = popup_y + 60
        visible_count = 8
        start_idx = max(0, selected_index - visible_count // 2)
        
        for display_idx, (original_idx, weapon) in enumerate(filtered_weapons[start_idx:start_idx + visible_count]):
            actual_idx = start_idx + display_idx
            
            item_rect = pygame.Rect(popup_x + 20, list_y, popup_width - 40, 35)
            
            if actual_idx == selected_index:
                pygame.draw.rect(screen, (100, 80, 60), item_rect)
                pygame.draw.rect(screen, (255, 200, 100), item_rect, 2)
            
            # 무기 정보
            grade_color = GRADE_COLORS.get(weapon.grade, (200, 200, 200))
            display_name = get_weapon_display_name(weapon)
            
            name_text = font_small.render(display_name, True, grade_color)
            screen.blit(name_text, (item_rect.x + 10, item_rect.y + 5))
            
            # 등급
            grade_text = font_small.render(f"[{weapon.grade}]", True, grade_color)
            screen.blit(grade_text, (item_rect.right - 80, item_rect.y + 5))
            
            list_y += 40
    
    # 조작법
    help_text = font_small.render("W/S: 선택  |  Enter: 확정  |  ESC: 취소", True, (150, 150, 150))
    help_rect = help_text.get_rect(center=(WIDTH // 2, popup_y + popup_height - 30))
    screen.blit(help_text, help_rect)


def draw_result_message(screen, font_small, WIDTH, HEIGHT, font_path=None):
    """결과 메시지 표시"""
    msg_width = 400
    msg_height = 100
    msg_x = (WIDTH - msg_width) // 2
    msg_y = (HEIGHT - msg_height) // 2
    
    # 배경
    msg_rect = pygame.Rect(msg_x, msg_y, msg_width, msg_height)
    pygame.draw.rect(screen, (60, 50, 40), msg_rect)
    pygame.draw.rect(screen, (255, 200, 100), msg_rect, 3)
    
    # 메시지
    msg_surface = font_small.render(blacksmith_state["result_message"], True, (255, 255, 255))
    msg_text_rect = msg_surface.get_rect(center=(WIDTH // 2, msg_y + 35))
    screen.blit(msg_surface, msg_text_rect)
    
    # 획득 아이템 표시
    if blacksmith_state["result_items"]:
        items_y = msg_y + 60
        items_text = "  ".join(blacksmith_state["result_items"])
        items_surface = font_small.render(items_text, True, (200, 200, 100))
        items_rect = items_surface.get_rect(center=(WIDTH // 2, items_y))
        screen.blit(items_surface, items_rect)


def handle_blacksmith_input(events, game_state):
    """대장간 입력 처리"""
    from scripts.inventory import player_inventory
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            
            # 내부 화면
            if blacksmith_state["stage"] == "inside":
                if blacksmith_state["is_talking"]:
                    if event.key == pygame.K_RETURN:
                        blacksmith_state["dialog_index"] += 1
                        if blacksmith_state["dialog_index"] >= 4:
                            blacksmith_state["is_talking"] = False
                            blacksmith_state["dialog_index"] = 0
                else:
                    if event.key == pygame.K_w:
                        blacksmith_state["selected_button"] = max(0, blacksmith_state["selected_button"] - 1)
                    elif event.key == pygame.K_s:
                        blacksmith_state["selected_button"] = min(4, blacksmith_state["selected_button"] + 1)
                    elif event.key == pygame.K_RETURN:
                        selected = blacksmith_state["selected_button"]
                        if selected == 0:  # 합성
                            blacksmith_state["stage"] = "compose"
                            reset_compose_state()
                        elif selected == 1:  # 분해
                            blacksmith_state["stage"] = "decompose"
                            reset_decompose_state()
                        elif selected == 2:  # 강화
                            blacksmith_state["stage"] = "upgrade"
                            reset_upgrade_state()
                        elif selected == 3:  # 대화
                            blacksmith_state["is_talking"] = True
                        elif selected == 4:  # 나가기
                            game_state["state"] = "town"
                            reset_all_state()
                    elif event.key == pygame.K_ESCAPE:
                        game_state["state"] = "town"
                        reset_all_state()
            
            # 합성 화면
            elif blacksmith_state["stage"] == "compose":
                handle_compose_input(event, player_inventory)
            
            # 분해 화면
            elif blacksmith_state["stage"] == "decompose":
                handle_decompose_input(event, player_inventory, game_state)
            
            # 강화 화면
            elif blacksmith_state["stage"] == "upgrade":
                handle_upgrade_input(event, player_inventory)


def handle_compose_input(event, player_inventory):
    """합성 입력 처리"""
    if blacksmith_state["compose_inventory_open"]:
        # 인벤토리에서 무기 선택
        filtered = [w for w in player_inventory["weapons"] if can_compose(w)]
        
        if event.key == pygame.K_w:
            if filtered:
                blacksmith_state["compose_inventory_index"] = max(0, blacksmith_state["compose_inventory_index"] - 1)
        elif event.key == pygame.K_s:
            if filtered:
                blacksmith_state["compose_inventory_index"] = min(len(filtered) - 1, blacksmith_state["compose_inventory_index"])
        elif event.key == pygame.K_RETURN:
            if filtered and blacksmith_state["compose_inventory_index"] < len(filtered):
                selected_weapon = filtered[blacksmith_state["compose_inventory_index"]]
                
                # 인벤토리에서 제거
                player_inventory["weapons"].remove(selected_weapon)
                
                # 슬롯에 배치
                if blacksmith_state["compose_selected"] == 0:
                    blacksmith_state["compose_slot1"] = selected_weapon
                else:
                    blacksmith_state["compose_slot2"] = selected_weapon
                
                blacksmith_state["compose_inventory_open"] = False
                blacksmith_state["compose_inventory_index"] = 0
        elif event.key == pygame.K_ESCAPE:
            blacksmith_state["compose_inventory_open"] = False
    else:
        # 슬롯 선택
        if event.key == pygame.K_a:
            blacksmith_state["compose_selected"] = 0
        elif event.key == pygame.K_d:
            blacksmith_state["compose_selected"] = 1
        elif event.key == pygame.K_RETURN:
            # 현재 슬롯 확인
            current_slot = blacksmith_state["compose_selected"]
            current_weapon = blacksmith_state["compose_slot1"] if current_slot == 0 else blacksmith_state["compose_slot2"]
            
            if current_weapon:
                # 무기 빼기 (인벤토리로 반환)
                player_inventory["weapons"].append(current_weapon)
                if current_slot == 0:
                    blacksmith_state["compose_slot1"] = None
                else:
                    blacksmith_state["compose_slot2"] = None
            else:
                # 무기 넣기 (인벤토리 열기)
                blacksmith_state["compose_inventory_open"] = True
                blacksmith_state["compose_inventory_index"] = 0
        
        elif event.key == pygame.K_SPACE:
            # 합성 실행
            weapon1 = blacksmith_state["compose_slot1"]
            weapon2 = blacksmith_state["compose_slot2"]
            
            if weapon1 and weapon2:
                success, result_weapon, message = do_compose(weapon1, weapon2)
                
                # 슬롯 비우기
                blacksmith_state["compose_slot1"] = None
                blacksmith_state["compose_slot2"] = None
                
                # 결과 무기 인벤토리에 추가
                if result_weapon:
                    player_inventory["weapons"].append(result_weapon)
                
                blacksmith_state["result_message"] = message
                blacksmith_state["result_timer"] = 0
            else:
                blacksmith_state["result_message"] = "무기 2개를 넣어주세요!"
                blacksmith_state["result_timer"] = 0
        
        elif event.key == pygame.K_ESCAPE:
            # 슬롯의 무기 반환
            if blacksmith_state["compose_slot1"]:
                player_inventory["weapons"].append(blacksmith_state["compose_slot1"])
            if blacksmith_state["compose_slot2"]:
                player_inventory["weapons"].append(blacksmith_state["compose_slot2"])
            
            blacksmith_state["stage"] = "inside"
            reset_compose_state()


def handle_decompose_input(event, player_inventory, game_state):
    """분해 입력 처리"""
    if blacksmith_state["decompose_inventory_open"]:
        filtered = [w for w in player_inventory["weapons"] if can_decompose(w)]
        
        if event.key == pygame.K_w:
            if filtered:
                blacksmith_state["decompose_inventory_index"] = max(0, blacksmith_state["decompose_inventory_index"] - 1)
        elif event.key == pygame.K_s:
            if filtered:
                blacksmith_state["decompose_inventory_index"] = min(len(filtered) - 1, blacksmith_state["decompose_inventory_index"])
        elif event.key == pygame.K_RETURN:
            if filtered and blacksmith_state["decompose_inventory_index"] < len(filtered):
                selected_weapon = filtered[blacksmith_state["decompose_inventory_index"]]
                player_inventory["weapons"].remove(selected_weapon)
                blacksmith_state["decompose_slot"] = selected_weapon
                blacksmith_state["decompose_inventory_open"] = False
                blacksmith_state["decompose_inventory_index"] = 0
        elif event.key == pygame.K_ESCAPE:
            blacksmith_state["decompose_inventory_open"] = False
    else:
        if event.key == pygame.K_RETURN:
            if blacksmith_state["decompose_slot"]:
                # 무기 빼기
                player_inventory["weapons"].append(blacksmith_state["decompose_slot"])
                blacksmith_state["decompose_slot"] = None
            else:
                # 무기 넣기
                blacksmith_state["decompose_inventory_open"] = True
                blacksmith_state["decompose_inventory_index"] = 0
        
        elif event.key == pygame.K_SPACE:
            # 분해 실행
            weapon = blacksmith_state["decompose_slot"]
            
            if weapon:
                gold, materials, message = do_decompose(weapon)
                
                # 골드 추가
                game_state["gold"] = game_state.get("gold", 0) + gold
                
                # 재료 추가
                result_items = [f"+{gold}G"]
                for mat_id, amount in materials.items():
                    player_materials[mat_id] += amount
                    mat_name = UPGRADE_MATERIALS[mat_id]["name"]
                    result_items.append(f"{mat_name} +{amount}")
                
                blacksmith_state["decompose_slot"] = None
                blacksmith_state["result_message"] = message
                blacksmith_state["result_items"] = result_items
                blacksmith_state["result_timer"] = 0
            else:
                blacksmith_state["result_message"] = "분해할 무기를 넣어주세요!"
                blacksmith_state["result_timer"] = 0
        
        elif event.key == pygame.K_ESCAPE:
            if blacksmith_state["decompose_slot"]:
                player_inventory["weapons"].append(blacksmith_state["decompose_slot"])
            blacksmith_state["stage"] = "inside"
            reset_decompose_state()


def handle_upgrade_input(event, player_inventory):
    """강화 입력 처리"""
    if blacksmith_state["upgrade_inventory_open"]:
        filtered = [w for w in player_inventory["weapons"] if can_upgrade(w)]
        
        if event.key == pygame.K_w:
            if filtered:
                blacksmith_state["upgrade_inventory_index"] = max(0, blacksmith_state["upgrade_inventory_index"] - 1)
        elif event.key == pygame.K_s:
            if filtered:
                blacksmith_state["upgrade_inventory_index"] = min(len(filtered) - 1, blacksmith_state["upgrade_inventory_index"])
        elif event.key == pygame.K_RETURN:
            if filtered and blacksmith_state["upgrade_inventory_index"] < len(filtered):
                selected_weapon = filtered[blacksmith_state["upgrade_inventory_index"]]
                player_inventory["weapons"].remove(selected_weapon)
                blacksmith_state["upgrade_slot"] = selected_weapon
                blacksmith_state["upgrade_inventory_open"] = False
                blacksmith_state["upgrade_inventory_index"] = 0
        elif event.key == pygame.K_ESCAPE:
            blacksmith_state["upgrade_inventory_open"] = False
    else:
        if event.key == pygame.K_RETURN:
            if blacksmith_state["upgrade_slot"]:
                player_inventory["weapons"].append(blacksmith_state["upgrade_slot"])
                blacksmith_state["upgrade_slot"] = None
            else:
                blacksmith_state["upgrade_inventory_open"] = True
                blacksmith_state["upgrade_inventory_index"] = 0
        
        elif event.key == pygame.K_SPACE:
            weapon = blacksmith_state["upgrade_slot"]
            
            if weapon:
                if getattr(weapon, 'upgrade_level', 0) >= 5:
                    blacksmith_state["result_message"] = "이미 최대 강화입니다!"
                    blacksmith_state["result_timer"] = 0
                else:
                    success, message = do_upgrade(weapon)
                    blacksmith_state["result_message"] = message
                    blacksmith_state["result_timer"] = 0
            else:
                blacksmith_state["result_message"] = "강화할 무기를 넣어주세요!"
                blacksmith_state["result_timer"] = 0
        
        elif event.key == pygame.K_ESCAPE:
            if blacksmith_state["upgrade_slot"]:
                player_inventory["weapons"].append(blacksmith_state["upgrade_slot"])
            blacksmith_state["stage"] = "inside"
            reset_upgrade_state()


def reset_compose_state():
    """합성 상태 초기화"""
    blacksmith_state["compose_slot1"] = None
    blacksmith_state["compose_slot2"] = None
    blacksmith_state["compose_selected"] = 0
    blacksmith_state["compose_inventory_open"] = False
    blacksmith_state["compose_inventory_index"] = 0


def reset_decompose_state():
    """분해 상태 초기화"""
    blacksmith_state["decompose_slot"] = None
    blacksmith_state["decompose_inventory_open"] = False
    blacksmith_state["decompose_inventory_index"] = 0


def reset_upgrade_state():
    """강화 상태 초기화"""
    blacksmith_state["upgrade_slot"] = None
    blacksmith_state["upgrade_inventory_open"] = False
    blacksmith_state["upgrade_inventory_index"] = 0


def reset_all_state():
    """전체 상태 초기화"""
    blacksmith_state["stage"] = "inside"
    blacksmith_state["selected_button"] = 0
    blacksmith_state["is_talking"] = False
    blacksmith_state["dialog_index"] = 0
    blacksmith_state["result_message"] = ""
    blacksmith_state["result_timer"] = 0
    blacksmith_state["result_items"] = []
    reset_compose_state()
    reset_decompose_state()
    reset_upgrade_state()