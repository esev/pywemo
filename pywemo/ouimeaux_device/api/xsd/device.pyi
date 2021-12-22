"""Manually generated type stub for device.py.

Covers just the types used by pyWeMo.
"""

def parseString(
    inString: bytes, silence: bool = False, print_warnings: bool = True
) -> root:
    pass

def quote_xml(inStr: str) -> str:
    pass

class root(GeneratedsSuper):
    def get_device(self) -> DeviceType | None:
        pass

class DeviceType(GeneratedsSuper):
    def get_manufacturer(self) -> str | None:
        pass

class serviceType(GeneratedsSuper):
    def get_SCPDURL(self) -> str | None:
        pass
    def get_controlURL(self) -> str | None:
        pass
    def get_eventSubURL(self) -> str | None:
        pass
    def get_serviceType(self) -> str | None:
        pass
