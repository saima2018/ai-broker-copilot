import pytest
import pandas as pd
import pytest
from agents.intention_and_params import intention_agent


def load_cases(filepath='./test_case_intention.xlsx'):
    # Load test cases from excel
    df = pd.read_excel(filepath)
    df.fillna('', inplace=True)
    test_data = df.to_numpy().tolist()
    return test_data


@pytest.mark.parametrize("customer_input, current_history, expected_intention, expected_follow_up", load_cases())
def test_intention_agent(customer_input, current_history, expected_intention, expected_follow_up):
        result = intention_agent(customer_input, None, current_history)
        intention = result['intention']
        clarify_question = result['clarify_question']
        # Assert that the function's output matches the expected output
        assert (intention == expected_intention) and (expected_follow_up if clarify_question else not expected_follow_up), \
            f"Failed for inputs: {customer_input}, {current_history}"