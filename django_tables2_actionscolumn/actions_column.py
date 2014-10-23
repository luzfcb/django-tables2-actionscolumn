# coding: utf-8
from __future__ import absolute_import, unicode_literals
from django.core.urlresolvers import reverse_lazy
from django.template import Context, Template
from django.template.loader import render_to_string
from django_tables2.columns.base import Column, library

__all__ = [
    'ActionsColumn',
]


@library.register
class ActionsColumn(Column):
    """
    A subclass of `.Column` that renders some template code to use as
    the cell value.

    :type  template_code: `unicode`
    :param template_code: the template code to render
    :type  template_name: `unicode`
    :param template_name: the name of the template to render

    A `~django.template.Template` object is created from the
    *template_code* or *template_name* and rendered with a context containing:

    - *record* -- data record for the current row
    - *value* -- value from `record` that corresponds to the current column
    - *default* -- appropriate default value to use as fallback

    Example:

    .. code-block:: python

        class ExampleTable(tables.Table):
            foo = tables.TemplateColumn('{{ record.bar }}')
            # contents of `myapp/bar_column.html` is `{{ value }}`
            bar = tables.TemplateColumn(template_name='myapp/name2_column.html')

    Both columns will have the same output.

    .. important::

        In order to use template tags or filters that require a
        `~django.template.RequestContext`, the table **must** be rendered via
        :ref:`{% render_table %} <template-tags.render_table>`.
    """
    empty_values = ()

    def __init__(self, template_code=None, template_name=None,
                 update_view_url=None,
                 detail_view_url=None,
                 delete_view_url=None,
                 use_slug=False,
                 orderable=False,
                 **extra):
        super(ActionsColumn, self).__init__(orderable=orderable, **extra)
        self.update_view_url = update_view_url
        self.detail_view_url = detail_view_url
        self.delete_view_url = delete_view_url
        self.use_slug = use_slug
        self.template_code = template_code
        self.template_name = template_name

        self.update_view_url_resolved = None
        self.detail_view_url_resolved = None
        self.delete_view_url_resolved = None


        if not self.template_code and not self.template_name:
            self.template_name = "django_tables2_actionscolumn/action_column.html"

    def render(self, record, table, value, bound_column, **kwargs):
        # If the table is being rendered using `render_table`, it hackily
        # attaches the context to the table as a gift to `TemplateColumn`. If
        # the table is being rendered via `Table.as_html`, this won't exist.

        context = getattr(table, 'context', Context())

        if self.use_slug:
             arg = record.slug
        else:
             arg = record.pk
        #
        # if self.update_view_url:
        #     self.update_view_url_resolved = reverse_lazy(self.update_view_url, kwargs=args)
        #     print("#########################")
        #     #print(self.update_view_url_resolved)
        #     print(type(self.update_view_url_resolved))
        #     print(dir(self.update_view_url_resolved))
        #     print("#########################")
        # if self.detail_view_url:
        #     self.detail_view_url_resolved = reverse_lazy(self.detail_view_url, kwargs=args)
        # if self.delete_view_url:
        #     self.delete_view_url_resolved = reverse_lazy(self.delete_view_url, kwargs=args)

        context.update({'default': bound_column.default,
                        'record': record, 'value': value,
                        'arg': arg,
                        'update_view_url_resolved': self.update_view_url,
                        'detail_view_url_resolved': self.detail_view_url,
                        'delete_view_url_resolved': self.delete_view_url,
                        })
        try:
            if self.template_code:
                return Template(self.template_code).render(context)
            else:
                return render_to_string(self.template_name, context)
        finally:
            context.pop()
