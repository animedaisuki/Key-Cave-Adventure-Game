import random
import re
import os
import requests

import voyager.utils as U
from voyager.prompts import load_prompt
from voyager.utils.json_utils import fix_and_parse_json
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from langchain.vectorstores import Chroma


class CurriculumAgent:
    def __init__(
            self,
            model_name="gpt-3.5-turbo",
            temperature=0,
            request_timout=120,
            ckpt_dir="ckpt",
            resume=False,
            dungeon_map="game1.txt",
            mode="auto",
    ):
        os.environ["OPENAI_API_KEY"] = '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'

        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            request_timeout=request_timout,
        )

        assert mode in [
            "auto",
            "manual",
        ], f"mode {mode} not supported"

        self.mode = mode
        self.ckpt_dir = ckpt_dir
        U.f_mkdir(f"{ckpt_dir}/curriculum/vectordb")

        self.completed_tasks = []
        self.failed_tasks = []
        self.qa_cache = {}
        self.dungeon_map = dungeon_map

    @property
    def progress(self):
        return len(self.completed_tasks)

    def render_observation(self):
        print(123)
        game_data = U.get_game_initial_data(self.dungeon_map)

        print(game_data)

        observation = {
            "player_starting_position": f"Player Starting Position: {game_data['player_position']}\n\n",
            "key_position": f"Key Position: {game_data['key_position']}\n\n",
            "door_position": f"Door Position: {game_data['door_position']}\n\n",
            "potion_position": f"Potion Position: {game_data['potion_position']}\n\n",
            "barrier_positions": f"Barrier Positions: {game_data['barrier_positions']}\n\n",
            "dungeon_size": f"Dungeon Size: {game_data['dungeon_size']}\n\n",
            "moves_remaining": f"Move Remaining: {game_data['moves_left']}\n\n",
            "game_map": f"Game Map: {game_data['game_board']}\n\n"
        }

        return observation

    def render_system_message(self):
        system_message = SystemMessage(content=load_prompt("curriculum"))
        assert isinstance(system_message, SystemMessage)
        return system_message

    def render_human_message(self):
        content = ""
        observation = self.render_observation()

        for key in observation:
            content += observation[key]

        print(f"\033[35m****Curriculum Agent human message****\n{content}\033[0m")
        return HumanMessage(content=content)

    def propose_solution(self, max_retries=5):
        messages = [
            self.render_system_message(),
            self.render_human_message()
        ]

        if self.mode == "auto":
            return self.propose_ai_solution(messages=messages, max_retries=max_retries)

    def propose_ai_solution(self, *, messages, max_retries=5):
        if max_retries == 0:
            raise RuntimeError("Max retries reached, failed to propose ai task.")
        curriculum = self.llm(messages).content
        print(f"\033[31m****Curriculum Agent ai message****\n{curriculum}\033[0m")
        try:
            response = self.parse_ai_solution(curriculum)
            assert "next_task" in response
        except Exception as e:
            print(
                f"\033[35mError parsing curriculum response: {e}. Trying again!\033[0m"
            )
            return self.propose_ai_solution(
                messages=messages,
                max_retries=max_retries - 1,
            )

    def parse_ai_solution(self, message):
        solution = ""
        for line in message.split("\n"):
            if line.startswith("Solution:"):
                solution = line[9:].replace(".", "").strip()
                # print(solution)
        assert solution, "Solution not found in Curriculum Agent response"
        return {"solution": solution}

if __name__ == "__main__":
    curriculum_agent = CurriculumAgent()
    print(curriculum_agent.render_observation())
    curriculum_agent.propose_solution()
