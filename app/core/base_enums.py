from enum import Enum
from typing import Any


class BaseEnum(Enum):
    """Base enum class with automatic value checking"""

    def __contains__(self, value: Any) -> bool:
        """Check if value is in enum"""
        return value in [item.value for item in self.__class__]

    @classmethod
    def values(cls):
        """Get all enum values"""
        return [item.value for item in cls]

    @classmethod
    def names(cls):
        """Get all enum names"""
        return [item.name for item in cls]

    @classmethod
    def items(cls):
        """Get (name, value) pairs"""
        return [(item.name, item.value) for item in cls]

    @classmethod
    def from_value(cls, value: Any):
        """Get enum item from value"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

    def __str__(self) -> str:
        return str(self.value)
