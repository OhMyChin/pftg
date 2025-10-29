import pygame
import sys
from scripts import interactions

# --- 기본 설정 ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
pftg_icon = pygame.image.load("resources\\pftg_icon.png")
game_state = {"state": "start"}  # start, town, battle
blink_timer = 0

# --- 초기화 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PFTG")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 60)

# --- 색상 정의 ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# --- 플레이어 클래스 ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)

    def handle_input(self, buildings_group):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)

        # 방향 벡터 계산
        if keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_s]:
            direction.y += 1
        if keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_d]:
            direction.x += 1

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

# --- 건물 클래스 ---
class Building(pygame.sprite.Sprite):
    def __init__(self, name, x, y, width, height, image=None,  on_interact=None):
        super().__init__()
        self.name = name
        self.on_interact = on_interact

        # 이미지 설정 (없으면 회색 박스)
        if image:
            self.image = pygame.transform.scale(pygame.image.load(image), (width, height))
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((150, 150, 150))  # 기본 색상

        self.rect = self.image.get_rect(topleft=(x, y))

        # 상호작용 영역 생성 (건물 아래 중앙)
        interact_width = 60
        interact_height = 30
        interact_x = x + (width - interact_width) // 2
        interact_y = y + height - interact_height // 2
        self.interact_rect = pygame.Rect(interact_x, interact_y, interact_width, interact_height)

    def interact(self):
        if self.on_interact:
            self.on_interact()  # ✅ 지정된 함수 실행
        else:
            print(f"{self.name}과 상호작용 중...")  # 기본 동작

# --- 그룹 생성 ---
all_sprites = pygame.sprite.Group()
buildings = pygame.sprite.Group()

# --- 플레이어 생성 ---
player = Player(400, 300)
all_sprites.add(player)

# --- 예시 건물 생성 ---
house = Building("작은 집", 500, 300, 100, 100)
buildings.add(house)
all_sprites.add(house)

house2 = Building("큰 집", 100, 300, 150, 150)
buildings.add(house2)
all_sprites.add(house2)

house3 = Building("이쁜 집", 200, -100, 125, 125, "resources\\pretty_house.png")
buildings.add(house3)
all_sprites.add(house3)

dungeon = Building(
    "던전", 500, 600, 120, 200, "resources\\dungeon.png",
    on_interact=lambda: interactions.enter_dungeon(game_state)
)
buildings.add(dungeon)
all_sprites.add(dungeon)

# --- 카메라 오프셋 ---
camera_offset = pygame.Vector2(0, 0)

# --- E 키 상호작용 상태 변수 ---
e_key_pressed = False

# --- 메인 게임 루프 ---
while True:
    dt = clock.tick(FPS) / 1000  # 프레임 시간 계산

    # --- 이벤트 처리 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    match game_state["state"]:
        # 시작 화면
        case "start":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                game_state["state"] = "town"

            screen.fill((0, 0, 0))
            blink_timer += dt
            if int(blink_timer * 2) % 2 == 0:   # 0.5초마다 깜빡임
                text = font.render("Press Enter to Start", True, (255, 255, 255))
                rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(text, rect)

        # 마을 화면
        case "town":
            # --- 입력 처리 및 이동 ---
            player.handle_input(buildings)

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

            # --- 화면 그리기 ---
            screen.fill(WHITE)

            # --- 건물 그리기 (카메라 오프셋 적용) ---
            for building in buildings:
                screen.blit(building.image, building.rect.topleft - camera_offset)

                # 디버깅용: 상호작용 영역 시각화 (빨간색 테두리)
                debug_rect = building.interact_rect.move(-camera_offset)
                pygame.draw.rect(screen, (255, 0, 0), debug_rect, 1)

            # --- 플레이어 그리기 (항상 화면 중앙에 위치) ---
            player_screen_pos = (WIDTH // 2 - player.rect.width // 2, HEIGHT // 2 - player.rect.height // 2)
            screen.blit(player.image, player_screen_pos)

        # 전투 화면
        case "battle":
                screen.fill((50, 50, 100))
                text = font.render("fight scene", True, (255, 255, 255))
                rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(text, rect)

                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:  # ESC로 마을 복귀
                    game_state["state"] = "town"

    # --- 화면 업데이트 ---
    pygame.display.flip()
    pygame.display.set_icon(pftg_icon)