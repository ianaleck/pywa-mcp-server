import base64
import dataclasses
import datetime as dt
import enum
import inspect

import pytest

import pywa_mcp_server as main


class Color(enum.Enum):
    RED = "red"
    BLUE = "blue"


@dataclasses.dataclass
class Address:
    street: str
    city: str


@dataclasses.dataclass
class Person:
    name: str
    age: int
    address: Address | None = None


# ---------- _serialize ----------


def test_serialize_bytes():
    out = main._serialize(b"hello")
    assert out == {"_bytes_b64": base64.b64encode(b"hello").decode(), "size": 5}


def test_serialize_path(tmp_path):
    p = tmp_path / "x.txt"
    assert main._serialize(p) == str(p)


def test_serialize_datetime():
    d = dt.datetime(2026, 1, 2, 3, 4, 5, tzinfo=dt.timezone.utc)
    assert main._serialize(d) == "2026-01-02T03:04:05+00:00"


def test_serialize_date():
    assert main._serialize(dt.date(2026, 1, 2)) == "2026-01-02"


def test_serialize_timedelta():
    assert main._serialize(dt.timedelta(seconds=90)) == 90.0


def test_serialize_enum():
    assert main._serialize(Color.RED) == "red"


def test_serialize_dataclass_nested():
    p = Person(name="Ian", age=30, address=Address(street="1 Main", city="JHB"))
    assert main._serialize(p) == {
        "name": "Ian",
        "age": 30,
        "address": {"street": "1 Main", "city": "JHB"},
    }


def test_serialize_list_of_enums():
    assert main._serialize([Color.RED, Color.BLUE]) == ["red", "blue"]


def test_serialize_repr_fallback():
    class Opaque:
        def __repr__(self):
            return "OPAQUE"

    assert main._serialize(Opaque()) == "OPAQUE"


# ---------- _coerce ----------


def test_coerce_string_to_list():
    out = main._coerce('[1, 2, 3]', list[int])
    assert out == [1, 2, 3]


def test_coerce_string_to_dict_dataclass():
    out = main._coerce('{"street":"a","city":"b"}', Address)
    assert out == Address(street="a", city="b")


def test_coerce_list_in_union():
    out = main._coerce([{"street": "a", "city": "b"}], list[Address] | None)
    assert out == [Address(street="a", city="b")]


def test_coerce_dataclass_dict():
    out = main._coerce({"name": "Ian", "age": 30}, Person)
    assert out.name == "Ian" and out.age == 30


def test_coerce_enum_value():
    assert main._coerce("red", Color) is Color.RED


def test_coerce_none_passthrough():
    assert main._coerce(None, list[int]) is None


def test_coerce_unknown_field_raises():
    with pytest.raises(TypeError):
        main._coerce({"name": "x", "age": 1, "bogus": 1}, Person)


# ---------- _build_schema ----------


def test_build_schema_basic():
    def fn(a: str, b: int = 0): ...

    s = main._build_schema(fn)
    assert s["properties"]["a"] == {"type": "string"}
    assert s["properties"]["b"] == {"type": "integer"}
    assert s["required"] == ["a"]


def test_build_schema_varargs():
    def fn(first: str, *rest: str, end: int): ...

    s = main._build_schema(fn)
    assert "_args" in s["properties"]
    assert s["properties"]["_args"] == {"type": "array"}
    assert "first" in s["properties"]
    assert "end" in s["properties"]


def test_build_schema_skips_self_and_varkw():
    class C:
        def m(self, x: int, **kw): ...

    s = main._build_schema(C().m)
    assert list(s["properties"]) == ["x"]


# ---------- _discover ----------


class _Fake:
    def send_text(self): ...

    def listen(self): ...

    def get_templates(self): ...

    _private = lambda: None


def test_discover_skips_default_listen(monkeypatch):
    monkeypatch.delenv("PYWA_MCP_TOOLS", raising=False)
    out = main._discover(_Fake())
    assert "send_text" in out
    assert "get_templates" in out
    assert "listen" not in out


def test_discover_allowlist_strict(monkeypatch):
    monkeypatch.setenv("PYWA_MCP_TOOLS", "send_text,listen")
    out = main._discover(_Fake())
    assert set(out) == {"send_text", "listen"}


def test_discover_allowlist_excludes_others(monkeypatch):
    monkeypatch.setenv("PYWA_MCP_TOOLS", "get_templates")
    out = main._discover(_Fake())
    assert set(out) == {"get_templates"}


# ---------- _py_to_schema ----------


def test_schema_empty_for_no_annotation():
    assert main._py_to_schema(inspect.Parameter.empty) == {}


def test_schema_primitives():
    assert main._py_to_schema(str) == {"type": "string"}
    assert main._py_to_schema(int) == {"type": "integer"}
    assert main._py_to_schema(float) == {"type": "number"}
    assert main._py_to_schema(bool) == {"type": "boolean"}


def test_schema_list_and_dict():
    assert main._py_to_schema(list[int]) == {"type": "array"}
    assert main._py_to_schema(dict[str, int]) == {"type": "object"}


def test_schema_optional_unwraps():
    assert main._py_to_schema(str | None) == {"type": "string"}


def test_schema_ambiguous_union_empty():
    assert main._py_to_schema(str | int) == {}


# ---------- _coerce edge cases ----------


def test_coerce_literal_enum():
    import typing as t

    hint = t.Literal[Color.RED, Color.BLUE]
    assert main._coerce("red", hint) is Color.RED


def test_coerce_invalid_json_string_passthrough():
    out = main._coerce("not json", list[int] | None)
    assert out == "not json"


def test_coerce_dataclass_in_optional():
    out = main._coerce({"street": "a", "city": "b"}, Address | None)
    assert out == Address(street="a", city="b")


def test_coerce_unknown_hint_passthrough():
    assert main._coerce("anything", object) == "anything"


# ---------- _coerce_args ----------


def test_coerce_args_uses_hints():
    def fn(items: list[int], name: str): ...

    out = main._coerce_args(fn, {"items": "[1,2]", "name": "x"})
    assert out == {"items": [1, 2], "name": "x"}


def test_coerce_args_handles_get_type_hints_failure():
    def fn(items): ...

    out = main._coerce_args(fn, {"items": [1, 2]})
    assert out == {"items": [1, 2]}


def test_coerce_args_handles_bad_annotation():
    def fn(x: "BogusUndefinedType"): ...  # noqa: F821

    out = main._coerce_args(fn, {"x": 1})
    assert out == {"x": 1}


def test_serialize_pydantic():
    from pydantic import BaseModel as PM

    class M(PM):
        a: int
        b: str

    assert main._serialize(M(a=1, b="z")) == {"a": 1, "b": "z"}


class _FakeWithCallable:
    def good(self): ...
    not_callable = 42


def test_discover_skips_non_callable(monkeypatch):
    monkeypatch.delenv("PYWA_MCP_TOOLS", raising=False)
    out = main._discover(_FakeWithCallable())
    assert "good" in out
    assert "not_callable" not in out


def test_coerce_literal_non_enum_passthrough():
    import typing as t

    assert main._coerce("foo", t.Literal["foo", "bar"]) == "foo"
