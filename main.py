import pygame as pg, ctypes, sys, itertools, random, load_art as art
from ui_tools import Button, Scroller
from game_units import Unit, Building, PowerUp, Terrain

# declare globals
game_state = 1
sound = True
music = False
reset = True
all_unlocks = False

# grid related vars
grid_width = 12
grid_height = 36
grid = [[None for x in range(grid_width)] for x in range(grid_height)]
# adj vars = how far from (0, 0) does the grid Surface start
adj_x = 50
adj_y = 30
# cell size, how big are the cells = abbreviated to c
c = 0
grid_scroll = 0
# list of items populating the grid
item_list = []

# orientation tools (what cell am I selecting, what unit is in that cell)
selected_cell = None
selected_unit = None

# graphic tool: has the move/attack/range graphic been requested and what squares should be highlighted
click_graphic = 0
graphic_squares = []

# who has the turn and can do things?
turn = 0
turn_map = {0: 'Blue', 1: 'Red'}
round_counter = 1

# current unit limits:
unit_limit = {'Blue': 5, 'Red': 5}
# secret documents per team:
secret_docs = {'Blue': 0, 'Red': 0}
# unlocked structures per team:
build_unlocks = {'Blue': 0, 'Red': 0}
# docs to win the game
doc_limit = 20
# coords adjacent to collection posts
collection_coords = [(0, 1), (1, 0), (2, 1), (1, 2), (10, 0), (9, 1), (10, 2), (11, 1), (1, 33), (0, 34), (1, 35), \
                     (2, 34), (10, 35), (9, 34), (10, 33), (11, 34)]

game_over = False


def set_screen():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1) - 79
    return w, h


def asteroid_effect(ast_list):
    proc_asteroid = random.randint(0, 120)
    if proc_asteroid == 0:
        ast_list.append(art.MenuAsteroid(w, h, screen))
    for asteroid in ast_list:
        asteroid.draw()
        if asteroid.x > w or asteroid.x < 0 - asteroid.size or asteroid.y > h or asteroid.y < 0 - asteroid.size:
            asteroid.destroy()
            ast_list.remove(asteroid)


def make_click():
    click = pg.mixer.Sound('art/click.wav')
    if sound:
        click.play()


def main_menu():
    global w, h, screen
    play_button = Button(art.DARK_GREY, 400, 250, 350, 250, 'Play', 60, 'rockwell')
    settings_button = Button(art.DARK_GREY, 400, 550, 350, 250, 'Settings', 60, 'rockwell')
    tutorial_button = Button(art.DARK_GREY, w - 750, 250, 350, 250, 'Tutorial', 60, 'rockwell')
    quit_button = Button(art.DARK_GREY, w - 750, 550, 350, 250, 'Quit', 60, 'rockwell')
    are_you_sure_button = Button(art.WHITE, int(w / 2) - 200, 200, 400, 200, 'Are you sure?', txt_size=65)
    yes_button = Button(art.RED, int(w / 2) - 170, 330, 80, 60, 'yes')
    no_button = Button(art.GREEN, int(w / 2) + 90, 330, 80, 60, 'no')
    are_you_sure = False
    image_map = {
        0: art.BlueScoutIMG, 1: art.BlueEnginnerIMG, 2: art.BlueSoldierIMG, 3: art.RedSpyIMG, 4: art.RedScoutIMG,
        5: art.WildBerryIMG, 6: art.TeleIMG
    }
    ast_list = []
    while game_state == 1:
        screen.fill(art.TITLE_GREY)
        art.draw_menu_border(w, h, screen)
        asteroid_effect(ast_list)
        screen.blit(art.InfiltrateTEXT, (round(w / 2 - (art.TitleWidth / 2)), 100))
        screen.blit(art.return_icon(image_map.get(0)), (100, 150))
        screen.blit(art.return_icon(image_map.get(1)), (80, 450))
        screen.blit(art.return_icon(image_map.get(2)), (110, 750))
        screen.blit(art.return_flipped(art.return_icon(image_map.get(3))), (w - 250, 250))
        screen.blit(art.return_flipped(art.return_icon(image_map.get(4))), (w - 280, 600))
        screen.blit(art.return_icon(image_map.get(5)), (round((w / 2) - 150), 300))
        screen.blit(art.return_icon(image_map.get(6)), (round((w / 2) - 90), 650))
        play_button.draw(screen, art.BLACK)
        settings_button.draw(screen, art.BLACK)
        tutorial_button.draw(screen, art.BLACK)
        quit_button.draw(screen, art.BLACK)
        if are_you_sure:
            are_you_sure_button.draw(screen, art.BLACK)
            yes_button.draw(screen, art.BLACK)
            no_button.draw(screen, art.BLACK)
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    are_you_sure = True
            if event.type == pg.MOUSEBUTTONDOWN:
                if play_button.is_over(event.pos):
                    return 3
                if settings_button.is_over(event.pos):
                    return 2
                if tutorial_button.is_over(event.pos):
                    return 4
                if quit_button.is_over(event.pos):
                    are_you_sure = True
                if are_you_sure:
                    if yes_button.is_over(event.pos):
                        return 0
                    if no_button.is_over(event.pos):
                        are_you_sure = False
                make_click()
            if event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
                w, h = event.w, event.h
            if event.type == pg.QUIT:
                return 0

        pg.display.update()
        clock.tick(60)


def draw_settings():
    switch = {True: 'on', False: 'off'}
    draw_text = art.render_text('Sound', 'rockwell', 98, art.BLACK)
    screen.blit(draw_text, (110, 100))
    draw_text = art.render_text(switch.get(sound), 'rockwell', 64, art.BLACK)
    screen.blit(draw_text, (425, 115))
    draw_text = art.render_text('Music', 'rockwell', 98, art.BLACK)
    screen.blit(draw_text, (110, 300))
    draw_text = art.render_text(switch.get(music), 'rockwell', 64, art.BLACK)
    screen.blit(draw_text, (425, 315))
    draw_text = art.render_text('Unlocks', 'rockwell', 98, art.BLACK)
    screen.blit(draw_text, (110, 500))
    draw_text = art.render_text(switch.get(all_unlocks), 'rockwell', 64, art.BLACK)
    screen.blit(draw_text, (485, 515))
    draw_text = art.render_text('(on: automatically unlock all buildings)', 'hpsimplified', 42, art.BLACK)
    screen.blit(draw_text, (600, 515))


def toggle_music():
    track1 = pg.mixer.music.load('art/game_track.wav')
    if music and not game_over:
        pg.mixer.music.play(-1)
    else:
        pg.mixer.music.stop()


def settings_menu():
    global w, h, screen, sound, music, reset, all_unlocks
    back_button = Button(art.DARK_GREY, (w - 130), 30, 100, 50, 'Back', 40, 'rockwell')
    sound_up = Button(art.DARK_GREY, 435, 90, 65, 35, shape='tri', sub_shape='up')
    sound_down = Button(art.DARK_GREY, 435, 190, 65, 35, shape='tri', sub_shape='down')
    music_up = Button(art.DARK_GREY, 435, 290, 65, 35, shape='tri', sub_shape='up')
    music_down = Button(art.DARK_GREY, 435, 390, 65, 35, shape='tri', sub_shape='down')
    reset_button = Button(art.DARK_GREY, 110, 700, 400, 100, 'Reset Game', 60, 'rockwell')
    unlocks_up = Button(art.DARK_GREY, 495, 490, 65, 35, shape='tri', sub_shape='up')
    unlocks_down = Button(art.DARK_GREY, 495, 590, 65, 35, shape='tri', sub_shape='down')
    ast_list = []
    while game_state == 2:
        screen.fill(art.TITLE_GREY)
        art.draw_menu_border(w, h, screen)
        asteroid_effect(ast_list)
        back_button.draw(screen, art.BLACK)
        reset_button.draw(screen, art.BLACK)
        if sound:
            sound_down.draw(screen, art.BLACK)
        else:
            sound_up.draw(screen, art.BLACK)
        if music:
            music_down.draw(screen, art.BLACK)
        else:
            music_up.draw(screen, art.BLACK)
        if all_unlocks:
            unlocks_down.draw(screen, art.BLACK)
        else:
            unlocks_up.draw(screen, art.BLACK)
        draw_settings()
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 1
            if event.type == pg.MOUSEBUTTONDOWN:
                if back_button.is_over(event.pos):
                    return 1
                if sound_up.is_over(event.pos):
                    sound = True
                if sound_down.is_over(event.pos):
                    sound = False
                if music_up.is_over(event.pos):
                    music = True
                    toggle_music()
                if music_down.is_over(event.pos):
                    music = False
                    toggle_music()
                if reset_button.is_over(event.pos):
                    reset = True
                if unlocks_up.is_over(event.pos):
                    all_unlocks = True
                if unlocks_down.is_over(event.pos):
                    all_unlocks = False
                make_click()
            if event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
                w, h = event.w, event.h
            if event.type == pg.QUIT:
                return 0

        pg.display.update()
        clock.tick(60)


def draw_grid_lines(grid_space, w, h):
    for line in range(grid_width - 1):
        line_start = c * (line + 1)
        pg.draw.line(grid_space, art.BLACK, (line_start, 0), (line_start, h), 6)
        pg.draw.line(grid_space, art.BLACK, (0, line_start), (w, line_start), 6)
    pg.draw.line(screen, art.BLACK, (adj_x - 2, adj_y - 2), (adj_x - 2, h + adj_y + 2), 8)
    pg.draw.line(screen, art.BLACK, (adj_x - 2, adj_y - 2), (w + adj_x + 2, adj_y - 2), 8)
    pg.draw.line(grid_space, art.BLACK, (w + 2, -2), (w + 2, h + 4), 8)
    pg.draw.line(grid_space, art.BLACK, (-2, h + 2), (w + 4, h + 2), 8)


def draw_game_text(grid_w):
    draw_text = art.render_text(f"Round {round_counter}: ", 'hpsimplified', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 300, 20))
    text_length = draw_text.get_width()
    if turn:
        draw_text = art.render_text(turn_map.get(turn), 'hpsimplified', 48, art.RED)
    else:
        draw_text = art.render_text(turn_map.get(turn), 'hpsimplified', 48, art.BLUE)
    screen.blit(draw_text, (grid_w + 300 + text_length, 20))
    text_length += draw_text.get_width()
    draw_text = art.render_text("'s turn", 'hpsimplified', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 300 + text_length, 20))
    # and draw text border for draw_display_text() below
    pg.draw.rect(screen, art.WHITE, (grid_w + 145, 475, 820, 490))
    pg.draw.line(screen, art.BLACK, (grid_w + 145, 475), (grid_w + 145, 965), 8)
    pg.draw.line(screen, art.BLACK, (grid_w + 145, 475), (grid_w + 965, 475), 8)
    pg.draw.line(screen, art.BLACK, (grid_w + 145, 965), (grid_w + 965, 965), 8)
    pg.draw.line(screen, art.BLACK, (grid_w + 965, 475), (grid_w + 965, 965), 8)


def draw_team_stats(grid_w, count, active):
    if turn:
        draw_text = art.render_text(f'Units: {count}/{unit_limit.get("Red")}', 'rockwell', 24, art.RED)
    else:
        draw_text = art.render_text(f'Units: {count}/{unit_limit.get("Blue")}', 'rockwell', 24, art.BLUE)
    screen.blit(draw_text, (grid_w + 670, 100))
    if turn:
        draw_text = art.render_text(f'With activities: {active}', 'rockwell', 24, art.RED)
    else:
        draw_text = art.render_text(f'With activities: {active}', 'rockwell', 24, art.BLUE)
    screen.blit(draw_text, (grid_w + 670, 140))
    if turn:
        draw_text = art.render_text(f'Secret Documents: {secret_docs.get("Red")}/{doc_limit}', 'rockwell', 24, art.RED)
    else:
        draw_text = art.render_text(f'Secret Documents: {secret_docs.get("Blue")}/{doc_limit}', 'rockwell', 24, \
                                    art.BLUE)
    screen.blit(draw_text, (grid_w + 670, 180))


def draw_display_stats(grid_w, unit):
    if unit.static:
        if selected_unit.produce is not None:
            if selected_unit.queue is None:
                draw_text = art.render_text('No units in build queue', 'rockwell', 24, art.BLACK)
            else:
                draw_text = \
                    art.render_text(f'{selected_unit.queue_timer} round(s) until spawn', 'rockwell', 24, art.BLACK)
                screen.blit(draw_text, (grid_w + 670, 260))
                draw_text = art.render_text(f'{selected_unit.queue} in build queue', 'rockwell', 24, art.BLACK)
            screen.blit(draw_text, (grid_w + 670, 220))
        elif selected_unit.game_id == 'Construction':
            draw_text = art.render_text(f'{selected_unit.construct_timer} round(s) until finish', \
                                        'rockwell', 24, art.BLACK)
            screen.blit(draw_text, (grid_w + 670, 220))
    else:
        if unit.steps_remaining > 0:
            draw_text = art.render_text(f'{unit.steps_remaining} steps remaining', 'rockwell', 24, art.BLACK)
        else:
            draw_text = art.render_text('No steps remaining', 'rockwell', 24, art.BLACK)
        screen.blit(draw_text, (grid_w + 670, 220))
        if not unit.can_attack:
            draw_text = art.render_text('No attack', 'rockwell', 24, art.BLACK)
        elif unit.has_attacked:
            draw_text = art.render_text('Attack used', 'rockwell', 24, art.BLACK)
        else:
            draw_text = art.render_text('Attack available', 'rockwell', 24, art.BLACK)
        screen.blit(draw_text, (grid_w + 670, 260))
        if unit.special_used:
            draw_text = art.render_text('Special move deployed', 'rockwell', 24, art.BLACK)
        elif unit.special_condition:
            draw_text = art.render_text('Special move available', 'rockwell', 24, art.BLACK)
        else:
            draw_text = art.render_text('Special move unavailable', 'rockwell', 24, art.BLACK)
        screen.blit(draw_text, (grid_w + 670, 300))
        if unit.carrying:
            draw_text = art.render_text('Carrying Secret Document', 'rockwell', 24, art.YELLOW)
            screen.blit(draw_text, (grid_w + 670, 340))


def draw_display_text(grid_w, unit):
    build_select = Button(art.WHITE, (grid_w + 650), 670, 200, 200, '', 40, 'rockwell')
    build_up = Button(art.WHITE, (grid_w + 725), 635, 50, 25, shape='tri', sub_shape='up')
    build_down = Button(art.WHITE, (grid_w + 725), 880, 50, 25, shape='tri', sub_shape='down')
    cancel_build_button = Button(art.WHITE, (grid_w + 805), 485, 150, 50, 'cancel', 30, 'rockwell')
    if unit.team is None:
        draw_text = art.render_text(f"{unit.game_id}", 'rockwell', 48, art.BLACK)
    else:
        draw_text = art.render_text(f"Health: {unit.current_hp}/{unit.hp}", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text(f"{unit.team} {unit.game_id}", 'rockwell', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 500 - int(draw_text.get_width() / 2), 400))
    if unit.team is None:
        description = unit.generic_description()
        if type(description) == list:
            for line, part in enumerate(description):
                draw_text = art.render_text(part, 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 500 + (line * 40)))
        else:
            draw_text = art.render_text(description, 'hpsimplified', 48, art.BLACK)
            screen.blit(draw_text, (grid_w + 160, 500))
    else:
        if unit.static:
            if unit.produce is not None:
                draw_text = art.render_text(f"Production time: {unit.produce_time}", 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 560))
            elif unit.range is not None:
                draw_text = art.render_text(f"Range: {unit.range}", 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 560))
            elif unit.game_id == 'Construction':
                draw_text = art.render_text(f"{unit.con_type} under construction", 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 560))
            draw_text = art.render_text(f"{unit.w} x {unit.h}", 'hpsimplified', 48, art.BLACK)
            screen.blit(draw_text, (grid_w + 160, 620))
            description = unit.building_description()
            if type(description) == list:
                for line, part in enumerate(description):
                    draw_text = art.render_text(part, 'hpsimplified', 48, art.BLACK)
                    screen.blit(draw_text, (grid_w + 160, 820 + (line * 40)))
            else:
                draw_text = art.render_text(description, 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 820))
        elif selected_unit.game_id == 'Engineer' and selected_unit.build_menu:
            build_select.draw(screen, art.BLACK)
            build_up.draw(screen, art.BLACK)
            build_down.draw(screen, art.BLACK)
            cancel_build_button.draw(screen, art.BLACK)
        else:
            if unit.can_attack:
                draw_text = art.render_text(f"Damage: {unit.damage}", 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 560))
                draw_text = art.render_text(f"Range: {unit.range}", 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 680))
            else:
                draw_text = art.render_text("Unarmed unit: cannot attack", 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 680))
            draw_text = art.render_text(f"Speed: {unit.speed}", 'hpsimplified', 48, art.BLACK)
            screen.blit(draw_text, (grid_w + 160, 620))
            draw_text = art.render_text(f"Special move: {unit.special_move}", 'hpsimplified', 48, art.BLACK)
            screen.blit(draw_text, (grid_w + 160, 740))
            description = unit.special_move_description()
            if type(description) == list:
                for line, part in enumerate(description):
                    draw_text = art.render_text(part, 'hpsimplified', 48, art.BLACK)
                    screen.blit(draw_text, (grid_w + 160, 820 + (line * 40)))
            else:
                draw_text = art.render_text(description, 'hpsimplified', 48, art.BLACK)
                screen.blit(draw_text, (grid_w + 160, 820))


def draw_build_menu_text(grid_w, building, dimensions):
    timer = 2
    hp = 200
    if building == 'Academy':
        purpose = 'Soldiers and scouts'
    elif building == 'Quarters':
        purpose = 'Increase unit limit'
        timer = 3
    elif building == 'Tower':
        purpose = 'Damage enemies'
        hp = 250
    elif building == 'Institute':
        purpose = 'Spies and snipers'
        timer = 4
    elif building == 'Med Bay':
        purpose = 'Heal allies'
        timer = 3
        hp = 150
    elif building == 'Teleporter':
        purpose = 'Transport units'
        timer = 3
        hp = 100
    draw_text = art.render_text(f"Structures unlocked: {build_unlocks.get(turn_map.get(turn))}/4", \
                                'hpsimplified', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 160, 560))
    draw_text = art.render_text(f"Total structures: {build_unlocks.get(turn_map.get(turn)) + 2}", \
                                'hpsimplified', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 160, 620))
    draw_text = art.render_text(building, 'hpsimplified', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 350, 700))
    text_w = draw_text.get_width()
    draw_text = art.render_text(str(dimensions), 'hpsimplified', 48, art.BLACK)
    screen.blit(draw_text, (grid_w + 360 + text_w, 700))
    draw_text = art.render_text(purpose, 'hpsimplified', 36, art.BLACK)
    screen.blit(draw_text, (grid_w + 350, 750))
    draw_text = art.render_text(f'{timer} rounds to build', 'hpsimplified', 36, art.BLACK)
    screen.blit(draw_text, (grid_w + 350, 800))
    draw_text = art.render_text(f'{hp} health', 'hpsimplified', 36, art.BLACK)
    screen.blit(draw_text, (grid_w + 350, 850))


def find_grid_coords(x, y, w):
    found = False
    grid_x = 0
    grid_y = 0
    y_max = round(w / grid_width) + adj_y
    y_min = adj_y
    while not found:
        x_max = round(w / grid_width) + adj_x
        x_min = adj_x
        for space in range(grid_width):
            if x_max >= x >= x_min and y_max >= y >= y_min:
                return grid_x, grid_y + grid_scroll
            else:
                x_min += round(w / grid_width)
                x_max += round(w / grid_width)
                grid_x += 1
        grid_x = 0
        y_max += round(w / grid_width)
        y_min += round(w / grid_width)
        grid_y += 1


def find_move_squares():
    # ox, oy = origin_x, origin_y...
    ox, oy = selected_cell
    if oy - selected_unit.steps_remaining < 0:
        start_index = 0
    else:
        start_index = oy - selected_unit.steps_remaining
    if oy + selected_unit.steps_remaining > grid_height:
        end_index = grid_height
    else:
        end_index = oy + selected_unit.steps_remaining + 1
    for y, row in enumerate(grid[start_index:end_index], start_index):
        for x, item in enumerate(row):
            if valid_move(selected_unit, selected_unit.xy, (x, y), item):
                graphic_squares.append((x, y))


def find_attack_targets():
    if selected_cell[1] - selected_unit.range <= 0:
        start_index = 0
    else:
        start_index = int(selected_cell[1] - selected_unit.range)
    if selected_cell[1] + selected_unit.range >= grid_height:
        end_index = grid_height
    else:
        end_index = int(selected_cell[1] + selected_unit.range + 1)
    for y, row in enumerate(grid[start_index:end_index], start_index):
        for x, item in enumerate(row):
            if item is not None:
                if item.multi_cell:
                    if valid_attack(selected_unit, selected_cell, (x, y), item) and not item in graphic_squares:
                        graphic_squares.append(item)
                else:
                    if valid_attack(selected_unit, selected_cell, item.xy, item):
                        graphic_squares.append(item)


def find_range():
    if selected_unit.multi_cell:
        ox, oy = selected_unit.xy[0]
        end_h = selected_unit.h
    else:
        ox, oy = selected_cell
        end_h = 1
    if oy - selected_unit.range < 0:
        start_index = 0
    else:
        start_index = oy - selected_unit.range
    if oy + selected_unit.range + end_h > grid_height:
        end_index = grid_height
    else:
        end_index = oy + selected_unit.range + end_h
    for y, row in enumerate(grid[start_index:end_index], start_index):
        for x, item in enumerate(row):
            if selected_unit.multi_cell:
                for coord in selected_unit.xy:
                    ox, oy = coord
                    xy = x, y
                    if abs(ox - x) + abs(oy - y) == selected_unit.range and xy not in selected_unit.xy:
                        graphic_squares.append((x, y))
            elif selected_unit.game_id == 'Engineer':
                if abs(ox - x) + abs(oy - y) == selected_unit.range and grid[y][x] is None:
                    graphic_squares.append((x, y))
            else:
                if abs(ox - x) + abs(oy - y) == selected_unit.range:
                    graphic_squares.append((x, y))


def draw_graphics(grid_space, w):
    # c here is cell size in pixels (declared globally)
    # cor = correct: slight grid adjustment
    cor = 2
    visible = []
    for y, row in enumerate(grid[grid_scroll:grid_scroll + 12]):
        for x, item in enumerate(row):
            if item is not None and item not in visible:
                visible.append(item)
            draw_x, draw_y = c * x, c * y + cor
    for item in visible:
        if item.multi_cell:
            x, y = item.xy[0]
            y -= grid_scroll
        else:
            x = item.xy[0]
            y = item.xy[1] - grid_scroll
        draw_x, draw_y = c * x, c * y + cor
        grid_space.blit(item.image, (draw_x, draw_y))
    if type(selected_cell) == tuple and grid_scroll + 12 >= selected_cell[1] >= grid_scroll:
        if selected_unit is not None and selected_unit.multi_cell:
            x, y = selected_unit.xy[0]
            y -= grid_scroll
            draw_x, draw_y = c * x, c * y
            draw_w, draw_h = c * selected_unit.w + 1, c * selected_unit.h + 1
        else:
            x, y = selected_cell[0], selected_cell[1] - grid_scroll
            draw_x, draw_y = c * x, c * y
            draw_w, draw_h = c + 1, c + 1
        if click_graphic == 1 and selected_unit.steps_remaining > 0:
            if len(graphic_squares) == 0:
                find_move_squares()
                graphic_squares.append('Search complete')
            for square in graphic_squares[:-1]:
                if grid_scroll + 12 >= square[1] >= grid_scroll:
                    x, y = square[0], square[1] - grid_scroll
                    draw_x, draw_y = c * x, c * y
                    draw_w, draw_h = c + 1, c + 1
                    pg.draw.rect(grid_space, art.GREEN, (draw_x, draw_y, draw_w, draw_h), 3)
        else:
            pg.draw.rect(grid_space, art.RED, (draw_x, draw_y, draw_w, draw_h), 1)
            if click_graphic == 2 and selected_unit.activities[1] == 0:
                if len(graphic_squares) == 0:
                    find_attack_targets()
                    graphic_squares.append('Search complete')
                for target in graphic_squares[:-1]:
                    if target.multi_cell:
                        x, y = target.xy[0]
                        y -= grid_scroll
                        draw_x, draw_y = c * x, c * y
                        draw_w, draw_h = c * target.w + 1, c * target.h + 1
                    else:
                        x, y = target.xy[0], target.xy[1] - grid_scroll
                        draw_x, draw_y = c * x, c * y
                        draw_w, draw_h = c + 1, c + 1
                    pg.draw.rect(grid_space, art.YELLOW, (draw_x, draw_y, draw_w, draw_h), 3)
            elif click_graphic == 3:
                if len(graphic_squares) == 0:
                    find_range()
                for square in graphic_squares:
                    if grid_scroll + 12 >= square[1] >= grid_scroll:
                        x, y = square[0], square[1] - grid_scroll
                        draw_x, draw_y = c * x, c * y
                        draw_w, draw_h = c + 1, c + 1
                        pg.draw.rect(grid_space, art.YELLOW, (draw_x, draw_y, draw_w, draw_h), 3)


def game_reset():
    global grid, selected_cell, turn, round_counter, reset, grid_scroll, game_over
    grid = [[None for x in range(grid_width)] for x in range(grid_height)]
    item_list.clear()
    selected_cell = None
    grid_scroll = 0
    turn = 0
    round_counter = 1
    secret_docs['Blue'], secret_docs['Red'] = 0, 0
    if all_unlocks or game_state == 4:
        build_unlocks['Blue'], build_unlocks['Red'] = 4, 4
    else:
        build_unlocks['Blue'], build_unlocks['Red'] = 0, 0
    if game_state == 3:
        starting_units()
        reset = False
    else:
        reset = True
    game_over = False


def new_unit(x, y, team, game_id):
    item_list.append(Unit((x, y), team, game_id))
    unit = item_list[-1]
    grid[unit.xy[1]][unit.xy[0]] = unit
    unit.scale_image(c)


def new_building(x, y, team, game_id, con=None):
    if con is None:
        item_list.append(Building((x, y), team, game_id))
    else:
        item_list.append(Building((x, y), team, game_id, con_type=con))
    building = item_list[-1]
    if building.multi_cell:
        for coord in item_list[-1].xy:
            grid[coord[1]][coord[0]] = building
    else:
        coord = building.xy
        grid[coord[1]][coord[0]] = building
    building.scale_image(c)


def new_terrain(x, y, game_id):
    item_list.append(Terrain((x, y), game_id))
    terrain = item_list[-1]
    grid[terrain.xy[1]][terrain.xy[0]] = terrain
    terrain.scale_image(c)


def valid_move(unit, start, dest, dest_unit):
    if abs(start[0] - dest[0]) + abs(start[1] - dest[1]) <= unit.steps_remaining:
        if dest_unit is None or dest_unit.__class__.__name__ == 'PowerUp':
            return True
    return False


def move_unit(unit, start, dest, dest_unit):
    global game_over
    grid[start[1]][start[0]] = None
    if dest_unit is not None and dest_unit.__class__.__name__ == 'PowerUp':
        dest_unit.use_power(unit)
        item_list.remove(dest_unit)
        if sound:
            consume = pg.mixer.Sound('art/beep.wav')
            consume.play()
    grid[dest[1]][dest[0]] = unit
    unit.xy = dest
    unit.steps_remaining -= abs(start[0] - dest[0]) + abs(start[1] - dest[1])
    if start[0] > dest[0] and not unit.flipped or start[0] < dest[0] and unit.flipped:
        unit.flip_unit()
    if unit.game_id == 'Sniper':
        unit.special_condition = False
    if dest in collection_coords and unit.carrying:
        if sound:
            collected = pg.mixer.Sound('art/clacking.wav')
            collected.play()
        secret_docs[turn_map.get(turn)] += 1
        unit.carrying = False
        if secret_docs[turn_map.get(turn)] >= doc_limit:
            game_over = True
        elif secret_docs[turn_map.get(turn)] % 4 == 0:
            build_unlocks[turn_map.get(turn)] += 1


def valid_attack(unit, start, dest, dest_unit):
    if dest_unit is not None and dest_unit.team == turn_map.get(abs(turn - 1)):
        if dest_unit.multi_cell:
            for coord in dest_unit.xy:
                if abs(start[0] - coord[0]) + abs(start[1] - coord[1]) <= unit.range and unit.activities[1] == 0:
                    return True
            return False
        else:
            if abs(start[0] - dest[0]) + abs(start[1] - dest[1]) <= unit.range and unit.activities[1] == 0:
                if dest_unit.game_id == 'Spy' and dest_unit.activities[2] == 0:
                    return False
                else:
                    return True
            else:
                return False
    else:
        return False


def attack_unit(unit, start, dest, dest_unit):
    global grid, game_over
    dest_unit.current_hp -= unit.damage
    if unit.game_id == 'Soldier':
        attack_sound = pg.mixer.Sound('art/rifle.wav')
    elif unit.game_id == 'Spy':
        attack_sound = pg.mixer.Sound('art/stab.wav')
    else:
        attack_sound = pg.mixer.Sound('art/pistol.wav')
    if sound:
        attack_sound.play()
    if dest_unit.check_death():
        if dest_unit.static:
            explode = pg.mixer.Sound('art/explode.wav')
            if sound:
                explode.play()
        else:
            death = pg.mixer.Sound('art/death.wav')
            if sound:
                death.play()
        if dest_unit.game_id == 'HQ':
            game_over = True
        else:
            if dest_unit.game_id == 'Quarters':
                unit_limit[dest_unit.team] -= 5
            if dest_unit.multi_cell:
                for coord in dest_unit.xy:
                    dest_x, dest_y = coord
                    grid[dest_y][dest_x] = None
            else:
                dest_x, dest_y = dest_unit.xy
                grid[dest_y][dest_x] = None
            item_list.remove(dest_unit)
    if unit.game_id == 'Soldier':
        unit.turn_attacks += 1
        if unit.turn_attacks > 1:
            unit.has_attacked = True
            unit.special_used = True
    else:
        unit.has_attacked = True
        if unit.game_id == 'Spy':
            unit.special_used = True
    if start[0] > dest[0] and not unit.flipped or start[0] < dest[0] and unit.flipped:
        unit.flip_unit()
    if unit.game_id == 'Scout' or unit.game_id == 'Sniper' and not unit.special_used:
        unit.special_condition = False


def check_build_direction(start, d, length):
    coords = []
    if d == 'r':
        for space in range(length):
            coord_x = start[0] + space
            if grid_width >= coord_x >= 0 and grid[start[1]][coord_x] is None:
                coords.append((coord_x, start[1]))
            else:
                return False, None
    elif d == 'l':
        for space in range(length):
            coord_x = start[0] - space
            if grid_width >= coord_x >= 0 and grid[start[1]][coord_x] is None:
                coords.append((coord_x, start[1]))
            else:
                return False, None
    elif d == 'u':
        for space in range(length):
            coord_y = start[1] + space
            if grid_height >= coord_y >= 0 and grid[coord_y][start[0]] is None:
                coords.append((start[0], coord_y))
            else:
                return False, None
    else:
        for space in range(length):
            coord_y = start[1] - space
            if grid_height >= coord_y >= 0 and grid[coord_y][start[0]] is None:
                coords.append((start[0], coord_y))
            else:
                return False, None
    return True, coords


def evaluate_build_space(start, dest, unit, build_type, dimensions):
    x, y = dimensions[0] - 1, dimensions[1] - 1
    building_coords = [dest]
    approved = False
    if grid[dest[1]][dest[0]] is None and abs(start[0] - dest[0]) + abs(start[1] - dest[1]) == 1:
        if start[1] == dest[1]:
            if start[0] < dest[0]:
                approved, new_coords = check_build_direction((dest[0] + 1, dest[1]), 'l', x)
                if unit.flipped:
                    unit.flip_unit()
            else:
                approved, new_coords = check_build_direction((dest[0] - 1, dest[1]), 'r', x)
                if not unit.flipped:
                    unit.flip_unit()
            if approved:
                building_coords.extend(new_coords)
                building_coords.sort()
                new_coords.clear()
                approved = False
                new_x, new_y = building_coords[0]
                for col in range(x + 1):
                    approved, new_coords = check_build_direction((new_x + col, new_y + 1), 'u', y)
                    if approved:
                        building_coords.extend(new_coords)
                    else:
                        break
                if not approved:
                    for col in range(x + 1):
                        approved, new_coords = check_build_direction((new_x + col, new_y - 1), 'd', y)
                        if approved:
                            building_coords.extend(new_coords)
                        else:
                            break
        else:
            if start[1] < dest[1]:
                approved, new_coords = check_build_direction((dest[0], dest[1] + 1), 'u', y)
            else:
                approved, new_coords = check_build_direction((dest[0], dest[1] - 1), 'd', y)
            if approved:
                building_coords.extend(new_coords)
                building_coords.sort()
                new_coords.clear()
                approved = False
                new_x, new_y = building_coords[0]
                for row in range(y + 1):
                    approved, new_coords = check_build_direction((new_x + 1, new_y + row), 'r', x)
                    if approved:
                        building_coords.extend(new_coords)
                    else:
                        break
                if not approved:
                    for row in range(y + 1):
                        approved, new_coords = check_build_direction((new_x - 1, new_y + row), 'l', x)
                        if approved:
                            building_coords.extend(new_coords)
                        else:
                            break
    if approved:
        building_coords.sort()
        build_x, build_y = building_coords[0]
        new_building(build_x, build_y, unit.team, 'Construction', con=build_type)
        unit.special_used = True
        unit.steps_remaining = 0
        unit.building_timer = item_list[-1].construct_timer


def update_unit_status():
    unit_count = [item for item in item_list if not item.static and item.team == turn_map.get(turn)]
    active_units = [unit for unit in unit_count if 0 in unit.activities]
    cycle = itertools.cycle(active_units)
    return unit_count, active_units, cycle


def spawn_unit(unit, building):
    x, y = building.xy[0]
    if building.team == 'Blue':
        door_side = building.h
    else:
        door_side = -1
    spawned = False
    for space in range(building.w):
        if grid[y + door_side][x + space] is None and not spawned:
            new_unit(x + space, y + door_side, building.team, unit)
            spawned = True
    if spawned:
        building.queue = None
    else:
        building.queue_timer = 1


def detect_proximity(range, building):
    ox, oy = building.xy[0]
    end_h = building.h
    if oy - range < 0:
        start_index = 0
    else:
        start_index = oy - range
    if oy + building.range + end_h > grid_height:
        end_index = grid_height
    else:
        end_index = oy + range + end_h
    for y, row in enumerate(grid[start_index:end_index], start_index):
        for x, item in enumerate(row):
            for coord in building.xy:
                ox, oy = coord
                xy = x, y
                if abs(ox - x) + abs(oy - y) <= range and grid[y][x] is not None and grid[y][x].team is \
                        not None:
                    target = grid[y][x]
                    if building.game_id == 'Tower' and target.team != building.team:
                        target.current_hp -= building.damage
                    if building.game_id == 'Med Bay' and not target.static and target.team == building.team:
                        if target.current_hp + building.healing >= target.hp:
                            target.current_hp = target.hp
                        else:
                            target.current_hp += building.healing


def find_tp_targets():
    x, y = selected_cell
    tp_targets = []
    if grid[y][x - 1] is not None and not grid[y][x - 1].static:
        tp_targets = [grid[y][x - 1]]
    if grid[y][x + 1] is not None and not grid[y][x + 1].static:
        tp_targets.append(grid[y][x + 1])
    if grid[y - 1][x] is not None and not grid[y - 1][x].static:
        tp_targets.append(grid[y - 1][x])
    if grid[y + 1][x] is not None and not grid[y + 1][x].static:
        tp_targets.append(grid[y + 1][x])
    return tp_targets


def power_spawn():
    if round_counter % 5 == 0:
        if grid[15][2] is None:
            doc_one = PowerUp((2, 15), 'Secret Document')
            doc_one.scale_image(c)
            grid[15][2] = doc_one
            item_list.append(doc_one)
        elif not grid[15][2].static:
            grid[15][2].carrying = True
        if grid[21][9] is None:
            doc_two = PowerUp((9, 21), 'Secret Document')
            doc_two.scale_image(c)
            grid[21][9] = doc_two
            item_list.append(doc_two)
        elif not grid[21][9].static:
            grid[21][9].carrying = True
    start_x = 1
    end_x = 10
    berry_proc = random.randint(0, 4)
    if berry_proc == 0:
        start_y = 10
        end_y = 25
        x, y = random.randint(start_x, end_x), random.randint(start_y, end_y)
        search_max = (end_x - start_x + 1) * (end_y - start_y + 1)
        while grid[y][x] is not None:
            x, y = random.randint(start_x, end_x), random.randint(start_y, end_y)
            search_max -= 1
            if search_max == 0:
                break
        berry = PowerUp((x, y), 'Wild Berries')
        berry.scale_image(c)
        grid[y][x] = berry
        item_list.append(berry)
    crystal_proc = random.randint(0, 14)
    if crystal_proc == 0 and round_counter >= 10:
        start_y = 13
        end_y = 22
        x, y = random.randint(start_x, end_x), random.randint(start_y, end_y)
        search_max = (end_x - start_x + 1) * (end_y - start_y + 1)
        while grid[y][x] is not None:
            x, y = random.randint(start_x, end_x), random.randint(start_y, end_y)
            search_max -= 1
            if search_max == 0:
                break
        crystal = PowerUp((x, y), 'Alchemist Crystal')
        crystal.scale_image(c)
        grid[y][x] = crystal
        item_list.append(crystal)


def next_turn():
    global turn, round_counter, selected_cell, selected_unit, grid_scroll
    tone = pg.mixer.Sound('art/tone.wav')
    if sound:
        tone.play()
    turn = abs(turn - 1)
    if turn:
        grid_scroll = grid_height - grid_width
    else:
        for item in item_list:
            item.refresh()
            if item.static and item.team in turn_map.values():
                if item.queue is not None and item.production():
                    spawn_unit(item.queue, item)
                elif item.game_id == 'Construction' and item.construct_finished():
                    if item.con_type == 'Quarters':
                        unit_limit[item.team] += 5
                    if item.con_type == 'Teleporter':
                        build_x, build_y = item.xy
                    else:
                        build_x, build_y = item.xy[0]
                    new_building(build_x, build_y, item.team, item.con_type)
                    item_list.remove(item)
                elif item.range is not None and item.game_id != 'Teleporter':
                    detect_proximity(item.range, item)
        grid_scroll = 0
        round_counter += 1
        power_spawn()
    selected_cell = None
    selected_unit = None


def starting_units():
    new_building(4, 1, 'Blue', 'HQ')
    new_building(4, 31, 'Red', 'HQ')
    new_unit(5, 5, 'Blue', 'Engineer')
    new_unit(6, 30, 'Red', 'Engineer')
    item_list[-1].flip_unit()
    new_terrain(3, 5, 'Boulder')
    new_terrain(2, 6, 'Boulder')
    new_terrain(8, 5, 'Boulder')
    new_terrain(9, 6, 'Boulder')
    new_terrain(3, 30, 'Boulder')
    new_terrain(2, 29, 'Boulder')
    new_terrain(8, 30, 'Boulder')
    new_terrain(9, 29, 'Boulder')
    new_building(0, 14, None, 'Secret Lab')
    new_terrain(0, 13, 'Boulder')
    new_terrain(1, 13, 'Boulder')
    new_terrain(0, 16, 'Boulder')
    new_terrain(1, 16, 'Boulder')
    new_building(10, 20, None, 'Secret Lab')
    new_terrain(10, 19, 'Boulder')
    new_terrain(11, 19, 'Boulder')
    new_terrain(10, 22, 'Boulder')
    new_terrain(11, 22, 'Boulder')
    new_terrain(1, 1, 'Collection Post')
    new_terrain(10, 1, 'Collection Post')
    new_terrain(1, 34, 'Collection Post')
    new_terrain(10, 34, 'Collection Post')


def game_over_text(winning_team):
    global reset
    if sound or music:
        victory = pg.mixer.Sound('art/fanfare.wav')
        victory.play()
    pg.draw.rect(screen, art.WHITE, (int(w / 4), int(h / 4), int(w / 2), int(h / 2)))
    art.draw_game_over_border(screen, int(w / 4), int(h / 4), int(w / 2), int(h / 2))
    if winning_team == 'Blue':
        draw_text = art.render_text('Blue wins!', 'rockwell', 128, art.BLUE)
    else:
        draw_text = art.render_text('Red wins!', 'rockwell', 128, art.BLUE)
    screen.blit(draw_text, (int(w / 2) - int(draw_text.get_width() / 2), int(h / 3) - int(draw_text.get_height() / 2)))
    draw_text = art.render_text('Click back to exit to the main menu.', 'rockwell', 52, art.BLACK)
    screen.blit(draw_text, (int(w / 2) - int(draw_text.get_width() / 2), int(h / 2) + int(h / 8)))
    reset = True


def draw_tutorial_graphics(progress, grid_w, grid):
    RedArrow = pg.transform.scale(art.RedArrowIMG, (c, c))
    if progress == 0:
        draw_text = art.render_text('Welcome to Infiltrate!', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Left click the engineer to begin.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        grid.blit(RedArrow, (c * 5, c * (4 - grid_scroll)))
    if progress == 1:
        draw_text = art.render_text('Click the move button to view movable squares.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        screen.blit(RedArrow, (grid_w + 180, 30))
    if progress == 2:
        draw_text = art.render_text('Now right click any green square to move there.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
    if progress == 3:
        draw_text = art.render_text('Engineers can build things.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('This is their "special move".', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text('Click special move to initiate the process.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        draw_text = art.render_text('Or you can also press the space bar.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 680))
        screen.blit(RedArrow, (grid_w + 180, 170))
    if progress > 3 and progress < 7:
        pg.draw.rect(screen, art.WHITE, (grid_w + 160, 550, 400, 150))
    if progress == 4:
        draw_text = art.render_text('Click "down" to select a different building.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('This first building creates soldiers and scouts.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        screen.blit(RedArrow, (grid_w + 720, 790))
    if progress == 5:
        draw_text = art.render_text('This building increases the max number of units.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Click the image to select it for building.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        screen.blit(RedArrow, (grid_w + 760, 650))
    if progress == 6:
        draw_text = art.render_text('Left click a cell to build in.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Note that there must be room for the size.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text('And that the engineer will be busy', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        draw_text = art.render_text('for the', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 650))
        draw_text = art.render_text('duration.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 680))
    if progress == 7:
        draw_text = art.render_text('The build time for this building is 3 turns.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('To end your turn, click "End Turn".', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        screen.blit(RedArrow, (grid_w + 180, 320))
    if progress == 8:
        draw_text = art.render_text('You are now acting as the red player.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Click the "Next Unit" button to cycle to the next', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text('available unit.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        screen.blit(RedArrow, (grid_w + 180, 235))
    if progress == 9:
        draw_text = art.render_text("The soldier's special move is to attack twice.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Every other unit can only attack once per turn.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text('Click the attack button to see targets in range.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        screen.blit(RedArrow, (grid_w + 180, 100))
    if progress == 10:
        draw_text = art.render_text("Right click the blue unit to attack it.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
    if progress == 11:
        draw_text = art.render_text("You damaged the unit. Left click it to assess the", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('damage.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        grid.blit(RedArrow, (c * 3, c * (26 - grid_scroll)))
    if progress == 12 or progress == 13:
        draw_text = art.render_text("Now reselect the soldier and fire again.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('This time, just right click the enemy unit without', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text('clicking the attack button.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
    if progress == 14:
        draw_text = art.render_text("Now that you attacked twice, he can't attack again", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('this turn.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text('Next, click the red scout.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        grid.blit(RedArrow, (c * 8, c * (27 - grid_scroll)))
    if progress == 15:
        draw_text = art.render_text("The scout is wounded. Luckily, we can move to", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('the "wild berries" powerup to recover health.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        grid.blit(RedArrow, (c * 8, c * (19 - grid_scroll)))
        if grid_scroll > 20:
            draw_text = art.render_text('Scroll up to see the berries.', 'hpsimplified', 48, art.BLACK)
            screen.blit(draw_text, (grid_w + 160, 620))
    if progress == 16:
        draw_text = art.render_text("He's back to full health, but has used all his", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('movement. Luckily, his special move is to restore', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text("all movement as long as he doesn't attack in the", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        draw_text = art.render_text("same round.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 680))
        screen.blit(RedArrow, (grid_w + 180, 170))
    if progress == 17 or progress == 18:
        draw_text = art.render_text("Now we can move again this round.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Move anywhere, then click "End Turn".', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
    if progress == 18:
        screen.blit(RedArrow, (grid_w + 180, 320))
    if progress == 19:
        draw_text = art.render_text("This is the starting position of a game.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Click on the blue HQ to continue.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        grid.blit(RedArrow, (c * 6, c * (1 - grid_scroll)))
    if progress == 20:
        draw_text = art.render_text("Some buildings produce units.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Click the engineer icon to produce one.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text("To produce military units, you can build either an", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        draw_text = art.render_text("Academy for basic or Institute for special units.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 680))
        screen.blit(RedArrow, (grid_w + 180, 30))
    if progress == 21:
        draw_text = art.render_text("An engineer has been added to the queue, and", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('will spawn next turn.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text("Scroll down to continue.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
    if progress == 22:
        draw_text = art.render_text("There are two ways to win a game:", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('destroy the enemy HQ, or collect 20', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text("Secret Documents. Click one to continue.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        grid.blit(RedArrow, (c * 2, c * (14 - grid_scroll)))
        grid.blit(RedArrow, (c * 9, c * (20 - grid_scroll)))
    if progress == 23:
        draw_text = art.render_text("Secret Documents spawn here every 5 rounds.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text('Your job is to collect them, and for every fourth', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text("that you collect, you will unlock a new structure", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        draw_text = art.render_text('that you can build. To collect one, a unit must', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 680))
        draw_text = art.render_text('return them to one of the "Collection Posts".', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 740))
        draw_text = art.render_text('Scroll back up to your base to locate them.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 800))
    if progress == 24:
        draw_text = art.render_text("When your unit is within one square of the posts,", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 500))
        draw_text = art.render_text("the document is added to your tally.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 560))
        draw_text = art.render_text("... which should be all you need to know for now.", 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 620))
        draw_text = art.render_text('Click "Back" to return to the menu.', 'hpsimplified', 48, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 680))
        draw_text = art.render_text("Good luck!", 'hpsimplified', 64, art.BLACK)
        screen.blit(draw_text, (grid_w + 160, 760))
        grid.blit(RedArrow, (c, c * (0 - grid_scroll)))
        grid.blit(RedArrow, (c * 10, c * (0 - grid_scroll)))


def tutorial():
    global w, h, c, screen, selected_cell, selected_unit, grid_scroll, click_graphic, game_over, grid
    # grid w/h = pixel space, width/height = column/row number
    grid_h = h - 70
    grid_w = grid_h
    grid_space = pg.Surface((grid_w + 6, grid_h + 6))
    disp_w, disp_h = 300, 300
    display_window = pg.Surface((disp_w, disp_h))
    c = round(grid_w / grid_width)
    # buttons/scoller
    scroller = Scroller(art.GREEN, grid_w + 80, grid_h + adj_y, adj_y, 20, 15, max_val=grid_height - grid_width)
    back_button = Button(art.GREY, (w - 120), 20, 100, 50, 'Back', 40, 'rockwell')
    move_button = Button(art.GREY, grid_w + 145, 100, 150, 50, 'Move', 30, 'rockwell')
    attack_button = Button(art.GREY, grid_w + 145, 170, 150, 50, 'Attack', 30, 'rockwell')
    special_button = Button(art.GREY, grid_w + 145, 240, 150, 50, 'Special Move', 20, 'rockwell')
    build_button_1 = Button(art.GREY, grid_w + 165, 100, 75, 75, '', 30, 'rockwell')
    build_button_2 = Button(art.GREY, grid_w + 165, 200, 75, 75, '', 20, 'rockwell')
    tp_button_1 = Button(art.GREY, grid_w + 130, 100, 75, 75, '', 20, 'rockwell')
    tp_button_2 = Button(art.GREY, grid_w + 235, 100, 75, 75, '', 20, 'rockwell')
    tp_button_3 = Button(art.GREY, grid_w + 130, 200, 75, 75, '', 20, 'rockwell')
    tp_button_4 = Button(art.GREY, grid_w + 235, 200, 75, 75, '', 20, 'rockwell')
    tp_request = None
    next_button = Button(art.GREY, grid_w + 145, 310, 150, 50, 'Next Unit', 30, 'rockwell')
    turn_button = Button(art.GREY, grid_w + 145, 380, 150, 50, 'End Turn', 30, 'rockwell')
    # engineer build menu/utility kit
    build_select = Button(art.WHITE, (grid_w + 650), 670, 200, 200, '', 40, 'rockwell')
    build_up = Button(art.WHITE, (grid_w + 725), 635, 50, 25, shape='tri', sub_shape='up')
    build_down = Button(art.WHITE, (grid_w + 725), 880, 50, 25, shape='tri', sub_shape='down')
    build_lib = {0: 'Academy', 1: 'Quarters', 2: 'Tower', 3: 'Institute', 4: 'Med Bay', 5: 'Teleporter'}
    dimension_lib = {'Academy': (2, 2), 'Quarters': (2, 2), 'Tower': (2, 4), 'Institute': (2, 2), 'Med Bay': (3, 3),
                     'Teleporter': (1, 1)}
    cancel_build_button = Button(art.WHITE, (grid_w + 805), 485, 150, 50, 'cancel', 30, 'rockwell')
    build_scroll = 0
    build_request = None
    unit_count, active_units, cycle = update_unit_status()
    scrolling = False
    display_img = False
    game_reset()
    new_unit(5, 5, 'Blue', 'Engineer')
    tutorial_progress = 0
    while game_state == 4:
        screen.fill(art.DARK_GREY)
        grid_space.fill(art.LIGHT_GREEN)
        display_window.fill(art.WHITE)
        art.display_border(display_window, disp_w, disp_h)
        draw_grid_lines(grid_space, grid_w, grid_h)
        draw_graphics(grid_space, grid_w)
        draw_game_text(grid_w)
        scroller.draw(screen)
        back_button.draw(screen, art.BLACK)
        next_button.draw(screen, art.BLACK)
        turn_button.draw(screen, art.BLACK)
        if tutorial_progress > 3 and tutorial_progress < 7:
            build_select.draw(screen, art.BLACK)
            build_up.draw(screen, art.BLACK)
            build_down.draw(screen, art.BLACK)
        if scrolling:
            grid_scroll = scroller.scroll(event.pos[1])
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 1
                if event.key == pg.K_s:
                    if grid_scroll < grid_height - grid_width:
                        grid_scroll += 1
                        scroller.update_y(grid_scroll)
                if event.key == pg.K_w:
                    if grid_scroll > 0:
                        grid_scroll -= 1
                        scroller.update_y(grid_scroll)
                if event.key == pg.K_SPACE and tutorial_progress == 3 or tutorial_progress == 16:
                    selected_unit.use_special()
                    tutorial_progress += 1
                    make_click()
            if event.type == pg.MOUSEBUTTONDOWN:
                if grid_space.get_rect(x=(adj_x), y=(adj_y)).collidepoint(event.pos):
                    if event.button == 4:
                        if grid_scroll > 0:
                            grid_scroll -= 1
                            scroller.update_y(grid_scroll)
                    if event.button == 5:
                        if grid_scroll < grid_height - grid_width:
                            grid_scroll += 1
                            scroller.update_y(grid_scroll)
                    dest_cell = find_grid_coords(event.pos[0], event.pos[1], grid_w)
                    if tutorial_progress == 0 and event.button == 1 and dest_cell == (5, 5):
                        tutorial_progress += 1
                        selected_cell = (5, 5)
                        selected_unit = item_list[-1]
                        make_click()
                        display_img = True
                    if tutorial_progress == 2 or tutorial_progress == 17 and event.button == 3 and \
                            valid_move(selected_unit, selected_unit.xy, dest_cell, None):
                        tutorial_progress += 1
                        move_unit(selected_unit, selected_unit.xy, dest_cell, None)
                        selected_cell = dest_cell
                        make_click()
                        click_graphic = 0
                    if tutorial_progress == 6 and event.button == 1:
                        evaluate_build_space(selected_unit.xy, dest_cell, selected_unit, build_request, (2, 2))
                        if item_list[-1].game_id == 'Construction':
                            selected_unit = item_list[-1]
                            build_request = None
                            click_graphic = 0
                            tutorial_progress += 1
                    if tutorial_progress == 10 or tutorial_progress == 13 and event.button == 3 and \
                            dest_cell == (3, 27):
                        attack_unit(selected_unit, selected_unit.xy, dest_cell, item_list[-1])
                        click_graphic = 0
                        make_click()
                        tutorial_progress += 1
                    if tutorial_progress == 11 and event.button == 1 and dest_cell == (3, 27):
                        selected_cell = dest_cell
                        selected_unit = item_list[-1]
                        make_click()
                        tutorial_progress += 1
                    if tutorial_progress == 12 and event.button == 1 and dest_cell == (5, 30):
                        selected_unit = item_list[-3]
                        selected_cell = dest_cell
                        make_click()
                        tutorial_progress += 1
                    if tutorial_progress == 14 and event.button == 1 and dest_cell == (8, 28):
                        berry = PowerUp((8, 20), 'Wild Berries')
                        berry.scale_image(c)
                        grid[20][8] = berry
                        item_list.append(berry)
                        item_list[-3].current_hp -= 15
                        selected_unit = item_list[-3]
                        selected_cell = dest_cell
                        make_click()
                        tutorial_progress += 1
                    if tutorial_progress == 15 and event.button == 3 and dest_cell == (8, 20):
                        move_unit(item_list[-3], item_list[-3].xy, (8, 20), item_list[-1])
                        selected_cell = (8, 20)
                        make_click()
                        tutorial_progress += 1
                    if tutorial_progress == 19 and event.button == 1 and dest_cell[0] >= 4 and dest_cell[0] <= 7 and \
                            dest_cell[1] >= 1 and dest_cell[1] <= 4:
                        make_click()
                        selected_cell = (4, 1)
                        selected_unit = item_list[0]
                        display_img = True
                        tutorial_progress += 1
                    if tutorial_progress == 22 and event.button == 1 and dest_cell == (2, 15) or dest_cell == (9, 21):
                        make_click()
                        selected_cell = dest_cell
                        selected_unit = item_list[-1]
                        tutorial_progress += 1
                else:
                    if scroller.is_over(event.pos):
                        scrolling = True
                    else:
                        if back_button.is_over(event.pos):
                            return 1
                        if tutorial_progress == 1 and move_button.is_over(event.pos):
                            graphic_squares.clear()
                            make_click()
                            click_graphic = 1
                            tutorial_progress += 1
                        if tutorial_progress == 3 or tutorial_progress == 16 and special_button.is_over(event.pos):
                            selected_unit.use_special()
                            tutorial_progress += 1
                            make_click()
                        if tutorial_progress == 4 and build_down.is_over(event.pos):
                            build_scroll += 1
                            tutorial_progress += 1
                            make_click()
                        if tutorial_progress == 5 and build_select.is_over(event.pos):
                            build_request = 'Academy'
                            tutorial_progress += 1
                            make_click()
                        if tutorial_progress == 7 or tutorial_progress == 18 and turn_button.is_over(event.pos):
                            make_click()
                            if tutorial_progress == 7:
                                new_unit(5, 30, 'Red', 'Soldier')
                                new_unit(8, 28, 'Red', 'Scout')
                                new_unit(3, 27, 'Blue', 'Engineer')
                            else:
                                grid = [[None for x in range(grid_width)] for x in range(grid_height)]
                                item_list.clear()
                                starting_units()
                            tutorial_progress += 1
                            next_turn()
                            scroller.update_y(grid_scroll)
                        if tutorial_progress == 8 and next_button.is_over(event.pos):
                            tutorial_progress += 1
                            selected_cell = (5, 30)
                            selected_unit = item_list[-3]
                            display_img = True
                            make_click()
                        if tutorial_progress == 9 and attack_button.is_over(event.pos):
                            tutorial_progress += 1
                            graphic_squares.clear()
                            click_graphic = 2
                            make_click()
                        if tutorial_progress == 20 and build_button_1.is_over(event.pos):
                            make_click()
                            tutorial_progress += 1
                            selected_unit.queue = 'Engineer'
            if event.type == pg.MOUSEBUTTONUP:
                scrolling = False
            if event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
                w, h = event.w, event.h
            if event.type == pg.QUIT:
                return 0
        if tutorial_progress == 21 and grid_scroll >= 12:
            doc_one = PowerUp((2, 15), 'Secret Document')
            doc_one.scale_image(c)
            grid[15][2] = doc_one
            item_list.append(doc_one)
            doc_two = PowerUp((9, 21), 'Secret Document')
            doc_two.scale_image(c)
            grid[21][9] = doc_two
            item_list.append(doc_two)
            tutorial_progress += 1
        if tutorial_progress == 23 and grid_scroll == 0:
            tutorial_progress += 1
        if display_img:
            if selected_unit is None:
                display_img = False
            else:
                display_window.blit(art.return_icon(selected_unit.image), (round(disp_w / 6), round(disp_h / 6)))
                if selected_unit.team is not None:
                    art.draw_health_bar(display_window, disp_w, disp_h, selected_unit.current_hp, selected_unit.hp)
                if selected_unit.game_id == 'Engineer' and selected_unit.build_menu:
                    screen.blit(
                        art.return_icon(art.image_lib.get(f'{selected_unit.team}{build_lib.get(build_scroll)}')), \
                        ((grid_w + 650), 670))
                    draw_build_menu_text(grid_w, build_lib.get(build_scroll), \
                                         dimension_lib.get(build_lib.get(build_scroll)))
                    if build_request is not None:
                        graphic_squares.clear()
                        click_graphic = 3
                if selected_unit.team == turn_map.get(turn):
                    draw_display_stats(grid_w, selected_unit)
                    if selected_unit.static:
                        if selected_unit.produce is not None and type(selected_unit.produce) == tuple:
                            if selected_unit.queue is None and len(unit_count) < unit_limit.get(turn_map.get(turn)):
                                build_button_1.draw(screen, art.GREEN)
                                build_button_2.draw(screen, art.GREEN)
                            else:
                                build_button_1.draw(screen, art.RED)
                                build_button_2.draw(screen, art.RED)
                            screen.blit(selected_unit.button_1(), (grid_w + 165, 100))
                            screen.blit(selected_unit.button_2(), (grid_w + 165, 200))
                        elif selected_unit.produce is not None:
                            if selected_unit.queue is None and len(unit_count) < unit_limit.get(turn_map.get(turn)):
                                build_button_1.draw(screen, art.GREEN)
                            else:
                                build_button_1.draw(screen, art.RED)
                            screen.blit(selected_unit.button_1(), (grid_w + 165, 100))
                        elif selected_unit.game_id == 'Teleporter':
                            tp_options = find_tp_targets()
                            for num, option in enumerate(tp_options, 1):
                                current_button = locals()[f'tp_button_{num}']
                                current_button.draw(screen, art.GREEN)
                                screen.blit(art.return_button(option.image), (current_button.x, current_button.y))
                    else:
                        if selected_unit.steps_remaining == selected_unit.speed:
                            move_button.draw(screen, art.GREEN)
                        elif selected_unit.steps_remaining > 0:
                            move_button.draw(screen, art.BLACK)
                        else:
                            selected_unit.activities[0] = 1
                            move_button.draw(screen, art.RED)
                        if selected_unit.has_attacked or not selected_unit.can_attack:
                            selected_unit.activities[1] = 1
                            attack_button.draw(screen, art.RED)
                        else:
                            attack_button.draw(screen, art.GREEN)
                        if selected_unit.special_used or not selected_unit.special_condition:
                            selected_unit.activities[2] = 1
                            special_button.draw(screen, art.RED)
                        else:
                            special_button.draw(screen, art.GREEN)
                        if not 0 in selected_unit.activities:
                            unit_count, active_units, cycle = update_unit_status()
        draw_tutorial_graphics(tutorial_progress, grid_w, grid_space)
        screen.blit(grid_space, (adj_x, adj_y))
        screen.blit(display_window, (grid_w + 350, 100))

        pg.display.update()
        clock.tick(60)


def game():
    global w, h, c, screen, selected_cell, selected_unit, grid_scroll, click_graphic, game_over
    # grid w/h = pixel space, width/height = column/row number
    grid_h = h - 70
    grid_w = grid_h
    grid_space = pg.Surface((grid_w + 6, grid_h + 6))
    disp_w, disp_h = 300, 300
    display_window = pg.Surface((disp_w, disp_h))
    c = round(grid_w / grid_width)
    # buttons/scoller
    scroller = Scroller(art.GREEN, grid_w + 80, grid_h + adj_y, adj_y, 20, 15, max_val=grid_height - grid_width)
    back_button = Button(art.GREY, (w - 120), 20, 100, 50, 'Back', 40, 'rockwell')
    move_button = Button(art.GREY, grid_w + 145, 100, 150, 50, 'Move', 30, 'rockwell')
    attack_button = Button(art.GREY, grid_w + 145, 170, 150, 50, 'Attack', 30, 'rockwell')
    special_button = Button(art.GREY, grid_w + 145, 240, 150, 50, 'Special Move', 20, 'rockwell')
    build_button_1 = Button(art.GREY, grid_w + 165, 100, 75, 75, '', 30, 'rockwell')
    build_button_2 = Button(art.GREY, grid_w + 165, 200, 75, 75, '', 20, 'rockwell')
    tp_button_1 = Button(art.GREY, grid_w + 130, 100, 75, 75, '', 20, 'rockwell')
    tp_button_2 = Button(art.GREY, grid_w + 235, 100, 75, 75, '', 20, 'rockwell')
    tp_button_3 = Button(art.GREY, grid_w + 130, 200, 75, 75, '', 20, 'rockwell')
    tp_button_4 = Button(art.GREY, grid_w + 235, 200, 75, 75, '', 20, 'rockwell')
    tp_request = None
    next_button = Button(art.GREY, grid_w + 145, 310, 150, 50, 'Next Unit', 30, 'rockwell')
    turn_button = Button(art.GREY, grid_w + 145, 380, 150, 50, 'End Turn', 30, 'rockwell')
    # engineer build menu/utility kit
    build_select = Button(art.WHITE, (grid_w + 650), 670, 200, 200, '', 40, 'rockwell')
    build_up = Button(art.WHITE, (grid_w + 725), 635, 50, 25, shape='tri', sub_shape='up')
    build_down = Button(art.WHITE, (grid_w + 725), 880, 50, 25, shape='tri', sub_shape='down')
    cancel_build_button = Button(art.WHITE, (grid_w + 805), 485, 150, 50, 'cancel', 30, 'rockwell')
    build_scroll = 0
    build_lib = {0: 'Academy', 1: 'Quarters', 2: 'Tower', 3: 'Institute', 4: 'Med Bay', 5: 'Teleporter'}
    dimension_lib = {'Academy': (2, 2), 'Quarters': (2, 2), 'Tower': (2, 4), 'Institute': (2, 2), 'Med Bay': (3, 3),
                     'Teleporter': (1, 1)}
    build_request = None
    if reset:
        game_reset()
    unit_count, active_units, cycle = update_unit_status()
    scrolling = False
    display_img = False
    while game_state == 3:
        screen.fill(art.DARK_GREY)
        grid_space.fill(art.LIGHT_GREEN)
        display_window.fill(art.WHITE)
        art.display_border(display_window, disp_w, disp_h)
        draw_grid_lines(grid_space, grid_w, grid_h)
        draw_graphics(grid_space, grid_w)
        draw_game_text(grid_w)
        scroller.draw(screen)
        back_button.draw(screen, art.BLACK)
        next_button.draw(screen, art.BLACK)
        turn_button.draw(screen, art.BLACK)
        if scrolling:
            grid_scroll = scroller.scroll(event.pos[1])
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 1
                if not game_over:
                    if event.key == pg.K_s:
                        if grid_scroll < grid_height - grid_width:
                            grid_scroll += 1
                            scroller.update_y(grid_scroll)
                        # print(grid_scroll)
                    if event.key == pg.K_w:
                        if grid_scroll > 0:
                            grid_scroll -= 1
                            scroller.update_y(grid_scroll)
                        # print(grid_scroll)
                    if event.key == pg.K_SPACE:
                        if selected_unit is not None and not selected_unit.static and selected_unit.team == \
                                turn_map.get(turn) and selected_unit.manual_special:
                            selected_unit.use_special()
            if event.type == pg.MOUSEBUTTONDOWN:
                if grid_space.get_rect(x=(adj_x), y=(adj_y)).collidepoint(event.pos) and not game_over:
                    if event.button == 3:
                        click_graphic = 0
                        if selected_unit is not None and not selected_unit.static and selected_unit.team == \
                                turn_map.get(turn):
                            # dest = destination (cell/unit)
                            dest_cell = find_grid_coords(event.pos[0], event.pos[1], grid_w)
                            dest_unit = grid[dest_cell[1]][dest_cell[0]]
                            if valid_move(selected_unit, selected_cell, dest_cell, dest_unit):
                                move_unit(selected_unit, selected_cell, dest_cell, dest_unit)
                                selected_cell = dest_cell
                                make_click()
                            if valid_attack(selected_unit, selected_cell, dest_cell, dest_unit):
                                attack_unit(selected_unit, selected_cell, dest_cell, dest_unit)
                            # print(dest_cell)
                    elif event.button == 4:
                        if grid_scroll > 0:
                            grid_scroll -= 1
                            scroller.update_y(grid_scroll)
                        # print(grid_scroll)
                    elif event.button == 5:
                        if grid_scroll < grid_height - grid_width:
                            grid_scroll += 1
                            scroller.update_y(grid_scroll)
                        # print(grid_scroll)
                    else:
                        selected_cell = find_grid_coords(event.pos[0], event.pos[1], grid_w)
                        click_graphic = 0
                        if build_request is not None:
                            build_cell = find_grid_coords(event.pos[0], event.pos[1], grid_w)
                            evaluate_build_space(selected_unit.xy, build_cell, selected_unit, build_request, \
                                                 dimension_lib.get(build_request))
                            build_scroll = 0
                            selected_unit.build_menu = False
                            build_request = None
                        elif tp_request is not None:
                            request_dest = find_grid_coords(event.pos[0], event.pos[1], grid_w)
                            if grid[request_dest[1]][request_dest[0]] is None:
                                save_steps = tp_request.steps_remaining
                                move_unit(tp_request, tp_request.xy, request_dest, None)
                                tp_request.steps_remaining = save_steps
                                if sound:
                                    tp_sound = pg.mixer.Sound('art/teleport.wav')
                                    tp_sound.play()
                            tp_request = None
                        # print(selected_cell)
                        selected_unit = grid[selected_cell[1]][selected_cell[0]]
                        # print(selected_unit)
                        if selected_unit is None:
                            display_img = False
                        else:
                            display_img = True
                            if selected_unit.static and selected_unit.range is not None:
                                graphic_squares.clear()
                                click_graphic = 3
                        make_click()
                else:
                    if scroller.is_over(event.pos) and not game_over:
                        scrolling = True
                    else:
                        click_graphic = 0
                        if not game_over:
                            if move_button.is_over(event.pos):
                                graphic_squares.clear()
                                if selected_unit is not None and not selected_unit.static and selected_unit.team == \
                                        turn_map.get(turn):
                                    make_click()
                                    click_graphic = 1
                            if build_button_1.is_over(event.pos):
                                if selected_unit is not None and selected_unit.static and selected_unit.team == \
                                        turn_map.get(turn) and selected_unit.produce:
                                    if selected_unit.queue is None and len(unit_count) < unit_limit.get(
                                            turn_map.get(turn)):
                                        make_click()
                                        if type(selected_unit.produce) == tuple:
                                            selected_unit.queue = selected_unit.produce[0]
                                        else:
                                            selected_unit.queue = selected_unit.produce
                            if build_button_2.is_over(event.pos):
                                if selected_unit is not None and selected_unit.static and selected_unit.team == \
                                        turn_map.get(turn) and selected_unit.produce:
                                    if selected_unit.queue is None and type(selected_unit.produce) == tuple and \
                                            len(unit_count) < unit_limit.get(turn_map.get(turn)):
                                        make_click()
                                        selected_unit.queue = selected_unit.produce[1]
                            if attack_button.is_over(event.pos):
                                graphic_squares.clear()
                                if selected_unit is not None and not selected_unit.static and selected_unit.team == \
                                        turn_map.get(turn):
                                    make_click()
                                    click_graphic = 2
                            if special_button.is_over(event.pos):
                                if selected_unit is not None and not selected_unit.static and selected_unit.team == \
                                        turn_map.get(turn) and selected_unit.manual_special:
                                    make_click()
                                    selected_unit.use_special()
                            if next_button.is_over(event.pos):
                                if len(active_units) > 0:
                                    make_click()
                                    test_cycle = selected_unit
                                    selected_unit = next(cycle)
                                    if selected_unit == test_cycle and len(active_units) > 1:
                                        selected_unit = next(cycle)
                                    selected_cell = selected_unit.xy
                                    display_img = True
                                    if selected_unit.xy[1] - round(grid_width / 2) <= 0:
                                        grid_scroll = 0
                                    elif selected_unit.xy[1] - round(grid_width / 2) <= grid_height - grid_width:
                                        grid_scroll = selected_unit.xy[1] - round(grid_width / 2)
                                    else:
                                        grid_scroll = grid_height - grid_width
                                    scroller.update_y(grid_scroll)
                            if turn_button.is_over(event.pos):
                                next_turn()
                                unit_count, active_units, cycle = update_unit_status()
                                scroller.update_y(grid_scroll)
                            if selected_unit is not None and selected_unit.game_id == 'Engineer' and \
                                    selected_unit.build_menu:
                                if build_select.is_over(event.pos):
                                    make_click()
                                    build_request = build_lib.get(build_scroll)
                                if build_up.is_over(event.pos):
                                    if build_scroll >= 1:
                                        make_click()
                                        build_scroll -= 1
                                if build_down.is_over(event.pos):
                                    if build_scroll <= 0 + build_unlocks.get(turn_map.get(turn)):
                                        make_click()
                                        build_scroll += 1
                                if cancel_build_button.is_over(event.pos):
                                    make_click()
                                    build_request = None
                                    selected_unit.build_menu = False
                            if selected_unit is not None and selected_unit.game_id == 'Teleporter' and len(
                                    tp_options) > 0:
                                if tp_button_1.is_over(event.pos):
                                    make_click()
                                    tp_request = tp_options[0]
                                if tp_button_2.is_over(event.pos) and len(tp_options) > 1:
                                    make_click()
                                    tp_request = tp_options[1]
                                if tp_button_3.is_over(event.pos) and len(tp_options) > 2:
                                    make_click()
                                    tp_request = tp_options[2]
                                if tp_button_4.is_over(event.pos) and len(tp_options) > 3:
                                    make_click()
                                    tp_request = tp_options[3]
                        if back_button.is_over(event.pos):
                            return 1
            if event.type == pg.MOUSEBUTTONUP:
                scrolling = False
            if event.type == pg.VIDEORESIZE:
                screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
                w, h = event.w, event.h
            if event.type == pg.QUIT:
                return 0
        screen.blit(grid_space, (adj_x, adj_y))
        draw_team_stats(grid_w, len(unit_count), len(active_units))
        if display_img:
            if selected_cell is None:
                display_img = False
            else:
                display_window.blit(art.return_icon(selected_unit.image), (round(disp_w / 6), round(disp_h / 6)))
                if selected_unit.team is not None:
                    art.draw_health_bar(display_window, disp_w, disp_h, selected_unit.current_hp, selected_unit.hp)
                draw_display_text(grid_w, selected_unit)
                if selected_unit.game_id == 'Engineer' and selected_unit.build_menu:
                    screen.blit(
                        art.return_icon(art.image_lib.get(f'{selected_unit.team}{build_lib.get(build_scroll)}')), \
                        ((grid_w + 650), 670))
                    draw_build_menu_text(grid_w, build_lib.get(build_scroll), \
                                         dimension_lib.get(build_lib.get(build_scroll)))
                    if build_request is not None:
                        graphic_squares.clear()
                        click_graphic = 3
                if selected_unit.team == turn_map.get(turn):
                    draw_display_stats(grid_w, selected_unit)
                    if selected_unit.static:
                        if selected_unit.produce is not None and type(selected_unit.produce) == tuple:
                            if selected_unit.queue is None and len(unit_count) < unit_limit.get(turn_map.get(turn)):
                                build_button_1.draw(screen, art.GREEN)
                                build_button_2.draw(screen, art.GREEN)
                            else:
                                build_button_1.draw(screen, art.RED)
                                build_button_2.draw(screen, art.RED)
                            screen.blit(selected_unit.button_1(), (grid_w + 165, 100))
                            screen.blit(selected_unit.button_2(), (grid_w + 165, 200))
                        elif selected_unit.produce is not None:
                            if selected_unit.queue is None and len(unit_count) < unit_limit.get(turn_map.get(turn)):
                                build_button_1.draw(screen, art.GREEN)
                            else:
                                build_button_1.draw(screen, art.RED)
                            screen.blit(selected_unit.button_1(), (grid_w + 165, 100))
                        elif selected_unit.game_id == 'Teleporter':
                            tp_options = find_tp_targets()
                            for num, option in enumerate(tp_options, 1):
                                current_button = locals()[f'tp_button_{num}']
                                current_button.draw(screen, art.GREEN)
                                screen.blit(art.return_button(option.image), (current_button.x, current_button.y))
                    else:
                        if selected_unit.steps_remaining == selected_unit.speed:
                            move_button.draw(screen, art.GREEN)
                        elif selected_unit.steps_remaining > 0:
                            move_button.draw(screen, art.BLACK)
                        else:
                            selected_unit.activities[0] = 1
                            move_button.draw(screen, art.RED)
                        if selected_unit.has_attacked or not selected_unit.can_attack:
                            selected_unit.activities[1] = 1
                            attack_button.draw(screen, art.RED)
                        else:
                            attack_button.draw(screen, art.GREEN)
                        if selected_unit.special_used or not selected_unit.special_condition:
                            selected_unit.activities[2] = 1
                            special_button.draw(screen, art.RED)
                        else:
                            special_button.draw(screen, art.GREEN)
                        if not 0 in selected_unit.activities:
                            unit_count, active_units, cycle = update_unit_status()
        screen.blit(display_window, (grid_w + 350, 100))
        if game_over:
            winner = turn_map.get(turn)
            game_over_text(winner)

        pg.display.update()
        clock.tick(60)


# pg init / parent game loop
if __name__ == '__main__':
    w, h = set_screen()
    pg.init()
    clock = pg.time.Clock()
    pg.display.set_caption('Infiltrate')
    pg.display.set_icon(art.WindowLogo)
    screen = pg.display.set_mode((w, h), pg.RESIZABLE)
    while True:
        if game_state == 1:
            game_state = main_menu()
        elif game_state == 2:
            game_state = settings_menu()
        elif game_state == 3:
            game_state = game()
        elif game_state == 4:
            game_state = tutorial()
        else:
            pg.quit()
            sys.exit()
        make_click()
