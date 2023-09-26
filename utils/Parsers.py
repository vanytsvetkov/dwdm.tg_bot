import logging
import re
from dataclasses import asdict, dataclass

from models import GELFMessage
from utils.utils import escape_html_tags, unformat


# logging.basicConfig(level='DEBUG')


@dataclass
class Log:
    PRIVAL: int = int()
    VERSION: int = int()
    TIMESTAMP: str = str()
    SOURCE: str = str()
    LEVEL: str = str()
    SITE: str = str()
    SHELF: str = str()
    PIM: str = str()
    RESOURCE: str = str()
    DATE: str = str()
    TIME: str = str()
    YEAR: str = str()
    LOGNAME: str = str()
    LOGEVENT: str = str()
    UID: str = str()
    UPC: str = str()
    PORTTYPE: str = str()
    PORTADDR: str = str()
    STATUS: str = str()
    EVTDESCR: str = str()
    CONDITION_TYPE: str = str()
    SEVERITY: str = str()
    LOCATION: str = str()
    DIRECTION: str = str()
    DESCRIPTION: str = str()
    PORT_MODE: str = str()
    NE_ALARM_ID: str = str()
    MODE: str = str()
    ADDITIONALINFO: str = str()
    WAVELENGTH: str = str()
    SERVICE_AFFECTED: str = 'NSA'
    DBCHGSEQ: str = str()
    USERID: str = str()
    PRIORITY: str = str()
    ED_TELEMETRY: str = str()
    LOSTHRES: str = str()
    TELEPWR: str = str()
    TELEMODE: str = str()
    SIGNALPWR: str = str()
    RXPWR: str = str()
    SPANLOSS: str = str()
    MSG: str = str()
    processed: bool = False


def is_shelf(obj: str | list | dict) -> bool:
    if isinstance(obj, dict):
        return obj.get('SHELF')
    else:
        return 'SHELF' in obj


def is_logType(cond, text: str) -> bool:
    return cond in text


def get_log_level(text: str) -> str:
    match = re.search(r'\b(?:ALM|SECU|DBCHG)\b', text)
    return match.group() if match else str()


def get_log_prival(text: str) -> str:
    match = re.search(r'<(\d+)>', text)
    return match.group(1) if match else str()


def parse_log(msg: GELFMessage) -> str:
    msg_parsed = None

    try:
        pattern = None
        level = None

        if is_shelf(msg.full_message):
            PATTERNS = {
                'SECU': {
                    'COMMON': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM} {RESOURCE}:{DATE},{TIME}:YEAR={YEAR},LOGNAME={LOGNAME},LOGEVENT={LOGEVENT},UID={UID},UPC={UPC},PORTTYPE={PORTTYPE},PORTADDR={PORTADDR},STATUS={STATUS}<var1>,EVTDESCR={EVTDESCR}</var1>',
                    },
                'ALM': {
                    'TRC_INPROGRESS': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{CONDITION_TYPE},{SEVERITY},{DATE},{TIME},{LOCATION},{DIRECTION},,,:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}',
                    'OSRP_BLKD': {
                        '131': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}<var1>,ADDITIONALINFO="{ADDITIONALINFO}"</var1>',
                        '132': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{CONDITION_TYPE},{SEVERITY},{DATE},{TIME},{LOCATION},{DIRECTION},,,:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}<var1>,ADDITIONALINFO="{ADDITIONALINFO}"</var1>',
                        '133': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{CONDITION_TYPE},{SEVERITY},{DATE},{TIME},{LOCATION},{DIRECTION}<var2>,,,</var2>:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}<var1>,ADDITIONALINFO="{ADDITIONALINFO}"</var1>',
                        },
                    'OPTICAL_SF': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{CONDITION_TYPE},{SEVERITY},{DATE},{TIME},{LOCATION},{DIRECTION},,,:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE},WAVELENGTH={WAVELENGTH}',
                    'SIGNAL_DEGRADE_OCH': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE},ADDITIONALINFO="{ADDITIONALINFO}"',
                    'SEC_INTRUDER': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}',
                    'PWR_REDUCED': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION},,,:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}',
                    'PWR': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}',
                    'LOCH': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}',
                    'COMMON': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}'
                    },
                'DBCHG': {
                    'COMMON': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  DBCHGSEQ={DBCHGSEQ},DATE={DATE},TIME={TIME},USERID={USERID},SOURCE=,PRIORITY={PRIORITY},STATUS={STATUS}:ED-TELEMETRY:{ED_TELEMETRY}::LOSTHRES={LOSTHRES},TELEPWR={TELEPWR},TELEMODE={TELEMODE},SIGNALPWR={SIGNALPWR},RXPWR={RXPWR},SPANLOSS={SPANLOSS}:{MSG},',
                    },
                'DEFAULT': '<{PRIVAL}>{VERSION} {TIMESTAMP} {SOURCE} {LEVEL} {SITE}:{SHELF} {PIM}  {RESOURCE}:{SEVERITY},{CONDITION_TYPE},{SERVICE_AFFECTED},{DATE},{TIME},{LOCATION},{DIRECTION}:"{DESCRIPTION}",{PORT_MODE}:{NE_ALARM_ID},:YEAR={YEAR},MODE={MODE}'
                }

            msg.full_message = msg.full_message.replace(' -  ', '  ').replace('\\', '')

            match (level := get_log_level(msg.full_message)):
                case 'SECU':
                    pattern = PATTERNS.get(level).get('COMMON')
                case 'ALM':
                    if is_logType('TRC_INPROGRESS', msg.full_message):
                        pattern = PATTERNS.get(level).get('TRC_INPROGRESS')
                    elif is_logType('OSRP_BLKD', msg.full_message):
                        prival = get_log_prival(msg.full_message)
                        pattern = PATTERNS.get(level).get('OSRP_BLKD').get(prival, PATTERNS.get('DEFAULT'))
                    elif is_logType('OPTICAL_SF', msg.full_message):
                        pattern = PATTERNS.get(level).get('OPTICAL_SF')
                    elif is_logType('SIGNAL_DEGRADE_OCH', msg.full_message):
                        pattern = PATTERNS.get(level).get('SIGNAL_DEGRADE_OCH')
                    elif is_logType('PWR_REDUCED', msg.full_message):
                        pattern = PATTERNS.get(level).get('PWR_REDUCED')
                    elif is_logType('PWR', msg.full_message):
                        pattern = PATTERNS.get(level).get('PWR')
                    elif is_logType('LOCH', msg.full_message):
                        pattern = PATTERNS.get(level).get('LOCH')
                    elif is_logType('SEC_INTRUDER', msg.full_message):
                        pattern = PATTERNS.get(level).get('SEC_INTRUDER')
                    elif any(is_logType(cond, msg.full_message) for cond in ["LASER_FREQ_OOR", "LOS_OTS", "OCI_ODU", "T_TSUM_OTS", "LOWOPTRLOSOUT_OTS", "STC_OTS"]):
                        pattern = PATTERNS.get(level).get('COMMON')
                    else:
                        pattern = PATTERNS.get('DEFAULT')

                case 'DBCHG':
                    pattern = PATTERNS.get(level).get('COMMON')

                case _:
                    pattern = PATTERNS.get('DEFAULT')

        if pattern and level:
            log = Log(**unformat(msg.full_message, pattern))
            if log.processed:
                if is_shelf(asdict(log)):
                    match level:
                        case 'ALM':
                            msg_parsed = (
                                f'<em>{log.LEVEL}</em> [<b>{", ".join((log.SEVERITY, log.SERVICE_AFFECTED))}</b>]:'
                                f'<em>{log.DESCRIPTION}</em> at unit <code>{log.RESOURCE}</code>.' +
                                (f'\nAdditional Info: <em>{log.ADDITIONALINFO}</em>.' if log.ADDITIONALINFO else '')
                                )

                            # print(msg.full_message)
                            # print(pattern)
                            # print(log)
                            # print(msg_parsed)
                            # print('\n')
            # else:
            #     print(msg.full_message)
            #     print(pattern)
            #     print(log)
            #     print('\n')

    except Exception as e:
        logging.info('Failed to process message.')
        # logging.info(msg.full_message)
        # traceback.print_exc()
    finally:
        return msg_parsed if msg_parsed else escape_html_tags(msg.short_message)
