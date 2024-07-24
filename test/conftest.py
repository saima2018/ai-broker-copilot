"""
conftest 全局变量
"""
import os
import sys

sys.path.append(".")
sys.path.append("..")
import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
project_folder = os.path.dirname(test_folder)
apis_folder = os.path.join(project_folder, "apis")


@pytest.fixture(scope='session')
def dummy_user_id():
    return "dummy_user_id"
