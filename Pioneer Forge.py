import os
import platform
try:
    import pygame
except ImportError:
    os.system('pip3 install pygame-ce')
    import pygame
os.system('cls' if platform.system() == 'Windows' else 'clear')
print('Pioneer Forge v1.2 by Pickles6855')
import pickle
from data import *
from os.path import exists
from time import time

pygame.init()

def load_data():
    with open(load_path('save.pkl', parent_dir=DIR), 'rb') as save_file:
        world_data, buildings_save = pickle.load(save_file), pickle.load(save_file)
        wood, stone, food = pickle.load(save_file), pickle.load(save_file), pickle.load(save_file)
        population, happiness, day = pickle.load(save_file), pickle.load(save_file), pickle.load(save_file)
        population_growth, food_consumption = pickle.load(save_file), pickle.load(save_file)
        try:
            achievments = pickle.load(save_file)
        except:
            achievments = [
                # Achievment format
                # [name, description, [regular image, grayscale image], image path, completed (true or false), [show pop up, pop up delay], check for completion function]
                ['Defender', 'Have 3 fortresses.', [], load_path('achievments', 'defender.png'), False, [False, 0, 'down'], defender_achievment],
                ['Builder', 'Build all available structures.', [], load_path('achievments', 'builder.png'), False, [False, 0, 'down'], builder_achievment],
                ['Wealthy Settlement', 'Have 1,000 of each resource.', [], load_path('achievments', 'wealthy_settlement.png'), False, [False, 0, 'down'], wealthy_achievment],
                ['Happy Settlement', 'Have a happiness of 100%.', [], load_path('achievments', 'happiness.png'), False, [False, 0, 'down'], happiness_achievment],
                ['Hamlet', 'Have a population of 100.', [], load_path('achievments', 'hamlet.png'), [False, 0, 'down'], hamlet_achievment],
                ['Small Village', 'Have a population of 300.', [], load_path('achievments', 'small_village.png'), False, [False, 0, 'down'], small_village_achievment],
                ['Large Village', 'Have a population of 700.', [], load_path('achievments', 'large_village.png'), False, [False, 0, 'down'], large_village_achievment],
                ['Small City', 'Have a population of 1500.', [], load_path('achievments', 'small_city.png'), False, [False, 0, 'down'], small_city_achievment],
                ['Large City', 'Have a population of 3000.', [], load_path('achievments', 'large_city.png'), False, [False, 0, 'down'], large_city_achievment],
            ]
    buildings = [building[-1].load_save_obj(building) for building in buildings_save] 
    for achievment in achievments:
        img = pygame.transform.scale(pygame.image.load(achievment[3]), ACHIEVMENTS_SIZE).convert_alpha()
        achievment[2] = [img, grayscale(img.copy())]
    return world_data, buildings, wood, stone, food, population, happiness, day, population_growth, food_consumption, achievments

def draw_world_data(display: pygame.Surface, offset_x, offset_y, world_data):
    for y, row in enumerate(world_data):
        for x, col in enumerate(row):
            tile_pos = (x * TILE_SIZE - offset_x, y * TILE_SIZE - offset_y)
            
            # Grass and flowers
            if col >= 0 and col < 1:
                if col == 0:
                    display.blit(GRASS_IMG, tile_pos)
                elif col == 0.1:
                    display.blit(GRASS_DAISY_FLOWERS_IMG, tile_pos)
                elif col == 0.2:
                    display.blit(GRASS_RED_FLOWERS_IMG, tile_pos)
                elif col == 0.3:
                    display.blit(GRASS_YELLOW_FLOWERS_IMG, tile_pos)
            # Trees
            elif col >= 1 and col < 2:
                display.blit(GRASS_IMG, tile_pos)
                if col == 1:
                    display.blit(TREE_1_IMG, tile_pos)
                elif col == 1.1:
                    display.blit(TREE_2_IMG, tile_pos)
                elif col == 1.2:
                    display.blit(TREE_3_IMG, tile_pos)

            else:
                display.blit(GRASS_IMG, tile_pos)
                
    return display


def handle_movement(dt, offset_x, offset_y):
    keys = pygame.key.get_pressed()
    x_change = 0
    y_change = 0

    # Left
    if keys[pygame.K_a] and offset_x > MOVE_VEL:
        x_change -= MOVE_VEL
    # Right
    if keys[pygame.K_d] and offset_x < 5000 - WIDTH:
        x_change += MOVE_VEL
    # Up
    if keys[pygame.K_w] and offset_y > MOVE_VEL:
        y_change -= MOVE_VEL
    # Down
    if keys[pygame.K_s] and offset_y < 5000 - HEIGHT:
        y_change += MOVE_VEL
    # Speed up movement when shift is held
    if keys[pygame.K_LSHIFT]:
        x_change *= 2
        y_change *= 2

    offset_x += x_change * dt
    offset_y += y_change * dt

    return offset_x, offset_y



def main(display, current_music_track):
    # Generate world if one hasn't been generated
    if exists(load_path('save.pkl', parent_dir=DIR)) == False:
        generate_world()
    
    # Variables
    offset_x = (2500 - WIDTH//2)//TILE_SIZE * TILE_SIZE
    offset_y = (2500 - HEIGHT//2)//TILE_SIZE * TILE_SIZE
    policies_menu = False
    achievments_menu = False
    build_mode = False
    placed_building_x = 0
    placed_building_y = 0
    selected_building = 0
    selected_achievment = 0
    fps_clock = pygame.time.Clock()

    day_tick = 0
    building_action_tick = 0
    building_action_event = False
    speed = 1
    reload_world = False
    
    # Delta time variables
    last_time = time()
    
    # Attack variables
    attackers = 0
    under_attack = False
    attack_text_visible = 0
    days_since_last_attack = -5

    # Load data from save
    world_data, buildings, wood, stone, food, population, happiness, day, population_growth, food_consumption, achievments = load_data()

    # Buildings
    available_buildings = [
        House(
            load_path('buildings', 'house_1.png'), load_path('buildings', 'house_icon.png'),
            0, 0, 3, 'House 1', 3, 'A place to call home\n+3 Housing Slots\n+3 Happiness', {'wood': 2, 'stone': 1, 'food': 0}),
        House(
            load_path('buildings', 'house_2.png'), load_path('buildings', 'house_icon.png'), 
            0, 0, 5, 'House 2', 5, 'A place to call home\n+5 Housing Slots\n+5 Happiness', {'wood': 4, 'stone': 2, 'food': 0}),
        House(
            load_path('buildings', 'house_3.png'), load_path('buildings', 'house_icon.png'), 
            0, 0, 8, 'House 3', 6, 'A place to call home\n+8 Housing Slots\n+6 Happiness', {'wood': 6, 'stone': 2, 'food': 0}),
        Woodcutter(
            load_path('buildings', 'woodcutter.png'), load_path('buildings', 'woodcutter_icon.png'), 
            0, 0, 'Woodcutter', 1, 'Gathers wood by chopping trees\n+2 wood per worker every day\n+1 Happiness\n+5 Job Slots', {'wood': 1, 'stone': 3, 'food': 0}),
        Mine(
            load_path('buildings', 'mine.png'), load_path('buildings', 'mine_icon.png'), 
            0, 0, 'Mine', 1, 'Produces stone from deep mines\n+2 stone per worker every day\n+1 Happiness\n+5 Job Slots', {'wood': 3, 'stone': 1, 'food': 0}),
        Farm(
            load_path('buildings', 'farm.png'), load_path('buildings', 'farm_icon.png'), 
            0, 0, 'Farm', 2, 'Grows food to sustain your citizens\n+2 food per worker every day\n+2 Happiness\n+5 Job Slots', {'wood': 3, 'stone': 0, 'food': 1}),
        Bakery(
            load_path('buildings', 'bakery.png'), load_path('buildings', 'bakery_icon.png'), 
            0, 0, 'Bakery', 10, 'Makes delicious bread and sweets\n+2 food per worker every day\n+10 Happiness\n+2 Job Slots', {'wood': 2, 'stone': 2, 'food': 2}),
        Blacksmith(
            load_path('buildings', 'blacksmith.png'), load_path('buildings', 'blacksmith_icon.png'), 
            0, 0, 'Blacksmith', 1, 'Increases woodcutter and mine efficiency\n+1 Happiness\n+2 Job Slots', {'wood': 2, 'stone': 4, 'food': 0}),
        Tavern(
            load_path('buildings', 'tavern.png'), load_path('buildings', 'tavern_icon.png'), 
            0, 0, 'Tavern', 12, 'A place for people to hang out\n+12 Happiness\n+2 Job Slots', {'wood': 3, 'stone': 3, 'food': 2}),
        Fortress(
            load_path('buildings', 'fortress.png'), load_path('buildings', 'fortress_icon.png'),
            0, 0, 'Fortress', 1, 'Defends againsts attackers\n+0 Happiness\n+3 Job Slots', {'wood': 2, 'stone': 8, 'food': 0})
    ]
    buildings.append(
        House(
            load_path('buildings', 'house_3.png'), load_path('buildings', 'house_icon.png'),
            24, 24, 8, 'House 3', 6, 'A place to call home\n+8 Housing Slots\n+6 Happiness', {'wood': 6, 'stone': 2, 'food': 0})
    ) if buildings == [] else None
    world_data[24][24] = 2.1

    # Buttons
    pause_button = Button(get_frame(PAUSE_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], 0), get_frame(PAUSE_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], 1),
                          WIDTH - 10 - BUTTON_SIZE[0]//2, 10, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], play_button_sound)
    speed_button = Button('reg image', 'hover image', WIDTH - 20 - BUTTON_SIZE[0], 10, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], play_button_sound)
    policies_button = Button(get_frame(POLICIES_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], 0), get_frame(POLICIES_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], 1),
                             WIDTH - 30 - BUTTON_SIZE[0]//2 * 3, 10, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], play_button_sound)
    change_policies_buttons = [
        # Population growth buttons
        Button(get_frame(PLUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 0), get_frame(PLUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 1),
               -100, -100, BUTTON_SIZE[0]//4, BUTTON_SIZE[0]//2, play_button_sound),
        Button(get_frame(MINUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 0), get_frame(MINUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 1),
               -100, -100, BUTTON_SIZE[0]//4, BUTTON_SIZE[0]//2, play_button_sound),
        
        # Food consumption buttons
        Button(get_frame(PLUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 0), get_frame(PLUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 1),
               -100, -100, BUTTON_SIZE[0]//4, BUTTON_SIZE[0]//2, play_button_sound),
        Button(get_frame(MINUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 0), get_frame(MINUS_BUTTON_IMG, BUTTON_SIZE[0]//4, BUTTON_SIZE[1]//2, 1),
               -100, -100, BUTTON_SIZE[0]//4, BUTTON_SIZE[0]//2, play_button_sound)
    ]
    achievments_button = Button(get_frame(ACHIEVMENTS_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], 0), get_frame(ACHIEVMENTS_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], 1), 
                                WIDTH - 40 - BUTTON_SIZE[0] * 2, 10, BUTTON_SIZE[0]//2, BUTTON_SIZE[1], play_button_sound)
    right_arrow_button = Button(get_frame(RIGHT_ARROW_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[0], 0), get_frame(RIGHT_ARROW_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[0], 1),
                                int(0.9 * WIDTH), HEIGHT//2 - BUTTON_SIZE[0], BUTTON_SIZE[0]//2, BUTTON_SIZE[0], play_button_sound
                                )
    left_arrow_button = Button(get_frame(LEFT_ARROW_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[0], 1), get_frame(LEFT_ARROW_BUTTON_IMG, BUTTON_SIZE[0]//2, BUTTON_SIZE[0], 0),
                                WIDTH//10 - BUTTON_SIZE[0]//2, HEIGHT//2 - BUTTON_SIZE[0], BUTTON_SIZE[0]//2, BUTTON_SIZE[0], play_button_sound
                                )

    # Event loop
    while True:
        fps_clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = int(mouse_pos[0] * WIDTH / WINDOW.get_width())
        mouse_y = int(mouse_pos[1] * HEIGHT / WINDOW.get_height())
        events = pygame.event.get()
        dt = (time() - last_time) * 60
        last_time = time()
        for event in events:
            if event.type == pygame.QUIT:
                save_data(world_data, buildings, wood, stone, food, population, happiness, day, population_growth, food_consumption, achievments)
                pygame.quit()
                quit()

            # Update number of days
            if event.type == DAY_TICK_EVENT:
                if day_tick >= 3 - speed:
                    day += 1
                    day_tick = 0
                    if not under_attack:
                        days_since_last_attack += 1
                        
                    # Initiate attacks
                    if not under_attack and days_since_last_attack > 15 and randint(1, 3):
                        pygame.mixer.music.fadeout(1000)
                        ATTACK_CHANNEL.play(ATTACK_SOUND, 2)
                        attackers = day * 2
                        under_attack = True
                else:
                    day_tick += 1

            # Pause
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_ESCAPE:
                    if build_mode:
                        build_mode = False
                    elif policies_menu:
                        policies_menu = False
                    else:
                        save_data(world_data, buildings, wood, stone, food, population, happiness, day, population_growth, food_consumption, achievments)
                        display, current_music_track, reload_world = main_menu(display, current_music_track)
                        
                if event.key == pygame.K_r:
                    speed = change_speed(speed)

            # Produce resources
            if event.type == BUILDING_ACTION_EVENT:
                building_action_event = True
                if building_action_tick >= 3 - speed:
                    for building in buildings:
                        wood, stone, food, attackers = building.action(wood, stone, food, population, buildings, happiness, attackers)
                    building_action_tick = 0
                else:
                    building_action_tick += 1

            # Place Buildings
            if event.type == pygame.MOUSEBUTTONDOWN and build_mode == False and policies_menu == False and achievments_menu == False:

                # Calculates which tile is selected
                placed_building_x = int(((offset_x + mouse_x) // TILE_SIZE * TILE_SIZE) // TILE_SIZE)
                placed_building_y = int(((offset_y + mouse_y) // TILE_SIZE * TILE_SIZE) // TILE_SIZE)
                
                on_buttons = NO_PLACE_RECT.collidepoint(mouse_x, mouse_y)

                if world_data[placed_building_y][placed_building_x] != 2.1 and on_buttons == False:
                    build_mode = True
    
    
        current_music_track = handle_music(current_music_track)
        
        offset_x, offset_y = handle_movement(dt, offset_x, offset_y) if build_mode == False else (offset_x, offset_y)
        
        display = draw_world_data(display, offset_x, offset_y, world_data)

        population, buildings, happiness, food = handle_population(population, buildings, building_action_event, happiness, food, population_growth, food_consumption, under_attack)

        # Buildings
        building_info_list = []
        for building in buildings:
            display, menu_open, building_info, delete_building = building.update(display, offset_x, offset_y, events, mouse_x, mouse_y)
            if delete_building:
                world_data[building.grid_y][building.grid_x] = 0
                buildings.remove(building)
                DESTROY_BUILDING_SOUND.play()
            building_info_list.append(building_info)
            # Close building info for all buildings except one
            if menu_open:
                for building2 in buildings:
                    if building != building2:
                        building2.menu_open = False
        # Draw building info
        for building in building_info_list:
            if building != []:
                display.blit(building[0], building[1])
                display.blit(building[2], building[3])
        
        display = draw_resource_text(display, wood, stone, food, population, happiness, day, buildings, food_consumption, mouse_x, mouse_y)
    
        # Handle Build Mode
        if build_mode == True:
            display, selected_building, buildings, world_data, build_mode, wood, stone, food, right_arrow_button, left_arrow_button = handle_build_mode(
                display, selected_building, available_buildings, buildings, world_data, events, offset_x, offset_y, placed_building_x, placed_building_y, wood, stone, food, right_arrow_button, left_arrow_button, mouse_x, mouse_y)
            if build_mode == False:
                save_data(world_data, buildings, wood, stone, food, population, happiness, day, population_growth, food_consumption, achievments)
             
        # Achievments
        display, achievments = handle_achievments(display, achievments, wood, stone, food, happiness, population, buildings, available_buildings)
        if achievments_menu:
            display, selected_achievment = handle_achievments_menu(display, mouse_x, mouse_y, events, left_arrow_button, right_arrow_button, achievments, selected_achievment)
                
        # Attacks
        if under_attack:
            display, attackers, under_attack, attack_text_visible, days_since_last_attack = handle_attack(display, attackers, buildings, attack_text_visible, days_since_last_attack, events)        
        
        display, pause_button, speed_button, policies_button, achievments_button, speed, policies_menu, achievments_menu, population_growth, food_consumption, change_policies_buttons, current_music_track, reload_world = handle_hud(display, pause_button, speed, speed_button, policies_button, achievments_button, events, policies_menu, achievments_menu, food_consumption, population_growth, change_policies_buttons, current_music_track, world_data, buildings, wood, stone, food, population, happiness, day, mouse_x, mouse_y, achievments)
        
        # Will recheck the save file for new data if the player has reset the save file
        if reload_world:
            main(display, current_music_track)
            return
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_0]:
            population[0] += 1
            population[1] += 1
            wood += 1
            stone += 1
            food += 1
        
        draw_scaled_display(display)
        building_action_event = False

if __name__ == '__main__':
    
    # Setup Music
    pygame.mixer.music.load(MUSIC_TRACKS[0])
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play()
    current_music_track = 0
    
    display, current_music_track, _ = main_menu(pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA), current_music_track)
    main(display, current_music_track)