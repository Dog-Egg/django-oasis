"""
该模块编写了一些 Sphinx 的扩展。
"""

import functools
import hashlib
import importlib
import importlib.util
import json
import os
import traceback
import types
import uuid
from collections import defaultdict
from html import escape

import django
import docutils
import docutils.nodes
import sphinx
from django.apps import apps
from django.conf import settings
from docutils.parsers.rst import directives
from sphinx.directives.code import LiteralInclude
from sphinx.util.docutils import SphinxDirective

from django_oasis.core import OpenAPI
from django_oasis.docs import _get_swagger_ui_html


class OasisDirective(SphinxDirective):
    has_content = False
    required_arguments = 1

    __docname_to_samples = defaultdict(list)  # 用于将同一文档中的 sample 进行分组编号

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.samplename = self.arguments[0]

        docname = self.env.docname
        try:
            index = self.__docname_to_samples[docname].index(self.samplename)
        except ValueError:
            self.__docname_to_samples[docname].append(self.samplename)
            index = len(self.__docname_to_samples[docname]) - 1
        self.alias = f"[示例{index + 1}]"

    def module_path(self, module_name):
        return os.path.join(
            os.path.dirname(__file__),
            "samples",
            self.samplename,
            module_name,
        )


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
        "django-settings-module": directives.unchanged,
    }

    def get_default_settings(self):
        from django.urls import include, path

        try:
            urls_module = import_module_from_file(self.module_path("urls.py"))
        except FileNotFoundError:
            openapi = OpenAPI()
            openapi.add_resources(import_module_from_file(self.module_path("views.py")))
            urlpatterns = [
                path("", include(openapi.urls)),
            ]
            urls_module = type(
                "module",
                (),
                {
                    "urlpatterns": urlpatterns,
                },
            )
        return dict(ROOT_URLCONF=urls_module)

    @print_exc
    def run(self):
        from django.test import Client, override_settings
        from django.urls import get_resolver, reverse

        client = Client()

        if "django-settings-module" in self.options:
            module = import_module_from_file(
                self.module_path(self.options["django-settings-module"])
            )
            module_settings = {}
            for k, v in vars(module).items():
                if k.isupper():
                    module_settings[k] = v
        else:
            module_settings = self.get_default_settings()

        with override_settings(**module_settings):
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

        html_url = self.add_swagger_html(
            {
                "url": self.add_spec_file(
                    hashlib.md5(
                        f"{self.env.docname}:{self.lineno}".encode()
                    ).hexdigest()[:8]
                    + ".json",
                    json.dumps(response.json()),
                ),
                **extra_config,
            }
        )

        iframe_id = "id_" + uuid.uuid4().hex[:8]
        iframe = f"""
            <div style="border: 1px solid var(--color-background-border);">
                <div class="code-block-caption">
                    <span class="caption-text">SwaggerUI {self.alias}</span>
                </div>
                <iframe id="{iframe_id}" src="{html_url}" loading="lazy" frameborder="0" style="min-width: 100%; display: block;"></iframe>
            </div>
            <script src="{self.get_full_url('_static/iframeResizer.min.js')}"></script>
            <script>
                iFrameResize({{checkOrigin: false}}, '#{iframe_id}')
            </script>
            """

        return [docutils.nodes.raw(text=iframe, format="html")]

    def add_spec_file(self, filename: str, data: str):
        dirname = "_spec"
        dirpath = os.path.join(self.env.app.outdir, dirname)
        os.makedirs(dirpath, exist_ok=True)
        with open(os.path.join(dirpath, filename), "w") as fp:
            fp.write(data)
        return self.get_full_url(f"{dirname}/{filename}")

    def add_swagger_html(self, config: dict):
        html = _get_swagger_ui_html(
            config,
            insert_head=f"""
                <script src="{self.get_full_url('_static/iframeResizer.contentWindow.min.js')}"></script>
                <script src="{self.get_full_url('_static/swagger-ui-bundle.js')}"></script>
                <link rel="stylesheet" href="{self.get_full_url('_static/swagger-ui.css')}" />
                """,
            env="sphinx",
        )
        dirname = "_swagger"
        filename = (
            hashlib.md5(f"{self.env.docname}:{self.lineno}".encode()).hexdigest()
            + ".html"
        )
        dirpath = os.path.join(self.env.app.outdir, dirname)
        os.makedirs(dirpath, exist_ok=True)
        with open(
            os.path.join(dirpath, filename),
            "w",
        ) as fp:
            fp.write(html)
        return self.get_full_url(f"{dirname}/{filename}")

    @property
    def base_url(self):
        return self.env.config.html_baseurl

    def get_full_url(self, relative_path):
        base_url = self.config.html_baseurl.rstrip("/")
        return f"{base_url}/{relative_path.lstrip('/')}"


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
        self.arguments = [f"/../samples/{root}/{relfile}"]
        self.options["caption"] = f"{relfile} {self.alias}"
        return super().run()


settings.configure(
    DEBUG=True,
    SECRET_KEY="docs",
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                ],
            },
        },
    ],
    USE_TZ=False,  # django 5.0 之后该值默认为 True
)


def setup(app):
    django.setup()

    app.add_directive("oasis-swaggerui", OasisSwaggerUI)
    app.add_directive("oasis-literalinclude", OasisLiteralInclude)

    return {
        "version": sphinx.__display_version__,
        "parallel_read_safe": False,
        "parallel_write_safe": False,
    }
