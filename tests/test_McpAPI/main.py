from interactors.McpAPI import McpAPI
import logging
from utils.utils import load_creds

logging.basicConfig(level=logging.DEBUG)

credits = load_creds()

mcp = McpAPI(credits)

# token = mcp.get_token()

# networkConstructs = mcp.get_networkConstructs()

if (get := mcp.get_CienaWS()).success:
    for device in get.response.data:
        print(device.attributes.name)
        if (tpes := mcp.get_tpes(networkConstructId=device.id)).success:

            # for port in tpe.response.data:
            #     print(port.attributes.displayAlias, port.id)
            #     channels = mcp.get_supported_fres(port.id)
            #     for channel in channels.response.data:
            #         print(channel.attributes.displayData.displayName)
            for tpe in tpes.response.data:
                if tpe.attributes.nativeName:
                    supported_fresName = set()
                    for clientTpe in tpe.relationships.clientTpes.data:
                        if (clientFres := mcp.get_supported_fres(clientTpe.id)).success:
                            for clientFre in clientFres.response.data:
                                if clientFre.attributes.userLabel:
                                    supported_fresName.add(clientFre.attributes.userLabel)

                    if supported_fresName:
                        print(tpe.attributes.nativeName, supported_fresName)

        break
