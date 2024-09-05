from CS103.FinalProject.JDDMenu_v2_5 import * 
import random
import sys
import cmd
import os
import time

class GameState:
    def __init__(self):
        self.current_location = "Start"
        self.inventory = []
        self.quest_log = {}

    def has_item(self, item):
        """Check if the player has a specific item in their inventory."""
        return item in self.inventory

    def is_at_location(self, location):
        """Check if the player is at a specific location."""
        return self.current_location == location

    def move_to_location(self, location):
        """Move the player to a new location."""
        self.current_location = location
        print(f"Moved to {location}")

    def add_item(self, item):
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
        print(f"Inventory: {self.inventory}")
        print(f"Quest Log: {self.quest_log}")

class GameEngine:
    def __init__(self, state):
        self.state = state

    def perform_action(self, action, **kwargs):
        """Perform an action that updates the game state."""
        if action == "move":
            self.state.move_to_location(kwargs.get("location"))
        elif action == "pickup":
            self.state.add_item(kwargs.get("item"))
        elif action == "quest":
            self.state.update_quest(kwargs.get("quest_name"), kwargs.get("status"))
        elif action == "status":
            self.state.print_status()

def main():
    game_state = GameState()
    game_engine = GameEngine(game_state)
    
    # Define possible actions
    actions = {
        "move": {"location": "Castle"},
        "pickup": {"item": "Magic Wand"},
        "quest": {"quest_name": "Find the Lost Key", "status": "Completed"},
        "status": {}
    }

    builder = JDDMenuBuilder()
    builder.add_option("Go to the Castle", lambda: game_engine.perform_action("move", **actions["move"]))
    builder.add_option("Pick up Magic Wand", lambda: game_engine.perform_action("pickup", **actions["pickup"]))
    builder.add_option("Complete Quest", lambda: game_engine.perform_action("quest", **actions["quest"]))
    builder.add_option("Show Status", lambda: game_engine.perform_action("status"))

    menu = builder.build()
    menu.display_menu()




class GameUtils:

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

    menu_items = [
        ("Meet the stranger", encounter),
        ("Accept the quest", accept_quest),
        ("Decline the quest", decline_quest)
    ]

    def game_menu():
        context = {}
        builder = JDDMenuBuilder()
        for text, action in GameUtils.menu_items:
            builder.add_option(text, lambda ctx=context: action(ctx))
        menu = builder.build()
        menu.display_menu(context)

    #game_menu()


