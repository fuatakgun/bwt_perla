import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION
from .coordinator import BWTPerlaDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class BWTPerlaEntity(CoordinatorEntity):
    def __init__(self, coordinator: BWTPerlaDataUpdateCoordinator, entry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.host)},
            "name": NAME,
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def available(self) -> bool:
        return not not self.coordinator.data

    @property
    def should_poll(self) -> bool:
        return False
