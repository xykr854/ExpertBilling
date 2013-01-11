# coding: utf-8
from django.core.paginator import EmptyPage, PageNotAnInteger
from ebsadmin.models import TableSettings
from ebsadmin.forms import TableColumnsForm 

class RequestConfig(object):
    """
    A configurator that uses request data to setup a table.

    :type  paginate: `dict` or `bool`
    :param paginate: indicates whether to paginate, and if so, what default
                     values to use. If the value evaluates to `False`,
                     pagination will be disabled. A `dict` can be used to
                     specify default values for the call to
                     `~.tables.Table.paginate` (e.g. to define a default
                     *per_page* value).

                     A special *silent* item can be used to enable automatic
                     handling of pagination exceptions using the following
                     algorithm:

                     - If `~django.core.paginator.PageNotAnInteger`` is raised,
                       show the first page.
                     - If `~django.core.paginator.EmptyPage` is raised, show
                       the last page.

    """
    def __init__(self, request, paginate=True):
        self.request = request
        self.paginate = paginate

    def configure(self, table):
        """
        Configure a table using information from the request.
        """
        try:
            ts = TableSettings.objects.get(name=table.__class__.__name__, user=self.request.user)
        except:
            ts = TableSettings.objects.create(name=table.__class__.__name__, value={'fields': table.base_columns.keys()}, user=self.request.user)
            

        for key in table.base_columns:
            column = table.base_columns.get(key)
            if key not in ts.value.get('fields'):
                column.visible = False
        
        table.columns_form = TableColumnsForm(initial={'columns':ts.value.get('fields'), 'table_name': table.__class__.__name__})
        table.columns_form.fields['columns'].choices=[(x, x) for x in table.base_columns]
        order_by = self.request.GET.getlist(table.prefixed_order_by_field)
        if order_by:
            table.order_by = order_by
        if self.paginate:
            if hasattr(self.paginate, "items"):
                kwargs = dict(self.paginate)
            else:
                kwargs = {}
            # extract some options from the request
            for arg in ("page", "per_page"):
                name = getattr(table, u"prefixed_%s_field" % arg)
                try:
                    kwargs[arg] = int(self.request.GET[name])
                except (ValueError, KeyError):
                    pass

            silent = kwargs.pop('silent', True)
            if not silent:
                table.paginate(**kwargs)
            else:
                try:
                    table.paginate(**kwargs)
                except PageNotAnInteger:
                    table.page = table.paginator.page(1)
                except EmptyPage:
                    table.page = table.paginator.page(table.paginator.num_pages)