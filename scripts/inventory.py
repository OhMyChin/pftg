import pygame

# 텍스트 줄바꿈 함수
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
    
    return lines

# 인벤토리 상태
inventory_state = {
    "current_tab": "weapon",  # "weapon" 또는 "consume"
    "selected_area": "slots",  # "tabs", "slots", 또는 "pages"
    "selected_tab_index": 0,  # 0: 무기, 1: 소비
    "selected_row": 1,  # 0: 장착템, 1~3: 보유템
    "selected_col": 0,
    "weapon_page": 0,  # 0 또는 1
    "consume_page": 0,
    "max_equipped_slots": 2,  # 초기 2칸, 최대 6칸
    "max_inventory_slots": 6,  # 초기 6칸, 최대 36칸
    "message": "",
    "message_timer": 0,
    "action_menu_open": False,  # 액션 메뉴 표시 여부
    "action_menu_selected": 0,  # 선택된 액션 (0: 장착/해제, 1: 스킬, 2: 취소)
    "action_menu_item": None,  # 액션 메뉴가 열린 아이템
    "action_menu_is_equipped": False,  # 장착된 아이템인지 여부
    "info_screen_open": False,  # 정보 화면 표시 여부
    "info_screen_item": None,  # 정보 화면에 표시할 아이템
    "weapon_select_open": False,  # 무기 선택 화면 표시 여부
    "weapon_select_index": 0,  # 선택된 무기 인덱스
    "weapon_select_consumable": None,  # 사용할 소모품
}

# 플레이어 인벤토리 데이터
player_inventory = {
    "equipped_weapons": [],  # 장착된 무기 리스트
    "weapons": [],  # 보유 무기 리스트
    "consumables": []  # 소비 아이템 리스트
}

def draw_inventory(screen, font_main, font_small, WIDTH, HEIGHT, battle_player, dt, font_path=None, game_state=None):
    """인벤토리 화면 그리기"""
    global inventory_state
    
    # 배경 (검은색)
    screen.fill((20, 20, 30))
    
    # 작은 폰트 생성 (설명용)
    if font_path:
        font_tiny = pygame.font.Font(font_path, 20)
    else:
        font_tiny = pygame.font.Font(None, 20)
    
    # ===== 골드 정보 표시 (오른쪽 위) =====
    if game_state:
        gold_text = font_small.render(f"골드: {game_state.get('gold', 0)}G", True, (255, 215, 0))
        gold_rect = gold_text.get_rect(topright=(WIDTH - 30, 30))
        
        # 골드 배경 박스
        gold_bg_rect = pygame.Rect(gold_rect.x - 15, gold_rect.y - 10, gold_rect.width + 30, gold_rect.height + 20)
        pygame.draw.rect(screen, (40, 40, 50), gold_bg_rect)
        pygame.draw.rect(screen, (255, 215, 0), gold_bg_rect, 2)
        
        screen.blit(gold_text, gold_rect)
    
    # 레이아웃 설정
    info_panel_width = 240
    info_panel_x = 30
    info_panel_y = 30
    info_panel_height = HEIGHT - 60  # 하단 여백을 30으로 조정
    
    tab_area_x = info_panel_x + info_panel_width + 30
    tab_area_y = 30
    
    slot_size = 75
    slot_gap = 4
    
    # ===== 왼쪽 정보 패널 =====
    info_rect = pygame.Rect(info_panel_x, info_panel_y, info_panel_width, info_panel_height)
    pygame.draw.rect(screen, (40, 40, 50), info_rect)
    pygame.draw.rect(screen, (100, 100, 120), info_rect, 3)
    
    # 선택된 아이템 정보 표시
    selected_item = get_selected_item(battle_player)
    if selected_item:
        y_offset = info_panel_y + 20
        max_name_width = info_panel_width - 30  # 패널 내 최대 너비
        
        # 무기 정보
        if hasattr(selected_item, 'durability'):
            # 이름 글자 크기 자동 조절
            name_font_size = 28  # font_small 기본 크기 (추정)
            if font_path:
                name_font = pygame.font.Font(font_path, name_font_size)
            else:
                name_font = font_small
            
            # 텍스트가 너무 길면 폰트 크기 줄이기
            while name_font.size(selected_item.name)[0] > max_name_width and name_font_size > 14:
                name_font_size -= 2
                if font_path:
                    name_font = pygame.font.Font(font_path, name_font_size)
                else:
                    name_font = pygame.font.Font(None, name_font_size)
            
            name_text = name_font.render(selected_item.name, True, (255, 255, 255))
            screen.blit(name_text, (info_panel_x + 15, y_offset))
            y_offset += 35
            
            # 등급과 내구도 텍스트 준비
            grade_str = f"등급: {selected_item.grade}"
            durability_str = f"내구도: {selected_item.durability}/{selected_item.max_durability}"
            
            # 둘 중 더 긴 텍스트에 맞춰 폰트 크기 조절
            info_font_size = 28
            if font_path:
                info_font = pygame.font.Font(font_path, info_font_size)
            else:
                info_font = font_small
            
            # 둘 다 패널 안에 들어올 때까지 크기 줄이기
            while (info_font.size(grade_str)[0] > max_name_width or 
                   info_font.size(durability_str)[0] > max_name_width) and info_font_size > 14:
                info_font_size -= 2
                if font_path:
                    info_font = pygame.font.Font(font_path, info_font_size)
                else:
                    info_font = pygame.font.Font(None, info_font_size)
            
            grade_text = info_font.render(grade_str, True, (200, 200, 100))
            screen.blit(grade_text, (info_panel_x + 15, y_offset))
            y_offset += 30
            
            durability_text = info_font.render(durability_str, True, (100, 200, 255))
            screen.blit(durability_text, (info_panel_x + 15, y_offset))
            y_offset += 30
            
            # 강화도 표시
            upgrade_level = getattr(selected_item, 'upgrade_level', 0)
            if upgrade_level > 0:
                upgrade_text = info_font.render(f"강화: +{upgrade_level}", True, (255, 180, 50))
                screen.blit(upgrade_text, (info_panel_x + 15, y_offset))
                y_offset += 30
            
            # 초월 여부 표시
            is_transcended = getattr(selected_item, 'is_transcended', False)
            transcend_skill = getattr(selected_item, 'transcend_skill', None)
            if is_transcended and transcend_skill:
                from scripts.skills import ALL_SKILLS
                skill_name = ALL_SKILLS[transcend_skill].name if transcend_skill in ALL_SKILLS else transcend_skill
                transcend_text = info_font.render(f"초월: {skill_name}", True, (255, 100, 255))
                screen.blit(transcend_text, (info_panel_x + 15, y_offset))
                y_offset += 30
            elif transcend_skill and not is_transcended:
                transcend_text = font_tiny.render("(+5 강화 시 초월 가능)", True, (150, 100, 150))
                screen.blit(transcend_text, (info_panel_x + 15, y_offset))
                y_offset += 25
            
            y_offset += 8
            desc_lines = wrap_text(selected_item.description, font_tiny, info_panel_width - 30)
            for line in desc_lines:
                desc_text = font_tiny.render(line, True, (180, 180, 180))
                screen.blit(desc_text, (info_panel_x + 15, y_offset))
                y_offset += 22
        
        # 소모품 정보
        elif hasattr(selected_item, 'type'):  # Consumable
            # 이름 글자 크기 자동 조절
            name_font_size = 28
            if font_path:
                name_font = pygame.font.Font(font_path, name_font_size)
            else:
                name_font = font_small
            
            while name_font.size(selected_item.name)[0] > max_name_width and name_font_size > 14:
                name_font_size -= 2
                if font_path:
                    name_font = pygame.font.Font(font_path, name_font_size)
                else:
                    name_font = pygame.font.Font(None, name_font_size)
            
            name_text = name_font.render(selected_item.name, True, (255, 255, 255))
            screen.blit(name_text, (info_panel_x + 15, y_offset))
            y_offset += 35
            
            # 타입 표시
            type_name = "포션" if selected_item.type == "potion" else "수리 키트"
            type_text = font_small.render(f"종류: {type_name}", True, (200, 200, 100))
            screen.blit(type_text, (info_panel_x + 15, y_offset))
            y_offset += 30
            
            # 효과 표시
            if selected_item.type == "potion":
                effect_text = font_small.render(
                    f"회복량: {selected_item.effect_value} HP", 
                    True, (100, 200, 255)
                )
            else:  # repair_kit
                effect_text = font_small.render(
                    f"수리량: {selected_item.effect_value}", 
                    True, (100, 200, 255)
                )
            screen.blit(effect_text, (info_panel_x + 15, y_offset))
            y_offset += 35
            
            # 설명
            y_offset += 8
            desc_lines = wrap_text(selected_item.description, font_tiny, info_panel_width - 30)
            for line in desc_lines:
                desc_text = font_tiny.render(line, True, (180, 180, 180))
                screen.blit(desc_text, (info_panel_x + 15, y_offset))
                y_offset += 22
    
    # ===== 탭 버튼 =====
    tab_button_width = 130
    tab_button_height = 45
    
    weapon_tab_rect = pygame.Rect(tab_area_x, tab_area_y, tab_button_width, tab_button_height)
    consume_tab_rect = pygame.Rect(tab_area_x + tab_button_width + 10, tab_area_y, tab_button_width, tab_button_height)
    
    weapon_color = (150, 150, 250) if inventory_state["current_tab"] == "weapon" else (80, 80, 100)
    consume_color = (150, 150, 250) if inventory_state["current_tab"] == "consume" else (80, 80, 100)
    
    pygame.draw.rect(screen, weapon_color, weapon_tab_rect)
    
    # 탭이 선택되었는지 체크
    if inventory_state["selected_area"] == "tabs":
        if inventory_state["selected_tab_index"] == 0:
            pygame.draw.rect(screen, (100, 150, 255), weapon_tab_rect, 4)
        else:
            pygame.draw.rect(screen, (255, 255, 255), weapon_tab_rect, 3)
    else:
        pygame.draw.rect(screen, (255, 255, 255), weapon_tab_rect, 3)
    
    pygame.draw.rect(screen, consume_color, consume_tab_rect)
    
    if inventory_state["selected_area"] == "tabs":
        if inventory_state["selected_tab_index"] == 1:
            pygame.draw.rect(screen, (100, 150, 255), consume_tab_rect, 4)
        else:
            pygame.draw.rect(screen, (255, 255, 255), consume_tab_rect, 3)
    else:
        pygame.draw.rect(screen, (255, 255, 255), consume_tab_rect, 3)
    
    weapon_text = font_small.render("무기", True, (255, 255, 255))
    consume_text = font_small.render("소비", True, (255, 255, 255))
    
    screen.blit(weapon_text, weapon_text.get_rect(center=weapon_tab_rect.center))
    screen.blit(consume_text, consume_text.get_rect(center=consume_tab_rect.center))
    
    # ===== 아이템 슬롯 영역 =====
    slots_start_y = tab_area_y + tab_button_height + 15
    
    if inventory_state["current_tab"] == "weapon":
        # 장착템 영역 (빨간 테두리)
        equipped_area_x = tab_area_x - 10
        equipped_area_y = slots_start_y
        equipped_area_width = slot_size * 6 + slot_gap * 5 + 20
        equipped_area_height = slot_size + 20
        
        equipped_rect = pygame.Rect(equipped_area_x, equipped_area_y, equipped_area_width, equipped_area_height)
        pygame.draw.rect(screen, (50, 50, 60), equipped_rect)
        pygame.draw.rect(screen, (100, 100, 120), equipped_rect, 4)
        
        # 장착 슬롯 그리기
        for col in range(6):
            slot_x = equipped_area_x + 10 + col * (slot_size + slot_gap)
            slot_y = equipped_area_y + 10
            
            is_unlocked = col < inventory_state["max_equipped_slots"]
            is_selected = (inventory_state["selected_area"] == "slots" and 
                          inventory_state["selected_row"] == 0 and 
                          inventory_state["selected_col"] == col)
            
            draw_slot(screen, slot_x, slot_y, slot_size, is_unlocked, is_selected, 
                     player_inventory["equipped_weapons"][col] if col < len(player_inventory["equipped_weapons"]) else None)
        
        # 보유템 영역
        inventory_area_y = equipped_area_y + equipped_area_height + 15
        
        for row in range(3):
            for col in range(6):
                slot_x = tab_area_x + col * (slot_size + slot_gap)
                slot_y = inventory_area_y + row * (slot_size + slot_gap)
                
                slot_index = row * 6 + col + (inventory_state["weapon_page"] * 18)
                is_unlocked = slot_index < inventory_state["max_inventory_slots"]
                is_selected = (inventory_state["selected_area"] == "slots" and 
                              inventory_state["selected_row"] == row + 1 and 
                              inventory_state["selected_col"] == col)
                
                item = player_inventory["weapons"][slot_index] if slot_index < len(player_inventory["weapons"]) else None
                draw_slot(screen, slot_x, slot_y, slot_size, is_unlocked, is_selected, item)
        
        # 페이지 버튼 (아래쪽): [이전] [페이지 정보] [다음]
        max_weapon_pages = max(1, (inventory_state["max_inventory_slots"] + 17) // 18)  # 3*6=18칸
        page_button_y = inventory_area_y + 3 * (slot_size + slot_gap) + 10
        page_button_width = 80
        page_button_height = 40
        page_button_gap = 20
        
        # 중앙 정렬을 위한 시작 X 좌표
        total_width = page_button_width * 2 + 150 + page_button_gap * 2
        page_buttons_start_x = tab_area_x + (6 * (slot_size + slot_gap) - total_width) // 2
        
        # [이전] 버튼
        prev_button_rect = pygame.Rect(page_buttons_start_x, page_button_y, page_button_width, page_button_height)
        is_prev_selected = (inventory_state["selected_area"] == "pages" and inventory_state["selected_col"] == 0)
        can_go_prev = inventory_state["weapon_page"] > 0
        
        if can_go_prev:
            prev_bg = (70, 80, 90) if not is_prev_selected else (90, 100, 110)
            prev_border = (150, 150, 250) if is_prev_selected else (180, 180, 200)
            prev_text_color = (255, 255, 255)
        else:
            prev_bg = (40, 40, 50)
            prev_border = (80, 80, 100)
            prev_text_color = (100, 100, 100)
        
        pygame.draw.rect(screen, prev_bg, prev_button_rect)
        pygame.draw.rect(screen, prev_border, prev_button_rect, 4 if is_prev_selected else 2)
        prev_text = font_small.render("이전", True, prev_text_color)
        prev_text_rect = prev_text.get_rect(center=prev_button_rect.center)
        screen.blit(prev_text, prev_text_rect)
        
        # 페이지 정보 (중앙)
        page_info_x = page_buttons_start_x + page_button_width + page_button_gap
        page_info_rect = pygame.Rect(page_info_x, page_button_y, 150, page_button_height)
        pygame.draw.rect(screen, (60, 60, 70), page_info_rect)
        pygame.draw.rect(screen, (100, 100, 120), page_info_rect, 2)
        
        page_info_text = font_small.render(f"{inventory_state['weapon_page'] + 1} / {max_weapon_pages}", True, (200, 200, 200))
        page_info_text_rect = page_info_text.get_rect(center=page_info_rect.center)
        screen.blit(page_info_text, page_info_text_rect)
        
        # [다음] 버튼
        next_button_x = page_info_x + 150 + page_button_gap
        next_button_rect = pygame.Rect(next_button_x, page_button_y, page_button_width, page_button_height)
        is_next_selected = (inventory_state["selected_area"] == "pages" and inventory_state["selected_col"] == 1)
        can_go_next = inventory_state["weapon_page"] < max_weapon_pages - 1
        
        if can_go_next:
            next_bg = (70, 80, 90) if not is_next_selected else (90, 100, 110)
            next_border = (150, 150, 250) if is_next_selected else (180, 180, 200)
            next_text_color = (255, 255, 255)
        else:
            next_bg = (40, 40, 50)
            next_border = (80, 80, 100)
            next_text_color = (100, 100, 100)
        
        pygame.draw.rect(screen, next_bg, next_button_rect)
        pygame.draw.rect(screen, next_border, next_button_rect, 4 if is_next_selected else 2)
        next_text = font_small.render("다음", True, next_text_color)
        next_text_rect = next_text.get_rect(center=next_button_rect.center)
        screen.blit(next_text, next_text_rect)
    
    else:  # consume 탭
        consume_area_y = slots_start_y
        max_pages = max(1, (len(player_inventory["consumables"]) + 29) // 30)  # 5*6=30칸
        
        # 5x6 아이템 슬롯
        for row in range(5):
            for col in range(6):
                slot_x = tab_area_x + col * (slot_size + slot_gap)
                slot_y = consume_area_y + row * (slot_size + slot_gap)
                
                slot_index = row * 6 + col + (inventory_state["consume_page"] * 30)
                is_selected = (inventory_state["selected_area"] == "slots" and 
                              inventory_state["selected_row"] == row and 
                              inventory_state["selected_col"] == col)
                
                item = player_inventory["consumables"][slot_index] if slot_index < len(player_inventory["consumables"]) else None
                draw_slot(screen, slot_x, slot_y, slot_size, True, is_selected, item)
        
        # 페이지 버튼 (아래쪽): [이전] [페이지 정보] [다음]
        page_button_y = consume_area_y + 5 * (slot_size + slot_gap) + 10
        page_button_width = 80
        page_button_height = 40
        page_button_gap = 20
        
        # 중앙 정렬을 위한 시작 X 좌표
        total_width = page_button_width * 2 + 150 + page_button_gap * 2  # 이전 + 정보 + 다음
        page_buttons_start_x = tab_area_x + (6 * (slot_size + slot_gap) - total_width) // 2
        
        # [이전] 버튼
        prev_button_rect = pygame.Rect(page_buttons_start_x, page_button_y, page_button_width, page_button_height)
        is_prev_selected = (inventory_state["selected_area"] == "pages" and inventory_state["selected_col"] == 0)
        can_go_prev = inventory_state["consume_page"] > 0
        
        if can_go_prev:
            prev_bg = (70, 80, 90) if not is_prev_selected else (90, 100, 110)
            prev_border = (150, 150, 250) if is_prev_selected else (180, 180, 200)  # 선택 시 파란색, 평소 밝은 회색
            prev_text_color = (255, 255, 255)
        else:
            prev_bg = (40, 40, 50)
            prev_border = (80, 80, 100)
            prev_text_color = (100, 100, 100)
        
        pygame.draw.rect(screen, prev_bg, prev_button_rect)
        pygame.draw.rect(screen, prev_border, prev_button_rect, 4 if is_prev_selected else 2)
        prev_text = font_small.render("이전", True, prev_text_color)
        prev_text_rect = prev_text.get_rect(center=prev_button_rect.center)
        screen.blit(prev_text, prev_text_rect)
        
        # 페이지 정보 (중앙)
        page_info_x = page_buttons_start_x + page_button_width + page_button_gap
        page_info_rect = pygame.Rect(page_info_x, page_button_y, 150, page_button_height)
        pygame.draw.rect(screen, (60, 60, 70), page_info_rect)
        pygame.draw.rect(screen, (100, 100, 120), page_info_rect, 2)
        
        page_info_text = font_small.render(f"{inventory_state['consume_page'] + 1} / {max_pages}", True, (200, 200, 200))
        page_info_text_rect = page_info_text.get_rect(center=page_info_rect.center)
        screen.blit(page_info_text, page_info_text_rect)
        
        # [다음] 버튼
        next_button_x = page_info_x + 150 + page_button_gap
        next_button_rect = pygame.Rect(next_button_x, page_button_y, page_button_width, page_button_height)
        is_next_selected = (inventory_state["selected_area"] == "pages" and inventory_state["selected_col"] == 1)
        can_go_next = inventory_state["consume_page"] < max_pages - 1
        
        if can_go_next:
            next_bg = (70, 80, 90) if not is_next_selected else (90, 100, 110)
            next_border = (150, 150, 250) if is_next_selected else (180, 180, 200)  # 선택 시 파란색, 평소 밝은 회색
            next_text_color = (255, 255, 255)
        else:
            next_bg = (40, 40, 50)
            next_border = (80, 80, 100)
            next_text_color = (100, 100, 100)
        
        pygame.draw.rect(screen, next_bg, next_button_rect)
        pygame.draw.rect(screen, next_border, next_button_rect, 4 if is_next_selected else 2)
        next_text = font_small.render("다음", True, next_text_color)
        next_text_rect = next_text.get_rect(center=next_button_rect.center)
        screen.blit(next_text, next_text_rect)
    
    # ===== 정보 화면 표시 (최우선) =====
    if inventory_state["info_screen_open"]:
        draw_info_screen(screen, font_main, font_small, WIDTH, HEIGHT)
    
    # ===== 무기 선택 화면 표시 =====
    if inventory_state["weapon_select_open"]:
        draw_weapon_select_screen(screen, font_main, font_small, WIDTH, HEIGHT)
    
    # ===== 액션 메뉴 표시 =====
    if inventory_state["action_menu_open"]:
        draw_action_menu(screen, font_small, WIDTH, HEIGHT)
    
    # ===== 메시지 표시 (최최상위 - 모든 화면 위에) =====
    if inventory_state["message"]:
        # 텍스트 박스
        box_width = WIDTH - 100
        box_height = 100
        box_x = 50
        box_y = HEIGHT - 150
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (20, 20, 20), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
        
        # 텍스트 줄바꿈 처리
        max_text_width = box_width - 40
        lines = wrap_text(inventory_state["message"], font_small, max_text_width)
        
        # 여러 줄 렌더링
        y_offset = box_y + 20
        for line in lines:
            text_surface = font_small.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (box_x + 20, y_offset))
            y_offset += 30
        
        inventory_state["message_timer"] += dt
        if inventory_state["message_timer"] > 2:
            inventory_state["message"] = ""
            inventory_state["message_timer"] = 0


def draw_info_screen(screen, font_main, font_small, WIDTH, HEIGHT):
    """무기 정보 상세 화면"""
    item = inventory_state["info_screen_item"]
    if not item:
        return
    
    # 배경 (어두운 반투명)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(240)
    overlay.fill((20, 20, 30))
    screen.blit(overlay, (0, 0))
    
    # 스탯용 작은 폰트 생성 (font_small보다 작게)
    import os
    FONT_PATH = os.path.join("resources", "font", "DOSGothic.ttf")
    font_stat = pygame.font.Font(FONT_PATH, 20)
    
    # 4등분 사각형 크기 및 위치 - 간격 = 여백으로 통일
    margin = 25
    gap = 25  # 박스 간격 = 여백과 동일
    box_width = (WIDTH - 2 * margin - gap) // 2
    box_height = (HEIGHT - 2 * margin - gap) // 2
    
    # 4개 사각형 위치
    positions = [
        (margin, margin),  # 좌상
        (margin + box_width + gap, margin),  # 우상
        (margin, margin + box_height + gap),  # 좌하
        (margin + box_width + gap, margin + box_height + gap)  # 우하
    ]
    
    # 무기 스킬 가져오기 (skill_ids 사용)
    weapon_skills = []
    if hasattr(item, 'skill_ids'):  # 무기인 경우
        from scripts.skills import ALL_SKILLS
        for skill_id in item.skill_ids:
            if skill_id in ALL_SKILLS:
                weapon_skills.append(ALL_SKILLS[skill_id])
    
    # 4개 박스 그리기
    for i, pos in enumerate(positions):
        box_rect = pygame.Rect(pos[0], pos[1], box_width, box_height)
        
        # 배경
        pygame.draw.rect(screen, (40, 40, 50), box_rect)
        pygame.draw.rect(screen, (100, 100, 120), box_rect, 4)
        
        # 스킬 정보 표시
        if i < len(weapon_skills):
            skill = weapon_skills[i]
            
            # 스킬 이름 (작은 폰트 사용)
            skill_name_text = font_small.render(skill.name, True, (255, 255, 100))
            skill_name_rect = skill_name_text.get_rect(centerx=pos[0] + box_width // 2, y=pos[1] + 20)
            screen.blit(skill_name_text, skill_name_rect)
            
            # 구분선
            line_y = pos[1] + 55
            pygame.draw.line(screen, (100, 100, 120), 
                           (pos[0] + 20, line_y), 
                           (pos[0] + box_width - 20, line_y), 2)
            
            # 스킬 정보 (왼쪽 정렬, 작은 폰트)
            info_x = pos[0] + 30
            info_y = line_y + 20
            
            # 공격력 (작은 폰트)
            power_text = font_stat.render(f"공격력: {skill.power}", True, (255, 100, 100))
            screen.blit(power_text, (info_x, info_y))
            info_y += 25
            
            # 우선도 (작은 폰트)
            priority_text = font_stat.render(f"우선도: {skill.priority}", True, (100, 200, 255))
            screen.blit(priority_text, (info_x, info_y))
            info_y += 25
            
            # 소모량 (작은 폰트)
            durability_text = font_stat.render(f"소모량: {skill.durability_cost}", True, (255, 200, 100))
            screen.blit(durability_text, (info_x, info_y))
            info_y += 35
            
            # 설명 (줄바꿈, font_stat 사용)
            desc_lines = wrap_info_text(skill.description, font_stat, box_width - 60)
            for line in desc_lines:
                desc_text = font_stat.render(line, True, (180, 180, 180))
                screen.blit(desc_text, (info_x, info_y))
                info_y += 28
        else:
            # 빈 슬롯
            empty_text = font_small.render("스킬 없음", True, (100, 100, 100))
            empty_rect = empty_text.get_rect(center=box_rect.center)
            screen.blit(empty_text, empty_rect)


def wrap_info_text(text, font, max_width):
    """정보 화면용 텍스트 줄바꿈"""
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
    
    return lines




def draw_weapon_select_screen(screen, font_main, font_small, WIDTH, HEIGHT):
    """무기 선택 화면 (수리 키트 사용 시) - 장착무기만 표시"""
    # 배경 (어두운 반투명)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(240)
    overlay.fill((20, 20, 30))
    screen.blit(overlay, (0, 0))
    
    # 중앙 패널
    panel_width = 600
    panel_height = 520
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (40, 40, 50), panel_rect)
    pygame.draw.rect(screen, (100, 100, 120), panel_rect, 4)
    
    # 제목
    title_text = font_main.render("수리할 무기 선택", True, (255, 255, 255))
    title_rect = title_text.get_rect(centerx=WIDTH // 2, y=panel_y + 20)
    screen.blit(title_text, title_rect)
    
    # 선택된 수리 키트 정보
    item = inventory_state["weapon_select_consumable"]
    if item:
        item_info = font_small.render(f"사용: {item.name} (수리량: +{item.effect_value})", True, (100, 200, 255))
        item_info_rect = item_info.get_rect(centerx=WIDTH // 2, y=panel_y + 80)
        screen.blit(item_info, item_info_rect)
    
    # 장착 무기 목록만 사용 (항상 6개 슬롯 표시)
    weapons = player_inventory["equipped_weapons"]
    
    slot_width = 520
    slot_height = 55
    slot_gap = 8
    start_y = panel_y + 125
    
    import os
    FONT_PATH = os.path.join("resources", "font", "DOSGothic.ttf")
    font_stat = pygame.font.Font(FONT_PATH, 20)
    
    for i in range(6):
        slot_y = start_y + i * (slot_height + slot_gap)
        slot_x = panel_x + (panel_width - slot_width) // 2
        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
        
        is_selected = (inventory_state["weapon_select_index"] == i)
        
        # 무기가 있는지 확인
        has_weapon = i < len(weapons)
        
        if has_weapon:
            weapon = weapons[i]
            bg_color = (70, 80, 90)
            border_color = (150, 150, 250) if is_selected else (180, 180, 200)
        else:
            bg_color = (40, 40, 50)
            border_color = (80, 80, 100)
        
        border_width = 4 if is_selected else 2
        
        pygame.draw.rect(screen, bg_color, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, border_width)
        
        if has_weapon:
            weapon = weapons[i]
            
            # 무기 이미지
            img_size = 45
            img_x = slot_x + 8
            img_y = slot_y + 5
            
            try:
                if hasattr(weapon, 'image_path') and weapon.image_path:
                    weapon_img = pygame.image.load(weapon.image_path).convert_alpha()
                    weapon_img = pygame.transform.scale(weapon_img, (img_size, img_size))
                    screen.blit(weapon_img, (img_x, img_y))
                else:
                    pygame.draw.rect(screen, (100, 100, 100), (img_x, img_y, img_size, img_size))
            except:
                pygame.draw.rect(screen, (100, 100, 100), (img_x, img_y, img_size, img_size))
            
            # 무기 이름 (왼쪽)
            info_x = img_x + img_size + 12
            info_y = slot_y + (slot_height // 2) - 10
            
            name_text = font_small.render(weapon.name, True, (255, 255, 255))
            screen.blit(name_text, (info_x, info_y))
            
            # 내구도 (오른쪽 정렬)
            durability_str = f"{weapon.durability}/{weapon.max_durability}"
            durability_text = font_small.render(durability_str, True, (100, 200, 255))
            durability_x = slot_x + slot_width - durability_text.get_width() - 10
            screen.blit(durability_text, (durability_x, info_y))
        else:
            # 빈 슬롯 표시
            empty_text = font_small.render("빈 슬롯", True, (100, 100, 100))
            empty_rect = empty_text.get_rect(center=slot_rect.center)
            screen.blit(empty_text, empty_rect)


def draw_action_menu(screen, font_small, WIDTH, HEIGHT):
    """액션 메뉴 그리기"""
    # 메뉴 크기 및 위치
    menu_width = 200
    menu_height = 150
    menu_x = (WIDTH - menu_width) // 2
    menu_y = (HEIGHT - menu_height) // 2
    
    # 배경
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    border_width = 4
    pygame.draw.rect(screen, (40, 40, 50), menu_rect)
    pygame.draw.rect(screen, (100, 100, 120), menu_rect, border_width)
    
    # 버튼 옵션
    is_equipped = inventory_state["action_menu_is_equipped"]
    if is_equipped:
        options = ["해제", "스킬", "취소"]
    else:
        options = ["장착", "스킬", "취소"]
    
    button_height = 35
    button_gap = 10
    side_margin = 20  # 좌우 여백
    
    # 전체 버튼 높이 계산
    total_buttons_height = len(options) * button_height + (len(options) - 1) * button_gap
    
    # 사용 가능한 세로 공간 (테두리 제외)
    available_height = menu_height - 2 * border_width
    
    # 중앙 정렬 (위아래 간격 동일)
    top_margin = (available_height - total_buttons_height) // 2
    start_y = menu_y + border_width + top_margin
    
    for i, option in enumerate(options):
        button_y = start_y + i * (button_height + button_gap)
        button_rect = pygame.Rect(menu_x + side_margin, button_y, menu_width - 2 * side_margin, button_height)
        
        # 선택된 버튼
        is_selected = (inventory_state["action_menu_selected"] == i)
        
        if is_selected:
            bg_color = (70, 80, 90)
            border_color = (150, 150, 250)
            btn_border_width = 4
        else:
            bg_color = (50, 50, 60)
            border_color = (100, 100, 120)
            btn_border_width = 2
        
        pygame.draw.rect(screen, bg_color, button_rect)
        pygame.draw.rect(screen, border_color, button_rect, btn_border_width)
        
        # 텍스트
        text_surface = font_small.render(option, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)


def draw_slot(screen, x, y, size, is_unlocked, is_selected, item):
    """개별 슬롯 그리기"""
    slot_rect = pygame.Rect(x, y, size, size)
    
    # 배경
    if is_unlocked:
        pygame.draw.rect(screen, (60, 60, 70), slot_rect)
    else:
        pygame.draw.rect(screen, (30, 30, 35), slot_rect)
    
    # 선택 테두리 (파란색)
    if is_selected:
        pygame.draw.rect(screen, (100, 150, 255), slot_rect, 4)
    else:
        pygame.draw.rect(screen, (100, 100, 120), slot_rect, 2)
    
    # 아이템 이미지 표시
    if item and is_unlocked:
        try:
            if hasattr(item, 'id'):  # 무기
                # image_path가 있으면 사용, 없으면 기본 표시
                if hasattr(item, 'image_path') and item.image_path:
                    item_img = pygame.image.load(item.image_path).convert_alpha()
                    item_img = pygame.transform.scale(item_img, (size - 10, size - 10))
                    screen.blit(item_img, (x + 5, y + 5))
                else:
                    # 이미지 경로가 없으면 기본 표시
                    pygame.draw.rect(screen, (100, 100, 150), (x + 10, y + 10, size - 20, size - 20))

        except:
            # 이미지 로드 실패 시 기본 표시
            pygame.draw.rect(screen, (100, 100, 150), (x + 10, y + 10, size - 20, size - 20))


def get_selected_item(battle_player):
    """현재 선택된 아이템 반환"""
    if inventory_state["selected_area"] == "tabs":
        return None
    
    if inventory_state["current_tab"] == "weapon":
        if inventory_state["selected_row"] == 0:  # 장착템
            col = inventory_state["selected_col"]
            if col < len(player_inventory["equipped_weapons"]):
                return player_inventory["equipped_weapons"][col]
        else:  # 보유템
            row = inventory_state["selected_row"] - 1
            col = inventory_state["selected_col"]
            index = row * 6 + col + (inventory_state["weapon_page"] * 18)
            if index < len(player_inventory["weapons"]):
                return player_inventory["weapons"][index]
    else:  # consume
        row = inventory_state["selected_row"]
        col = inventory_state["selected_col"]
        index = row * 6 + col + (inventory_state["consume_page"] * 30)
        if index < len(player_inventory["consumables"]):
            return player_inventory["consumables"][index]
    return None


def handle_inventory_input(events, battle_player):
    """인벤토리 입력 처리
    
    Returns:
        bool: 이벤트가 완전히 처리되었는지 여부 (True면 main.py에서 추가 처리 안 함)
    """
    for event in events:
        if event.type == pygame.KEYDOWN:
            # 무기 선택 화면이 열려있을 때
            if inventory_state["weapon_select_open"]:
                # 장착 무기만 사용
                equipped_weapons = player_inventory["equipped_weapons"]
                
                if event.key == pygame.K_w:
                    # 위로 이동
                    inventory_state["weapon_select_index"] = max(0, inventory_state["weapon_select_index"] - 1)
                elif event.key == pygame.K_s:
                    # 아래로 이동 (장착무기 수 -1 또는 최대 5)
                    max_index = min(len(equipped_weapons) - 1, 5)
                    inventory_state["weapon_select_index"] = min(max_index, inventory_state["weapon_select_index"] + 1)
                elif event.key == pygame.K_RETURN:
                    # 무기 선택
                    if equipped_weapons and inventory_state["weapon_select_index"] < len(equipped_weapons):
                        selected_weapon = equipped_weapons[inventory_state["weapon_select_index"]]
                        consumable = inventory_state["weapon_select_consumable"]
                        
                        # 내구도가 이미 최대인지 확인
                        if selected_weapon.durability >= selected_weapon.max_durability:
                            inventory_state["message"] = "내구도가 이미 최대입니다!"
                            inventory_state["message_timer"] = 0
                            # 화면은 유지 (닫지 않음)
                        elif consumable:
                            success, message = consumable.use(selected_weapon)
                            if success:
                                # 소모품 제거
                                if consumable in player_inventory["consumables"]:
                                    player_inventory["consumables"].remove(consumable)
                            inventory_state["message"] = message
                            inventory_state["message_timer"] = 0
                            
                            # 사용 성공 시 무기 선택 화면 닫기
                            inventory_state["weapon_select_open"] = False
                            inventory_state["weapon_select_index"] = 0
                            inventory_state["weapon_select_consumable"] = None
                    return True
                
                elif event.key == pygame.K_ESCAPE:
                    # 무기 선택 취소
                    inventory_state["weapon_select_open"] = False
                    inventory_state["weapon_select_index"] = 0
                    inventory_state["weapon_select_consumable"] = None
                    return True
                
                return True  # 다른 입력 무시
            
            # 정보 화면이 열려있을 때
            if inventory_state["info_screen_open"]:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    # ESC 또는 Enter로 정보 화면 닫기
                    inventory_state["info_screen_open"] = False
                    inventory_state["info_screen_item"] = None
                    return True  # 이벤트 완전히 처리됨
                # 정보 화면이 열려있으면 다른 입력 무시
                return True  # 이벤트 완전히 처리됨
            
            # 액션 메뉴가 열려있을 때
            if inventory_state["action_menu_open"]:
                if event.key == pygame.K_w:
                    # 위로 이동
                    inventory_state["action_menu_selected"] = max(0, inventory_state["action_menu_selected"] - 1)
                elif event.key == pygame.K_s:
                    # 아래로 이동
                    inventory_state["action_menu_selected"] = min(2, inventory_state["action_menu_selected"] + 1)
                elif event.key == pygame.K_RETURN:
                    # 선택 실행
                    selected_option = inventory_state["action_menu_selected"]
                    
                    if selected_option == 0:  # 장착/해제
                        if inventory_state["action_menu_is_equipped"]:
                            # 해제
                            unequip_weapon(battle_player)
                        else:
                            # 장착
                            equip_weapon(battle_player)
                    elif selected_option == 1:  # 정보
                        show_item_info()
                    elif selected_option == 2:  # 취소
                        pass  # 아무것도 하지 않음
                    
                    # 메뉴 닫기
                    inventory_state["action_menu_open"] = False
                    inventory_state["action_menu_selected"] = 0
                    inventory_state["action_menu_item"] = None
                
                elif event.key == pygame.K_ESCAPE:
                    # ESC로 메뉴 닫기
                    inventory_state["action_menu_open"] = False
                    inventory_state["action_menu_selected"] = 0
                    inventory_state["action_menu_item"] = None
                
                # 액션 메뉴가 열려있으면 다른 입력 무시
                continue
            
            # 일반 입력 처리 (액션 메뉴가 닫혀있을 때)
            # WASD로 슬롯 이동
            if event.key == pygame.K_w:
                move_selection(-1, 0)
            elif event.key == pygame.K_s:
                move_selection(1, 0)
            elif event.key == pygame.K_a:
                move_selection(0, -1)
            elif event.key == pygame.K_d:
                move_selection(0, 1)
            
            # 엔터: 액션 메뉴 열기 또는 탭 전환
            elif event.key == pygame.K_RETURN:
                if inventory_state["selected_area"] == "tabs":
                    # 탭 전환 (선택 영역과 위치 모두 유지)
                    if inventory_state["selected_tab_index"] == 0:
                        inventory_state["current_tab"] = "weapon"
                    else:
                        inventory_state["current_tab"] = "consume"
                    # selected_area, row, col 모두 그대로 유지
                elif inventory_state["current_tab"] == "weapon":
                    if inventory_state["selected_area"] == "pages":
                        # 페이지 버튼 클릭 시
                        max_weapon_pages = max(1, (inventory_state["max_inventory_slots"] + 17) // 18)
                        
                        if inventory_state["selected_col"] == 0:  # 이전 버튼
                            if inventory_state["weapon_page"] > 0:
                                inventory_state["weapon_page"] -= 1
                        elif inventory_state["selected_col"] == 1:  # 다음 버튼
                            if inventory_state["weapon_page"] < max_weapon_pages - 1:
                                inventory_state["weapon_page"] += 1
                    else:
                        # 무기 탭: 액션 메뉴 열기
                        item = get_selected_item(battle_player)
                        if item:
                            inventory_state["action_menu_open"] = True
                            inventory_state["action_menu_selected"] = 0
                            inventory_state["action_menu_item"] = item
                            inventory_state["action_menu_is_equipped"] = (inventory_state["selected_row"] == 0)
                elif inventory_state["current_tab"] == "consume":
                    if inventory_state["selected_area"] == "pages":
                        # 페이지 버튼 클릭 시
                        max_pages = max(1, (len(player_inventory["consumables"]) + 29) // 30)
                        
                        if inventory_state["selected_col"] == 0:  # 이전 버튼
                            if inventory_state["consume_page"] > 0:
                                inventory_state["consume_page"] -= 1
                                # 선택 위치 유지 (슬롯으로 돌아가지 않음)
                        elif inventory_state["selected_col"] == 1:  # 다음 버튼
                            if inventory_state["consume_page"] < max_pages - 1:
                                inventory_state["consume_page"] += 1
                                # 선택 위치 유지 (슬롯으로 돌아가지 않음)
                    else:
                        use_consumable(battle_player)
    
    return False  # 이벤트가 처리되지 않음 (main.py에서 추가 처리 가능)


def move_selection(d_row, d_col):
    """선택 슬롯 이동"""
    if inventory_state["selected_area"] == "tabs":
        # 탭 영역에서 이동
        if d_col != 0:
            new_index = inventory_state["selected_tab_index"] + d_col
            if 0 <= new_index <= 1:
                inventory_state["selected_tab_index"] = new_index
        
        # 아래로 이동하면 슬롯 영역으로
        if d_row > 0:
            inventory_state["selected_area"] = "slots"
            if inventory_state["current_tab"] == "weapon":
                inventory_state["selected_row"] = 0  # 장착템으로 이동
            else:
                inventory_state["selected_row"] = 0
            inventory_state["selected_col"] = 0
    
    elif inventory_state["current_tab"] == "weapon":
        if inventory_state["selected_area"] == "slots":
            max_row = 3  # 0: 장착, 1~3: 보유
            max_col = 5
            
            new_row = inventory_state["selected_row"] + d_row
            new_col = inventory_state["selected_col"] + d_col
            
            # 위로 이동 시 탭으로
            if new_row < 0:
                inventory_state["selected_area"] = "tabs"
                inventory_state["selected_tab_index"] = 0  # 무기 탭
                return
            
            # 아래로 이동 시 페이지 버튼으로
            if new_row > max_row:
                inventory_state["selected_area"] = "pages"
                inventory_state["selected_col"] = 0
                return
            
            # 행 범위 체크
            if 0 <= new_row <= max_row:
                inventory_state["selected_row"] = new_row
            
            # 열 범위 체크
            if 0 <= new_col <= max_col:
                inventory_state["selected_col"] = new_col
        
        elif inventory_state["selected_area"] == "pages":
            # 페이지 버튼 영역에서 이동 (0=이전, 1=다음)
            
            # 위로 이동 시 슬롯으로
            if d_row < 0:
                inventory_state["selected_area"] = "slots"
                inventory_state["selected_row"] = 3  # 마지막 행
                return
            
            # 좌우 이동 (이전/다음 버튼 사이)
            if d_col != 0:
                new_col = inventory_state["selected_col"] + d_col
                if 0 <= new_col <= 1:  # 0=이전, 1=다음
                    inventory_state["selected_col"] = new_col
    
    else:  # consume
        if inventory_state["selected_area"] == "slots":
            # 슬롯 영역에서 이동
            max_row = 4  # 0~4 = 5행
            max_col = 5  # 0~5 = 6열
            
            new_row = inventory_state["selected_row"] + d_row
            new_col = inventory_state["selected_col"] + d_col
            
            # 위로 이동 시 탭으로
            if new_row < 0:
                inventory_state["selected_area"] = "tabs"
                inventory_state["selected_tab_index"] = 1  # 소비 탭
                return
            
            # 아래로 이동 시 페이지 슬롯으로
            if new_row > max_row:
                inventory_state["selected_area"] = "pages"
                inventory_state["selected_col"] = 0
                return
            
            if 0 <= new_row <= max_row:
                inventory_state["selected_row"] = new_row
            
            if 0 <= new_col <= max_col:
                inventory_state["selected_col"] = new_col
        
        elif inventory_state["selected_area"] == "pages":
            # 페이지 버튼 영역에서 이동 (0=이전, 1=다음)
            
            # 위로 이동 시 슬롯으로
            if d_row < 0:
                inventory_state["selected_area"] = "slots"
                inventory_state["selected_row"] = 4  # 마지막 행
                return
            
            # 좌우 이동 (이전/다음 버튼 사이)
            if d_col != 0:
                new_col = inventory_state["selected_col"] + d_col
                if 0 <= new_col <= 1:  # 0=이전, 1=다음
                    inventory_state["selected_col"] = new_col


def equip_weapon(battle_player):
    """무기 장착"""
    row = inventory_state["selected_row"] - 1
    col = inventory_state["selected_col"]
    index = row * 6 + col + (inventory_state["weapon_page"] * 18)
    
    if index < len(player_inventory["weapons"]):
        weapon = player_inventory["weapons"][index]
        
        # 장착 공간 체크
        if len(player_inventory["equipped_weapons"]) >= inventory_state["max_equipped_slots"]:
            inventory_state["message"] = "장착한 무기가 너무 많습니다!"
            return
        
        # 장착 처리
        player_inventory["weapons"].pop(index)
        player_inventory["equipped_weapons"].append(weapon)
        
        # battle_player 무기 업데이트 (첫 번째 장착 무기 사용)
        battle_player.equip_weapon(player_inventory["equipped_weapons"][0])
        inventory_state["message"] = f"{weapon.name} 장착!"


def unequip_weapon(battle_player):
    """무기 해제"""
    col = inventory_state["selected_col"]
    if col < len(player_inventory["equipped_weapons"]):
        weapon = player_inventory["equipped_weapons"][col]
        
        # 인벤토리 공간 체크
        if len(player_inventory["weapons"]) >= inventory_state["max_inventory_slots"]:
            inventory_state["message"] = "인벤토리 공간이 부족합니다!"
            return
        
        # 해제 처리
        player_inventory["equipped_weapons"].pop(col)
        player_inventory["weapons"].insert(0, weapon)  # 맨 앞에 추가
        
        # battle_player 무기 업데이트
        if battle_player.weapon == weapon:
            if player_inventory["equipped_weapons"]:
                battle_player.equip_weapon(player_inventory["equipped_weapons"][0])
            else:
                battle_player.weapon = None
        
        inventory_state["message"] = f"{weapon.name} 해제!"


def show_item_info():
    """아이템 정보 표시"""
    item = inventory_state["action_menu_item"]
    if item:
        inventory_state["info_screen_open"] = True
        inventory_state["info_screen_item"] = item


def toggle_equip_weapon(battle_player):
    """무기 장착/해제 토글"""
    if inventory_state["selected_row"] == 0:  # 장착템 영역
        # 해제
        col = inventory_state["selected_col"]
        if col < len(player_inventory["equipped_weapons"]):
            weapon = player_inventory["equipped_weapons"][col]
            
            # 인벤토리 공간 체크
            if len(player_inventory["weapons"]) >= inventory_state["max_inventory_slots"]:
                inventory_state["message"] = "인벤토리 공간이 부족합니다!"
                return
            
            # 해제 처리
            player_inventory["equipped_weapons"].pop(col)
            player_inventory["weapons"].insert(0, weapon)  # 맨 앞에 추가
            
            # battle_player 무기 업데이트
            if battle_player.weapon == weapon:
                if player_inventory["equipped_weapons"]:
                    battle_player.equip_weapon(player_inventory["equipped_weapons"][0])
                else:
                    battle_player.weapon = None
    
    else:  # 보유템 영역
        # 장착
        row = inventory_state["selected_row"] - 1
        col = inventory_state["selected_col"]
        index = row * 6 + col + (inventory_state["weapon_page"] * 18)
        
        if index < len(player_inventory["weapons"]):
            weapon = player_inventory["weapons"][index]
            
            # 장착 공간 체크
            if len(player_inventory["equipped_weapons"]) >= inventory_state["max_equipped_slots"]:
                inventory_state["message"] = "장착한 무기가 너무 많습니다!"
                return
            
            # 장착 처리
            player_inventory["weapons"].pop(index)
            player_inventory["equipped_weapons"].append(weapon)
            
            # battle_player 무기 업데이트 (첫 번째 장착 무기 사용)
            battle_player.equip_weapon(player_inventory["equipped_weapons"][0])


def wrap_text(text, font, max_width):
    """텍스트를 줄바꿈 처리"""
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




def use_consumable(battle_player):
    """소모품 사용"""
    row = inventory_state["selected_row"]
    col = inventory_state["selected_col"]
    index = row * 6 + col + (inventory_state["consume_page"] * 30)
    
    if index >= len(player_inventory["consumables"]):
        inventory_state["message"] = "아이템이 없습니다!"
        inventory_state["message_timer"] = 0
        return
    
    consumable = player_inventory["consumables"][index]
    
    # 소모품 타입에 따라 처리
    if consumable.type == "potion":
        # 포션: 체력이 최대인지 확인
        if battle_player.hp >= battle_player.max_hp:
            inventory_state["message"] = "체력이 이미 최대입니다!"
            inventory_state["message_timer"] = 0
            return
        
        # 플레이어에게 직접 사용
        success, message = consumable.use(battle_player)
        if success:
            # 사용 성공: 인벤토리에서 제거
            player_inventory["consumables"].pop(index)
            inventory_state["message"] = message
        else:
            inventory_state["message"] = message
        inventory_state["message_timer"] = 0
    
    elif consumable.type == "repair_kit":
        # 수리 키트: 무기 선택 화면 열기 (장착무기만)
        equipped_weapons = player_inventory["equipped_weapons"]
        
        if equipped_weapons:
            # 무기 선택 화면 열기
            inventory_state["weapon_select_open"] = True
            inventory_state["weapon_select_index"] = 0
            inventory_state["weapon_select_consumable"] = consumable
        else:
            inventory_state["message"] = "수리할 무기가 없습니다!"
            inventory_state["message_timer"] = 0


def init_inventory(battle_player):
    """인벤토리 초기화 (게임 시작 시 호출)"""
    # 초기 무기를 장착템에 추가
    if battle_player.weapon:
        player_inventory["equipped_weapons"].append(battle_player.weapon)


def is_info_screen_open():
    """정보 화면이 열려있는지 확인"""
    return inventory_state["info_screen_open"]


def is_action_menu_open():
    """액션 메뉴가 열려있는지 확인"""
    return inventory_state["action_menu_open"]


def is_weapon_select_open():
    """무기 선택 화면이 열려있는지 확인"""
    return inventory_state["weapon_select_open"]