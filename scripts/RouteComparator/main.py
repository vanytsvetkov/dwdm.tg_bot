import pandas as pd
import dataframe_image as dfi
import logging as log
from interactors.McpAPI import McpAPI
from utils.utils import load_creds, get_df_from_gt


REPORT_FN = 'comparator_result'
SHEET_NAME = 'ROUTES'

COL_WAVE_NAME = 0
COL_WAVE_RESILIENSE = 1
COL_WAVE_CLIENT = 2
COL_WAVE_NODES = 3

VALID_PREFIXES = ["G-", "GBL-", "RUN-", "TG-", "TG-SGP-"]


def is_valid(name: str) -> bool:
    return any(name.startswith(prefix) for prefix in VALID_PREFIXES)


if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)

    creds = load_creds()

    mcp = McpAPI(creds)

    # Get reference dataset from Google Tables

    df = get_df_from_gt(sheet_id=creds.gtable.sheet_id, sheet_names=[SHEET_NAME])

    dataset = df[SHEET_NAME]

    reference_nodes = {}
    reference_resilienceLevels = {}
    reference_customers = {}

    # Get probes dataset from MCP

    probe_nodes = {}
    probe_resilienceLevels = {}
    probe_customers = {}

    for _, row in dataset.iterrows():
        wave = row.iloc[COL_WAVE_NAME]
        if is_valid(wave):
            nodes = row.iloc[COL_WAVE_NODES:]
            reference_nodes.setdefault(wave, set(node for node in nodes if node))

            resilienceLevel = row.iloc[COL_WAVE_RESILIENSE]
            reference_resilienceLevels.setdefault(wave, resilienceLevel)

            customer = row.iloc[COL_WAVE_CLIENT]
            reference_customers.setdefault(wave, customer)

            get = mcp.get_freID(displayName=wave, serviceClass=['Photonic'])
            if get.success:
                for fre in get.response.data:
                    serviceTopology = mcp.get_serviceTopology(id_=fre.id)
                    if serviceTopology.success:
                        nodes = {
                            neName for node in serviceTopology.response.included
                            if (neName := node.attributes.locations[0].neName)
                            }

                        probe_nodes.setdefault(wave, nodes)
                        probe_resilienceLevels.setdefault(wave, serviceTopology.response.data.attributes.resilienceLevel)
                        probe_customers.setdefault(wave, serviceTopology.response.data.attributes.customerName)
                    break

            break

    # Comparing datasets

    # compare_nodes = {}
    # compare_resilienceLevels = {}
    # compare_customers = {}

    # for wave in reference_nodes:
    #     compare_nodes.setdefault(wave, reference_nodes[wave].issubset(probe_nodes[wave]))
    #     compare_resilienceLevels.setdefault(wave, reference_resilienceLevels[wave] == probe_resilienceLevels[wave])
    #     compare_customers.setdefault(wave, reference_customers[wave] == probe_customers[wave])

    # Split reference dataset by customer types
    prev_split_indx = 0
    splitIndexes = list(df.index[df.iloc[:, PathsIndex].isna()][1:]) + [-1]

    # Generate table plots
    pd.set_option("display.max_column", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option('display.width', -1)
    pd.set_option('display.max_rows', None)


