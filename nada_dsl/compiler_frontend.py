import json
import os
from json import JSONEncoder
import inspect
from typing import List, Dict, Any

from nada_dsl.source_ref import SourceRef
from nada_dsl.circuit_io import Input, Output
from nada_dsl.nada_types.rational import SecretRational
from nada_dsl.nada_types.collections import (
    Array,
    Vector,
    NadaTuple,
    ArrayType,
    VectorType,
    NadaTupleType,
)
from nada_dsl.nada_types.function import NadaFunction
from nada_dsl.future.operations import Cast
from nada_dsl.operations import (
    Addition,
    Subtraction,
    Multiplication,
    Division,
    Modulo,
    RightShift,
    LeftShift,
    LessThan,
    GreaterThan,
    LessOrEqualThan,
    GreaterOrEqualThan,
    Equals,
    Map,
    Reduce,
    Zip,
    Unzip,
)

INPUTS = {}
PARTIES = {}
FUNCTIONS = {}


class ClassEncoder(JSONEncoder):
    def default(self, o):
        if inspect.isclass(o):
            return o.__name__
        return {type(o).__name__: o.__dict__}


def get_target_dir() -> str:
    env_dir = os.environ.get("NADA_TARGET_DIR")
    if env_dir:
        return env_dir

    cwd = os.getcwd()

    try:
        os.mkdir("target")
    except FileExistsError:
        pass

    return os.path.join(cwd, "target")


def nada_compile(outputs: List[Output]) -> str:
    compiled = nada_dsl_to_nada_mir(outputs)
    return json.dumps(compiled)


def compile_to_nada_pydsl_hir(output_file, outputs, target_dir):
    nada_pydsl_hir = json.dumps(outputs, cls=ClassEncoder, indent=2)
    with open(f"{target_dir}/{output_file}.nada-pydsl-hir.json", "w") as file:
        file.write(nada_pydsl_hir)


def compile_to_nada_mir(target_dir, outputs, output_file):
    circuit = nada_dsl_to_nada_mir(outputs)
    nada_mir = json.dumps(circuit, indent=2)
    with open(f"{target_dir}/{output_file}.nada.json", "w") as file:
        file.write(nada_mir)


def nada_dsl_to_nada_mir(outputs: List[Output]) -> Dict[str, Any]:
    new_outputs = []
    PARTIES.clear()
    INPUTS.clear()
    for output in outputs:
        new_out = process_operation(output.inner)
        party = output.party
        PARTIES[party.name] = party
        new_outputs.append(
            {
                "inner": new_out,
                "name": output.name,
                "party": party.name,
                "type": to_type_dict(output.inner),
                "source_ref": output.source_ref.to_dict(),
            }
        )

    return {
        "functions": to_function_list(FUNCTIONS),
        "parties": to_party_list(PARTIES),
        "inputs": to_input_list(INPUTS),
        "outputs": new_outputs,
        "source_files": SourceRef.get_sources(),
    }


def to_party_list(parties):
    return [
        {
            "name": party.name,
            "source_ref": party.source_ref.to_dict(),
        }
        for party in parties.values()
    ]


def to_input_list(inputs):
    input_list = []
    for party_inputs in inputs.values():
        for program_input, program_type in party_inputs.values():
            input_list.append(
                {
                    "name": program_input.name,
                    "type": program_type,
                    "party": program_input.party.name,
                    "doc": program_input.doc,
                    "source_ref": program_input.source_ref.to_dict(),
                }
            )
    return input_list


def to_function_list(functions):
    function_list = []
    while len(functions) > 0:
        function = functions.pop(list(functions.keys())[0])
        function_list.append(to_fn_dict(function))
    return function_list


def to_type_dict(op_wrapper):
    if type(op_wrapper) == Array or type(op_wrapper) == ArrayType:
        size = {"size": op_wrapper.size} if op_wrapper.size else {}
        from typing import TypeVar

        inner_type = (
            "T"
            if type(op_wrapper.inner_type) == TypeVar
            else to_type_dict(op_wrapper.inner_type)
        )
        return {"Array": {"inner_type": inner_type, **size}}
    elif type(op_wrapper) == Vector or type(op_wrapper) == VectorType:
        from typing import TypeVar

        inner_type = (
            "T"
            if type(op_wrapper.inner_type) == TypeVar
            else to_type_dict(op_wrapper.inner_type)
        )
        return {"Vector": {"inner_type": inner_type}}
    elif type(op_wrapper) == NadaTuple or type(op_wrapper) == NadaTupleType:
        return {
            "NadaTuple": {
                "left_type": to_type_dict(op_wrapper.left_type),
                "right_type": to_type_dict(op_wrapper.right_type),
            }
        }
    elif type(op_wrapper) == SecretRational:
        return {"Secret": {"Rational": {"digits": op_wrapper.digits}}}

    elif inspect.isclass(op_wrapper):
        return to_type(op_wrapper.__name__)
    else:
        return to_type(op_wrapper.__class__.__name__)


def to_type(name: str):
    if name.startswith("Public"):
        name = name[len("Public") :].lstrip()
        return {"Public": {name: None}}
    elif name.startswith("Secret"):
        name = name[len("Secret") :].lstrip()
        return {"Secret": {name: None}}
    else:
        return name


def to_fn_dict(fn: NadaFunction):
    return {
        "id": fn.id,
        "args": [{"name": arg.name, "type": to_type_dict(arg.type)} for arg in fn.args],
        "function": fn.function.__name__,
        "inner": process_operation(fn.inner),
        "return_type": to_type_dict(fn.return_type),
        "source_ref": fn.source_ref.to_dict(),
    }


def process_operation(operation_wrapper):
    from nada_dsl.nada_types.function import NadaFunctionArg

    ty = to_type_dict(operation_wrapper)
    operation = operation_wrapper.inner

    if isinstance(
        operation,
        (
            Addition,
            Subtraction,
            Multiplication,
            Division,
            Modulo,
            RightShift,
            LeftShift,
            LessThan,
            GreaterThan,
            GreaterOrEqualThan,
            LessOrEqualThan,
            Equals,
            Zip,
        ),
    ):
        return {
            type(operation).__name__: {
                "left": process_operation(operation.left),
                "right": process_operation(operation.right),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }

    elif isinstance(operation, Cast):
        return {
            "Cast": {
                "target": process_operation(operation.target),
                "to": operation.to.__name__,
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif isinstance(operation, Input):
        party_name = operation.party.name
        PARTIES[party_name] = operation.party
        if party_name not in INPUTS:
            INPUTS[party_name] = {}
        if operation.name in INPUTS[party_name] and id(
            INPUTS[party_name][operation.name][0]
        ) != id(operation):
            raise Exception(f"Input is duplicated: {operation.name}")
        else:
            INPUTS[party_name][operation.name] = (operation, ty)
        return {
            "InputReference": {
                "refers_to": operation.name,
                "type": ty,
            }
        }
    elif isinstance(operation, Map):
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        return {
            "Map": {
                "fn": operation.fn.id,
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif isinstance(operation, Reduce):
        if operation.fn.id not in FUNCTIONS:
            FUNCTIONS[operation.fn.id] = operation.fn
        return {
            "Reduce": {
                "fn": operation.fn.id,
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif isinstance(operation, Unzip):
        return {
            "Unzip": {
                "inner": process_operation(operation.inner),
                "type": ty,
                "source_ref": operation.source_ref.to_dict(),
            }
        }
    elif isinstance(operation, NadaFunctionArg):
        return {
            "NadaFunctionArgRef": {
                "function_id": operation.function_id,
                "refers_to": operation.name,
                "type": to_type_dict(operation.type),
            }
        }
    else:
        raise Exception(f"Compilation of Operation {operation} not supported")
