import logging


class GameLogger:
    def __init__(self):
        self.game_logger = logging.getLogger('game_log')
        self.game_logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler('game_log.txt')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('(message)s')
        file_handler.setFormatter(formatter)

        self.game_logger.addHandler(file_handler)

    def logger(self):
        return self.game_logger

