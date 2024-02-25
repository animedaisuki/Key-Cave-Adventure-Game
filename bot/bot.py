import requests
from bot_logger import logger


class Bot:
    def __init__(self, base_url):
        self.base_url = base_url

    def start_game(self, dungeon_name="game1.txt"):
        response = requests.post(f"{self.base_url}/game/start", json={"dungeon": dungeon_name})
        return response.json()

    def move(self, action):
        action_sequence = ["W", "A", "S", "D"]
        if action not in action_sequence:
            return
        response = requests.post(f"{self.base_url}/game/move", json={"action": action})
        return response.json()

    def move_up(self):
        self.move('W')

    def move_down(self):
        self.move('S')

    def move_left(self):
        self.move('A')

    def move_right(self):
        self.move('D')

    def get_status(self, log=False):
        response = requests.get(f"{self.base_url}/game/status")
        status = response.json()
        if log:
            logger.info("Game status: %s", status)
        return status

    def check_moves_left(self):
        status = self.get_status()
        return status['moves_left']

    def check_game_finish(self):
        status = self.get_status()
        if status['status'] == 'Game in progress':
            return False
        else:
            return True

    def check_win(self):
        status = self.get_status()
        if not self.check_game_finish():
            return False
        else:
            if status['status'] == 'Win':
                return True
            else:
                return False

if __name__ == "__main__":
    bot = Bot("http://localhost:8000")

    bot.start_game("game1.txt")
    bot.get_status(log=True)

    bot.move_right()
    bot.get_status(log=True)

    bot.move_right()
    bot.get_status(log=True)

    bot.move_up()
    bot.get_status(log=True)

    bot.move_down()
    bot.get_status(log=True)

    bot.move_down()
    bot.get_status(log=True)

    bot.move_left()
    bot.get_status(log=True)
