import json
from datetime import datetime

from agents.utils import find_best_string_match
from prompts.prompt_utils import format_prompt, InitialPrompt
from agents.intention_and_params.filter_conditions import filter_conditions
from agents.llm_inference import get_request_result_jf


def intention_agent(customer_input, account_no, current_history):
    """classify customer input into one predefined intention_and_params and fetch relevant agent workflow from df"""
    filtered_intention_script_df = filter_conditions()

    filtered_intentions = filtered_intention_script_df['intention'].tolist()
    filtered_intention_workflow_dict = dict(zip(filtered_intention_script_df.intention, filtered_intention_script_df.aggregated_workflow))
    # feed filtered final candidates to llm prompt
    # current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final_input = format_prompt(
        prompt_template=InitialPrompt,
        customer_input=customer_input,
        current_history=current_history,
        filtered_intentions=filtered_intentions,
        # filtered_data_returned=filtered_data_returned
    )
    print('iiiinnnnnnnpppppppp', final_input)
    output_string = get_request_result_jf(final_input)
    print('intention output string: ', output_string)
    try:
        output_dict = json.loads('{' + output_string.split('{')[1].split('}')[0] + '}')
        intention = output_dict['intention']
        clarify_question = output_dict['clarify_question']
        assert intention in filtered_intention_script_df['intention'].tolist(), 'not in df, use string match'
    except:
        intention = find_best_string_match(filtered_intention_script_df['intention'].tolist(), output_string)
        clarify_question = ''

    return {'intention': intention,
            'filtered_intention_workflow_dict': filtered_intention_workflow_dict,
            'clarify_question': clarify_question,
            }
