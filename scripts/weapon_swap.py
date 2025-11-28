import pygame

# 무기 교체 상태
swap_state = {
    "selected_index": 0,  # 오른쪽 무기 리스트에서 선택된 인덱스
    "showing_confirm": False,  # 교체 확인 다이얼로그 표시 여부
    "confirm_selected": 0,  # 0: 예, 1: 아니오
    "return_to": "town",  # 돌아갈 상태 (town 또는 battle)
}

def draw_weapon_swap(screen, font_main, font_small, WIDTH, HEIGHT, battle_player, font_path=None):
    """무기 교체 화면 그리기"""
    from scripts.inventory import player_inventory
    
    screen.fill((20, 20, 30))
    
    # 작은 폰트
    if font_path:
        font_tiny = pygame.font.Font(font_path, 20)
    else:
        font_tiny = pygame.font.Font(None, 20)
    
    # 레이아웃 설정
    margin = 30
    gap = 20
    
    # 왼쪽 영역 (현재 무기 + 선택된 무기 정보)
    left_width = 350
    left_x = margin
    
    # 오른쪽 영역 (무기 리스트)
    right_x = left_x + left_width + gap
    right_width = WIDTH - right_x - margin
    
    # 상단 영역 (현재 장착 무기)
    current_weapon_height = 280
    current_weapon_y = margin
    
    # 하단 영역 (선택된 무기 정보)
    selected_info_y = current_weapon_y + current_weapon_height + gap
    selected_info_height = HEIGHT - selected_info_y - margin
    
    # ===== 왼쪽 상단: 현재 장착 무기 =====
    current_rect = pygame.Rect(left_x, current_weapon_y, left_width, current_weapon_height)
    pygame.draw.rect(screen, (40, 50, 60), current_rect)
    pygame.draw.rect(screen, (100, 150, 100), current_rect, 4)
    
    # 타이틀
    title_text = font_small.render("현재 장착 중", True, (100, 255, 100))
    screen.blit(title_text, (current_rect.x + 20, current_rect.y + 15))
    
    if battle_player and battle_player.weapon:
        weapon = battle_player.weapon
        
        # 무기 이미지
        try:
            weapon_img_path = f"resources/png/weapon/{weapon.id}.png"
            weapon_img = pygame.image.load(weapon_img_path).convert_alpha()
            weapon_img = pygame.transform.scale(weapon_img, (100, 100))
            screen.blit(weapon_img, (current_rect.centerx - 50, current_rect.y + 60))
        except:
            pygame.draw.rect(screen, (60, 60, 80), 
                           (current_rect.centerx - 50, current_rect.y + 60, 100, 100))
        
        # 무기 정보
        y_offset = current_rect.y + 175
        
        name_text = font_small.render(weapon.name, True, (255, 255, 255))
        screen.blit(name_text, (current_rect.x + 20, y_offset))
        y_offset += 30
        
        grade_text = font_small.render(f"등급: {weapon.grade}", True, (200, 200, 100))
        screen.blit(grade_text, (current_rect.x + 20, y_offset))
        y_offset += 30
        
        durability_text = font_small.render(
            f"내구도: {weapon.durability}/{weapon.max_durability}",
            True, (100, 200, 255)
        )
        screen.blit(durability_text, (current_rect.x + 20, y_offset))
    else:
        # 맨손
        no_weapon_text = font_main.render("맨손", True, (150, 150, 150))
        screen.blit(no_weapon_text, (current_rect.centerx - no_weapon_text.get_width() // 2,
                                     current_rect.centery - no_weapon_text.get_height() // 2))
    
    # ===== 왼쪽 하단: 선택된 무기 정보 =====
    selected_info_rect = pygame.Rect(left_x, selected_info_y, left_width, selected_info_height)
    pygame.draw.rect(screen, (40, 40, 50), selected_info_rect)
    pygame.draw.rect(screen, (100, 100, 120), selected_info_rect, 3)
    
    # 선택된 무기 정보 표시
    if swap_state["selected_index"] < len(player_inventory["equipped_weapons"]):
        selected_weapon = player_inventory["equipped_weapons"][swap_state["selected_index"]]
        
        y_offset = selected_info_rect.y + 20
        
        # 제목
        info_title = font_small.render("선택한 무기", True, (200, 200, 200))
        screen.blit(info_title, (selected_info_rect.x + 20, y_offset))
        y_offset += 40
        
        # 무기 이름
        name_text = font_small.render(selected_weapon.name, True, (255, 255, 255))
        screen.blit(name_text, (selected_info_rect.x + 20, y_offset))
        y_offset += 35
        
        # 등급
        grade_text = font_small.render(f"등급: {selected_weapon.grade}", True, (200, 200, 100))
        screen.blit(grade_text, (selected_info_rect.x + 20, y_offset))
        y_offset += 30
        
        # 내구도
        durability_text = font_small.render(
            f"내구도: {selected_weapon.durability}/{selected_weapon.max_durability}",
            True, (100, 200, 255)
        )
        screen.blit(durability_text, (selected_info_rect.x + 20, y_offset))
        y_offset += 40
        
        # 설명
        if hasattr(selected_weapon, 'description'):
            desc_lines = wrap_text(selected_weapon.description, font_tiny, left_width - 40)
            for line in desc_lines:
                desc_text = font_tiny.render(line, True, (180, 180, 180))
                screen.blit(desc_text, (selected_info_rect.x + 20, y_offset))
                y_offset += 22
    
    # ===== 오른쪽: 무기 리스트 =====
    # 6개 슬롯을 균등하게 배치
    total_height = HEIGHT - 2 * margin
    weapon_slot_height = 85
    total_slots_height = weapon_slot_height * 6
    weapon_slot_gap = (total_height - total_slots_height) / 7  # 위아래 + 슬롯 사이 간격
    
    for i in range(6):  # 항상 6칸 표시
        slot_y = margin + weapon_slot_gap + i * (weapon_slot_height + weapon_slot_gap)
        slot_rect = pygame.Rect(right_x, slot_y, right_width, weapon_slot_height)
        
        is_selected = (swap_state["selected_index"] == i)
        
        # 무기가 있는지 확인
        has_weapon = i < len(player_inventory["equipped_weapons"])
        
        if has_weapon:
            weapon = player_inventory["equipped_weapons"][i]
            is_current = (battle_player and battle_player.weapon == weapon)
            
            # 배경색
            if is_current:
                base_color = (50, 80, 50)
            else:
                base_color = (50, 50, 70)
        else:
            # 빈 슬롯
            base_color = (30, 30, 40)
            is_current = False
        
        if is_selected and has_weapon:
            color = tuple(min(255, c + 30) for c in base_color)
        else:
            color = base_color
        
        pygame.draw.rect(screen, color, slot_rect)
        
        # 테두리
        if is_selected and has_weapon:
            pygame.draw.rect(screen, (100, 150, 255), slot_rect, 4)
        else:
            pygame.draw.rect(screen, (100, 100, 120), slot_rect, 2)
        
        if has_weapon:
            # 무기 이미지
            try:
                weapon_img_path = f"resources/png/weapon/{weapon.id}.png"
                weapon_img = pygame.image.load(weapon_img_path).convert_alpha()
                weapon_img = pygame.transform.scale(weapon_img, (70, 70))
                screen.blit(weapon_img, (slot_rect.x + 10, slot_rect.y + 10))
            except:
                pygame.draw.rect(screen, (60, 60, 80), 
                               (slot_rect.x + 10, slot_rect.y + 10, 70, 70))
            
            # 무기 정보
            weapon_name = font_small.render(weapon.name, True, (255, 255, 255))
            screen.blit(weapon_name, (slot_rect.x + 90, slot_rect.y + 15))
            
            durability_text = font_small.render(
                f"{weapon.durability}/{weapon.max_durability}",
                True, (200, 200, 200)
            )
            screen.blit(durability_text, (slot_rect.x + 90, slot_rect.y + 50))
            
            # 현재 장착 표시
            if is_current:
                current_badge = font_small.render("장착중", True, (100, 255, 100))
                screen.blit(current_badge, (slot_rect.x + slot_rect.width - 100, slot_rect.y + 30))
        else:
            # 빈 슬롯 표시
            empty_text = font_small.render("빈 슬롯", True, (100, 100, 120))
            screen.blit(empty_text, (slot_rect.centerx - empty_text.get_width() // 2,
                                    slot_rect.centery - empty_text.get_height() // 2))
    
    # ===== 확인 다이얼로그 =====
    if swap_state["showing_confirm"]:
        # 반투명 오버레이
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 다이얼로그 박스
        dialog_width = 500
        dialog_height = 200
        dialog_x = (WIDTH - dialog_width) // 2
        dialog_y = (HEIGHT - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, (40, 40, 50), dialog_rect)
        pygame.draw.rect(screen, (150, 150, 200), dialog_rect, 4)
        
        # 메시지
        if swap_state["selected_index"] < len(player_inventory["equipped_weapons"]):
            selected_weapon = player_inventory["equipped_weapons"][swap_state["selected_index"]]
            message = f"{selected_weapon.name}(으)로 교체하시겠습니까?"
            message_text = font_small.render(message, True, (255, 255, 255))
            screen.blit(message_text, (dialog_x + (dialog_width - message_text.get_width()) // 2,
                                       dialog_y + 50))
        
        # 버튼
        button_width = 150
        button_height = 50
        button_gap = 30
        
        yes_x = dialog_x + (dialog_width - button_width * 2 - button_gap) // 2
        no_x = yes_x + button_width + button_gap
        button_y = dialog_y + dialog_height - 80
        
        yes_rect = pygame.Rect(yes_x, button_y, button_width, button_height)
        no_rect = pygame.Rect(no_x, button_y, button_width, button_height)
        
        # 예 버튼
        yes_color = (100, 200, 100) if swap_state["confirm_selected"] == 0 else (60, 120, 60)
        pygame.draw.rect(screen, yes_color, yes_rect)
        if swap_state["confirm_selected"] == 0:
            pygame.draw.rect(screen, (100, 150, 255), yes_rect, 4)
        
        yes_text = font_small.render("예", True, (255, 255, 255))
        screen.blit(yes_text, (yes_rect.centerx - yes_text.get_width() // 2,
                               yes_rect.centery - yes_text.get_height() // 2))
        
        # 아니오 버튼
        no_color = (200, 100, 100) if swap_state["confirm_selected"] == 1 else (120, 60, 60)
        pygame.draw.rect(screen, no_color, no_rect)
        if swap_state["confirm_selected"] == 1:
            pygame.draw.rect(screen, (100, 150, 255), no_rect, 4)
        
        no_text = font_small.render("아니오", True, (255, 255, 255))
        screen.blit(no_text, (no_rect.centerx - no_text.get_width() // 2,
                              no_rect.centery - no_text.get_height() // 2))


def handle_weapon_swap_input(events, battle_player, game_state):
    """무기 교체 입력 처리"""
    from scripts.inventory import player_inventory
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            # 확인 다이얼로그가 표시 중일 때
            if swap_state["showing_confirm"]:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    # 예/아니오 토글
                    swap_state["confirm_selected"] = 1 - swap_state["confirm_selected"]
                
                elif event.key == pygame.K_RETURN:
                    if swap_state["confirm_selected"] == 0:  # 예
                        # 무기 교체 실행
                        if swap_state["selected_index"] < len(player_inventory["equipped_weapons"]):
                            selected_weapon = player_inventory["equipped_weapons"][swap_state["selected_index"]]
                            battle_player.equip_weapon(selected_weapon)
                            # 전투 화면으로 돌아가므로 마을 메시지 설정 안 함
                        
                        # 다이얼로그 닫기
                        swap_state["showing_confirm"] = False
                        swap_state["confirm_selected"] = 0
                        
                        # 전투로 돌아가기
                        from scripts import battle_system
                        battle_system.battle_state["returning_from_swap"] = True
                        game_state["state"] = "battle"
                    else:  # 아니오
                        # 다이얼로그만 닫기 (교체 화면에 머물기)
                        swap_state["showing_confirm"] = False
                        swap_state["confirm_selected"] = 0
                
                elif event.key == pygame.K_ESCAPE:
                    # 취소
                    swap_state["showing_confirm"] = False
                    swap_state["confirm_selected"] = 0
            
            # 무기 리스트 탐색
            else:
                if event.key == pygame.K_w:
                    # 위로 이동 (무기가 있는 칸으로만)
                    new_index = swap_state["selected_index"] - 1
                    while new_index >= 0:
                        if new_index < len(player_inventory["equipped_weapons"]):
                            swap_state["selected_index"] = new_index
                            break
                        new_index -= 1
                
                elif event.key == pygame.K_s:
                    # 아래로 이동 (무기가 있는 칸으로만)
                    new_index = swap_state["selected_index"] + 1
                    while new_index < 6:
                        if new_index < len(player_inventory["equipped_weapons"]):
                            swap_state["selected_index"] = new_index
                            break
                        new_index += 1
                
                elif event.key == pygame.K_RETURN:
                    # 현재 장착 중인 무기가 아닌 경우에만 교체 확인
                    if swap_state["selected_index"] < len(player_inventory["equipped_weapons"]):
                        selected_weapon = player_inventory["equipped_weapons"][swap_state["selected_index"]]
                        if battle_player.weapon != selected_weapon:
                            swap_state["showing_confirm"] = True
                            swap_state["confirm_selected"] = 0
                        # 이미 장착 중이면 아무 동작도 하지 않음
                
                elif event.key == pygame.K_ESCAPE:
                    # 전투로 돌아가기
                    from scripts import battle_system
                    battle_system.battle_state["returning_from_swap"] = True
                    game_state["state"] = "battle"
                    swap_state["selected_index"] = 0


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