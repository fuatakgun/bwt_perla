import logging

from decimal import Decimal

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    TIME_DAYS,
    VOLUME_LITERS,
)

from .const import DOMAIN
from .entity import BWTPerlaEntity
from .coordinator import BWTPerlaDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    coordinator = hass.data[DOMAIN]

    INSTRUMENTS = [
        (
            "current_flow",
            "Current Flow",
            "aktuellerDurchfluss",
            "L/h",
            "mdi:water-pump",
            None,
        ),
        (
            "current_consumed_capacity",
            "Current Consumed Capacity",
            "aktuellerDurchflussProzent",
            PERCENTAGE,
            "mdi:water-percent",
            None,
        ),
        (
            "flow_today",
            "Flow Today",
            "durchflussHeute",
            VOLUME_LITERS,
            "mdi:cup-water",
            None,
        ),
        (
            "flow_month",
            "Flow This Month",
            "durchflussMonat",
            VOLUME_LITERS,
            "mdi:cup-water",
            None,
        ),
        (
            "flow_year",
            "Flow This Year",
            "durchflussJahr",
            VOLUME_LITERS,
            "mdi:cup-water",
            None,
        ),
        (
            "salt_remaining_percentage",
            "Regenerative Remaining Percentage",
            "RegeneriemittelVerbleibend",
            PERCENTAGE,
            "mdi:percent",
            None,
        ),
        (
            "salt_days_to_refill",
            "Regenerative Remaining Days",
            "RegeneriemittelNachfuellenIn",
            TIME_DAYS,
            "mdi:calendar-today",
            None,
        ),
    ]

    sensors = [
        BWTPerlaSensor(
            coordinator, entry, id, description, key, unit, icon, device_class
        )
        for id, description, key, unit, icon, device_class in INSTRUMENTS
    ]

    async_add_devices(sensors, True)


class BWTPerlaSensor(BWTPerlaEntity):
    def __init__(
        self,
        coordinator: BWTPerlaDataUpdateCoordinator,
        entry: ConfigEntry,
        id: str,
        description: str,
        key: str,
        unit: str,
        icon: str,
        device_class: str,
    ):
        super().__init__(coordinator, entry)
        self._id = id
        self.description = description
        self.key = key
        self.unit = unit
        self._icon = icon
        self._device_class = device_class

    @property
    def state(self):
        if self._id == "flow_year":
            value = int(self.coordinator.data[self.key]) * 100
            return value
        return self.coordinator.data[self.key]

    @property
    def unit_of_measurement(self):
        return self.unit

    @property
    def icon(self):
        return self._icon

    @property
    def device_class(self):
        return self._device_class

    @property
    def name(self):
        return f"{self.description}"

    @property
    def id(self):
        return f"{DOMAIN}_{self._id}"

    @property
    def unique_id(self):
        return f"{DOMAIN}-{self._id}-{self.coordinator.api.host}"
