#!/usr/bin/env python3

import gamelib.Utils as Utils
import gamelib.Constants as Constants
import gamelib.Structures as Structures
import gamelib.Sprites as Sprites
import gamelib.Actuators.SimpleActuators as SimpleActuators
from gamelib.Game import Game
from gamelib.Characters import Player,NPC
from gamelib.Board import Board
from gamelib.BoardItem import BoardItemVoid
import os
import uuid
from copy import deepcopy

# Global variables
is_modified = False
edit_mode = True

# Functions definition
def place_and_go(object,x,y,direction):
    global is_modified
    global game
    game.move_player(direction,1)
    game.current_board().place_item( deepcopy(object),x,y)
    is_modified = True

def clear_and_go(direction):
    global is_modified
    global game
    new_x = game.player.pos[0]
    new_y = game.player.pos[1]
    if direction == Constants.DOWN:
        new_x += 1
    elif direction == Constants.UP:
        new_x -= 1
    elif direction == Constants.LEFT:
        new_y -= 1
    elif direction == Constants.RIGHT:
        new_y += 1

    if new_x < 0 or new_y < 0 or new_x > (game.current_board().size[1]-1) or new_y > (game.current_board().size[0]-1):
        Utils.warn(f"Cannot remove anything at [{new_x},{new_y}] as it is out of bound.")
    else:
        game.current_board().clear_cell(new_x,new_y)
        game.move_player(direction,1)
        is_modified = True

def switch_edit_mode():
    global edit_mode
    edit_mode = not edit_mode
    if edit_mode:
        game.update_menu_entry('main',Utils.white_bright('j/i/k/l'),Utils.green_bright('Place')+' the current object and then move cursor Left/Up/Down/Right')
    else:
        game.update_menu_entry('main',Utils.white_bright('j/i/k/l'),'Move cursor Left/Up/Down/Right and '+Utils.red_bright('Delete')+' anything that was at destination.')


def color_picker():
    global game
    game.clear_screen()
    print('Pick a form and color from the list:')
    game.display_menu('graphics_utils',Constants.ORIENTATION_HORIZONTAL,8)
    return str(input('\n(Enter a number)> '))

def sprite_picker():
    global game
    game.clear_screen()
    print('Pick a sprite from the list:')
    game.display_menu('graphics_sprites',Constants.ORIENTATION_HORIZONTAL,8)
    return str(input('\n(Enter a number)> '))

def model_picker():
    global game
    game.clear_screen()
    print("What kind of model do you want (you can edit that later)?\n1 - Colored squares and rectangles\n2 - Sprites\n3 - Set your own string of character(s)")
    choice = str( Utils.get_key() )
    if choice == '1':
        return game.get_menu_entry('graphics_utils',color_picker())['data']
    if choice == '2':
        return game.get_menu_entry('graphics_sprites',sprite_picker())['data']
    if choice == '3':
        return str( input('Enter your string now: ') )

def to_history(object):
    global object_history
    if len(object_history) <= 10 and object not in object_history and not isinstance(object,BoardItemVoid):
        object_history.append(object)
    elif len(object_history) > 10 and object not in object_history and not isinstance(object,BoardItemVoid):
        del(object_history[0])
        object_history.append(object)

def create_wizzard():
    global game
    game.clear_screen()
    # 1 - Choose object type between structures or characters
    # 2 - pick one
    # 3 - Structure: customize name, type, size, etc.
    print(Utils.green_bright("\t\tObject creation wizzard"))
    print('What do you want to create: a NPC or a structure?')
    print('1 - NPC (Non Playable Character)')
    print('2 - Structure (Wall, Treasure, Portal, Trees, etc.)')
    key = Utils.get_key()
    if key == '1':
        game.clear_screen()
        print(Utils.green_bright("\t\tObject creation wizzard: ")+Utils.cyan_bright("NPC") )
        new_object = NPC()
        print("First give a name to your NPC. Default value: "+new_object.name)
        r = str( input('(Enter name)> ') )
        if len(r) > 0:
            new_object.name = r
        print("Then give it a type. A type is important as it allows grouping.\nType is a string. Default value: "+new_object.type)
        r = str( input('(Enter type)> ') )
        if len(r) > 0:
            new_object.type = r
        print("Now we need a model. Default value: "+new_object.model)
        input('Hit "Enter" when you are ready to choose a model.')
        new_object.model = model_picker()
        game.clear_screen()
        print(Utils.green_bright("\t\tObject creation wizzard: ")+Utils.cyan_bright("NPC")+f' - {new_object.model}' )
        print('We now needs to go through some basic statistics. You can decide to go with default by simply hitting the "Enter" key.')
        r = input(f'Number of cell crossed in one turn. Default: {new_object.step}(type: int) > ')
        if len(r)> 0:
            new_object.step = int(r)
        else:
            # If it's 0 it means it's going to be a static NPC so to prevent python to pass some random pre-initilized default, we explicitely set the Actuator to a static one
            new_object.actuator = SimpleActuators.RandomActuator(moveset=[])
        r = input(f'Max HP (Health Points). Default: {new_object.max_hp}(type: int) > ')
        if len(r)> 0:
            new_object.max_hp = int(r)
        new_object.hp = new_object.max_hp
        r = input(f'Max MP (Mana Points). Default: {new_object.max_mp}(type: int) > ')
        if len(r)> 0:
            new_object.max_mp = int(r)
        new_object.mp = new_object.max_mp
        r = input(f'Remaining lives (it is advised to set that to 1 for a standard NPC). Default: {new_object.remaining_lives}(type: int) > ')
        if len(r)> 0:
            new_object.remaining_lives = int(r)
        r = input(f'AP (Attack Power). Default: {new_object.attack_power}(type: int) > ')
        if len(r)> 0:
            new_object.attack_power = int(r)
        r = input(f'DP (Defense Power). Default: {new_object.defense_power}(type: int) > ')
        if len(r)> 0:
            new_object.defense_power = int(r)
        r = input(f'Strength. Default: {new_object.strength}(type: int) > ')
        if len(r)> 0:
            new_object.strength = int(r)
        r = input(f'Intelligence. Default: {new_object.intelligence}(type: int) > ')
        if len(r)> 0:
            new_object.intelligence = int(r)
        r = input(f'Agility. Default: {new_object.agility}(type: int) > ')
        if len(r)> 0:
            new_object.agility = int(r)
        game.clear_screen()
        print("We now need to give some life to that NPC. What kind of movement should it have:")
        print("1 - Randomly chosen from a preset of directions")
        print("2 - Following a predetermined path")
        r = Utils.get_key()
        if r == '1':
            new_object.actuator = SimpleActuators.RandomActuator(moveset=[])
            print('Random it is! Now choose from which preset of movements should we give it:')
            print('1 - UP,DOWN,LEFT, RIGHT')
            print('2 - UP,DOWN')
            print('3 - LEFT, RIGHT')
            print('4 - UP,DOWN,LEFT, RIGHT + all DIAGONALES')
            print('5 - DIAGONALES (DIAG UP LEFT, DIAG UP RIGHT, etc.) but NO straight UP, DOWN, LEFT and RIGHT')
            r = Utils.get_key()
            if r == '1':
                new_object.actuator.moveset = [Constants.UP,Constants.DOWN,Constants.LEFT,Constants.RIGHT]
            elif r == '2':
                new_object.actuator.moveset = [Constants.UP,Constants.DOWN]
            elif r == '3':
                new_object.actuator.moveset = [Constants.RIGHT,Constants.LEFT]
            elif r == '4':
                new_object.actuator.moveset = [Constants.UP,Constants.DOWN,Constants.LEFT,Constants.RIGHT,Constants.DLDOWN,Constants.DLUP,Constants.DRDOWN,Constants.DRUP]
            elif r == '5':
                new_object.actuator.moveset = [Constants.DLDOWN,Constants.DLUP,Constants.DRDOWN,Constants.DRUP]
        elif r == '2':
            new_object.actuator = SimpleActuators.PathActuator(path=[])
            print("Great, so what path this NPC should take:")
            print('1 - UP/DOWN patrol')
            print('2 - DOWN/UP patrol')
            print('3 - LEFT/RIGHT patrol')
            print('4 - RIGHT/LEFT patrol')
            print('5 - Circle patrol: LEFT, DOWN, RIGHT, UP')
            print('6 - Circle patrol: LEFT, UP, RIGHT, DOWN')
            print('7 - Circle patrol: RIGHT, DOWN, LEFT, UP')
            print('8 - Circle patrol: RIGHT, UP, LEFT, DOWN')
            print('9 - Write your own path')
            r = Utils.get_key()
            if r == '1':
                print("How many steps should the NPC go in one direction before turning back ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
            elif r == '2':
                print("How many steps should the NPC go in one direction before turning back ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
            elif r == '3':
                print("How many steps should the NPC go in one direction before turning back ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.LEFT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.RIGHT for i in range(0, r,1) ]
            elif r == '3':
                print("How many steps should the NPC go in one direction before turning back ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.RIGHT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.LEFT for i in range(0, r,1) ]
            elif r == '4':
                print("How many steps should the NPC go in one direction before turning back ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
            elif r == '5':
                print("How many steps should the NPC go in EACH direction before changing ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.LEFT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.RIGHT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
            elif r == '6':
                print("How many steps should the NPC go in EACH direction before changing ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.LEFT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.RIGHT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
            elif r == '7':
                print("How many steps should the NPC go in EACH direction before changing ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.RIGHT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.LEFT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
            elif r == '8':
                print("How many steps should the NPC go in EACH direction before changing ?")
                r = int(input("(please enter an integer)> "))
                new_object.actuator.path += [Constants.RIGHT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.UP for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.LEFT for i in range(0, r,1) ]
                new_object.actuator.path += [Constants.DOWN for i in range(0, r,1) ]
            elif r == '9':
                print("Write your own path using only words from this list: UP, DOWN, LEFT, RIGHT, DLDOWN, DLUP, DRDOWN, DRUP.")
                print('Each direction has to be separated by a coma.')
                r = str(input('Write your path: ')).upper()
                new_object.actuator.path = r.split(',')

        return new_object
    elif key == '2':
        game.clear_screen()
        print(Utils.green_bright("\t\tObject creation wizzard: ")+Utils.magenta_bright("Structure") )
        print("What kind of structure do you want to create:")
        print('1 - A wall like structure (an object that cannot be picked-up and is not overlappable). Ex: walls, trees, non moving elephant (try to go through an elephant or to pick it up in your backpack...)')
        print('2 - A treasure (can be picked up, take space in the inventory, give points to the player)')
        print('3 - A generic object (you can set the properties to make it pickable or overlappable)')
        print('4 - A generic actionnable object (to make portals, heart to resplenish life, etc.)')
        key = Utils.get_key()
        new_object = None
        if key == '1':
            new_object = Structures.Wall()
            new_object.name = str(uuid.uuid1())
            new_object.model = model_picker()
        if key == '2':
            new_object = Structures.Treasure()
            print("First give a name to your Treasure. Default value: "+new_object.name)
            r = str( input('(Enter name)> ') )
            if len(r) > 0:
                new_object.name = r
            print("Then give it a type. A type is important as it allows grouping (in this case probably in the inventory).\nType is a string. Default value: "+new_object.type)
            r = str( input('(Enter type)> ') )
            if len(r) > 0:
                new_object.type = r
            print("Now we need a model. Default value: "+new_object.model)
            input('Hit "Enter" when you are ready to choose a model.')
            new_object.model = model_picker()
        if key == '3' or key == '4':
            if key == '3':
                new_object = Structures.GenericStructure()
            else:
                new_object = Structures.GenericActionnableStructure()
            new_object.set_overlappable(False)
            new_object.set_pickable(False)
            print("First give a name to your structure. Default value: "+new_object.name)
            r = str( input('(Enter name)> ') )
            if len(r) > 0:
                new_object.name = r
            print("Then give it a type. \nType is a string. Default value: "+new_object.type)
            r = str( input('(Enter type)> ') )
            if len(r) > 0:
                new_object.type = r
            print("Now we need a model. Default value: "+new_object.model)
            input('Hit "Enter" when you are ready to choose a model.')
            new_object.model = model_picker()
            print('Is this object pickable? (can it be picked up by the player)?')
            print('0 - No')
            print('1 - Yes')
            r = Utils.get_key()
            if r == '1':
                new_object.set_pickable(True)
            print('Is this object overlappable? (can it be walked over by player?')
            print('0 - No')
            print('1 - Yes')
            r = Utils.get_key()
            if r == '1':
                new_object.set_overlappable(True)

        return new_object

    #Placeholder
    return BoardItemVoid()


def save_current_board():
    global game
    global object_history
    global is_modified
    if not os.path.exists('hac-maps') or not os.path.isdir('hac-maps'):
        os.makedirs('hac-maps')
    game.object_library = object_history
    game.save_board(1,'hac-maps/'+game.current_board().name.replace(' ','_')+'.json')
    is_modified=False

def create_board_wizzard():
    global game
    global is_modified
    game.clear_screen()
    print( Utils.blue_bright("\t\tNew board") )
    print("First we need some informations on your new board:")
    name = str( input('Name: ') )
    width = int( input('Width (in number of cells): ') )
    height = int( input('Height (in number of cells): ') )
    game.add_board(1, Board(name=name,size=[width,height], ui_borders=Utils.WHITE_SQUARE,ui_board_void_cell=Utils.BLACK_SQUARE) )
    is_modified=True

# Main program
game = Game()
game.player = Player(model='[]')
key = 'None'
current_object = BoardItemVoid(model='None')
object_history = []
current_menu = 'main'

game.clear_screen()
print( Utils.cyan_bright("HAC-GAME-LIB - EDITOR v"+Constants.HAC_GAME_LIB_VERSION) )

print('Looking for existing maps in hac-maps/ directory...',end='')
hmaps = []
try:
    hmaps = os.listdir('hac-maps/')
    print(Utils.green('OK'))
except FileNotFoundError as e:
    print(Utils.red('KO'))

if len(hmaps) > 0:
    map_num = 0
    game.add_menu_entry('boards_list',None,"Choose a map to edit")
    for m in hmaps:
        print(f"{map_num} - edit hac-maps/{m}")
        game.add_menu_entry('boards_list',str(map_num),f"edit hac-maps/{m}",f"hac-maps/{m}")
        map_num += 1
else:
    print("No pre-existing map found.")
print("n - create a new map")
print("q - Quit the editor")
choice = str( Utils.get_key() )
if choice == "q":
    print("Good Bye!")
    exit()
elif choice == "n":
    create_board_wizzard()
elif int(choice) < len(hmaps):
    game.load_board('hac-maps/'+hmaps[int(choice)],1)

game.change_level(1)

if len(game.object_library)>0:
    object_history += game.object_library

# Build the menus
i = 0
for sp in dir(Utils):
    if sp.endswith('_SQUARE') or sp.endswith('_RECT'):
        game.add_menu_entry('graphics_utils',str(i), '"'+getattr(Utils,sp)+'"', getattr(Utils,sp))
        i += 1

i = 0
for sp in dir(Sprites):
    if not sp.startswith('__'):
        game.add_menu_entry('graphics_sprites',str(i), getattr(Sprites,sp), getattr(Sprites,sp) )
        i += 1

game.add_menu_entry('main',None,'\n=== Menu ===')
game.add_menu_entry('main',Utils.white_bright('Space'),'Switch between edit/delete mode')
game.add_menu_entry('main',Utils.white_bright('0 to 9'),'Select an item in history to be the current item')
game.add_menu_entry('main',Utils.white_bright('a/w/s/d'),'Move cursor Left/Up/Down/Right')
game.add_menu_entry('main',Utils.white_bright('j/i/k/l'),Utils.green_bright('Place')+' the current item and then move cursor Left/Up/Down/Right')
game.add_menu_entry('main',Utils.white_bright('c'),'Create a new board item (becomes the current item, previous one is placed in history)')
game.add_menu_entry('main',Utils.white_bright('p'),'Modify board parameters')
game.add_menu_entry('main',Utils.white_bright('P'),'Set player starting position')
game.add_menu_entry('main',Utils.white_bright('S'),'Save the current Board to hac-maps/'+game.current_board().name.replace(' ','_')+'.json')
game.add_menu_entry('main',Utils.white_bright('+'),'Save this Board and create a new one')
game.add_menu_entry('main',Utils.white_bright('L'),'Save this Board and load a new one')
game.add_menu_entry('main',Utils.white_bright('Q'),'Quit the editor')

game.add_menu_entry('board',None,'=== Board ===')
game.add_menu_entry('board','1','Change '+Utils.white_bright('width')+' (only sizing up)')
game.add_menu_entry('board','2','Change '+Utils.white_bright('height')+' (only sizing up)')
game.add_menu_entry('board','3','Change '+Utils.white_bright('name'))
game.add_menu_entry('board','4','Change '+Utils.white_bright('top')+' border')
game.add_menu_entry('board','5','Change '+Utils.white_bright('bottom')+' border')
game.add_menu_entry('board','6','Change '+Utils.white_bright('left')+' border')
game.add_menu_entry('board','7','Change '+Utils.white_bright('right')+' border')
game.add_menu_entry('board','8','Change '+Utils.white_bright('void cell'))
game.add_menu_entry('board','0','Go back to the main menu')

while True:
    dbg_messages = []    

    if key == 'Q':
        if is_modified:
            print("Board has been modified, do you want to save it to avoid loosing your changes? (y/n)")
            answer = str(input('> '))
            if answer.startswith('y'):
                if not os.path.exists('hac-maps') or not os.path.isdir('hac-maps'):
                    os.makedirs('hac-maps')
                game.object_library = object_history
                game.save_board(1,'hac-maps/'+game.current_board().name.replace(' ','_')+'.json')
        break
    elif key == 'S':
        save_current_board()
        dbg_messages.append("Board saved")
    elif current_menu == 'main':
        if key == 'w':
            game.move_player(Constants.UP,1)
        elif key == 's':
            game.move_player(Constants.DOWN,1)
        elif key == 'a':
            game.move_player(Constants.LEFT,1)
        elif key == 'd':
            game.move_player(Constants.RIGHT,1)
        elif key == "k" and edit_mode:
            place_and_go( current_object, game.player.pos[0], game.player.pos[1], Constants.DOWN )
        elif key == "i" and edit_mode:
            place_and_go( current_object, game.player.pos[0], game.player.pos[1], Constants.UP )
        elif key == "j" and edit_mode:
            place_and_go( current_object, game.player.pos[0], game.player.pos[1], Constants.LEFT )
        elif key == "l" and edit_mode:
            place_and_go( current_object, game.player.pos[0], game.player.pos[1], Constants.RIGHT )
        elif key == "k" and not edit_mode:
            clear_and_go(Constants.DOWN)
        elif key == "i" and not edit_mode:
            clear_and_go(Constants.UP)
        elif key == "j" and not edit_mode:
            clear_and_go(Constants.LEFT)
        elif key == "l" and not edit_mode:
            clear_and_go(Constants.RIGHT)
        elif key == ' ':
            switch_edit_mode()
        elif key in '1234567890' and current_menu == 'main':
            o = object_history[int(key)]
            to_history(current_object)
            current_object = o
        elif key == 'P':
            game.current_board().player_starting_position = game.player.pos
            is_modified = True
            dbg_messages.append(f'New player starting position set at {game.player.pos}')
        elif key == 'p':
            current_menu = 'board'
        elif key == 'c':
            to_history(current_object)
            current_object = create_wizzard()
            to_history(current_object)
        elif key == '+':
            save_current_board()
            create_board_wizzard()
        elif key == 'L':
            save_current_board()
            current_menu = "boards_list"
    elif current_menu == 'board':
        if key == "0":
            current_menu = 'main'
        elif key == "1":
            game.clear_screen()
            nw = int(input("Enter the new width: "))
            if nw >= game.current_board().size[0]:
                old_value = game.current_board().size[0]
                game.current_board().size[0] = nw
                for x in range(0,game.current_board().size[1],1):
                    for y in range(old_value,game.current_board().size[0],1):
                        game.current_board()._matrix[x].append( BoardItemVoid( model=game.current_board().ui_board_void_cell ) )
                        is_modified = True


        elif key == "2":
            game.clear_screen()
            nw = int(input("Enter the new height: "))
            if nw >= game.current_board().size[1]:
                old_value = game.current_board().size[1]
                game.current_board().size[1]=nw
                for x in range(old_value,nw,1):
                    new_array = []
                    for y in range(0, game.current_board().size[0], 1 ):
                        new_array.append( BoardItemVoid( model=game.current_board().ui_board_void_cell ) )
                    game.current_board()._matrix.append(new_array)
                    is_modified = True

        elif key == "3":
            game.clear_screen()
            n = str(input('Enter the new name: '))
            game.current_board().name = n
            is_modified = True
        elif key == '4':
            game.current_board().ui_border_top = model_picker()
            is_modified = True
        elif key == '5':
            game.current_board().ui_border_bottom = model_picker()
            is_modified = True
        elif key == '6':
            game.current_board().ui_border_left = model_picker()
            is_modified = True
        elif key == '7':
            game.current_board().ui_border_right = model_picker()
            is_modified = True
        elif key == '8':
            game.current_board().ui_board_void_cell = model_picker()
            is_modified = True
    elif current_menu == 'boards_list':
        if key in '1234567890':
            e = game.get_menu_entry('boards_list',key)
            if e != None:
                game.load_board(e['data'],1)
                current_menu = 'main'

        
     # Print the screen and interface   
    game.clear_screen()
    if current_menu == 'main' or current_menu == 'board':
        print(Utils.white_bright('Current mode: '),end='')
        if edit_mode:
            print(Utils.green_bright("EDIT"),end='')
        else:
            print(Utils.red_bright('DELETE'),end='')
        print(f' | Board: {game.current_board().name} - {game.current_board().size} | Cursor @ {game.player.pos}')
    game.display_board()
    if len(object_history) > 10:
        del(object_history[0])
    if current_menu == 'main':
        print('Item history:')
        cnt = 0
        for o in object_history:
            print(f"{cnt}: {o.model}", end='  ')
            cnt += 1
        print('')
        print(f'Current item: {current_object.model}')
    game.display_menu(current_menu,Constants.ORIENTATION_VERTICAL,15)
    for m in dbg_messages:
        Utils.debug(m)
    key = Utils.get_key()

