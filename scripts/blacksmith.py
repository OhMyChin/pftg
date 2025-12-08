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
    # 텍스트 박스 관련
    "textbox_message": "",
    "textbox_timer": 0,
    "textbox_needs_enter": False,  # True면 Enter 대기, False면 1.5초 후 자동 닫힘
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
    # 텍스트박스 타이머 (Enter 불필요시 1.5초 후 자동 닫힘)
    if blacksmith_state["textbox_message"] and not blacksmith_state["textbox_needs_enter"] and dt > 0:
        blacksmith_state["textbox_timer"] += dt
        if blacksmith_state["textbox_timer"] > 1.5:
            blacksmith_state["textbox_message"] = ""
            blacksmith_state["textbox_timer"] = 0
    
    # 메시지 타이머 (기존)
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
        w = blacksmith_state["compose_slots"][i]
        
        # 선택 테두리 (무기 있어도 표시)
        if not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
            if blacksmith_state["compose_selected"] == i:
                pygame.draw.rect(screen, (255, 255, 100), rect.inflate(16, 16), 8)
        
        # 무기 아이콘
        if w:
            draw_weapon_icon(screen, w, rect, font_small)
    
    # 애니메이션 프레임 그리기
    if blacksmith_state["animating"] and blacksmith_state["anim_type"] == "compose":
        frame_idx = min(blacksmith_state["anim_frame"], len(COMPOSE_FRAMES) - 1)
        try:
            frame_img = pygame.image.load(COMPOSE_FRAMES[frame_idx]).convert_alpha()
            screen.blit(frame_img, (0, 0))
        except Exception as e:
            print(f"Frame load error: {e}")
    
    # 합성 버튼 (텍스트 박스보다 먼저 그림)
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
    
    # 확률 안내 (두 슬롯 모두 채워졌을 때)
    w1 = blacksmith_state["compose_slots"][0]
    w2 = blacksmith_state["compose_slots"][1]
    if w1 and w2 and not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
        if w1.grade == w2.grade:
            grade = w1.grade
            # 등급별 성공률 (일반 50%, 희귀 25%, 영웅 10%)
            rates = {"일반": 50, "희귀": 25, "영웅": 10}
            rate = rates.get(grade, 10)
            next_grades = {"일반": "희귀", "희귀": "영웅", "영웅": "전설"}
            next_grade = next_grades.get(grade, "???")
            
            # 등급별 색상
            grade_colors = {
                "희귀": (100, 150, 255),    # 파란색
                "영웅": (200, 100, 255),    # 보라색
                "전설": (255, 200, 100),    # 금색
            }
            next_grade_color = grade_colors.get(next_grade, (255, 255, 255))
            
            # 안내 텍스트 (글씨 크기 키움)
            if font_path:
                info_font = pygame.font.Font(font_path, 26)
            else:
                info_font = pygame.font.Font(None, 26)
            
            info_y = 355
            
            # 성공 확률
            text1 = info_font.render(f"성공 확률: {rate}%", True, (100, 255, 100))
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, info_y))
            
            # 성공 시 [등급] 등급 무기 획득 - 등급 부분만 색상 다르게
            part1 = info_font.render("성공 시 [", True, (255, 230, 200))
            part2 = info_font.render(next_grade, True, next_grade_color)
            part3 = info_font.render("] 등급 무기 획득", True, (255, 230, 200))
            total_width = part1.get_width() + part2.get_width() + part3.get_width()
            start_x = WIDTH // 2 - total_width // 2
            screen.blit(part1, (start_x, info_y + 35))
            screen.blit(part2, (start_x + part1.get_width(), info_y + 35))
            screen.blit(part3, (start_x + part1.get_width() + part2.get_width(), info_y + 35))
            
            # 실패 시
            text3 = info_font.render("실패 시 무기 1개 반환", True, (255, 150, 150))
            screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, info_y + 70))
        else:
            # 등급 다를 때
            if font_path:
                info_font = pygame.font.Font(font_path, 26)
            else:
                info_font = pygame.font.Font(None, 26)
            warn_text = info_font.render("같은 등급 무기만 합성 가능!", True, (255, 100, 100))
            screen.blit(warn_text, (WIDTH // 2 - warn_text.get_width() // 2, 380))
    
    # 결과 표시 (오른쪽 슬롯 + 텍스트 박스) - 버튼 위에 그려짐
    if blacksmith_state["showing_result"] and blacksmith_state["anim_type"] == "compose":
        result = blacksmith_state["anim_result"]
        weapon = result.get("weapon") if result else None
        msg = result.get("message", "") if result else ""
        
        if weapon:
            draw_weapon_icon(screen, weapon, right_slot_rect, font_small)
        
        # 텍스트 박스 (버튼 위에 그려짐)
        if msg:
            draw_text_box(screen, font_small, WIDTH, HEIGHT, msg, need_enter=True)
    
    if blacksmith_state["weapon_select_open"]:
        # 합성 가능한 모든 무기 표시 (등급 필터 없음)
        ws = [w for w in player_inventory["weapons"] if can_compose(w)]
        draw_weapon_select(screen, font_small, WIDTH, HEIGHT, ws)
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
    
    # 슬롯 위치 (원래대로 - 재료 슬롯은 오른쪽 끝)
    slot_size_w = 185
    slot_size_h = 185
    input_slot_rect = pygame.Rect(27, 147, slot_size_w, slot_size_h)  # 분해할 무기 (화살표 왼쪽)
    result_right_rect = pygame.Rect(WIDTH - 27 - slot_size_w, 147, slot_size_w, slot_size_h)  # 결과: 재료 (원래 위치)
    result_left_rect = pygame.Rect(WIDTH - 27 - slot_size_w * 2 - 35, 147, slot_size_w, slot_size_h)  # 결과: 골드 (재료 왼쪽)
    
    # 결과 표시 중이 아닐 때 - 입력 슬롯에 무기 표시
    if not blacksmith_state["showing_result"]:
        w = blacksmith_state["decompose_slot"]
        
        # 선택 테두리 (무기 있어도 표시)
        if not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"]:
            if blacksmith_state["decompose_selected"] == 0:
                pygame.draw.rect(screen, (255, 255, 100), input_slot_rect.inflate(16, 16), 8)
        
        # 무기 아이콘
        if w:
            draw_weapon_icon(screen, w, input_slot_rect, font_small)
    
    # 애니메이션 프레임 그리기
    if blacksmith_state["animating"] and blacksmith_state["anim_type"] == "decompose":
        frame_idx = min(blacksmith_state["anim_frame"], len(DECOMPOSE_FRAMES) - 1)
        try:
            frame_img = pygame.image.load(DECOMPOSE_FRAMES[frame_idx]).convert_alpha()
            screen.blit(frame_img, (0, 0))
        except Exception as e:
            print(f"Frame load error: {e}")
    
    # 분해 버튼 (텍스트 박스보다 먼저 그림)
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
    
    # 분해 결과 안내 (슬롯에 무기가 있을 때)
    w = blacksmith_state["decompose_slot"]
    if w and not blacksmith_state["weapon_select_open"] and not blacksmith_state["animating"] and not blacksmith_state["showing_result"]:
        grade = w.grade
        
        if font_path:
            info_font = pygame.font.Font(font_path, 26)
        else:
            info_font = pygame.font.Font(None, 26)
        
        info_y = 345
        
        # 재료 색상 (GRADE_COLORS 기준)
        normal_color = (255, 255, 255)  # 흰색 - 철광석
        rare_color = (100, 150, 255)    # 파란색 - 미스릴
        hero_color = (200, 100, 255)    # 보라색 - 오리하르콘
        legend_color = (255, 200, 100)  # 금색 - 아다만티움
        
        # 등급별 예상 보상 (하위 등급 3~5개 50%, 동일 등급 1~2개 50%)
        text1 = info_font.render(f"예상 골드: {['10~30', '30~60', '60~120', '150~300'][['일반', '희귀', '영웅', '전설'].index(grade) if grade in ['일반', '희귀', '영웅', '전설'] else 0]}G", True, (255, 215, 0))
        screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, info_y))
        
        if grade == "일반":
            # 철광석: 1개(30%) 2개(20%) - 일반은 동일 등급만
            mat_text = info_font.render("철광석: 1개(60%) 2개(40%)", True, normal_color)
            screen.blit(mat_text, (WIDTH // 2 - mat_text.get_width() // 2, info_y + 35))
        elif grade == "희귀":
            # 철광석: 1개(15%) 2개(20%) 3개(15%)
            mat_text1 = info_font.render("철광석: 1개(15%) 2개(20%) 3개(15%)", True, normal_color)
            # 미스릴: 1개(30%) 2개(20%)
            mat_text2 = info_font.render("미스릴: 1개(30%) 2개(20%)", True, rare_color)
            screen.blit(mat_text1, (WIDTH // 2 - mat_text1.get_width() // 2, info_y + 35))
            screen.blit(mat_text2, (WIDTH // 2 - mat_text2.get_width() // 2, info_y + 70))
        elif grade == "영웅":
            # 미스릴: 1개(15%) 2개(20%) 3개(15%)
            mat_text1 = info_font.render("미스릴: 1개(15%) 2개(20%) 3개(15%)", True, rare_color)
            # 오리하르콘: 1개(30%) 2개(20%)
            mat_text2 = info_font.render("오리하르콘: 1개(30%) 2개(20%)", True, hero_color)
            screen.blit(mat_text1, (WIDTH // 2 - mat_text1.get_width() // 2, info_y + 35))
            screen.blit(mat_text2, (WIDTH // 2 - mat_text2.get_width() // 2, info_y + 70))
        elif grade == "전설":
            # 오리하르콘: 1개(15%) 2개(20%) 3개(15%)
            mat_text1 = info_font.render("오리하르콘: 1개(15%) 2개(20%) 3개(15%)", True, hero_color)
            # 아다만티움: 1개(30%) 2개(20%)
            mat_text2 = info_font.render("아다만티움: 1개(30%) 2개(20%)", True, legend_color)
            screen.blit(mat_text1, (WIDTH // 2 - mat_text1.get_width() // 2, info_y + 35))
            screen.blit(mat_text2, (WIDTH // 2 - mat_text2.get_width() // 2, info_y + 70))
    
    # 결과 표시: 골드 (왼쪽), 재료 (오른쪽 - 원래 슬롯 위치)
    if blacksmith_state["showing_result"] and blacksmith_state["anim_type"] == "decompose":
        result = blacksmith_state["anim_result"]
        if result:
            gold = result.get("gold", 0)
            mats = result.get("materials", {})
            
            # 골드 슬롯 (재료 왼쪽)
            pygame.draw.rect(screen, (80, 60, 20), result_left_rect)
            pygame.draw.rect(screen, (255, 215, 0), result_left_rect, 3)
            gold_text = font_main.render(f"+{gold}G", True, (255, 215, 0))
            screen.blit(gold_text, (result_left_rect.centerx - gold_text.get_width() // 2, result_left_rect.centery - gold_text.get_height() // 2))
            
            # 재료 슬롯 (원래 오른쪽 위치)
            pygame.draw.rect(screen, (30, 50, 70), result_right_rect)
            pygame.draw.rect(screen, (150, 200, 255), result_right_rect, 3)
            
            # 재료 텍스트를 수직 중앙에 정렬
            mat_lines = [(mat_type, amount) for mat_type, amount in mats.items() if amount > 0]
            total_height = len(mat_lines) * 32
            y_offset = result_right_rect.centery - total_height // 2
            
            for mat_type, amount in mat_lines:
                mat_name = MATERIAL_NAMES.get(mat_type, mat_type)
                grade_idx = ["normal", "rare", "hero", "legend"].index(mat_type) if mat_type in ["normal", "rare", "hero", "legend"] else 0
                color = GRADE_COLORS[GRADE_ORDER[grade_idx]]
                mat_text = font_small.render(f"+{amount} {mat_name}", True, color)
                screen.blit(mat_text, (result_right_rect.centerx - mat_text.get_width() // 2, y_offset))
                y_offset += 32
            
            # 텍스트 박스 (버튼 위에 그려짐)
            draw_text_box(screen, font_small, WIDTH, HEIGHT, "분해 완료!", need_enter=True)
    
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
            
            # 강화 확률 표시
            prob_text1 = "추가 공격력: +2(50%) / +3(50%)"
            prob_text2 = "내구도: +5(30%) / +10(40%) / +15(30%)"
            screen.blit(font_small.render(prob_text1, True, (255, 100, 100)), (WIDTH // 2 - font_small.size(prob_text1)[0] // 2, 410))
            screen.blit(font_small.render(prob_text2, True, (100, 200, 255)), (WIDTH // 2 - font_small.size(prob_text2)[0] // 2, 440))
    
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
    overlay.set_alpha(150)  # 더 어둡게 (80 → 150)
    overlay.fill((20, 15, 10))
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
    """무기 아이콘 그리기 - 배경색이 등급색"""
    grade_color = GRADE_COLORS.get(weapon.grade, (150, 150, 150))
    
    # 배경을 등급 색상으로 (어둡게)
    dark_grade = (grade_color[0] // 3, grade_color[1] // 3, grade_color[2] // 3)
    pygame.draw.rect(screen, dark_grade, rect)
    pygame.draw.rect(screen, grade_color, rect, 3)
    
    # 무기 이미지
    if weapon.image_path:
        try:
            img = pygame.image.load(weapon.image_path).convert_alpha()
            screen.blit(pygame.transform.scale(img, (rect.width - 10, rect.height - 10)), (rect.x + 5, rect.y + 5))
        except:
            pass
    
    # 강화 레벨
    level = getattr(weapon, 'upgrade_level', 0)
    if level > 0:
        screen.blit(font_small.render(f"+{level}", True, (255, 255, 100)), (rect.x + 5, rect.y + 5))


def draw_weapon_select(screen, font_small, WIDTH, HEIGHT, weapons):
    pw, ph = 450, 400  # 높이 늘림 (350 → 400)
    px, py = (WIDTH - pw) // 2, (HEIGHT - ph) // 2
    pygame.draw.rect(screen, (50, 40, 35), (px, py, pw, ph))
    pygame.draw.rect(screen, (200, 150, 100), (px, py, pw, ph), 3)
    screen.blit(font_small.render("무기 선택", True, (255, 200, 150)), (px + 20, py + 15))
    
    if not weapons:
        # 중앙 정렬
        no_weapon_text = font_small.render("사용 가능한 무기가 없습니다", True, (180, 180, 180))
        screen.blit(no_weapon_text, (px + pw // 2 - no_weapon_text.get_width() // 2, py + ph // 2 - no_weapon_text.get_height() // 2))
        return
    
    # 위쪽 화살표 영역
    arrow_x = px + pw // 2
    arrow_up_y = py + 45
    
    # 위쪽 화살표
    if scroll_offset > 0 if 'scroll_offset' in dir() else False:
        pass  # 아래에서 그림
    
    ly = py + 65  # 화살표 공간 확보 (50 → 65)
    visible = 7
    selected_slot = 3  # 선택 슬롯 고정 (가운데)
    
    # 스크롤 오프셋 계산 (선택된 아이템이 가운데 오도록)
    scroll_offset = max(0, min(blacksmith_state["weapon_select_index"] - selected_slot, len(weapons) - visible))
    
    for i in range(visible):
        idx = scroll_offset + i
        ir = pygame.Rect(px + 15, ly, pw - 30, 38)
        
        if idx < len(weapons):
            w = weapons[idx]
            # 선택된 아이템
            if idx == blacksmith_state["weapon_select_index"]:
                pygame.draw.rect(screen, (100, 80, 60), ir)
                pygame.draw.rect(screen, (255, 200, 100), ir, 2)
            
            color = GRADE_COLORS.get(w.grade, (200, 200, 200))
            level = getattr(w, 'upgrade_level', 0)
            name = f"+{level} {w.name}" if level > 0 else w.name
            screen.blit(font_small.render(name, True, color), (ir.x + 10, ir.y + 8))
            grade_text = font_small.render(f"[{w.grade}]", True, color)
            screen.blit(grade_text, (ir.right - grade_text.get_width() - 10, ir.y + 8))
        
        ly += 42
    
    # 위/아래 화살표 (스크롤 인디케이터)
    # 위쪽 화살표
    if scroll_offset > 0:
        pygame.draw.polygon(screen, (255, 200, 150), [
            (arrow_x, arrow_up_y),
            (arrow_x - 10, arrow_up_y + 12),
            (arrow_x + 10, arrow_up_y + 12)
        ])
    
    # 아래쪽 화살표 (리스트 끝 아래에 여유 공간)
    if scroll_offset + visible < len(weapons):
        arrow_down_y = py + ph - 25  # 더 아래로
        pygame.draw.polygon(screen, (255, 200, 150), [
            (arrow_x, arrow_down_y + 12),
            (arrow_x - 10, arrow_down_y),
            (arrow_x + 10, arrow_down_y)
        ])


def wrap_text(text, font, max_width):
    """텍스트 줄바꿈"""
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
    
    return lines if lines else [text]


def draw_text_box(screen, font_small, WIDTH, HEIGHT, message, need_enter=True):
    """대장간 스타일 텍스트 박스 - 버튼 위에 그려짐"""
    mw, mh = WIDTH - 100, 140  # 세로 길이 40 더 늘림
    mx, my = 50, HEIGHT - 210  # 위로 40 더 올림
    
    # 대장간 스타일 배경
    pygame.draw.rect(screen, (40, 30, 20), (mx, my, mw, mh))
    pygame.draw.rect(screen, (200, 150, 100), (mx, my, mw, mh), 3)
    
    # 줄바꿈 처리
    lines = wrap_text(message, font_small, mw - 60)
    y_offset = my + 20
    for line in lines:
        t = font_small.render(line, True, (255, 230, 200))
        screen.blit(t, (mx + 20, y_offset))
        y_offset += 28
    
    # Enter 대기 시 화살표 표시 (배틀 시스템 스타일)
    if need_enter:
        arrow_text = pygame.font.SysFont("consolas", 30).render("▼", True, (255, 200, 150))
        screen.blit(arrow_text, (mx + mw - 40, my + mh - 35))


def draw_textbox(screen, font_small, WIDTH, HEIGHT):
    """상태 기반 텍스트 박스 (호환용)"""
    if not blacksmith_state["textbox_message"]:
        return
    draw_text_box(screen, font_small, WIDTH, HEIGHT, 
                  blacksmith_state["textbox_message"], 
                  blacksmith_state["textbox_needs_enter"])


def draw_message(screen, font_small, WIDTH, HEIGHT):
    """기존 메시지 - 대장간 스타일"""
    mw, mh = WIDTH - 100, 140
    mx, my = 50, HEIGHT - 210
    
    # 대장간 스타일 배경
    pygame.draw.rect(screen, (40, 30, 20), (mx, my, mw, mh))
    pygame.draw.rect(screen, (200, 150, 100), (mx, my, mw, mh), 3)
    
    lines = wrap_text(blacksmith_state["message"], font_small, mw - 60)
    y_offset = my + 20
    for line in lines:
        t = font_small.render(line, True, (255, 230, 200))
        screen.blit(t, (mx + 20, y_offset))
        y_offset += 28


def can_compose(w):
    return w and w.grade not in ["전설", "몬스터"] and not getattr(w, 'is_boss_drop', False)

def can_compose_together(w1, w2):
    """두 무기가 합성 가능한지 (같은 등급 불가)"""
    if not w1 or not w2:
        return False
    return w1.grade != w2.grade

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
    """같은 등급 무기 2개를 합성하여 상위 등급 획득 시도"""
    if w1.grade != w2.grade:
        return None, "같은 등급만 합성 가능!"
    
    g = w1.grade
    g_idx = GRADE_ORDER.index(g) if g in GRADE_ORDER else 0
    
    if g_idx >= len(GRADE_ORDER) - 1:
        return None, "전설 등급은 합성 불가!"
    
    # 등급별 성공률: 일반 50%, 희귀 25%, 영웅 10%
    rates = {"일반": 0.50, "희귀": 0.25, "영웅": 0.10}
    rate = rates.get(g, 0.10)
    
    if random.random() < rate:
        from scripts.weapons import ALL_WEAPONS, create_weapon
        next_grade = GRADE_ORDER[g_idx + 1]
        # 보스 무기 제외 (is_boss_drop 속성이 True인 무기 제외)
        avail = [wid for wid, wp in ALL_WEAPONS.items() 
                 if wp.grade == next_grade 
                 and wp.grade != "몬스터" 
                 and not getattr(wp, 'is_boss_drop', False)]
        if avail:
            return create_weapon(random.choice(avail)), f"합성 성공! {next_grade} 등급 획득!"
    return random.choice([w1, w2]), "합성 실패... 무기 하나 반환"

def do_decompose(w):
    g = w.grade
    gold, mats = 0, {}
    if g == "일반":
        gold = random.randint(10, 30)
        # 철광석: 1개(60%) 2개(40%)
        roll = random.random()
        if roll < 0.6:
            mats["normal"] = 1
        else:
            mats["normal"] = 2
    elif g == "희귀":
        gold = random.randint(30, 60)
        # 철광석: 1개(15%) 2개(20%) 3개(15%) / 미스릴: 1개(30%) 2개(20%)
        roll = random.random()
        if roll < 0.15:
            mats["normal"] = 1
        elif roll < 0.35:
            mats["normal"] = 2
        elif roll < 0.50:
            mats["normal"] = 3
        elif roll < 0.80:
            mats["rare"] = 1
        else:
            mats["rare"] = 2
    elif g == "영웅":
        gold = random.randint(60, 120)
        # 미스릴: 1개(15%) 2개(20%) 3개(15%) / 오리하르콘: 1개(30%) 2개(20%)
        roll = random.random()
        if roll < 0.15:
            mats["rare"] = 1
        elif roll < 0.35:
            mats["rare"] = 2
        elif roll < 0.50:
            mats["rare"] = 3
        elif roll < 0.80:
            mats["hero"] = 1
        else:
            mats["hero"] = 2
    elif g == "전설":
        gold = random.randint(150, 300)
        # 오리하르콘: 1개(15%) 2개(20%) 3개(15%) / 아다만티움: 1개(30%) 2개(20%)
        roll = random.random()
        if roll < 0.15:
            mats["hero"] = 1
        elif roll < 0.35:
            mats["hero"] = 2
        elif roll < 0.50:
            mats["hero"] = 3
        elif roll < 0.80:
            mats["legend"] = 1
        else:
            mats["legend"] = 2
    return gold, mats

def do_upgrade(w):
    if not can_afford_upgrade(w):
        return False, "재료 부족!"
    for m, a in get_upgrade_cost(w).items():
        player_materials[m] -= a
    if not hasattr(w, 'upgrade_level'):
        w.upgrade_level = 0
    if not hasattr(w, 'bonus_power'):
        w.bonus_power = 0
    
    w.upgrade_level += 1
    
    # 추가 공격력: 2(50%) 또는 3(50%)
    power_bonus = random.choice([2, 3])
    w.bonus_power += power_bonus
    
    # 내구도 보너스: 5(30%) / 10(40%) / 15(30%)
    durability_roll = random.random()
    if durability_roll < 0.3:
        durability_bonus = 5
    elif durability_roll < 0.7:
        durability_bonus = 10
    else:
        durability_bonus = 15
    w.max_durability += durability_bonus
    w.durability = w.max_durability
    
    # 초월 체크
    if w.upgrade_level >= 5 and not getattr(w, 'is_transcended', False):
        w.is_transcended = True
        # 전설 무기: 패시브 해금
        if hasattr(w, 'transcend_passive') and w.transcend_passive:
            return True, f"+5 강화! 초월 달성! 패시브 해금!"
        # 일반~영웅 무기: 스킬 해금
        elif hasattr(w, 'transcend_skill') and w.transcend_skill and w.transcend_skill not in w.skill_ids:
            w.skill_ids.append(w.transcend_skill)
            return True, f"+5 강화! 초월 달성! 새 스킬 해금!"
    return True, f"+{w.upgrade_level} 강화! 공격력+{power_bonus}, 내구도+{durability_bonus}"


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
        # 합성 가능한 모든 무기 표시 (등급 필터 없음)
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
        # A/D로 슬롯 좌우 이동
        if e.key == pygame.K_a:
            if blacksmith_state["compose_selected"] < 2:
                blacksmith_state["compose_selected"] = 0
        elif e.key == pygame.K_d:
            if blacksmith_state["compose_selected"] < 2:
                blacksmith_state["compose_selected"] = 1
        # W로 슬롯으로, S로 버튼으로
        elif e.key == pygame.K_w:
            if blacksmith_state["compose_selected"] == 2:
                blacksmith_state["compose_selected"] = 0
        elif e.key == pygame.K_s:
            blacksmith_state["compose_selected"] = 2  # 바로 버튼으로
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
                    # 등급 체크
                    if w1.grade != w2.grade:
                        blacksmith_state["message"], blacksmith_state["message_timer"] = "같은 등급만 합성 가능!", 0
                        return
                    
                    # 합성 실행 및 결과 저장
                    r, m = do_compose(w1, w2)
                    blacksmith_state["compose_slots"] = [None, None]
                    if r:
                        from scripts.inventory import try_add_weapon
                        success, location = try_add_weapon(r)
                        if location == "storage":
                            m = m + " (신전 보관)"
                    
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
                    
                    # 분해 기록
                    from scripts import temple
                    temple.set_visited("blacksmith_decompose")
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