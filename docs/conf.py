import sys
from pathlib import Path

from sphinx.application import Sphinx

sys.path.append((Path(__file__).parent / "_samples").as_posix())

project = "django-oasis"

extensions = [
    "sphinx_swaggerui",
]


def _import_string(dotpath: str):
    import importlib

    module_path, _, class_name = dotpath.rpartition(".")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def setup(app: Sphinx):
    def swaggerui_process_config(app, config: dict):
        from openapi.routing import Router

        router_dotpath = config.pop("$router", None)
        if router_dotpath is not None:
            router: Router = _import_string(router_dotpath)
            config.update(spec=router.spec())

    app.connect("swaggerui-process-config", swaggerui_process_config)
