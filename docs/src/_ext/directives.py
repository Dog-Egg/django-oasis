import os

from docutils.parsers.rst import directives
from sphinx.directives.code import LiteralInclude

from .utils import generate_id


class MyLiteralInclude(LiteralInclude):
    def run(self):
        rel_filename, filename = self.env.relfn2path(self.arguments[0])

        self.options["name"] = generate_id(rel_filename)

        if "caption" not in self.options:
            self.options["caption"] = os.path.split(rel_filename)[1]

        return super().run()


def setup(app):
    directives.register_directive("myliteralinclude", MyLiteralInclude)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
