from commons.cfg_loader import email_cfg
import requests
import aiohttp
from data.mail_processing import mail_cleaning


async def a_get_email_history(task_id) -> str:
    url = email_cfg.get('history_email_url') + str(task_id)

    headers = {
        'authority': 'mailmanage.worth2own.com',
        'accept': 'application/json',
        'auth': 'feefwqdqwudbweidbqwid'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response = await response.json()
                json_response = response['data']['row']
                history = []
                for item in json_response:
                    if item['type'] == 'accept':
                        history.append('customer: '+ mail_cleaning(item['content']))
                    elif item['type'] == 'send':
                        history.append('you: '+ mail_cleaning(item['content']))
                return history
            else:
                print(f"Failed to retrieve data: {response.status} - {response.reason}")
                return ''


if __name__ == '__main__':
    import asyncio
    task_id = '609055'
    a_get_email_history(task_id)
    result = asyncio.run(a_get_email_history(609055))
    print('result', result)