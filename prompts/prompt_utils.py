import os
from typing import Optional
import jinja2
from jinja2 import Environment, FileSystemLoader

from commons.cfg_loader import project_cfg, agent_jinja_path
from configs.base_config import BaseConfig



class BasePromptTemplate:
    def __init__(self, template_path=None):
        assert template_path, 'template_path must be given'
        with open(template_path, encoding='utf-8') as fp:
            template = fp.read()
        self.template = jinja2.Template(template)

    def format(self, **kwargs):
        return self.template.render(**kwargs)


class InitialPrompt(BasePromptTemplate):
    def __init__(self, jinja_file=project_cfg.initial_prompt):
        super(InitialPrompt, self).__init__(jinja_file)


class FinalPrompt(BasePromptTemplate):
    def __init__(self, jinja_file=project_cfg.final_prompt):
        super(FinalPrompt, self).__init__(jinja_file)


class ParamsPrompt(BasePromptTemplate):
    def __init__(self, jinja_file):
        super(ParamsPrompt, self).__init__(jinja_file)


def format_prompt(prompt_template: BasePromptTemplate,
                  **format_params
                  ) -> str:
    """
    :return: final prompt
    """

    prompt_template = prompt_template()
    final_prompt = prompt_template.format(**format_params)
    return final_prompt


def format_params_prompt(content_filename: str,
                  **format_params
                  ) -> str:
    """
    :return: final prompt
    """
    env = Environment(loader=FileSystemLoader(agent_jinja_path))
    loaded = env.get_template(f'{content_filename}.jinja')
    final_prompt = loaded.render(**format_params)
    return final_prompt


if __name__ == '__main__':
    final_input = format_params_prompt(
        content_filename='place_order'
    )
    print(final_input)