# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import typing


def fqname(
        obj,  # type: typing.Any
):  # type: (...) -> str
    """
    .. todo:: Check whether :func:`fqname()` could be factorized with :func:`scenario._reflex.qualname()`.
    """
    if inspect.ismodule(obj):
        return str(obj.__name__)
    return f"{inspect.getmodule(obj)}.{obj.__name__}"


def isspecialfunction(
        obj,  # type: typing.Any
):  # type: (...) -> bool
    """
    Due to [sphinx#6808](https://github.com/sphinx-doc/sphinx/issues/6808), it seems preferrable to rely on the actual object,
    rather than the ``what`` and ``name`` parameters, in this class's *autodoc* handlers,
    which behaviour does not always conform to their respective documentation.

    Inspired from:
    - https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method
    - https://docs.python.org/3/reference/datamodel.html
    """
    return (inspect.isfunction(obj) or inspect.ismethod(obj)) and (obj.__name__ in (
        # 3. Data model (https://docs.python.org/3/reference/datamodel.html#data-model)
        # 3.1. Objects, values and types (https://docs.python.org/3/reference/datamodel.html#objects-values-and-types)
        # 3.2. The standard type hierarchy (https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy)
        #     Memo: Interesting description about special attributes.
        # 3.3. Special method names (https://docs.python.org/3/reference/datamodel.html#special-method-names)
        # 3.3.1. Basic customization (https://docs.python.org/3/reference/datamodel.html#basic-customization).
        "__new__",              # https://docs.python.org/3/reference/datamodel.html#object.__new__
        "__init__",             # https://docs.python.org/3/reference/datamodel.html#object.__init__
        "__del__",              # https://docs.python.org/3/reference/datamodel.html#object.__del__
        "__repr__",             # https://docs.python.org/3/reference/datamodel.html#object.__repr__
        "__str__",              # https://docs.python.org/3/reference/datamodel.html#object.__str__
        "__bytes__",            # https://docs.python.org/3/reference/datamodel.html#object.__bytes__
        "__format__",           # https://docs.python.org/3/reference/datamodel.html#object.__format__
        "__lt__",               # https://docs.python.org/3/reference/datamodel.html#object.__lt__
        "__le__",               # https://docs.python.org/3/reference/datamodel.html#object.__le__
        "__eq__",               # https://docs.python.org/3/reference/datamodel.html#object.__eq__
        "__ne__",               # https://docs.python.org/3/reference/datamodel.html#object.__ne__
        "__gt__",               # https://docs.python.org/3/reference/datamodel.html#object.__gt__
        "__ge__",               # https://docs.python.org/3/reference/datamodel.html#object.__ge__
        "__hash__",             # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        "__bool__",             # https://docs.python.org/3/reference/datamodel.html#object.__bool__
        # 3.3.2. Customizing attribute access (https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access)
        "__getattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        "__getattributes__",    # https://docs.python.org/3/reference/datamodel.html#object.__getattribute__
        "__setattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__setattr__
        "__delattr__",          # https://docs.python.org/3/reference/datamodel.html#object.__delattr__
        "__dir__",              # https://docs.python.org/3/reference/datamodel.html#object.__dir__
        # 3.3.2.1. Customizing module attribute access (https://docs.python.org/3/reference/datamodel.html#customizing-module-attribute-access)
        # 3.3.2.2. Implementing Descriptors (https://docs.python.org/3/reference/datamodel.html#implementing-descriptors)
        "__get__",              # https://docs.python.org/3/reference/datamodel.html#object.__get__
        "__set__",              # https://docs.python.org/3/reference/datamodel.html#object.__set__
        "__delete__",           # https://docs.python.org/3/reference/datamodel.html#object.__delete__
        # 3.3.2.3. Invoking Descriptors (https://docs.python.org/3/reference/datamodel.html#invoking-descriptors)
        # 3.3.2.4. __slots__ (https://docs.python.org/3/reference/datamodel.html#slots)
        "__slots__",            # https://docs.python.org/3/reference/datamodel.html#object.__slots__
        # 3.3.2.4.1. Notes on using __slots__ (https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots)
        # 3.3.3. Customizing class creation (https://docs.python.org/3/reference/datamodel.html#customizing-class-creation)
        "__init_subclass__",    # https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__
        "__set_name__",         # https://docs.python.org/3/reference/datamodel.html#object.__set_name__
        # 3.3.3.1. Metaclasses (https://docs.python.org/3/reference/datamodel.html#metaclasses)
        # 3.3.3.2. Resolving MRO entries (https://docs.python.org/3/reference/datamodel.html#resolving-mro-entries)
        # 3.3.3.3. Determining the appropriate metaclass (https://docs.python.org/3/reference/datamodel.html#determining-the-appropriate-metaclass)
        # 3.3.3.4. Preparing the class namespace (https://docs.python.org/3/reference/datamodel.html#preparing-the-class-namespace)
        # 3.3.3.5. Executing the class body (https://docs.python.org/3/reference/datamodel.html#executing-the-class-body)
        # 3.3.3.6. Creating the class object (https://docs.python.org/3/reference/datamodel.html#creating-the-class-object)
        # 3.3.3.7. Uses for metaclasses (https://docs.python.org/3/reference/datamodel.html#uses-for-metaclasses)
        # 3.3.4. Customizing instance and subclass checks (https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks)
        "__instancecheck__",    # https://docs.python.org/3/reference/datamodel.html#class.__instancecheck__
        "__subclasscheck__",    # https://docs.python.org/3/reference/datamodel.html#class.__subclasscheck__
        # 3.3.5. Emulating generic types (https://docs.python.org/3/reference/datamodel.html#emulating-generic-types)
        "__class_getitem__",    # https://docs.python.org/3/reference/datamodel.html#object.__class_getitem__
        # 3.3.5.1. The purpose of __class_getitem__ (https://docs.python.org/3/reference/datamodel.html#the-purpose-of-class-getitem)
        # 3.3.5.2. __class_getitem__ versus __getitem__ (https://docs.python.org/3/reference/datamodel.html#class-getitem-versus-getitem)
        # 3.3.6. Emulating callable objects (https://docs.python.org/3/reference/datamodel.html#emulating-callable-objects)
        "__call__",             # https://docs.python.org/3/reference/datamodel.html#object.__call__
        # 3.3.7. Emulating container types (https://docs.python.org/3/reference/datamodel.html#emulating-container-types)
        "__len__",              # https://docs.python.org/3/reference/datamodel.html#object.__len__
        "__length_hint__",      # https://docs.python.org/3/reference/datamodel.html#object.__length_hint__
        "__getitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__getitem__
        "__setitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__setitem__
        "__delitem__",          # https://docs.python.org/3/reference/datamodel.html#object.__delitem__
        "__missing__",          # https://docs.python.org/3/reference/datamodel.html#object.__missing__
        "__iter__",             # https://docs.python.org/3/reference/datamodel.html#object.__iter__
        "__reversed__",         # https://docs.python.org/3/reference/datamodel.html#object.__reversed__
        "__contains__",         # https://docs.python.org/3/reference/datamodel.html#object.__contains__
        # 3.3.8. Emulating numeric types (https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types)
        "__add__",              # https://docs.python.org/3/reference/datamodel.html#object.__add__
        "__sub__",              # https://docs.python.org/3/reference/datamodel.html#object.__sub__
        "__mul__",              # https://docs.python.org/3/reference/datamodel.html#object.__mul__
        "__matmul__",           # https://docs.python.org/3/reference/datamodel.html#object.__matmul__
        "__truediv__",          # https://docs.python.org/3/reference/datamodel.html#object.__truediv__
        "__floordiv__",         # https://docs.python.org/3/reference/datamodel.html#object.__floordiv__
        "__mod__",              # https://docs.python.org/3/reference/datamodel.html#object.__mod__
        "__divmod__",           # https://docs.python.org/3/reference/datamodel.html#object.__divmod__
        "__pow__",              # https://docs.python.org/3/reference/datamodel.html#object.__pow__
        "__lshift__",           # https://docs.python.org/3/reference/datamodel.html#object.__lshift__
        "__rshift__",           # https://docs.python.org/3/reference/datamodel.html#object.__rshift__
        "__and__",              # https://docs.python.org/3/reference/datamodel.html#object.__and__
        "__xor__",              # https://docs.python.org/3/reference/datamodel.html#object.__xor__
        "__or__",               # https://docs.python.org/3/reference/datamodel.html#object.__or__
        "__radd__",             # https://docs.python.org/3/reference/datamodel.html#object.__radd__
        "__rsub__",             # https://docs.python.org/3/reference/datamodel.html#object.__rsub__
        "__rmul__",             # https://docs.python.org/3/reference/datamodel.html#object.__rmul__
        "__rmatmul__",          # https://docs.python.org/3/reference/datamodel.html#object.__rmatmul__
        "__rtruediv__",         # https://docs.python.org/3/reference/datamodel.html#object.__rtruediv__
        "__rfloordiv__",        # https://docs.python.org/3/reference/datamodel.html#object.__rfloordiv__
        "__rmod__",             # https://docs.python.org/3/reference/datamodel.html#object.__rmod__
        "__rdivmod__",          # https://docs.python.org/3/reference/datamodel.html#object.__rdivmod__
        "__rpow__",             # https://docs.python.org/3/reference/datamodel.html#object.__rpow__
        "__rlshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__rlshift__
        "__rrshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__rrshift__
        "__rand__",             # https://docs.python.org/3/reference/datamodel.html#object.__rand__
        "__rxor__",             # https://docs.python.org/3/reference/datamodel.html#object.__rxor__
        "__ror__",              # https://docs.python.org/3/reference/datamodel.html#object.__ror__
        "__iadd__",             # https://docs.python.org/3/reference/datamodel.html#object.__iadd__
        "__isub__",             # https://docs.python.org/3/reference/datamodel.html#object.__isub__
        "__imul__",             # https://docs.python.org/3/reference/datamodel.html#object.__imul__
        "__imatmul__",          # https://docs.python.org/3/reference/datamodel.html#object.__imatmul__
        "__itruediv__",         # https://docs.python.org/3/reference/datamodel.html#object.__itruediv__
        "__ifloordiv__",        # https://docs.python.org/3/reference/datamodel.html#object.__ifloordiv__
        "__imod__",             # https://docs.python.org/3/reference/datamodel.html#object.__imod__
        "__ipow__",             # https://docs.python.org/3/reference/datamodel.html#object.__ipow__
        "__ilshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__ilshift__
        "__irshift__",          # https://docs.python.org/3/reference/datamodel.html#object.__irshift__
        "__iand__",             # https://docs.python.org/3/reference/datamodel.html#object.__iand__
        "__ixor__",             # https://docs.python.org/3/reference/datamodel.html#object.__ixor__
        "__ior__",              # https://docs.python.org/3/reference/datamodel.html#object.__ior__
        "__neg__",              # https://docs.python.org/3/reference/datamodel.html#object.__neg__
        "__pos__",              # https://docs.python.org/3/reference/datamodel.html#object.__pos__
        "__abs__",              # https://docs.python.org/3/reference/datamodel.html#object.__abs__
        "__invert__",           # https://docs.python.org/3/reference/datamodel.html#object.__invert__
        "__complex__",          # https://docs.python.org/3/reference/datamodel.html#object.__complex__
        "__int__",              # https://docs.python.org/3/reference/datamodel.html#object.__int__
        "__float__",            # https://docs.python.org/3/reference/datamodel.html#object.__float__
        "__index__",            # https://docs.python.org/3/reference/datamodel.html#object.__index__
        "__round__",            # https://docs.python.org/3/reference/datamodel.html#object.__round__
        "__trunc__",            # https://docs.python.org/3/reference/datamodel.html#object.__trunc__
        "__floor__",            # https://docs.python.org/3/reference/datamodel.html#object.__floor__
        "__ceil__",             # https://docs.python.org/3/reference/datamodel.html#object.__ceil__
        # 3.3.9. With Statement Context Managers (https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers)
        "__enter__",            # https://docs.python.org/3/reference/datamodel.html#object.__enter__
        "__exit__",             # https://docs.python.org/3/reference/datamodel.html#object.__exit__
        # 3.3.10. Customizing positional arguments in class pattern matching
        #         (https://docs.python.org/3/reference/datamodel.html#customizing-positional-arguments-in-class-pattern-matching)
        # 3.3.11. Special method lookup (https://docs.python.org/3/reference/datamodel.html#special-method-lookup)
        # 3.4. Coroutines (https://docs.python.org/3/reference/datamodel.html#coroutines)
        # 3.4.1. Awaitable Objects (https://docs.python.org/3/reference/datamodel.html#awaitable-objects)
        "__await__",            # https://docs.python.org/3/reference/datamodel.html#object.__await__
        # 3.4.2. Coroutine Objects (https://docs.python.org/3/reference/datamodel.html#coroutine-objects)
        # 3.4.3. Asynchronous Iterators (https://docs.python.org/3/reference/datamodel.html#asynchronous-iterators)
        "__aiter__",            # https://docs.python.org/3/reference/datamodel.html#object.__aiter__
        "__anext__",            # https://docs.python.org/3/reference/datamodel.html#object.__anext__
        # 3.4.4. Asynchronous Context Managers (https://docs.python.org/3/reference/datamodel.html#asynchronous-context-managers)
        "__aenter__",           # https://docs.python.org/3/reference/datamodel.html#object.__aenter__
        "__aexit__",            # https://docs.python.org/3/reference/datamodel.html#object.__aexit__

        # Other special methods.
        "__fspath__",           # https://docs.python.org/3/library/os.html#os.PathLike.__fspath__
    ))
