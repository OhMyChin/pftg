import pygame

# 소모품 선택 상태
consume_battle_state = {
    "selected_area": "tabs",  # "tabs" 또는 "slots"
    "selected_tab": 0,  # 0: 포션, 1: 키트
    "selected_slot": 0,  # 세로 스크롤 위치 (0~4)
    "scroll_offset": 0,  # 아이템 리스트 스크롤 오프셋
    "mode": "select_item",  # "select_item" 또는 "select_weapon"
    "selected_consumable": None,
    "selected_weapon_slot": 0,
    "message": "",  # 메시지
    "message_timer": 0,  # 메시지 타이머
}

def reset_consume_battle_state():
    """소모품 선택 상태 초기화"""
    consume_battle_state["selected_area"] = "tabs"
    consume_battle_state["selected_tab"] = 0
    consume_battle_state["selected_slot"] = 0
    consume_battle_state["scroll_offset"] = 0
    consume_battle_state["mode"] = "select_item"
    consume_battle_state["selected_consumable"] = None
    consume_battle_state["selected_weapon_slot"] = 0
    consume_battle_state["message"] = ""
    consume_battle_state["message_timer"] = 0


def draw_consume_battle(screen, font_main, font_small, WIDTH, HEIGHT, battle_player):
    """전투 중 소모품 사용 화면"""
    from scripts.inventory import player_inventory
    
    # 배경 (반투명)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((20, 20, 30))
    screen.blit(overlay, (0, 0))
    
    if consume_battle_state["mode"] == "select_item":
        draw_item_selection(screen, font_main, font_small, WIDTH, HEIGHT, player_inventory)
    elif consume_battle_state["mode"] == "select_weapon":
        draw_weapon_selection(screen, font_main, font_small, WIDTH, HEIGHT, player_inventory)
    
    # ===== 메시지 표시 (최상위) =====
    if consume_battle_state["message"]:
        # 텍스트 박스
        box_width = WIDTH - 100
        box_height = 80
        box_x = 50
        box_y = HEIGHT - 130
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (20, 20, 20), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)
        
        # 메시지 텍스트
        msg_text = font_small.render(consume_battle_state["message"], True, (255, 255, 255))
        screen.blit(msg_text, (box_x + 20, box_y + 25))


def draw_item_selection(screen, font_main, font_small, WIDTH, HEIGHT, player_inventory):
    """아이템 선택 화면 - 왼쪽 정보 패널 + 오른쪽 슬롯"""
    
    # ===== 레이아웃 설정 =====
    left_panel_width = 300
    left_panel_height = 500
    left_panel_x = 50
    left_panel_y = (HEIGHT - left_panel_height) // 2
    
    right_panel_width = 400
    right_panel_height = 500
    right_panel_x = left_panel_x + left_panel_width + 30
    right_panel_y = left_panel_y
    
    # ===== 왼쪽 패널 (정보) =====
    left_rect = pygame.Rect(left_panel_x, left_panel_y, left_panel_width, left_panel_height)
    pygame.draw.rect(screen, (40, 40, 50), left_rect)
    pygame.draw.rect(screen, (100, 100, 120), left_rect, 4)
    
    # 제목
    title_text = font_main.render("정보", True, (255, 255, 255))
    title_rect = title_text.get_rect(centerx=left_panel_x + left_panel_width // 2, y=left_panel_y + 20)
    screen.blit(title_text, title_rect)
    
    # 선택된 아이템 정보 표시
    if consume_battle_state["selected_area"] == "slots":
        # 현재 탭의 아이템 목록
        if consume_battle_state["selected_tab"] == 0:
            items = [item for item in player_inventory["consumables"] if item.type == "potion"]
        else:
            items = [item for item in player_inventory["consumables"] if item.type == "repair_kit"]
        
        # 실제 아이템 인덱스 = scroll_offset + selected_slot
        actual_index = consume_battle_state["scroll_offset"] + consume_battle_state["selected_slot"]
        
        if actual_index < len(items):
            item = items[actual_index]
            
            info_y = left_panel_y + 80
            
            # 아이템 이름
            name_text = font_small.render(item.name, True, (255, 255, 255))
            screen.blit(name_text, (left_panel_x + 20, info_y))
            info_y += 40
            
            # 타입
            type_name = "포션" if item.type == "potion" else "수리 키트"
            type_text = font_small.render(f"종류: {type_name}", True, (200, 200, 100))
            screen.blit(type_text, (left_panel_x + 20, info_y))
            info_y += 35
            
            # 효과
            if item.type == "potion":
                effect_text = font_small.render(f"회복: {item.effect_value} HP", True, (100, 255, 100))
            else:
                effect_text = font_small.render(f"수리: {item.effect_value}", True, (100, 200, 255))
            screen.blit(effect_text, (left_panel_x + 20, info_y))
            info_y += 40
            
            # 설명
            desc_lines = wrap_text(item.description, font_small, left_panel_width - 40)
            for line in desc_lines:
                desc_text = font_small.render(line, True, (180, 180, 180))
                screen.blit(desc_text, (left_panel_x + 20, info_y))
                info_y += 25
    
    # ===== 오른쪽 패널 (탭 + 슬롯) =====
    right_rect = pygame.Rect(right_panel_x, right_panel_y, right_panel_width, right_panel_height)
    pygame.draw.rect(screen, (40, 40, 50), right_rect)
    pygame.draw.rect(screen, (100, 100, 120), right_rect, 4)
    
    # ===== 탭 버튼 =====
    tab_height = 50
    tab_gap = 10
    tab_width = (right_panel_width - 30 - tab_gap) // 2  # 양쪽 여백 15씩
    tab_y = right_panel_y + 10
    
    potion_tab_x = right_panel_x + 15  # 왼쪽 여백 15
    kit_tab_x = potion_tab_x + tab_width + tab_gap
    
    # 포션 탭
    potion_rect = pygame.Rect(potion_tab_x, tab_y, tab_width, tab_height)
    is_potion_selected = (consume_battle_state["selected_area"] == "tabs" and consume_battle_state["selected_tab"] == 0)
    is_potion_active = (consume_battle_state["selected_tab"] == 0)
    
    if is_potion_active:
        potion_bg = (100, 150, 200)
        potion_border = (150, 150, 250) if is_potion_selected else (150, 200, 255)
    else:
        potion_bg = (60, 60, 70)
        potion_border = (100, 100, 120)
    
    pygame.draw.rect(screen, potion_bg, potion_rect)
    pygame.draw.rect(screen, potion_border, potion_rect, 4 if is_potion_selected else 2)
    
    potion_text = font_small.render("포션", True, (255, 255, 255))
    screen.blit(potion_text, potion_text.get_rect(center=potion_rect.center))
    
    # 키트 탭
    kit_rect = pygame.Rect(kit_tab_x, tab_y, tab_width, tab_height)
    is_kit_selected = (consume_battle_state["selected_area"] == "tabs" and consume_battle_state["selected_tab"] == 1)
    is_kit_active = (consume_battle_state["selected_tab"] == 1)
    
    if is_kit_active:
        kit_bg = (100, 150, 200)
        kit_border = (150, 150, 250) if is_kit_selected else (150, 200, 255)
    else:
        kit_bg = (60, 60, 70)
        kit_border = (100, 100, 120)
    
    pygame.draw.rect(screen, kit_bg, kit_rect)
    pygame.draw.rect(screen, kit_border, kit_rect, 4 if is_kit_selected else 2)
    
    kit_text = font_small.render("키트", True, (255, 255, 255))
    screen.blit(kit_text, kit_text.get_rect(center=kit_rect.center))
    
    # ===== 아이템 슬롯 (5개 세로) =====
    slot_start_y = tab_y + tab_height + 20
    slot_width = right_panel_width - 30
    slot_height = 70
    slot_gap = 10
    
    # 현재 탭의 아이템 목록
    if consume_battle_state["selected_tab"] == 0:
        items = [item for item in player_inventory["consumables"] if item.type == "potion"]
    else:
        items = [item for item in player_inventory["consumables"] if item.type == "repair_kit"]
    
    # 5개 슬롯 그리기 (스크롤 적용)
    for i in range(5):
        slot_y = slot_start_y + i * (slot_height + slot_gap)
        slot_x = right_panel_x + 15
        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
        
        # 실제 아이템 인덱스
        actual_index = consume_battle_state["scroll_offset"] + i
        
        # 선택 여부
        is_selected = (consume_battle_state["selected_area"] == "slots" and 
                      consume_battle_state["selected_slot"] == i)
        
        # 아이템이 있는지 확인
        if actual_index < len(items):
            item = items[actual_index]
            bg_color = (70, 80, 90)
            border_color = (150, 150, 250) if is_selected else (180, 180, 200)
            border_width = 4 if is_selected else 2
        else:
            bg_color = (40, 40, 50)
            border_color = (80, 80, 100)
            border_width = 2
        
        pygame.draw.rect(screen, bg_color, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, border_width)
        
        # 아이템 표시
        if actual_index < len(items):
            item = items[actual_index]
            
            # 아이템 이미지 (왼쪽)
            img_size = 60
            img_x = slot_x + 5
            img_y = slot_y + 5
            
            try:
                if hasattr(item, 'image_path') and item.image_path:
                    item_img = pygame.image.load(item.image_path).convert_alpha()
                    item_img = pygame.transform.scale(item_img, (img_size, img_size))
                    screen.blit(item_img, (img_x, img_y))
                else:
                    # 기본 색상 표시
                    if item.type == "potion":
                        if "small" in item.id:
                            color = (255, 182, 193)
                        elif "medium" in item.id:
                            color = (255, 105, 180)
                        else:
                            color = (220, 20, 60)
                    else:
                        if "basic" in item.id:
                            color = (135, 206, 250)
                        elif "advanced" in item.id:
                            color = (70, 130, 180)
                        else:
                            color = (25, 25, 112)
                    pygame.draw.rect(screen, color, (img_x, img_y, img_size, img_size))
            except:
                pygame.draw.rect(screen, (100, 100, 100), (img_x, img_y, img_size, img_size))
            
            # 아이템 이름 (오른쪽 위)
            name_x = img_x + img_size + 10
            name_text = font_small.render(item.name, True, (255, 255, 255))
            screen.blit(name_text, (name_x, slot_y + 10))
            
            # 효과 (오른쪽 아래)
            if item.type == "potion":
                effect_str = f"HP +{item.effect_value}"
                effect_color = (100, 255, 100)
            else:
                effect_str = f"내구도 +{item.effect_value}"
                effect_color = (100, 200, 255)
            
            effect_text = font_small.render(effect_str, True, effect_color)
            screen.blit(effect_text, (name_x, slot_y + 40))
    
    # 아이템 없을 때
    if not items:
        # 3번째 슬롯(중앙) 위치에 표시
        center_slot_y = slot_start_y + 2 * (slot_height + slot_gap) + slot_height // 2
        no_item_text = font_small.render("아이템이 없습니다", True, (150, 150, 150))
        no_item_rect = no_item_text.get_rect(center=(right_panel_x + right_panel_width // 2, center_slot_y))
        screen.blit(no_item_text, no_item_rect)
    
    # ===== 스크롤 인디케이터 (위/아래 화살표) =====
    if items and len(items) > 5:
        arrow_x = right_panel_x + right_panel_width // 2
        
        # 위쪽 화살표 (스크롤 더 있음)
        if consume_battle_state["scroll_offset"] > 0:
            arrow_up_y = slot_start_y - 15
            # 삼각형 (위쪽)
            pygame.draw.polygon(screen, (150, 150, 250), [
                (arrow_x, arrow_up_y),
                (arrow_x - 8, arrow_up_y + 10),
                (arrow_x + 8, arrow_up_y + 10)
            ])
        
        # 아래쪽 화살표 (스크롤 더 있음)
        max_visible_index = consume_battle_state["scroll_offset"] + 4
        if max_visible_index < len(items) - 1:
            arrow_down_y = slot_start_y + 5 * (slot_height + slot_gap) - 5  # 더 위로
            # 삼각형 (아래쪽)
            pygame.draw.polygon(screen, (150, 150, 250), [
                (arrow_x, arrow_down_y + 10),
                (arrow_x - 8, arrow_down_y),
                (arrow_x + 8, arrow_down_y)
            ])


def draw_weapon_selection(screen, font_main, font_small, WIDTH, HEIGHT, player_inventory):
    """무기 선택 화면"""
    
    # 중앙 패널 - 높이 증가
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
    
    # 선택된 수리 키트 정보 - 아래로 이동
    item = consume_battle_state["selected_consumable"]
    if item:
        item_info = font_small.render(f"사용: {item.name} (수리량: +{item.effect_value})", True, (100, 200, 255))
        item_info_rect = item_info.get_rect(centerx=WIDTH // 2, y=panel_y + 80)
        screen.blit(item_info, item_info_rect)
    
    # 무기 목록 (항상 6개 슬롯 표시) - 아래로 이동
    weapons = player_inventory["equipped_weapons"]
    
    slot_width = 520
    slot_height = 55
    slot_gap = 8
    start_y = panel_y + 125
    
    for i in range(6):
        slot_y = start_y + i * (slot_height + slot_gap)
        slot_x = panel_x + (panel_width - slot_width) // 2
        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
        
        is_selected = (consume_battle_state["selected_weapon_slot"] == i)
        
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
            
            # 내구도 (오른쪽 정렬, "내구도:" 제거)
            durability_str = f"{weapon.durability}/{weapon.max_durability}"
            durability_text = font_small.render(durability_str, True, (100, 200, 255))
            
            # 오른쪽 끝에서 10px 여백
            durability_x = slot_x + slot_width - durability_text.get_width() - 10
            screen.blit(durability_text, (durability_x, info_y))
        else:
            # 빈 슬롯 표시
            empty_text = font_small.render("빈 슬롯", True, (100, 100, 100))
            empty_rect = empty_text.get_rect(center=slot_rect.center)
            screen.blit(empty_text, empty_rect)


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


def handle_consume_battle_input(events, battle_player, return_to_battle_callback):
    """소모품 사용 입력 처리"""
    from scripts.inventory import player_inventory
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if consume_battle_state["mode"] == "select_item":
                # ===== 아이템 선택 모드 =====
                
                if event.key == pygame.K_w:
                    if consume_battle_state["selected_area"] == "tabs":
                        # 탭에서 위로 이동 불가
                        pass
                    else:  # slots
                        # 슬롯 영역에서 위로
                        if consume_battle_state["selected_slot"] > 0:
                            consume_battle_state["selected_slot"] -= 1
                        elif consume_battle_state["scroll_offset"] > 0:
                            # 스크롤 위로
                            consume_battle_state["scroll_offset"] -= 1
                        else:
                            # 맨 위 → 탭으로
                            consume_battle_state["selected_area"] = "tabs"
                
                elif event.key == pygame.K_s:
                    if consume_battle_state["selected_area"] == "tabs":
                        # 탭 → 슬롯으로
                        consume_battle_state["selected_area"] = "slots"
                        consume_battle_state["selected_slot"] = 0
                    else:  # slots
                        # 현재 탭의 아이템 목록
                        if consume_battle_state["selected_tab"] == 0:
                            items = [item for item in player_inventory["consumables"] if item.type == "potion"]
                        else:
                            items = [item for item in player_inventory["consumables"] if item.type == "repair_kit"]
                        
                        # 아래로 이동
                        actual_index = consume_battle_state["scroll_offset"] + consume_battle_state["selected_slot"]
                        
                        if actual_index < len(items) - 1:
                            if consume_battle_state["selected_slot"] < 4:
                                # 슬롯 내에서 아래로
                                consume_battle_state["selected_slot"] += 1
                            else:
                                # 스크롤 아래로
                                consume_battle_state["scroll_offset"] += 1
                
                elif event.key == pygame.K_a:
                    if consume_battle_state["selected_area"] == "tabs":
                        # 탭 왼쪽
                        consume_battle_state["selected_tab"] = 0
                        consume_battle_state["scroll_offset"] = 0
                
                elif event.key == pygame.K_d:
                    if consume_battle_state["selected_area"] == "tabs":
                        # 탭 오른쪽
                        consume_battle_state["selected_tab"] = 1
                        consume_battle_state["scroll_offset"] = 0
                
                elif event.key == pygame.K_RETURN:
                    if consume_battle_state["selected_area"] == "tabs":
                        # 탭 선택 → 슬롯으로 이동
                        consume_battle_state["selected_area"] = "slots"
                        consume_battle_state["selected_slot"] = 0
                    else:
                        # 아이템 사용
                        if consume_battle_state["selected_tab"] == 0:
                            items = [item for item in player_inventory["consumables"] if item.type == "potion"]
                        else:
                            items = [item for item in player_inventory["consumables"] if item.type == "repair_kit"]
                        
                        actual_index = consume_battle_state["scroll_offset"] + consume_battle_state["selected_slot"]
                        
                        if actual_index < len(items):
                            item = items[actual_index]
                            
                            if item.type == "potion":
                                # 포션 사용 - 체력 최대 체크
                                if battle_player.hp >= battle_player.max_hp:
                                    consume_battle_state["message"] = "체력이 이미 최대입니다!"
                                    consume_battle_state["message_timer"] = 0
                                else:
                                    success, message = item.use(battle_player)
                                    if success:
                                        player_inventory["consumables"].remove(item)
                                        # 스크롤 위치 조정
                                        if consume_battle_state["scroll_offset"] > 0 and actual_index >= len(items) - 1:
                                            consume_battle_state["scroll_offset"] -= 1
                                        
                                        # 전투로 복귀하면서 메시지 전달
                                        return_to_battle_callback(f"{item.name}으로 체력을 {item.effect_value} 회복했습니다.")
                            else:
                                # 수리 키트 → 무기 선택 모드로
                                consume_battle_state["mode"] = "select_weapon"
                                consume_battle_state["selected_consumable"] = item
                                consume_battle_state["selected_weapon_slot"] = 0
                
                elif event.key == pygame.K_ESCAPE:
                    # 전투로 복귀
                    return_to_battle_callback()
            
            elif consume_battle_state["mode"] == "select_weapon":
                # ===== 무기 선택 모드 =====
                if event.key == pygame.K_w:
                    consume_battle_state["selected_weapon_slot"] = max(0, consume_battle_state["selected_weapon_slot"] - 1)
                
                elif event.key == pygame.K_s:
                    max_slot = min(5, len(player_inventory["equipped_weapons"]) - 1)
                    consume_battle_state["selected_weapon_slot"] = min(max_slot, consume_battle_state["selected_weapon_slot"] + 1)
                
                elif event.key == pygame.K_RETURN:
                    # 수리 실행 - 내구도 최대 체크
                    slot_index = consume_battle_state["selected_weapon_slot"]
                    if slot_index < len(player_inventory["equipped_weapons"]):
                        weapon = player_inventory["equipped_weapons"][slot_index]
                        item = consume_battle_state["selected_consumable"]
                        
                        # 내구도가 이미 최대인지 확인
                        if weapon.durability >= weapon.max_durability:
                            consume_battle_state["message"] = "내구도가 이미 최대입니다!"
                            consume_battle_state["message_timer"] = 0
                            # 화면 유지
                        else:
                            success, message = item.use(weapon)
                            if success:
                                player_inventory["consumables"].remove(item)
                                
                                # 전투로 복귀하면서 메시지 전달
                                return_to_battle_callback(f"{item.name}(으)로 {weapon.name}의 내구도를 {item.effect_value} 회복했습니다.")
                
                elif event.key == pygame.K_ESCAPE:
                    # 아이템 선택 모드로 복귀
                    consume_battle_state["mode"] = "select_item"
                    consume_battle_state["selected_consumable"] = None

def update_consume_battle_message(dt):
    """메시지 타이머 업데이트"""
    if consume_battle_state["message"]:
        consume_battle_state["message_timer"] += dt
        if consume_battle_state["message_timer"] > 2:
            consume_battle_state["message"] = ""
            consume_battle_state["message_timer"] = 0