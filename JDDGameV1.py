from JDDMenu_v2_5 import * 
import random
import sys
import cmd
import os
import time
import json

#TODO fix lmao im tired
class GameState:

    def __init__(self, filepath='GameMenus.json'):
        with open(filepath, 'r') as file:
            self.environments = json.load(file)
        self.current_location = "Limbo"
        self.inventory = []
        self.quest_log = {}
        self.health = 20

    def has_item(self, item):
        """Check if the player has a specific item in their inventory."""
        return item in self.inventory
    
    #TODO
    def has_looted(self, looted_area):
        """Check if the player has already looted the current area"""
        return self.looted_area == looted_area

    def is_at_location(self, location):
        """Check if the player is at a specific location."""
        return self.current_location == location

    def move_to_location(self, location):
        """Move the player to a new location."""
        self.current_location = location
        print(f"Moved to {location}")

    """
    TODO Fix the search_area function to allow searching the same environment/area multiple times. also need to add a element 
        of randomness on each search, making it so that each time you search an area there is a chance of a enemy appearing, 
        silimar to grass in the pokemon games. 

        I may add multiple duplicates of items for every area, and potentially add a enemy cap for each area so that extremely
        unlucky players would not have to fight enemies over and over and over again.
    """
    def search_area(self):
        """Allow the player to search the current area for clues and items."""
        area = self.environments[self.current_location]
        if not area["searched"]:
            print(area["searchableInfo"])
            item = random.choice(area["lootPool"])
            self.loot_item(item)
            area["searched"] = True
        else:
            print("You have already searched this area thoroughly.")

    def loot_item(self, item):
        """Add an item to the player's inventory."""
        self.inventory.append(item)
        print(f"{item} added to inventory")

    def update_quest(self, quest_name, status):
        """Update the status of a quest."""
        self.quest_log[quest_name] = status
        print(f"Quest '{quest_name}' updated to {status}")

    def print_status(self):
        """Print the current overall status of the player."""
        print(f"Current Location: {self.current_location}")
        print(f"Health: {self.health}")
        print(f"Inventory: {self.inventory}")
        print(f"Quest Log: {self.quest_log}")

#TODO Fix and define more actions for the player to take, i want this game to be very very cool. 
class GameEngine:

    def __init__(self, state):
        self.state = state

    def perform_action(self, action, **kwargs):
        action_method = getattr(self, f"do_{action}", None)
        if callable(action_method):
            action_method(**kwargs)
        else:
            print(f"Action {action} not recognized.")

    def do_move(self, location=None):
        if location and not self.state.is_at_location(location):
            self.state.move_to_location(location)
            print(f"Arrived at {location}.")
        else:
            print("You are already here.")

    def do_search(self):
        self.state.search_area()

    def do_pickup(self, item=None):
        if item and not self.state.has_item(item):
            self.state.loot_item(item)

class DataHandling:

    def load_menus(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data["menus"]
    
    def load_environments(filepath):
            with open(filepath, 'r') as file:
                data = json.load(file)
            return data["environments"]

    def load_environments(filepath):
        with open(filepath, 'r') as file:
            data = json.load(file)
        return data["environments"]

#TODO Fix menus to read JSON file instead of Modular style menus like shown here
class GameUI:

    def __init__(self, game_state, game_engine):
        self.game_state = game_state
        self.game_engine = game_engine

    def load_menu(self):
        current_env = self.game_state.environments[self.game_state.current_location]
        builder = JDDMenuBuilder()
        builder.set_title(f"Exploring {self.game_state.current_location}")
        builder.add_option("Search the area", lambda: self.game_engine.perform_action("search"))
        for connection in current_env.get("connections", []):
            builder.add_option(f"Go to {connection}", lambda conn=connection: self.game_engine.perform_action("move", location=conn))
        builder.add_option("Check status", lambda: self.game_engine.perform_action("status"))
        return builder.build()
     
class GameUtils:

    def create_dynamic_menu(game_state, game_engine):
        """Exapmple function of how im using DAG within the game"""
        builder = JDDMenuBuilder()

        # Conditionally moving to the castle
        move_to_castle = JDDMenuUtils.dynamic_action_generator(
            condition=lambda ctx: not game_state.at_location("Castle"),
            action_if_true=lambda ctx: game_engine.perform_action("move", location="Castle"),
            action_if_false=lambda ctx: print("You are already at the Castle.")
        )
        builder.add_option("Go to the Castle", move_to_castle)

        # Conditionally picking up the magic wand
        pick_magic_wand = JDDMenuUtils.dynamic_action_generator(
            condition=lambda ctx: not game_state.in_inventory("Magic Wand"),
            action_if_true=lambda ctx: game_engine.perform_action("pickup", item="Magic Wand"),
            action_if_false=lambda ctx: print("You already have the Magic Wand.")
        )
        builder.add_option("Pick up Magic Wand", pick_magic_wand)

        # Always available option to show status
        builder.add_option("Show Status", lambda ctx: game_engine.perform_action("status"))

        return builder.build()


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