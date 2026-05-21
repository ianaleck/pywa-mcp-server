import asyncio
import base64
import collections.abc
import datetime as _dt
import enum
import inspect
import json
import os
import pathlib
import types
import typing
from dataclasses import fields, is_dataclass

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel
from pywa import WhatsApp

JSON_PRIMITIVES = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    type(None): "null",
}


def _py_to_schema(annotation) -> dict:
    if annotation is inspect.Parameter.empty or annotation is typing.Any:
        return {}
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is typing.Union or origin is types.UnionType or (origin is None and args):
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _py_to_schema(non_none[0])
        return {}
    if origin in (list, tuple, set, frozenset) or annotation in (list, tuple, set):
        return {"type": "array"}
    if origin is dict or annotation is dict:
        return {"type": "object"}
    if annotation in JSON_PRIMITIVES:
        return {"type": JSON_PRIMITIVES[annotation]}
    return {}


def _build_schema(fn) -> dict:
    sig = inspect.signature(fn)
    props: dict = {}
    required: list[str] = []
    for name, p in sig.parameters.items():
        if name == "self" or p.kind is p.VAR_KEYWORD:
            continue
        if p.kind is p.VAR_POSITIONAL:
            props["_args"] = {"type": "array"}
            continue
        props[name] = _py_to_schema(p.annotation) or {}
        if p.default is inspect.Parameter.empty:
            required.append(name)
    schema = {"type": "object", "properties": props, "additionalProperties": True}
    if required:
        schema["required"] = required
    return schema


def _serialize(obj):
    if isinstance(obj, (bytes, bytearray)):
        return {"_bytes_b64": base64.b64encode(bytes(obj)).decode("ascii"), "size": len(obj)}
    if isinstance(obj, pathlib.PurePath):
        return str(obj)
    if isinstance(obj, (_dt.datetime, _dt.date, _dt.time)):
        return obj.isoformat()
    if isinstance(obj, _dt.timedelta):
        return obj.total_seconds()
    if isinstance(obj, enum.Enum):
        return obj.value
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: _serialize(getattr(obj, f.name)) for f in fields(obj) if not f.name.startswith("_")}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return repr(obj)


_ITERABLE_ORIGINS = (list, tuple, set, frozenset, collections.abc.Iterable, collections.abc.Sequence)


def _coerce(value, hint):
    if value is None or hint is None or hint is typing.Any:
        return value
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    if origin is typing.Union or origin is types.UnionType:
        non_none = [a for a in args if a is not type(None)]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except (ValueError, TypeError):
                parsed = None
            if isinstance(parsed, (list, dict)):
                value = parsed
        if isinstance(value, list):
            for a in non_none:
                ao = typing.get_origin(a)
                if ao in _ITERABLE_ORIGINS:
                    return _coerce(value, a)
        for a in non_none:
            try:
                return _coerce(value, a)
            except (TypeError, ValueError):
                continue
        return value

    if origin is typing.Literal:
        for a in args:
            if isinstance(a, enum.Enum) and value in (a, a.value, a.name):
                return a
        return value

    if origin in _ITERABLE_ORIGINS:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (ValueError, TypeError):
                pass
        if not isinstance(value, (list, tuple, set, frozenset)):
            raise TypeError(f"expected iterable, got {type(value).__name__}")
        item = args[0] if args else None
        return [_coerce(v, item) for v in value]

    if inspect.isclass(hint) and issubclass(hint, enum.Enum):
        return value if isinstance(value, hint) else hint(value)

    if inspect.isclass(hint) and is_dataclass(hint):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    value = parsed
            except (ValueError, TypeError):
                pass
        if isinstance(value, dict):
            try:
                field_hints = typing.get_type_hints(hint)
            except Exception:
                field_hints = {}
            valid = {f.name for f in fields(hint)}
            unknown = set(value) - valid
            if unknown:
                raise TypeError(f"{hint.__name__} has no fields {unknown}")
            kwargs = {k: _coerce(v, field_hints.get(k)) for k, v in value.items()}
            return hint(**kwargs)

    if inspect.isclass(hint) and isinstance(value, hint):
        return value

    return value


def _coerce_args(fn, arguments: dict) -> dict:
    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = {}
    return {k: _coerce(v, hints.get(k)) for k, v in arguments.items()}


DEFAULT_SKIP = {"listen"}


def _discover(client: WhatsApp) -> dict:
    allow_env = os.environ.get("PYWA_MCP_TOOLS", "").strip()
    allow = {s.strip() for s in allow_env.split(",") if s.strip()} if allow_env else None

    tools = {}
    for name in dir(client):
        if name.startswith("_"):
            continue
        if allow is None:
            if name in DEFAULT_SKIP:
                continue
        elif name not in allow:
            continue
        fn = getattr(client, name)
        if not callable(fn) or inspect.isclass(fn):
            continue
        try:
            inspect.signature(fn)
        except (TypeError, ValueError):
            continue
        tools[name] = fn
    return tools


async def amain() -> None:
    def env(*keys):
        for k in keys:
            v = os.environ.get(k)
            if v:
                return v
        return None

    phone_id = env("WA_PHONE_ID", "WHATSAPP_PHONE_ID")
    token = env("WA_TOKEN", "WHATSAPP_TOKEN")
    if not phone_id or not token:
        raise SystemExit("phone_id/token env vars required (WA_PHONE_ID|WHATSAPP_PHONE_ID, WA_TOKEN|WHATSAPP_TOKEN)")

    app_id = env("WA_APP_ID", "WHATSAPP_APP_ID")
    client = WhatsApp(
        phone_id=phone_id,
        token=token,
        business_account_id=env("WA_BUSINESS_ACCOUNT_ID", "WHATSAPP_WABA_ID"),
        app_id=int(app_id) if app_id else None,
        app_secret=env("WA_APP_SECRET", "WHATSAPP_APP_SECRET"),
    )
    methods = _discover(client)
    server = Server("pywa-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        out = []
        for name, fn in methods.items():
            doc = (inspect.getdoc(fn) or "").strip().split("\n\n")[0][:1000]
            out.append(Tool(name=name, description=doc or name, inputSchema=_build_schema(fn)))
        return out

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        fn = methods.get(name)
        if fn is None:
            raise ValueError(f"unknown tool: {name}")
        args_dict = dict(arguments or {})
        var_args = args_dict.pop("_args", None)
        if isinstance(var_args, str):
            try:
                var_args = json.loads(var_args)
            except (ValueError, TypeError):
                pass
        if var_args is None:
            var_args = []
        elif not isinstance(var_args, (list, tuple)):
            var_args = [var_args]

        coerced = _coerce_args(fn, args_dict)
        sig = inspect.signature(fn)
        positional: list = []
        kwargs: dict = dict(coerced)
        if var_args:
            for pname, p in sig.parameters.items():
                if pname == "self":
                    continue
                if p.kind is p.VAR_POSITIONAL:
                    break
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD):
                    if pname in kwargs:
                        positional.append(kwargs.pop(pname))
        result = fn(*positional, *var_args, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        payload = _serialize(result)
        text = json.dumps(payload, ensure_ascii=False, default=repr, indent=2)
        return [TextContent(type="text", text=text)]

    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()
