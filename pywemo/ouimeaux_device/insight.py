"""Representation of a WeMo Insight device."""
from __future__ import annotations

import logging
import sys
import warnings
from datetime import datetime
from enum import Enum
from typing import Any

from .api.service import RequiredService
from .switch import Switch

LOG = logging.getLogger(__name__)


class StandbyState(str, Enum):
    """Standby state for the Insight device."""

    ON = "on"
    OFF = "off"
    STANDBY = "standby"


_STANDBY_STATE_MAP = {
    0: StandbyState.OFF,
    1: StandbyState.ON,
    8: StandbyState.STANDBY,
}

if sys.version_info >= (3, 8):
    from typing import TypedDict

    class InsightParams(TypedDict, total=False):
        """Energy related parameters for Insight devices."""

        state: StandbyState
        lastchange: datetime
        onfor: int
        ontoday: int
        ontotal: int
        todaymw: int
        totalmw: int
        currentpower: int
        wifipower: int
        powerthreshold: int


else:
    from typing import Dict, Union

    InsightParams = Dict[str, Union[StandbyState, datetime, int]]


class Insight(Switch):
    """Representation of a WeMo Insight device."""

    EVENT_TYPE_INSIGHT_PARAMS = "InsightParams"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a WeMo Switch device."""
        super().__init__(*args, **kwargs)
        self.insight_params: InsightParams = {}

        self.update_insight_params()

    @property
    def _required_services(self) -> list[RequiredService]:
        return super()._required_services + [
            RequiredService(name="insight", actions=["GetInsightParams"]),
        ]

    def update_insight_params(self) -> None:
        """Get and parse the device attributes."""
        params = self.insight.GetInsightParams().get('InsightParams')
        assert params
        self.insight_params = self.parse_insight_params(params)

    def subscription_update(self, _type: str, _params: str) -> bool:
        """Update the device attributes due to a subscription update event."""
        LOG.debug("subscription_update %s %s", _type, _params)
        if _type == self.EVENT_TYPE_INSIGHT_PARAMS:
            self.insight_params = self.parse_insight_params(_params)
            return True
        updated = super().subscription_update(_type, _params)
        if _type == self.EVENT_TYPE_BINARY_STATE and updated:
            # Special case: When an Insight device turns off, it also stops
            # sending InsightParams updates. Return False in this case to
            # indicate that the current state of the device hasn't been fully
            # updated.
            return self._state != 0
        return updated

    @staticmethod
    def parse_insight_params(params: str) -> InsightParams:
        """Parse the Insight parameters."""
        (
            state,  # 0 if off, 1 if on, 8 if on but load is off
            lastchange,
            onfor,  # seconds
            ontoday,  # seconds
            ontotal,  # seconds
            _timeperiod,
            wifipower,  # wifi rssi signal strength
            currentmw,
            todaymw,
            totalmw,
            powerthreshold,
        ) = params.split('|')
        return {
            'state': _STANDBY_STATE_MAP.get(int(state), StandbyState.OFF),
            'lastchange': datetime.fromtimestamp(int(lastchange)),
            'onfor': int(onfor),
            'ontoday': int(ontoday),
            'ontotal': int(ontotal),
            'todaymw': int(float(todaymw)),
            'totalmw': int(float(totalmw)),
            'currentpower': int(float(currentmw)),
            'wifipower': int(float(wifipower)),
            'powerthreshold': int(float(powerthreshold)),
        }

    def get_state(self, force_update: bool = False) -> int:
        """Return the device state."""
        if force_update or self._state is None:
            self.update_insight_params()

        return super().get_state(force_update)

    @property
    def today_kwh(self) -> float:
        """Return the number of kWh consumed today."""
        return float(self.insight_params['todaymw']) * 1.6666667e-8

    @property
    def total_kwh(self) -> float:
        """Return the total kWh consumed for the device."""
        return float(self.insight_params['totalmw']) * 1.6666667e-8

    @property
    def current_power(self) -> int:
        """Return the current power usage in mW."""
        return self.insight_params['currentpower']

    @property
    def current_power_watts(self) -> float:
        """Return the current power usage in Watts."""
        return float(self.current_power) / 1000.0

    @property
    def wifi_power(self) -> int:
        """Return the current rssi wifi signal."""
        return self.insight_params['wifipower']

    @property
    def threshold_power(self) -> int:
        """Return the threshold power in mW.

        Above this the device is on, below it is standby.
        """
        return self.insight_params['powerthreshold']

    @property
    def threshold_power_watts(self) -> float:
        """Return the threshold power in watts."""
        return float(self.threshold_power) / 1000.0

    @property
    def today_on_time(self) -> int:
        """Return the number of seconds the device has been on today."""
        return self.insight_params['ontoday']

    @property
    def today_standby_time(self) -> int:
        """Return how long the device has been in standby today."""
        warnings.warn(
            "The Insight.today_standby_time property should not be used and "
            "will be removed in a future version of pyWeMo. Switch to using "
            "the Insight.today_on_time property instead.",
            DeprecationWarning,
        )
        return self.insight_params['ontoday']

    @property
    def total_on_time(self) -> int:
        """Return the number of seconds the device has been on."""
        return self.insight_params['ontotal']

    @property
    def on_for(self) -> int:
        """Return the number of seconds the device was last on for."""
        return self.insight_params['onfor']

    @property
    def last_change(self) -> datetime:
        """Return the last change datetime."""
        return self.insight_params['lastchange']

    @property
    def get_standby_state(self) -> StandbyState:
        """Return the standby state of the device."""
        return self.insight_params['state']
