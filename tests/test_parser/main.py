import logging as log
import redis as r
from models.GELFMessage import GELFMessage
from utils.Parsers import parse_log
import pandas as pd

from utils.utils import load_creds

fn = 'data.csv'

if __name__ == '__main__':
    log.basicConfig(level='DEBUG')

    creds = load_creds()

    redis = r.Redis(
                host=creds.redis.host,
                port=creds.redis.port,
                db=creds.redis.db,
                decode_responses=True,
                charset='utf-8'
                )

    df = pd.read_csv(fn)

    data = df.to_dict('records')

    filters = [
        'T-CUMEVRSH-OTS',
        'T-CUMEVLSH-OTS',
        'T-MAXEVRSH-OTS',
        'T-MAXEVLSH-OTS',
        'DNLD-6-TRANSFER_COMPLETE'
        # 'SHELF'
        ]

    output = open('output.log', 'w')

    i = 1
    # while i < 6000:
    while i < len(data)-1:
        msg = data[len(data)-i]
        msg['_source'] = msg['source']
        msg['short_message'] = msg['message']
        # msg['full_message'] = msg['full_message'].replace(' -  ', '  ').replace('\\', '')

        if not any(word in msg['full_message'] for word in filters):

            if 'TACACS-4-INTRUSION_DETECTION' in msg['full_message']:

                gelf_msg = GELFMessage(**msg)
                msg_parsed = parse_log(gelf_msg, redis)

                # if msg_parsed != msg['message']:
                output.write(f"{msg['full_message']}\n")
                output.write(f'{msg_parsed}\n\n')

        i += 1

    output.close()
