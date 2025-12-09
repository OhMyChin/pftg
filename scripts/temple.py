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
    "boss_rich_king": False,  # 황금왕 처치
    "boss_hextech_golem": False,  # 마공학 골렘 처치
}

# --- 무기 보관함 ---
weapon_storage = []

# --- 스토리 데이터 (층 해금) ---
STORY_DATA = {
    0: {
        "title": "프롤로그: 이방인",
        "pages": [
            "...어디지, 여기는?",
            "눈을 떴을 때, 낯선 하늘이 보였다.",
            "기억이 없다. 이름도, 어디서 왔는지도...",
            "정처없이 헤매다 도착한 곳은 작은 마을의 신전이었다.",
            "신전의 사제가 다가왔다.",
            "'기억의 사제'라 불리는 그는 부드러운 목소리로 말했다.",
            "\"이방인이여, 당신이 기억을 잃은 이유를 알고 있습니다.\"",
            "\"이 세계 '메모리아'에 어둠의 신이 나타났습니다.\"",
            "\"그의 힘이 몬스터들을 폭주시키고, 세계의 균형을 무너뜨리고 있지요.\"",
            "\"저 역시 그 영향으로 힘을 잃었습니다.\"",
            "\"만약 당신이 어둠의 신을 물리쳐 준다면...\"",
            "\"제 힘이 돌아왔을 때, 당신의 기억을 되찾아 드리겠습니다.\"",
            "던전으로 향해야 한다. 하지만 무기가 없다.",
            "사제는 미안한 표정을 지었다.",
            "\"드릴 수 있는 무기가 없어 죄송합니다...\"",
            "신전 구석에 버려진 나무 막대기가 눈에 들어왔다.",
            "...이거라도 들고 가야겠다."
        ],
        "unlock_floor": 0
    },
    1: {
        "title": "1장: 여정의 시작",
        "pages": [
            "킹 슬라임을 쓰러뜨렸다.",
            "던전의 첫 번째 지배자... 생각보다 강했다.",
            "하지만 이건 시작에 불과하다.",
            "던전은 깊고, 어둠의 기운은 아래로 갈수록 짙어진다.",
            "기억을 되찾기 위해... 더 깊이 나아가야 한다."
        ],
        "unlock_floor": 10
    },
    2: {
        "title": "2장: 강해지는 어둠",
        "pages": [
            "뮤턴트 고블린을 쓰러뜨렸다.",
            "신전으로 돌아오자, 기억의 사제의 표정이 어두웠다.",
            "\"이상합니다... 어둠의 힘이 오히려 강해지고 있어요.\"",
            "\"보스를 쓰러뜨리면 약해져야 하는데...\"",
            "무언가 이상하다. 보스를 잡을수록 강해지는 어둠이라니.",
            "의문을 품은 채, 다시 던전으로 향했다."
        ],
        "unlock_floor": 20
    },
    3: {
        "title": "3장: 던전의 비밀",
        "pages": [
            "황금왕을 쓰러뜨렸다.",
            "쓰러지기 직전, 황금왕이 의미심장한 말을 남겼다.",
            "\"...어리석은 자여... 너는 아무것도 모르는구나...\"",
            "\"어둠의 신이 우리를 폭주시킨 것은 사실이다...\"",
            "\"하지만... 그가 우리를 이 던전에 가둔 이유가 있다...\"",
            "황금왕의 말이 머릿속을 맴돈다.",
            "어둠의 신은 왜 몬스터들을 던전에 가뒀을까?",
            "단순히 세상을 혼란에 빠뜨리려는 것이라면...",
            "가두지 않고 풀어놓는 것이 더 효과적이지 않았을까?"
        ],
        "unlock_floor": 30
    },
    4: {
        "title": "4장: 억제된 힘",
        "pages": [
            "마공학 골렘을 쓰러뜨렸다.",
            "던전의 최하층에 가까워질수록 이상한 느낌이 든다.",
            "어둠의 힘이... 억제되고 있다?",
            "마치 누군가가 일부러 힘을 막고 있는 것 같은...",
            "기억의 사제에게 이 사실을 전하자, 그는 놀란 표정을 지었다.",
            "\"그렇다면... 어둠의 신은 단순한 적이 아닐지도...\"",
            "\"던전 최심층에서 진실을 확인해야 할 것 같습니다.\"",
            "모든 의문의 답이 그곳에 있다.",
            "어둠의 신... 그의 정체는 무엇인가?"
        ],
        "unlock_floor": 40
    },
    5: {
        "title": "에필로그: 새로운 시작",
        "pages": [
            "당신은 해냈습니다.",
            "어둠의 신... 아니, '옛 용사'를 쓰러뜨리고 돌아왔습니다.",
            "기억의 사제가 따뜻한 눈으로 당신을 맞이합니다.",
            "\"정말... 고생 많으셨습니다.\"",
            "\"모든 진실을 알게 되셨군요.\"",
            "\"어둠의 신은... 원래 이 세계를 지키던 용사였습니다.\"",
            "\"메모리아에 어둠의 힘이 밀려왔을 때...\"",
            "\"그는 자신을 희생하여 그 힘을 던전에 가뒀지요.\"",
            "\"하지만 오랜 세월 어둠과 싸우다, 결국 물들고 말았습니다.\"",
            "\"그래서 마지막 수단으로... 자신의 기억 일부를 분리해\"",
            "\"자신을 쓰러뜨릴 수 있는 용사로 소환한 것입니다.\"",
            "\"...그게 바로 당신이었습니다.\"",
            "사제가 잠시 눈을 감았다 뜹니다.",
            "\"약속대로, 당신의 기억을 되돌려 드리겠습니다.\"",
            "따스한 빛이 당신을 감싸고...",
            "잃어버렸던 기억들이 스쳐 지나갑니다.",
            "당신의 이름, 고향, 소중한 사람들...",
            "그리고... '옛 용사'와 함께했던 기억들.",
            "\"이제 당신은 선택할 수 있습니다.\"",
            "\"원래 세계로 돌아갈 수도, 이곳에 남을 수도 있습니다.\"",
            "\"어느 쪽을 선택하든... 당신은 메모리아의 영웅입니다.\"",
            "사제가 미소 짓습니다.",
            "\"언제든 찾아와 주십시오. 당신의 이야기는 전설이 될 것입니다.\"",
            "어둠이 걷힌 메모리아의 하늘은...",
            "그 어느 때보다 맑고 푸르다."
        ],
        "unlock_floor": 45
    },
}

# --- 대화 데이터 (방문/보스 해금) ---
QUESTION_DATA = {
    "shop": {
        "title": "상점에 대하여",
        "speaker": "기억의 사제",
        "lines": [
            "상점의 주인을 만나셨군요.",
            "그는 먼 나라에서 온 상인입니다.",
            "젊은 시절, 모험가였다고 하더군요.",
            "어둠의 신이 나타나기 전... 던전에서 큰 부상을 입고 은퇴했답니다.",
            "그래서인지 모험가들에게 특별한 애정을 가지고 있지요.",
            "좋은 물건이 필요하시다면 그에게 가보십시오."
        ],
        "unlock_key": "shop"
    },
    "shop_consumable": {
        "title": "소비 아이템에 대하여",
        "speaker": "기억의 사제",
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
        "speaker": "기억의 사제",
        "lines": [
            "대장간에 다녀오셨군요.",
            "원래 그곳에는 뛰어난 대장장이가 있었습니다.",
            "하지만 어둠의 신이 나타난 후... 갑자기 사라져버렸지요.",
            "던전 깊은 곳에서 전설의 광석을 찾겠다며 떠났다는 소문이 있습니다.",
            "지금은 그가 남긴 도구들로 셀프 대장간이 운영되고 있습니다.",
            "조금 불편하시겠지만, 그래도 쓸만할 겁니다."
        ],
        "unlock_key": "blacksmith"
    },
    "blacksmith_decompose": {
        "title": "광석에 대하여",
        "speaker": "기억의 사제",
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
        "speaker": "기억의 사제",
        "lines": [
            "던전에 다녀오셨군요. 무사하셔서 다행입니다.",
            "그 던전은... 어둠의 신이 나타난 후 생겨났습니다.",
            "폭주한 몬스터들이 그 안에 갇혀 있지요.",
            "이상한 점은... 몬스터들이 던전 밖으로 나오지 못한다는 것입니다.",
            "마치 누군가가 일부러 가둬놓은 것처럼요.",
            "조심하십시오. 던전 깊은 곳에는 더 강한 존재들이 있습니다."
        ],
        "unlock_key": "dungeon"
    },
    "boss_king_slime": {
        "title": "슬라임에 대하여",
        "speaker": "기억의 사제",
        "lines": [
            "킹 슬라임을 쓰러뜨리셨군요. 대단합니다.",
            "슬라임들은 원래 메모리아의 순수한 마력이 응집된 존재입니다.",
            "본래는 온순하고 해를 끼치지 않았지요.",
            "하지만 어둠의 힘에 의해 폭주하게 되었습니다.",
            "킹 슬라임은 그중에서도 가장 오래된 개체...",
            "아마도 무리를 지키려다 가장 먼저 어둠에 물든 것일 겁니다."
        ],
        "unlock_key": "boss_king_slime"
    },
    "boss_mutant_goblin": {
        "title": "고블린에 대하여",
        "speaker": "기억의 사제",
        "lines": [
            "뮤턴트 고블린을 쓰러뜨리셨군요.",
            "고블린들은 원래 작은 부족 사회를 이루며 살던 종족입니다.",
            "영리하고, 나름의 문화도 가지고 있었지요.",
            "하지만 어둠의 힘이 그들을 변이시켰습니다.",
            "뮤턴트 고블린... 그는 아마 부족장이었을 겁니다.",
            "부족을 지키려다 스스로 괴물이 되는 길을 택한 것이지요."
        ],
        "unlock_key": "boss_mutant_goblin"
    },
    "boss_rich_king": {
        "title": "황금왕에 대하여",
        "speaker": "기억의 사제",
        "lines": [
            "황금왕을 쓰러뜨리셨군요... 놀랍습니다.",
            "그는 한때 메모리아에서 가장 부유한 왕이었습니다.",
            "끝없는 탐욕으로 부를 쌓았지만, 그것으로도 만족하지 못했지요.",
            "어둠의 신이 나타났을 때, 그는 더 큰 힘을 원했습니다.",
            "결국 어둠의 힘에 물들어 황금빛 괴물이 되었고...",
            "당신에게 쓰러지는 순간, 마지막 양심으로 단서를 남긴 것입니다."
        ],
        "unlock_key": "boss_rich_king"
    },
    "boss_magolem": {
        "title": "골렘에 대하여",
        "speaker": "기억의 사제",
        "lines": [
            "마공학 골렘을 쓰러뜨리셨다고요...? 놀랍습니다.",
            "골렘은 고대 마법사들이 만든 수호자입니다.",
            "흥미로운 점은... 그 골렘은 어둠의 신에게 폭주당한 것이 아닙니다.",
            "오히려 던전 자체를 수호하도록 프로그래밍되어 있었지요.",
            "마치... 누군가가 던전을 지키길 원했던 것처럼요.",
            "어둠의 신의 진정한 목적... 점점 의문이 깊어집니다."
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