import importlib.util
import os
import traceback
import uuid
from html import escape

import django
from django.apps import apps
from django.conf import settings
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from django_oasis.docs import _get_swagger_ui_html

from ..utils import generate_id


class OpenAPIView(SphinxDirective):
    has_content = True
    option_spec = {
        "docexpansion": directives.unchanged,
    }

    def run(self):
        try:
            rel_filename, filename = self.env.relfn2path(self.content[0])
            module = import_module_from_file(filename)

            extra_config = {}
            if "docexpansion" in self.options:
                extra_config["docExpansion"] = self.options["docexpansion"]

            def getsrc(filename):
                relpath = os.path.relpath(
                    self.env.srcdir, os.path.dirname(self.get_source_info()[0])
                )
                result = os.path.join(relpath, filename)
                return result

            html = _get_swagger_ui_html(
                {
                    "spec": parse_module(module),
                    **extra_config,
                },
                insert_head=f"""
                <script src="{getsrc('_static/iframeResizer.contentWindow.min.js')}"></script>
                <script src="{getsrc('_static/swagger-ui-bundle.js')}"></script>
                <link rel="stylesheet" href="{getsrc('_static/swagger-ui.css')}" />
                """,
                env="sphinx",
            )

            iframe_id = "id_" + uuid.uuid4().hex[:8]
            iframe = f"""
            <div style="border: 1px solid var(--color-background-border);">
                <div class="code-block-caption">
                    <span class="caption-text">由 <a href="#{generate_id(rel_filename)}">{os.path.split(filename)[1]}</a> 解析获得</span>
                </div>
                <iframe id="{iframe_id}" srcdoc="{escape(html)}" frameborder="0" style="min-width: 100%; display: block;"></iframe>
            </div>
            <script src="{getsrc('_static/iframeResizer.min.js')}"></script>
            <script>
                iFrameResize({{checkOrigin: false}}, '#{iframe_id}')
            </script>
            """

            node = nodes.raw(text=iframe, format="html")
            return [node]
        except Exception as exc:
            traceback.print_exc()
            return [self.state.document.reporter.warning(exc, line=self.lineno)]


def parse_module(module):
    """添加模块内的 Resource 对象，解析为 OpenAPI Specification"""
    from devtools import get_openapi_from_module

    openapi = get_openapi_from_module(module)
    oas = openapi.get_spec()
    return oas


def import_module_from_file(path):
    """将文件导入为模块"""
    name = os.path.splitext(os.path.relpath(path, os.getcwd()))[0].replace("/", ".")

    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)

    INSTALLED_APPS = [
        module.__name__.rsplit(".", 1)[0],  # 将该模块所在的上级模块注册为 Django APP
        "django_oasis",
    ]
    apps.set_installed_apps(INSTALLED_APPS)

    spec.loader.exec_module(module)
    return module


settings.configure(
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

    app.add_directive("openapiview", OpenAPIView)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
