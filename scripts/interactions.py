from scripts import battle_system

def enter_dungeon(battle_start_func, game_state_ref, player_name):
    """던전 진입 (체력이 0이면 입장 불가)"""
    player = battle_system.battle_player

    if not player:
        game_state_ref["message"] = "플레이어 정보가 없습니다."
        return

    if player.hp <= 0:
        game_state_ref["message"] = "체력이 부족해 던전에 들어갈 수 없습니다!"
        return
    
    print(f"{player_name}이(가) 던전에 들어갑니다!")
    battle_start_func(game_state_ref, player_name)

def home_interact(game_state_ref):
    """집과 상호작용: 체력 회복 + 페널티 적용"""
    player = battle_system.battle_player  # 전투 시스템의 플레이어 참조

    if not player:
        game_state_ref["message"] = "플레이어 정보가 없습니다."
        return

    if player.hp == player.max_hp:
        game_state_ref["message"] = "이미 체력이 가득 찼습니다."
        return

    # HP 회복
    player.hp = player.max_hp

    # 간단한 페널티 (예시: 골드 감소)
    game_state_ref["gold"] = max(0, game_state_ref.get("gold", 100) - 10)
    game_state_ref["message"] = "휴식을 취했습니다. 체력이 회복되었지만 10G를 잃었습니다."

def enter_shop(game_state_ref):
    """상점 진입"""
    print("상점에 들어갑니다...")
    game_state_ref["state"] = "shop"

def get_easter(game_state_ref):
    """이스터에그 상호작용 - 테스트 무기 지급"""
    from scripts.weapons import create_weapon
    from scripts.inventory import player_inventory
    
    # 이미 받았는지 확인
    if game_state_ref.get("easter_claimed", False):
        game_state_ref["message"] = "이미 보물을 획득했습니다!"
        return
    
    # 테스트 무기 지급
    weapon_id = "test_sword"
    new_weapon = create_weapon(weapon_id)
    
    if new_weapon:
        player_inventory["weapons"].append(new_weapon)
        game_state_ref["easter_claimed"] = True
        game_state_ref["message"] = f"축하합니다! {new_weapon.name}을(를) 발견했습니다!"
        print(f"이스터에그: {new_weapon.name} 획득!")
    else:
        game_state_ref["message"] = "이스터에그를 발견했습니다!"