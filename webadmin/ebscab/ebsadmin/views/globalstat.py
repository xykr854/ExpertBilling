# -*- coding: utf-8 -*-

from django.contrib import messages
from django.db.models import Sum, Min, Max
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from billservice.forms import GlobalStatSearchForm
from billservice.utils import systemuser_required
from billservice.models import GlobalStat
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response
from ebscab.lib.decorators import render_to
from object_log.models import LogItem

from ebsadmin.tables import GlobalStatTable


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/globalstat_list.html')
def globalstat(request):
    if not (request.user.account.has_perm('billservice.view_groupstat')):
        messages.error(request,
                       _(u'У вас нет прав на доступ в этот раздел.'),
                       extra_tags='alert-danger')
        return HttpResponseRedirect('/ebsadmin/')

    if request.GET:
        data = request.GET
        form = GlobalStatSearchForm(data)
        if data and form.is_valid():
            accounts = form.cleaned_data.get('accounts')
            groups = form.cleaned_data.get('groups')
            daterange = form.cleaned_data.get('daterange') or []

            start_date, end_date = (form.cleaned_data.get('start_date'),
                                    form.cleaned_data.get('end_date'))
            query = (GlobalStat.objects
                     .all()
                     .select_related()
                     .values('account__username')
                     .annotate(bytes_in=Sum('bytes_in'),
                               bytes_out=Sum('bytes_out'),
                               min=Min('datetime'),
                               max=Max('datetime')))

            query.group_by = ['account__username']

            res = query
            if accounts:
                res = res.filter(account__in=accounts)

            if start_date:
                res = res.filter(datetime__gte=start_date)

            if end_date:
                res = res.filter(datetime__lte=end_date)

            table = GlobalStatTable(res)
            table_to_report = RequestConfig(
                request,
                paginate=(False if request.GET.get('paginate') == 'False'
                          else True))
            table_to_report = table_to_report.configure(table)
            if table_to_report:
                return create_report_http_response(table_to_report, request)

            return {
                "table": table,
                'form': form,
                'resultTab': True
            }

        else:
            return {
                'status': False,
                'form': form
            }
    else:
        form = GlobalStatSearchForm()
        return {
            'form': form
        }
