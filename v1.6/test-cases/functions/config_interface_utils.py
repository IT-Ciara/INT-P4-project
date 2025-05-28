import json

#========================================================================================================================
"""Utility functions for managing and loading interfaces from JSON files.
This module provides a function to load interfaces from a specified JSON file."""
#========================================================================================================================

def get_interfaces(file_name):
    """
    Load interfaces from a JSON file.
    :param file_name: Name of the JSON file (without extension) to load interfaces from.
    :return: List of interfaces loaded from the JSON file.
    """
    with open(f'./functions/{file_name}.json') as f:
        target = json.load(f)
    interfaces = list(target.values())
    # print(interfaces)
    return interfaces