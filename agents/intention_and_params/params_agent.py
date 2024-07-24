import json
from datetime import datetime
from typing import Dict

from agents.llm_inference import get_request_result_jf
from prompts.prompt_utils import ParamsPrompt, format_params_prompt
from commons.logger import logger
from commons.redis_conn import redis_conn


def get_cached_params(current_workflow) -> Dict:
    parameters_already_extracted = redis_conn.get('parameters_already_extracted')
    print('parameters_already_extracted', parameters_already_extracted)
    parameters_already_extracted = eval(parameters_already_extracted)
    if current_workflow in parameters_already_extracted:
        params_extracted_current_workflow = parameters_already_extracted[current_workflow]
        params_extracted_current_workflow['follow_up_question'] = ''  # remove question from previous round
    else:
        params_extracted_current_workflow = {}  # clear history params for current workflow

    print(f'parameters_already_extracted for workflow {current_workflow}: ', params_extracted_current_workflow)
    return params_extracted_current_workflow


def params_agent(customer_input, current_history, intention, aggregated_workflow, previous_workflow_output=None,
                   parameters_already_extracted=None) -> Dict:

    # if APIs need extra params than account number
    all_params = extract_params_llm(customer_input,
                                    current_history,
                                    intention,
                                    aggregated_workflow,
                                    previous_workflow_output,
                                    parameters_already_extracted)
    logger.info(f'all params, {all_params}')
    if 'follow_up_question' not in all_params:
        all_params['follow_up_question'] = ''
    redis_conn.set('parameters_already_extracted', str({aggregated_workflow: all_params}))
    print('\nset redis just now: ', redis_conn.get("parameters_already_extracted"))
    return all_params


def extract_params_llm(customer_input, current_history, final_intention, aggregated_workflow, previous_workflow_output=None,
                       parameters_already_extracted=None):

    # parameters_already_extracted = eval(parameters_already_extracted)
    print('params from previous workflow: ', previous_workflow_output)
    print('99999999params from conversation history: ', parameters_already_extracted)

    final_input = format_params_prompt(
        prompt_template=ParamsPrompt,
        content_filename=aggregated_workflow,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        customer_input=customer_input,
        current_history=current_history,
        previous_workflow_output=previous_workflow_output,
        parameters_already_extracted=parameters_already_extracted,
        final_intention=final_intention
    )
    #
    print('\nextract params final input to llm: ', final_input)

    output_string = get_request_result_jf(final_input)
    output_string = '{' + str(output_string) if '{' not in output_string else output_string
    output_string = output_string.replace('```', '').replace('\n', '')
    print('\nextracted params: ', output_string)
    try:
        output_params = json.loads('{' + output_string.split('{')[1].split('}')[0] + '}')
        if 'symbols' in output_params:
            output_params['symbol'] = output_params['symbols']
            del output_params['symbols']
    except:
        output_params = {}

    print('\noutput params: ', output_params)

    return output_params