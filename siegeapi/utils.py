def get_xp_to_next_lvl(lvl: int):
    if lvl == 0:
        return 500
    if lvl == 1:
        return 1_500
    if lvl in (2, 3):
        return 3_500
    if lvl in (4, 5):
        return 4_000
    if lvl in (6, 7, 8):
        return 4_500
    if lvl in (9, 10):
        return 5_500
    if lvl in (11, 12, 13):
        return 6_000
    if lvl in (14, 15, 16):
        return 6_500
    if lvl in (17, 18, 19):
        return 7_000
    if lvl in (20, 21, 22):
        return 7_500
    if lvl in (23, 24, 25):
        return 8_000
    if lvl in (26, 27, 28):
        return 8_500
    if lvl in (29, 30, 31):
        return 9_000
    if lvl in (32, 33, 34):
        return 9_500
    if lvl in (35, 36, 37):
        return 10_000
    return (lvl - 18) * 500


def get_total_xp(lvl: int, current_xp: int):
    total = 0
    for level in range(1, lvl):
        total += _get_xp_to_next_lvl(level)
    return total + current_xp
