# External Libraries
import rich.align
import rich.text
import rich.live

# Built in libraries
import time
import os

# Terminal Class for simplicity
class terminal:

    def __init__(self, console: rich.Console, letter_speed_multiplier=1):

        self.console = console
        self.letter_speed_multiplier = letter_speed_multiplier

    # Clears Screen
    def clear_screen(self):

        os.system("cls")

    # Centers if needed, then prints
    def print(self, text, center_horizontally=True, center_vertically=False, **args):

        formatted = text

        if center_horizontally and center_vertically:
            formatted = rich.align.Align.center(
                text,
                vertical="middle",
                height=self.console.size.height
            )

        elif center_horizontally:
            formatted = rich.align.Align.center(text)

        elif center_vertically:
            formatted = rich.align.Align.center(
                text,
                vertical="middle",
                height=self.console.size.height
            )

        self.console.print(formatted, **args)

    # Breaks up text into chunks and prints slows 
    def slowprint(self, text, center=True, letters_per_second=7, end: str | None = "\n"):

        display = rich.text.Text()

        # Live with update
        with rich.live.Live(console=self.console, refresh_per_second=60) as live:

            for segment in rich.text.Text.from_markup(text).render(self.console):

                for character in segment.text:

                    display.append(character, style=segment.style)

                    update=display

                    live.update(update)
                    time.sleep(1 / (letters_per_second*self.letter_speed_multiplier))

            if end:
                self.console.print(end, end="")

    # Forces user to use specific window size
    def force_window_size(self, min_height, min_width):

        display = rich.align.Align.center(
            rich.text.Text(f"TST - Resize your window\nMin Height: {min_height}\nMin Width: {min_width}"),
            vertical="middle",
            height=self.console.size.height
        )

        with rich.rich.live.Live.rich.live.Live(display, refresh_per_second=10, console=self.console) as rich.live.Live:
            
            while True: 

                if self.console.size.width >= min_width and self.console.size.height >= min_height:
                    break

                rich.live.Live.update(display)
        
        self.clear_screen()