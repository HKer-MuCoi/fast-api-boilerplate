#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define an Abstract Base Class (ABC) for models
"""
from weakref import WeakValueDictionary

from sqlalchemy import inspect  # noqa
from sqlalchemy.orm import aliased  # noqa

from app.extensions import db


class MetaBaseModel(db.Model.__class__):
    """Define a metaclass for the BaseModel
    Implement `__getitem__` for managing aliases"""

    def __init__(cls, *args):
        super().__init__(*args)
        cls.aliases = WeakValueDictionary()

    def __getitem__(cls, key):
        try:
            alias = cls.aliases[key]
        except KeyError:
            alias = aliased(cls)
            cls.aliases[key] = alias
        return alias


class BaseModel:
    """Generalize __init__, __repr__ and to_json
    Based on the models columns"""

    print_filter = ()

    def __repr__(self):
        """Define a base way to print models
        Columns inside `print_filter` are excluded"""
        return "%s(%s)" % (
            self.__class__.__name__,
            {
                column: value
                for column, value in self.to_dict().items()
                if column not in self.print_filter
            },
        )

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(e)
        return self

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(e)