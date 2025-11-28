import pygame

# 상점 상태
shop_state = {
    "stage": "inside",  # "inside" (상점 내부) 또는 "buying" (구매 UI)
    "selected_button": 0,  # 상점 내부에서 선택된 버튼 (0: 구매, 1: 대화, 2: 나가기)
    "is_talking": False,  # 대화 중인지 여부
    "dialog_index": 0,  # 현재 대사 인덱스
    "page": 0,  # 현재 페이지
    "selected_slot": 0,  # 선택된 상품 슬롯 (0-2)
    "message": "",  # 구매 메시지
    "message_timer": 0,  # 메시지 타이머
}

# 상점 아이템 정의
SHOP_ITEMS = [
    # 페이지 0 (포션)
    [
        {"id": "health_potion_small", "name": "작은 체력 물약", "price": 50, "type": "consumable"},
        {"id": "health_potion_medium", "name": "중간 체력 물약", "price": 100, "type": "consumable"},
        {"id": "health_potion_large", "name": "큰 체력 물약", "price": 200, "type": "consumable"},
    ],
    # 페이지 1 (수리 키트)
    [
        {"id": "repair_kit_basic", "name": "초급 수리 키트", "price": 50, "type": "consumable"},
        {"id": "repair_kit_advanced", "name": "중급 수리 키트", "price": 100, "type": "consumable"},
        {"id": "repair_kit_master", "name": "고급 수리 키트", "price": 200, "type": "consumable"},
    ],
    # 페이지 2 (무기)
    [
        {"id": "iron_sword", "name": "철 검", "price": 300, "type": "weapon"},
        {"id": "rusty_dagger", "name": "녹슨 단검", "price": 150, "type": "weapon"},
        None,  # 빈 슬롯
    ],
]

def draw_shop(screen, font_main, font_small, WIDTH, HEIGHT, game_state, dt=0):
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
        draw_shop_buying(screen, font_main, font_small, WIDTH, HEIGHT, game_state)


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


def draw_shop_buying(screen, font_main, font_small, WIDTH, HEIGHT, game_state):
    """구매 UI 화면"""
    
    # 배경 약간 어둡게
    screen.fill((50, 50, 50))
    
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
    
    # 현재 페이지의 아이템들
    current_page = shop_state["page"]
    if current_page < len(SHOP_ITEMS):
        items = SHOP_ITEMS[current_page]
    else:
        items = []
    
    # 3개의 상품 슬롯 그리기
    slot_width = 160
    slot_height = 280
    slot_gap = 30
    total_width = slot_width * 3 + slot_gap * 2
    start_x = ui_x + (ui_width - total_width) // 2
    start_y = ui_y + 50
    
    for i in range(3):
        slot_x = start_x + i * (slot_width + slot_gap)
        slot_rect = pygame.Rect(slot_x, start_y, slot_width, slot_height)
        
        # 선택된 슬롯 강조
        if shop_state["selected_slot"] == i:
            pygame.draw.rect(screen, (255, 215, 0), slot_rect, 4)
        
        # 아이템이 있으면 표시
        if i < len(items) and items[i] is not None:
            item = items[i]
            
            # 가격 표시 (상단)
            price_text = font_small.render(f"{item['price']}G", True, (0, 0, 0))
            price_rect = price_text.get_rect(center=(slot_x + slot_width // 2, start_y + 30))
            screen.blit(price_text, price_rect)
            
            # 아이템 이미지 (중앙)
            item_img_y = start_y + 60  # 이미지 위치 조정
            try:
                if item["type"] == "consumable":
                    # 소모품 이미지 (consume.py에서 경로 가져오기)
                    from scripts.consume import ALL_CONSUMABLES
                    consumable_template = ALL_CONSUMABLES.get(item['id'])
                    if consumable_template and consumable_template.image_path:
                        consumable_img = pygame.image.load(consumable_template.image_path).convert_alpha()
                        consumable_img = pygame.transform.scale(consumable_img, (80, 80))
                        item_x = slot_x + (slot_width - 80) // 2
                        screen.blit(consumable_img, (item_x, item_img_y))
                    else:
                        # 이미지 경로가 없으면 기본 표시 (색상 구분)
                        item_size = 80
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
                        weapon_img = pygame.transform.scale(weapon_img, (80, 80))
                        item_x = slot_x + (slot_width - 80) // 2
                        screen.blit(weapon_img, (item_x, item_img_y))
                    else:
                        # 이미지 경로가 없으면 기본 표시
                        pygame.draw.rect(screen, (150, 150, 150), 
                                       (slot_x + 40, item_img_y, 80, 80))
            except:
                # 이미지 로드 실패
                pygame.draw.rect(screen, (150, 150, 150), 
                               (slot_x + 40, item_img_y, 80, 80))
            
            # 아이템 이름 (하단)
            name_lines = wrap_text(item["name"], font_small, slot_width - 20)
            name_y = start_y + 170  # 이름 위치 조정
            for line in name_lines:
                name_text = font_small.render(line, True, (0, 0, 0))
                name_rect = name_text.get_rect(center=(slot_x + slot_width // 2, name_y))
                screen.blit(name_text, name_rect)
                name_y += 25
            
            # 구매 버튼 영역 (하단)
            button_y = start_y + slot_height - 50
            buy_text = font_small.render("구매", True, (0, 0, 0))
            buy_rect = buy_text.get_rect(center=(slot_x + slot_width // 2, button_y))
            screen.blit(buy_text, buy_rect)
    
    # 페이지 표시
    page_text = font_small.render(f"페이지 {current_page + 1}/{len(SHOP_ITEMS)}", True, (255, 255, 255))
    screen.blit(page_text, (WIDTH // 2 - page_text.get_width() // 2, ui_y + ui_height + 20))
    
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
        
        # 메시지 텍스트
        msg_text = font_small.render(shop_state["message"], True, (255, 255, 255))
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
                            shop_state["page"] = 0
                            shop_state["selected_slot"] = 0
                            shop_state["selected_button"] = 0
                            shop_state["is_talking"] = False
                    
                    # ESC로 바로 나가기
                    elif event.key == pygame.K_ESCAPE:
                        game_state["state"] = "town"
                        shop_state["stage"] = "inside"
                        shop_state["page"] = 0
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
                    # 페이지 올리기
                    shop_state["page"] = max(0, shop_state["page"] - 1)
                    shop_state["selected_slot"] = 0
                elif event.key == pygame.K_s:
                    # 페이지 내리기
                    shop_state["page"] = min(len(SHOP_ITEMS) - 1, shop_state["page"] + 1)
                    shop_state["selected_slot"] = 0
                
                elif event.key == pygame.K_RETURN:
                    # 구매
                    current_page = shop_state["page"]
                    selected_slot = shop_state["selected_slot"]
                    
                    if current_page < len(SHOP_ITEMS):
                        items = SHOP_ITEMS[current_page]
                        if selected_slot < len(items) and items[selected_slot] is not None:
                            item = items[selected_slot]
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
                                    consumable = create_consumable(item["id"])
                                    if consumable:
                                        player_inventory["consumables"].append(consumable)
                                        shop_state["message"] = f"{item['name']}을(를) 구매했습니다!"
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