"""Representation of a WeMo CrockPot device."""
from __future__ import annotations

from enum import IntEnum
from typing import Any

from .api.service import RequiredService
from .switch import Switch


# These enums were derived from the CrockPot.basicevent.GetCrockpotState()
# service call. Thus these names/values were not chosen randomly and the
# numbers have meaning.
class CrockPotMode(IntEnum):
    """Modes for the CrockPot."""

    # pylint: disable=invalid-name
    Off = 0
    Warm = 50
    Low = 51
    High = 52


MODE_NAMES = {
    CrockPotMode.Off: "Turned Off",
    CrockPotMode.Warm: "Warm",
    CrockPotMode.Low: "Low",
    CrockPotMode.High: "High",
}


class CrockPot(Switch):
    """WeMo Crockpot."""

    EVENT_TYPE_COOKED_TIME = "cookedTime"
    EVENT_TYPE_MODE = "mode"
    EVENT_TYPE_TIME = "time"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a WeMo CrockPot device."""
        super().__init__(*args, **kwargs)
        self._attributes: dict[str, str] = {}

    @property
    def _required_services(self) -> list[RequiredService]:
        return super()._required_services + [
            RequiredService(
                name="basicevent",
                actions=["GetCrockpotState", "SetCrockpotState"],
            ),
        ]

    def update_attributes(self) -> None:
        """Request state from device."""
        state_attributes = self.basicevent.GetCrockpotState()

        # Only update our state on complete updates from the device
        if (
            state_attributes is not None
            and state_attributes["mode"] is not None
            and state_attributes["time"] is not None
            and state_attributes["cookedTime"] is not None
        ):
            self._attributes = state_attributes
            self._state = self.mode

    def subscription_update(self, _type: str, _params: str) -> bool:
        """Handle reports from device."""
        if _type == self.EVENT_TYPE_MODE:
            self._attributes['mode'] = _params
            self._state = self.mode
            return True
        if _type == self.EVENT_TYPE_TIME:
            self._attributes['time'] = _params
            return True
        if _type == self.EVENT_TYPE_COOKED_TIME:
            self._attributes['cookedTime'] = _params
            return True

        return super().subscription_update(_type, _params)

    @property
    def mode(self) -> CrockPotMode:
        """Return the mode of the device."""
        return CrockPotMode(int(self._attributes.get('mode', '0')))

    @property
    def mode_string(self) -> str:
        """Return the mode of the device as a string."""
        return MODE_NAMES.get(self.mode, "Unknown")

    @property
    def remaining_time(self) -> int:
        """Return the remaining time in minutes."""
        return int(self._attributes.get('time', '0'))

    @property
    def cooked_time(self) -> int:
        """Return the cooked time in minutes."""
        return int(self._attributes.get('cookedTime', '0'))

    def get_state(self, force_update: bool = False) -> int:
        """Return 0 if off and 1 if on."""
        # The base implementation using GetBinaryState doesn't work for
        # CrockPot (always returns 0) so use mode instead.
        if force_update or self.mode is None:
            self.update_attributes()

        return int(self.mode != CrockPotMode.Off)

    def set_state(self, state: int) -> None:
        """Set the state of this device to on or off."""
        if state:
            self.update_settings(
                CrockPotMode.High, int(self._attributes.get('time', '0'))
            )
        else:
            self.update_settings(CrockPotMode.Off, 0)

    def update_settings(self, mode: CrockPotMode, time: int) -> None:
        """Update mode and cooking time."""
        self.basicevent.SetCrockpotState(mode=str(int(mode)), time=str(time))

        # The CrockPot might not be ready - so it's not safe to assume the
        # state is what you just set so re-read it from the device.
        self.get_state(True)
