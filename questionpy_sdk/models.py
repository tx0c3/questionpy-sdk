#  This file is part of the QuestionPy SDK. (https://questionpy.org)
#  The QuestionPy SDK is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>

from collections.abc import Mapping
from typing import Literal

from questionpy_common.manifest import Manifest

BuildHookName = Literal["pre", "post"]


class PackageConfig(Manifest):
    """A QuestionPy source package configuration.

    This class expands upon [`Manifest`][questionpy_common.manifest.Manifest] by incorporating additional configuration
    parameters.
    """

    build_hooks: Mapping[BuildHookName, str | list[str]] = {}

    @property
    def manifest(self) -> Manifest:
        """Creates [`Manifest`][questionpy_common.manifest.Manifest] from config model."""
        return Manifest.model_validate(dict(self))
