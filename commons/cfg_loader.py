import os.path

from configs.base_config import BaseConfig

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_cfg = BaseConfig(os.path.join(project_path, "configs/project.yaml"), project_path=project_path)
mysql_cfg = BaseConfig(os.path.join(project_path, "configs/mysql.yaml"), project_path=project_path)
redis_cfg = BaseConfig(os.path.join(project_path, "configs/redis.yaml"), project_path=project_path)
agent_jinja_path = os.path.join(project_path, "prompts/agent_params_extraction")
