# External Libraries
import rich.align
import rich.text
import rich.live

# Internal Libraries
from . import terminal

# Item object
class Item:

    # Custom emoji per object for nice formatting
    def __init__(self, name, emoji, price, id="pass"):

        self.name = name
        self.emoji = emoji
        self.price = int(price)
        self.selected = False
        self.id = id

# Shop object for easy set/reset
class shop:

    def __init__(self, 
        tstt: terminal.terminal, 

        title: str,

        store_keeper_name: str,
        store_keeper_msg: str,
        player: dict
    ):

        self.tstt = tstt

        self.title = title

        self.store_keeper_name = store_keeper_name
        self.store_keeper_msg = store_keeper_msg

        self.changed = False
        self.player = player

        self.items: list[Item] = [] # Initialize items object
        self.diff = 0 # Difference of previous price; (-100) ui

    def add_items(self, items: list):

        self.items.extend(items)

    def render(self):

        items_rendered = ""

        self.credits = self.player["credits"] # Set credits

        idx = 1

        for item in self.items:

            item_render = f"{idx}. {item.emoji} {item.name} {item.price}"

            style = "white"

            if item.price < self.credits:

                style = "bright_black"

            elif item.price > self.credits: # Make it red if they can not afford it

                style = "dark_red"
            
            elif item.name == "Exit":

                style = "green"
            
            items_rendered += f"\n[{style}]{item_render}[/{style}]" # Color markdown
            
            idx += 1

        diff = self.diff
        self.diff = 0

        diff_text = ""

        if diff > 0:
            diff_text = f"[red](-{diff})[/red]" # Say how much was spent last purchase

        # Render everything
        rendered = f"{self.title}" \
            + "\n--------" \
            + f"\n{self.store_keeper_name}: {self.store_keeper_msg}" \
            + f"\nSpace Yen: {self.credits} {diff_text}" \
            + f"\n--------\n" \
            + f"\n{items_rendered}" \
            + f"\n[green]x. Exit[/green]"

        self.changed = True
        
        return rendered
    
    # Run shop
    def run(self):

        # Live; it updates dynamically
        with rich.live.Live(console=self.tstt.console, refresh_per_second=60) as live:

            while True:

                rendered = ""

                rendered = self.render()

                display = rich.text.Text()

                for segment in rich.text.Text.from_markup(rendered).render(self.tstt.console):

                    display.append(segment.text, style=segment.style)
                
                # Check if it's changed and if it is it resets the changed value and updates
                if self.changed:
                    live.update(rich.align.Align(rendered, align="center"))
                    self.changed = False
                
                live.stop()
                
                # Asks which item 
                prompt_value = input("Which item # would you like to buy from? (x to exit)> ")
                try: item_idx = int(prompt_value)-1
                except: 
                    if prompt_value.lower() == "x" or prompt_value.lower() == "exit": return ""
                    continue

                # Clears screen of useless information
                self.tstt.clear_screen()

                live.start()

                try:
                    item_chosen = self.items[item_idx]
                except:
                    pass # They should know that their selection is wrong from the highlighting
                    
                self.tstt.clear_screen()

                live.update(rich.align.Align(rendered, align="center"))

                number_of_items = 1 

                # If they CAN afford it
                if not item_chosen.price > self.credits:
                    
                    live.stop()
                    number_of_items = int(input("How many would you like to buy? > "))

                    if number_of_items <= 0:
                        self.store_keeper_msg = "Sorry?" # Immersive error correction
                        continue

                    self.tstt.clear_screen()
                    live.start()

                # If they can NOT afford it
                if item_chosen.price*number_of_items > self.credits:

                    self.store_keeper_msg = "Insufficient funds!"
                
                else:

                    # Print all information, ask again

                    self.store_keeper_msg = f"You bought {number_of_items} {item_chosen.name}s!"

                    self.player[item_chosen.id] += number_of_items
                    self.player["credits"] -= item_chosen.price*number_of_items

                    self.diff = item_chosen.price*number_of_items


# Test code
if __name__ == "__main__":

    shoppy= shop(terminal.terminal(rich.get_console()), 1000, "John's shop", "John", "Good afternoon!")
            
    shoppy.add_items([Item("Meat", "🍖", 5000)])

    shoppy.run()
            

        
