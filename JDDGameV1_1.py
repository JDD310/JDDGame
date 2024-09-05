from CS103.FinalProject.JDDMenu_v2_5 import * 
import random
import sys
import cmd
import os
import time

#TODO fix lmao im tired
class GameState:
    def __init__(self):
        # Player Status
        self.current_location = "Limbo"
        self.health = 20
        self.inventory = []
        self.quest_log = {}
        #TODO
        self.looted_area = False
    
    localEnvironment = {

    }

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
        print(f"Health: {self.health}")
        print(f"Inventory: {self.inventory}")
        print(f"Quest Log: {self.quest_log}")

#TODO Fix and define more actions for the player to take, i want this game to be very very cool. 
class GameEngine:
    def __init__(self, state):
        self.state = state

    def perform_action(self, action, **kwargs):
        if action.lower() == "move" and not self.state.is_at_location(kwargs.get("location")):
            self.state.move_to_location(kwargs.get("location"))

        #TODO
        elif action.lower() == "examine" and not 

        elif action.lower() == "pickup" and not self.state.has_item(kwargs.get("item")):
            self.state.add_item(kwargs.get("item"))

        elif action == "quest":
            self.state.update_quest(kwargs.get("quest_name"), kwargs.get("status"))

        elif action == "status":
            self.state.print_status()

#TODO Need to fix main logic so that this POS actually runs
def main():
    game_state = GameState()
    game_engine = GameEngine(game_state)

    while True:
        menu = GameUtils.create_dynamic_menu(game_state, game_engine)
        menu.display_menu()
        # Optionally, check for game end conditions
        if game_state.current_location == "End":
            print("Game Over")
            break

if __name__ == "__main__":
    main()

#TODO Fix menus to read JSON file instead of Modular style menus like shown here
class GameMenus:
     
    def scene_castle(game_state, game_engine):
        builder = JDDMenuBuilder()
        builder.set_title("At the Castle Gate")
        builder.add_option("Enter the Castle", lambda ctx: scene_castle_interior(game_state, game_engine))
        builder.add_option("Explore the Grounds", lambda ctx: scene_castle_grounds(game_state, game_engine))
        return builder.build()

    def scene_castle_interior(game_state, game_engine):
        builder = JDDMenuBuilder()
        builder.set_title("Inside the Castle")
        builder.add_option("Talk to the King", lambda ctx: GameMenus.action_talk_to_king(game_state, game_engine))
        builder.add_option("Leave the Castle", lambda ctx: scene_castle(game_state, game_engine))
        return builder.build()

    def action_talk_to_king(game_state, game_engine):
        builder = JDDMenuBuilder()
        builder.set_title("Inside the Castle")
        builder.add_option("Talk to the King", lambda ctx: action_talk_to_king(game_state, game_engine))
        builder.add_option("Leave the Castle", lambda ctx: scene_castle(game_state, game_engine))
        return builder.build()

    def scene_forest(game_state, game_engine):
        builder = JDDMenuBuilder()
        builder.set_title("In the Deep Forest")
        if game_state.has_item("magic compass"):
            builder.add_option("Follow the compass", lambda ctx: special_forest_path(game_state, game_engine))
        builder.add_option("Return to the crossroads", lambda ctx: scene_crossroads(game_state, game_engine))
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


    #TODO will remove later
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


