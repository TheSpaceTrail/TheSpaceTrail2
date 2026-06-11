from rich import align
import rich

from rich.text import Text
from . import terminal

import time

console = rich.get_console()

def lerp(a, b, t):
    return int(a + (b - a) * t)

def rgb_green_gradient(text: str):

    lines = text.split("\n")
    total = max(len(lines) - 1, 1)

    start = (0, 100, 0)
    end = (0, 255, 0)

    for i, line in enumerate(lines):

        if not line.strip():

            console.print("")
            
            continue

        t = i / total

        r = lerp(start[0], end[0], t)
        g = lerp(start[1], end[1], t)
        b = lerp(start[2], end[2], t)

        style = f"rgb({r},{g},{b})"

        console.print(rich.align.Align(Text(line, style=style), align="center"))

def left_pad(text, pad):

    return "\n".join([" "*pad + line for line in text.split("\n")])

def seqence(force=True):

    tstt = terminal.terminal(rich.get_console())

    if force: tstt.force_window_size(20, 110)

    tstt.clear_screen()
    tstt.console.print("\n")
    tstt.slowprint("Location: [green][bold]Earth[/bold][/green]")
    time.sleep(2)
    tstt.slowprint("The year is [blue]2069[/blue].\n")
    tstt.slowprint("Your account balance; [bold][cyan1]1000S¥[/cyan1][/bold] (Space Yen).\n\n")
    time.sleep(2)
    tstt.slowprint("Your Mission: get to [khaki3]Saturn[/khaki3].")
    time.sleep(2)

    tstt.clear_screen()

    rgb_green_gradient("""
88888888888 888               .d8888b.                                88888888888             d8b 888 
    888     888              d88P  Y88b                                   888                 Y8P 888 
    888     888              Y88b.                                        888                     888 
    888     88888b.  .d88b.   "Y888b.    88888b.   8888b.  .d8888b .d88b  888 888d888 8888b.  888 888 
    888     888 "88b d8P  Y8 b    "Y88b. 888 "88b     "88b d88P"   d8P  Y 888 888P"      "88b 888 888 
    888     888  888 8888888 8      "888 888  888 .d888888 888     888888 888 888    .d888888 888 888 
    888     888  888 Y8b.     Y88b  d88P 888 d88P 888  888 Y88b.   Y8b.   888 888    888  888 888 888 
    888     888  888 "Y8888   "Y8888P"   8888P"  "Y888888  "Y8888P "Y8888 888 888    "Y888888 888 888 
                                        888                                                          
                                      ~888                                                           """)
    rich.print(rich.align.Align("""
[bold]            █████            
          ██     ██          
         █         █         
        █           █        
        █           █        
       █    ▄███▄    █       
       █    █   █    █       
       █    ▀███▀    █       
      ▄█             █▄      
     ███             ███     
    ██  █           █  ██    
   ██   █           █   ██   
  █▀     █         █     ▀█  
▄█▀       ██     ██       ▀█▄
█   ▄█████▓▓█████▓▓█████▄   █
██▀▀▀▀ ░▒▒▓▓▓▓▓▓▓▓▓▒▒░ ▀▀▀▀██
        ░▒▓▒▓▓▓▓▓▒▓▒░        
         ▒▒▒▒▒▓▒▒▒▒▒         
         ░▒▒▒▒▒▒▒▒▒░         
          ░▒▒░░░▒▒░          
            ░   ░      [/bold]"""
    .replace("▓", "[dark_orange3]▓[/dark_orange3]")
    .replace("▒", "[dark_orange3]▒[/dark_orange3]") 
    .replace("░", "[dark_orange3]░[/dark_orange3]"), 
    
    align="center"
    
    ))

    time.sleep(5) # I made this pixel art, they're gonna look at it!