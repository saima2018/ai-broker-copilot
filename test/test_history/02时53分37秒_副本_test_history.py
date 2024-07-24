import pytest
from fastapi.testclient import TestClient
from prompt_engineering.libs.mongo_tables.user_history import UserHistoryManager

from app import app
import random
import string

client = TestClient(app)


class TestHistory:
    @classmethod
    @pytest.fixture(autouse=True)
    def setup_class(self):
        """初始化环境"""
        pass

    def test_history_api(self, dummy_user_id: str):
        user_input = "".join([random.choice(string.ascii_letters + string.digits)] * 5)
        ai_output = "".join([random.choice(string.ascii_letters + string.digits)] * 5)
        resp = client.post("/api/v1/history/add_history/",
                           json={"user_input": user_input,
                                 "ai_output": ai_output,
                                 "user_id": dummy_user_id})
        assert resp.status_code == 200
        resp = resp.json()
        assert resp["message"] == "success", resp["message"]
        assert resp["code"] == 0, resp["code"]

        user_history_man = UserHistoryManager()
        last_history = user_history_man.list_history(dummy_user_id, k=1)[0]
        last_q, last_a = user_history_man.get_QA(last_history)
        assert last_q == user_input
        assert last_a == ai_output
        user_history_man.delete_user_history(dummy_user_id)

