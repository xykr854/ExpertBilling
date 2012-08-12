# -*-coding: utf-8 -*-

from ebscab.lib.decorators import render_to, ajax_request
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django_tables2.config import RequestConfig
from object_log.models import LogItem

from ebsadmin.tables import HardwareTypeTable

from billservice.forms import HardwareTypeForm
from billservice.models import HardwareType

log = LogItem.objects.log_action



@login_required
@render_to('ebsadmin/hardwaretype_list.html')
def hardwaretype(request):
    res = HardwareType.objects.all()
    table = HardwareTypeTable(res)
    RequestConfig(request, paginate = False).configure(table)
    return {"table": table} 
    
@login_required
@render_to('ebsadmin/hardwaretype_edit.html')
def hardwaretype_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 

        if id:
            model = HardwareType.objects.get(id=id)
            form = HardwareTypeForm(request.POST, instance=model) 
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.change_hardwaretype')):
                return {'status':False, 'message': u'У вас нет прав на редактирование типов оборудования'}
        else:
            form = HardwareTypeForm(request.POST) 
        if  not (request.user.is_staff==True and request.user.has_perm('billservice.add_hardwaretype')):
            return {'status':False, 'message': u'У вас нет прав на добавление типов оборудования'}


        if form.is_valid():
            model = form.save(commit=False)
            model.save()

            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            return {'form':form,  'status': True} 
        else:

            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")

        if id:
            if  not (request.user.is_staff==True and request.user.has_perm('billservice.hardwaretype_view')):
                return {'status':True}

            item = HardwareType.objects.get(id=id)
            
            form = HardwareTypeForm(instance=item)
        else:
            form = HardwareTypeForm()

    return { 'form':form, 'status': False} 

@ajax_request
@login_required
def hardwaretype_delete(request):
    if  not (request.user.is_staff==True and request.user.has_perm('billservice.delete_hardwaretype')):
        return {'status':False, 'message': u'У вас нет прав на удаление типов оборудования пулов'}
    id = int(request.POST.get('id',0)) or int(request.GET.get('id',0))
    if id:
        try:
            item = HardwareType.objects.get(id=id)
        except Exception, e:
            return {"status": False, "message": u"Указанный тип оборудования не найден %s" % str(e)}
        log('DELETE', request.user, item)
        item.delete()
        return {"status": True}
    else:
        return {"status": False, "message": "HardwareType not found"} 
    