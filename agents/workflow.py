import re
import traceback
from typing import Callable, Dict, Union
from routers.utils import JFResponse

from commons.logger import logger
from .intention_and_params.params_agent import get_cached_params
from .utils import LazyCallable
from .intention_and_params import params_agent
from commons.redis_conn import redis_conn


def workflow_handler(account_no, external_params: Dict, workflow_function: Callable):
    external_params['account_no'] = account_no
    logger.info(f'external params: {external_params}')
    return workflow_function(**external_params)


def run_workflow(account_no, customer_input, current_history, intention, aggregated_workflow) -> Union[dict, JFResponse]:
    workflow_list = []
    if ',' in aggregated_workflow:
        first_workflow, second_workflow = aggregated_workflow.split(',')[0], aggregated_workflow.split(',')[1]
        workflow_list.append(first_workflow)
        workflow_list.append(second_workflow)
    else:
        workflow_list.append(aggregated_workflow)

    resp = resp_description = ''
    for current_workflow in workflow_list:
        # get cached params for current workflow
        params_extracted_current_workflow = get_cached_params(current_workflow)

        print(f'Current workflow {current_workflow}, resp description: {resp_description}')
        # get params for workflow
        all_params = params_agent(customer_input, current_history, intention, current_workflow,
                                  previous_workflow_output=resp_description,
                                  parameters_already_extracted=params_extracted_current_workflow)

        if all_params['follow_up_question']:
            return JFResponse(no=0,
                              message='success',
                              data={"content": all_params['follow_up_question'],
                                    "api_resp": {},
                                    "intention": "follow up for necessary information"})

        else: # enter workflow, clear workflow params
            redis_conn.set('parameters_already_extracted', str({current_workflow: {}}))
            aggregated_workflow_response = workflow_handler(account_no,
                            all_params,
                            workflow_function=LazyCallable('agents.'+current_workflow))

            print('aggregated_workflow_response', aggregated_workflow_response)
            resp, resp_description = aggregated_workflow_response['resp'], aggregated_workflow_response['resp_description']

    return {'resp': resp, 'resp_description': resp_description}