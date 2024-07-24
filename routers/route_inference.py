import datetime
import json
import traceback
from fastapi import APIRouter, Body, Depends

from auth import *
from commons.logger import logger
from agents.workflow import run_workflow
from agents.intention_and_params import intention_agent
from prompts.prompt_utils import format_prompt, FinalPrompt
from agents.llm_inference import get_request_result_jf
from routers.utils import ContextIncludedRoute, JFResponse

MainRoute = APIRouter(route_class=ContextIncludedRoute)

@MainRoute.post('/in_trading')
async def in_trading(
        token: str = Body('', description='Internal secret key'),
        customer_input: str = Body('', description='customer email content'),
        account_no: str = Body('', description='customer account number'),
        current_history: str = Body('', description='current conversation history'),
) -> JFResponse:

    if token != SECRET_KEY:
        return JFResponse(no=-1, message="Invalid token", data=None)

    current_history_rounds = len(current_history.split('}{'))
    logger.info(f'Customer input: {customer_input}, customer account number: {account_no}, current history: {current_history}')

    if not customer_input:
        return JFResponse(no=0,
                              message='success',
                              data={"content": "",
                                    "api_resp": "",
                                    "intention": "empty customer input, unrecognisable"})

    # get intention and agent workflow
    result = intention_agent(customer_input, account_no, current_history)
    intention = result['intention']
    filtered_intention_workflow_dict = result['filtered_intention_workflow_dict']
    clarify_question = result['clarify_question']
    logger.info(f'intention: {intention} \n| clarifying question: {clarify_question}')

    if intention == 'customer has not shown a clear intention':
        return JFResponse(no=0,
                          message='success',
                          data={"content": "Could you please provide more context or specify what you would like assistance with?",
                                "api_resp": {},
                                "intention": "customer has not shown a stock market relevant intention"})

    if clarify_question:
        return JFResponse(no=0,
                          message='success',
                          data={"content": clarify_question,
                                "api_resp": {},
                                "intention": "follow up to clarify intention"})
    aggregated_workflow = filtered_intention_workflow_dict[intention]
    workflow_response = run_workflow(account_no, customer_input, current_history, intention, aggregated_workflow)
    if isinstance(workflow_response, JFResponse):
        return workflow_response
    else:
        resp, resp_description = workflow_response['resp'], workflow_response['resp_description']

    logger.info(f'aggregated_workflow_response: , {resp}, description: {resp_description}')

    # final pass to llm to generate final answer using rag info
    final_input = format_prompt(
        prompt_template=FinalPrompt,
        customer_input=customer_input,
        current_history=current_history,
        aggregated_workflow_response=resp,
        aggregated_workflow_resp_description=resp_description
    )
    # logger.info(f'final input generation: {final_input}')
    try:
        chat_completion = get_request_result_jf(final_input,
                                                model='gpt-3.5-turbo',
                                                )

        output_string = chat_completion
        print('Final output: ' + output_string)
        resp = {} if not resp else resp
        return JFResponse(no=0,
                          message='success',
                          data={"content": output_string,
                                "api_resp": resp,
                                "intention": intention,
                                }
                          )
    except:
        logger.error(str(traceback.format_exc()))
        return JFResponse(no=-1, message='error')


@MainRoute.post('/question_suggestion')
async def question_suggestion(
        account_no: str = Body('', description='customer account number'),
        current_history: str = Body('', description='current conversation history'),
) -> JFResponse:
    current_history_rounds = len(current_history.split('}{'))
    logger.info(f'Customer account number: {account_no}, current history rounds: {current_history_rounds}')

    question_categories = {'Stock Positions': 'Show me my overall positions',
                            'Stock Performances': 'How is AAPL.US doing recently?',
                            'Accounts and Balances': 'How much balance do I have available?',
                            'Accounts and Balances': 'Show me my account status.',
                            'Orders': 'What orders have I placed today?'}
    try:
        return JFResponse(no=0,
                      message='success',
                      data={"content": "",
                            "api_resp": question_categories,
                            "intention": "question suggestions",
                            }
                      )
    except:
        logger.error(str(traceback.format_exc()))
        return JFResponse(no=-1, message="error", data=None)

