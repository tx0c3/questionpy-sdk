#  This file is part of the QuestionPy SDK. (https://questionpy.org)
#  The QuestionPy SDK is free software released under terms of the MIT license. See LICENSE.md.
#  (c) Technische Universität Berlin, innoCampus <info@isis.tu-berlin.de>

import json
from typing import TYPE_CHECKING

import aiohttp_jinja2
from aiohttp import web
from aiohttp.web_exceptions import HTTPFound

from questionpy_common.environment import RequestUser
from questionpy_sdk.webserver.app import SDK_WEBSERVER_APP_KEY, WebServer
from questionpy_sdk.webserver.context import contextualize
from questionpy_sdk.webserver.state_storage import get_nested_form_data, parse_form_data

if TYPE_CHECKING:
    from questionpy_server.worker.worker import Worker

routes = web.RouteTableDef()


@routes.get("/")
async def render_options(request: web.Request) -> web.Response:
    """Gets the options form definition that allows a question creator to customize a question."""
    webserver = request.app[SDK_WEBSERVER_APP_KEY]
    stored_state = webserver.state_storage.get(webserver.package_location)
    old_state = json.dumps(stored_state) if stored_state else None

    worker: Worker
    async with webserver.worker_pool.get_worker(webserver.package_location, 0, None) as worker:
        manifest = await worker.get_manifest()
        form_definition, form_data = await worker.get_options_form(RequestUser(["de", "en"]), old_state)

    context = {
        "manifest": manifest,
        "options": contextualize(form_definition=form_definition, form_data=form_data).model_dump(),
    }

    return aiohttp_jinja2.render_template("options.html.jinja2", request, context)


async def _save_updated_form_data(form_data: dict, webserver: "WebServer") -> None:
    stored_state = webserver.state_storage.get(webserver.package_location)
    old_state = json.dumps(stored_state) if stored_state else None
    worker: Worker
    async with webserver.worker_pool.get_worker(webserver.package_location, 0, None) as worker:
        question = await worker.create_question_from_options(RequestUser(["de", "en"]), old_state, form_data=form_data)

    webserver.state_storage.insert(webserver.package_location, json.loads(question.question_state))


@routes.post("/submit")
async def submit_form(request: web.Request) -> web.Response:
    """Stores the form_data from the Options Form in the StateStorage."""
    webserver = request.app[SDK_WEBSERVER_APP_KEY]
    form_data = parse_form_data(await request.json())
    await _save_updated_form_data(form_data, webserver)

    return web.Response(status=201)


@routes.post("/repeat")
async def repeat_element(request: web.Request) -> web.Response:
    """Adds Repetitions to the referenced RepetitionElement and store the form_data in the StateStorage."""
    webserver = request.app[SDK_WEBSERVER_APP_KEY]
    data = await request.json()
    question_form_data = parse_form_data(data["form_data"])
    repetition_list = get_nested_form_data(question_form_data, data["repetition_name"])
    if isinstance(repetition_list, list) and "increment" in data:
        repetition_list.extend([repetition_list[-1]] * int(data["increment"]))

    await _save_updated_form_data(question_form_data, webserver)
    return HTTPFound("/")


@routes.post("/options/remove-repetition")
async def remove_element(request: web.Request) -> web.Response:
    webserver = request.app[SDK_WEBSERVER_APP_KEY]
    data = await request.json()
    question_form_data = parse_form_data(data["form_data"])
    repetition_list = get_nested_form_data(question_form_data, data["repetition_name"])
    if isinstance(repetition_list, list) and "index" in data:
        del repetition_list[int(data["index"])]

    await _save_updated_form_data(question_form_data, webserver)
    return HTTPFound("/")
