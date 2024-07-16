import functools
import hashlib
from collections import defaultdict

from django.http import HttpRequest, HttpResponse, HttpResponseNotModified
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from django_oasis.core import OpenAPI


def _get_swagger_ui_html(config: dict, insert_head="", env=None):
    return render_to_string(
        "swagger-ui.html",
        context=dict(
            config=config,
            insert_head=insert_head,
            env=env,
        ),
    )


@functools.lru_cache
def _get_swagger_ui_urls():
    from django.urls import URLPattern, URLResolver, get_resolver

    from django_oasis.core import OpenAPI

    spec_view = OpenAPI.spec_view
    lookup_str = spec_view.__module__ + "." + spec_view.__qualname__

    def _traverse_pattern_endpoints(patterns, namespaces=None):
        # 变量所有路由端点，找出 OpenAPI.spec_view 函数及路由名称(命名空间)。
        namespaces = namespaces or []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                if pattern.lookup_str == lookup_str:
                    yield namespaces, pattern.name, pattern.callback
            elif isinstance(pattern, URLResolver):
                ns = namespaces.copy()
                if pattern.namespace:
                    ns.append(pattern.namespace)
                yield from _traverse_pattern_endpoints(pattern.url_patterns, ns)

    patterns = get_resolver().url_patterns
    name_to_urls = defaultdict(list)
    for namespaces, view_name, view in _traverse_pattern_endpoints(patterns):
        name_to_urls[view.__self__.title].append(
            reverse_lazy(":".join(namespaces + [view_name]))
        )

    rv = []
    for name, urls in name_to_urls.items():
        for i, url in enumerate(urls):
            if i > 0:
                name = "%s(%s)" % (name, i)
            rv.append(dict(name=name, url=url))
    return rv


def swagger_ui(*openapi: OpenAPI):

    def view(request: HttpRequest):
        urls = _get_swagger_ui_urls()

        if not urls:
            config = {}
        elif len(urls) == 1:
            config = {"url": urls[0]["url"]}
        else:
            config = {"urls": urls}

        content = _get_swagger_ui_html(config)

        etag = '"%s"' % hashlib.sha1(content.encode()).hexdigest()
        if request.headers.get("If-None-Match") == etag:
            return HttpResponseNotModified()
        return HttpResponse(content, headers={"ETag": etag})

    return view
