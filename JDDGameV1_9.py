from JDDMenu_v2_6 import * 
import random
import sys
import cmd
import os
import time
import json

class GameState:
    def __init__(self, filepath):
        # Game state initialization, setting the playing grid and loading game managers
        self.grid_width = 9
        self.grid_height = 5
        self.player_position = [1, 1]
        self.environment_manager = self.EnvironmentManager(filepath, self)
        self.player_manager = self.PlayerManager(health=20, inventory=[], quest_log={}, attacks=[])
        self.inventory_manager = self.InventoryManager(inventory=[])
        self.npc_manager = self.NPCManager(filepath)
        self.combat_manager = self.CombatManager(filepath, self)

    class EnvironmentManager:
        def __init__(self, filepath, game_state):
            # Manages game environments, loading data and mapping locations
            self.game_state = game_state  # Store the reference to GameState
            self.data = GameUtils.load_data(filepath)
            # Here environments are mapped by their grid locations for easy access
            self.environments_tuple = {tuple(env['gridLocation']): key for key, env in self.data['environments'].items()}
            self.current_location = [1, 1]  # Initial sync of locations with player_position
            self.location_tuple = tuple(self.current_location)
            self.environment_name = self.environments_tuple.get(self.location_tuple, "")
            self.environment = self.data['environments'].get(str(self.environment_name), None)
            self.encounter_enemy = False

        def printEnv(self):
            """
            print self.environments_tuple for debugging purposes
            """
            print(self.environments_tuple)

        def update_environment(self):
            # Updates the display to show the current environment based on player's location
            if self.location_tuple in self.environments_tuple and self.environment_name in self.environments_tuple:
                print(f"Current Location: {self.environment_name}")
            else:
                print("This area of the map is uncharted.")

        def examine_area(self):
            # Prints searchable information for the current environment
            if self.environment:
                searchable_info = self.environment.get('searchableInfo', 'No information available.')
                print(searchable_info)
            else:
                print("No environment found at the specified location.")

        def search_area(self):
            # Searches the current environment for enemies or loot, engaging in combat or updating inventory
            if self.environment:
                has_enemies = 'enemies' in self.environment and self.environment['enemies']
                has_loot = 'lootPool' in self.environment and self.environment['lootPool']
                if has_enemies or has_loot:
                    if has_enemies and (not has_loot or random.choice(['enemy', 'loot']) == 'enemy'):
                        return "enemy_encounter"
                    elif has_loot:
                        item = random.choice(self.environment['lootPool'])
                        self.environment['lootPool'].remove(item)
                        self.game_state.inventory_manager.add_item(item)
                        return "item_found", item
                else:
                    print("Nothing else found in this area.")
            else:
                print("No environment found at the specified location.")

        def get_current_location(self):
            # Ensure current location is updated each time method is called
            self.location_tuple = tuple(self.current_location)
            self.environment_name = self.environments_tuple.get(self.location_tuple)
            if self.environment_name:
                return self.environment_name
            else:
                # Return a default or handle the case where environment_name is not found
                print("No valid current location found.")
                return None  # or return a default environment name if applicable

        def get_coordinates_for_location(self, location_name):
            # Debugging function used to get coordinates for a location when given a location name
            # Iterate over environments to find matching location name
            for name, env in self.data['environments'].items():
                if name == location_name:
                    return env['gridLocation']
            # If location name not found, return a message indicating invalid location
            return f"No coordinates found for the location: {location_name}"
        
        def log_player_location(self):
            # Debugging Function used to show the current coordinates
            print(f"!Dev Alert! Location = {self.current_location}")

    class PlayerManager:
        def __init__(self, health, inventory, quest_log, attacks):
            # Manages player health, inventory, and quests
            self.health = health
            self.inventory = inventory
            self.quest_log = quest_log
            self.attacks = attacks

        def update_health(self, amount):
            # Updates player's health
            self.health += amount

        def is_defeated(self):
            # Check if the player's health has dropped to zero or below.
            return self.health <= 0

        def update_quest(self, quest_name, status):
            # Updates the status of a quest
            self.quest_log[quest_name] = status
            print(f"Quest '{quest_name}' updated to {status}")

        def learn_attack(self, new_attack):
            # Adds a new attack to the player's arsenal
            self.attacks.append(new_attack)

    class InventoryManager:
        def __init__(self, inventory):
            # Manages the player's inventory
            self.inventory = inventory

        def add_item(self, item):
            # Adds an item to the inventory
            self.inventory.append(item)
            print(f"Added {item} to inventory")

        def remove_item(self, item):
            # Removes an item from the inventory
            if item in self.inventory:
                self.inventory.remove(item)
                print(f"Removed {item} from inventory")

        def has_item(self, item):
            # This just returns an item in the inventory if its in the inventory, I can't remember why I wrote this
            # Leaving this here in case i need it for some reason
            return item in self.inventory
        
    class NPCManager:
        """
        Example usage, will delete later. 
            if player_input == 'talk':
                npc_interaction = game_state.npc_manager.interact_with_npc(game_state.player_position)
                print(npc_interaction)
        """
        def __init__(self, filepath):
            self.npcs = self.load_npcs(filepath)

        def load_npcs(self, filepath):
            # Load NPCs from a JSON file and store them in a dictionary.
            data = GameUtils.load_data(filepath)
            character_data = data['characters']
            npcs = {}
            for name, details in character_data.items():
                # print(details)  # Debug: Check what details contains
                npcs[name] = self.NPC(name, details['description'], details['dialogue'], details.get('quest'), details['gridLocation'])
            return npcs

        def get_npc_by_position(self, gridLocation):
            # Return the NPC at a given position if there's any
            for npc in self.npcs.values():
                if npc.position == gridLocation:
                    return npc
            return None

        def interact_with_npc(self, gridLocation):
            # Facilitate interaction with an NPC based on the player's position
            npc = self.get_npc_by_position(gridLocation)
            if npc:
                return f"Meeting {npc.name}: {npc.speak()}\n{npc.give_quest()}"
            else:
                return "No NPCs here to interact with."

        class NPC:
            def __init__(self, name, description, dialogues, quest, gridLocation):
                self.name = name
                self.description = description
                self.dialogues = dialogues
                self.quest = quest
                self.gridLocation = gridLocation

            def speak(self):
                return random.choice(self.dialogues)

            def give_quest(self):
                if self.quest:
                    return f"{self.name} has given you a quest: {self.quest}"
                else:
                    return f"{self.name} has no quests for you."
                
    class CombatManager:
        def __init__(self, filepath, game_state):
            self.data = GameUtils.load_data(filepath)
            self.attacks = self.data['attacks']
            self.enemies = self.data['enemies']
            self.game_state = game_state
            self.enemy_name = self.choose_enemy()
            enemy = self.enemies[self.enemy_name]
            self.enemy_health = enemy['health']
            self.enemy_attacks = enemy['attacks']
            self.enemy_description = enemy['description']
            self.enemy_handler = self.EnemyHandler(self.enemy_name, self.enemy_health, self.enemy_attacks, self.game_state)

        def choose_enemy(self):
            enemy_name = self.enemy_name = random.choice(self.game_state.environment_manager.environment['enemies'])
            return enemy_name

        def get_attack_damage(self, attack_name):
            # Returns random damage within the range specified for the attack
            attack = self.attacks[attack_name]
            damage = random.randint(attack['damageRange'][0], attack['damageRange'][1])
            return damage, attack
        
        def engage_combat(self, player_attack_choice):
            # Handles a single round of combat between player and enemy based on chosen attacks.
            GameUtils.clear_screen()
            # Display initial encounter
            print(f"You have encountered a {self.enemy_name}: {self.enemy_description}")
            # Player's attack
            player_damage = self.get_attack_damage(player_attack_choice)
            print(f"You use {player_attack_choice}, dealing {player_damage} damage.")
            self.enemy_handler.receive_damage(player_damage)
            if self.enemy_handler.is_defeated():
                    self.enemy_handler.enemy_defeated()
                    return 'player_win'
            
            # Enemy's turn
            damage, enemy_attack = self.enemy_handler.perform_attack()
            print(f"The {self.enemy_name} attacks with {enemy_attack}, dealing {damage} damage.")
            self.game_state.player_manager.update_health(-damage)
            if self.game_state.player_manager.is_defeated():
                return "player_lose"

        def simulate_combat(self):
            """
            This Combat Loop is an optional combat method that simulates and displays the battle to the
            player, randomly chosing moves for the player to execute.
            """
            # Clears Terminal to allow for clean Combat GUI
            GameUtils.clear_screen()
            # Handles a single round of combat between player and enemy based on chosen attacks.
            print(f"> You have encountered a {self.enemy_name}: {self.enemy_description}")
            while not self.game_state.player_manager.is_defeated() and not self.enemy_handler.is_defeated:
                # Player's turn
                player_attack = random.choice(self.game_state.player_manager.attacks)  # Assuming player has a list of possible attacks
                player_damage = self.get_attack_damage(player_attack)
                print(f"\n> You attack with {player_attack} dealing {player_damage} damage.")
                self.enemy_handler.receive_damage(player_damage)
                if self.enemy_handler.is_defeated():
                    self.enemy_handler.enemy_defeated()
                    return 'player_win'
                time.sleep(1.5)

                # Enemy's turn
                damage, enemy_attack = self.enemy_handler.perform_attack()
                print(f"\n> The {self.enemy_name} attacks with {enemy_attack}, dealing {damage} damage.")
                self.game_state.player_manager.update_health(-damage)
                if self.game_state.player_manager.is_defeated():
                    return "player_lose"
                time.sleep(1.5)

        class EnemyHandler:
            def __init__(self, name, health, attacks, game_state):
                self.name = name
                self.health = health
                self.attacks = attacks  # List of attack names with associated damage ranges
                self.game_state = game_state

            def receive_damage(self, damage):
                # Reduce the health of the enemy by the damage amount
                self.health -= damage
                if self.is_defeated():
                    return True  # Enemy is defeated
                return False # Enemy is Alive

            def perform_attack(self):
                # Randomly select an attack and return its name and damage.
                attack = random.choice(self.attacks)
                damage, enemy_attack = self.game_state.combat_manager.get_attack_damage(attack)
                return damage, enemy_attack

            def is_defeated(self):
                # Check if the enemy's health has dropped to zero or below.
                return self.health <= 0
            
            def enemy_defeated(self):
                self.game_state.environment_manager.encounter_enemy = True
                self.game_state.environment_manager.environment['enemies'].remove()

                


class GameEngine:
    def __init__(self, game_state, config_path):
        # Engine to handle player movements and actions
        self.game_state = game_state
        self.config_path = config_path
        self.movements = {
            'n': (0, -1),
            's': (0, 1),
            'e': (1, 0),
            'w': (-1, 0)
        }

    def move(self, direction):
        # Moves the player in the specified direction
        if direction in self.movements:
            dx, dy = self.movements[direction]
            new_x = self.game_state.player_position[0] + dx
            new_y = self.game_state.player_position[1] + dy
            if 0 <= new_x < self.game_state.grid_height and 0 <= new_y < self.game_state.grid_width:
                self.game_state.player_position = [new_x, new_y]
                self.game_state.environment_manager.current_location = self.game_state.player_position
                self.game_state.environment_manager.update_environment()
            else:
                print(f"Cannot move {direction.upper()} - out of bounds!")
        else:
            print("Invalid direction!")

    def spawn_player(self, spawnLocation):
        # Spawns the player at a specified location
        print(f"!Dev Alert! Spawning at location = {spawnLocation}")
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
        # Executes a specified action
        # Again, can't remember why I wrote this, maybe I didn't know what lambda functions were yet.
        # Either way I'm leaving it in just in case.
        action_method = getattr(self, f"do_{action}", None)
        if callable(action_method):
            action_method(**kwargs)
        else:
            print(f"Action {action} not recognized.")

    def print_status(self):
        # Print the current overall status of the player.
        GameUtils.clear_screen()
        self.game_state.environment_manager.update_environment()
        print(f"Health: {self.game_state.player_manager.health}")
        print(f"Inventory: {self.game_state.inventory_manager.inventory}")
        print(f"Quest Log: {self.game_state.player_manager.quest_log}")
        time.sleep(10)

    def do_search(self):
        # Executes the search_area function and then the program sleeps for 5 seconds
        result = self.game_state.environment_manager.search_area()
        if result == 'enemy_encounter':
            self.game_state.environment_manager.encounter_enemy = True
        else:
            pass
        time.sleep(5)

    def do_search_conditional(self): #TODO
        pass

    def do_examine(self):
        # Executes the examine_area function and then the program sleeps for 5 seconds
        self.game_state.environment_manager.examine_area()
        time.sleep(5)

    def do_pickup(self, item=None):
        # Checks if an item is in the inventory already and if not adds it to the inventory
        if item and not self.game_state.inventory_manager.has_item(item):
            self.game_state.inventory_manager.add_item(item)
    
    def exit_game(self):
        # Current 'Unsatisfied Adventurer' ending. 
        print("You're an Unsatisfied Adventurer, forever wandering in search of something you'll never find.")
        exit()
    
class GameUI:
    def __init__(self, game_state, game_engine, config_path):
        # Manages user interface and menus
        self.game_state = game_state
        self.game_engine = game_engine
        self.config_path = config_path

    def create_and_display_menu(self, menu_name):
        """
        Creates and displays menus based on game data and player environment

        Menu Types
        1 - gets it's title and description from the GameData JSON file
            - used for the main menu and the spawn selection menus
        2 - gets it's title and description from the name and description of the environment at the current location of the player
            - used for the main game loop 
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
            GameUtils.clear_screen()
            builder.set_title(menu_info['title'])
            builder.set_desc(menu_info.get('desc', 'Choose an option below:'))
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        # This Factory is for type 2 Menus
        elif menu_info.get('type') == 2:
            GameUtils.clear_screen()
            builder.set_title(environment_name)
            builder.set_desc(environment_info.get('description', "No Environment Description\n If you see this I've messed up somewhere."))
            builder.desc_enabled(True)
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        # This Factory is for type 3 Menus
        elif menu_info.get('type') == 3:
            GameUtils.clear_screen()
            builder.set_title(environment_name)
            builder.desc_enabled(True)
            builder.set_desc(self.game_state.player_position)
            builder.set_prompt(menu_info.get("prompt", 'Select an option to Proceed\n >'))
        # This Factory is for type 4 Menus (Currently Does Not Exist)
        elif menu_info.get('type') == 4:
            builder.set_title('You are in Combat!')
            builder.desc_enabled(True)
            builder.set_desc(f"Brom Crystalind Health: {self.game_state.player_manager.health} | {self.game_state.combat}") #TODO
        # This Factory is for type 5 Menus (Currently Does Not Exist)
        elif menu_info.get('type') == 5:
            pass
        # This Factory is for type 6 Menus (Currently Does Not Exist)
        elif menu_info.get('type') == 6:
            pass
        # Add the options to the menu
        for option in menu_info['options']:
            action = action_handlers.get(option['action'], lambda: print("Action not available"))
            builder.add_option(option['text'], action)
        # Build and Display the created menu
        menu = builder.build()
        menu.display_menu()
        return menu
    
    def prepare_action_handlers(self):
        # Maps user actions to functions. Additionally Contains a dictionary of used conditions
        return {
            'leave': (lambda _: self.game_engine.exit_game()),
            'spawnZone': (lambda _: self.create_and_display_menu('spawnMenu')),
            'spawn_city': lambda _: (self.game_engine.spawn_player('city'), self.create_and_display_menu('gameMenu')),
            'spawn_mountain': lambda _: (self.game_engine.spawn_player('mountain'), self.create_and_display_menu('gameMenu')),
            'spawn_forest': lambda _: (self.game_engine.spawn_player('forest'), self.create_and_display_menu('gameMenu')),
            'move_choice': (lambda _: self.create_and_display_menu('moveMenu')),
            'move_n': lambda _: (self.game_engine.move('n'), self.create_and_display_menu('moveMenu')),
            'move_s': lambda _: (self.game_engine.move('s'), self.create_and_display_menu('moveMenu')),
            'move_e': lambda _: (self.game_engine.move('e'), self.create_and_display_menu('moveMenu')),
            'move_w': lambda _: (self.game_engine.move('w'), self.create_and_display_menu('moveMenu')),
            'backtogame': lambda _: self.create_and_display_menu('gameMenu'),
            'search_area': lambda _: (self.game_engine.do_search()),
            'examine_area': lambda _: (self.game_engine.do_examine(), self.create_and_display_menu('gameMenu')),
            'status': lambda _: (self.game_engine.print_status(), self.create_and_display_menu('gameMenu')),
        }

class GameUtils:
    @staticmethod
    def load_data(filepath):
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: The file {filepath} was not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file {filepath}.")
            return {}
        

    @staticmethod
    def clear_screen():
        # Clears the console screen
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def GoodPrint(input):
        # Prints text to the console with a delay for each character
        # Does not like to work :(
        for character in input:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)
        print("\n")

def main():
    # Main function to start the game
    file_path = '' #file path for when im working on it myself
    #file_path = input("Enter the path to the game configuration file: ") # Command for future when running on other computers

    try:
        game_state = GameState(filepath=file_path)
        game_engine = GameEngine(game_state=game_state, config_path=file_path)
        game_ui = GameUI(game_state, game_engine, config_path=file_path)
        def start_game():
            # Display the Main Menu
            game_ui.create_and_display_menu('Main_Menu')
        start_game()
    except Exception as e:
        raise
if __name__ == "__main__":
    main()

