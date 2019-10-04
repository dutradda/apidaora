from logging import getLogger
from typing import Any, Dict, Type, _TypedDictMeta  # type: ignore

from jsondaora import jsondaora

from ....core.request import PathArgs
from ....core.router import PATH_RE, split_path
from ....exceptions import InvalidPathParams


logger = getLogger(__name__)


def path_args(
    pattern: str, operation_annotations: Dict[str, Any]
) -> Type[PathArgs]:
    path_args_matchs = map(lambda p: PATH_RE.match(p), split_path(pattern))
    path_args_names = set(
        match.groupdict()['name'] for match in path_args_matchs if match
    )
    path_args_annotations = {
        k: v for k, v in operation_annotations.items() if k in path_args_names
    }

    if len(path_args_annotations) != len(path_args_names):
        missing_args = ', '.join(
            set(path_args_annotations.keys()).difference(path_args_names)
        )
        invalid_args = ', '.join(
            set(path_args_names).difference(path_args_annotations.keys())
        )
        raise InvalidPathParams(
            f'Missing args: {missing_args}. Invalid args: {invalid_args}'
        )

    if path_args_annotations:
        OperationPathArgs = _TypedDictMeta(
            'OperationPathArgs',
            (PathArgs,),
            {'__annotations__': path_args_annotations},
        )
        OperationPathArgs: Type[PathArgs] = jsondaora(OperationPathArgs)

    else:
        OperationPathArgs = PathArgs

    return OperationPathArgs
