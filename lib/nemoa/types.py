# -*- coding: utf-8 -*-
"""Collection of types and constants used in nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

# import generic types from typing
from typing import (
    Any, Callable, ClassVar, Dict, Hashable, Iterable,
    List, Optional, Sequence, Set, Tuple, TypeVar, Union)

# import specific types from builtin packages
from array import ArrayType as Array
from os import PathLike as Path
from types import ModuleType as Module, FunctionType as Function

################################################################################
# Define generic Variables
################################################################################

# Generic Type-Variables
S = TypeVar('S')
T = TypeVar('T')

# Built-in Type Aliases and constants
Obj = object

################################################################################
# Define numerical Constants
################################################################################

NaN = float('nan')
Infty = float('inf')

################################################################################
# Define Types for Literals and Collections of Literals
################################################################################

# Unions of Literals
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptComplex = Optional[complex]
OptBool = Optional[bool]
OptArray = Optional[Array]
StrOrBool = Union[str, bool]
OptStrOrBool = Optional[StrOrBool]
BytesLike = Union[bytes, bytearray, memoryview]
BytesLikeOrStr = Union[BytesLike, str]
Num = Union[int, float, complex]
OptNum = Optional[Num]
Scalar = Union[int, float, complex]

# Collections of Literals
StrSet = Set[str]
StrPair = Tuple[str, str]
StrTuple = Tuple[str, ...]
StrList = List[str]
StrDict = Dict[str, Any]
IntSet = Set[int]
IntPair = Tuple[int, int]
IntTuple = Tuple[int, ...]
IntList = List[int]
IntDict = Dict[int, Any]
FloatPair = Tuple[float, float]

# Unions of Collections of Literals
StrOrDict = Union[str, Dict[Hashable, Any]]
OptSet = Optional[Set[Any]]
OptPair = Optional[Tuple[Any, Any]]
OptTuple = Optional[Tuple[Any, ...]]
OptList = Optional[List[Any]]
OptDict = Optional[Dict[Any, Any]]
OptStrDict = Optional[StrDict]
OptStrList = Optional[StrList]
OptStrTuple = Optional[StrTuple]
OptStrOrDict = Optional[StrOrDict]
OptIntList = Optional[IntList]
OptIntTuple = Optional[IntTuple]

# Compounds of Literals and Collections of Literals
DictOfDicts = Dict[Hashable, Dict[Hashable, Any]]
DictOfDictOfDicts = Dict[Hashable, DictOfDicts]
StrPairDict = Dict[StrPair, Any]
StrListPair = Tuple[StrList, StrList]
StrTupleDict = Dict[Union[str, Tuple[str, ...]], Any]
RecDict = Dict[Hashable, StrDict]
DictOfRecDicts = Dict[Hashable, RecDict]
Vector = Sequence[Scalar]

# Nested Types
# TODO: (2018.09) currently recursive type definition is not fully supported
# by the typing module. When recursive type definition is available replace
# the following lines by their respective recursive definitions
NestDict = Union[Dict[Hashable, Any], DictOfDicts, DictOfDictOfDicts]
#NestDict = Dict[Hashable, Union[Any, 'NestDict']]
NestRecDict = Union[StrDict, RecDict, DictOfRecDicts]
# NestRecDict = Dict[Hashable, Union[StrDict, 'NestRecDict']]
OptNestDict = Optional[NestDict]
IterNestRecDict = Iterable[NestRecDict]

################################################################################
# Define Types for Callables
################################################################################

# Elementary Callables
AnyFunc = Callable[..., Any]
BoolFunc = Callable[..., bool]
ScalarFunc = Callable[..., Scalar]
VectorFunc = Callable[..., Vector]
UnaryFunc = Callable[[T], Any]
BinaryFunc = Callable[[S, T], Any]
TestFunc = Callable[[S, T], bool]

# Unions of Callables and Literals
OptCallable = Optional[AnyFunc]
OptFunction = Optional[Function]
OptModule = Optional[Module]

# Collections of Callables
StrDictOfFuncs = Dict[str, AnyFunc]
StrDictOfTestFuncs = Dict[str, TestFunc]

# Unions of Collections of Callables and Literals
OptStrDictOfFuncs = Optional[StrDictOfFuncs]
OptStrDictOfTestFuncs = Optional[StrDictOfTestFuncs]

# Compounds of Collables and Literals
FuncWrapper = Callable[[Callable[..., T]], Callable[..., T]]

################################################################################
# Define Types for Class Variables
################################################################################

ClassDict = ClassVar[Dict[Hashable, Any]]
ClassStrDict = ClassVar[Dict[str, Any]]

################################################################################
# Define specific Types for builtin Packages
################################################################################

# os / pathlib
PathLike = Union[str, Path]
# Nested Types
# TODO: (2018.09) currently recursive type definition is not fully supported
# by the typing module. When recursive type definition is available replace
# the following lines by their respective recursive definitions
PathLikeSeq = Sequence[PathLike]
PathLikeSeq2 = Sequence[Union[PathLike, PathLikeSeq]]
PathLikeSeq3 = Sequence[Union[PathLike, PathLikeSeq, PathLikeSeq2]]
NestPath = Union[PathLike, PathLikeSeq, PathLikeSeq2, PathLikeSeq3]
#NestPath = Sequence[Union[str, Path, 'NestPath']]
NestPathDict = Dict[str, NestPath]
OptNestPathDict = Optional[NestPathDict]

################################################################################
# Define specific Types for external Packages
################################################################################

# NumPy types
NpShape = Optional[IntTuple]
NpShapeLike = Optional[Union[int, Sequence[int]]]
NpAxis = Union[None, int, IntTuple]
NpFields = Union[None, str, Iterable[str]]
# TODO: (2018.09) currently typing support for NumPy is not available
# but typing support is on the road:
# see: https://github.com/numpy/numpy-stubs
NpArray = Any # TODO: replace with numpy.ndarray, when supported
NpMatrix = Any # TODO: replace with numpy.matrix, when supported
NpRecArray = Any # TODO: replace with numpy.recarray, when supported
NpDtype = Any # TODO: replace with numpy.dtype, when supported
NpArraySeq = Sequence[NpArray]
NpMatrixSeq = Sequence[NpMatrix]
NpArrayLike = Union[Num, NpArray, NpArraySeq, NpMatrix, NpMatrixSeq]
OptNpRecArray = Optional[NpRecArray]
OptNpArray = Optional[NpArray]
NpArrayFunc = Callable[..., NpArray]
NpRecArrayFunc = Callable[..., NpRecArray]
NpMatrixFunc = Callable[..., NpMatrix]
# TODO: (2018.09) currently typing for callables with variing numbers of
# arguments is not supported by the typing module, but on the road:
# see: https://github.com/python/typing/issues/264
# TODO: specify arguments, when supported
# FuncOfNpArray = Callable[[NpArray, ...], Any]
# NpArrayFuncOfNpArray = Callable[[NpArray, ...], NpArray]