import asyncio
import logging as log
import sys
from datetime import timedelta

import redis as r

import vars
from interactors.McpAPI import McpAPI
from utils.Senders import send_tg_msg
from utils.utils import load_creds

if __name__ == "__main__":
    log.basicConfig(level=vars.LOG_LEVEL)

    log.info('Loading credits')
    creds = load_creds()

    REPORT_RECIPIENT = None

    if len(sys.argv) > 2:
        REPORT_RECIPIENT = {
            'chat_id': int(sys.argv[1]),
            'msg_id': int(sys.argv[2])
            }

    redis = r.Redis(host=creds.redis.host, port=creds.redis.port, db=creds.redis.db)
    mcp = McpAPI(creds)

    # Upload Ciena 6500 to Redis

    if (get := mcp.get_Ciena6500()).success:
        for device in get.response.data:
            for shelf in device.attributes.memberShelvesData:
                shelfName = f'{device.attributes.displayData.displayName}:SHELF-{shelf.shelfNumber}'

                redis.set(f'{vars.PROJECT_NAME}.mcp.devices.{shelf.shelfIP}.displayName', shelfName)
                redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{shelf.shelfIP}.displayName', timedelta(days=7))

                redis.set(f'{vars.PROJECT_NAME}.mcp.devices.{shelf.shelfIP}.typeGroup', device.attributes.typeGroup)
                redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{shelf.shelfIP}.typeGroup', timedelta(days=7))

                redis.set(f'{vars.PROJECT_NAME}.mcp.devices.{shelf.shelfIP}.resourceType', device.attributes.resourceType)
                redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{shelf.shelfIP}.resourceType', timedelta(days=7))

    # Upload Ciena WS to Redis

    if (get := mcp.get_CienaWS()).success:
        for device in get.response.data:

            redis.set(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.displayName', device.attributes.displayData.displayName)
            redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.displayName', timedelta(days=7))

            redis.set(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.typeGroup', device.attributes.typeGroup)
            redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.typeGroup', timedelta(days=7))

            redis.set(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.resourceType', device.attributes.resourceType)
            redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.resourceType', timedelta(days=7))

            if (tpes := mcp.get_tpes(networkConstructId=device.id)).success:
                for tpe in tpes.response.data:
                    if tpe.attributes.additionalAttributes.alarmResourceId:
                        supported_fresName = set()

                        # get direct userLabel, if available
                        if tpe.attributes.additionalAttributes.userLabel:
                            supported_fresName.add(tpe.attributes.additionalAttributes.userLabel)

                        # get all supported fres by tpe.relationships.clientTpes
                        for clientTpe in tpe.relationships.clientTpes.data:
                            if (clientFres := mcp.get_supported_fres(clientTpe.id)).success:
                                for clientFre in clientFres.response.data:
                                    if clientFre.attributes.userLabel:
                                        supported_fresName.add(clientFre.attributes.userLabel)

                        # get all supported fres by tpe.id
                        # ex. Transport Clients for Photonic port or Clients for channels
                        # if (fres := mcp.get_supported_fres(tpe.id)).success:
                        #     for fre in fres.response.data:
                        #         if fre.attributes.userLabel:
                        #             supported_fresName.add(fre.attributes.userLabel)

                        if supported_fresName:
                            for resource in tpe.attributes.additionalAttributes.alarmResourceId.split(','):
                                redis.delete(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.tpes.{resource.lower()}.fres')
                                redis.sadd(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.tpes.{resource.lower()}.fres', *supported_fresName)
                                redis.expire(f'{vars.PROJECT_NAME}.mcp.devices.{device.attributes.ipAddress}.tpes.{resource.lower()}.fres', timedelta(days=7))

    redis.close()

    if REPORT_RECIPIENT:
        asyncio.run(send_tg_msg(text='Update successful.', chat_id=REPORT_RECIPIENT['chat_id'], reply_to_message_id=REPORT_RECIPIENT['msg_id'], token=creds.tg[vars.BOT_NAME].token))
