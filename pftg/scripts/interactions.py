def enter_dungeon(game_state_ref):
    print("던전에 들어갑니다...")
    game_state_ref["state"] = "battle"  #  전역 참조 대신 딕셔너리로 상태 변경