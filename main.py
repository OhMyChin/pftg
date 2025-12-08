import pygame

pygame.init()

import os
import sys
from scripts import interactions, battle_system, inventory
from scripts.weapons import create_weapon
from scripts import weapon_swap, consume_battle
from scripts import blacksmith
from scripts import temple

# --- 기본 설정 ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5

# --- 텍스트 줄바꿈 함수 ---
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

# --- 맵 설정 ---
MAP_WIDTH = 1024
MAP_HEIGHT = 1024

pftg_icon = pygame.image.load("resources\\png\\pftg_icon.png")
game_state = {
    "state": "start",  # start, town, battle등등
    "player_name": "Hero",
    "gold": 10000000,  # 초기 골드 추가
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

# --- 배경 이미지 로드 (화면 설정 후) ---
try:
    town_bg = pygame.image.load("resources\\png\\town_bg.png").convert()
    town_bg = pygame.transform.scale(town_bg, (MAP_WIDTH, MAP_HEIGHT))
    print("배경 이미지 로드 성공!")
except Exception as e:
    print(f"배경 이미지 로드 실패: {e}")
    town_bg = None

# --- 배경 오버레이 이미지 로드 (건물 위, 플레이어 아래에 그려짐) ---
try:
    town_overlay = pygame.image.load("resources\\png\\town_bg_1.png").convert_alpha()
    town_overlay = pygame.transform.scale(town_overlay, (MAP_WIDTH, MAP_HEIGHT))
    print("오버레이 이미지 로드 성공!")
except Exception as e:
    print(f"오버레이 이미지 로드 실패: {e}")
    town_overlay = None

# --- 색상 정의 ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# --- 히트박스 전용 오브젝트 클래스 (이미지 선택 가능) ---
class HitboxObject(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image=None, image_offset=(0, 0)):
        """
        image: 이미지 경로 (None이면 이미지 없음)
        image_offset: 히트박스 기준 이미지 오프셋 (x, y)
        """
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        
        # 이미지 설정
        if image:
            self.image = pygame.image.load(image).convert_alpha()
            # 이미지 위치 계산 (히트박스 기준 오프셋)
            img_x = x + image_offset[0]
            img_y = y + image_offset[1]
            self.image_rect = self.image.get_rect(topleft=(img_x, img_y))
        else:
            self.image = None
            self.image_rect = None

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
    def __init__(self, name, x, y, width, height, image=None, on_interact=None, hitbox=None, interact_area=None):
        """
        hitbox: (offset_x, offset_y, width, height) 튜플
                offset_x, offset_y는 이미지 좌상단 기준 오프셋
                None이면 이미지 하단 기준 자동 생성
        interact_area: (offset_x, offset_y, width, height) 튜플
                       offset_x, offset_y는 이미지 좌상단 기준 오프셋
                       None이면 이미지 하단 중앙에 자동 생성
        """
        super().__init__()
        self.name = name
        self.on_interact = on_interact

        # 이미지 설정 (없으면 회색 박스)
        if image:
            self.image = pygame.transform.scale(pygame.image.load(image), (width, height))
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((150, 150, 150))

        self.image_rect = self.image.get_rect(topleft=(x, y))
        
        # 히트박스 설정
        if hitbox:
            hb_offset_x, hb_offset_y, hb_width, hb_height = hitbox
            hb_x = x + hb_offset_x
            hb_y = y + hb_offset_y
        else:
            # 기본값: 이미지 하단 중앙, 너비 80%, 높이 20px
            hb_width = int(width * 0.8)
            hb_height = 20
            hb_x = x + (width - hb_width) // 2
            hb_y = y + height - hb_height
        
        self.rect = pygame.Rect(hb_x, hb_y, hb_width, hb_height)  # 충돌 판정용

        # 상호작용 영역 설정
        if interact_area:
            ia_offset_x, ia_offset_y, ia_width, ia_height = interact_area
            ia_x = x + ia_offset_x
            ia_y = y + ia_offset_y
        else:
            # 기본값: 이미지 하단 중앙
            ia_width = 60
            ia_height = 30
            ia_x = x + (width - ia_width) // 2
            ia_y = y + height - ia_height // 2
        
        self.interact_rect = pygame.Rect(ia_x, ia_y, ia_width, ia_height)

    def interact(self):
        if self.on_interact:
            self.on_interact()
        else:
            print(f"{self.name}과 상호작용 중...")

# --- 그룹 생성 ---
all_sprites = pygame.sprite.Group()
buildings = pygame.sprite.Group()

# --- 플레이어 생성 (맵 중앙에서 시작) ---
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
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

easter_egg = Building(
    "이스터에그", 705, 576, 128, 192, "resources\\png\\building\\easter_egg.png",
    on_interact=lambda: interactions.get_easter(game_state),
    hitbox=(0, 0, 0, 0),
    interact_area=(53, 47, 23, 23)
)
buildings.add(easter_egg)
all_sprites.add(easter_egg)

# --- 건물 생성 (1024x1024 맵 기준) ---
# 위쪽 중앙 - 집 (165x165)
# 히트박스: 건물 하단부, 가로 중앙
# 상호작용: 히트박스 바로 아래
house = Building("집", 430, 91, 165, 165, "resources\\png\\building\\pretty_house.png",
    on_interact=lambda: interactions.home_interact(game_state),
    hitbox=(8, 90, 150, 50),
    interact_area=(50, 140, 65, 25)
)
buildings.add(house)
all_sprites.add(house)

# 위쪽 왼쪽 - 상점 (125x125)
# 히트박스: 건물 하단부
# 상호작용: 히트박스 바로 아래
shop = Building(
    "상점", 180, 101, 155, 155, "resources\\png\\building\\shop.png",
    on_interact=lambda: interactions.enter_shop(game_state),
    hitbox=(6, 80, 143, 50),
    interact_area=(45, 131, 64, 24)
)
buildings.add(shop)
all_sprites.add(shop)

# 위쪽 오른쪽 - 대장간 (175x175)
# 히트박스: 건물 하단부
# 상호작용: 히트박스 바로 아래
forge = Building("대장간", 678, 81, 175, 175, "resources\\png\\building\\blacksmith.png",
    on_interact=lambda: interactions.enter_blacksmith(game_state),
    hitbox=(15, 125, 145, 30),
    interact_area=(60, 155, 60, 20)
)
buildings.add(forge)
all_sprites.add(forge)

# 왼쪽 밝은 길 끝 - 교회 (이미지 준비되면 주석 해제)
# church = Building("교회", 50, 420, 125, 125, "resources\\png\\building\\church.png",
#     hitbox=(10, 95, 105, 25),
#     interact_area=(30, 120, 65, 30)
# )
# buildings.add(church)
# all_sprites.add(church)

# 아래쪽 보라색 영역 - 던전 (128x192)
# 히트박스: 건물 하단부 (던전은 세로로 길어서 아래쪽에)
# 상호작용: 히트박스 바로 아래
dungeon = Building(
    "던전", 705, 576, 128, 192, "resources\\png\\building\\dungeon.png",
    on_interact=lambda: interactions.enter_dungeon(
        battle_system.start_battle, game_state, game_state["player_name"]
    ),
    hitbox=(0, 125, 128, 65),
    interact_area=(30, 190, 68, 20)
)
buildings.add(dungeon)
all_sprites.add(dungeon)

# 왼쪽 - 신전 (128x128)
temple_building = Building(
    "신전", 177, 480, 160, 160, "resources\\png\\building\\temple.png",
    on_interact=lambda: interactions.enter_temple(game_state),
    hitbox=(9, 80, 143, 60),
    interact_area=(47, 140, 66, 20)
)
buildings.add(temple_building)
all_sprites.add(temple_building)

# --- 히트박스 전용 오브젝트 (배경에 이미지 포함됨) ---
# 나무 그루터기 - town_bg_2.png
# 히트박스 위치: (280, 890), 크기: 90x25
# 이미지 오프셋: 히트박스 기준으로 이미지가 위에 그려지도록 조정
stump = HitboxObject(280, 890, 90, 25, 
    image="resources\\png\\town_bg_2.png",
    image_offset=(-280, -890)  # 이미지가 히트박스 위쪽에 그려지도록 (조정 필요)
)
buildings.add(stump)

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
                        # HitboxObject는 상호작용 없음
                        if isinstance(building, HitboxObject):
                            continue
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
            screen.fill((50, 50, 50))  # 맵 밖 영역은 어두운 색
            
            # --- 배경 이미지 그리기 ---
            if town_bg:
                screen.blit(town_bg, (-camera_offset.x, -camera_offset.y))

            # --- 플레이어와 건물을 Y좌표(히트박스 하단) 기준으로 정렬해서 그리기 ---
            # 플레이어 정보 준비
            player_depth = player.hitbox.bottom  # 플레이어 히트박스 하단 Y
            player_image_bottom_y = HEIGHT // 2 + player.hitbox.height // 2
            player_image_top_y = player_image_bottom_y - player.image_height
            player_image_rect = player.display_image.get_rect(centerx=WIDTH // 2, top=player_image_top_y)
            
            # 그릴 대상 리스트 만들기 (depth, type, data)
            render_list = []
            
            # 건물 추가
            for building in buildings:
                render_list.append((building.rect.bottom, "building", building))
            
            # 플레이어 추가
            render_list.append((player_depth, "player", None))
            
            # Y좌표(depth) 기준 정렬 (작은 값이 먼저 = 뒤에 그려짐)
            render_list.sort(key=lambda x: x[0])
            
            # 정렬된 순서대로 그리기
            for depth, obj_type, obj in render_list:
                if obj_type == "building":
                    # HitboxObject 처리
                    if isinstance(obj, HitboxObject):
                        # 이미지가 있으면 그리기
                        if obj.image:
                            screen.blit(obj.image, obj.image_rect.topleft - camera_offset)
                        continue
                    
                    # 건물 이미지 그리기
                    screen.blit(obj.image, obj.image_rect.topleft - camera_offset)
                    
                elif obj_type == "player":
                    # 오버레이 이미지 그리기 (플레이어 아래에)
                    if town_overlay:
                        screen.blit(town_overlay, (-camera_offset.x, -camera_offset.y))
                    
                    # 플레이어 그리기
                    screen.blit(player.display_image, player_image_rect)

            # --- 디버깅용 테두리 (플레이어 위에 표시) ---
            # 건물 히트박스 및 상호작용 영역
            for building in buildings:
                if isinstance(building, HitboxObject):
                    # 히트박스 전용 오브젝트 (노란색 테두리)
                    hitbox_debug = building.rect.move(-camera_offset.x, -camera_offset.y)
                    pygame.draw.rect(screen, (255, 255, 0), hitbox_debug, 2)
                else:
                    # 건물 히트박스 (파란색 테두리)
                    hitbox_debug = building.rect.move(-camera_offset.x, -camera_offset.y)
                    pygame.draw.rect(screen, (0, 100, 255), hitbox_debug, 2)
                    
                    # 상호작용 영역 (빨간색 테두리)
                    debug_rect = building.interact_rect.move(-camera_offset)
                    pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

            # 플레이어 히트박스 (초록색 테두리)
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

            # 메시지가 있으면 하단에 텍스트박스로 출력 (전투 스타일)
            if game_state.get("message"):
                # 메시지 박스 (인벤토리와 동일한 스타일)
                text_box = pygame.Rect(50, HEIGHT - 150, WIDTH - 100, 100)
                pygame.draw.rect(screen, (20, 20, 20), text_box)
                pygame.draw.rect(screen, (255, 255, 255), text_box, 2)
                
                # 텍스트 줄바꿈 처리
                max_text_width = text_box.width - 40
                lines = wrap_text(game_state["message"], FONT_SMALL, max_text_width)
                
                # 여러 줄 렌더링
                y_offset = text_box.y + 20
                for line in lines:
                    text_surface = FONT_SMALL.render(line, True, (255, 255, 255))
                    screen.blit(text_surface, (text_box.x + 20, y_offset))
                    y_offset += 30
                
                # 타이머
                game_state["message_timer"] += dt
                if game_state["message_timer"] > 1.5:
                    game_state["message"] = ""
                    game_state["message_timer"] = 0

        case "inventory":
            inventory.draw_inventory(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT, 
                                    battle_system.battle_player, dt, FONT_PATH, game_state)
            
            # 인벤토리 입력 처리 (True 반환 시 이벤트 완전히 소비됨)
            event_consumed = inventory.handle_inventory_input(events, battle_system.battle_player)
            
            # 이벤트가 소비되지 않았을 때만 ESC/I 키 처리
            if not event_consumed:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if not inventory.is_info_screen_open() and not inventory.is_action_menu_open() and not inventory.is_weapon_select_open():
                                game_state["state"] = "town"
                        elif event.key == pygame.K_i:
                            if not inventory.is_info_screen_open() and not inventory.is_action_menu_open() and not inventory.is_weapon_select_open():
                                game_state["state"] = "town"

        case "shop":
            from scripts import shop
            shop.draw_shop(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT, game_state, dt, FONT_PATH)
            shop.handle_shop_input(events, game_state)
        
        case "blacksmith":
            blacksmith.draw_blacksmith(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT, game_state, dt, FONT_PATH)
            blacksmith.handle_blacksmith_input(events, game_state)
        
        case "temple":
            temple.draw_temple(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT, game_state, dt, FONT_PATH)
            temple.handle_temple_input(events, game_state)
                    
        case "battle":
            battle_system.update_battle(screen, FONT_SMALL, WIDTH, HEIGHT, game_state, events)

        case "weapon_swap":
            weapon_swap.draw_weapon_swap(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT,
                                        battle_system.battle_player, FONT_PATH)
            weapon_swap.handle_weapon_swap_input(events, battle_system.battle_player, game_state)
        
        case "consume_battle":
            consume_battle.draw_consume_battle(screen, FONT_MAIN, FONT_SMALL, WIDTH, HEIGHT,
                                              battle_system.battle_player)
            
            # 전투로 복귀하는 함수 (메시지 전달)
            def return_to_battle(message=""):
                game_state["state"] = "battle"
                consume_battle.reset_consume_battle_state()
                if message:
                    # 소모품 메시지 설정
                    battle_system.battle_state["consumable_message"] = message
                    battle_system.battle_state["showing_consumable_message"] = True
                    battle_system.battle_state["waiting_for_click"] = True
            
            consume_battle.handle_consume_battle_input(events, battle_system.battle_player, return_to_battle)

    # --- 화면 업데이트 ---
    pygame.display.flip()