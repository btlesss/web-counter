from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    SerializationInfo,
)
from random import choice
from typing import List
import json


en = ("aeiouy", "bcdfghjklmnpqrstvwxz")


class IDGenerator(BaseModel):
    id: str = ""
    _ln = 6

    def generate_id(self):
        ans = ""
        letter_type = True
        for _ in range(self._ln):
            ans += choice(en[letter_type])
            letter_type = not (letter_type)
        self.id = ans


class CounterTimings(BaseModel):
    per24h: int = 0
    per7d: int = 0
    per30d: int = 0


class CounterTimingsUnfilled(BaseModel):
    pass


class Counter(IDGenerator):
    name: str = Field(
        min_length=1, max_length=32, title="Human-readable name of counter"
    )
    value: int = Field(0, title="Total count")
    timings: CounterTimings = Field(CounterTimingsUnfilled())


class RedisCounter(IDGenerator):
    name: str = Field(
        min_length=1, max_length=32, title="Human-readable name of counter"
    )
    value: int = Field(0, title="Total count")


class NewCounter(BaseModel):
    name: str = Field(
        min_length=1, max_length=32, title="Human-readable name of counter"
    )
    value: int = Field(0, title="Initial count")


class Group(IDGenerator):
    name: str = Field(
        "", min_length=1, max_length=32, title="Human-readable name of group"
    )
    counters: List[Counter] = Field(
        default_factory=lambda: [], title="List of counters objects"
    )


class RedisGroup(IDGenerator):
    name: str = Field(
        "", min_length=1, max_length=32, title="Human-readable name of group"
    )
    counters: List[str] = Field(
        default_factory=lambda: [], title="List of counters ids"
    )

    @field_validator("counters", mode="before")
    def loads_timings(cls, counters: str):
        if isinstance(counters, str):
            return json.loads(counters)
        return counters

    @field_serializer("counters", when_used="json")
    def serialize_timings(self, counters: List[str]):
        return json.dumps(counters)


class NewGroup(BaseModel):
    name: str = Field(
        "", min_length=1, max_length=32, title="Human-readable name of group"
    )
    counters: List[str] = Field(
        default_factory=lambda: [], title="List of counters ids"
    )


class OperationSuccess(BaseModel):
    ok: bool = True
