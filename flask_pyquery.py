
import importlib
import os

import flask
from flask.signals import template_rendered

import pyquery
import lxml.html

try:
    from flask import _app_ctx_stack as context_stack
except ImportError:
    from flask import _request_ctx_stack as context_stack

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)
__author__ = 'Lars P. Søndergaard'
__license__ = 'BSD'
__copyright__ = '(c) 2014 by Lars P. Søndergaard'
__all__ = ['Template', 'render_template']


class PyQueryTemplates:

    doctype_names = {
        'html5': '<!DOCTYPE html>'
    }

    def __init__(self, app=None, module_path='renderer'):
        self.app = None
        self.module_path = None
        self.renderer_module = None

        if app is not None:
            self.init_app(app, module_path)

    def init_app(self, app, module_path='renderer'):
        """Initalizes the application with the extension.

        :param app: The Flask application object.
        """
        if self.app:
            raise RuntimeError("Cannot call init_app when app argument was "
                               "provided to PyQueryTemplates constructor.")

        self.app = app

        self.module_path = module_path
        self.renderer_module = importlib.import_module(
            self.app.import_name + '.' + self.module_path)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['pyquery'] = self
        app._pyquery_lookup = None

        app.config.setdefault('PYQUERY_DOCTYPE', 'html5')


class TemplateError(Exception):
    pass


class Template:

    def __init__(self, template_path, renderer, kwargs):
        self.path = template_path
        self.renderer = renderer
        self.kwargs = kwargs

    def render(self, **context):
        with open(self.path, 'r', encoding='utf-8') as fp:
            source = fp.read()

        doc = pyquery.PyQuery(source, parser='html')
        doc = self.renderer(doc, context)

        if len(doc) != 1 or doc[0].tag != 'html':
            raise TemplateError(
                'There should only be one root document '
                'and it should be an <html> tag')

        return lxml.html.tostring(doc[0], doctype=self.kwargs['doctype'])


class TemplateLookup:

    def __init__(self, app, directories, **kwargs):
        self.app = app
        self.kwargs = kwargs
        self.directories = directories

    def get_template(self, template_name) -> Template:
        pq = self.app.extensions['pyquery']
        func = getattr(pq.renderer_module, template_name, None)
        if func is None:
            raise AttributeError('No such renderer {} in {}'
                                 .format(func, pq.renderer_module))

        filename = '{}.html'.format(template_name)
        for directory in self.directories:
            template_path = os.path.join(directory, filename)
            if os.path.exists(template_path)\
                    and os.path.isfile(template_path):
                return Template(template_path, func, self.kwargs)
        raise FileNotFoundError('No such template {!r}'.format(filename))


def _create_lookup(app: flask.Flask) -> TemplateLookup:
    pq = app.extensions['pyquery']
    doctype = app.config['PYQUERY_DOCTYPE']
    kwargs = {
        'doctype': pq.doctype_names.get(doctype, doctype)
    }

    if isinstance(app.template_folder, (list, tuple)):
        paths = [os.path.join(app.root_path, tf) for tf in app.template_folder]
    else:
        paths = [os.path.join(app.root_path, app.template_folder)]

    blueprints = getattr(app, 'blueprints', {})
    for blueprint in blueprints.values():
        bp_tf = blueprint.template_folder
        if bp_tf:
            if isinstance(bp_tf, (list, tuple)):
                paths.extend([os.path.join(blueprint.root_path, tf)
                              for tf in bp_tf])
            else:
                paths.append(os.path.join(blueprint.root_path, bp_tf))
    paths = [path for path in paths if os.path.isdir(path)]

    return TemplateLookup(app, directories=paths, **kwargs)


def _lookup(app: flask.Flask) -> TemplateLookup:
    if not app._pyquery_lookup:
        app._pyquery_lookup = _create_lookup(app)
    return app._pyquery_lookup


def _render(template: Template, context, app: flask.Flask):
    """Renders the template and fires the signal"""
    context.update(app.jinja_env.globals)
    app.update_template_context(context)
    try:
        rv = template.render(**context)
        template_rendered.send(app, template=template, context=context)
        return rv
    except:
        raise


def render_template(template_name, **context):
    """Renders a template from the template folder with the given
    context.
    :param template_name: the name of the template to be rendered
    :param context: the variables that should be available in the
                    context of the template.
    """
    ctx = context_stack.top
    return _render(_lookup(ctx.app).get_template(template_name),
                   context, ctx.app)
