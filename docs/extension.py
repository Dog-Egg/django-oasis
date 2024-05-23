"""
该模块编写了一些 Sphinx 的扩展。
"""

import functools
import importlib
import importlib.util
import os
import traceback
import types
import uuid
from html import escape

import django
import docutils
import docutils.nodes
import sphinx
from django.apps import apps
from docutils.parsers.rst import directives
from sphinx.directives.code import LiteralInclude
from sphinx.util.docutils import SphinxDirective

from django_oasis.core import OpenAPI
from django_oasis.docs import _get_swagger_ui_html


class OasisDirective(SphinxDirective):
    has_content = False
    required_arguments = 1

    __rootname2alias = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rootname = self.arguments[0]

        if self.rootname not in self.__rootname2alias:
            self.__rootname2alias[self.rootname] = (
                f"[示例{len(self.__rootname2alias) + 1}]"
            )
        self.alias = self.__rootname2alias[self.rootname]

    def module_path(self, module_name):
        return os.path.join(
            os.path.dirname(__file__),
            "examples",
            self.rootname,
            module_name,
        )

    def _rel_src(self, filename):
        relpath = os.path.relpath(
            self.env.srcdir, os.path.dirname(self.get_source_info()[0])
        )
        return os.path.join(relpath, filename)


def print_exc(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            raise

    return wrapper


class OasisSwaggerUI(OasisDirective):
    option_spec = {
        "doc-expansion": directives.unchanged,
    }

    def get_urlconf(self):
        from django.urls import include, path

        try:
            return import_module_from_file(self.module_path("urls.py"))
        except FileNotFoundError:
            openapi = OpenAPI()
            openapi.add_resources(import_module_from_file(self.module_path("views.py")))
            module = type(
                "module",
                (),
                {
                    "urlpatterns": [
                        path("", include(openapi.urls)),
                    ]
                },
            )
            return module

    @print_exc
    def run(self):
        from django.test import Client, override_settings
        from django.urls import get_resolver, reverse

        client = Client()

        with override_settings(ROOT_URLCONF=self.get_urlconf()):
            resolver = get_resolver()
            for view in resolver.reverse_dict.keys():
                if (
                    isinstance(view, types.MethodType)
                    and view.__func__ is OpenAPI.spec_view
                ):
                    url = reverse(view)
                    break
            else:
                raise RuntimeError("Can't find OpenAPI spec view")
            response = client.get(url)

        extra_config = {}
        if "doc-expansion" in self.options:
            extra_config["docExpansion"] = self.options["doc-expansion"]

        html = _get_swagger_ui_html(
            {
                "spec": response.json(),
                **extra_config,
            },
            insert_head=f"""
                <script src="{self._rel_src('_static/iframeResizer.contentWindow.min.js')}"></script>
                <script src="{self._rel_src('_static/swagger-ui-bundle.js')}"></script>
                <link rel="stylesheet" href="{self._rel_src('_static/swagger-ui.css')}" />
                """,
            env="sphinx",
        )

        iframe_id = "id_" + uuid.uuid4().hex[:8]
        iframe = f"""
            <div style="border: 1px solid var(--color-background-border);">
                <div class="code-block-caption">
                    <span class="caption-text">SwaggerUI {self.alias}</span>
                </div>
                <iframe id="{iframe_id}" srcdoc="{escape(html)}" frameborder="0" style="min-width: 100%; display: block;"></iframe>
            </div>
            <script src="{self._rel_src('_static/iframeResizer.min.js')}"></script>
            <script>
                iFrameResize({{checkOrigin: false}}, '#{iframe_id}')
            </script>
            """

        return [docutils.nodes.raw(text=iframe, format="html")]


def import_module_from_file(path):
    name = os.path.splitext(os.path.relpath(path, os.path.dirname(__file__)))[
        0
    ].replace("/", ".")

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)

    INSTALLED_APPS = [
        module.__name__.rsplit(".", 1)[0],  # 将该模块所在的上级模块注册为 Django APP
        "django_oasis",
    ]
    apps.set_installed_apps(INSTALLED_APPS)

    spec.loader.exec_module(module)
    return module


class OasisLiteralInclude(LiteralInclude, OasisDirective):
    required_arguments = 2

    def run(self):
        root = self.arguments[0]
        relfile = self.arguments[1]
        self.arguments = [f"/../examples/{root}/{relfile}"]
        self.options["caption"] = f"{relfile} {self.alias}"
        return super().run()


def setup(app):
    django.setup()

    app.add_directive("oasis-swaggerui", OasisSwaggerUI)
    app.add_directive("oasis-literalinclude", OasisLiteralInclude)

    return {
        "version": sphinx.__display_version__,
        "parallel_read_safe": False,
        "parallel_write_safe": False,
    }
