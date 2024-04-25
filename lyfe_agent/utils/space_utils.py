"""Utils for spatial computation."""


def get_nearby_entities_action_info(nearby_creature):
    """
    Retrieves action information about entities that are nearby.

    Parameters:
        nearby_creature (list): List of nearby creatures.
    """
    # TODO reorg: Replace with better implementation that doesn't rely on globalInfo.
    # nearby_action_info = []
    # for name in nearby_creature:
    #     if (
    #         name in globalInfo.action_info.keys()
    #         and globalInfo.action_info[name] not in NONCE
    #     ):
    #         nearby_action_info.extend(globalInfo.action_info[name])
    # return list(set(nearby_action_info))
    return list()
