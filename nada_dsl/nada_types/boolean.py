# This file is automatically generated. Do not edit!

from . import NadaType
from dataclasses import dataclass
from nada_dsl.circuit_io import Literal
from nada_dsl.operations import Equals, PublicEquals
from nada_dsl.source_ref import SourceRef
from typing import Union

@dataclass
class Boolean(NadaType):
    value: bool

    def __init__(self, value: bool):
        super().__init__(inner=Literal(value=value, source_ref=SourceRef.back_frame()))
        if isinstance(value, bool):
            self.value = value
        else:
            raise ValueError(f"Expected bool, got {type(value).__name__}")

    def __eq__(
        self, other: Union["Boolean", "PublicBoolean", "SecretBoolean"]
    ) -> Union["Boolean", "PublicBoolean", "SecretBoolean"]:
        if isinstance(other, Boolean):
            return Boolean(value=bool(self.value == other.value))
        elif isinstance(other, PublicBoolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        elif isinstance(other, SecretBoolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")

@dataclass
class PublicBoolean(NadaType):
    def __eq__(
        self, other: Union["Boolean", "PublicBoolean", "SecretBoolean"]
    ) -> Union["PublicBoolean", "SecretBoolean"]:
        if isinstance(other, Boolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        elif isinstance(other, PublicBoolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        elif isinstance(other, SecretBoolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")

    def public_equals(
        self, other: Union["PublicBoolean", "SecretBoolean"]
    ) -> "PublicBoolean":
        if isinstance(other, PublicBoolean):
            operation = PublicEquals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        elif isinstance(other, SecretBoolean):
            operation = PublicEquals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self}.public_equals({other})")

@dataclass
class SecretBoolean(NadaType):
    def __eq__(
        self, other: Union["Boolean", "PublicBoolean", "SecretBoolean"]
    ) -> "SecretBoolean":
        if isinstance(other, Boolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return SecretBoolean(inner=operation)
        elif isinstance(other, PublicBoolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return SecretBoolean(inner=operation)
        elif isinstance(other, SecretBoolean):
            operation = Equals(left=self, right=other, source_ref=SourceRef.back_frame())
            return SecretBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self} == {other}")

    def public_equals(
        self, other: Union["PublicBoolean", "SecretBoolean"]
    ) -> "PublicBoolean":
        if isinstance(other, PublicBoolean):
            operation = PublicEquals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        elif isinstance(other, SecretBoolean):
            operation = PublicEquals(left=self, right=other, source_ref=SourceRef.back_frame())
            return PublicBoolean(inner=operation)
        else:
            raise TypeError(f"Invalid operation: {self}.public_equals({other})")

