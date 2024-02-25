from voyager import Voyager
from bot import Bot

openai_api_key = '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'

bot = Bot("http://localhost:8000")

voyager = Voyager(
    openai_api_key=openai_api_key,
    ckpt_dir="/Users/amouyotsuha/Documents/Projects/Key-Cave-Adventure-Game/voyager/agents/ckpt",
    bot=bot,
    dungeon_map="game1.txt"
)

voyager.learn()
