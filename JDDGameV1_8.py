from JDDMenu_v2_6 import * 
import random
import sys
import cmd
import os
import time
import json

class GameState:

    def __init__(self, filepath):
        self.grid_width = 9
        self.grid_height = 5
        self.player_position = [1,1]
        self.environment_manager = self.EnvironmentManager(filepath, self)
        self.player_manager = self.PlayerManager(health=20, inventory=[], quest_log={})
        self.inventory_manager = self.InventoryManager(inventory=[])


    class EnvironmentManager:
        def __init__(self, filepath, game_state):
            self.game_state = game_state  # Store the reference to GameState
            self.data = GameUtils.load_data(filepath)
            # Here environments are mapped by their grid locations for easy access
            self.environments = {tuple(env['gridLocation']): key for key, env in self.data['environments'].items()}
            self.current_location = [1, 1]  # Initial sync of locations with player_position
            self.environment_data = self.data['environments']


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
                print(f"Current Location: {environment_name}")
            else:
                print("This area of the map is uncharted.")

        def examine_area(self):
            """
            Prints the searchable information for the current environment
            """
            location_tuple = tuple(self.current_location)
            if location_tuple in self.environments:
                # Access the environment by name using the grid location
                environment_name = self.environments[location_tuple]
            location_key = str(environment_name)
            
            # Find the environment by the location
            environment = self.data['environments'].get(location_key, None)
            if environment:
                searchable_info = environment.get('searchableInfo', 'No information available.')
                print(searchable_info)
            else:
                print("No environment found at the specified location.")

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
            location_tuple = tuple(self.current_location)
            environment_name = self.environments.get(location_tuple)
            if environment_name:
                location_key = str(environment_name)  
                environment = self.data['environments'].get(location_key, None)
                if environment:
                    has_enemies = 'enemies' in environment and environment['enemies']
                    has_loot = 'lootPool' in environment and environment['lootPool']
                    if has_enemies or has_loot:
                        if has_enemies and (not has_loot or random.choice(['enemy', 'loot']) == 'enemy'):
                            enemy = random.choice(environment['enemies'])
                            print(f"Encountering enemy: {enemy}")
                            # Placeholder for combat logic
                            pass
                        elif has_loot:
                            item = random.choice(environment['lootPool'])
                            environment['lootPool'].remove(item)
                            self.game_state.inventory_manager.add_item(item)  # Access through game_state
                    else:
                        print("Nothing else found in this area.")
                else:
                    print("No environment found at the specified location.")

        def log_player_location(self):
            print(f"!Dev Alert! Location = {self.current_location}")

    class PlayerManager:

        def __init__(self, health, inventory, quest_log):
            self.health = health
            self.inventory = inventory
            self.quest_log = quest_log

        def update_health(self, amount):
            self.health += amount

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

        def has_item(self, item):
            return item in self.inventory


class GameEngine:

    def __init__(self, game_state, config_path):
        self.game_state = game_state
        self.config_path = config_path
        self.movements = {
            'n': (0, -1),
            's': (0, 1),
            'e': (1, 0),
            'w': (-1, 0)
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

    def spawn_player(self, spawnLocation):
            print(f"!Dev Alert! Spawning at location = {spawnLocation}")  # Debug: Log the input location
            if spawnLocation == 'city':
                self.game_state.player_position = [3,1]
            elif spawnLocation == 'mountain':
                self.game_state.player_position = [2,4]
            elif spawnLocation == 'forest':
                self.game_state.player_position = [1,7]

            self.game_state.environment_manager.current_location = self.game_state.player_position
            self.game_state.environment_manager.update_environment()
            self.game_state.environment_manager.log_player_location()

    def perform_action(self, action, **kwargs):
        action_method = getattr(self, f"do_{action}", None)
        if callable(action_method):
            action_method(**kwargs)
        else:
            print(f"Action {action} not recognized.")

    def print_status(self):
        """Print the current overall status of the player."""
        GameUtils.clear_screen()
        self.game_state.environment_manager.update_environment()
        print(f"Health: {self.game_state.player_manager.health}")
        print(f"Inventory: {self.game_state.inventory_manager.inventory}")
        print(f"Quest Log: {self.game_state.player_manager.quest_log}")
        time.sleep(10)

    def do_search(self):
        self.game_state.environment_manager.search_area()
        time.sleep(5)

    def do_examine(self):
        self.game_state.environment_manager.examine_area()
        time.sleep(5)

    def do_pickup(self, item=None):
        if item and not self.game_state.inventory_manager.has_item(item):
            self.game_state.inventory_manager.add_item(item)
    

        

class GameUI:
    def __init__(self, game_state, game_engine, config_path):
        self.game_state = game_state
        self.game_engine = game_engine
        self.config_path = config_path


    def create_and_display_menu(self, menu_name):
        """
        Menu Types
        1 - gets it's title and description from the GameData JSON file
        2 - gets it's title and description from the name and description of the environment at the current location of the player
        3 - gets it's title from the name of the environment, and it's description from the player's current location
        """
        # Load menu data from configuration path
        game_data = GameUtils.load_data(self.config_path)

        # Check if the specified menu exists in the loaded data
        if menu_name not in game_data['menus']:
            print(f"{menu_name} not found in the menu data.")
            return None
        
        # Prepare action handlers that correspond to user choices
        action_handlers = self.prepare_action_handlers()

        # Getting the current position of the player and setting the name of the corresponding location to the variable
        # Used so that actual in game menus have their title and description set to the environment's name and description
        environment_name = self.game_state.environment_manager.get_current_location()
        
        # Create the menu using JDDMenuBuilder
        builder = JDDMenuBuilder()
        menu_info = game_data['menus'][menu_name]
        environment_info = game_data['environments'][environment_name]

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
        
        # This Factory is for type 2 Menus
        elif menu_info.get('type') == 2:

            # Clear the Terminal or Console of previous data
            GameUtils.clear_screen()

            builder.set_title(environment_name)
            builder.set_desc(environment_info.get('description', "No Environment Description\n If you see this I've messed up somewhere."))
            builder.desc_enabled(True)
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))

            for option in menu_info['options']:
                action = action_handlers.get(option['action'], lambda: print("Action not available"))
                builder.add_option(option['text'], action)

            menu = builder.build()
            
            # Display the created menu
            menu.display_menu()
            return menu  # Optional return if needed for further handling
        
        # This Factory is for type 3 Menus
        elif menu_info.get('type') == 3:

            # Clear the Terminal or Console of previous data
            GameUtils.clear_screen()
            
            builder.set_title(environment_name)
            builder.desc_enabled(True)
            builder.set_desc(self.game_state.player_position)
            builder.set_prompt(menu_info.get("prompt", 'Select an option to Proceed\n >'))

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
            'spawn_city': lambda _: (self.game_engine.spawn_player('city'), self.create_and_display_menu('gameMenu')),
            'spawn_mountain': lambda _: (self.game_engine.spawn_player('mountain'), self.create_and_display_menu('gameMenu')),
            'spawn_forest': lambda _: (self.game_engine.spawn_player('forest'), self.create_and_display_menu('gameMenu')),
            'move_choice': (lambda _: self.create_and_display_menu('moveMenu')),
            'move_n': lambda _: (self.game_engine.move('n'),self.create_and_display_menu('moveMenu')),
            'move_s': lambda _: (self.game_engine.move('s'),self.create_and_display_menu('moveMenu')),
            'move_e': lambda _: (self.game_engine.move('e'),self.create_and_display_menu('moveMenu')),
            'move_w': lambda _: (self.game_engine.move('w'),self.create_and_display_menu('moveMenu')),
            'backtogame': lambda _: self.create_and_display_menu('gameMenu'),
            'search_area': lambda _: (self.game_engine.do_search(), self.create_and_display_menu('gameMenu')),
            'examine_area': lambda _: (self.game_engine.do_examine(), self.create_and_display_menu('gameMenu')),
            'status': lambda _: (self.game_engine.print_status(), self.create_and_display_menu('gameMenu')),
            
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

    def GoodPrint(input):
        """
        Making a print function for my game, making printing to the terminal look nicer. 
        """
        for character in input:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)
        print("\n")


def main():
    #file path for when im working on it myself
    file_path = ''

    # Command for future when running on other computers
    #file_path = input("Enter the path to the game configuration file: ")

    try:
        game_state = GameState(filepath=file_path)
        game_engine = GameEngine(game_state=game_state, config_path=file_path)
        game_ui = GameUI(game_state, game_engine, config_path=file_path)

        def start_game():
            # Display the Main Menu
            game_ui.create_and_display_menu('Main_Menu')
        start_game()

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

