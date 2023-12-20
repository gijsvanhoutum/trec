from PyQt5.QtCore import QObject
from abc import ABCMeta


class MetaClass(type(QObject),ABCMeta):
    """
    Because otherwise there would be a metaclass conflict. 
    """