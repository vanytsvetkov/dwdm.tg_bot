from models.GELFMessage import GELFMessage
from utils.Parsers import parse_log
import pandas as pd

fn = 'data.csv'

if __name__ == '__main__':
    df = pd.read_csv(fn)

    data = df.to_dict('records')

    filters = [
        'T-CUMEVRSH-OTS',
        'T-CUMEVLSH-OTS',
        'T-MAXEVRSH-OTS',
        'T-MAXEVLSH-OTS'
        ]

    i = 1
    # while i < 10:
    output = open('output.log', 'w')
    while i < len(data)-1:
        msg = data[len(data)-i]
        msg['short_message'] = msg['message']
        # msg['full_message'] = msg['full_message'].replace(' -  ', '  ').replace('\\', '')

        if not any(word in msg['full_message'] for word in filters):

            gelf_msg = GELFMessage(**msg)
            msg_parsed = parse_log(gelf_msg)

            if msg_parsed != msg['message']:
                output.write(f"{msg['full_message']}\n")
                output.write(f'{msg_parsed}\n\n')

        i += 1

    output.close()
