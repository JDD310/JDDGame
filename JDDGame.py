from JDDMenu_v2_6 import * 
import random
import sys
import os
import time
import json

"""
Instructions for use:
    - Change the file path in main() to the file path to your copy of the GameData.JSON file
    - Make sure JDDMenu_v2_6 is in the same file as your Copy of the Game so that it can be easily imported.

    - Please email jdd310@gmail.com with the subject line "JDDGame_Bug" if you find any bugs.

    Goals For Future of this Project
    ----------------------------------

    Uncompleted Goals - Marked with #TODO or #subTODO
    Work in Progress Goals - Marked with #WIP
    Completed Goals - Marked with #DONE

        DONE Upload to Github
        TODO Port to Java
            * I want to do this for two reasons, I need to learn java and this is a perfect way to do it, and 
              porting to java could help make this easier to work on, because i actually have access to real object oriented
              programming instead of just kind of bastardizing it which is what i feel like i've been doing so far. 
        TODO Impliment Save States. 
            * I want a player to be able to save their game state to the machine, and be able to load it at any time. 
            * Implimenting auto-saving would probably be too much, but doing it manually could help me a lot.
        TODO Combat Overhaul 
            * There are a couple of things i want to do to combat, they will each have their own todo under this banner.
            subTODO Make combat player controled
                #NOTE Will need to create a new menu for this.
                * The player should be able to control combat as opposed to currently where it is done automatically
                  by the program; Classic RPG options should work.
                subTODO Allow players to attempt to run from combat
                    * Similar to pokemon players should be able to run from combat if the enemy 
                      is too strong. May end up removing this if save states are properly implimented
                subTODO Allow Players to Heal during their turn in combat using items
                    * Items need more use. this is a natural progression, and will also make the game more enjoyable.
            subTODO Add the ability to learn new moves
                * Shouldn't be too hard, iirc i already have the framework, or at least ideas. will have to check.
            subTODO Add EXP Values to Enemies depending on their stregnth
                * Enemies should drop exp when killed.
            subTODO make the moves avalable to the player in combat change based on current build
                * Might not do this, it would be cool but it seems like a gargantuan ammount of work
        TODO Item Overhaul
            subTODO Need to add an equipment system
                * I want the player to be able to get stronger, not just by learning new moves but by getting items.
            subTODO Add a shop for players to spend gold and sell items
                #LEARN Will need to figure this out.
                * I have no idea where to start with this but I think it would be neat.
            subTODO Crafting System.
                * Self Explanatory. Player should be able to 
            subTODO Add/Remove Items
                * Go over items and add/remove based on need and importance to game
        TODO Environmental Overhaul
            subTODO Expand map
                * with all of these new additions i'm going to need a bigger map. really as big as i can get it, i might
                even write a program to help with this. 
            #NOTE I may end up locking parts of the map behind level barriers.
                * This would decrease freedom, but possibly result in a more fun end experience because the 
                  player would not accidentally wander into areas that have enemies far stronger than they are. 
            subTODO Fix/Expand Quest System
                * IIRC i wasn't very happy with how the quest system turned out, it needs to be done better.
            subTODO NPCS
                * With the planned changes, there needs to be more NPCS.
                * i also need to probably work on the existing ones. 
        TODO Player Character Overhaul
            * Player needs development to allow for more freedom for the user
            subTODO Add ability for player to name their own Character
                * Self Explanatory, Would be nice for people to be able to play as any character they want.
            subTODO Add Leveling System
                * The player should be able to level up as they progress through the game.
                * Health should be the most basic increase that goes up as leveling does, but i
                  may impliment moves getting stronger as well. i'll have to determine if that is a 
                  viable option before true implimentation.
            subTODO Add a way for the player to use items while not in combat
                * Can't remember if players heal after battle but if they don't i need to add a way for players to heal
                after battles, similar to pokemon
                #NOTE Will require addition to menu

        TODO Add Graphics
            * This is in the last spot because I am genuinely conflicted on wether or not to do it
              it would probably be the most difficult thing on this list, only because i genuinely have no idea
              where to even start.
            #NOTE Shelving this idea until everything else is done, because its such a huge undertaking.
            subTODO Add graphical interface for program
                * Even if i dont add full graphics, an interface for the program to run out of instead of just the
                  terminal would probably help a lot for the user's end experience. 
"""

class GameState: 
    EXPLORING = "exploring"
    IN_COMBAT = "in_combat"
    princess_defeated = False
    def __init__(self, filepath):
        #COMMENT Game state initialization, setting the playing grid and loading game managers
        self.current_state = GameState.EXPLORING
        self.grid_width = 9
        self.grid_height = 5
        self.player_position = [0, 0]
        self.filepath = filepath
        self.environment_manager = self.EnvironmentManager(filepath, self)
        self.player_manager = self.PlayerManager(filepath, self)
        self.inventory_manager = self.InventoryManager(inventory=[])
        self.npc_manager = self.NPCManager(self, filepath)
        self.combat_manager = self.CombatManager(self, filepath)

    class EnvironmentManager:
        def __init__(self, filepath, game_state):
            self.game_state = game_state
            self.data = GameUtils.load_data(filepath)
            #COMMENT Ensure environments data exists and is correctly formatted
            if 'environments' not in self.data or not isinstance(self.data['environments'], dict):
                print("Environments data is missing or corrupt.")
                self.data['environments'] = {}
            #COMMENT Map grid locations to environment names
            self.environments_tuple = {tuple(env['gridLocation']): key for key, env in self.data['environments'].items()}
            self.current_location = [0, 0]  # Initial sync of locations with player_position
            self.update_environment()

        def update_environment(self):
            #COMMENT Update the current environment based on player location
            location_tuple = tuple(self.current_location)
            self.environment_name = self.environments_tuple.get(location_tuple, "")
            #COMMENT Safely access the environment data
            self.current_environment = self.data['environments'].get(self.environment_name, {})
            if self.current_environment:
                print(f"Current Location: {self.environment_name}")
            else:
                print("This area of the map is uncharted.")

        def examine_area(self):
            #COMMENT Print searchable information if available
            if self.current_environment:
                searchable_info = self.current_environment.get('searchableInfo', 'No information available.')
                print(f">>{searchable_info}")
            else:
                print("No environment found at the specified location.")
    

        def search_area(self):
            #COMMENT Searches the current environment for enemies or loot, engaging in combat or updating inventory
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
            #COMMENT Ensure current location is updated each time method is called
            location_tuple = tuple(self.current_location)
            environment_name = self.environments_tuple.get(location_tuple)
            if environment_name:
                return environment_name
            else:
                #COMMENT Return a default or handle the case where environment_name is not found
                print("No valid current location found.")
                return None  #COMMENT or return a default environment name if applicable

        def get_coordinates_for_location(self, location_name):
            #COMMENT Debugging function used to get coordinates for a location when given a location name
            #COMMENT Iterate over environments to find matching location name
            for name, env in self.data['environments'].items():
                if name == location_name:
                    return env['gridLocation']
            #COMMENT If location name not found, return a message indicating invalid location
            return f"No coordinates found for the location: {location_name}"
        
        def log_player_location(self):
            #COMMENT Debugging Function used to show the current coordinates
            print(f"!Dev Alert! Location = {self.current_location}")

    class PlayerManager:
        quests_complete = 0

        def __init__(self, filepath, game_state):
            #COMMENT Manages player health, inventory, and quests
            self.game_state = game_state
            self.data = GameUtils.load_data(filepath)
            self.health = 100
            self.quest_log = {}
            self.attacks = ["Atomic Flame"]#["Sword Slash","Sword Slash+","Dagger Slash","Dagger Slash+","Fireball","Water Ball","Air Palm","Mean Elbow"]

        def update_health(self, amount):
            #COMMENT Updates player's health
            self.health += amount

        def player_win(self, enemy_name):
            #COMMENT Updating quests based upon certain Battle Outcomes
            if enemy_name == "Dragon":
                self.update_quest("Slay the Dragon", "Complete")
            elif enemy_name == "Necromancer":
                self.update_quest("Slay the Necromancer", "Complete")
            elif enemy_name == "Boss Bandit":
                self.update_quest("Slay the Boss of the Bandits", "Complete")
            elif enemy_name == "King of the Forest":
                self.update_quest("Slay the King of the Forest", "Complete")
            elif enemy_name == "Sandra Baylent":
                GameState.princess_defeated = True
                self.update_quest("Talk to Princess Sandra", "Incomplete")

        def is_defeated(self):
            #COMMENT Check if the player's health has dropped to zero or below.
            return self.health <= 0

        def update_quest(self, quest_name, status):
            #COMMENT Updates the status of a quest
            self.quest_log[quest_name] = status
            print(f"Quest '{quest_name}' updated to {status}")
            if status == 'Complete':
                self.quests_complete += 1
            GameEngine.respected_individual(self)
            time.sleep(5)

        def learn_attack(self, new_attack):
            #COMMENT Adds a new attack to the player's arsenal
            self.attacks.append(new_attack)

    class InventoryManager:
        
        def __init__(self, inventory):
            #COMMENT Manages the player's inventory
            self.inventory = inventory

        def add_item(self, item):
            #COMMENT Adds an item to the inventory
            self.inventory.append(item)
            print(f"Added {item} to inventory")

        def remove_item(self, item):
            #COMMENT Removes an item from the inventory
            if item in self.inventory:
                self.inventory.remove(item)
                print(f"Removed {item} from inventory")

        def has_item(self, item):
            #COMMENT This just returns an item in the inventory if its in the inventory, I can't remember why I wrote this
            #NOTE Leaving this here in case i need it for some reason
            return item in self.inventory
        
    class NPCManager:
        #COMMENT remainders from a feature I did not get to impliment. Ran out of time.
        times_talked_osiris = 0 
        times_talked_princess = 0
        times_talked_irons = 0 
        times_talked_erynn = 0 
        times_talked_james = 0 

        def __init__(self, game_state, filepath):
            self.game_state = game_state
            self.npcs = self.load_npcs(filepath)
            self.filepath = filepath
            
        def load_npcs(self,filepath):
            #COMMENT Load NPCs from a JSON file and store them in a dictionary.
            data = GameUtils.load_data(filepath)
            character_data = data['characters']
            npcs = {}
            for name, details in character_data.items():
                #COMMENT print(details)  # Debug: Check what details contains
                npcs[name] = self.NPC(name, details['description'], details['dialogue'], details['quest_dialogue'], details.get('quest'), details['gridLocation'], self.game_state)
            return npcs

        def get_npc_by_position(self, gridLocation):
            #COMMENT Return the NPC at a given position if there's any
            for npc in self.npcs.values():
                if npc.gridLocation == gridLocation:
                    return npc
            return None

        def intro_to_npc(self, gridLocation):
            #COMMENT Facilitate interaction with an NPC based on the player's position
            npc = self.get_npc_by_position(gridLocation)
            if npc:
                return f"{npc.name}: {npc.description}"

        def interact_with_npc(self, gridLocation):
            #COMMENT Facilitate interaction with an NPC based on the player's position
            npc = self.get_npc_by_position(gridLocation)
            speak_type = random.randint(0,3)
            #COMMENT Just Speaking Random Dialogue Options to the Player specifically for sandra after fight
            if npc and npc.name == 'Sandra Baylent' and self.game_state.princess_defeated == True and speak_type != 3 and not "Talk to Princess Sandra" in self.game_state.player_manager.quest_log:
                GameUtils.clear_screen()
                print(f">>{npc.name}: {npc.speak()}")
                time.sleep(3.33)
                GameUtils.clear_screen()
            #COMMENT Speaking Specific quest dialogue to the player specifically for sandra after fight
            elif npc and npc.name == 'Sandra Baylent' and self.game_state.princess_defeated == True and speak_type == 3 and not "Talk to Princess Sandra" in self.game_state.player_manager.quest_log:
                GameUtils.clear_screen()
                print(f">>{npc.name}: {npc.quest_dialogue}\n{npc.give_quest()}")
                self.game_state.player_manager.update_quest("Talk to Princess Sandra", "Complete")
                time.sleep(15)
                GameUtils.clear_screen()
            elif npc and npc.name == 'Sandra Baylent' and self.game_state.princess_defeated == True and "Run away with Princess Sandra?" in self.game_state.player_manager.quest_log:
                GameUtils.clear_screen()
                GameUI(game_state=self.game_state, game_engine=GameEngine(game_state=self.game_state, config_path=self.filepath),config_path=self.filepath).create_and_display_menu('sandra')
            #COMMENT Specific condition for sandra for before you fight her.
            elif npc and npc.name == 'Sandra Baylent' and self.game_state.princess_defeated == False:
                GameUtils.clear_screen()
                print(">>You're stopped by the guards before you get to the princess")
                GameUtils.clear_screen()
            #COMMENT Just Speaking Random Dialogue Options to the Player
            elif npc and speak_type != 3:
                GameUtils.clear_screen()
                print(f">>{npc.name}: {npc.speak()}")
                time.sleep(3.33)
                GameUtils.clear_screen()
            #COMMENT Speaking Specific quest dialogue to the player
            elif npc and speak_type == 3:
                GameUtils.clear_screen()
                print(f">>{npc.name}: {npc.quest_dialogue}\n{npc.give_quest()}")
                time.sleep(10)
                GameUtils.clear_screen()
            

        class NPC:
            def __init__(self, name, description, dialogues, quest_dialogue, quest, gridLocation, game_state):
                self.name = name
                self.description = description
                self.dialogues = dialogues
                self.quest_dialogue = quest_dialogue
                self.quest = quest
                self.gridLocation = gridLocation
                self.game_state = game_state
                self.times_spoken = 0 

            def speak(self):
                return random.choice(self.dialogues)


            def give_quest(self):
                if self.quest:
                    self.game_state.player_manager.update_quest(self.quest, "Incomplete")
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
            print(f">>You attack with {player_attack} ({self.attacks[player_attack]['description']}), dealing {damage} damage.")

        def enemy_turn(self, enemy_info):
            if enemy_info['health'] > 0:
                print("\nEnemy's turn!")
                enemy_attack = random.choice(enemy_info['attacks'])
                damage = self.get_attack_damage(enemy_attack)
                self.game_state.player_manager.update_health(-damage)
                print(f">>The {enemy_info['name']} attacks with {enemy_attack} ({self.attacks[enemy_attack]['description']}), dealing {damage} damage.")

        def combat(self):
            self.game_state.current_state = GameState.IN_COMBAT
            enemy_name, enemy_info = self.choose_enemy()
            if not enemy_info:
                print("No enemy to fight.")
                return
            while self.game_state.player_manager.health > 0 and enemy_info['health'] > 0:
                self.player_turn(enemy_info)
                if enemy_info['health'] <= 0:
                    print(f">>\nYou have defeated the {enemy_name}!")
                    self.game_state.player_manager.player_win(enemy_name)
                    self.game_state.current_state = GameState.EXPLORING
                    return True
                time.sleep(3)
                self.enemy_turn(enemy_info)
                if self.game_state.player_manager.is_defeated():
                    GameEngine.defeat(self)
                    self.game_state.current_state = GameState.EXPLORING
                    return False
                time.sleep(3)

        def Final_combat(self):
            self.game_state.current_state = GameState.IN_COMBAT
            final_boss = self.enemies['The End']
            while self.game_state.player_manager.health > 0 and final_boss['health'] > 0:
                self.player_turn(final_boss)
                if final_boss['health'] <= 0:
                    print(f"\nYou have defeated The End!\nYou Have Acheived the Hardest, Most Secret Ending!")
                    exit()
                time.sleep(0.1)
                self.enemy_turn(final_boss)
                if self.game_state.player_manager.is_defeated():
                    print("\nYou have been defeated by The End!!")
                    self.game_state.player_manager.defeat()
                time.sleep(0.1)

class GameEngine:
    def __init__(self, game_state, config_path):
        #COMMENT Engine to handle player movements and actions
        self.game_state = game_state
        self.config_path = config_path
        self.movements = {
            'n': (0, -1),
            's': (0, 1),
            'e': (1, 0),
            'w': (-1, 0)
        }

    def move(self, direction):
        #COMMENT Moves the player in the specified direction
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
        #COMMENT Spawns the player at a specified location
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
        #COMMENT Executes a specified action
        #NOTE: Again, can't remember why I wrote this, maybe I didn't know what lambda functions were yet.
        #NOTE Either way I'm leaving it in just in case.
        action_method = getattr(self, f"do_{action}", None)
        if callable(action_method):
            action_method(**kwargs)
        else:
            print(f"Action {action} not recognized.")

    def print_status(self):
        #COMMENT Print the current overall status of the player.
        GameUtils.clear_screen()
        self.game_state.environment_manager.update_environment()
        print(f"Health: {self.game_state.player_manager.health}")
        print(f"Inventory: {self.game_state.inventory_manager.inventory}")
        print(f"Quest Log: {self.game_state.player_manager.quest_log}")
        time.sleep(10)

    def do_search(self):
        #COMMENT Executes the search_area function 
        GameUtils.clear_screen()
        result = self.game_state.environment_manager.search_area()
        if result == 'enemy_encounter':
            self.game_state.combat_manager.combat()
        time.sleep(4)
        GameUtils.clear_screen()


    def do_examine(self):
        #COMMENT Executes the examine_area function and then the program sleeps for 6 seconds
        GameUtils.clear_screen()
        self.game_state.environment_manager.examine_area()
        time.sleep(6)
        GameUtils.clear_screen()

    def do_pickup(self, item=None):
        #COMMENT Checks if an item is in the inventory already and if not adds it to the inventory
        if item and not self.game_state.inventory_manager.has_item(item):
            self.game_state.inventory_manager.add_item(item)

    def exit_game(self):
        #COMMENT Exits the game.
        exit()

    #NOTE Below are 4/5 endings the last one is secret and only triggered when a certain condition is met
    def respected_individual(self):
        #COMMENT The Respected Individual ending.
        if self.game_state.player_manager.quests_complete == 4:
            print("Congratulations! All character quests are complete. You have won the game!\n\
            You retire happily to a small village in the countryside of the Baylent Kingdom.\n\
            You live out the rest of your life as a well respected elder and a paragon of the community.\n\
            'Respected Individual'")
            exit()
        else:
            print("Some quests are still incomplete.")

    def defeat(self):
        #COMMENT The Death Ending
        if self.game_state.player_manager.is_defeated():
            print("You Died. The End.\n\
                  'Death'")
            exit()
    
    def HWHL(self):
        #COMMENT The Happy Wife Happy Life ending.
        self.game_state.current_state = GameState.IN_COMBAT
        print('You take the princess by the hand and leave the kingdom.')
        time.sleep(1.5)
        print('You Adventure together for many years, together evading attempts to return the princess to the kingdom.')
        time.sleep(1.5)
        print('Eventually you fall in love.')
        time.sleep(1.5)
        print('You eventually work up the courage to ask her to marry you')
        time.sleep(1.5)
        print('You Marry the Princess and Retire Happily in the Magical Forest, Satisfied with your life')
        time.sleep(3)
        print("'Happy Wife Happy Life'")
        exit()

    def unsatisfied(self):
        #COMMENT The Unsatisfied Adventurer ending. 
        print("You're an Unsatisfied Adventurer, forever wandering in search of something you'll never find.\n\
              'Unsatisfied Adventurer'")
        exit()

    
    
class GameUI:
    def __init__(self, game_state, game_engine, config_path):
        #COMMENT Manages user interface and menus
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
            return  #BUGFIX Avoid displaying the menu if not exploring
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
        #COMMENT Prepare action handlers that correspond to user choices
        action_handlers = self.prepare_action_handlers()
        #COMMENT Getting the current position of the player and setting the name of the corresponding location to the variable
        #NOTE Used so that actual in game menus have their title and description set to the environment's name and description
        environment_name = self.game_state.environment_manager.get_current_location()
        #COMMENT Create the menu using JDDMenuBuilder
        builder = JDDMenuBuilder()
        menu_info = game_data['menus'][menu_name]
        environment_info = game_data['environments'][environment_name]
        #NOTE This Factory is for type 1 Menus
        if menu_info.get('type') == 1:
            GameUtils.clear_screen()
            builder.set_title(menu_info['title'])
            builder.set_desc(menu_info.get('desc', 'Choose an option below:'))
            builder.desc_enabled(True)
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        #NOTE This Factory is for type 2 Menus for Environments with NPCs
        elif menu_info.get('type') == 2 and environment_info.get('has_npc', 'no') == 'no':
            GameUtils.clear_screen()
            builder.set_title(environment_name)
            builder.set_desc(environment_info.get('description', "No Environment Description If you see this I've messed up somewhere."))
            builder.desc_enabled(True)
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        #NOTE This Factory is for type 2 Menus for Environments with NPCs
        elif menu_info.get('type') == 2 and environment_info.get('has_npc', 'no') == 'yes':
            GameUtils.clear_screen()
            npc = self.game_state.npc_manager.get_npc_by_position(self.game_state.player_position)
            builder.set_title(environment_name)
            builder.set_desc(f"{environment_info.get('description', 'No Environment Description If you see this I have messed up somewhere.')}""\nNPCs at your current location:"f"\n{self.game_state.npc_manager.intro_to_npc(self.game_state.player_position)}")
            builder.desc_enabled(True)
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
            builder.add_option(f"Talk to {npc.name}", lambda _: (self.game_state.npc_manager.interact_with_npc(self.game_state.player_position)))
        #NOTE This Factory is for type 3 Menus, AKA The Move Menu
        #COMMENT Has an If Statement that serves as the trigger for the secret ending option, if the conditions are met
        elif menu_info.get('type') == 3:
            GameUtils.clear_screen()
            builder.set_title(environment_name)
            builder.desc_enabled(True)
            builder.set_desc(self.game_state.player_position)
            builder.set_prompt(menu_info.get("prompt", 'Select an option to Proceed\n >'))
            #USEFUL Secret 'One Above All' Ending Trigger
            if self.game_state.inventory_manager.has_item('Aincent Tome') and self.game_state.inventory_manager.has_item('Aincent Sword') and self.game_state.inventory_manager.has_item('Aincent Shield'):
                builder.add_option("go to The End.", 'finale')
        #NOTE This Factory is for type 4 Menus (Currently Does Not Exist)
        if menu_info.get('type') == 4:
            GameUtils.clear_screen()
            builder.set_title(menu_info['title'])
            builder.set_prompt(menu_info.get('prompt', 'Select an option to Proceed\n >'))
        #NOTE This Factory is for type 5 Menus (Currently Does Not Exist)
        elif menu_info.get('type') == 5:
            GameUtils.clear_screen()
            pass
        #NOTE This Factory is for type 6 Menus (Currently Does Not Exist)
        elif menu_info.get('type') == 6:
            GameUtils.clear_screen()
            pass
        #COMMENT Add the options to the menu
        for option in menu_info['options']:
            action = action_handlers.get(option['action'], lambda: print("Action not available"))
            builder.add_option(option['text'], action)
        #COMMENT Build and Display the created menu
        menu = builder.build()
        menu.display_menu()
        return menu
    
    

    def prepare_action_handlers(self):
        #COMMENT Maps user actions to functions. Additionally Contains a dictionary of used conditions
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
            'talkNPC': lambda _: (self.npc_manager.interact_with_npc(self.game_state.player_position)),
            'end_game': lambda _: self.game_engine.unsatisfied(),
            'finale': lambda _: self.game_state.combat_manager.Final_combat(),
            'runaway': lambda _: self.game_engine.HWHL(),
            'nope': lambda _: (self.game_state.player_manager.update_quest('Run away with Princess Sandra?', 'Complete'), self.create_and_display_menu('moveMenu'))
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
        #COMMENT Clears the console screen
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def GoodPrint(input):
        #COMMENT Prints text to the console with a delay for each character
        #NOTE Does not like to work :(
        for character in input:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(0.05)
        print("\n")

def main():
    #COMMENT Main function to start the game

    #COMMENT Input file path to the gamedata file manually 
    #USEFUL THIS IS HIGHLY RECOMMENDED
    file_path = '' 
    #COMMENT Un-Comment to use, Enter File path on each run # NOT RECOMMENDED
    #file_path = input("Enter the path to the game configuration file: ") 

    try:
        game_state = GameState(filepath=file_path)
        game_engine = GameEngine(game_state=game_state, config_path=file_path)
        game_ui = GameUI(game_state=game_state, game_engine=game_engine, config_path=file_path)
        def start_game():
            #COMMENT Display the Main Menu
            game_ui.create_and_display_menu('Main_Menu')
        start_game()
    except Exception as e:
        raise
if __name__ == "__main__":
    main()