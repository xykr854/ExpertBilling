# -*- coding: utf-8 -*-

import commands
import os

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from billservice.utils import systemuser_required
from ebscab.lib.decorators import render_to
from object_log.models import LogItem

from ebsadmin.forms import LogViewer


log = LogItem.objects.log_action


@systemuser_required
@render_to('ebsadmin/logview.html')
def logview(request):
    denied = False
    if not (request.user.account.has_perm('billservice.view_log_files')):
        messages.error(request,
                       _(u'У вас нет прав на просмотр лог-файлов'),
                       extra_tags='alert-danger')
        denied = True
    if not (request.user.account.has_perm('billservice.list_log_files')):
        messages.error(request,
                       _(u'У вас нет прав на получение списка лог-файлов'),
                       extra_tags='alert-danger')
        denied = True
    if denied:
        return {
            'status': False
        }

    logfiles = os.listdir('/opt/ebs/data/log/')

    if request.method == 'GET':
        form = LogViewer(request.GET)
        form.fields['log'].choices = [(x, x) for x in logfiles]
        o = ''

        if form.is_valid():
            log_name = form.cleaned_data.get("log")
            count = form.cleaned_data.get("lines", 0)
            all_file = form.cleaned_data.get('full')

            if all_file:
                s, o = commands.getstatusoutput(
                    "cat /opt/ebs/data/log/%s" % log_name.replace('/', ''))
            else:
                s, o = commands.getstatusoutput(
                    "tail -n %s /opt/ebs/data/log/%s" %
                    (count, log_name.replace('/', '')))

            return {
                'form': form,
                'content': unicode(o, errors='ignore')
            }

    form = LogViewer()
    form.fields['log'].choices = [(x, x) for x in logfiles]

    return {
        'form': form
    }
