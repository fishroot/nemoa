# -*- coding: utf-8 -*-
"""Types."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from abc import ABC, abstractmethod
import array
import collections
import datetime
import io
import os
import types
from typing import Any, Callable, ClassVar, ContextManager, Dict, Hashable, IO
from typing import Iterable, Iterator, List, Optional, Sequence, Set, Tuple
from typing import Type, TypeVar, Union, Container, Sized
#from nemoa.file import stream

# Type-Variables for Generic Structural Types
S = TypeVar('S')
T = TypeVar('T')

################################################################################
# Constants
################################################################################

NaN = float('nan')
Infty = float('inf')
void: Callable[..., None] = lambda *args, **kwds: None

################################################################################
# Stub Classes
################################################################################

class FileAccessorBase(ABC):
    """FileHandler Base Class."""

    name: str

    @abstractmethod
    def open(self, *args: Any, **kwds: Any) -> io.IOBase:
        raise NotImplementedError(
            f"'type(self).__name__' requires to implement 'open'")

################################################################################
# Classes
################################################################################

Array = array.ArrayType
Date = datetime.datetime
Function = types.FunctionType
Method = types.MethodType
Module = types.ModuleType
OrderedDict = collections.OrderedDict
Collection = collections.Collection
Path = os.PathLike
BytesIOBaseClass = io.BufferedIOBase
TextIOBaseClass = io.TextIOBase
Traceback = types.TracebackType

################################################################################
# ClassInfos
################################################################################

CallableClasses = (Function, Method)
PathLikeClasses = (str, Path)
FileClasses = (BytesIOBaseClass, TextIOBaseClass)
TextFileClasses = (str, Path, TextIOBaseClass)
ClassInfoClasses = (type, tuple)

################################################################################
# Structural Types for Literals and Collections of Literals
################################################################################

# Numbers
RealNumber = Union[int, float]
Number = Union[RealNumber, complex]
OptNumber = Optional[Number]

# Literals
OptType = Optional[type]
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptComplex = Optional[complex]
OptBool = Optional[bool]
OptBytes = Optional[bytes]
OptArray = Optional[Array]
StrOrBool = Union[str, bool]
OptStrOrBool = Optional[StrOrBool]
StrOrInt = Union[str, int]
BytesLike = Union[bytes, bytearray, memoryview]
BytesLikeOrStr = Union[BytesLike, str]

# Classes
Class = Type[Any]
OptClass = Optional[Class]
ClassInfo = Union[Class, Tuple[Class, ...]]
OptClassInfo = Optional[ClassInfo]

# Collections of numbers
RealVector = Sequence[RealNumber]
Vector = Sequence[Number]

# Collections of literals
HashDict = Dict[Hashable, Any]
AnyDict = Dict[Any, Any]
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
StrOrDict = Union[str, AnyDict]
StrOrType = Union[type, str]
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
StrPairDict = Dict[StrPair, Any]
StrListPair = Tuple[StrList, StrList]
StrTupleDict = Dict[Union[str, Tuple[str, ...]], Any]
RecDict = Dict[Any, StrDict]
DictOfRecDicts = Dict[Any, RecDict]

# Classvariables of Compounds
ClassStrList = ClassVar[StrList]
ClassDict = ClassVar[AnyDict]
ClassStrDict = ClassVar[StrDict]

################################################################################
# Structural Types for Callables and Collections of Callables
################################################################################

# Elementary Callables
AnyFunc = Callable[..., Any]
VoidFunc = Callable[..., None]
BoolFunc = Callable[..., bool]
RealFunc = Callable[..., RealNumber]
ScalarFunc = Callable[..., Number]
VectorFunc = Callable[..., Vector]
UnaryFunc = Callable[[Any], Any]
BinaryFunc = Callable[[Any, Any], Any]
TernaryFunc = Callable[[Any, Any, Any], Any]
TestFunc = Callable[[Any, Any], bool]

# Unions of Callables and Literals
OptVoidFunc = Optional[VoidFunc]
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
# Structural Types for standard library packages
################################################################################

# Generic Collections
IterAny = Iterator[Any]
IterNone = Iterator[None]
OptContainer = Optional[Container]
OptSized = Optional[Sized]

# Path Like
OptPath = Optional[Path]
PathList = List[Path]
StrDictOfPaths = Dict[str, Path]
PathLike = Union[str, Path]
PathLikeList = List[PathLike]
OptPathLike = Optional[PathLike]

# Exceptions
Exc = BaseException
ExcType = Type[Exc]
ExcInfo = Union[ExcType, Tuple[ExcType, ...]]

# BytesIO Like
BytesIOLike = IO[bytes]
IterBytesIOLike = Iterator[BytesIOLike]
CManBytesIOLike = ContextManager[BytesIOLike]

# StringIO Like
StringIOLike = IO[str]
IterStringIOLike = Iterator[StringIOLike]
CManStringIOLike = ContextManager[StringIOLike]

# File Like
FileLike = Union[BytesIOLike, StringIOLike]
IterFileLike = Iterator[FileLike]
CManFileLike = ContextManager[FileLike]

# File References
FileOrPathLike = Union[FileLike, PathLike]
FileRef = Union[FileOrPathLike, FileAccessorBase]

################################################################################
# Structural Types for external Packages
################################################################################

# Numpy
# TODO (patrick.michl@gmail.com): Currently (numpy 1.15.3) typing support for
# numpy is not available but a workaround is in progress, see:
# https://github.com/numpy/numpy-stubs
NpShape = Optional[IntTuple]
NpShapeLike = Optional[Union[int, Sequence[int]]]
NpAxes = Union[None, int, IntTuple]
NpFields = Union[None, str, Iterable[str]]
NpArray = Any # TODO: Replace with numpy.ndarray, when supported
NpMatrix = Any # TODO: replace with numpy.matrix, when supported
NpRecArray = Any # TODO: replace with numpy.recarray, when supported
NpDtype = Any # TODO: replace with numpy.dtype, when supported
NpArraySeq = Sequence[NpArray]
NpMatrixSeq = Sequence[NpMatrix]
NpArrayLike = Union[Number, NpArray, NpArraySeq, NpMatrix, NpMatrixSeq]
OptNpRecArray = Optional[NpRecArray]
OptNpArray = Optional[NpArray]
NpArrayFunc = Callable[..., NpArray]
NpRecArrayFunc = Callable[..., NpRecArray]
NpMatrixFunc = Callable[..., NpMatrix]
# TODO (patrick.michl@gmail.com): Currently (Python 3.7.1) the typing module
# does not support argument specification for callables with variing numbers of
# arguments, but this feature is in progress, see:
# https://github.com/python/typing/issues/264
# Use argument specification, when available:
# FuncOfNpArray = Callable[[NpArray, ...], Any]
# NpArrayFuncOfNpArray = Callable[[NpArray, ...], NpArray]

# NetworkX
