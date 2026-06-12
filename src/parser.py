import json
import random
from dataclasses import dataclass
from typing import Optional, Any

import rich
import rich.prompt

from . import shop_archive
from . import terminal



# Data


storyline = json.load(
    open("./src/storyline.json", "r", encoding="utf-8")
)

database = {
    "state": "intro"
}

player = {
    "credits": 0,
    "food": 0,
    "parts": 0,
    "arms": 0,
}

@dataclass
class Event:
    pass


@dataclass
class Print(Event):
    text: str


@dataclass
class SlowPrint(Event):
    text: str
    speed: int


@dataclass
class Prompt(Event):
    question: str
    choices: list[str]


@dataclass
class Shop(Event):
    shop_data: dict


@dataclass
class Jump(Event):
    target: str


@dataclass
class End(Event):
    pass

@dataclass
class Roulette(Event):
    pass

@dataclass
class Hunting(Event):
    pass

@dataclass
class Asteroid(Event):
    pass

@dataclass
class Pause(Event):
    pass


def check_variable(test):

    global database

    if test[0] == "$":

        if test[1:] in database:
            return database[test[1:]]

        return test[1:]

    return test

def run_sequence(sequence):

    global database
    global player

    print(sequence)

    print(database)
    print(player)


    idx = 0 

    while idx < len(sequence):

        g_idx = idx

        entry = sequence[idx]

        if isinstance(entry, str) and " " in entry:
            split_sequence = entry.split(" ")
        else:
            split_sequence = [entry]

        
        # Commands
        

        if isinstance(entry, str) and entry.startswith("!"):

            command = split_sequence[0]

            
            # Jumps
            

            if command == "!jump":
                yield Jump(split_sequence[1])
                return

            if command == "!jump_switch":
                yield Jump(
                    sequence[idx + 1][database[split_sequence[1]]]
                )
                return

            if command == "!random_hop":
                yield Jump(
                    random.choice(split_sequence[1:])
                )
                return
            
            if command == "!roulette":
                yield Roulette()

            if command == "!hunting":
                yield Hunting()

            if command == "!asteroid":
                yield Asteroid()
            
            # End
            

            if command == "!end":
                yield End()
                return

            
            # Variable storage
            

            if command == "!store":
                database[
                    split_sequence[1]
                ] = check_variable(split_sequence[2])

            
            # Slow print
            

            if command == "!slow":
                yield SlowPrint(
                    text=" ".join(split_sequence[2:]),
                    speed=int(split_sequence[1])
                )

            
            # Player modification
            

            if command == "!modify":

                key = split_sequence[1]
                operation = split_sequence[2]
                value = int(split_sequence[3])

                if operation == "+":
                    player[key] += value

                elif operation == "-":
                    player[key] -= value

                elif operation == "*":
                    player[key] *= value

                elif operation == "/":
                    player[key] /= value

            
            # Conditional
            

            if command == "!if":

                lhs = player[split_sequence[1]]
                rhs = int(split_sequence[3])

                success_branch = sequence[idx + 2]
                failure_branch = sequence[idx + 1]

                if split_sequence[2] == ">=":

                    branch = (
                        success_branch
                        if lhs >= rhs
                        else failure_branch
                    )

                elif split_sequence[2] == "<=":

                    branch = (
                        success_branch
                        if lhs <= rhs
                        else failure_branch
                    )

                else:
                    raise ValueError(
                        f"Unsupported operator: {split_sequence[2]}"
                    )

                result = yield from run_sequence(branch)

                if result is not None:
                    return result

            
            # Shop
            

            if command == "!shop":

                shop_json = sequence[idx + 1]

                yield Shop(shop_json)

                idx += 1

        
        # Comment
        

        elif isinstance(entry, str) and entry.startswith("#"):
            pass

        
        # Prompt
        

        elif isinstance(entry, str) and entry.startswith("?"):

            question = entry[1:]

            options = sequence[idx + 1]

            if isinstance(options, list):

                answer = yield Prompt(
                    question=question,
                    choices=options
                )

                database["choice"] = answer

            elif isinstance(options, dict):

                answer = yield Prompt(
                    question=question,
                    choices=list(options.keys())
                )

                database["choice"] = answer

                yield Jump(options[answer])
                return

            idx += 1

        
        # Normal text
        

        else:

            yield Print(str(entry))

        idx += 1

def execute_parse(console: rich.Console):

    global storyline

    tstt = terminal.terminal(console)

    state = "intro"

    while True:

        generator = run_sequence(
            storyline[state]
        )

        send_value = None

        try:

            while True:

                event = generator.send(send_value)
                send_value = None

                
                # Print
                

                if isinstance(event, Print):

                    rich.print(event.text)

                
                # Slow print
                

                elif isinstance(event, SlowPrint):

                    tstt.slowprint(
                        event.text,
                        letters_per_second=event.speed
                    )

                
                # Prompt
                

                elif isinstance(event, Prompt):

                    answer = rich.prompt.Prompt.ask(
                        "?> ",
                        choices=event.choices,
                        case_sensitive=False
                    )

                    send_value = answer

                
                # Shop
                

                elif isinstance(event, Shop):

                    shop_json = event.shop_data

                    shop_obj = shop.shop(
                        tstt,
                        title=shop_json["title"],
                        store_keeper_name=shop_json["store_keeper_name"],
                        store_keeper_msg=shop_json["store_keeper_msg"],
                        player=player,
                    )

                    for item_json in shop_json["items"]:

                        shop_obj.add_items([
                            shop.Item(
                                name=item_json["name"],
                                emoji=item_json["emoji"],
                                price=item_json["price"],
                                id=item_json["id"],
                            )
                        ])

                    shop_obj.run()

                
                # Jump
                

                elif isinstance(event, Jump):

                    state = event.target
                    break

                
                # End
                

                elif isinstance(event, End):

                    return

        except StopIteration:
            pass

#execute_parse(rich.get_console())
