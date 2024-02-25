from voyager import Voyager
from bot import Bot

openai_api_key = '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'

bot = Bot("http://localhost:8000")

voyager = Voyager(
    openai_api_key=openai_api_key,
    ckpt_dir="/Users/amouyotsuha/Documents/Projects/Key-Cave-Adventure-Game/voyager/agents/ckpt",
    bot=bot,
    dungeon_map="game2.txt"
)

voyager.learn()
