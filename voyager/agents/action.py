import time


class ActionAgent:
    def __init__(
        self,
        bot,
        dungeon_map="game1.txt",
    ):
        self.bot = bot
        self.dungeon_map = dungeon_map

    def execute_solution(self, solution):
        retry = 3
        error = None

        while retry > 0:
            try:
                self.bot.start_game(dungeon_name=self.dungeon_map)
                instructions = solution.split(', ')
                for instruction in instructions:
                    words = instruction.split(' ')
                    direction = words[1]
                    steps = int(words[3])

                    for _ in range(steps):
                        if direction == 'right':
                            self.bot.move_right()
                        elif direction == 'up':
                            self.bot.move_up()
                        elif direction == 'down':
                            self.bot.move_down()
                        elif direction == 'left':
                            self.bot.move_left()
                return self.bot.get_status(log=True)


            except Exception as e:
                retry -= 1
                error = e
                time.sleep(1)

        return f"Error parsing solution (before program execution): {error}"
