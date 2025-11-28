import pygame

# 소모품 선택 상태
consume_battle_state = {
    "selected_tab": 0,  # 0: 포션, 1: 수리 키트
    "selected_slot": 0,
    "mode": "select_item",  # "select_item" 또는 "select_weapon" (수리 키트용)
    "selected_consumable": None,
    "selected_weapon_slot": 0,
}

def draw_consume_battle(screen, font_main, font_small, WIDTH, HEIGHT, battle_player):
    """전투 중 소모품 사용 화면"""
    from scripts.inventory import player_inventory
    
    # 배경 (반투명)
    screen.fill((20, 20, 30))
    
    # 제목
    title_text = font_main.render("소모품 사용", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 30))
    
    if consume_battle_state["mode"] == "select_item":
        # ===== 아이템 선택 모드 =====
        draw_item_selection(screen, font_small, WIDTH, HEIGHT, player_inventory)
    else:
        # ===== 무기 선택 모드 (수리 키트 사용) =====
        draw_weapon_selection(screen, font_small, WIDTH, HEIGHT, player_inventory)
    
    # 조작 안내
    controls_y = HEIGHT - 80
    if consume_battle_state["mode"] == "select_item":
        controls = [
            "W/S: 탭 선택",
            "A/D: 아이템 선택",
            "Enter: 사용",
            "ESC: 취소"
        ]
    else:
        controls = [
            "W/S: 무기 선택",
            "Enter: 수리",
            "ESC: 취소"
        ]
    
    for i, control in enumerate(controls):
        text = font_small.render(control, True, (200, 200, 200))
        screen.blit(text, (30 + i * 150, controls_y))


def draw_item_selection(screen, font_small, WIDTH, HEIGHT, player_inventory):
    """아이템 선택 화면"""
    # 탭 버튼 (포션 / 수리 키트)
    tab_width = 200
    tab_height = 50
    tab_y = 100
    tab_gap = 20
    
    potion_tab_x = WIDTH // 2 - tab_width - tab_gap // 2
    repair_tab_x = WIDTH // 2 + tab_gap // 2
    
    # 포션 탭
    potion_rect = pygame.Rect(potion_tab_x, tab_y, tab_width, tab_height)
    potion_color = (100, 150, 255) if consume_battle_state["selected_tab"] == 0 else (60, 60, 80)
    pygame.draw.rect(screen, potion_color, potion_rect)
    pygame.draw.rect(screen, (150, 150, 150), potion_rect, 3)
    potion_text = font_small.render("포션", True, (255, 255, 255))
    screen.blit(potion_text, potion_text.get_rect(center=potion_rect.center))
    
    # 수리 키트 탭
    repair_rect = pygame.Rect(repair_tab_x, tab_y, tab_width, tab_height)
    repair_color = (100, 150, 255) if consume_battle_state["selected_tab"] == 1 else (60, 60, 80)
    pygame.draw.rect(screen, repair_color, repair_rect)
    pygame.draw.rect(screen, (150, 150, 150), repair_rect, 3)
    repair_text = font_small.render("수리 키트", True, (255, 255, 255))
    screen.blit(repair_text, repair_text.get_rect(center=repair_rect.center))
    
    # 아이템 목록 필터링
    if consume_battle_state["selected_tab"] == 0:
        # 포션만 표시
        items = [item for item in player_inventory["consumables"] if item.type == "potion"]
    else:
        # 수리 키트만 표시
        items = [item for item in player_inventory["consumables"] if item.type == "repair_kit"]
    
    # 아이템 슬롯 그리기 (가로 3개)
    slot_size = 120
    slot_gap = 20
    start_y = 200
    
    for i in range(min(3, len(items))):
        item = items[i] if i < len(items) else None
        slot_x = WIDTH // 2 - (slot_size * 3 + slot_gap * 2) // 2 + i * (slot_size + slot_gap)
        slot_rect = pygame.Rect(slot_x, start_y, slot_size, slot_size)
        
        # 선택된 슬롯 강조
        is_selected = (consume_battle_state["selected_slot"] == i)
        bg_color = (80, 80, 100) if item else (40, 40, 50)
        border_color = (255, 215, 0) if is_selected else (100, 100, 120)
        border_width = 4 if is_selected else 2
        
        pygame.draw.rect(screen, bg_color, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, border_width)
        
        if item:
            # 아이템 이미지
            try:
                if hasattr(item, 'image_path') and item.image_path:
                    item_img = pygame.image.load(item.image_path).convert_alpha()
                    item_img = pygame.transform.scale(item_img, (80, 80))
                    screen.blit(item_img, (slot_x + 20, start_y + 10))
                else:
                    # 기본 표시
                    pygame.draw.rect(screen, (150, 150, 200), (slot_x + 20, start_y + 10, 80, 80))
            except:
                pygame.draw.rect(screen, (150, 150, 200), (slot_x + 20, start_y + 10, 80, 80))
            
            # 아이템 이름
            name_text = font_small.render(item.name, True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(slot_x + slot_size // 2, start_y + slot_size + 20))
            screen.blit(name_text, name_rect)
            
            # 효과 설명
            effect_text = font_small.render(item.description, True, (200, 200, 200))
            effect_rect = effect_text.get_rect(center=(slot_x + slot_size // 2, start_y + slot_size + 50))
            screen.blit(effect_text, effect_rect)
    
    # 아이템이 없을 때
    if not items:
        no_item_text = font_small.render("사용 가능한 아이템이 없습니다", True, (150, 150, 150))
        screen.blit(no_item_text, (WIDTH // 2 - no_item_text.get_width() // 2, start_y + 50))


def draw_weapon_selection(screen, font_small, WIDTH, HEIGHT, player_inventory):
    """무기 선택 화면 (수리 키트 사용)"""
    # 안내 메시지
    guide_text = font_small.render("수리할 무기를 선택하세요", True, (255, 255, 255))
    screen.blit(guide_text, (WIDTH // 2 - guide_text.get_width() // 2, 100))
    
    # 장착된 무기 목록
    weapons = player_inventory["equipped_weapons"]
    
    slot_size = 100
    slot_gap = 20
    start_y = 200
    
    for i in range(min(6, len(weapons))):
        weapon = weapons[i] if i < len(weapons) else None
        slot_x = 100
        slot_y = start_y + i * (slot_size + slot_gap)
        slot_rect = pygame.Rect(slot_x, slot_y, WIDTH - 200, slot_size)
        
        # 선택된 슬롯 강조
        is_selected = (consume_battle_state["selected_weapon_slot"] == i)
        bg_color = (80, 80, 100) if weapon else (40, 40, 50)
        border_color = (255, 215, 0) if is_selected else (100, 100, 120)
        border_width = 4 if is_selected else 2
        
        pygame.draw.rect(screen, bg_color, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, border_width)
        
        if weapon:
            # 무기 이미지
            try:
                if hasattr(weapon, 'image_path') and weapon.image_path:
                    weapon_img = pygame.image.load(weapon.image_path).convert_alpha()
                    weapon_img = pygame.transform.scale(weapon_img, (80, 80))
                    screen.blit(weapon_img, (slot_x + 10, slot_y + 10))
            except:
                pygame.draw.rect(screen, (150, 150, 200), (slot_x + 10, slot_y + 10, 80, 80))
            
            # 무기 정보
            info_x = slot_x + 100
            name_text = font_small.render(weapon.name, True, (255, 255, 255))
            screen.blit(name_text, (info_x, slot_y + 20))
            
            durability_text = font_small.render(
                f"내구도: {weapon.durability}/{weapon.max_durability}",
                True, (200, 200, 100)
            )
            screen.blit(durability_text, (info_x, slot_y + 50))


def handle_consume_battle_input(events, battle_player, return_to_battle_func):
    """소모품 선택 화면 입력 처리"""
    from scripts.inventory import player_inventory
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if consume_battle_state["mode"] == "select_item":
                # ===== 아이템 선택 모드 =====
                if event.key == pygame.K_w:
                    # 탭 위로
                    consume_battle_state["selected_tab"] = 0
                    consume_battle_state["selected_slot"] = 0
                elif event.key == pygame.K_s:
                    # 탭 아래로
                    consume_battle_state["selected_tab"] = 1
                    consume_battle_state["selected_slot"] = 0
                
                elif event.key == pygame.K_a:
                    # 슬롯 왼쪽
                    consume_battle_state["selected_slot"] = max(0, consume_battle_state["selected_slot"] - 1)
                elif event.key == pygame.K_d:
                    # 슬롯 오른쪽
                    consume_battle_state["selected_slot"] = min(2, consume_battle_state["selected_slot"] + 1)
                
                elif event.key == pygame.K_RETURN:
                    # 아이템 사용
                    if consume_battle_state["selected_tab"] == 0:
                        items = [item for item in player_inventory["consumables"] if item.type == "potion"]
                    else:
                        items = [item for item in player_inventory["consumables"] if item.type == "repair_kit"]
                    
                    selected_slot = consume_battle_state["selected_slot"]
                    if selected_slot < len(items):
                        consumable = items[selected_slot]
                        
                        if consumable.type == "potion":
                            # 포션: 즉시 사용
                            success, message = consumable.use(battle_player)
                            if success:
                                # 인벤토리에서 제거
                                player_inventory["consumables"].remove(consumable)
                                print(message)
                                # 전투로 복귀
                                return_to_battle_func()
                        
                        elif consumable.type == "repair_kit":
                            # 수리 키트: 무기 선택 모드로 전환
                            if player_inventory["equipped_weapons"]:
                                consume_battle_state["selected_consumable"] = consumable
                                consume_battle_state["mode"] = "select_weapon"
                                consume_battle_state["selected_weapon_slot"] = 0
                
                elif event.key == pygame.K_ESCAPE:
                    # 전투로 복귀
                    return_to_battle_func()
            
            else:
                # ===== 무기 선택 모드 =====
                if event.key == pygame.K_w:
                    consume_battle_state["selected_weapon_slot"] = max(0, consume_battle_state["selected_weapon_slot"] - 1)
                elif event.key == pygame.K_s:
                    max_slot = min(5, len(player_inventory["equipped_weapons"]) - 1)
                    consume_battle_state["selected_weapon_slot"] = min(max_slot, consume_battle_state["selected_weapon_slot"] + 1)
                
                elif event.key == pygame.K_RETURN:
                    # 수리 실행
                    weapon_slot = consume_battle_state["selected_weapon_slot"]
                    if weapon_slot < len(player_inventory["equipped_weapons"]):
                        weapon = player_inventory["equipped_weapons"][weapon_slot]
                        consumable = consume_battle_state["selected_consumable"]
                        
                        success, message = consumable.use(weapon)
                        if success:
                            # 인벤토리에서 제거
                            player_inventory["consumables"].remove(consumable)
                            print(message)
                        
                        # 전투로 복귀
                        consume_battle_state["mode"] = "select_item"
                        consume_battle_state["selected_consumable"] = None
                        return_to_battle_func()
                
                elif event.key == pygame.K_ESCAPE:
                    # 아이템 선택으로 돌아가기
                    consume_battle_state["mode"] = "select_item"
                    consume_battle_state["selected_consumable"] = None


def reset_consume_battle_state():
    """소모품 선택 상태 초기화"""
    consume_battle_state["selected_tab"] = 0
    consume_battle_state["selected_slot"] = 0
    consume_battle_state["mode"] = "select_item"
    consume_battle_state["selected_consumable"] = None
    consume_battle_state["selected_weapon_slot"] = 0