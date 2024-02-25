import time


class ActionAgent:
    def __init__(
        self,
        bot,
        dungeon_map="game1.txt",
        resume=False
    ):
        self.bot = bot
        self.dungeon_map = dungeon_map

    def execute_solution(self, solution):
        retry = 3
        error = None

        while retry > 0:
            try:
                self.bot.start_game(dungeon_name=self.dungeon_map)
                code = f'bot = Bot("{self.bot.get_base_url()}")\n\n'
                code += f'bot.start_game(dungeon_name={self.dungeon_map})\n\n'
                instructions = solution.split(', ')
                for instruction in instructions:
                    words = instruction.split(' ')
                    direction = words[1]
                    steps = int(words[3])

                    for _ in range(steps):
                        if direction == 'right':
                            self.bot.move_right()
                            code += 'bot.move_right()\n\n'
                        elif direction == 'up':
                            self.bot.move_up()
                            code += 'bot.move_up()\n\n'
                        elif direction == 'down':
                            self.bot.move_down()
                            code += 'bot.move_down()\n\n'
                        elif direction == 'left':
                            self.bot.move_left()
                            code += 'bot.move_left()\n\n'
                code += 'bot.get_status()\n\n'
                return self.bot.get_status(log=True), code

            except Exception as e:
                retry -= 1
                error = e
                time.sleep(1)

        return f"Error parsing solution (before program execution): {error}"
