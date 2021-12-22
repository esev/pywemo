"""Manually generated type stub for service.py.

Covers just the types used by pyWeMo.
"""

def parseString(
    inString: bytes, silence: bool = False, print_warnings: bool = True
) -> scpd:
    pass

class ArgumentType(GeneratedsSuper):
    def get_direction(self) -> str | None:
        pass

class ActionType(GeneratedsSuper):
    def get_name(self) -> str | None:
        pass
    def get_argumentList(self) -> ArgumentListType | None:
        pass
