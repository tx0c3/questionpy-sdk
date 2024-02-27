import jinja2
from jinja2 import PrefixLoader
from questionpy_common.api.attempt import BaseAttempt
from questionpy_common.api.qtype import BaseQuestionType
from questionpy_common.api.question import BaseQuestion
from questionpy_common.environment import Package, get_qpy_environment


def _loader_for_package(package: Package) -> jinja2.BaseLoader:
    return jinja2.PackageLoader(f"{package.manifest.namespace}.{package.manifest.short_name}")


def create_jinja2_environment(attempt: BaseAttempt, question: BaseQuestion,
                              qtype: BaseQuestionType) -> jinja2.Environment:
    qpy_env = get_qpy_environment()

    package_loaders = {f"{p.manifest.namespace}.{p.manifest.short_name}": _loader_for_package(p)
                       for p in qpy_env.packages.values()}

    env = jinja2.Environment(loader=PrefixLoader(mapping=package_loaders))
    env.globals.update({
        "environment": qpy_env,
        "attempt": attempt,
        "question": question,
        "question_type": qtype
    })

    return env
