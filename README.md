# Voyager: An Open-Ended Embodied Agent with Large Language Models

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.9-blue.svg)](https://github.com/MineDojo/Voyager)
[![GitHub license](https://img.shields.io/github/license/MineDojo/Voyager)](https://github.com/MineDojo/Voyager/blob/main/LICENSE)

______________________________________________________________________

</div>

Welcome to the Key Cave Adventure Game: Voyager Edition, where we integrate the advanced capabilities of Voyager, an LLM-powered autonomous agent, into the classic maze navigation and puzzle-solving experience. Voyager, designed to operate within the Key Cave Adventure Game, brings a new level of autonomy, learning, and exploration to this text-based adventure.

Voyager is not just any agent leverages the power of Large Language Models (LLMs) like GPT-4 for continuous learning. Within the Key Cave Adventure Game, Voyager's integration showcases its ability to navigate mazes, solve puzzles, and make novel discoveries autonomously, all while continuously improving its strategies.

## Core Components of Voyager

Voyager's operation in the Key Cave Adventure Game is centered around two main components, reflecting a simplified yet powerful framework for autonomous exploration and learning:

- Curriculum Agent: Acting as the backbone for Voyager's exploration, the curriculum agent guides Voyager through the game, proposing solutions and strategies based on the current game state and Voyager's accumulated knowledge. It utilizes game logs to assess Voyager's performance and adjust its teaching strategy accordingly, maximizing learning efficiency and adaptability.

- Action Agent: The action agent executes the strategies and solutions proposed by the curriculum agent, interacting directly with the game environment. It embodies Voyager's ability to act within the game, applying learned skills to navigate mazes, collect items, and solve puzzles. Through iterative prompting, the action agent refines its actions based on feedback from the game environment, continuously improving its decision-making process.

Together, these components allow Voyager to navigate the complexities of the Key Cave Adventure Game with unprecedented autonomy and learning capability.

## Voyager's Learning Process

Voyager's learning process is a continuous loop of action, feedback, and adaptation. The curriculum agent observes Voyager's performance through game logs, adapting its instructional strategy to introduce new challenges and reinforce learning outcomes. The action agent, on the other hand, applies Voyager's current knowledge base to solve these challenges, learning from both successes and failures.

This process is facilitated by Voyager's access to a vast array of skills and strategies through its interaction with GPT-4. Unlike traditional game agents, Voyager does not rely on hardcoded responses or predefined paths. Instead, it generates solutions in real-time, adapting to the game environment and evolving challenges.

## Installation
Voyager requires Python ≥ 3.9 and Node.js ≥ 16.13.0. We have tested on Ubuntu 20.04, Windows 11, and macOS. You need to follow the instructions below to install Voyager.

```bash
git@github.com:animedaisuki/Key-Cave-Adventure-Game.git
cd Key-Cave-Adventure-Game
pip install -e .
```

# Getting Started
Voyager uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You can get one from [here](https://platform.openai.com/account/api-keys).

After the installation process, you can run Voyager by:
```python
from voyager import Voyager
from bot import Bot
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain.*")

openai_api_key = "YOUR_OPENAI_API_KEY"

bot = Bot("http://localhost:8000")

voyager = Voyager(
    openai_api_key=openai_api_key,
    ckpt_dir="YOUR_CKPT_DIR",
    bot=bot,
    dungeon_map="YOUR_GAME_MAP_FILE"
)

voyager.learn()
```
