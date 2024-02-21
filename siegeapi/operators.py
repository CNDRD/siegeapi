from __future__ import annotations
from typing import Dict, List, Type, Union

from .constants import operator_dict
from .default_stats import DefaultStats


class Operator(DefaultStats):
    def __init__(self, data: dict, op_about: bool):
        super().__init__(data)

        self.name: str = data.get("statsDetail","")
        if self.name == "":
            self.name = "Unknown Operator"

        if op_about:
            self.icon_url: str = self._get_str_from_operators_const("icon_url")
            self.real_name: str = self._get_str_from_operators_const("realname")
            self.birth_place: str = self._get_str_from_operators_const("birthplace")
            self.date_of_birth: str = self._get_str_from_operators_const("date_of_birth")
            self.age: int = self._get_int_from_operators_const("age")
            self.roles: List[str] = self._get_list_from_operators_const("roles")
            self.unit: str = self._get_str_from_operators_const("unit")
            self.country_code: str = self._get_str_from_operators_const("country_code")
            self.season_introduced: str = self._get_str_from_operators_const("season_introduced")

    def _get_from_operators_const(self, value: str) -> Union[str, int, list]:
        return operator_dict.get(self.name.lower(), {}).get(value, "Missing Data")

    # for typing
    def _get_str_from_operators_const(self, value: str) -> str:
        returnv = self._get_from_operators_const(value)
        if isinstance(returnv, str):
            return returnv
        raise ValueError(f"Value {value} is not a string")
    
    def _get_int_from_operators_const(self, value: str) -> int:
        returnv = self._get_from_operators_const(value)
        if isinstance(returnv, int):
            return returnv
        raise ValueError(f"Value {value} is not an integer")
    
    def _get_list_from_operators_const(self, value: str) -> list:
        returnv = self._get_from_operators_const(value)
        if isinstance(returnv, list):
            return returnv
        raise ValueError(f"Value {value} is not a list")
        


class OperatorsGameMode:
    def __init__(self, data: dict, op_about: bool):
        self.attacker: list = [Operator(operator, op_about) for operator in data.get("teamRoles", {}).get("Attacker", {})]
        self.defender: list = [Operator(operator, op_about) for operator in data.get("teamRoles", {}).get("Defender", {})]

    def __repr__(self) -> str:
        return str(vars(self))


class Operators:
    def __init__(self, data: dict, op_about: bool):
        self.all: OperatorsGameMode = OperatorsGameMode(data.get("platforms",{}).get("PC",{}).get("gameModes",{}).get("all", {}), op_about)
        self.casual: OperatorsGameMode = OperatorsGameMode(data.get("platforms",{}).get("PC",{}).get("gameModes",{}).get("casual", {}), op_about)
        self.ranked: OperatorsGameMode = OperatorsGameMode(data.get("platforms",{}).get("PC",{}).get("gameModes",{}).get("ranked", {}), op_about)
        self.unranked: OperatorsGameMode = OperatorsGameMode(data.get("platforms",{}).get("PC",{}).get("gameModes",{}).get("unranked", {}), op_about)
        self.newcomer: OperatorsGameMode = OperatorsGameMode(data.get("platforms",{}).get("PC",{}).get("gameModes",{}).get("newcomer", {}), op_about)
        self._start_date: str = str(data.get("startDate", ""))
        self._end_date: str = str(data.get("endDate", ""))

    def get_timespan_dates(self) -> Dict[str, str]:
        return {"start_date": self._start_date, "end_date": self._end_date}

    def __repr__(self) -> str:
        return str(vars(self))
