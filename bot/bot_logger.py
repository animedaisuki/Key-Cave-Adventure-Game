import logging

GREEN = '\033[92m'
RESET = '\033[0m'

logging.basicConfig(level=logging.INFO,
                    format=f'{GREEN}%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
