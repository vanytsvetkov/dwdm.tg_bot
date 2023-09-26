import re
import pandas as pd

fn = 'data.csv'

if __name__ == '__main__':
    df = pd.read_csv(fn)
    data = df.to_dict('records')

    syslog_types = set()
    for msg in data:
        syslog_type = re.findall(r'<(\d+)>', msg['full_message'])
        if syslog_type:
            if syslog_type[0] not in syslog_types:
                print(msg['full_message'])

            syslog_types.add(syslog_type[0])

    print(syslog_types)
