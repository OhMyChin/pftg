import pygame

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
    "message_timer": 0
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
        
        # 무기 정보
        if hasattr(selected_item, 'durability'):
            name_text = font_small.render(selected_item.name, True, (255, 255, 255))
            screen.blit(name_text, (info_panel_x + 15, y_offset))
            y_offset += 35
            
            grade_text = font_small.render(f"등급: {selected_item.grade}", True, (200, 200, 100))
            screen.blit(grade_text, (info_panel_x + 15, y_offset))
            y_offset += 30
            
            durability_text = font_small.render(
                f"내구도: {selected_item.durability}/{selected_item.max_durability}", 
                True, (100, 200, 255)
            )
            screen.blit(durability_text, (info_panel_x + 15, y_offset))
            y_offset += 35
            
            y_offset += 8
            desc_lines = wrap_text(selected_item.description, font_tiny, info_panel_width - 30)
            for line in desc_lines:
                desc_text = font_tiny.render(line, True, (180, 180, 180))
                screen.blit(desc_text, (info_panel_x + 15, y_offset))
                y_offset += 22
        
        # 소모품 정보
        elif hasattr(selected_item, 'type'):  # Consumable
            name_text = font_small.render(selected_item.name, True, (255, 255, 255))
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
        
        # 페이지 표시
        if inventory_state["max_inventory_slots"] > 18:
            page_text = font_small.render(f"페이지: {inventory_state['weapon_page'] + 1}/2", True, (200, 200, 200))
            screen.blit(page_text, (tab_area_x, inventory_area_y + 3 * (slot_size + slot_gap) + 10))
        
        # ===== 스킬 버튼 영역 (인벤토리 슬롯 아래) =====
        # 인벤토리 전체 가로 길이
        inventory_total_width = 6 * slot_size + 5 * slot_gap
        
        skill_button_gap = 10
        # 2x2 배치에서 각 버튼의 가로 크기
        skill_button_width = (inventory_total_width - skill_button_gap) // 2
        skill_button_height = 55
        
        skill_start_x = tab_area_x
        skill_start_y = inventory_area_y + 3 * (slot_size + slot_gap) + 10
        
        # 선택된 아이템의 스킬 가져오기
        selected_weapon = get_selected_item(battle_player)
        available_skills = []
        if selected_weapon and hasattr(selected_weapon, 'durability'):
            available_skills = selected_weapon.get_skills()
        
        # 항상 2x2 (4칸) 표시
        for i in range(4):
            row = i // 2
            col = i % 2
            
            skill_rect = pygame.Rect(
                skill_start_x + col * (skill_button_width + skill_button_gap),
                skill_start_y + row * (skill_button_height + skill_button_gap),
                skill_button_width,
                skill_button_height
            )
            
            if i < len(available_skills):
                skill = available_skills[i]
                # 스킬이 있는 경우
                pygame.draw.rect(screen, (70, 80, 90), skill_rect)
                pygame.draw.rect(screen, (150, 150, 250), skill_rect, 2)
                
                # 스킬 이름 (중앙)
                skill_name_text = font_small.render(skill.name, True, (255, 255, 255))
                skill_name_rect = skill_name_text.get_rect(center=skill_rect.center)
                screen.blit(skill_name_text, skill_name_rect)
            else:
                # 빈 슬롯
                pygame.draw.rect(screen, (40, 40, 50), skill_rect)
                pygame.draw.rect(screen, (80, 80, 100), skill_rect, 2)
    
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
    
    # ===== 메시지 표시 =====
    if inventory_state["message"]:
        msg_text = font_small.render(inventory_state["message"], True, (255, 100, 100))
        msg_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        screen.blit(msg_text, msg_rect)
        
        inventory_state["message_timer"] += dt
        if inventory_state["message_timer"] > 2:
            inventory_state["message"] = ""
            inventory_state["message_timer"] = 0


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
    """인벤토리 입력 처리"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            # WASD로 슬롯 이동
            if event.key == pygame.K_w:
                move_selection(-1, 0)
            elif event.key == pygame.K_s:
                move_selection(1, 0)
            elif event.key == pygame.K_a:
                move_selection(0, -1)
            elif event.key == pygame.K_d:
                move_selection(0, 1)
            
            # 엔터: 장착/해제 또는 탭 전환
            elif event.key == pygame.K_RETURN:
                if inventory_state["selected_area"] == "tabs":
                    # 탭 전환 (선택 영역과 위치 모두 유지)
                    if inventory_state["selected_tab_index"] == 0:
                        inventory_state["current_tab"] = "weapon"
                    else:
                        inventory_state["current_tab"] = "consume"
                    # selected_area, row, col 모두 그대로 유지
                elif inventory_state["current_tab"] == "weapon":
                    toggle_equip_weapon(battle_player)
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
        max_row = 3  # 0: 장착, 1~3: 보유
        max_col = 5
        
        new_row = inventory_state["selected_row"] + d_row
        new_col = inventory_state["selected_col"] + d_col
        
        # 위로 이동 시 탭으로
        if new_row < 0:
            inventory_state["selected_area"] = "tabs"
            inventory_state["selected_tab_index"] = 0  # 무기 탭
            return
        
        # 행 범위 체크
        if 0 <= new_row <= max_row:
            inventory_state["selected_row"] = new_row
        
        # 열 범위 체크
        if 0 <= new_col <= max_col:
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
        # 포션: 플레이어에게 직접 사용
        success, message = consumable.use(battle_player)
        if success:
            # 사용 성공: 인벤토리에서 제거
            player_inventory["consumables"].pop(index)
            inventory_state["message"] = message
        else:
            inventory_state["message"] = message
        inventory_state["message_timer"] = 0
    
    elif consumable.type == "repair_kit":
        # 수리 키트: 무기 선택 필요
        # 일단은 첫 번째 장착 무기에 사용
        if player_inventory["equipped_weapons"]:
            weapon = player_inventory["equipped_weapons"][0]
            success, message = consumable.use(weapon)
            if success:
                # 사용 성공: 인벤토리에서 제거
                player_inventory["consumables"].pop(index)
                inventory_state["message"] = message
            else:
                inventory_state["message"] = message
        else:
            inventory_state["message"] = "수리할 무기가 없습니다!"
        inventory_state["message_timer"] = 0


def init_inventory(battle_player):
    """인벤토리 초기화 (게임 시작 시 호출)"""
    # 초기 무기를 장착템에 추가
    if battle_player.weapon:
        player_inventory["equipped_weapons"].append(battle_player.weapon)