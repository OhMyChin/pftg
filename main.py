import pygame

pygame.init()

import os
import sys
from scripts import interactions, battle_system, inventory
from scripts.weapons import create_weapon
from scripts import weapon_swap, consume_battle

# --- 기본 설정 ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
pftg_icon = pygame.image.load("resources\\png\\pftg_icon.png")
game_state = {
    "state": "start",  # start, town, battle등등
    "player_name": "Hero",
    "gold": 20000,  # 초기 골드 추가
    "message": "",
    "message_timer": 0
}
blink_timer = 0

# --- 폰트 경로 설정 ---
FONT_PATH = os.path.join("resources", "font", "DOSGothic.ttf")
FONT_MAIN = pygame.font.Font(FONT_PATH, 60)
FONT_SMALL = pygame.font.Font(FONT_PATH, 28)

# --- 전투 시스템 폰트 공유 설정 ---
battle_system.FONT_PATH = FONT_PATH
battle_system.FONT_MAIN = pygame.font.Font(FONT_PATH, 32)
battle_system.FONT_SMALL = pygame.font.Font(FONT_PATH, 24)

# --- 초기화 ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PFTG")
pygame.display.set_icon(pftg_icon)
clock = pygame.time.Clock()

# --- 색상 정의 ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# --- 플레이어 클래스 ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # 히트박스는 40x10
        self.hitbox = pygame.Rect(0, 0, 40, 10)
        self.hitbox.center = (x, y)
        self.rect = self.hitbox.copy()  # 충돌 판정용
        self.pos = pygame.Vector2(x, y)

        # 스프라이트 이미지 로드 (3프레임)
        try:
            sprite_sheet = pygame.image.load("resources/png/hero_moving.png").convert_alpha()
            frame_width = sprite_sheet.get_width() // 3
            frame_height = sprite_sheet.get_height()
            
            # 가로를 40으로 고정, 세로는 원본 비율 유지
            target_width = 40
            aspect_ratio = frame_height / frame_width
            target_height = int(target_width * aspect_ratio)
            
            self.frames = []
            for i in range(3):
                frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                scaled_frame = pygame.transform.scale(frame, (target_width, target_height))
                self.frames.append(scaled_frame)
            
            self.display_image = self.frames[0]
            self.image_height = target_height
        except:
            # 이미지 로드 실패 시 기본 초록 박스
            default_surface = pygame.Surface((40, 40))
            default_surface.fill(GREEN)
            self.frames = [default_surface, default_surface, default_surface]
            self.display_image = self.frames[0]
            self.image_height = 40
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # 프레임 전환 속도 (초)
        
        self.facing_right = True  # 오른쪽을 보고 있는지
        self.is_moving = False

    def handle_input(self, buildings_group, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)

        # 방향 벡터 계산
        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
            self.facing_right = False  # 왼쪽으로 이동 시 방향 전환
        if keys[pygame.K_d]:
            direction.x += 1
            self.facing_right = True  # 오른쪽으로 이동 시 방향 전환

        if direction.length_squared() > 0:
            direction = direction.normalize()
            new_pos = self.pos + direction * PLAYER_SPEED
            new_rect = self.rect.copy()
            new_rect.center = new_pos

            # 충돌 검사: 건물과 겹치지 않을 경우만 이동
            collision = False
            for building in buildings_group:
                if new_rect.colliderect(building.rect):
                    collision = True
                    break

            if not collision:
                self.pos = new_pos
                self.rect.center = self.pos
                self.hitbox.center = self.pos
                self.is_moving = True
                
                # 애니메이션 업데이트
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    # 2, 3번 프레임만 번갈아가며 표시
                    if self.current_frame == 1:
                        self.current_frame = 2
                    else:
                        self.current_frame = 1
            else:
                self.is_moving = False
        else:
            self.is_moving = False
            self.current_frame = 0  # 정지 시 첫 번째 프레임
        
        # 이미지 업데이트
        self.update_image()
    
    def update_image(self):
        """현재 프레임과 방향에 따라 이미지 업데이트"""
        self.display_image = self.frames[self.current_frame]
        
        # 왼쪽을 보고 있으면 이미지 반전
        if not self.facing_right:
            self.display_image = pygame.transform.flip(self.display_image, True, False)

# --- 건물 클래스 ---
class Building(pygame.sprite.Sprite):
    def __init__(self, name, x, y, width, height, image=None, on_interact=None):
        super().__init__()
        self.name = name
        self.on_interact = on_interact

        # 이미지 설정 (없으면 회색 박스)
        if image:
            self.image = pygame.transform.scale(pygame.image.load(image), (width, height))
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((150, 150, 150))

        self.rect = self.image.get_rect(topleft=(x, y))

        # 상호작용 영역 생성 (건물 아래 중앙)
        interact_width = 60
        interact_height = 30
        interact_x = x + (width - interact_width) // 2
        interact_y = y + height - interact_height // 2
        self.interact_rect = pygame.Rect(interact_x, interact_y, interact_width, interact_height)

    def interact(self):
        if self.on_interact:
            self.on_interact()
        else:
            print(f"{self.name}과 상호작용 중...")

# --- 그룹 생성 ---
all_sprites = pygame.sprite.Group()
buildings = pygame.sprite.Group()

# --- 플레이어 생성 ---
player = Player(400, 300)
all_sprites.add(player)

# 전투 시스템 플레이어 초기화
if battle_system.battle_player is None:
    battle_system.battle_player = battle_system.Player(
        game_state["player_name"], 
        hp=50, 
        speed=10
    )
    battle_system.battle_player.max_hp = 50
    battle_system.battle_player.image = pygame.transform.scale(
        pygame.image.load("resources/png/hero.png").convert_alpha(), 
        (160, 160)
    )
    # 기본 무기 장착
    battle_system.battle_player.equip_weapon(create_weapon("wooden_stick"))

# 인벤토리 초기화
inventory.init_inventory(battle_system.battle_player)

# --- 예시 건물 생성 ---
house = Building("집", 100, -100, 125, 125, "resources\\png\\building\\pretty_house.png",
    on_interact=lambda: interactions.home_interact(game_state)
)
buildings.add(house)
all_sprites.add(house)

shop = Building(
    "상점", 300, -100, 125, 125, "resources\\png\\building\\shop.png",
    on_interact=lambda: interactions.enter_shop(game_state)
)
buildings.add(shop)
all_sprites.add(shop)

forge = Building("대장간", 500, -150, 175, 175, "resources\\png\\building\\blacksmith.png")
buildings.add(forge)
all_sprites.add(forge)

dungeon = Building(
    "던전", 600, 150, 120, 200, "resources\\png\\building\\dungeon.png",
    on_interact=lambda: interactions.enter_dungeon(
        battle_system.start_battle, game_state, game_state["player_name"]
    )
)
buildings.add(dungeon)
all_sprites.add(dungeon)

# --- 카메라 오프셋 ---
camera_offset = pygame.Vector2(0, 0)

# --- E 키 상호작용 상태 변수 ---
e_key_pressed = False

# --- 이름 입력 변수 초기화 ---
player_name_input = ""

# --- 메인 게임 루프 ---
while True:
    dt = clock.tick(FPS) / 1000
    events = pygame.event.get()

    # --- 이벤트 처리 ---
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # 이름 입력 상태일 때만 글자 입력 받기
            if game_state["state"] == "name_input":
                if event.key == pygame.K_RETURN:
                    game_state["player_name"] = player_name_input if player_name_input else "Hero"
                    # 플레이어 이름 업데이트
                    if battle_system.battle_player:
                        battle_system.battle_player.name = game_state["player_name"]
                    game_state["state"] = "town"
                elif event.key == pygame.K_BACKSPACE:
                    player_name_input = player_name_input[:-1]
                else:
                    if len(player_name_input) < 10 and event.unicode.isprintable():
                        player_name_input += event.unicode

    match game_state["state"]:
        # 시작 화면
        case "start":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                game_state["state"] = "name_input"
                player_name_input = ""

            # 배경 이미지 표시
            try:
                start_bg = pygame.image.load("resources/png/start_screen.png")
                start_bg = pygame.transform.scale(start_bg, (WIDTH, HEIGHT))
                screen.blit(start_bg, (0, 0))
            except:
                screen.fill((0, 0, 0))
    
            blink_timer += dt
            if int(blink_timer * 2) % 2 == 0:
                text = FONT_MAIN.render("Press Enter to Start", True, (255, 255, 255))
                rect = text.get_rect(center=(WIDTH // 2, HEIGHT * 0.9))
                screen.blit(text, rect)

        case "name_input":
            screen.fill((0, 0, 0))
            title = FONT_MAIN.render("플레이어 이름을 입력하세요", True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
            
            input_surface = FONT_MAIN.render(player_name_input + "|", True, (255, 255, 0))
            screen.blit(input_surface, (WIDTH // 2 - input_surface.get_width() // 2, HEIGHT // 2))

            notice_text = FONT_SMALL.render("* 영어만 입력 가능 / 최대 10글자", True, (180, 180, 180))
            screen.blit(notice_text, (WIDTH // 2 - notice_text.get_width() // 2, HEIGHT // 2 + 100))

        # 마을 화면
        case "town":
            # --- 입력 처리 및 이동 ---
            player.handle_input(buildings, dt)

            # --- 카메라: 플레이어를 화면 중앙에 유지 ---
            camera_offset.x = player.rect.centerx - WIDTH // 2
            camera_offset.y = player.rect.centery - HEIGHT // 2

            # --- E 키 상호작용 처리 (한 번만 실행되도록) ---
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                if not e_key_pressed:
                    for building in buildings:
                        if player.rect.colliderect(building.interact_rect):
                            building.interact()
                    e_key_pressed = True
            else:
                e_key_pressed = False

            # --- I 키 인벤토리 열기 ---
            if keys[pygame.K_i]:
                if not i_key_pressed:
                    game_state["state"] = "inventory"
                    i_key_pressed = True
            else:
                i_key_pressed = False

            # --- 화면 그리기 ---
            screen.fill(WHITE)

            # --- 건물 그리기 (카메라 오프셋 적용) ---
            for building in buildings:
                screen.blit(building.image, building.rect.topleft - camera_offset)

                # 디버깅용: 상호작용 영역 시각화 (빨간색 테두리)
                debug_rect = building.interact_rect.move(-camera_offset)
                pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

            # --- 플레이어 그리기 (항상 화면 중앙에 위치) ---
            image_bottom_y = HEIGHT // 2 + player.hitbox.height // 2
            image_top_y = image_bottom_y - player.image_height
            image_rect = player.display_image.get_rect(centerx=WIDTH // 2, top=image_top_y)
            screen.blit(player.display_image, image_rect)

            # 히트박스 시각화 (초록색 테두리)
            hitbox_screen = pygame.Rect(
                WIDTH // 2 - player.hitbox.width // 2,
                HEIGHT // 2 - player.hitbox.height // 2,
                player.hitbox.width,
                player.hitbox.height
            )
            pygame.draw.rect(screen, (0, 255, 0), hitbox_screen, 2)

            # --- 마을 체력 표시 (텍스트 + 체력바) ---
            if battle_system.battle_player:
                bp = battle_system.battle_player
                # 이름만 표시 (HP는 체력바에 표시)
                name_text = FONT_SMALL.render(f"{bp.name}", True, BLACK)
                screen.blit(name_text, (20, 20))

                # 체력바 배경
                bar_x, bar_y, bar_width, bar_height = 20, 50, 200, 20
                pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))

                # 체력바 채우기
                if bp.max_hp > 0:
                    hp_ratio = max(0, bp.hp) / bp.max_hp
                else:
                    hp_ratio = 0
                pygame.draw.rect(
                    screen,
                    (200, 50, 50),
                    (bar_x, bar_y, int(bar_width * hp_ratio), bar_height)
                )
                
                # 체력바 테두리
                pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
                
                # 체력바 안에 HP 수치 표시
                hp_number_text = FONT_SMALL.render(f"{bp.hp}/{bp.max_hp}", True, (255, 255, 255))
                hp_number_rect = hp_number_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
                screen.blit(hp_number_text, hp_number_rect)

                # 무기 아이콘 표시 (6개)
                from scripts.inventory import player_inventory
                icon_size = 50
                icon_gap = 10
                start_x = 20
                start_y = 80
                
                for i in range(6):
                    icon_x = start_x + i * (icon_size + icon_gap)
                    icon_rect = pygame.Rect(icon_x, start_y, icon_size, icon_size)
                    
                    # 무기가 있는지 확인
                    if i < len(player_inventory["equipped_weapons"]):
                        weapon = player_inventory["equipped_weapons"][i]
                        is_current = (i == 0)  # 첫 번째 슬롯만 초록색
                        
                        # 배경 및 테두리 (현재 장착 무기는 녹색 테두리)
                        bg_color = (150, 150, 150)  # 배경색은 항상 동일
                        border_color = (100, 255, 100) if is_current else (100, 100, 100)
                        border_width = 3 if is_current else 2
                        
                        pygame.draw.rect(screen, bg_color, icon_rect)
                        pygame.draw.rect(screen, border_color, icon_rect, border_width)
                        
                        # 무기 아이콘 (weapon.image_path 사용)
                        try:
                            if hasattr(weapon, 'image_path') and weapon.image_path:
                                weapon_img = pygame.image.load(weapon.image_path).convert_alpha()
                                weapon_img = pygame.transform.scale(weapon_img, (icon_size - 10, icon_size - 10))
                                screen.blit(weapon_img, (icon_x + 5, start_y + 5))
                            else:
                                # 이미지 경로가 없으면 기본 표시
                                pygame.draw.rect(screen, (100, 100, 120), (icon_x + 5, start_y + 5, icon_size - 10, icon_size - 10))
                        except:
                            # 이미지 로드 실패 시 기본 사각형
                            pygame.draw.rect(screen, (100, 100, 120), (icon_x + 5, start_y + 5, icon_size - 10, icon_size - 10))
                    else:
                        # 빈 슬롯
                        pygame.draw.rect(screen, (100, 100, 100), icon_rect)
                        pygame.draw.rect(screen, (80, 80, 80), icon_rect, 1)

            # 메시지가 있으면 하단에 출력
            if game_state.get("message"):
                msg_text = FONT_SMALL.render(game_state["message"], True, (100, 0, 0))
                msg_rect = msg_text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
                screen.blit(msg_text, msg_rect)

                game_state["message_timer"] += dt
                if game_state["message_timer"] > 3:
                    game_state["message"] = ""
                    game_state["message_timer"] = 0

        case "inventory":
            inventory.draw_inventory(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT, 
                                    battle_system.battle_player, dt, FONT_PATH, game_state)
            inventory.handle_inventory_input(events, battle_system.battle_player)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                game_state["state"] = "town"
            elif keys[pygame.K_i]:
                if not i_key_pressed:
                    game_state["state"] = "town"
                    i_key_pressed = True
            else:
                i_key_pressed = False

        case "shop":
            from scripts import shop
            shop.draw_shop(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT, game_state, dt)
            shop.handle_shop_input(events, game_state)
                    
        case "battle":
            battle_system.update_battle(screen, FONT_SMALL, WIDTH, HEIGHT, game_state, events)

        case "weapon_swap":
            weapon_swap.draw_weapon_swap(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT,
                                        battle_system.battle_player, FONT_PATH)
            weapon_swap.handle_weapon_swap_input(events, battle_system.battle_player, game_state)
        
        case "consume_battle":
            consume_battle.draw_consume_battle(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT,
                                              battle_system.battle_player)
            
            # 전투로 복귀하는 함수
            def return_to_battle():
                game_state["state"] = "battle"
                consume_battle.reset_consume_battle_state()
            
            consume_battle.handle_consume_battle_input(events, battle_system.battle_player, return_to_battle)

    # --- 화면 업데이트 ---
    pygame.display.flip()