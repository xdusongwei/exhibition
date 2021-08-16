import addict


class Settings:
    def __init__(self, config: addict.Addict):
        self.config = config

    def update(self, config: dict) -> bool:
        start, end = self.working_port_range
        self.config = addict.Addict({
            'settings': config,
        })
        return (start, end, ) != self.working_port_range

    @property
    def test_url(self) -> str:
        return self.config.settings.testUrl or 'https://ssl.gstatic.com/gb/images/p2_edfc3681.png'

    @property
    def export_reboot_period(self) -> int:
        value = self.config.settings.exportRebootPeriod
        if not isinstance(value, int) or value < 0:
            return 8 * 60 * 60
        return value

    @property
    def working_port_range(self) -> tuple[int, int]:
        default = (9000, 9999, )
        start = self.config.settings.workingPortRangeStart
        if not isinstance(start, int) or start < 1:
            return default
        end = self.config.settings.workingPortRangeEnd
        if not isinstance(end, int) or end < 1:
            return default
        if end < start:
            return default
        return start, end,

    def to_dict(self):
        return {
            'testUrl': self.test_url,
            'exportRebootPeriod': self.export_reboot_period,
            'workingPortRangeStart': self.working_port_range[0],
            'workingPortRangeEnd': self.working_port_range[1],
        }


__all__ = [
    'Settings',
]