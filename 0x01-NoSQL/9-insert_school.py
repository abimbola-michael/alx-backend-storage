#!/usr/bin/env python3
"""
 Insert a document in Python
"""


def insert_school(mongo_collection, **kwargs):
    """
     function that inserts a new document in
     a collection based on kwargs
    """
    mongo_collection.insert_one(kwargs)