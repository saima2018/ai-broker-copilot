import json

import pytest
import pandas as pd
import pytest
from agents.intention_and_params import params_agent
from libs import symbol_processing


def load_cases(filepath='./test_case_params.xlsx'):
    # Load test cases from excel
    df = pd.read_excel(filepath)
    df.fillna('', inplace=True)
    test_data = df.to_numpy().tolist()
    return test_data


@pytest.mark.parametrize("customer_input, current_history, final_intention, aggregated_workflow, previous_workflow_output, params_already_extracted, expected_params, expected_follow_up", load_cases())
def test_params_agent(customer_input, current_history, final_intention, aggregated_workflow, previous_workflow_output, params_already_extracted, expected_params, expected_follow_up):
        all_params = params_agent(customer_input, current_history, final_intention, aggregated_workflow, previous_workflow_output, params_already_extracted)
        follow_up_question = all_params['follow_up_question']
        if 'symbol' in all_params:
            all_params['symbol'] = symbol_processing((all_params['symbol']))
        expected_params = json.loads(expected_params)
        # Assert that the function's output matches the expected output
        for k, v in all_params.items():
            if (k != 'follow_up_question') and v:
                assert (k in expected_params) and expected_params[k] == v, f"Failed for param: {k} and value: {v}"
        assert (expected_follow_up if follow_up_question else not expected_follow_up), \
            f"Failed for inputs: {customer_input}, {current_history}"