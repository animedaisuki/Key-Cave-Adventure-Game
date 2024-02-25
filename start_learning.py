from voyager import Voyager
from bot import Bot

openai_api_key = "YOUR OPENAI API KEY"

bot = Bot("http://localhost:8000")

voyager = Voyager(
    openai_api_key=openai_api_key,
    ckpt_dir="/ckpt",
    bot=bot,
    dungeon_map="game1.txt"
)

voyager.learn()
