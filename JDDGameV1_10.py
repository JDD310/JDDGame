from JDDMenu_v2_6 import * 
import random
import sys
import cmd
import os
import time
import json

class GameState: 
    EXPLORING = "exploring"
    IN_COMBAT = "in_combat"
    def __init__(self, filepath):
        # Game state initialization, setting the playing grid and loading game managers
        self.current_state = GameState.EXPLORING
        self.grid_width = 9
        self.grid_height = 5
        self.player_position = [0, 0]
        self.filepath = filepath
        self.environment_manager = self.EnvironmentManager(filepath, self)
        self.player_manager = self.PlayerManager(filepath, self)
        self.inventory_manager = self.InventoryManager(inventory=[])
        self.npc_manager = self.NPCManager(filepath)
        self.combat_manager = self.CombatManager(self, filepath)

    class EnvironmentManager:
        def __init__(self, filepath, game_state):
            # Manages game environments, loading data and mapping locations
            self.game_state = game_state  # Store the reference to GameState
            self.data = GameUtils.load_data(filepath)
            self.environments_tuple = {tuple(env['gridLocation']): key for key, env in self.data['environments'].items()}
            self.current_location = [1, 1]  # Initial sync of locations with player_position
            self.environment_name = self.environments_tuple.get(tuple(self.current_location), "")
            self.environment_data = self.data['environments']
            self.current_environment = self.environment_data[self.environment_name]
            self.environment = self.environments_tuple.get(self.environment_name, None)

        def update_environment(self):
            location_tuple = tuple(self.current_location)
            if location_tuple in self.environments_tuple:
                # Access the environment by name using the grid location
                environment_name = self.environments_tuple[location_tuple]
                print(f"Current Location: {environment_name}")
            else:
                print("This area of the map is uncharted.")

        def search_area(self):
            # Searches the current environment for enemies or loot, engaging in combat or updating inventory
            if self.current_environment:
                has_enemies = 'enemies' in self.current_environment and self.current_environment['enemies']
                has_loot = 'lootPool' in self.current_environment and self.current_environment['lootPool']
                if has_enemies or has_loot:
                    if has_enemies and (not has_loot or random.choice(['enemy', 'loot']) == 'enemy'):
                        return "enemy_encounter"
                    elif has_loot:
                        item = random.choice(self.current_environment['lootPool'])
                        self.game_state.inventory_manager.add_item(item)
                        return "item_found", item
                else:
                    print("Nothing else found in this area.")
            else:
                print("No environment found at the specified location.")

        def get_current_location(self):
            # Ensure current location is updated each time method is called
            location_tuple = tuple(self.current_location)
            environment_name = self.environments_tuple.get(location_tuple)
            if environment_name:
                return environment_name
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
        def __init__(self, filepath, game_state):
            # Manages player health, inventory, and quests
            self.game_state = game_state
            self.data = GameUtils.load_data(filepath)
            player_character = self.data["playerCharacter"]
            self.health = player_character["Brom Crystalind"]["health"]
            self.quest_log = player_character.get("quest_log", {})
            self.attacks = player_character["Brom Crystalind"]["attacks"]
                
        def check_all_quests(self):
            characters = self.data.get('characters', {})
            all_complete = True
            for char_name, char_details in characters.items():
                quest = char_details.get('quest', {})
                if quest.get('status', 'incomplete') != 'complete':
                    all_complete = False
                    break
            
            if all_complete:
                print("Congratulations! All quests are complete. You have won the game!\n 'Respected Individual'")
            else:
                print("Some quests are still incomplete.")

        def update_health(self, amount):
            # Updates player's health
            self.health += amount

        def one_above_all(self):
            if self.game_state.inventory_manager.has_item('Aincent Tome') and self.game_state.inventory_manager.has_item('Aincent Sword') and self.game_state.inventory_manager.has_item('Aincent Shield'):
                self.game_state.combat_manager.Final_combat()

        def is_defeated(self):
            # Check if the player's health has dropped to zero or below.
            return self.health <= 0

        def defeat(self):
            if self.is_defeated():
                print("You Died. The End.")
                exit()

        def update_quest(self, quest_name, status):
            # Updates the status of a quest
            self.quest_log[quest_name] = status
            print(f"Quest '{quest_name}' updated to {status}")
            self.check_all_quests()

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
        def __init__(self, game_state, filepath):
            self.filepath = filepath
            self.game_state = game_state
            self.enemies = self.load_combat_data('enemies')  # Load enemies
            self.attacks = self.load_combat_data('attacks')  # Load attacks
            self.player_info = self.load_combat_data('playerCharacter')
            self.player_char = self.player_info['Brom Crystalind']

        def load_combat_data(self, key):
            try:
                with open(self.filepath, 'r') as file:
                    data = json.load(file)
                    return data.get(key, {})
            except Exception as e:
                print(f"Failed to load {key} data: {e}")
                return {}

        def choose_enemy(self):
            current_env = self.game_state.environment_manager.current_environment
            if not current_env or 'enemies' not in current_env:
                print("No enemies available in this environment.")
                return None, None
            enemy_name = random.choice(current_env['enemies'])
            enemy_info = self.enemies.get(enemy_name, {})
            if not enemy_info:
                print(f"Enemy data for {enemy_name} not found.")
                return None, None
            print(f"You have encountered a {enemy_name}: {enemy_info.get('description', 'No description available.')}")
            return enemy_name, enemy_info

        def get_attack_damage(self, attack_name):
            attack = self.attacks.get(attack_name, {})
            damage = random.randint(attack.get('damageRange', [0, 0])[0], attack.get('damageRange', [0, 0])[1])
            return damage

        def player_turn(self, enemy_info):
            print("\nYour turn!")
            player_attack = random.choice(self.player_char['attacks'])
            damage = self.get_attack_damage(player_attack)
            enemy_info['health'] -= damage
            print(f"You attack with {player_attack} ({self.attacks[player_attack]['description']}), dealing {damage} damage.")

        def enemy_turn(self, enemy_info):
            if enemy_info['health'] > 0:
                print("\nEnemy's turn!")
                enemy_attack = random.choice(enemy_info['attacks'])
                damage = self.get_attack_damage(enemy_attack)
                self.game_state.player_manager.health -= damage
                print(f"The {enemy_info['name']} attacks with {enemy_attack} ({self.attacks[enemy_attack]['description']}), dealing {damage} damage.")

        def combat(self):
            self.game_state.current_state = GameState.IN_COMBAT
            enemy_name, enemy_info = self.choose_enemy()
            if not enemy_info:
                print("No enemy to fight.")
                return
            while self.game_state.player_manager.health > 0 and enemy_info['health'] > 0:
                self.player_turn(enemy_info)
                if enemy_info['health'] <= 0:
                    print(f"\nYou have defeated the {enemy_name}!")
                    self.game_state.current_state = GameState.EXPLORING
                    return True
                time.sleep(3)
                self.enemy_turn(enemy_info)
                if self.game_state.player_manager.is_defeated():
                    print("\nYou have been defeated!")
                    self.game_state.current_state = GameState.EXPLORING
                    return False
                time.sleep(3)

        def Final_combat(self):
            self.game_state.current_state = GameState.IN_COMBAT
            final_boss = self.enemies['The End']
            while self.game_state.player_manager.health > 0 and final_boss['health'] > 0:
                self.player_turn(final_boss)
                if final_boss['health'] <= 0:
                    print(f"\nYou have defeated The End!\n You Have Acheived the Hardest, Most Secret Ending!")
                    exit()
                time.sleep(0.1)
                self.enemy_turn(final_boss)
                if self.game_state.player_manager.is_defeated():
                    print("\nYou have been defeated by The End!!")
                    self.game_state.player_manager.defeat()
                time.sleep(0.1)

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
        # Executes the search_area function 
        result = self.game_state.environment_manager.search_area()
        if result == 'enemy_encounter':
            self.game_state.combat_manager.combat()

    def do_examine(self):
        # Executes the examine_area function and then the program sleeps for 5 seconds
        self.game_state.environment_manager.examine_area()

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
        if self.game_state.current_state != GameState.EXPLORING:
            return  # Avoid displaying the menu if not exploring
        game_data = GameUtils.load_data(self.config_path)
        environment_name = self.game_state.environment_manager.get_current_location()
        if environment_name is None:
            print("Error: Current location is invalid or not found in environments.")
            return
        if menu_name not in game_data['menus']:
            print(f"{menu_name} not found in the menu data.")
            return None
        menu_info = game_data['menus'][menu_name]
        environment_info = game_data['environments'].get(environment_name, {})

        if not environment_info:
            print(f"No information available for environment '{environment_name}'.")
            return
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
            
            builder.set_title(menu_info['title'])
            builder.set_desc(menu_info.get('desc', 'Choose an option below:'))
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        # This Factory is for type 2 Menus
        elif menu_info.get('type') == 2:
            
            builder.set_title(environment_name)
            builder.set_desc(environment_info.get('description', "No Environment Description\n If you see this I've messed up somewhere."))
            builder.desc_enabled(True)
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        # This Factory is for type 3 Menus
        elif menu_info.get('type') == 3:
            
            builder.set_title(environment_name)
            builder.desc_enabled(True)
            builder.set_desc(self.game_state.player_position)
            builder.set_prompt(menu_info.get("prompt", 'Select an option to Proceed\n >'))
        # This Factory is for type 4 Menus (Currently Does Not Exist)
        elif menu_info.get('type') == 4:
            pass
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

