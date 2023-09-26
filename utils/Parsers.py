import json
import logging
import re
import traceback
import redis as r
import models.Logs
import vars
from models.GELFMessage import GELFMessage
from utils.utils import escape_html_tags, unformat

with open(f'{vars.BASE}/{vars.DATA_DIR}/{vars.PATTERNS_FILENAME}') as file:
    PATTERNS = json.load(file)


class MessageProcessingError(BaseException):
    def __init__(self, message: str):
        super().__init__(message)


def is_logType(cond, text: str) -> bool:
    match = re.match(fr'\W{cond}\W', text)
    return bool(match)


def get_log_level(text: str) -> str:
    match = re.search(r'\b(?:ALM|SECU|DBCHG)\b', text)
    return match.group() if match else str()


def get_event_id(text: str) -> str:
    match = re.search(r'EVENT-ID="(\d+-\d+)"', text)
    return match.group(1) if match else str()


def get_log_prival(text: str) -> str:
    match = re.search(r'<(\d+)>', text)
    return match.group(1) if match else str()


def get_pattern_for_shelf(log: str) -> str:
    global PATTERNS

    level = get_log_level(log)
    match level:
        case 'SECU':
            pattern = PATTERNS.get('Ciena6500').get(level).get('COMMON')
        case 'ALM':
            if is_logType('TRC_INPROGRESS', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('TRC_INPROGRESS')
            elif is_logType('OSRP_BLKD', log):
                prival = get_log_prival(log)
                pattern = PATTERNS.get('Ciena6500').get(level).get('OSRP_BLKD').get(prival, PATTERNS.get('Ciena6500').get('DEFAULT'))
            elif is_logType('OPTICAL_SF', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('OPTICAL_SF')
            elif is_logType('SIGNAL_DEGRADE_OCH', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('SIGNAL_DEGRADE_OCH')
            elif is_logType('PWR_REDUCED', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('PWR_REDUCED')
            elif is_logType('PWR', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('PWR')
            elif is_logType('LOCH', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('LOCH')
            elif is_logType('SEC_INTRUDER', log):
                pattern = PATTERNS.get('Ciena6500').get(level).get('SEC_INTRUDER')
            elif any(is_logType(cond, log) for cond in ["LASER_FREQ_OOR", "LOS_OTS", "OCI_ODU", "T_TSUM_OTS", "LOWOPTRLOSOUT_OTS", "STC_OTS"]):
                pattern = PATTERNS.get('Ciena6500').get(level).get('COMMON')
            else:
                pattern = PATTERNS.get('Ciena6500').get('DEFAULT')

        case 'DBCHG':
            pattern = PATTERNS.get('Ciena6500').get(level).get('COMMON')

        case _:
            pattern = PATTERNS.get('Ciena6500').get('DEFAULT')

    return pattern


def get_pattern_for_ws(log: str) -> str:
    global PATTERNS
    event_id = get_event_id(log)
    match event_id:
        case _:
            pattern = PATTERNS.get('CienaWaveserver').get('DEFAULT')

    return pattern


def preprocess_log(log: GELFMessage, redis: r.Redis) -> tuple:
    typeGroup = redis.get(f'{vars.PROJECT_NAME}.mcp.devices.{log.source_}.typeGroup')
    if typeGroup is None:
        logging.info('typeGroup is undefined for message')
        raise MessageProcessingError(msg.full_message)

    pattern = str()
    match typeGroup:
        case 'Ciena6500':
            pattern = get_pattern_for_shelf(log.full_message)
            log.full_message = log.full_message.replace(' -  ', '  ').replace('\\', '')
        case 'CienaWaveserver':
            pattern = get_pattern_for_ws(log.full_message)

    if pattern is str():
        logging.info('Pattern is undefined for message')
        raise MessageProcessingError(msg.full_message)

    return typeGroup, pattern, log.full_message


def gen_message(typeGroup: str, log: models.Logs.Log | models.Logs.LogCiena6500 | models.Logs.LogCienaWaveserver) -> str:
    message = str()
    match typeGroup:
        case 'Ciena6500':
            match log.LEVEL:
                case 'ALM':
                    message = (
                            f'<em>{log.LEVEL}</em> [<b>{", ".join((log.SEVERITY, log.SERVICE_AFFECTED))}</b>]: '
                            f'<em>{log.DESCRIPTION}</em> at unit <code>{log.RESOURCE}</code>.' +
                            (f'\nAdditional Info: <em>{log.ADDITIONALINFO}</em>.' if log.ADDITIONALINFO else '')
                        )
        case 'CienaWaveserver':
            match log.EVENT_ID:
                case _:
                    message = log.MSG

    return message


def parse_log(msg: GELFMessage, redis: r.Redis) -> str:
    msg_parsed = None

    try:
        typeGroup, pattern, preprocessed_log = preprocess_log(msg, redis)

        logModel = getattr(models.Logs, f'Log{typeGroup}', models.Logs.Log)
        log = logModel.model_validate(unformat(preprocessed_log, pattern))
        if log.processed:
            msg_parsed = gen_message(typeGroup, log)
        else:
            raise MessageProcessingError(msg.full_message)

    except MessageProcessingError as e:
        logging.info('Failed to process message')
        logging.info(e)
    except Exception:
        logging.debug(traceback.format_exc())
    finally:
        return msg_parsed if msg_parsed else escape_html_tags(msg.short_message)
