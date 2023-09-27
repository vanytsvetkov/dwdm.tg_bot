import html
import json
import logging
import traceback

import redis as r

import models.Logs
import vars
from models.GELFMessage import GELFMessage
from utils.utils import get_event_id, get_log_level, get_log_prival, is_logType, unformat

with open(f'{vars.BASE}/{vars.DATA_DIR}/{vars.PATTERNS_FILENAME}') as file:
    PATTERNS = json.load(file)


class MessageProcessingError(BaseException):
    def __init__(self, message: str):
        super().__init__(message)


def get_pattern_shelf(typeGroup: str, log: str) -> str:
    global PATTERNS

    level = get_log_level(log)
    match level:
        case 'SECU':
            pattern = PATTERNS.get(typeGroup).get(level).get('COMMON')
        case 'ALM':
            if is_logType('TRC_INPROGRESS', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('TRC_INPROGRESS')
            elif is_logType('OSRP_BLKD', log):
                prival = get_log_prival(log)
                pattern = PATTERNS.get(typeGroup).get(level).get('OSRP_BLKD').get(prival, PATTERNS.get(typeGroup).get('DEFAULT'))
            elif is_logType('OPTICAL_SF', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('OPTICAL_SF')
            elif is_logType('SIGNAL_DEGRADE_OCH', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('SIGNAL_DEGRADE_OCH')
            elif is_logType('PWR_REDUCED', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('PWR_REDUCED')
            elif is_logType('PWR', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('PWR')
            elif is_logType('LOCH', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('LOCH')
            elif is_logType('SEC_INTRUDER', log):
                pattern = PATTERNS.get(typeGroup).get(level).get('SEC_INTRUDER')
            elif any(is_logType(cond, log) for cond in ["LASER_FREQ_OOR", "LOS_OTS", "OCI_ODU", "T_TSUM_OTS", "LOWOPTRLOSOUT_OTS", "STC_OTS"]):
                pattern = PATTERNS.get(typeGroup).get(level).get('COMMON')
            else:
                pattern = PATTERNS.get(typeGroup).get('DEFAULT')

        case 'DBCHG':
            pattern = PATTERNS.get(typeGroup).get(level).get('COMMON')

        case _:
            pattern = PATTERNS.get(typeGroup).get('DEFAULT')

    return pattern


def get_pattern_ws(typeGroup: str, log: str) -> str:
    global PATTERNS
    pattern = str()
    event_id = get_event_id(log)
    if event_id is not str():
        match event_id:
            # case '24-001' | '39-003' | '39-006':
            #     pattern = PATTERNS.get(typeGroup).get(event_id, None)
            case _:
                pattern = PATTERNS.get(typeGroup).get(event_id, str())
    else:
        if is_logType('TACACS-4-INTRUSION_DETECTION', log):
            pattern = PATTERNS.get(typeGroup).get('TACACS-4-INTRUSION_DETECTION', str())

    if pattern is str():
        pattern = PATTERNS.get(typeGroup).get('DEFAULT')

    return pattern


def preprocess_log(log: GELFMessage, redis: r.Redis) -> tuple:
    typeGroup = redis.get(f'{vars.PROJECT_NAME}.mcp.devices.{log.source_}.typeGroup')
    if typeGroup is None:
        logging.info('typeGroup is undefined for message')
        raise MessageProcessingError(log.full_message)

    pattern = str()
    match typeGroup:
        case 'Ciena6500':
            pattern = get_pattern_shelf(typeGroup, log.full_message)
            log.full_message = log.full_message.replace(' -  ', '  ').replace('\\', '')
        case 'CienaWaveserver':
            pattern = get_pattern_ws(typeGroup, log.full_message)
            log.full_message = log.full_message.replace('   ', '  ')

    if pattern is str():
        logging.info('Pattern is undefined for message')
        raise MessageProcessingError(log.full_message)

    return typeGroup, pattern, log.full_message


def gen_message_shelf(log: models.Logs.LogCiena6500) -> str:
    message = str()
    match log.LEVEL:
        case 'ALM':
            message = (
                    f'<i>{log.LEVEL}</i> [<b>{", ".join((log.SEVERITY, log.SERVICE_AFFECTED))}</b>]: '
                    f'<i>{log.DESCRIPTION}</i> at unit <code>{log.RESOURCE}</code>.' +
                    (f'\nAdditional Info: <i>{log.ADDITIONALINFO}</i>.' if log.ADDITIONALINFO else '')
                )
    return message


def gen_message_ws(log: models.Logs.LogCienaWaveserver, src: str, redis: r.Redis) -> str:
    message = str()
    match log.EVENT_ID:
        case '39-003' | '39-006':
            AffectedServices = redis.smembers(f'{vars.PROJECT_NAME}.mcp.devices.{src}.tpes.{log.RESOURCE.replace("/", "-")}.fres')
            message = (
                f'<code>{log.RESOURCE}</code> <i>{log.ERROR}</i>.' +
                (f"\nAffected Services: {', '.join([html.escape(af) for af in AffectedServices])}" if AffectedServices else '')
                )
        case _:
            message = log.MSG
    return message


def gen_message(typeGroup: str, log: models.Logs.Log | models.Logs.LogCiena6500 | models.Logs.LogCienaWaveserver, src: str, redis: r.Redis) -> str:
    message = str()
    match typeGroup:
        case 'Ciena6500':
            message = gen_message_shelf(log)

        case 'CienaWaveserver':
            message = gen_message_ws(log, src, redis)

    return message


def parse_log(msg: GELFMessage, redis: r.Redis) -> str:
    msg_parsed = None

    try:
        typeGroup, pattern, preprocessed_log = preprocess_log(msg, redis)

        logModel = getattr(models.Logs, f'Log{typeGroup}', models.Logs.Log)
        log = logModel.model_validate(unformat(preprocessed_log, pattern))
        if log.processed:
            msg_parsed = gen_message(typeGroup, log, msg.source_, redis)
        else:
            raise MessageProcessingError(msg.full_message)

    except MessageProcessingError as e:
        logging.info('Failed to process message')
        logging.info(e)
    except Exception:
        logging.debug(traceback.format_exc())
    finally:
        return msg_parsed if msg_parsed else html.escape(msg.short_message)
