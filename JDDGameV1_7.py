from JDDMenu_v2_6 import * 
import random
import sys
import cmd
import os
import time
import json


class GameState:

    def __init__(self, filepath):
        self.environment_manager = self.EnvironmentManager(filepath)
        self.player_manager = self.PlayerManager(health=20, inventory=[], quest_log={})
        self.inventory_manager = self.InventoryManager(inventory=[])
        self.grid_width = 9
        self.grid_height = 5
        self.player_position = [3,5] # World Spawn

    class EnvironmentManager:

        def __init__(self, filepath):
            self.data = GameUtils.load_data(filepath)
            # Here environments are mapped by their grid locations for easy access
            self.environments = {tuple(env['gridLocation']): key for key, env in self.data['environments'].items()}
            self.current_location = [3, 5]  # Initially synced with GameState player position

        def printEnv(self):
            """
            print self.environments for debugging purposes
            """
            print(self.environments)

        def update_environment(self):
            location_tuple = tuple(self.current_location)
            if location_tuple in self.environments:
                # Access the environment by name using the grid location
                environment_name = self.environments[location_tuple]
                print(f"You are now at {environment_name}")
            else:
                print("This area of the map is uncharted.")

        def get_current_location(self):
            location_tuple = tuple(self.current_location)
            if location_tuple in self.environments:
                # Access the environment by name using the grid location
                environment_name = self.environments[location_tuple]
            return environment_name

        def get_coordinates_for_location(self, location_name):
            """
            Debugging function used to get coordinates for a location when given a location name
            """
            # Iterate over environments to find matching location name
            for name, env in self.data['environments'].items():
                if name == location_name:
                    return env['gridLocation']
            # If location name not found, return a message indicating invalid location
            return f"No coordinates found for the location: {location_name}"

        def search_area(self):
            area = self.environments[self.current_location]
            if 'searched' not in area or not area['searched']:
                print(area.get("searchableInfo", "Nothing of interest."))
                if "lootPool" in area and area['lootPool']:
                    item = random.choice(area["lootPool"])
                    GameState.inventory_manager.add_item(item)
                area['searched'] = True
            else:
                print("You have already searched this area thoroughly.")

        def spawn_player(self, spawnLocation):
            print(f"!DEV Alert! Spawning at location = {spawnLocation}")  # Debug: Log the input location
            if spawnLocation == 'city':
                self.current_location = [4,2]
            elif spawnLocation == 'mountain':
                self.current_location = [3,5]
            elif spawnLocation == 'forest':
                self.current_location = [2,8]
            self.update_environment()
            self.log_player_location()

        def log_player_location(self):
            print(f"!Dev Alert! Location = {self.current_location}")

    class PlayerManager:

        def __init__(self, health, inventory, quest_log):
            self.health = health
            self.inventory = inventory
            self.quest_log = quest_log

        def update_health(self, amount):
            self.health += amount

        def has_item(self, item):
            return item in self.inventory

        def update_quest(self, quest_name, status):
            self.quest_log[quest_name] = status
            print(f"Quest '{quest_name}' updated to {status}")

    class InventoryManager:

        def __init__(self, inventory):
            self.inventory = inventory

        def add_item(self, item):
            self.inventory.append(item)
            print(f"Added {item} to inventory")

        def remove_item(self, item):
            if item in self.inventory:
                self.inventory.remove(item)
                print(f"Removed {item} from inventory")

    def print_status(self):
        """Print the current overall status of the player."""
        print(f"Current Location: {self.environment_manager.current_location}")
        print(f"Health: {self.player_manager.health}")
        print(f"Inventory: {self.inventory_manager.inventory}")
        print(f"Quest Log: {self.player_manager.quest_log}")


class GameEngine:

    def __init__(self, game_state, config_path):
        self.game_state = game_state
        self.config_path = config_path
        self.game_ui = GameUI(game_state, config_path)
        self.movements = {
            'n': (-1, 0),
            's': (1, 0),
            'e': (0, 1),
            'w': (0, -1)
        }

    def move(self, direction):
        if direction in self.movements:
            dx, dy = self.movements[direction]
            new_x = self.game_state.player_position[0] + dx
            new_y = self.game_state.player_position[1] + dy
            grid_height = self.game_state.grid_height
            grid_width = self.game_state.grid_width

            if 0 <= new_x < grid_height and 0 <= new_y < grid_width:
                self.game_state.player_position = [new_x, new_y]
                self.game_state.environment_manager.current_location = self.game_state.player_position
                self.game_state.environment_manager.update_environment()
            else:
                print(f"Cannot move {direction.upper()} - out of bounds!")
        else:
            print("Invalid direction!")

    def perform_action(self, action, **kwargs):
        action_method = getattr(self, f"do_{action}", None)
        if callable(action_method):
            action_method(**kwargs)
        else:
            print(f"Action {action} not recognized.")

    def do_search(self):
        self.game_state.search_area()

    def do_pickup(self, item=None):
        if item and not self.state.has_item(item):
            self.state.loot_item(item)
    
    def start_game(self):
            # Display the Main Menu
            self.game_ui.create_and_display_menu('Main_Menu')
        

class GameUI:

    def __init__(self, game_state, config_path):
        self.game_state = game_state
        self.config_path = config_path

    def create_and_display_menu(self, menu_name):
        """
        Menu Types
        1 - gets it's title and description from the GameData JSON file
        2 - gets it's title and description from the name and description of the environment at the current location of the player
        """
        # Load menu data from configuration path
        menu_data = GameUtils.load_data(self.config_path)

        # Check if the specified menu exists in the loaded data
        if menu_name not in menu_data['menus']:
            print(f"{menu_name} not found in the menu data.")
            return None
        
        # Prepare action handlers that correspond to user choices
        action_handlers = self.prepare_action_handlers()

        # Getting the current position of the player and setting the name of the corresponding location to the variable
        # Used so that actual in game menus have their title and description set to the environment's name and description
        environment_name = self.game_state.environment_manager.get_current_location()
        
        # Create the menu using JDDMenuBuilder
        builder = JDDMenuBuilder()
        menu_info = menu_data['menus'][menu_name]
        environment_info = menu_data['environments'][environment_name]

        # This Factory is for type 1 Menus
        if menu_info.get('type') == 1:

            # Clear the Terminal or Console of previous data
            GameUtils.clear_screen()

            builder.set_title(menu_info['title'])
            builder.set_desc(menu_info.get('desc', 'Choose an option below:'))
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n '))

            for option in menu_info['options']:
                action = action_handlers.get(option['action'], lambda: print("Action not available"))
                builder.add_option(option['text'], action)

            menu = builder.build()
            
            # Display the created menu
            menu.display_menu()
            return menu  # Optional return if needed for further handling
        
        elif menu_info.get('type') == 2:

            # Clear the Terminal or Console of previous data
            GameUtils.clear_screen()

            builder.set_title(environment_name)
            builder.set_desc(environment_info.get('description', "No Environment Description\n If you see this I've messed up somewhere."))
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))

            for option in menu_info['options']:
                action = action_handlers.get(option['action'], lambda: print("Action not available"))
                builder.add_option(option['text'], action)

            menu = builder.build()
            
            # Display the created menu
            menu.display_menu()
            return menu  # Optional return if needed for further handling
    
    def prepare_action_handlers(self):
        # Return a dictionary mapping action names to their corresponding methods
        return {
            'leave': (lambda _: self.exit_game()),
            'spawnZone': (lambda _: self.create_and_display_menu('spawnMenu')),
            'spawn_city': lambda _: (self.game_state.environment_manager.spawn_player('city')),
            'spawn_mountain': lambda _: (self.game_state.environment_manager.spawn_player('mountain')),
            'spawn_forest': lambda _: (self.game_state.environment_manager.spawn_player('forest'))
        }
    
    def exit_game(self):
        print("You're an Unsatisfied Adventurer, forever wandering in search of something you'll never find.")
        exit()



class GameUtils:

    @staticmethod
    def load_data(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)

    @staticmethod
    def clear_screen():
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For Unix/Linux/Mac
        else:
            os.system('clear')

    def GoodPrint1(input):
        """
        Making a print function for my game, making printing to the terminal look nicer. 
        """
        for character in input:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)
        print("\n")

    def GoodPrint(*args, sep=' ', end='\n', file=None, flush=False):
        """
        Enhanced print function that provides additional functionality or formatting.

        This function acts similarly to the built-in print function, allowing multiple arguments,
        customizable separators, end characters, file output, and optional flushing of the output buffer.

        Parameters:
        args : multiple arguments that can be of any type.
        sep : str, optional
            The separator between arguments, default is a space.
        end : str, optional
            The character to append at the end of the print, default is newline.
        file : file-like object, optional
            A file-like object to write the message to (defaults to standard output).
        flush : bool, optional
            Whether to forcibly flush the stream.

        Usage:
        GoodPrint("Hello", "world", sep='-', end='!!')
        """
        print(*args, sep=sep, end=end, file=file, flush=flush)


def main():

    # Command for future when running on other computers
    file_path = input("Enter the path to the game configuration file: ")

    try:
        game_state = GameState(filepath=file_path)
        game_engine = GameEngine(game_state=game_state, config_path=file_path)

        game_engine.start_game()

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

