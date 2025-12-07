import pygame
import random

# 대장간 상태
blacksmith_state = {
    "stage": "inside",
    "selected_button": 0,
    "is_talking": False,
    "dialog_index": 0,
    "compose_slots": [None, None],
    "compose_selected": 0,
    "decompose_slot": None,
    "decompose_selected": 0,
    "upgrade_slot": None,
    "upgrade_selected": 0,
    "weapon_select_open": False,
    "weapon_select_index": 0,
    "weapon_select_target": None,
    "message": "",
    "message_timer": 0,
    "animating": False,
    "anim_type": None,
    "anim_frame": 0,
    "anim_timer": 0,
    "anim_result": None,
    "showing_result": False,
}

# 애니메이션 프레임
COMPOSE_FRAMES = [f"resources/png/building/blacksmith_frames/blacksmith_compose_frame{i}.png" for i in range(1, 9)]
DECOMPOSE_FRAMES = [f"resources/png/building/blacksmith_frames/blacksmith_decompose_frame{i}.png" for i in range(1, 9)]
ANIM_FRAME_DURATION = 0.1

player_materials = {"normal": 0, "rare": 0, "hero": 0, "legend": 0}
MATERIAL_NAMES = {"normal": "철광석", "rare": "미스릴", "hero": "오리하르콘", "legend": "아다만티움"}
GRADE_ORDER = ["일반", "희귀", "영웅", "전설"]
GRADE_COLORS = {"일반": (200, 200, 200), "희귀": (100, 150, 255), "영웅": (200, 100, 255), "전설": (255, 200, 50)}


def draw_blacksmith(screen, font_main, font_small, WIDTH, HEIGHT, game_state, dt=0, font_path=None):
    if blacksmith_state["message"] and dt > 0:
        blacksmith_state["message_timer"] += dt
        if blacksmith_state["message_timer"] > 2.5:
            blacksmith_state["message"] = ""
            blacksmith_state["message_timer"] = 0
    
    # 애니메이션 업데이트
    if blacksmith_state["animating"] and dt > 0:
        blacksmith_state["anim_timer"] += dt
        if blacksmith_state["anim_timer"] >= ANIM_FRAME_DURATION:
            blacksmith_state["anim_timer"] = 0
            blacksmith_state["anim_frame"] += 1
            frames = COMPOSE_FRAMES if blacksmith_state["anim_type"] == "compose" else DECOMPOSE_FRAMES
            if blacksmith_state["anim_frame"] >= len(frames):
                blacksmith_state["animating"] = False
                blacksmith_state["showing_result"] = True
    
    if blacksmith_state["stage"] == "inside":
        draw_inside(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)
    elif blacksmith_state["stage"] == "compose":
        draw_compose(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)
    elif blacksmith_state["stage"] == "decompose":
        draw_decompose(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)
    elif blacksmith_state["stage"] == "upgrade":
        draw_upgrade(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)


def draw_inside(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path):
    try:
        bg = pygame.image.load("resources/png/building/blacksmith_inside.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
        screen.blit(bg, (0, 0))
    except:
        screen.fill((60, 40, 30))
    
    # 타이틀
    title = font_main.render("대장간", True, (255, 200, 150))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
    
    # 버튼들 (중앙 배치)
    buttons = ["합성", "분해", "강화", "나가기"]
    btn_w, btn_h, btn_gap = 200, 50, 15
    total_h = len(buttons) * btn_h + (len(buttons) - 1) * btn_gap
    btn_x = (WIDTH - btn_w) // 2
    btn_start_y = (HEIGHT - total_h) // 2
    
    for i, txt in enumerate(buttons):
        btn_y = btn_start_y + i * (btn_h + btn_gap)
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        if blacksmith_state["selected_button"] == i:
            pygame.draw.rect(screen, (180, 100, 50), btn_rect)
            pygame.draw.rect(screen, (255, 150, 100), btn_rect, 3)
        else:
            pygame.draw.rect(screen, (100, 60, 30), btn_rect)
            pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
        text = font_small.render(txt, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=btn_rect.center))


def draw_compose(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path):
    from scripts.inventory import player_inventory
    draw_bg_overlay_light(screen, WIDTH, HEIGHT)
    
    # UI 이미지 원본 그대로 사용 (800x600)
    try:
        ui = pygame.image.load("resources/png/building/blacksmith_compose.png").convert_alpha()
        screen.blit(ui, (0, 0))
    except:
        pass
    
    screen.blit(font_main.render("무기 합성", True, (255, 200, 150)), (WIDTH // 2 - font_main.size("무기 합성")[0] // 2, 15))
    
    # 슬롯 위치
    slot_size_w = 185
    slot_size_h = 185
    left_slots = [(27, 147, 0), (247, 147, 1)]  # 왼쪽 2개 슬롯
    right_slot_rect = pygame.Rect(WIDTH - 27 - slot_size_w, 147, slot_size_w, slot_size_h)  # 오른쪽 결과 슬롯
    
    # 왼쪽 슬롯들 그리기
    for sx, sy, i in left_slots:
        rect = pygame.Rect(sx, sy, slot_size_w, slot_size_h)
        if not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
            if blacksmith_state["compose_selected"] == i:
                pygame.draw.rect(screen, (255, 255, 100), rect.inflate(16, 16), 10)
        w = blacksmith_state["compose_slots"][i]
        if w:
            draw_weapon_icon(screen, w, rect, font_small)
    
    # 애니메이션 프레임 그리기 (화살표 위치에)
    if blacksmith_state["animating"] and blacksmith_state["anim_type"] == "compose":
        frame_idx = min(blacksmith_state["anim_frame"], len(COMPOSE_FRAMES) - 1)
        try:
            frame_img = pygame.image.load(COMPOSE_FRAMES[frame_idx]).convert_alpha()
            screen.blit(frame_img, (0, 0))
        except Exception as e:
            print(f"Frame load error: {e}")
    
    # 결과 표시 (오른쪽 슬롯)
    if blacksmith_state["showing_result"] and blacksmith_state["anim_type"] == "compose":
        result = blacksmith_state["anim_result"]
        weapon = result.get("weapon") if result else None
        if weapon:
            # 결과 슬롯 하이라이트
            grade_color = GRADE_COLORS.get(weapon.grade, (200, 200, 200))
            pygame.draw.rect(screen, grade_color, right_slot_rect.inflate(16, 16), 10)
            draw_weapon_icon(screen, weapon, right_slot_rect, font_small)
        
        # 결과 메시지 (슬롯 아래)
        msg = result.get("message", "") if result else ""
        msg_text = font_small.render(msg, True, (255, 255, 100))
        screen.blit(msg_text, (right_slot_rect.centerx - msg_text.get_width() // 2, right_slot_rect.bottom + 15))
        
        # Enter 안내
        hint = font_small.render("Enter로 확인", True, (180, 180, 180))
        screen.blit(hint, (right_slot_rect.centerx - hint.get_width() // 2, right_slot_rect.bottom + 45))
    
    # 합성 버튼
    btn_rect = pygame.Rect(WIDTH // 2 - 60, 530, 120, 40)
    if not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
        if blacksmith_state["compose_selected"] == 2:
            pygame.draw.rect(screen, (180, 100, 50), btn_rect)
            pygame.draw.rect(screen, (255, 200, 100), btn_rect, 3)
        else:
            pygame.draw.rect(screen, (100, 60, 30), btn_rect)
            pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
    else:
        pygame.draw.rect(screen, (100, 60, 30), btn_rect)
        pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
    screen.blit(font_small.render("합성!", True, (255, 255, 255)), font_small.render("합성!", True, (255, 255, 255)).get_rect(center=btn_rect.center))
    
    if blacksmith_state["weapon_select_open"]:
        draw_weapon_select(screen, font_small, WIDTH, HEIGHT, [w for w in player_inventory["weapons"] if can_compose(w)])
    if blacksmith_state["message"]:
        draw_message(screen, font_small, WIDTH, HEIGHT)


def draw_decompose(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path):
    from scripts.inventory import player_inventory
    draw_bg_overlay_light(screen, WIDTH, HEIGHT)
    
    # UI 이미지 원본 그대로 사용 (800x600)
    try:
        ui = pygame.image.load("resources/png/building/blacksmith_decompose.png").convert_alpha()
        screen.blit(ui, (0, 0))
    except:
        pass
    
    screen.blit(font_main.render("무기 분해", True, (255, 200, 150)), (WIDTH // 2 - font_main.size("무기 분해")[0] // 2, 15))
    
    # 슬롯 위치
    slot_size_w = 185
    slot_size_h = 185
    slot_rect = pygame.Rect(27, 147, slot_size_w, slot_size_h)  # 왼쪽 슬롯
    right_slot_rect = pygame.Rect(WIDTH - 27 - slot_size_w, 147, slot_size_w, slot_size_h)  # 오른쪽 결과 슬롯
    
    # 왼쪽 슬롯 그리기
    if not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
        if blacksmith_state["decompose_selected"] == 0:
            pygame.draw.rect(screen, (255, 255, 100), slot_rect.inflate(16, 16), 10)
    if blacksmith_state["decompose_slot"]:
        draw_weapon_icon(screen, blacksmith_state["decompose_slot"], slot_rect, font_small)
    
    # 애니메이션 프레임 그리기
    if blacksmith_state["animating"] and blacksmith_state["anim_type"] == "decompose":
        frame_idx = min(blacksmith_state["anim_frame"], len(DECOMPOSE_FRAMES) - 1)
        try:
            frame_img = pygame.image.load(DECOMPOSE_FRAMES[frame_idx]).convert_alpha()
            screen.blit(frame_img, (0, 0))
        except Exception as e:
            print(f"Frame load error: {e}")
    
    # 결과 표시 (오른쪽 슬롯 영역)
    if blacksmith_state["showing_result"] and blacksmith_state["anim_type"] == "decompose":
        result = blacksmith_state["anim_result"]
        if result:
            # 결과 박스 (오른쪽 슬롯 위치)
            pygame.draw.rect(screen, (50, 45, 40), right_slot_rect)
            pygame.draw.rect(screen, (255, 215, 0), right_slot_rect, 4)
            
            # 골드 표시
            gold = result.get("gold", 0)
            gold_text = font_small.render(f"+{gold}G", True, (255, 215, 0))
            screen.blit(gold_text, (right_slot_rect.centerx - gold_text.get_width() // 2, right_slot_rect.y + 30))
            
            # 재료 표시
            mats = result.get("materials", {})
            y_offset = right_slot_rect.y + 70
            for mat_type, amount in mats.items():
                if amount > 0:
                    mat_name = MATERIAL_NAMES.get(mat_type, mat_type)
                    grade_idx = ["normal", "rare", "hero", "legend"].index(mat_type) if mat_type in ["normal", "rare", "hero", "legend"] else 0
                    color = GRADE_COLORS[GRADE_ORDER[grade_idx]]
                    mat_text = font_small.render(f"+{amount} {mat_name}", True, color)
                    screen.blit(mat_text, (right_slot_rect.centerx - mat_text.get_width() // 2, y_offset))
                    y_offset += 28
            
            # Enter 안내
            hint = font_small.render("Enter로 확인", True, (180, 180, 180))
            screen.blit(hint, (right_slot_rect.centerx - hint.get_width() // 2, right_slot_rect.bottom + 15))
    
    # 분해 버튼
    btn_rect = pygame.Rect(WIDTH // 2 - 60, 530, 120, 40)
    if not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
        if blacksmith_state["decompose_selected"] == 1:
            pygame.draw.rect(screen, (180, 100, 50), btn_rect)
            pygame.draw.rect(screen, (255, 200, 100), btn_rect, 3)
        else:
            pygame.draw.rect(screen, (100, 60, 30), btn_rect)
            pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
    else:
        pygame.draw.rect(screen, (100, 60, 30), btn_rect)
        pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
    screen.blit(font_small.render("분해!", True, (255, 255, 255)), font_small.render("분해!", True, (255, 255, 255)).get_rect(center=btn_rect.center))
    
    if blacksmith_state["weapon_select_open"]:
        draw_weapon_select(screen, font_small, WIDTH, HEIGHT, [w for w in player_inventory["weapons"] if can_decompose(w)])
    if blacksmith_state["message"]:
        draw_message(screen, font_small, WIDTH, HEIGHT)
    
    # 분해 버튼
    btn_rect = pygame.Rect(WIDTH // 2 - 60, 530, 120, 40)
    if not blacksmith_state["weapon_select_open"] and blacksmith_state["decompose_selected"] == 1:
        pygame.draw.rect(screen, (180, 100, 50), btn_rect)
        pygame.draw.rect(screen, (255, 200, 100), btn_rect, 3)
    else:
        pygame.draw.rect(screen, (100, 60, 30), btn_rect)
        pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
    screen.blit(font_small.render("분해!", True, (255, 255, 255)), font_small.render("분해!", True, (255, 255, 255)).get_rect(center=btn_rect.center))
    
    if blacksmith_state["weapon_select_open"]:
        draw_weapon_select(screen, font_small, WIDTH, HEIGHT, [w for w in player_inventory["weapons"] if can_decompose(w)])
    if blacksmith_state["message"]:
        draw_message(screen, font_small, WIDTH, HEIGHT)


def draw_upgrade(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path):
    from scripts.inventory import player_inventory
    draw_bg_overlay_light(screen, WIDTH, HEIGHT)
    
    # UI 이미지 원본 그대로 사용 (800x600)
    try:
        ui = pygame.image.load("resources/png/building/blacksmith_upgrade.png").convert_alpha()
        screen.blit(ui, (0, 0))
    except:
        pass
    
    screen.blit(font_main.render("무기 강화", True, (255, 200, 150)), (WIDTH // 2 - font_main.size("무기 강화")[0] // 2, 15))
    
    # 슬롯 위치 (크기 조정)
    slot_size_w = 185
    slot_size_h = 185
    slot_rect = pygame.Rect(307, 148, slot_size_w, slot_size_h)
    
    if not blacksmith_state["weapon_select_open"] and blacksmith_state["upgrade_selected"] == 0:
        pygame.draw.rect(screen, (255, 255, 100), slot_rect.inflate(16, 16), 10)
    
    if blacksmith_state["upgrade_slot"]:
        draw_weapon_icon(screen, blacksmith_state["upgrade_slot"], slot_rect, font_small)
        weapon = blacksmith_state["upgrade_slot"]
        level = getattr(weapon, 'upgrade_level', 0)
        screen.blit(font_small.render(f"현재: +{level}/5", True, (255, 200, 100)), (WIDTH // 2 - 50, 350))
        if level < 5:
            cost = get_upgrade_cost(weapon)
            cost_str = " ".join([f"{MATERIAL_NAMES[m]} {a}개(보유:{player_materials[m]})" for m, a in cost.items()])
            color = (100, 255, 100) if can_afford_upgrade(weapon) else (255, 100, 100)
            screen.blit(font_small.render(cost_str, True, color), (WIDTH // 2 - font_small.size(cost_str)[0] // 2, 380))
    
    # 강화 버튼
    btn_rect = pygame.Rect(WIDTH // 2 - 60, 530, 120, 40)
    if not blacksmith_state["weapon_select_open"] and blacksmith_state["upgrade_selected"] == 1:
        pygame.draw.rect(screen, (180, 100, 50), btn_rect)
        pygame.draw.rect(screen, (255, 200, 100), btn_rect, 3)
    else:
        pygame.draw.rect(screen, (100, 60, 30), btn_rect)
        pygame.draw.rect(screen, (150, 100, 80), btn_rect, 2)
    screen.blit(font_small.render("강화!", True, (255, 255, 255)), font_small.render("강화!", True, (255, 255, 255)).get_rect(center=btn_rect.center))
    
    # 강화 재료 (슬롯 오른쪽에 표시)
    draw_materials_right(screen, font_small, slot_rect.right + 20, slot_rect.y, slot_size_h)
    
    if blacksmith_state["weapon_select_open"]:
        draw_weapon_select(screen, font_small, WIDTH, HEIGHT, [w for w in player_inventory["weapons"] if can_upgrade(w)])
    if blacksmith_state["message"]:
        draw_message(screen, font_small, WIDTH, HEIGHT)


def draw_bg_overlay(screen, WIDTH, HEIGHT):
    try:
        bg = pygame.image.load("resources/png/building/blacksmith_inside.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
        screen.blit(bg, (0, 0))
    except:
        screen.fill((60, 40, 30))
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))


def draw_bg_overlay_light(screen, WIDTH, HEIGHT):
    try:
        bg = pygame.image.load("resources/png/building/blacksmith_inside.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
        screen.blit(bg, (0, 0))
    except:
        screen.fill((80, 60, 50))
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(80)
    overlay.fill((30, 20, 15))
    screen.blit(overlay, (0, 0))


def draw_materials(screen, font_small, WIDTH):
    x, y = WIDTH - 160, 15
    box_w, box_h = 150, 140
    pygame.draw.rect(screen, (40, 30, 20), (x - 10, y - 5, box_w, box_h))
    pygame.draw.rect(screen, (150, 120, 100), (x - 10, y - 5, box_w, box_h), 2)
    screen.blit(font_small.render("강화 재료", True, (255, 200, 150)), (x + 5, y + 5))
    y += 32
    for i, mat in enumerate(["normal", "rare", "hero", "legend"]):
        screen.blit(font_small.render(f"{MATERIAL_NAMES[mat]}: {player_materials[mat]}", True, GRADE_COLORS[GRADE_ORDER[i]]), (x + 5, y))
        y += 26


def draw_materials_right(screen, font_small, x, y, slot_size):
    # 슬롯과 같은 높이, 오른쪽 여백과 간격 동일하게
    gap = x - (309 + 186)  # 슬롯과 박스 사이 간격
    box_w = 800 - x - gap  # 오른쪽 여백도 같은 간격
    box_h = slot_size
    pygame.draw.rect(screen, (50, 40, 30), (x, y, box_w, box_h))
    pygame.draw.rect(screen, (180, 140, 100), (x, y, box_w, box_h), 3)
    # 타이틀 상단 중앙 배치
    title = font_small.render("강화 재료", True, (255, 220, 150))
    screen.blit(title, (x + box_w // 2 - title.get_width() // 2, y + 15))
    ty = y + 50
    for i, mat in enumerate(["normal", "rare", "hero", "legend"]):
        screen.blit(font_small.render(f"{MATERIAL_NAMES[mat]}: {player_materials[mat]}", True, GRADE_COLORS[GRADE_ORDER[i]]), (x + 15, ty))
        ty += 32


def draw_weapon_icon(screen, weapon, rect, font_small):
    pygame.draw.rect(screen, GRADE_COLORS.get(weapon.grade, (150, 150, 150)), rect, 3)
    if weapon.image_path:
        try:
            img = pygame.image.load(weapon.image_path).convert_alpha()
            screen.blit(pygame.transform.scale(img, (rect.width - 10, rect.height - 10)), (rect.x + 5, rect.y + 5))
        except:
            pass
    level = getattr(weapon, 'upgrade_level', 0)
    if level > 0:
        screen.blit(font_small.render(f"+{level}", True, (255, 255, 100)), (rect.x + 5, rect.y + 5))


def draw_weapon_select(screen, font_small, WIDTH, HEIGHT, weapons):
    pw, ph = 450, 350
    px, py = (WIDTH - pw) // 2, (HEIGHT - ph) // 2
    pygame.draw.rect(screen, (50, 40, 35), (px, py, pw, ph))
    pygame.draw.rect(screen, (200, 150, 100), (px, py, pw, ph), 3)
    screen.blit(font_small.render("무기 선택", True, (255, 200, 150)), (px + 20, py + 15))
    
    if not weapons:
        screen.blit(font_small.render("사용 가능한 무기가 없습니다", True, (180, 180, 180)), (px + pw // 2 - 100, py + ph // 2))
        return
    
    ly = py + 50
    visible = 7
    start = max(0, blacksmith_state["weapon_select_index"] - visible // 2)
    for i, w in enumerate(weapons[start:start + visible]):
        idx = start + i
        ir = pygame.Rect(px + 15, ly, pw - 30, 38)
        if idx == blacksmith_state["weapon_select_index"]:
            pygame.draw.rect(screen, (100, 80, 60), ir)
            pygame.draw.rect(screen, (255, 200, 100), ir, 2)
        color = GRADE_COLORS.get(w.grade, (200, 200, 200))
        level = getattr(w, 'upgrade_level', 0)
        name = f"+{level} {w.name}" if level > 0 else w.name
        screen.blit(font_small.render(name, True, color), (ir.x + 10, ir.y + 8))
        screen.blit(font_small.render(f"[{w.grade}]", True, color), (ir.right - 80, ir.y + 8))
        ly += 42


def draw_message(screen, font_small, WIDTH, HEIGHT):
    mw, mh = WIDTH - 100, 100
    mx, my = 50, HEIGHT - 130
    pygame.draw.rect(screen, (20, 20, 20), (mx, my, mw, mh))
    pygame.draw.rect(screen, (255, 255, 255), (mx, my, mw, mh), 2)
    t = font_small.render(blacksmith_state["message"], True, (255, 255, 255))
    screen.blit(t, (mx + 20, my + mh // 2 - t.get_height() // 2))


def can_compose(w):
    return w and w.grade not in ["전설", "몬스터"] and not getattr(w, 'is_boss_drop', False)

def can_decompose(w):
    return w and w.grade != "몬스터"

def can_upgrade(w):
    return w and w.grade != "몬스터" and getattr(w, 'upgrade_level', 0) < 5

def get_upgrade_cost(w):
    g, l = w.grade, getattr(w, 'upgrade_level', 0)
    c = 3 + l
    return {"normal": c} if g == "일반" else {"rare": c} if g == "희귀" else {"hero": c} if g == "영웅" else {"legend": c} if g == "전설" else {}

def can_afford_upgrade(w):
    return all(player_materials.get(m, 0) >= a for m, a in get_upgrade_cost(w).items())

def do_compose(w1, w2):
    if w1.grade != w2.grade:
        return None, "같은 등급만 합성 가능!"
    g = w1.grade
    ni = GRADE_ORDER.index(g) + 1
    if ni >= len(GRADE_ORDER):
        return None, "더 이상 합성 불가!"
    rate = 0.10 if g == "영웅" else 0.30
    if random.random() < rate:
        from scripts.weapons import ALL_WEAPONS, create_weapon
        avail = [wid for wid, wp in ALL_WEAPONS.items() if wp.grade == GRADE_ORDER[ni] and wp.grade != "몬스터"]
        if avail:
            return create_weapon(random.choice(avail)), f"합성 성공! {GRADE_ORDER[ni]} 등급 획득!"
    return random.choice([w1, w2]), "합성 실패... 무기 하나 반환"

def do_decompose(w):
    g = w.grade
    gold, mats = 0, {}
    if g == "일반":
        gold, mats["normal"] = random.randint(10, 30), random.randint(2, 3)
    elif g == "희귀":
        gold = random.randint(30, 60)
        mats["normal" if random.random() < 0.5 else "rare"] = random.randint(4, 5) if random.random() < 0.5 else random.randint(2, 3)
    elif g == "영웅":
        gold = random.randint(60, 120)
        mats["rare" if random.random() < 0.5 else "hero"] = random.randint(4, 5) if random.random() < 0.5 else random.randint(2, 3)
    elif g == "전설":
        gold = random.randint(150, 300)
        mats["hero"], mats["legend"] = random.randint(4, 5), random.randint(2, 3)
    return gold, mats

def do_upgrade(w):
    if not can_afford_upgrade(w):
        return False, "재료 부족!"
    for m, a in get_upgrade_cost(w).items():
        player_materials[m] -= a
    if not hasattr(w, 'upgrade_level'):
        w.upgrade_level = 0
    w.upgrade_level += 1
    bonus = random.randint(5, 15)
    w.max_durability += bonus
    w.durability = w.max_durability
    sb = 1 if random.random() < 0.6 else 2 if random.random() < 0.9 else 3
    if w.skill_ids:
        sid = random.choice(w.skill_ids)
        if not hasattr(w, 'skill_upgrades'):
            w.skill_upgrades = {}
        w.skill_upgrades[sid] = w.skill_upgrades.get(sid, 0) + sb
    if w.upgrade_level >= 5 and not getattr(w, 'is_transcended', False):
        w.is_transcended = True
        if hasattr(w, 'transcend_skill') and w.transcend_skill and w.transcend_skill not in w.skill_ids:
            w.skill_ids.append(w.transcend_skill)
            return True, f"+5 강화! 초월 달성! 새 스킬 해금!"
    return True, f"+{w.upgrade_level} 강화! 내구도+{bonus}, 스킬+{sb}"


def handle_blacksmith_input(events, game_state):
    from scripts.inventory import player_inventory
    for e in events:
        if e.type == pygame.KEYDOWN:
            if blacksmith_state["animating"]:
                return
            if blacksmith_state["showing_result"]:
                if e.key == pygame.K_RETURN:
                    blacksmith_state["showing_result"] = False
                    blacksmith_state["anim_result"] = None
                return
            
            if blacksmith_state["stage"] == "inside":
                handle_inside(e, game_state)
            elif blacksmith_state["stage"] == "compose":
                handle_compose(e, player_inventory)
            elif blacksmith_state["stage"] == "decompose":
                handle_decompose(e, player_inventory, game_state)
            elif blacksmith_state["stage"] == "upgrade":
                handle_upgrade(e, player_inventory)


def handle_inside(e, gs):
    if e.key == pygame.K_w:
        blacksmith_state["selected_button"] = max(0, blacksmith_state["selected_button"] - 1)
    elif e.key == pygame.K_s:
        blacksmith_state["selected_button"] = min(3, blacksmith_state["selected_button"] + 1)
    elif e.key == pygame.K_RETURN:
        b = blacksmith_state["selected_button"]
        if b == 0:
            blacksmith_state["stage"] = "compose"
            blacksmith_state["compose_slots"] = [None, None]
            blacksmith_state["compose_selected"] = 0
        elif b == 1:
            blacksmith_state["stage"] = "decompose"
            blacksmith_state["decompose_slot"] = None
            blacksmith_state["decompose_selected"] = 0
        elif b == 2:
            blacksmith_state["stage"] = "upgrade"
            blacksmith_state["upgrade_slot"] = None
            blacksmith_state["upgrade_selected"] = 0
        elif b == 3:
            exit_bs(gs)
    elif e.key == pygame.K_ESCAPE:
        exit_bs(gs)


def handle_compose(e, inv):
    # 애니메이션 중에는 입력 무시
    if blacksmith_state["animating"]:
        return
    
    # 결과 화면에서 Enter로 닫기
    if blacksmith_state["showing_result"]:
        if e.key == pygame.K_RETURN:
            blacksmith_state["showing_result"] = False
            blacksmith_state["anim_type"] = None
            blacksmith_state["anim_result"] = None
        return
    
    if blacksmith_state["weapon_select_open"]:
        ws = [w for w in inv["weapons"] if can_compose(w)]
        if e.key == pygame.K_w:
            blacksmith_state["weapon_select_index"] = max(0, blacksmith_state["weapon_select_index"] - 1)
        elif e.key == pygame.K_s and ws:
            blacksmith_state["weapon_select_index"] = min(len(ws) - 1, blacksmith_state["weapon_select_index"] + 1)
        elif e.key == pygame.K_RETURN and ws and blacksmith_state["weapon_select_index"] < len(ws):
            w = ws[blacksmith_state["weapon_select_index"]]
            inv["weapons"].remove(w)
            t = blacksmith_state["weapon_select_target"]
            blacksmith_state["compose_slots"][0 if t == "compose1" else 1] = w
            blacksmith_state["weapon_select_open"] = False
        elif e.key == pygame.K_ESCAPE:
            blacksmith_state["weapon_select_open"] = False
    else:
        if e.key == pygame.K_w:
            blacksmith_state["compose_selected"] = max(0, blacksmith_state["compose_selected"] - 1)
        elif e.key == pygame.K_s:
            blacksmith_state["compose_selected"] = min(2, blacksmith_state["compose_selected"] + 1)
        elif e.key in [pygame.K_a, pygame.K_d] and blacksmith_state["compose_selected"] < 2:
            blacksmith_state["compose_selected"] = 0 if e.key == pygame.K_a else 1
        elif e.key == pygame.K_RETURN:
            s = blacksmith_state["compose_selected"]
            if s < 2:
                if blacksmith_state["compose_slots"][s]:
                    inv["weapons"].append(blacksmith_state["compose_slots"][s])
                    blacksmith_state["compose_slots"][s] = None
                else:
                    blacksmith_state["weapon_select_open"] = True
                    blacksmith_state["weapon_select_index"] = 0
                    blacksmith_state["weapon_select_target"] = f"compose{s+1}"
            else:
                w1, w2 = blacksmith_state["compose_slots"]
                if w1 and w2:
                    # 합성 실행 및 결과 저장
                    r, m = do_compose(w1, w2)
                    blacksmith_state["compose_slots"] = [None, None]
                    if r:
                        inv["weapons"].append(r)
                    
                    # 애니메이션 시작
                    blacksmith_state["animating"] = True
                    blacksmith_state["anim_type"] = "compose"
                    blacksmith_state["anim_frame"] = 0
                    blacksmith_state["anim_timer"] = 0
                    blacksmith_state["anim_result"] = {"title": "합성 결과", "weapon": r, "message": m}
                else:
                    blacksmith_state["message"], blacksmith_state["message_timer"] = "무기 2개를 넣어주세요!", 0
        elif e.key == pygame.K_ESCAPE:
            for w in blacksmith_state["compose_slots"]:
                if w:
                    inv["weapons"].append(w)
            blacksmith_state["compose_slots"] = [None, None]
            blacksmith_state["stage"] = "inside"


def handle_decompose(e, inv, gs):
    # 애니메이션 중에는 입력 무시
    if blacksmith_state["animating"]:
        return
    
    # 결과 화면에서 Enter로 닫기
    if blacksmith_state["showing_result"]:
        if e.key == pygame.K_RETURN:
            blacksmith_state["showing_result"] = False
            blacksmith_state["anim_type"] = None
            blacksmith_state["anim_result"] = None
        return
    
    if blacksmith_state["weapon_select_open"]:
        ws = [w for w in inv["weapons"] if can_decompose(w)]
        if e.key == pygame.K_w:
            blacksmith_state["weapon_select_index"] = max(0, blacksmith_state["weapon_select_index"] - 1)
        elif e.key == pygame.K_s and ws:
            blacksmith_state["weapon_select_index"] = min(len(ws) - 1, blacksmith_state["weapon_select_index"] + 1)
        elif e.key == pygame.K_RETURN and ws and blacksmith_state["weapon_select_index"] < len(ws):
            w = ws[blacksmith_state["weapon_select_index"]]
            inv["weapons"].remove(w)
            blacksmith_state["decompose_slot"] = w
            blacksmith_state["weapon_select_open"] = False
        elif e.key == pygame.K_ESCAPE:
            blacksmith_state["weapon_select_open"] = False
    else:
        if e.key == pygame.K_w:
            blacksmith_state["decompose_selected"] = 0
        elif e.key == pygame.K_s:
            blacksmith_state["decompose_selected"] = 1
        elif e.key == pygame.K_RETURN:
            if blacksmith_state["decompose_selected"] == 0:
                if blacksmith_state["decompose_slot"]:
                    inv["weapons"].append(blacksmith_state["decompose_slot"])
                    blacksmith_state["decompose_slot"] = None
                else:
                    blacksmith_state["weapon_select_open"] = True
                    blacksmith_state["weapon_select_index"] = 0
            else:
                w = blacksmith_state["decompose_slot"]
                if w:
                    # 분해 실행 및 결과 저장
                    gold, mats = do_decompose(w)
                    gs["gold"] = gs.get("gold", 0) + gold
                    for m, a in mats.items():
                        player_materials[m] += a
                    blacksmith_state["decompose_slot"] = None
                    
                    # 애니메이션 시작
                    blacksmith_state["animating"] = True
                    blacksmith_state["anim_type"] = "decompose"
                    blacksmith_state["anim_frame"] = 0
                    blacksmith_state["anim_timer"] = 0
                    blacksmith_state["anim_result"] = {"title": "분해 결과", "gold": gold, "materials": mats, "message": "분해 완료!"}
                else:
                    blacksmith_state["message"], blacksmith_state["message_timer"] = "무기를 넣어주세요!", 0
        elif e.key == pygame.K_ESCAPE:
            if blacksmith_state["decompose_slot"]:
                inv["weapons"].append(blacksmith_state["decompose_slot"])
            blacksmith_state["decompose_slot"] = None
            blacksmith_state["stage"] = "inside"


def handle_upgrade(e, inv):
    if blacksmith_state["weapon_select_open"]:
        ws = [w for w in inv["weapons"] if can_upgrade(w)]
        if e.key == pygame.K_w:
            blacksmith_state["weapon_select_index"] = max(0, blacksmith_state["weapon_select_index"] - 1)
        elif e.key == pygame.K_s and ws:
            blacksmith_state["weapon_select_index"] = min(len(ws) - 1, blacksmith_state["weapon_select_index"] + 1)
        elif e.key == pygame.K_RETURN and ws and blacksmith_state["weapon_select_index"] < len(ws):
            w = ws[blacksmith_state["weapon_select_index"]]
            inv["weapons"].remove(w)
            blacksmith_state["upgrade_slot"] = w
            blacksmith_state["weapon_select_open"] = False
        elif e.key == pygame.K_ESCAPE:
            blacksmith_state["weapon_select_open"] = False
    else:
        if e.key == pygame.K_w:
            blacksmith_state["upgrade_selected"] = 0
        elif e.key == pygame.K_s:
            blacksmith_state["upgrade_selected"] = 1
        elif e.key == pygame.K_RETURN:
            if blacksmith_state["upgrade_selected"] == 0:
                if blacksmith_state["upgrade_slot"]:
                    inv["weapons"].append(blacksmith_state["upgrade_slot"])
                    blacksmith_state["upgrade_slot"] = None
                else:
                    blacksmith_state["weapon_select_open"] = True
                    blacksmith_state["weapon_select_index"] = 0
            else:
                w = blacksmith_state["upgrade_slot"]
                if w:
                    if getattr(w, 'upgrade_level', 0) >= 5:
                        blacksmith_state["message"] = "이미 최대 강화!"
                    else:
                        _, msg = do_upgrade(w)
                        blacksmith_state["message"] = msg
                    blacksmith_state["message_timer"] = 0
                else:
                    blacksmith_state["message"], blacksmith_state["message_timer"] = "무기를 넣어주세요!", 0
        elif e.key == pygame.K_ESCAPE:
            if blacksmith_state["upgrade_slot"]:
                inv["weapons"].append(blacksmith_state["upgrade_slot"])
            blacksmith_state["upgrade_slot"] = None
            blacksmith_state["stage"] = "inside"


def exit_bs(gs):
    gs["state"] = "town"
    blacksmith_state["stage"] = "inside"
    blacksmith_state["selected_button"] = 0
    blacksmith_state["is_talking"] = False
    blacksmith_state["message"] = ""