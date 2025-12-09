# scripts/temple.py
import pygame

# --- 신전 상태 ---
temple_state = {
    "menu_index": 0,  # 0: 대화, 1: 무기 수령, 2: 나가기
    "current_screen": "menu",  # menu, dialogue_menu, story_select, story, question_select, question, weapon_storage
    "dialogue_menu_index": 0,  # 0: 스토리, 1: 질문
    "story_select_index": 0,  # 스토리 선택 인덱스
    "story_index": 0,
    "story_page": 0,
    "question_select_index": 0,  # 질문 선택 인덱스
    "question_line": 0,
    "weapon_select_index": 0,
    "message": "",
    "message_timer": 0,
}

# --- 프롤로그 완료 여부 ---
prologue_completed = False

# --- 방문 기록 (질문 해금용) ---
visited_places = {
    "shop": False,
    "blacksmith": False,
    "dungeon": False,
    "shop_consumable": False,  # 상점에서 소비템 구매
    "blacksmith_decompose": False,  # 대장간에서 분해
    "boss_king_slime": False,  # 킹 슬라임 처치
    "boss_mutant_goblin": False,  # 뮤턴트 고블린 처치
    "boss_golden_king": False,  # 황금왕 처치
    "boss_hextech_golem": False,  # 마공학 골렘 처치
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
            "던전에서 답을 찾으라는 신관의 말이 떠오른다...",
            "신관이 말했다. '던전은 위험합니다. 무기가 필요할 것입니다.'",
            "하지만 줄 수 있는 무기가 없다고 한다.",
            "신전 구석에 버려진 나무 막대기가 눈에 들어왔다.",
            "...이거라도 들고 가야겠다."
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
    4: {
        "title": "4장: 마법사의 유산",
        "pages": [
            "마공학 골렘... 그것은 단순한 몬스터가 아니었다.",
            "마법과 기술의 결정체, 헥스텍의 힘이 깃든 인공 생명체.",
            "던전을 만든 마법사가 남긴 최후의 수호자였다.",
            "골렘의 코어에서 발견된 기록에는 이런 문구가 있었다.",
            "'내 연구의 끝에는 영원이 있다. 그리고 영원의 끝에는...'",
            "문장은 거기서 끊겨 있었다."
        ],
        "unlock_floor": 40
    },
}

# --- 대화 데이터 (방문/보스 해금) ---
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
    "shop_consumable": {
        "title": "소비 아이템에 대하여",
        "speaker": "신관",
        "lines": [
            "소비 아이템을 구매하셨군요.",
            "체력 물약은 전투 중 체력을 회복시켜 줍니다.",
            "작은 물약부터 큰 물약까지, 회복량이 다르니 상황에 맞게 사용하세요.",
            "수리 키트는 무기의 내구도를 회복시킵니다.",
            "무기가 부서지면 전투가 힘들어지니, 항상 여유분을 챙기세요."
        ],
        "unlock_key": "shop_consumable"
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
    "blacksmith_decompose": {
        "title": "광석에 대하여",
        "speaker": "신관",
        "lines": [
            "무기를 분해해 보셨군요.",
            "분해하면 무기에 깃든 광석을 추출할 수 있습니다.",
            "철광석은 가장 흔한 광석이고, 미스릴은 희귀한 광석입니다.",
            "오리하르콘은 영웅급 무기에서만 얻을 수 있는 귀한 광석이지요.",
            "전설급 무기에서는 아다만티움이라는 최고급 광석이 나옵니다.",
            "좋은 무기를 합성하려면 많은 광석이 필요합니다."
        ],
        "unlock_key": "blacksmith_decompose"
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
    "boss_king_slime": {
        "title": "킹 슬라임에 대하여",
        "speaker": "신관",
        "lines": [
            "킹 슬라임을 쓰러뜨리셨군요. 대단합니다.",
            "슬라임들은 원래 던전의 마력이 응집된 존재입니다.",
            "킹 슬라임은 그중에서도 가장 오래된 개체지요.",
            "오랜 세월 마력을 흡수하며 거대해진 것입니다.",
            "하지만 걱정 마십시오. 시간이 지나면 또 다른 킹 슬라임이 탄생합니다.",
            "던전은... 스스로를 재생하는 힘이 있으니까요."
        ],
        "unlock_key": "boss_king_slime"
    },
    "boss_mutant_goblin": {
        "title": "뮤턴트 고블린에 대하여",
        "speaker": "신관",
        "lines": [
            "뮤턴트 고블린을 쓰러뜨리셨군요.",
            "그 괴물은... 자연적으로 태어난 것이 아닙니다.",
            "누군가가 고블린에게 실험을 했습니다.",
            "던전의 마력과 금지된 연금술을 결합한 흔적이 보입니다.",
            "아마도 던전을 만든 마법사의 소행이겠지요.",
            "더 깊은 곳에는 더 끔찍한 실험의 결과물이 있을지도 모릅니다."
        ],
        "unlock_key": "boss_mutant_goblin"
    },
    "boss_golden_king": {
        "title": "황금왕에 대하여",
        "speaker": "신관",
        "lines": [
            "황금왕을... 해방시켜 주셨군요.",
            "그는 수백 년 전 이 땅을 다스리던 왕이었습니다.",
            "영원히 살고 싶었던 그는 던전의 마법사에게 손을 내밀었지요.",
            "마법사는 그에게 불사의 몸을 주었지만... 대가가 있었습니다.",
            "황금으로 변한 몸, 영원히 던전에 갇힌 영혼.",
            "당신 덕분에 그는 드디어 안식을 찾았을 것입니다. 감사합니다."
        ],
        "unlock_key": "boss_golden_king"
    },
    "boss_magolem": {
        "title": "마공학 골렘에 대하여",
        "speaker": "신관",
        "lines": [
            "마공학 골렘을 쓰러뜨리셨다고요...? 놀랍습니다.",
            "그것은 던전을 만든 마법사의 최고 걸작이었습니다.",
            "헥스텍... 마법과 기술을 융합한 금지된 학문이지요.",
            "마법사는 헥스텍으로 영원히 움직이는 생명체를 만들려 했습니다.",
            "마공학 골렘은 그 연구의 완성체... 혹은 실패작이었을지도 모릅니다.",
            "그 해머에 담긴 힘을 잘 사용하시길 바랍니다."
        ],
        "unlock_key": "boss_hextech_golem"
    },
}

# --- 하이패스 상태 ---
highpass_state = {
    "active": False,
    "select_index": 0,
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


def get_highpass_floors():
    """하이패스 가능한 층 목록 (1, 11, 21, 31...)"""
    floors = [1]  # 1층은 항상 가능
    for f in range(11, max_floor_reached + 1, 10):
        floors.append(f)
    return floors


def is_highpass_active():
    return highpass_state["active"]


def activate_highpass():
    global highpass_state
    highpass_state["active"] = True
    highpass_state["select_index"] = 0


def deactivate_highpass():
    global highpass_state
    highpass_state["active"] = False


def get_selected_highpass_floor():
    floors = get_highpass_floors()
    if highpass_state["select_index"] < len(floors):
        return floors[highpass_state["select_index"]]
    return 1


def wrap_text(text, font, max_width):
    """텍스트 줄바꿈 함수"""
    words = list(text)  # 한글은 글자 단위로 분리
    lines = []
    current_line = ""
    
    for char in words:
        test_line = current_line + char
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    
    if current_line:
        lines.append(current_line)
    
    return lines


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
        "story_select_index": 0,
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
    elif current_screen == "story_select":
        draw_story_select(screen, font_main, font_small, width, height)
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
    """대화 서브메뉴: 스토리, 대화"""
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


def draw_story_select(screen, font_main, font_small, width, height):
    """스토리 선택 화면 - 질문 선택과 동일한 스타일"""
    unlocked = get_unlocked_stories()
    
    # 중앙 팝업
    pw, ph = 400, 320
    px, py = (width - pw) // 2, (height - ph) // 2
    
    pygame.draw.rect(screen, (35, 50, 60), (px, py, pw, ph))
    pygame.draw.rect(screen, (100, 180, 220), (px, py, pw, ph), 3)
    
    # 제목
    title_font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else font_small
    title = title_font.render("스토리 선택", True, (150, 220, 255))
    screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 15))
    
    if not unlocked:
        no_s_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
        no_s_text = no_s_font.render("아직 해금된 스토리가 없습니다.", True, (180, 180, 180))
        screen.blit(no_s_text, (px + pw // 2 - no_s_text.get_width() // 2, py + ph // 2 - 30))
        no_s_text2 = no_s_font.render("던전을 탐험하세요.", True, (180, 180, 180))
        screen.blit(no_s_text2, (px + pw // 2 - no_s_text2.get_width() // 2, py + ph // 2 + 10))
        return
    
    # 스토리 목록 (스크롤)
    ly = py + 60
    item_font = pygame.font.Font(FONT_PATH, 20) if FONT_PATH else font_small
    
    visible = 5
    scroll_offset = max(0, min(temple_state["story_select_index"] - 2, len(unlocked) - visible))
    
    for i in range(visible):
        idx = scroll_offset + i
        if idx >= len(unlocked):
            break
        
        key, story = unlocked[idx]
        ir = pygame.Rect(px + 20, ly, pw - 40, 40)
        
        if idx == temple_state["story_select_index"]:
            pygame.draw.rect(screen, (50, 80, 100), ir)
            pygame.draw.rect(screen, (100, 180, 220), ir, 2)
            text_color = (255, 255, 255)
        else:
            text_color = (180, 180, 180)
        
        text = item_font.render(story["title"], True, text_color)
        screen.blit(text, (ir.x + 15, ir.y + 8))
        
        ly += 45
    
    # 위쪽 화살표
    arrow_x = px + pw // 2
    if scroll_offset > 0:
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, py + 52),
            (arrow_x - 8, py + 62),
            (arrow_x + 8, py + 62)
        ])
    
    # 아래쪽 화살표
    if scroll_offset + visible < len(unlocked):
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, py + ph - 35),
            (arrow_x - 8, py + ph - 45),
            (arrow_x + 8, py + ph - 45)
        ])


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
    
    # 페이지 내용 (줄바꿈 적용)
    content_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
    max_text_width = dialog_rect.width - 80
    lines = wrap_text(story["pages"][page], content_font, max_text_width)
    
    text_y = dialog_y + 55
    for line in lines:
        line_surface = content_font.render(line, True, (255, 255, 255))
        screen.blit(line_surface, (40, text_y))
        text_y += 32
    
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
    pw, ph = 400, 320
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
    
    # 대화 목록 (스크롤)
    ly = py + 60
    item_font = pygame.font.Font(FONT_PATH, 20) if FONT_PATH else font_small
    
    visible = 5
    scroll_offset = max(0, min(temple_state["question_select_index"] - 2, len(unlocked) - visible))
    
    for i in range(visible):
        idx = scroll_offset + i
        if idx >= len(unlocked):
            break
        
        key, question = unlocked[idx]
        ir = pygame.Rect(px + 20, ly, pw - 40, 40)
        
        if idx == temple_state["question_select_index"]:
            pygame.draw.rect(screen, (50, 80, 100), ir)
            pygame.draw.rect(screen, (100, 180, 220), ir, 2)
            text_color = (255, 255, 255)
        else:
            text_color = (180, 180, 180)
        
        text = item_font.render(question["title"], True, text_color)
        screen.blit(text, (ir.x + 15, ir.y + 8))
        
        ly += 45
    
    # 위쪽 화살표
    arrow_x = px + pw // 2
    if scroll_offset > 0:
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, py + 52),
            (arrow_x - 8, py + 62),
            (arrow_x + 8, py + 62)
        ])
    
    # 아래쪽 화살표
    if scroll_offset + visible < len(unlocked):
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, py + ph - 35),
            (arrow_x - 8, py + ph - 45),
            (arrow_x + 8, py + ph - 45)
        ])


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
    
    # 대사 (줄바꿈 적용)
    line_font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else font_small
    max_text_width = dialog_rect.width - 80  # 좌우 여백
    lines = wrap_text(question["lines"][line_idx], line_font, max_text_width)
    
    text_y = dialog_y + 55
    for line in lines:
        line_surface = line_font.render(line, True, (255, 255, 255))
        screen.blit(line_surface, (40, text_y))
        text_y += 32
    
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
                        temple_state["current_screen"] = "story_select"
                        temple_state["story_select_index"] = 0
                    elif temple_state["dialogue_menu_index"] == 1:  # 질문
                        temple_state["current_screen"] = "question_select"
                        temple_state["question_select_index"] = 0
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "menu"
            
            elif current_screen == "story_select":
                unlocked = get_unlocked_stories()
                if event.key == pygame.K_w:
                    if unlocked:
                        temple_state["story_select_index"] = (temple_state["story_select_index"] - 1) % len(unlocked)
                elif event.key == pygame.K_s:
                    if unlocked:
                        temple_state["story_select_index"] = (temple_state["story_select_index"] + 1) % len(unlocked)
                elif event.key == pygame.K_RETURN:
                    if unlocked:
                        temple_state["story_index"] = temple_state["story_select_index"]
                        temple_state["story_page"] = 0
                        temple_state["current_screen"] = "story"
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "dialogue_menu"
            
            elif current_screen == "story":
                unlocked = get_unlocked_stories()
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if unlocked:
                        story_key, story = unlocked[temple_state["story_index"]]
                        if temple_state["story_page"] < len(story["pages"]) - 1:
                            temple_state["story_page"] += 1
                        else:
                            # 프롤로그(스토리 0) 완료 시 나무막대기 지급
                            global prologue_completed
                            if story_key == 0 and not prologue_completed:
                                prologue_completed = True
                                from scripts.weapons import create_weapon
                                from scripts import inventory
                                wooden_stick = create_weapon("wooden_stick")
                                if wooden_stick:
                                    inventory.player_inventory["weapons"].append(wooden_stick)
                                    temple_state["message"] = "나무 막대기를 획득했습니다!"
                                    temple_state["message_timer"] = 0
                            
                            # 스토리 선택 화면으로 돌아가기
                            temple_state["current_screen"] = "story_select"
                            temple_state["story_page"] = 0
                    else:
                        temple_state["current_screen"] = "story_select"
                elif event.key == pygame.K_ESCAPE:
                    temple_state["current_screen"] = "story_select"
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


def draw_highpass(screen, font_main, font_small, width, height, font_path=None):
    """하이패스 선택 화면 그리기"""
    global FONT_PATH
    if font_path:
        FONT_PATH = font_path
    
    floors = get_highpass_floors()
    
    # 중앙 팝업
    pw, ph = 350, 300
    px, py = (width - pw) // 2, (height - ph) // 2
    
    pygame.draw.rect(screen, (35, 50, 60), (px, py, pw, ph))
    pygame.draw.rect(screen, (100, 180, 220), (px, py, pw, ph), 3)
    
    # 제목
    title_font = pygame.font.Font(FONT_PATH, 26) if FONT_PATH else font_small
    title = title_font.render("던전 입장", True, (150, 220, 255))
    screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 15))
    
    # 안내
    guide_font = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else font_small
    guide = guide_font.render("시작 층을 선택하세요", True, (180, 180, 180))
    screen.blit(guide, (px + pw // 2 - guide.get_width() // 2, py + 50))
    
    # 층 목록
    ly = py + 85
    item_font = pygame.font.Font(FONT_PATH, 22) if FONT_PATH else font_small
    
    visible = 5
    scroll_offset = max(0, min(highpass_state["select_index"] - 2, len(floors) - visible))
    
    for i in range(visible):
        idx = scroll_offset + i
        if idx >= len(floors):
            break
        
        floor = floors[idx]
        ir = pygame.Rect(px + 30, ly, pw - 60, 35)
        
        if idx == highpass_state["select_index"]:
            pygame.draw.rect(screen, (50, 80, 100), ir)
            pygame.draw.rect(screen, (100, 180, 220), ir, 2)
            text_color = (255, 255, 255)
        else:
            text_color = (180, 180, 180)
        
        floor_text = f"{floor}층"
        text = item_font.render(floor_text, True, text_color)
        screen.blit(text, (ir.x + ir.width // 2 - text.get_width() // 2, ir.y + 5))
        
        ly += 40
    
    # 위쪽 화살표
    arrow_x = px + pw // 2
    if scroll_offset > 0:
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, py + 78),
            (arrow_x - 8, py + 88),
            (arrow_x + 8, py + 88)
        ])
    
    # 아래쪽 화살표
    if scroll_offset + visible < len(floors):
        pygame.draw.polygon(screen, (150, 220, 255), [
            (arrow_x, py + ph - 35),
            (arrow_x - 8, py + ph - 45),
            (arrow_x + 8, py + ph - 45)
        ])


def handle_highpass_input(events, game_state, battle_start_func, player_name):
    """하이패스 입력 처리"""
    global highpass_state
    
    floors = get_highpass_floors()
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if floors:
                    highpass_state["select_index"] = (highpass_state["select_index"] - 1) % len(floors)
            elif event.key == pygame.K_s:
                if floors:
                    highpass_state["select_index"] = (highpass_state["select_index"] + 1) % len(floors)
            elif event.key == pygame.K_RETURN:
                # 선택한 층으로 던전 시작
                selected_floor = get_selected_highpass_floor()
                deactivate_highpass()
                
                # 던전 시작 (선택한 층에서)
                battle_start_func(game_state, player_name, start_floor=selected_floor)
                return
            elif event.key == pygame.K_ESCAPE:
                deactivate_highpass()
                game_state["state"] = "town"