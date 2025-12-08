import pygame

# 상점 상태
shop_state = {
    "stage": "inside",  # "inside" (상점 내부) 또는 "buying" (구매 UI)
    "selected_button": 0,  # 상점 내부에서 선택된 버튼 (0: 구매, 1: 대화, 2: 나가기)
    "is_talking": False,  # 대화 중인지 여부
    "dialog_index": 0,  # 현재 대사 인덱스
    "current_tab": 0,  # 현재 탭 (0: 포션, 1: 키트, 2: 무기, 3: 기타)
    "selected_slot": 0,  # 선택된 상품 슬롯 (0-2)
    "message": "",  # 구매 메시지
    "message_timer": 0,  # 메시지 타이머
}

# 탭 이름
TAB_NAMES = ["포션", "키트", "무기", "기타"]

# 상점 아이템 정의 (탭별)
SHOP_ITEMS = {
    # 탭 0: 포션
    0: [
        {"id": "health_potion_small", "name": "작은 체력 물약", "price": 50, "type": "consumable"},
        {"id": "health_potion_medium", "name": "중간 체력 물약", "price": 100, "type": "consumable"},
        {"id": "health_potion_large", "name": "큰 체력 물약", "price": 200, "type": "consumable"},
    ],
    # 탭 1: 수리 키트
    1: [
        {"id": "repair_kit_basic", "name": "초급 수리 키트", "price": 50, "type": "consumable"},
        {"id": "repair_kit_advanced", "name": "중급 수리 키트", "price": 100, "type": "consumable"},
        {"id": "repair_kit_master", "name": "고급 수리 키트", "price": 200, "type": "consumable"},
    ],
    # 탭 2: 무기
    2: [
        {"id": "random_box", "name": "랜덤 박스", "price": 250, "type": "random_box"},
        {"id": "rusty_dagger", "name": "녹슨 단검", "price": 150, "type": "weapon"},
        {"id": "iron_sword", "name": "철 검", "price": 300, "type": "weapon"},
    ],
    # 탭 3: 기타 (가방 등) - 동적으로 현재 레벨에 맞는 가방만 표시
    3: [
        {"id": "bag", "type": "bag"},  # 동적으로 정보가 채워짐
        None,
        None,
    ],
}

# 가방 레벨별 데이터
# 기본: 장착 2칸, 보유 6칸 (1줄)
# 레벨당 장착 +1칸, 보유 +12칸 (2줄)
BAG_LEVELS = {
    1: {"name": "가방(Lv.1)", "price": 300, "equipped_slots": 3, "inventory_slots": 18,
        "description": "장착 3칸, 보유 18칸으로 확장"},
    2: {"name": "가방(Lv.2)", "price": 1000, "equipped_slots": 4, "inventory_slots": 30,
        "description": "장착 4칸, 보유 30칸으로 확장"},
    3: {"name": "가방(Lv.3)", "price": 3000, "equipped_slots": 5, "inventory_slots": 42,
        "description": "장착 5칸, 보유 42칸으로 확장"},
    4: {"name": "가방(Lv.4)", "price": 10000, "equipped_slots": 6, "inventory_slots": 54,
        "description": "장착 6칸, 보유 54칸으로 확장 (최대)"},
}

def get_current_bag_level():
    """현재 가방 레벨 반환 (0: 기본, 1~4: 레벨)"""
    from scripts.inventory import inventory_state
    equipped = inventory_state["max_equipped_slots"]
    
    if equipped >= 6:
        return 4
    elif equipped >= 5:
        return 3
    elif equipped >= 4:
        return 2
    elif equipped >= 3:
        return 1
    else:
        return 0  # 기본 가방

def get_next_bag_item():
    """다음 레벨 가방 정보 반환"""
    current_level = get_current_bag_level()
    next_level = current_level + 1
    
    if next_level > 4:
        return None  # 최대 레벨 도달
    
    bag_data = BAG_LEVELS[next_level]
    return {
        "id": f"bag_lv{next_level}",
        "name": bag_data["name"],
        "price": bag_data["price"],
        "type": "bag",
        "equipped_slots": bag_data["equipped_slots"],
        "inventory_slots": bag_data["inventory_slots"],
        "description": bag_data["description"],
        "level": next_level,
    }

def draw_shop(screen, font_main, font_small, WIDTH, HEIGHT, game_state, dt=0, font_path=None):
    """상점 화면 그리기"""
    
    # 메시지 타이머 업데이트
    if shop_state["message"] and dt > 0:
        shop_state["message_timer"] += dt
        if shop_state["message_timer"] > 2:  # 2초 후 메시지 숨김
            shop_state["message"] = ""
            shop_state["message_timer"] = 0
    
    if shop_state["stage"] == "inside":
        # 상점 내부 화면
        draw_shop_inside(screen, font_main, font_small, WIDTH, HEIGHT, game_state)
    else:
        # 구매 UI 화면
        draw_shop_buying(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path)


def draw_shop_inside(screen, font_main, font_small, WIDTH, HEIGHT, game_state):
    """상점 내부 화면 (NPC와 대화)"""
    
    # 배경 이미지 로드 및 표시
    try:
        shop_bg = pygame.image.load("resources/png/building/shop_inside.png").convert()
        shop_bg = pygame.transform.scale(shop_bg, (WIDTH, HEIGHT))
        screen.blit(shop_bg, (0, 0))
    except:
        # 이미지 로드 실패 시 기본 배경
        screen.fill((100, 150, 100))
    
    # 대화 박스 (크기 증가)
    dialog_height = 179
    dialog_y = HEIGHT - dialog_height - 20
    dialog_rect = pygame.Rect(20, dialog_y, WIDTH - 40, dialog_height)
    
    # 대화 박스 배경 (반투명)
    dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
    dialog_surface.set_alpha(220)
    dialog_surface.fill((40, 30, 20))
    screen.blit(dialog_surface, dialog_rect)
    
    # 대화 박스 테두리
    pygame.draw.rect(screen, (200, 180, 150), dialog_rect, 4)
    
    # 대화 중일 때
    if shop_state["is_talking"]:
        # NPC 대화 내용 리스트
        npc_dialogs = [
            "상인: 좋은 물건만 취급하고 있다네!",
            "상인: 마음에 드는 게 있으면 언제든 구매해주게.",
            "상인: 오늘도 좋은 하루 되시게!",
        ]
        
        # 현재 대사 인덱스
        current_index = shop_state["dialog_index"]
        
        # 현재 대사 표시
        if current_index < len(npc_dialogs):
            text_y = dialog_y + 30
            current_dialog = npc_dialogs[current_index]
            text = font_small.render(current_dialog, True, (255, 255, 255))
            screen.blit(text, (40, text_y))
            
            # 화살표 표시 (우측 하단)
            arrow_text = pygame.font.SysFont("consolas", 30).render("▼", True, (255, 255, 255))
            screen.blit(arrow_text, (dialog_rect.right - 40, dialog_rect.bottom - 40))
    
    # 선택 모드일 때
    else:
        # NPC 대사 (좌측)
        npc_text = [
            "어서오게! 우리 상점에 온 걸 환영하네.",
            "필요한 물건이 있으면 말해주게.",
        ]
        
        text_y = dialog_y + 30
        for line in npc_text:
            text = font_small.render(line, True, (255, 255, 255))
            screen.blit(text, (40, text_y))
            text_y += 40
        
        # 버튼들 (우측, 균등 배치)
        button_width = 180
        button_height = 45
        button_gap = 10
        button_x = dialog_rect.right - button_width - 20
        
        # 3개 버튼의 총 높이
        total_buttons_height = button_height * 3 + button_gap * 2
        # 위아래 여백을 균등하게 (테두리 4px 고려)
        border_width = 4
        usable_height = dialog_height - border_width * 2
        button_start_y = dialog_y + border_width + (usable_height - total_buttons_height) // 2
        
        buttons = [
            {"text": "구매", "action": "buy"},
            {"text": "대화", "action": "talk"},
            {"text": "나가기", "action": "exit"},
        ]
        
        for i, button in enumerate(buttons):
            button_y = button_start_y + i * (button_height + button_gap)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # 선택된 버튼 강조
            if shop_state["selected_button"] == i:
                bg_color = (180, 50, 50)
                border_color = (255, 100, 100)
                text_color = (255, 255, 255)
                border_width = 3
            else:
                bg_color = (100, 30, 30)
                border_color = (150, 80, 80)
                text_color = (200, 200, 200)
                border_width = 2
            
            # 버튼 그리기
            pygame.draw.rect(screen, bg_color, button_rect)
            pygame.draw.rect(screen, border_color, button_rect, border_width)
            
            # 버튼 텍스트
            button_text = font_small.render(button["text"], True, text_color)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, button_text_rect)


def draw_shop_buying(screen, font_main, font_small, WIDTH, HEIGHT, game_state, font_path=None):
    """구매 UI 화면"""
    
    # 먼저 상점 내부 배경 그리기
    try:
        shop_bg = pygame.image.load("resources/png/building/shop_inside.png").convert()
        shop_bg = pygame.transform.scale(shop_bg, (WIDTH, HEIGHT))
        screen.blit(shop_bg, (0, 0))
    except:
        screen.fill((100, 150, 100))
    
    # 반투명 어두운 오버레이
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 구매 UI 이미지 로드
    try:
        shop_ui = pygame.image.load("resources/png/building/shop_buy.png").convert_alpha()
        # 원본 비율 유지하며 가로 600으로 조정
        original_width = shop_ui.get_width()
        original_height = shop_ui.get_height()
        ui_width = 800
        aspect_ratio = original_height / original_width
        ui_height = int(ui_width * aspect_ratio)
        
        shop_ui = pygame.transform.scale(shop_ui, (ui_width, ui_height))
        ui_x = (WIDTH - ui_width) // 2
        ui_y = (HEIGHT - ui_height) // 2
        screen.blit(shop_ui, (ui_x, ui_y))
    except:
        # 이미지 로드 실패 시 기본 UI
        ui_width = 800
        ui_height = 400
        ui_x = (WIDTH - ui_width) // 2
        ui_y = (HEIGHT - ui_height) // 2
        pygame.draw.rect(screen, (220, 200, 150), (ui_x, ui_y, ui_width, ui_height))
        pygame.draw.rect(screen, (100, 80, 50), (ui_x, ui_y, ui_width, ui_height), 4)
    
    # 현재 탭의 아이템들
    current_tab = shop_state["current_tab"]
    if current_tab in SHOP_ITEMS:
        items = SHOP_ITEMS[current_tab].copy()  # 복사본 사용
        
        # 기타 탭이면 동적으로 다음 레벨 가방 정보 가져오기
        if current_tab == 3:  # 기타 탭
            next_bag = get_next_bag_item()
            if next_bag:
                items[0] = next_bag
            else:
                items[0] = {"id": "bag_max", "name": "최대 레벨!", "price": 0, "type": "none",
                           "description": "이미 최대 레벨 가방을 보유중입니다."}
    else:
        items = []
    
    # 3개의 상품 슬롯 그리기 (전체 화면 중앙 기준)
    slot_width = 200
    slot_height = 350
    slot_gap = 20
    total_width = slot_width * 3 + slot_gap * 2
    start_x = (WIDTH - total_width) // 2
    start_y = (HEIGHT - slot_height) // 2
    
    # ===== 탭 그리기 (두루마리 스타일 - 양쪽 막대, 가운데 종이) =====
    tab_width = 160
    tab_height = 20
    tab_gap = 8
    
    # 색상
    scroll_color = (222, 212, 146)  # 베이지색 (종이)
    scroll_border = (176, 166, 100)  # 베이지 테두리 (명암)
    wood_color = (117, 64, 38)  # 갈색 (나무 막대)
    wood_border = (92, 53, 32)  # 갈색 테두리 (명암)
    
    # 탭 배치 계산 (현재 탭 기준 위/아래 배치)
    other_tabs = [i for i in range(4) if i != current_tab]
    top_tabs = other_tabs[:current_tab]  # 현재 탭보다 앞에 있는 탭들
    bottom_tabs = other_tabs[current_tab:]  # 현재 탭보다 뒤에 있는 탭들
    
    # 탭용 폰트
    if font_path:
        tab_font = pygame.font.Font(font_path, 18)
    else:
        tab_font = pygame.font.Font(None, 18)
    
    def draw_scroll_tab(x, y, width, height, text):
        """두루마리 탭 그리기 - 양쪽 나무 막대, 가운데 종이"""
        rod_width = 12
        paper_width = width - rod_width * 2
        
        # 왼쪽 나무 막대 (먼저 그리기)
        pygame.draw.rect(screen, wood_color, (x, y + 1, rod_width, height - 2))
        pygame.draw.rect(screen, wood_border, (x, y + 1, rod_width, height - 2), 3)
        
        # 오른쪽 나무 막대 (먼저 그리기)
        right_rod_x = x + width - rod_width
        pygame.draw.rect(screen, wood_color, (right_rod_x, y + 1, rod_width, height - 2))
        pygame.draw.rect(screen, wood_border, (right_rod_x, y + 1, rod_width, height - 2), 3)
        
        # 종이 부분 (가운데) - 나무 막대 위에 그리기
        paper_x = x + rod_width
        paper_extend = 3
        pygame.draw.rect(screen, scroll_color, 
                        (paper_x, y - paper_extend, paper_width, height + paper_extend * 2))
        pygame.draw.rect(screen, scroll_border, 
                        (paper_x, y - paper_extend, paper_width, height + paper_extend * 2), 3)
        
        # 텍스트 (볼드 효과 - 살짝만)
        text_color = (60, 40, 20)
        center_x = x + width // 2
        center_y = y + height // 2
        
        tab_text = tab_font.render(text, True, text_color)
        tab_text_rect = tab_text.get_rect(center=(center_x, center_y))
        
        # 살짝 오프셋으로 볼드 효과 (덜 두껍게)
        screen.blit(tab_text, tab_text_rect)
        screen.blit(tab_text, (tab_text_rect.x + 1, tab_text_rect.y))
    
    # 위쪽 탭 그리기 (세로로 쌓기)
    if top_tabs:
        top_x = (WIDTH - tab_width) // 2
        
        for idx, tab_idx in enumerate(top_tabs):
            tab_y = start_y - 12 - (len(top_tabs) - idx) * (tab_height + tab_gap)
            draw_scroll_tab(top_x, tab_y, tab_width, tab_height, TAB_NAMES[tab_idx])
    
    # 아래쪽 탭 그리기 (세로로 쌓기)
    if bottom_tabs:
        bottom_x = (WIDTH - tab_width) // 2
        
        for idx, tab_idx in enumerate(bottom_tabs):
            tab_y = start_y + slot_height + 19 + idx * (tab_height + tab_gap)
            draw_scroll_tab(bottom_x, tab_y, tab_width, tab_height, TAB_NAMES[tab_idx])
    
    for i in range(3):
        slot_x = start_x + i * (slot_width + slot_gap)
        slot_rect = pygame.Rect(slot_x, start_y, slot_width, slot_height)
        
        # 선택된 슬롯 강조 (크기 키우고 두께도 키움)
        if shop_state["selected_slot"] == i:
            select_rect = pygame.Rect(slot_x - 3, start_y - 3, slot_width + 6, slot_height + 6)
            pygame.draw.rect(screen, (255, 215, 0), select_rect, 9)
        
        # 아이템이 있으면 표시
        if i < len(items) and items[i] is not None:
            item = items[i]
            
            # 가격 표시 (상단 노란 바에 맞춤) - 큰 폰트 사용
            if font_path:
                price_font = pygame.font.Font(font_path, 32)
            else:
                price_font = pygame.font.Font(None, 32)
            price_text = price_font.render(f"{item['price']}G", True, (0, 0, 0))
            price_rect = price_text.get_rect(center=(slot_x + slot_width // 2, start_y + 37))
            screen.blit(price_text, price_rect)
            
            # 아이템 이미지 (중앙)
            item_img_y = start_y + 110
            item_size = 110
            try:
                if item["type"] == "consumable":
                    # 소모품 이미지 (consume.py에서 경로 가져오기)
                    from scripts.consume import ALL_CONSUMABLES
                    consumable_template = ALL_CONSUMABLES.get(item['id'])
                    if consumable_template and consumable_template.image_path:
                        consumable_img = pygame.image.load(consumable_template.image_path).convert_alpha()
                        consumable_img = pygame.transform.scale(consumable_img, (item_size, item_size))
                        item_x = slot_x + (slot_width - item_size) // 2
                        screen.blit(consumable_img, (item_x, item_img_y))
                    else:
                        # 이미지 경로가 없으면 기본 표시 (색상 구분)
                        item_x = slot_x + (slot_width - item_size) // 2
                        if "potion" in item["id"]:
                            if "small" in item["id"]:
                                color = (255, 182, 193)  # 연한 핑크
                            elif "medium" in item["id"]:
                                color = (255, 105, 180)  # 진한 핑크
                            else:
                                color = (220, 20, 60)  # 빨강
                        else:  # repair_kit
                            if "basic" in item["id"]:
                                color = (200, 200, 255)  # 연한 파랑
                            elif "advanced" in item["id"]:
                                color = (100, 100, 255)  # 진한 파랑
                            else:
                                color = (50, 50, 200)  # 어두운 파랑
                        pygame.draw.rect(screen, color, (item_x, item_img_y, item_size, item_size))
                        pygame.draw.rect(screen, (255, 255, 255), (item_x, item_img_y, item_size, item_size), 3)
                    
                elif item["type"] == "weapon":
                    # 무기 이미지 (weapons.py에서 경로 가져오기)
                    from scripts.weapons import ALL_WEAPONS
                    weapon_template = ALL_WEAPONS.get(item['id'])
                    if weapon_template and weapon_template.image_path:
                        weapon_img = pygame.image.load(weapon_template.image_path).convert_alpha()
                        weapon_img = pygame.transform.scale(weapon_img, (item_size, item_size))
                        item_x = slot_x + (slot_width - item_size) // 2
                        screen.blit(weapon_img, (item_x, item_img_y))
                    else:
                        # 이미지 경로가 없으면 기본 표시
                        item_x = slot_x + (slot_width - item_size) // 2
                        pygame.draw.rect(screen, (150, 150, 150), 
                                       (item_x, item_img_y, item_size, item_size))
                
                elif item["type"] == "bag":
                    # 가방 이미지 (기본 표시)
                    item_x = slot_x + (slot_width - item_size) // 2
                    # 가방 레벨에 따른 색상
                    level = item.get("level", 1)
                    if level == 1:
                        color = (139, 90, 43)  # 갈색
                    elif level == 2:
                        color = (192, 192, 192)  # 은색
                    elif level == 3:
                        color = (255, 215, 0)  # 금색
                    else:  # level 4
                        color = (147, 112, 219)  # 보라색 (최대)
                    pygame.draw.rect(screen, color, (item_x, item_img_y, item_size, item_size))
                    pygame.draw.rect(screen, (255, 255, 255), (item_x, item_img_y, item_size, item_size), 3)
                    # 가방 아이콘 텍스트
                    bag_icon = font_small.render("BAG", True, (0, 0, 0))
                    bag_icon_rect = bag_icon.get_rect(center=(item_x + item_size // 2, item_img_y + item_size // 2))
                    screen.blit(bag_icon, bag_icon_rect)
                
                elif item["type"] == "none":
                    # 최대 레벨 표시
                    item_x = slot_x + (slot_width - item_size) // 2
                    pygame.draw.rect(screen, (100, 100, 100), (item_x, item_img_y, item_size, item_size))
                    pygame.draw.rect(screen, (150, 150, 150), (item_x, item_img_y, item_size, item_size), 3)
                    max_icon = font_small.render("MAX", True, (255, 215, 0))
                    max_icon_rect = max_icon.get_rect(center=(item_x + item_size // 2, item_img_y + item_size // 2))
                    screen.blit(max_icon, max_icon_rect)
                
                elif item["type"] == "random_box":
                    # 랜덤 박스 이미지
                    item_x = slot_x + (slot_width - item_size) // 2
                    try:
                        box_img = pygame.image.load("resources/png/random_box.png").convert_alpha()
                        box_img = pygame.transform.scale(box_img, (item_size, item_size))
                        screen.blit(box_img, (item_x, item_img_y))
                    except:
                        # 이미지 없으면 기본 표시
                        pygame.draw.rect(screen, (255, 200, 100), (item_x, item_img_y, item_size, item_size))
                        pygame.draw.rect(screen, (200, 150, 50), (item_x, item_img_y, item_size, item_size), 3)
                        box_icon = font_small.render("?", True, (100, 50, 0))
                        box_icon_rect = box_icon.get_rect(center=(item_x + item_size // 2, item_img_y + item_size // 2))
                        screen.blit(box_icon, box_icon_rect)
            except:
                # 이미지 로드 실패
                item_x = slot_x + (slot_width - item_size) // 2
                pygame.draw.rect(screen, (150, 150, 150), 
                               (item_x, item_img_y, item_size, item_size))
            
            # 아이템 이름 (하단) - 글자 크기 자동 조절
            name_font_size = 28  # 기본 크기
            if font_path:
                name_font = pygame.font.Font(font_path, name_font_size)
            else:
                name_font = font_small
            max_name_width = slot_width - 40  # 여백 더 줌
            
            # 이름이 너무 길면 폰트 크기 줄이기
            while name_font.size(item["name"])[0] > max_name_width and name_font_size > 14:
                name_font_size -= 2
                if font_path:
                    name_font = pygame.font.Font(font_path, name_font_size)
                else:
                    name_font = pygame.font.Font(None, name_font_size)
            
            name_text = name_font.render(item["name"], True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(slot_x + slot_width // 2, start_y + 240))
            screen.blit(name_text, name_rect)
            
            # 구매 버튼 영역 (하단 노란 바에 맞춤)
            button_y = start_y + 313
            buy_text = font_small.render("구매", True, (0, 0, 0))
            buy_rect = buy_text.get_rect(center=(slot_x + slot_width // 2, button_y))
            screen.blit(buy_text, buy_rect)
    
    # 현재 골드 표시 (인벤토리 스타일)
    gold_text = font_small.render(f"골드: {game_state.get('gold', 0)}G", True, (255, 215, 0))
    gold_rect = gold_text.get_rect(topright=(WIDTH - 30, 30))
    
    # 골드 배경 박스
    gold_bg_rect = pygame.Rect(gold_rect.x - 15, gold_rect.y - 10, gold_rect.width + 30, gold_rect.height + 20)
    pygame.draw.rect(screen, (40, 40, 50), gold_bg_rect)
    pygame.draw.rect(screen, (255, 215, 0), gold_bg_rect, 2)
    
    screen.blit(gold_text, gold_rect)
    
    # 메시지 박스 표시 (구매 성공/실패 메시지)
    if shop_state["message"]:
        # 메시지 박스 크기 및 위치
        msg_box_width = 500
        msg_box_height = 80
        msg_box_x = (WIDTH - msg_box_width) // 2
        msg_box_y = HEIGHT - 120  # 조작 안내 제거로 더 아래로 이동
        
        # 메시지 박스 배경 (반투명)
        msg_surface = pygame.Surface((msg_box_width, msg_box_height))
        msg_surface.set_alpha(230)
        msg_surface.fill((40, 30, 20))
        screen.blit(msg_surface, (msg_box_x, msg_box_y))
        
        # 메시지 박스 테두리
        msg_rect = pygame.Rect(msg_box_x, msg_box_y, msg_box_width, msg_box_height)
        pygame.draw.rect(screen, (200, 180, 150), msg_rect, 4)
        
        # 메시지 텍스트 - 글자 크기 자동 조절
        msg_font_size = 28
        if font_path:
            msg_font = pygame.font.Font(font_path, msg_font_size)
        else:
            msg_font = font_small
        max_msg_width = msg_box_width - 40
        
        while msg_font.size(shop_state["message"])[0] > max_msg_width and msg_font_size > 14:
            msg_font_size -= 2
            if font_path:
                msg_font = pygame.font.Font(font_path, msg_font_size)
            else:
                msg_font = pygame.font.Font(None, msg_font_size)
        
        msg_text = msg_font.render(shop_state["message"], True, (255, 255, 255))
        msg_text_rect = msg_text.get_rect(center=(msg_box_x + msg_box_width // 2, msg_box_y + msg_box_height // 2))
        screen.blit(msg_text, msg_text_rect)


def handle_shop_input(events, game_state):
    """상점 입력 처리"""
    from scripts.inventory import player_inventory
    from scripts import battle_system
    from scripts.weapons import create_weapon
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            
            # 상점 내부 (NPC 대화)
            if shop_state["stage"] == "inside":
                # 대화 중일 때
                if shop_state["is_talking"]:
                    # Enter로 다음 대사 또는 대화 종료
                    if event.key == pygame.K_RETURN:
                        # 대사 인덱스 증가
                        shop_state["dialog_index"] += 1
                        
                        # 총 대사 수 (draw_shop_inside와 동일하게)
                        total_dialogs = 3
                        
                        # 모든 대사를 봤으면 대화 종료
                        if shop_state["dialog_index"] >= total_dialogs:
                            shop_state["is_talking"] = False
                            shop_state["dialog_index"] = 0
                
                # 선택 모드일 때
                else:
                    # W/S 키로 버튼 선택
                    if event.key == pygame.K_w:
                        shop_state["selected_button"] = max(0, shop_state["selected_button"] - 1)
                    elif event.key == pygame.K_s:
                        shop_state["selected_button"] = min(2, shop_state["selected_button"] + 1)
                    
                    # Enter 키로 버튼 실행
                    elif event.key == pygame.K_RETURN:
                        selected = shop_state["selected_button"]
                        
                        if selected == 0:  # 구매
                            shop_state["stage"] = "buying"
                        elif selected == 1:  # 대화
                            shop_state["is_talking"] = True
                        elif selected == 2:  # 나가기
                            game_state["state"] = "town"
                            shop_state["stage"] = "inside"
                            shop_state["current_tab"] = 0
                            shop_state["selected_slot"] = 0
                            shop_state["selected_button"] = 0
                            shop_state["is_talking"] = False
                    
                    # ESC로 바로 나가기
                    elif event.key == pygame.K_ESCAPE:
                        game_state["state"] = "town"
                        shop_state["stage"] = "inside"
                        shop_state["current_tab"] = 0
                        shop_state["selected_slot"] = 0
                        shop_state["selected_button"] = 0
                        shop_state["is_talking"] = False
            
            # 구매 UI
            elif shop_state["stage"] == "buying":
                if event.key == pygame.K_a:
                    # 좌로 이동
                    shop_state["selected_slot"] = max(0, shop_state["selected_slot"] - 1)
                elif event.key == pygame.K_d:
                    # 우로 이동
                    shop_state["selected_slot"] = min(2, shop_state["selected_slot"] + 1)
                
                elif event.key == pygame.K_w:
                    # 이전 탭
                    shop_state["current_tab"] = max(0, shop_state["current_tab"] - 1)
                    shop_state["selected_slot"] = 0
                elif event.key == pygame.K_s:
                    # 다음 탭
                    shop_state["current_tab"] = min(3, shop_state["current_tab"] + 1)
                    shop_state["selected_slot"] = 0
                
                elif event.key == pygame.K_RETURN:
                    # 구매
                    current_tab = shop_state["current_tab"]
                    selected_slot = shop_state["selected_slot"]
                    
                    if current_tab in SHOP_ITEMS:
                        # 기타 탭이면 동적으로 아이템 가져오기
                        if current_tab == 3:  # 기타 탭
                            items = SHOP_ITEMS[current_tab].copy()
                            next_bag = get_next_bag_item()
                            if next_bag:
                                items[0] = next_bag
                            else:
                                items[0] = None
                        else:
                            items = SHOP_ITEMS[current_tab]
                        
                        if selected_slot < len(items) and items[selected_slot] is not None:
                            item = items[selected_slot]
                            
                            # none 타입은 구매 불가
                            if item.get("type") == "none":
                                shop_state["message"] = "이미 최대 레벨입니다!"
                                shop_state["message_timer"] = 0
                                continue
                            
                            player_gold = game_state.get("gold", 0)
                            
                            # 골드가 충분한지 확인
                            if player_gold >= item["price"]:
                                # 골드 차감
                                game_state["gold"] = player_gold - item["price"]
                                
                                # 아이템 지급
                                if item["type"] == "weapon":
                                    # 무기 추가
                                    weapon = create_weapon(item["id"])
                                    if weapon:
                                        player_inventory["weapons"].append(weapon)
                                        shop_state["message"] = f"{item['name']}을(를) 구매했습니다!"
                                        shop_state["message_timer"] = 0
                                elif item["type"] == "consumable":
                                    # 소모품 추가
                                    from scripts.consume import create_consumable
                                    from scripts import temple
                                    consumable = create_consumable(item["id"])
                                    if consumable:
                                        player_inventory["consumables"].append(consumable)
                                        shop_state["message"] = f"{item['name']}을(를) 구매했습니다!"
                                        shop_state["message_timer"] = 0
                                        # 소비템 구매 기록
                                        temple.set_visited("shop_consumable")
                                elif item["type"] == "bag":
                                    # 가방 구매 - 인벤토리 확장
                                    from scripts.inventory import inventory_state
                                    
                                    new_equipped = item["equipped_slots"]
                                    new_inventory = item["inventory_slots"]
                                    
                                    # 인벤토리 확장
                                    inventory_state["max_equipped_slots"] = new_equipped
                                    inventory_state["max_inventory_slots"] = new_inventory
                                    shop_state["message"] = f"{item['name']} 구매! 인벤토리가 확장되었습니다!"
                                    shop_state["message_timer"] = 0
                                elif item["type"] == "random_box":
                                    # 랜덤 박스 - 즉시 무기 획득
                                    import random
                                    from scripts.weapons import ALL_WEAPONS
                                    
                                    # 확률: 일반 50%, 희귀 49%, 영웅 1%
                                    roll = random.random()
                                    if roll < 0.50:
                                        target_grade = "일반"
                                    elif roll < 0.99:
                                        target_grade = "희귀"
                                    else:
                                        target_grade = "영웅"
                                    
                                    # 해당 등급 무기 중 랜덤 선택 (보스 드롭, 테스트 무기 제외)
                                    available_weapons = [
                                        wid for wid, wp in ALL_WEAPONS.items()
                                        if wp.grade == target_grade
                                        and wp.grade != "몬스터"
                                        and not getattr(wp, 'is_boss_drop', False)
                                        and "test" not in wid
                                    ]
                                    
                                    if available_weapons:
                                        weapon_id = random.choice(available_weapons)
                                        weapon = create_weapon(weapon_id)
                                        if weapon:
                                            player_inventory["weapons"].append(weapon)
                                            # 등급별 색상 지정
                                            grade_color = {"일반": "흰색", "희귀": "파란색", "영웅": "보라색"}
                                            shop_state["message"] = f"[{target_grade}] {weapon.name} 획득!"
                                            shop_state["message_timer"] = 0
                                    else:
                                        shop_state["message"] = "랜덤 박스 오류!"
                                        shop_state["message_timer"] = 0
                            else:
                                shop_state["message"] = "골드가 부족합니다!"
                                shop_state["message_timer"] = 0
                
                elif event.key == pygame.K_ESCAPE:
                    # 상점 내부로 돌아가기
                    shop_state["stage"] = "inside"


def wrap_text(text, font, max_width):
    """텍스트 줄바꿈"""
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines