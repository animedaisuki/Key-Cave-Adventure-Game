import pkg_resources
import voyager.utils as U
from importlib import resources


def load_prompt(prompt):
    with resources.path("voyager.prompts", f"{prompt}.txt") as prompt_path:
        return U.load_text(str(prompt_path))
