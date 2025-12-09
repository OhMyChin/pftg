# scripts/boss_battle.py
"""
최종 보스 (45층) - 3페이즈 전투 시스템
어둠의 신 → 옛 용사 → (플레이어 이름)
"""

import pygame

# --- 보스전 상태 ---
boss_state = {
    "active": False,           # 보스전 진행 중 여부
    "current_phase": 0,        # 현재 페이즈 (1, 2, 3)
    "phase_complete": False,   # 현재 페이즈 완료 여부
    "dialogue_index": 0,       # 현재 대화 인덱스
    "dialogue_type": None,     # "pre" 또는 "post"
    "showing_dialogue": False, # 대화 표시 중 여부
    "battle_started": False,   # 전투 시작 여부
    "ending_triggered": False, # 엔딩 트리거 여부
}

# --- 폰트 경로 ---
FONT_PATH = None


# ==================== 보스 데이터 ====================

def get_final_boss_data(player_name="???"):
    """
    플레이어 이름을 받아서 최종보스 데이터 반환
    3페이즈 보스명이 플레이어 이름이므로 동적 생성
    """
    return {
        1: {
            "name": "어둠의 신",
            "hp": 800,
            "speed": 15,
            "weapon_id": "dark_god_weapon",
            "image_path": "resources/png/enemy/boss/dark_god.png",
            "image_size": 300,
            "gold": (0, 0),  # 골드 없음
            "pre_dialogue": [
                "어둠의 기운이 압도적으로 짙어진다...",
                "???",
                "\"...드디어 여기까지 왔군.\"",
                "\"하찮은 인간이 감히 나에게 도전하다니.\"",
                "\"이 던전의 주인인 나, 어둠의 신을 쓰러뜨리겠다고?\"",
                "\"어리석군. 네 오만함의 대가를 치르게 해주마.\"",
                "\"덤벼라!\"",
            ],
            "post_dialogue": [
                "\"크윽... 강하군...\"",
                "\"인간 주제에... 이 정도의 힘을...\"",
                "\"...잠깐, 이 기운은...?\"",
                "어둠의 신의 눈빛이 흔들린다.",
                "\"네게서... 왜 이렇게 익숙한 기운이...\"",
                "\"...으윽...! 머리가...!\"",
                "어둠의 신이 머리를 부여잡는다.",
                "\"이건... 기억...? 내 기억인가...?\"",
                "어둠의 신의 형체가 일그러지기 시작한다...",
            ],
        },
        2: {
            "name": "옛 용사",
            "hp": 1200,
            "speed": 18,
            "weapon_id": "old_hero_weapon",
            "image_path": "resources/png/enemy/boss/old_hero.png",
            "image_size": 150,  # 플레이어 크기와 비슷하게
            "has_dark_aura": True,  # 어둠 오라 효과
            "gold": (0, 0),
            "pre_dialogue": [
                "어둠의 신의 모습이 변하기 시작한다...",
                "점점 인간의 형상으로...",
                "???",
                "\"...기억이 돌아왔다. 전부.\"",
                "\"나는 '옛 용사'... 이 세계를 지키던 자였다.\"",
                "\"어둠의 힘이 메모리아를 삼키려 했을 때...\"",
                "\"나는 이 던전을 만들어 그 힘을 가뒀다.\"",
                "\"하지만 그 과정에서 나도 어둠에 물들었고...\"",
                "\"모든 기억을 잃은 채 '어둠의 신'이 되어버렸지.\"",
                "\"완전히 잠식되기 전, 마지막으로 내 기억을 분리해서 보냈다.\"",
                "\"나를 쓰러뜨릴 수 있는 '용사'로서...\"",
                "옛 용사가 당신을 똑바로 바라본다.",
                "\"그게 바로 너다. 너는 나 자신이야.\"",
                "\"네 덕분에 기억을 되찾았다. 고마워.\"",
                "\"하지만...\"",
                "옛 용사의 몸에서 어둠의 기운이 폭주한다.",
                "\"크윽...! 어둠의 힘이... 몸을 지배하려 해...!\"",
                "\"도망쳐...! 아니, 안 돼... 여기서 끝내야 해!\"",
                "\"제발... 나를 멈춰줘!\"",
            ],
            "post_dialogue": [
                "\"...해냈구나.\"",
                "옛 용사의 표정이 평온해진다.",
                "\"고마워... 덕분에 잠시 제정신이 돌아왔어.\"",
                "\"하지만...\"",
                "옛 용사가 자신의 몸을 내려다본다.",
                "\"어둠의 힘은 아직 내 안에 있어.\"",
                "\"이대로 두면... 또다시 기억을 잃고 폭주할 거야.\"",
                "\"그러니...\"",
                "옛 용사가 미소 짓는다.",
                "\"마지막으로, 한 번만 더 싸워줘.\"",
            ],
        },
        3: {
            "name": player_name,  # 플레이어 이름
            "hp": 1,  # 연출용 - 한 방에 끝남
            "speed": 1,
            "weapon_id": "final_form_weapon",
            "image_path": "resources/png/enemy/boss/true_self.png",
            "image_size": 150,  # 플레이어 크기와 비슷하게
            "gold": (0, 0),
            "pre_dialogue": [
                "옛 용사의 모습이 다시 변하기 시작한다...",
                "이번에는... 낯익은 모습으로.",
                "거울을 보는 것 같다.",
                "\"...이것이 나의, 아니 '우리'의 진짜 모습이다.\"",
                f"\"{player_name}... 그것이 우리의 이름이었지.\"",
                "\"이제 전부 기억났다. 모든 것을.\"",
                "\"어둠의 힘을 품은 채로는 살아갈 수 없어.\"",
                "\"하지만 네가 나를 쓰러뜨리면...\"",
                "\"어둠의 힘도 함께 사라질 것이다.\"",
                "\"걱정 마. 네가 가진 기억은 사제가 되돌려줄 거야.\"",
                "\"너는 '나의 빛'이니까.\"",
                "\"오랫동안 혼자 싸웠어. 외롭고 무서웠지.\"",
                "\"하지만 이제 괜찮아. 네가 와줬으니까.\"",
                "\"...고마워. 그리고 미안해.\"",
                "\"부디... 행복하게 살아줘.\"",
                f"{player_name}(이)가 검을 들어올렸다.",
            ],
            "post_dialogue": [
                "\"......\"",
                f"{player_name}(이)가 쓰러진다.",
                "아니... '옛 용사'가 쓰러진다.",
                "\"...잘했어.\"",
                "\"이제... 모든 것이 끝났구나.\"",
                "옛 용사의 몸에서 어둠의 기운이 빠져나간다.",
                "그리고... 서서히 사방으로 흩어지기 시작한다.",
                "\"드디어... 쉴 수 있겠네.\"",
                "\"메모리아를... 부탁해.\"",
                "\"...안녕.\"",
                "...",
                "......",
                ".........",
                "어둠이 걷히고, 따스한 빛이 던전을 비춘다.",
                "당신은 살아남았다.",
                "그리고... 모든 것을 기억해냈다.",
            ],
        },
    }


# ==================== 보스전 제어 함수 ====================

def start_boss_battle(player_name):
    """최종 보스전 시작"""
    global boss_state
    boss_state = {
        "active": True,
        "current_phase": 1,
        "phase_complete": False,
        "dialogue_index": 0,
        "dialogue_type": "pre",
        "showing_dialogue": True,
        "battle_started": False,
        "ending_triggered": False,
        "player_name": player_name,
    }
    return True


def reset_boss_state():
    """보스전 상태 초기화"""
    global boss_state
    boss_state = {
        "active": False,
        "current_phase": 0,
        "phase_complete": False,
        "dialogue_index": 0,
        "dialogue_type": None,
        "showing_dialogue": False,
        "battle_started": False,
        "ending_triggered": False,
    }


def get_current_boss():
    """현재 페이즈의 보스 데이터 반환"""
    if not boss_state["active"]:
        return None
    
    player_name = boss_state.get("player_name", "???")
    boss_data = get_final_boss_data(player_name)
    phase = boss_state["current_phase"]
    
    if phase in boss_data:
        return boss_data[phase]
    return None


def get_current_dialogue():
    """현재 표시할 대화 텍스트 반환"""
    boss = get_current_boss()
    if not boss:
        return None
    
    dialogue_type = boss_state["dialogue_type"]
    dialogue_key = f"{dialogue_type}_dialogue"
    
    if dialogue_key in boss:
        dialogues = boss[dialogue_key]
        idx = boss_state["dialogue_index"]
        if idx < len(dialogues):
            return dialogues[idx]
    return None


def advance_dialogue():
    """다음 대화로 진행, 대화 끝나면 상태 변경"""
    global boss_state
    
    boss = get_current_boss()
    if not boss:
        return "end"
    
    dialogue_type = boss_state["dialogue_type"]
    dialogue_key = f"{dialogue_type}_dialogue"
    dialogues = boss.get(dialogue_key, [])
    
    boss_state["dialogue_index"] += 1
    
    if boss_state["dialogue_index"] >= len(dialogues):
        # 대화 끝
        boss_state["dialogue_index"] = 0
        
        if dialogue_type == "pre":
            # pre 대화 끝 → 전투 시작
            boss_state["showing_dialogue"] = False
            boss_state["battle_started"] = True
            return "start_battle"
        
        elif dialogue_type == "post":
            # post 대화 끝 → 다음 페이즈 또는 엔딩
            phase = boss_state["current_phase"]
            
            if phase < 3:
                # 다음 페이즈로
                boss_state["current_phase"] += 1
                boss_state["dialogue_type"] = "pre"
                boss_state["showing_dialogue"] = True
                boss_state["battle_started"] = False
                boss_state["phase_complete"] = False
                return "next_phase"
            else:
                # 3페이즈 완료 → 엔딩
                boss_state["ending_triggered"] = True
                boss_state["showing_dialogue"] = False
                return "ending"
    
    return "continue"


def on_phase_complete():
    """페이즈 클리어 시 호출"""
    global boss_state
    boss_state["phase_complete"] = True
    boss_state["dialogue_type"] = "post"
    boss_state["dialogue_index"] = 0
    boss_state["showing_dialogue"] = True
    boss_state["battle_started"] = False


def is_boss_battle_active():
    """보스전 진행 중 여부"""
    return boss_state["active"]


def is_showing_dialogue():
    """대화 표시 중 여부"""
    return boss_state["showing_dialogue"]


def get_phase():
    """현재 페이즈 반환"""
    return boss_state["current_phase"]


def is_ending():
    """엔딩 트리거 여부"""
    return boss_state.get("ending_triggered", False)


# ==================== 보스전 대화 UI ====================

def draw_boss_dialogue(screen, font_path, width, height):
    """보스전 대화 UI 그리기"""
    global FONT_PATH
    if font_path:
        FONT_PATH = font_path
    
    # 배경 어둡게
    overlay = pygame.Surface((width, height))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # 대화 박스
    box_width = width - 100
    box_height = 150
    box_x = 50
    box_y = height - box_height - 50
    
    # 박스 배경
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, (20, 20, 30), box_rect)
    
    # 페이즈별 테두리 색상
    phase = boss_state["current_phase"]
    if phase == 1:
        border_color = (150, 50, 150)  # 보라색 - 어둠의 신
    elif phase == 2:
        border_color = (50, 150, 200)  # 하늘색 - 옛 용사
    else:
        border_color = (255, 215, 0)   # 금색 - 진짜 모습
    
    pygame.draw.rect(screen, border_color, box_rect, 3)
    
    # 대화 텍스트
    dialogue = get_current_dialogue()
    if dialogue:
        font = pygame.font.Font(FONT_PATH, 24) if FONT_PATH else pygame.font.SysFont("malgungothic", 24)
        
        # 텍스트 줄바꿈
        lines = wrap_text(dialogue, font, box_width - 60)
        
        y_offset = box_y + 30
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (box_x + 30, y_offset))
            y_offset += 35
    
    # 진행 안내 (깜빡임 효과)
    small_font = pygame.font.Font(FONT_PATH, 18) if FONT_PATH else pygame.font.SysFont("malgungothic", 18)
    
    # 깜빡임 (0.5초 간격)
    import time
    if int(time.time() * 2) % 2 == 0:
        hint = small_font.render("[ Enter ]", True, (180, 180, 180))
        screen.blit(hint, (box_x + box_width - 100, box_y + box_height - 35))
    
    # 페이즈 표시 (상단)
    boss = get_current_boss()
    if boss:
        phase_font = pygame.font.Font(FONT_PATH, 28) if FONT_PATH else pygame.font.SysFont("malgungothic", 28)
        phase_text = f"― {boss['name']} ―"
        phase_surface = phase_font.render(phase_text, True, border_color)
        phase_x = width // 2 - phase_surface.get_width() // 2
        screen.blit(phase_surface, (phase_x, box_y - 50))


def wrap_text(text, font, max_width):
    """텍스트 줄바꿈"""
    words = list(text)
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


def handle_boss_dialogue_input(events):
    """보스전 대화 입력 처리"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                result = advance_dialogue()
                return result
    return "continue"