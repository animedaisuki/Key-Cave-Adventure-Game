import copy
import json
import os
import time
from typing import Dict

import voyager.utils as U

from .agents import ActionAgent
# from .agents import CriticAgent
from .agents import CurriculumAgent
# from .agents import SkillManager


# TODO: remove event memory
class Voyager:
    def __init__(
        self,
        openai_api_key: str = None,
        max_iterations: int = 160,
        action_agent_model_name: str = "gpt-4",
        action_agent_temperature: float = 0,
        action_agent_task_max_retries: int = 4,
        action_agent_show_chat_log: bool = True,
        action_agent_show_execution_error: bool = True,
        curriculum_agent_model_name: str = "gpt-4",
        curriculum_agent_temperature: float = 0,
        curriculum_agent_mode: str = "auto",
        critic_agent_model_name: str = "gpt-4",
        critic_agent_temperature: float = 0,
        critic_agent_mode: str = "auto",
        skill_manager_model_name: str = "gpt-3.5-turbo",
        skill_manager_temperature: float = 0,
        skill_manager_retrieval_top_k: int = 5,
        openai_api_request_timeout: int = 240,
        ckpt_dir: str = "ckpt",
        skill_library_dir: str = None,
        resume: bool = False,
        bot: any = None,
        dungeon_map: str = "game1.txt",
    ):

        self.max_iterations = max_iterations
        self.bot = bot
        self.dungeon_map = dungeon_map

        # set openai api key
        os.environ["OPENAI_API_KEY"] = openai_api_key

        # init agents
        self.action_agent = ActionAgent(
            bot=bot,
            resume=resume,
            dungeon_map=dungeon_map,
        )
        self.action_agent_task_max_retries = action_agent_task_max_retries
        self.curriculum_agent = CurriculumAgent(
            model_name=curriculum_agent_model_name,
            temperature=curriculum_agent_temperature,
            request_timout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
            mode=curriculum_agent_mode,
            dungeon_map=dungeon_map,
        )
        # self.critic_agent = CriticAgent(
        #     model_name=critic_agent_model_name,
        #     temperature=critic_agent_temperature,
        #     request_timout=openai_api_request_timeout,
        #     mode=critic_agent_mode,
        # )
        self.resume = resume

        # init variables for rollout
        self.action_agent_rollout_num_iter = -1
        self.solution = None
        self.messages = None
        self.conversations = []
        self.last_events = None

    def reset(self, solution, reset_env=True):
        self.action_agent_rollout_num_iter = 0
        self.solution = solution

    def step(self):
        if self.action_agent_rollout_num_iter < 0:
            raise ValueError("Agent must be reset before stepping")
        status, code = self.action_agent.execute_solution(self.solution)
        print(f"\033[34m****Action Agent message****\n{status}\033[0m")

        self.action_agent_rollout_num_iter += 1

        success = False

        if status['status'] == 'Win':
            success = True

        done = (
            self.action_agent_rollout_num_iter >= self.action_agent_task_max_retries
            or success
        )

        info = {
            "solution": self.solution,
            "success": success,
        }
        if success:
            # assert (
            #     "program_code" in parsed_result and "program_name" in parsed_result
            # ), "program and program_name must be returned when success"
            info["program_code"] = code
        else:
            print(
                f"\033[32m****Action Agent human message****\nGame Over\033[0m"
            )
        return self.messages, 0, done, info

    def rollout(self, *, solution, reset_env=True):
        self.reset(solution=solution,  reset_env=reset_env)
        while True:
            messages, reward, done, info = self.step()
            if done:
                break
        return messages, reward, done, info

    def learn(self, reset_env=True):
        tries = 0
        game_log_needed = False

        while True:
            if tries > self.max_iterations:
                print("Iteration limit reached")
                break
            game_log = U.load_text('/Users/amouyotsuha/Documents/Projects/Key-Cave-Adventure-Game/key_cave_adventure_game/game_log.txt') if game_log_needed else None
            wrong_solution = U.load_text('/Users/amouyotsuha/Documents/Projects/Key-Cave-Adventure-Game/previous_game_solution.txt') if game_log_needed else None
            solution = self.curriculum_agent.propose_solution(
                max_retries=5,
                game_log=game_log,
                wrong_solution=wrong_solution
            )
            print(
                f"\033[35mStarting for at most {self.action_agent_task_max_retries} times\033[0m"
            )
            try:
                messages, reward, done, info = self.rollout(
                    solution=solution,
                    reset_env=reset_env,
                )
                tries += 1
            except Exception as e:
                time.sleep(3)  # wait for mineflayer to exit
                info = {
                    "solution": solution,
                    "success": False,
                }

                # use red color background to print the error
                print("Your last round rollout terminated due to error:")
                print(f"\033[41m{e}\033[0m")

                tries += 1

            if info["success"]:
                print(
                    f"\033[35mSolution Works Successfully! \n\n{info['program_code']}\033[0m"
                )
                game_log_needed = False
                break
            else:
                game_log_needed = True

            # self.curriculum_agent.update_exploration_progress(info)
            # print(
            #     f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m"
            # )
            # print(
            #     f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
            # )

        # return {
        #     "completed_tasks": self.curriculum_agent.completed_tasks,
        #     "failed_tasks": self.curriculum_agent.failed_tasks,
        #     "skills": self.skill_manager.skills,
        # }
