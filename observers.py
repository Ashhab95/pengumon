from .imports import *
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from message import *

from abc import ABC, abstractmethod

class HealthObserver(ABC):
    """
    Abstract base class for observing health changes in a Pokemon.
    Subclasses must implement `on_health_changed`.
    """
    @abstractmethod
    def on_health_changed(self, subject, old_hp: int, new_hp: int) -> None:
        pass
    
class BattleMessageNotifier(HealthObserver):
    """
    Notifies a player with battle messages when a Pokemon health changes.
    Appends messages to a shared message buffer.
    """
    def __init__(self, player, message_buffer: list[Message]):
        self.__player = player
        self.__messages = message_buffer

    def on_health_changed(self, subject, old_hp, new_hp) -> None:
        """
        Sends a message if the subject takes damage or gets healed.
        Messages are stored in the provided message buffer.
        """
        if new_hp < old_hp:
            self.__messages.append(ServerMessage(
                self.__player,
                f"{subject.name} took damage! ({old_hp} → {new_hp})"
            ))
        elif new_hp > old_hp:
            self.__messages.append(ServerMessage(
                self.__player,
                f"{subject.name} was healed! ({old_hp} → {new_hp})"
            ))