from datetime import timedelta

import redis as r
import logging as log
from interactors.McpAPI import McpAPI
from utils.utils import load_credits


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)

    log.info('Loading credits')
    credits = load_credits()

    redis = r.Redis(host=credits.redis.host, port=credits.redis.port, db=credits.redis.db)
    mcp = McpAPI(credits)

    # Upload Ciena 6500 to Redis

    if not (get := mcp.get_Ciena6500()).errors:
        for device in get.response.data:
            for shelf in device.attributes.memberShelvesData:
                shelfName = f'{device.attributes.displayData.displayName}:SHELF-{shelf.shelfNumber}'
                print(shelfName, shelf.shelfIP)
                redis.set(f'dwdm.tg_bot.mcp.devices.{shelf.shelfIP}.displayName', shelfName)
                redis.expire(f'dwdm.tg_bot.mcp.devices.{shelf.shelfIP}.displayName', timedelta(days=7))

                redis.set(f'dwdm.tg_bot.mcp.devices.{shelf.shelfIP}.typeGroup', device.attributes.typeGroup)
                redis.expire(f'dwdm.tg_bot.mcp.devices.{shelf.shelfIP}.typeGroup', timedelta(days=7))

                redis.set(f'dwdm.tg_bot.mcp.devices.{shelf.shelfIP}.resourceType', device.attributes.resourceType)
                redis.expire(f'dwdm.tg_bot.mcp.devices.{shelf.shelfIP}.resourceType', timedelta(days=7))

    # Upload Ciena WS to Redis

    if not (get := mcp.get_CienaWS()).errors:
        for device in get.response.data:
            print(device.attributes.displayData.displayName, device.attributes.ipAddress)

            redis.set(f'dwdm.tg_bot.mcp.devices.{device.attributes.ipAddress}.displayName', device.attributes.displayData.displayName)
            redis.expire(f'dwdm.tg_bot.mcp.devices.{device.attributes.ipAddress}.displayName', timedelta(days=7))

            redis.set(f'dwdm.tg_bot.mcp.devices.{device.attributes.ipAddress}.typeGroup', device.attributes.typeGroup)
            redis.expire(f'dwdm.tg_bot.mcp.devices.{device.attributes.ipAddress}.typeGroup', timedelta(days=7))

            redis.set(f'dwdm.tg_bot.mcp.devices.{device.attributes.ipAddress}.resourceType', device.attributes.resourceType)
            redis.expire(f'dwdm.tg_bot.mcp.devices.{device.attributes.ipAddress}.resourceType', timedelta(days=7))
