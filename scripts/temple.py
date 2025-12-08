# scripts/temple.py
import pygame

# --- 신전 상태 ---
temple_state = {
    "menu_index": 0,  # 0: 대화, 1: 무기 수령, 2: 나가기
    "current_screen": "menu",  # menu, dialogue_menu, story, question_select, question, weapon_storage
    "dialogue_menu_index": 0,  # 0: 스토리, 1: 질문
    "story_index": 0,
    "story_page": 0,
    "question_select_index": 0,  # 질문 선택 인덱스
    "question_line": 0,
    "weapon_select_index": 0,
    "message": "",
    "message_timer": 0,
}

# --- 방문 기록 (질문 해금용) ---
visited_places = {
    "shop": False,
    "blacksmith": False,
    "dungeon": False,
}

# --- 무기 보관함 ---
weapon_storage = []

# --- 스토리 데이터 (층 해금) ---
STORY_DATA = {
    0: {
        "title": "프롤로그: 시작",
        "pages": [
            "당신은 눈을 떴다. 낯선 마을, 낯선 하늘...",
            "기억이 없다. 이름조차 희미하게 느껴진다.",
            "마을 사람들은 당신을 '이방인'이라 불렀다.",
            "던전에서 답을 찾으라는 신관의 말이 떠오른다..."
        ],
        "unlock_floor": 0
    },
    1: {
        "title": "1장: 슬라임의 왕",
        "pages": [
            "킹 슬라임을 처치했다.",
            "슬라임들은 왜 던전에 있는 것일까?",
            "신관이 말했다. '그들도 한때는 평범한 존재였다'고...",
            "던전의 마력이 그들을 변화시킨 것이다."
        ],
        "unlock_floor": 10
    },
    2: {
        "title": "2장: 고블린의 비밀",
        "pages": [
            "뮤턴트 고블린... 그 거대한 몸체는 자연스럽지 않았다.",
            "누군가가 고블린들을 실험한 흔적이 보인다.",
            "던전 깊은 곳에 무언가가 있다.",
            "진실에 가까워지고 있다는 느낌이 든다..."
        ],
        "unlock_floor": 20
    },
    3: {
        "title": "3장: 황금왕의 저주",
        "pages": [
            "황금왕은 한때 위대한 왕이었다고 한다.",
            "영원한 삶을 원했던 그는 던전의 힘에 손을 댔다.",
            "결국 그는 저주받은 불사의 존재가 되었다.",
            "당신의 손에 의해 해방된 황금왕... 그가 남긴 말이 마음에 남는다.",
            "'더 깊이... 진실은 더 깊은 곳에...'"
        ],
        "unlock_floor": 30
    },
}

# --- 질문 데이터 (방문 해금) ---
QUESTION_DATA = {
    "shop": {
        "title": "상점에 대하여",
        "speaker": "신관",
        "lines": [
            "상점의 주인을 만나셨군요.",
            "그는 먼 나라에서 온 상인입니다.",
            "젊은 시절, 모험가였다고 하더군요.",
            "던전에서 큰 부상을 입고 은퇴한 후 이곳에 정착했습니다.",
            "그래서인지 모험가들에게 특별한 애정을 가지고 있지요.",
            "좋은 물건이 필요하시다면 그에게 가보십시오."
        ],
        "unlock_key": "shop"
    },
    "blacksmith": {
        "title": "대장간에 대하여",
        "speaker": "신관",
        "lines": [
            "대장간에 다녀오셨군요.",
            "원래 그곳에는 뛰어난 대장장이가 있었습니다.",
            "하지만 어느 날 갑자기 사라져버렸지요.",
            "던전 깊은 곳에서 전설의 광석을 찾겠다며 떠났다는 소문이 있습니다.",
            "지금은 그가 남긴 도구들로 셀프 대장간이 운영되고 있습니다.",
            "조금 불편하시겠지만, 그래도 쓸만할 겁니다."
        ],
        "unlock_key": "blacksmith"
    },
    "dungeon": {
        "title": "던전에 대하여",
        "speaker": "신관",
        "lines": [
            "던전에 다녀오셨군요. 무사하셔서 다행입니다.",
            "그 던전은... 자연적으로 생긴 것이 아닙니다.",
            "오래전, 강력한 마법사가 만들어낸 것이라 전해집니다.",
            "그는 영원한 삶을 연구했고, 던전은 그 실험의 산물이지요.",
            "던전 깊은 곳에는 아직도 그의 비밀이 잠들어 있다고 합니다.",
            "조심하십시오. 던전은 들어가는 자를 시험합니다."
        ],
        "unlock_key": "dungeon"
    },
}

# --- 최대 진행 층 ---
max_floor_reached = 0

# --- 폰트 경로 ---
FONT_PATH = None


def set_visited(place):
    """장소 방문 기록"""
    global visited_places
    if place in visited_places:
        visited_places[place] = True


def get_max_floor_reached():
    return max_floor_reached


def set_max_floor_reached(floor):
    global max_floor_reached
    if floor > max_floor_reached:
        max_floor_reached = floor


def add_weapon_to_storage(weapon):
    """무기를 보관함에 추가"""
    global weapon_storage
    weapon_storage.append(weapon)


def get_unlocked_stories():
    """해금된 스토리 목록"""
    unlocked = []
    for idx, story in STORY_DATA.items():
        if max_floor_reached >= story["unlock_floor"]:
            unlocked.append((idx, story))
    return unlocked


def get_unlocked_questions():
    """해금된 질문 목록"""
    unlocked = []
    for key, question in QUESTION_DATA.items():
        if visited_places.get(question["unlock_key"], False):
            unlocked.append((key, question))
    return unlocked


def reset_temple_state():
    """신전 상태 초기화"""
    global temple_state
    temple_state = {
        "menu_index": 0,
        "current_screen": "menu",
        "dialogue_menu_index": 0,
        "story_index": 0,
        "story_page": 0,
        "question_select_index": 0,
        "question_line": 0,
        "weapon_select_index": 0,
        "message": "",
        "message_timer": 0,
    }


def draw_temple(screen, font_main, font_small, width, height, game_state, dt, font_path=None):
    """신전 화면 그리기"""
    global FONT_PATH
    if font_path:
        FONT_PATH = font_path
    
    # 메시지 타이머
    if temple_state["message"] and dt > 0:
        temple_state["message_timer"] += dt
        if temple_state["message_timer"] > 1.5:
            temple_state["message"] = ""
            temple_state["message_timer"] = 0
    
    # 배경
    try:
        bg = pygame.image.load("resources/png/building/temple_inside.png").convert()
        bg = pygame.transform.scale(bg, (width, height))
        screen.blit(bg, (0, 0))
    except:
        screen.fill((240, 220, 180))
    
    current_screen = temple_state["current_screen"]
    
    if current_screen == "menu":
        draw_menu(screen, font_main, font_small, width, height)
    elif current_screen == "dialogue_menu":
        draw_dialogue_menu(screen, font_main, font_small, width, height)
    elif current_screen == "story":
        draw_story(screen, font_main, font_small, width, height)
    elif current_screen == "question_select":
        draw_question_select(screen, font_main, font_small, width, height)
    elif current_screen == "question":
        draw_question(screen, font_main, font_small, width, height)
    elif current_screen == "weapon_storage":
        draw_weapon_storage(screen, font_main, font_small, width, height)


def draw_menu(screen, font_main, font_small, width, height):
    """메인 메뉴: 대화, 무기 수령, 나가기"""
    menu_items = ["대화", "무기 수령", "나가기"]
    
    # 대화 박스
    dialog_height = 179
    dialog_y = height - dialog_height - 20
    dialog_rect = pygame.Rect(20, dialog_y, width - 40, dialog_height)
    
    dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
    dialog_surface.set_alpha(220)
    dialog_surface.fill((40, 30, 20))
    screen.blit(dialog_surface, dialog_rect)
    pygame.draw.rect(screen, (200, 180, 150), dialog_rect, 4)
    
    # NPC 대사
    npc_text = [
        "빛의 신전에 오신 것을 환영합니다.",
        "무엇을 도와드릴까요?",
    ]
    
    text_font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else font_small
    text_y = dialog_y + 30
    for line in npc_text:
        text = text_font.render(line, True, (255, 255, 255))
        screen.blit(text, (40, text_y))
        text_y += 40
    
    # 버튼들
    button_width = 180
    button_height = 45
    button_gap = 10
    button_x = dialog_rect.right - button_width - 20
    
    total_buttons_height = button_height * 3 + button_gap * 2
    border_width = 4
    usable_height = dialog_height - border_width * 2
    button_start_y = dialog_y + border_width + (usable_height - total_buttons_height) // 2
    
    for i, item in enumerate(menu_items):
        button_y = button_start_y + i * (button_height + button_gap)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if i == temple_state["menu_index"]:
            bg_color = (50, 120, 150)
            border_color = (100, 180, 220)
            text_color = (255, 255, 255)
            btn_border_width = 3
        else:
            bg_color = (30, 60, 80)
            border_color = (60, 100, 120)
            text_color = (200, 200, 200)
            btn_border_width = 2
        
        pygame.draw.rect(screen, bg_color, button_rect)
        pygame.draw.rect(screen, border_color, button_rect, btn_border_width)
        
        btn_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
        
        display_text = item
        if i == 1 and len(weapon_storage) > 0:
            display_text = f"{item} ({len(weapon_storage)})"
        
        btn_text = btn_font.render(display_text, True, text_color)
        text_rect = btn_text.get_rect(center=button_rect.center)
        screen.blit(btn_text, text_rect)


def draw_dialogue_menu(screen, font_main, font_small, width, height):
    """대화 서브메뉴: 스토리, 질문"""
    menu_items = ["스토리", "질문"]
    
    # 대화 박스
    dialog_height = 179
    dialog_y = height - dialog_height - 20
    dialog_rect = pygame.Rect(20, dialog_y, width - 40, dialog_height)
    
    dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
    dialog_surface.set_alpha(220)
    dialog_surface.fill((40, 30, 20))
    screen.blit(dialog_surface, dialog_rect)
    pygame.draw.rect(screen, (200, 180, 150), dialog_rect, 4)
    
    # NPC 대사
    npc_text = [
        "어떤 이야기를 듣고 싶으십니까?",
    ]
    
    text_font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else font_small
    text_y = dialog_y + 50
    for line in npc_text:
        text = text_font.render(line, True, (255, 255, 255))
        screen.blit(text, (40, text_y))
        text_y += 40
    
    # 버튼들 (2개)
    button_width = 180
    button_height = 45
    button_gap = 10
    button_x = dialog_rect.right - button_width - 20
    
    total_buttons_height = button_height * 2 + button_gap
    border_width = 4
    usable_height = dialog_height - border_width * 2
    button_start_y = dialog_y + border_width + (usable_height - total_buttons_height) // 2
    
    for i, item in enumerate(menu_items):
        button_y = button_start_y + i * (button_height + button_gap)
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if i == temple_state["dialogue_menu_index"]:
            bg_color = (50, 120, 150)
            border_color = (100, 180, 220)
            text_color = (255, 255, 255)
            btn_border_width = 3
        else:
            bg_color = (30, 60, 80)
            border_color = (60, 100, 120)
            text_color = (200, 200, 200)
            btn_border_width = 2
        
        pygame.draw.rect(screen, bg_color, button_rect)
        pygame.draw.rect(screen, border_color, button_rect, btn_border_width)
        
        btn_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
        btn_text = btn_font.render(item, True, text_color)
        text_rect = btn_text.get_rect(center=button_rect.center)
        screen.blit(btn_text, text_rect)


def draw_story(screen, font_main, font_small, width, height):
    """스토리 화면"""
    unlocked = get_unlocked_stories()
    
    # 대화 박스
    dialog_height = 179
    dialog_y = height - dialog_height - 20
    dialog_rect = pygame.Rect(20, dialog_y, width - 40, dialog_height)
    
    dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
    dialog_surface.set_alpha(220)
    dialog_surface.fill((40, 30, 20))
    screen.blit(dialog_surface, dialog_rect)
    pygame.draw.rect(screen, (200, 180, 150), dialog_rect, 4)
    
    if not unlocked:
        text_font = pygame.font.Font(FONT_PATH, 26) if FONT_PATH else font_small
        text = text_font.render("아직 해금된 스토리가 없습니다.", True, (200, 200, 200))
        screen.blit(text, (40, dialog_y + 70))
        
        # 엔터 화살표
        draw_enter_arrow(screen, dialog_rect, dialog_y, dialog_height)
        return
    
    story_idx = temple_state["story_index"]
    if story_idx >= len(unlocked):
        story_idx = 0
        temple_state["story_index"] = 0
    
    _, story = unlocked[story_idx]
    page = temple_state["story_page"]
    
    if page >= len(story["pages"]):
        page = 0
        temple_state["story_page"] = 0
    
    # 제목
    title_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
    title = title_font.render(story["title"], True, (100, 200, 220))
    screen.blit(title, (40, dialog_y + 20))
    
    # 페이지 내용
    content_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
    content = content_font.render(story["pages"][page], True, (255, 255, 255))
    screen.blit(content, (40, dialog_y + 60))
    
    # 페이지 표시
    info_font = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else font_small
    page_text = info_font.render(f"{page + 1} / {len(story['pages'])}", True, (150, 150, 150))
    screen.blit(page_text, (dialog_rect.right - page_text.get_width() - 25, dialog_y + dialog_height - 35))
    
    # 엔터 화살표
    draw_enter_arrow(screen, dialog_rect, dialog_y, dialog_height)


def draw_question_select(screen, font_main, font_small, width, height):
    """질문 선택 화면 - 대장간 스타일 팝업"""
    unlocked = get_unlocked_questions()
    
    # 중앙 팝업
    pw, ph = 400, 300
    px, py = (width - pw) // 2, (height - ph) // 2
    
    pygame.draw.rect(screen, (35, 50, 60), (px, py, pw, ph))
    pygame.draw.rect(screen, (100, 180, 220), (px, py, pw, ph), 3)
    
    # 제목
    title_font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else font_small
    title = title_font.render("질문 선택", True, (150, 220, 255))
    screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 15))
    
    if not unlocked:
        no_q_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
        no_q_text = no_q_font.render("아직 해금된 질문이 없습니다.", True, (180, 180, 180))
        screen.blit(no_q_text, (px + pw // 2 - no_q_text.get_width() // 2, py + ph // 2 - 30))
        no_q_text2 = no_q_font.render("마을을 둘러보세요.", True, (180, 180, 180))
        screen.blit(no_q_text2, (px + pw // 2 - no_q_text2.get_width() // 2, py + ph // 2 + 10))
        return
    
    # 질문 목록
    ly = py + 60
    item_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
    
    for i, (key, question) in enumerate(unlocked):
        ir = pygame.Rect(px + 20, ly, pw - 40, 45)
        
        if i == temple_state["question_select_index"]:
            pygame.draw.rect(screen, (50, 80, 100), ir)
            pygame.draw.rect(screen, (100, 180, 220), ir, 2)
            text_color = (255, 255, 255)
        else:
            text_color = (180, 180, 180)
        
        text = item_font.render(question["title"], True, text_color)
        screen.blit(text, (ir.x + 15, ir.y + 10))
        
        ly += 50


def draw_question(screen, font_main, font_small, width, height):
    """질문 대화 화면"""
    unlocked = get_unlocked_questions()
    
    # 대화 박스
    dialog_height = 179
    dialog_y = height - dialog_height - 20
    dialog_rect = pygame.Rect(20, dialog_y, width - 40, dialog_height)
    
    dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
    dialog_surface.set_alpha(220)
    dialog_surface.fill((40, 30, 20))
    screen.blit(dialog_surface, dialog_rect)
    pygame.draw.rect(screen, (200, 180, 150), dialog_rect, 4)
    
    if not unlocked:
        return
    
    q_idx = temple_state["question_select_index"]
    if q_idx >= len(unlocked):
        q_idx = 0
        temple_state["question_select_index"] = 0
    
    _, question = unlocked[q_idx]
    line_idx = temple_state["question_line"]
    
    if line_idx >= len(question["lines"]):
        line_idx = 0
        temple_state["question_line"] = 0
    
    # 제목
    title_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
    title = title_font.render(question["title"], True, (100, 200, 220))
    screen.blit(title, (40, dialog_y + 20))
    
    # 대사
    line_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
    line = line_font.render(question["lines"][line_idx], True, (255, 255, 255))
    screen.blit(line, (40, dialog_y + 60))
    
    # 페이지 표시
    info_font = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else font_small
    page_text = info_font.render(f"{line_idx + 1} / {len(question['lines'])}", True, (150, 150, 150))
    screen.blit(page_text, (dialog_rect.right - page_text.get_width() - 25, dialog_y + dialog_height - 35))
    
    # 엔터 화살표
    draw_enter_arrow(screen, dialog_rect, dialog_y, dialog_height)


def draw_enter_arrow(screen, dialog_rect, dialog_y, dialog_height):
    """엔터 유도 화살표 - 페이지 표시 왼쪽"""
    arrow_x = dialog_rect.right - 100
    arrow_y = dialog_y + dialog_height - 40
    
    # 아래 화살표
    pygame.draw.polygon(screen, (255, 255, 255), [
        (arrow_x, arrow_y + 12),
        (arrow_x - 8, arrow_y),
        (arrow_x + 8, arrow_y)
    ])


def draw_weapon_storage(screen, font_main, font_small, width, height):
    """무기 보관함 화면"""
    from scripts import inventory
    
    grade_colors = {
        "일반": (200, 200, 200),
        "희귀": (100, 150, 255),
        "영웅": (200, 100, 255),
        "전설": (255, 200, 50),
    }
    
    # 보유칸만 체크
    weapons_count = len(inventory.player_inventory["weapons"])
    max_weapons = inventory.inventory_state["max_inventory_slots"]
    can_receive = weapons_count < max_weapons
    
    # 중앙 팝업
    pw, ph = 450, 400
    px, py = (width - pw) // 2, (height - ph) // 2
    
    pygame.draw.rect(screen, (35, 50, 60), (px, py, pw, ph))
    pygame.draw.rect(screen, (100, 180, 220), (px, py, pw, ph), 3)
    
    # 제목
    title_font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else font_small
    title = title_font.render("무기 보관함", True, (150, 220, 255))
    screen.blit(title, (px + 20, py + 15))
    
    # 보유칸 표시
    space_font = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else font_small
    space_color = (150, 255, 150) if can_receive else (255, 100, 100)
    space_text = space_font.render(f"보유칸: {weapons_count}/{max_weapons}", True, space_color)
    screen.blit(space_text, (px + pw - space_text.get_width() - 20, py + 20))
    
    if not weapon_storage:
        no_weapon_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
        no_weapon_text = no_weapon_font.render("보관된 무기가 없습니다", True, (180, 180, 180))
        screen.blit(no_weapon_text, (px + pw // 2 - no_weapon_text.get_width() // 2, 
                                      py + ph // 2 - no_weapon_text.get_height() // 2))
        return
    
    # 스크롤 화살표
    arrow_x = px + pw // 2
    arrow_up_y = py + 50
    
    ly = py + 70
    visible = 7
    selected_slot = 3
    
    scroll_offset = max(0, min(temple_state["weapon_select_index"] - selected_slot, len(weapon_storage) - visible))
    
    item_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
    
    for i in range(visible):
        idx = scroll_offset + i
        ir = pygame.Rect(px + 15, ly, pw - 30, 38)
        
        if idx < len(weapon_storage):
            w = weapon_storage[idx]
            
            if idx == temple_state["weapon_select_index"]:
                pygame.draw.rect(screen, (50, 80, 100), ir)
                pygame.draw.rect(screen, (100, 180, 220), ir, 2)
            
            color = grade_colors.get(w.grade, (200, 200, 200))
            level = getattr(w, 'upgrade_level', 0)
            name = f"+{level} {w.name}" if level > 0 else w.name
            screen.blit(item_font.render(name, True, color), (ir.x + 10, ir.y + 8))
            screen.blit(item_font.render(f"[{w.grade}]", True, color), (ir.right - 80, ir.y + 8))
        
        ly += 42
    
    # 위쪽 화살표
    if scroll_offset > 0:
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, arrow_up_y),
            (arrow_x - 10, arrow_up_y + 12),
            (arrow_x + 10, arrow_up_y + 12)
        ])
    
    # 아래쪽 화살표
    if scroll_offset + visible < len(weapon_storage):
        arrow_down_y = py + ph - 60
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, arrow_down_y + 12),
            (arrow_x - 10, arrow_down_y),
            (arrow_x + 10, arrow_down_y)
        ])
    
    # 메시지 표시
    if temple_state["message"]:
        msg_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
        if "가득" in temple_state["message"]:
            msg_color = (255, 100, 100)
        else:
            msg_color = (100, 255, 150)
        msg_text = msg_font.render(temple_state["message"], True, msg_color)
        screen.blit(msg_text, (px + pw // 2 - msg_text.get_width() // 2, py + ph - 45))


def handle_temple_input(events, game_state):
    """신전 입력 처리"""
    global temple_state, weapon_storage
    
    current_screen = temple_state["current_screen"]
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if current_screen == "menu":
                if event.key == pygame.K_w:
                    temple_state["menu_index"] = (temple_state["menu_index"] - 1) % 3
                elif event.key == pygame.K_s:
                    temple_state["menu_index"] = (temple_state["menu_index"] + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if temple_state["menu_index"] == 0:  # 대화
                        temple_state["current_screen"] = "dialogue_menu"
                        temple_state["dialogue_menu_index"] = 0
                    elif temple_state["menu_index"] == 1:  # 무기 수령
                        temple_state["current_screen"] = "weapon_storage"
                        temple_state["weapon_select_index"] = 0
                    elif temple_state["menu_index"] == 2:  # 나가기
                        reset_temple_state()
                        game_state["state"] = "town"
                elif event.key == pygame.K_ESCAPE:
                    reset_temple_state()
                    game_state["state"] = "town"
            
            elif current_screen == "dialogue_menu":
                if event.key == pygame.K_w:
                    temple_state["dialogue_menu_index"] = (temple_state["dialogue_menu_index"] - 1) % 2
                elif event.key == pygame.K_s:
                    temple_state["dialogue_menu_index"] = (temple_state["dialogue_menu_index"] + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if temple_state["dialogue_menu_index"] == 0:  # 스토리
                        temple_state["current_screen"] = "story"
                        temple_state["story_index"] = 0
                        temple_state["story_page"] = 0
                    elif temple_state["dialogue_menu_index"] == 1:  # 질문
                        temple_state["current_screen"] = "question_select"
                        temple_state["question_select_index"] = 0
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "menu"
            
            elif current_screen == "story":
                unlocked = get_unlocked_stories()
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if unlocked:
                        _, story = unlocked[temple_state["story_index"]]
                        if temple_state["story_page"] < len(story["pages"]) - 1:
                            temple_state["story_page"] += 1
                        else:
                            # 다음 스토리 or 돌아가기
                            if temple_state["story_index"] < len(unlocked) - 1:
                                temple_state["story_index"] += 1
                                temple_state["story_page"] = 0
                            else:
                                temple_state["current_screen"] = "dialogue_menu"
                                temple_state["story_page"] = 0
                    else:
                        temple_state["current_screen"] = "dialogue_menu"
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "dialogue_menu"
                    temple_state["story_page"] = 0
            
            elif current_screen == "question_select":
                unlocked = get_unlocked_questions()
                if event.key == pygame.K_w:
                    if unlocked:
                        temple_state["question_select_index"] = (temple_state["question_select_index"] - 1) % len(unlocked)
                elif event.key == pygame.K_s:
                    if unlocked:
                        temple_state["question_select_index"] = (temple_state["question_select_index"] + 1) % len(unlocked)
                elif event.key == pygame.K_RETURN:
                    if unlocked:
                        temple_state["current_screen"] = "question"
                        temple_state["question_line"] = 0
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "dialogue_menu"
            
            elif current_screen == "question":
                unlocked = get_unlocked_questions()
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if unlocked:
                        _, question = unlocked[temple_state["question_select_index"]]
                        if temple_state["question_line"] < len(question["lines"]) - 1:
                            temple_state["question_line"] += 1
                        else:
                            # 질문 끝 -> 질문 선택으로 돌아가기
                            temple_state["current_screen"] = "question_select"
                            temple_state["question_line"] = 0
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "question_select"
                    temple_state["question_line"] = 0
            
            elif current_screen == "weapon_storage":
                if event.key == pygame.K_w:
                    if weapon_storage:
                        temple_state["weapon_select_index"] = (temple_state["weapon_select_index"] - 1) % len(weapon_storage)
                elif event.key == pygame.K_s:
                    if weapon_storage:
                        temple_state["weapon_select_index"] = (temple_state["weapon_select_index"] + 1) % len(weapon_storage)
                elif event.key == pygame.K_RETURN:
                    from scripts import inventory
                    
                    weapons_count = len(inventory.player_inventory["weapons"])
                    max_weapons = inventory.inventory_state["max_inventory_slots"]
                    
                    if weapons_count >= max_weapons:
                        temple_state["message"] = "인벤토리가 가득 찼습니다!"
                        temple_state["message_timer"] = 0
                        return
                    
                    if not weapon_storage:
                        return
                    
                    select_idx = temple_state["weapon_select_index"]
                    weapon = weapon_storage.pop(select_idx)
                    inventory.player_inventory["weapons"].append(weapon)
                    
                    temple_state["message"] = f"{weapon.name} 수령!"
                    temple_state["message_timer"] = 0
                    
                    if temple_state["weapon_select_index"] >= len(weapon_storage):
                        temple_state["weapon_select_index"] = max(0, len(weapon_storage) - 1)
                    return
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "menu"