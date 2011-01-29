 #-*- coding=UTF-8 -*-
 
#NEWRPC = True
#if NEWRPC:
 
import os, sys
#print os.path.abspath('../../../')
sys.path.append(os.path.abspath('../../'))

from rpc2 import rpc_protocol, client_networking
    
import datetime

CUR_PATH = os.getcwd()
ROLE = 2

from django.conf import settings

import isdlogger
try:
    os.mkdir(settings.WEBCAB_LOG)
except:
    pass
                    
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection
from django.core.cache import cache
from django import template
from django.contrib.auth.decorators import login_required

from lib.http import JsonResponse

from billservice.models import Account, AccountTarif, NetFlowStream, Transaction, Card, TransactionType, TrafficLimit, Tariff, TPChangeRule, AddonService, AddonServiceTarif, AccountAddonService, PeriodicalServiceHistory, AddonServiceTransaction, OneTimeServiceHistory, TrafficTransaction, AccountPrepaysTrafic, PrepaidTraffic 
from billservice.forms import LoginForm, PasswordForm, CardForm, ChangeTariffForm, PromiseForm, StatististicForm
from billservice import authenticate, log_in, log_out
from radius.models import ActiveSession  
from billservice.utility import is_login_user, settlement_period_info
from nas.models import TrafficClass

from lib.decorators import render_to, ajax_request#, login_required

logger = isdlogger.isdlogger('logging', loglevel=settings.LOG_LEVEL, ident='webcab', filename=settings.WEBCAB_LOG)
rpc_protocol.install_logger(logger)
client_networking.install_logger(logger)

def addon_queryset(request, id_begin, field='datetime', field_to=None):
    if field_to == None:
        field_to = field
    addon_query = {}
    form = StatististicForm(request.GET)
    date_id_dict = request.session.get('date_id_dict',{})
    if form.is_valid():
        if form.cleaned_data['date_from']:
            addon_query[field+'__gte'] = form.cleaned_data['date_from']
            date_id_dict[id_begin+'_date_from'] = request.GET.get('date_from','') 
        else:
            if date_id_dict.has_key(id_begin+'_date_from'):
                del(date_id_dict[id_begin+'_date_from'])
        if form.cleaned_data['date_to']:
            from datetime import timedelta
            addon_query[field_to+'__lte'] = form.cleaned_data['date_to'] + timedelta(hours = 23, minutes=59, seconds=59)
            date_id_dict[id_begin+'_date_to'] = request.GET.get('date_to', '')
        else:
            if date_id_dict.has_key(id_begin+'_date_to'):
                del(date_id_dict[id_begin+'_date_to'])
        request.session['date_id_dict'] = date_id_dict 
        request.session.modified = True
    if request.GET.has_key('date_from') or request.GET.has_key('date_to'):
        is_range = True
    else:
        is_range = False
    return is_range, addon_query 


@render_to('registration/login.html')
def login(request):
    error_message = True
    if request.method == 'POST':
        pin = request.POST.get('pin')
        user = request.POST.get('user')
        if pin:
            if user:
                message = None
                try:               
                    authenticator = rpc_protocol.MD5_Authenticator('client', 'AUTH')
                    protocol = rpc_protocol.RPCProtocol(authenticator)
                    connection_server = rpc_protocol.BasicClientConnection(protocol)
                    transport = client_networking.BlockingTcpClient(settings.RPC_ADDRESS, settings.RPC_PORT)
                    transport.connect()
                    connection_server.registerConsumer_(transport)
                    auth_result = connection_server.authenticate(str(settings.RPC_USER), str(settings.RPC_PASSWORD), ROLE)
                    if not auth_result or not connection_server.protocol._check_status():
                        raise Exception('Status = False!')
                except Exception, e:
                    if isinstance(e, client_networking.TCPException):
                        error_message = u"Отказано в авторизации."
                    else:
                        error_message  = u"Невозможно подключиться к серверу."
                    
                message_type = connection_server.activate_card(user, pin)
                ok_message = False
                if message_type == 1:
                    message = u'Карточка успешно активирована. <br>  Ваш логин %s <br> ваш пароль %s' % (user, pin)
                    ok_message = True
                if message_type == 2:
                    message = u'Неверно введен логин или пин'
                if message_type == 3:
                    message = u'Карточка уже была активирована'
            form = LoginForm()
            return {
                    'form':form,
                    'message':message,
                    'ok_message':ok_message,
                    }
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                user = Account.objects.get(username=form.cleaned_data['username'])
                if not user.allow_webcab:
                    form = LoginForm()
                    error_message = u'У вас нет прав на вход в веб-кабинет'
                    return {
                            'error_message':error_message,
                            'form':form,
                            } 
                if user.password == form.cleaned_data['password']:
                    user = authenticate(username=user.username, password=form.cleaned_data['password'])
                    log_in(request, user)
                    if not cache.get(user.id):
                        cache.set(user.id, {'count':0,'last_date':datetime.datetime.now(),'blocked':False,}, 86400*365)
                    else:
                        cache_user = cache.get(user.id)
                        if cache_user['blocked']:
                            cache.set(user.id, {'count':cache_user['count'],'last_date':cache_user['last_date'],'blocked':cache_user['blocked'],}, 86400*365)
                        else:
                            cache.set(user.id, {'count':cache_user['count'],'last_date':datetime.datetime.now(),'blocked':cache_user['blocked'],}, 86400*365)    
                    tariff = user.get_account_tariff()
                    if tariff.allow_express_pay:
                        request.session['express_pay']=True
                    request.session.modified = True
                    return HttpResponseRedirect('/')
                else:
                    form = LoginForm(initial={'username': form.cleaned_data['username']})
                    error_message = u'Проверьте введенные данные'
                    return {
                            'error_message':error_message,
                            'form':form,
                            }
            except :
                form = LoginForm(initial={'username': form.cleaned_data['username']})
                error_message = u'Проверьте введенные данные'
                return {
                        'error_message':error_message,
                        'form':form,
                        }
        else:
            form = LoginForm(initial={'username': request.POST.get('username', None)})
            error_message = u'Проверьте введенные данные'
            return {
                    'error_message':error_message,
                    'form':form,
                    }
    else:
        form = LoginForm()
        return {
                'form':form,
               }  
               
def login_out(request):
    log_out(request)
    return HttpResponseRedirect('/')


@render_to('accounts/index.html')
@login_required
def index(request):
    user = request.user
    tariff_id, tariff_name = user.get_account_tariff_info()
    date = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    tariffs = AccountTarif.objects.filter(account=user, datetime__lt=date).order_by('-datetime')
    if len(tariffs) == 0 or len(tariffs) == 1:
        tariff_flag = False
    else:
        tariff_flag = True 
    try:
        ballance = user.ballance - user.credit
        ballance = u'%.2f' % user.ballance
    except:
        ballance = 0 
    traffic = TrafficLimit.objects.filter(tarif=tariff_id)      
    #account_tariff_id =  AccountTarif.objects.filter(account = user, datetime__lt=datetime.datetime.now()).order_by('id')[:1]
    account_tariff = AccountTarif.objects.filter(account=user, datetime__lte=datetime.datetime.now()).order_by('-datetime')[0]
    account_prepays_trafic = AccountPrepaysTrafic.objects.filter(account_tarif=account_tariff)
    prepaidtraffic = PrepaidTraffic.objects.filter(id__in=[ i.prepaid_traffic.id for i in account_prepays_trafic])
    try:
        next_tariff = AccountTarif.objects.filter(account=user, datetime__gte=datetime.datetime.now()).order_by('-datetime')[0]
    except:
        next_tariff = None
    return {
            'account_tariff':account_tariff,
            'ballance':ballance,
            'tariff':tariff_name,
            'tariffs':tariffs,
            #'status': bool(user.blocked),
            'tariff_flag':tariff_flag,
            'trafficlimit':traffic,
            'prepaidtraffic':prepaidtraffic,
            'active_class':'user-img',
            'next_tariff':next_tariff,
            }

@render_to('accounts/netflowstream_info.html')
@login_required
def netflowstream_info(request):
    from lib.paginator import SimplePaginator
    paginator = SimplePaginator(request, NetFlowStream.objects.filter(account=request.user).order_by('-date_start'), 500, 'page')
    return {
            'net_flow_streams':paginator.get_page_items(),
            'paginator': paginator,
            }
    

@render_to('accounts/get_promise.html')
@login_required
def get_promise(request):
    if settings.ALLOW_PROMISE==False:
        return HttpResponseRedirect('/')
    user = request.user
    LEFT_PROMISE_DATE = datetime.datetime.now()+datetime.timedelta(days = settings.LEFT_PROMISE_DAYS)
    if Transaction.objects.filter(account=user, promise=True, promise_expired=False).count() >= 1:
        last_promises = Transaction.objects.filter(account=user, promise=True).order_by('-created')[0:10]
        error_message = u"У вас есть незакрытые обещанные платежи"
        return {'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': True, 'last_promises': last_promises, 'active_class':'promise-img',}        
    if request.method == 'POST':
        rf = PromiseForm(request.POST)
        if not rf.is_valid():
            last_promises = Transaction.objects.filter(account=user, promise=True).order_by('-created')[0:10]
            error_message = u"Проверьте введённые в поля данные"
            return {'MAX_PROMISE_SUM': settings.MAX_PROMISE_SUM, 'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': False,  'last_promises': last_promises, 'active_class':'promise-img',}
        sum=rf.cleaned_data.get("sum", 0)
        if sum>settings.MAX_PROMISE_SUM:
            last_promises = Transaction.objects.filter(account=user, promise=True).order_by('-created')[0:10]
            error_message = u"Вы превысили максимальный размер обещанного платежа"
            return {'MAX_PROMISE_SUM': settings.MAX_PROMISE_SUM,'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': False,  'last_promises': last_promises, 'active_class':'promise-img',}
        if sum<=0:
            last_promises = Transaction.objects.filter(account=user, promise=True).order_by('-created')[0:10]
            error_message = u"Сумма обещанного платежа должна быть положительной"
            return {'MAX_PROMISE_SUM': settings.MAX_PROMISE_SUM,'error_message': error_message, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'disable_promise': False,  'last_promises': last_promises, 'active_class':'promise-img',}
        cursor = connection.cursor()
        cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, type_id, approved, tarif_id, summ, created, promise, end_promise, promise_expired) 
                          VALUES(%s, 'Обещанный платёж', 'MANUAL_TRANSACTION', True, get_tarif(%s), %s, now(), True, '%s', False)""" % (user.id, user.id, sum*(-1), LEFT_PROMISE_DATE))
        cursor.connection.commit()
        
        
        last_promises = Transaction.objects.filter(account=user, promise=True).order_by('-created')[0:10]
        
        return {'error_message': u'Обещанный платёж выполнен успешно. Обращаем ваше внимание на то, что повторно воспользоваться услугой обещанного платежа вы сможете после погашения суммы платежа или истечения даты созданного платежа.', 'disable_promise': True, 'last_promises': last_promises, 'active_class':'promise-img',}
    else:
        last_promises = Transaction.objects.filter(account=user, promise=True).order_by('-created')[0:10]
        return {'MAX_PROMISE_SUM': settings.MAX_PROMISE_SUM, 'last_promises': last_promises, 'disable_promise': False, 'LEFT_PROMISE_DATE': LEFT_PROMISE_DATE, 'active_class':'promise-img',}        

    
@render_to('accounts/transaction.html')
@login_required
def transaction(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'transactions', 'created')
    qs = Transaction.objects.filter(account=request.user, **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    transactions = paginator.get_page_items()
    if is_range:
        for trnsaction in qs:
            summ += trnsaction.summ
        for transactio in transactions:
            summ_on_page += trnsaction.summ 
    summ = summ*-1
    summ_on_page = summ_on_page*-1
    rec_count = len(transactions)+1 
    return {
            'transactions':transactions,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }
    
@render_to('accounts/vpn_session.html')
@login_required
def vpn_session(request):
    from lib.paginator import SimplePaginator
    user = request.user
    is_range, addon_query = addon_queryset(request, 'active_session', 'date_start', 'date_end')
    qs = ActiveSession.objects.filter(account=user, **addon_query).order_by('-date_start')
    paginator = SimplePaginator(request, qs, 50, 'page')
    bytes_in = 0
    bytes_out = 0
    bytes_all = 0
    bytes_in_on_page = 0
    bytes_out_on_page = 0
    bytes_all_on_page = 0
    sessions = paginator.get_page_items()
    if is_range:
        for session in qs:
            if session.bytes_in:
                bytes_in += session.bytes_in
            if session.bytes_out:
                bytes_out += session.bytes_out
        for session in sessions:
            if session.bytes_in:
                bytes_in_on_page += session.bytes_in
            if session.bytes_out:
                bytes_out_on_page += session.bytes_out
    bytes_all_on_page = bytes_in_on_page + bytes_out_on_page
    bytes_all = bytes_in + bytes_out
    rec_count = len(sessions)+1  
    return {
            'sessions':paginator.get_page_items(),
            'paginator': paginator,
            'user': user,
            'rec_count':rec_count,
            'bytes_in':bytes_in,
            'bytes_out':bytes_out,
            'bytes_all':bytes_in,
            'bytes_in_on_page':bytes_in_on_page,
            'bytes_out_on_page':bytes_out_on_page,
            'bytes_all_on_page':bytes_in_on_page,
            'is_range':is_range,
            'active_class':'statistic-img',
            }
    

@render_to('accounts/services_info.html')
@login_required    
def services_info(request):
    from lib.paginator import SimplePaginator
    user = request.user  
    is_range, addon_query = addon_queryset(request, 'services', 'activated')
    qs = AccountAddonService.objects.filter(account=user, **addon_query).order_by('-activated')
    paginator = SimplePaginator(request, qs, 50, 'page')
    summ = 0
    summ_on_page = 0
    services = paginator.get_page_items()
    if is_range:
        for service in qs:
            service_summ = 0
            for transaction in AddonServiceTransaction.objects.filter(accountaddonservice=service):
                service_summ += transaction.summ 
            summ += service_summ
        for service in services:
            service_summ = 0
            for transaction in AddonServiceTransaction.objects.filter(accountaddonservice=service):
                service_summ += transaction.summ 
            summ_on_page += service_summ
    services = paginator.get_page_items()
    rec_count = len(services)+1
    return {
            'services':services,
            'paginator': paginator,
            'user': user,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }
    
    
@render_to('accounts/change_password.html')
@login_required
def password_form(request):
    return {
            'form':PasswordForm()
            }

@ajax_request
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            try:
                user = request.user
                if user.password == form.cleaned_data['old_password'] and form.cleaned_data['new_password']==form.cleaned_data['repeat_password']:
                    user.password = form.cleaned_data['new_password']
                    user.save()
                    return {
                            'error_message': u'Пароль успешно изменен',
                            'ok':'ok',
                            }
                else:
                    return {
                            'error_message': u'Проверьте пароль',
                            }
            except Exception, e:
                return {
                        'error_message': u'Возникла ошибка. Обратитесь к администратору.',
                        }
        else:
            return {
                    'error_message': u'Проверьте введенные данные',
                    }
    else:
        return {
                'error_message': u'Не предвиденная ошибка',
                }



@ajax_request
@render_to('accounts/change_tariff.html')
@login_required
def change_tariff_form(request):
    from datetime import datetime, date 
    user = request.user
    account_tariff_id =  AccountTarif.objects.filter(account = user, datetime__lt=datetime.now()).order_by('-datetime')[:1]
    account_tariff = account_tariff_id[0]
    tariffs = TPChangeRule.objects.filter(ballance_min__lte=(user.ballance+user.credit), from_tariff = account_tariff.tarif)
    form = ChangeTariffForm(user, account_tariff)
    return {
            'form': form,
            'tariff_objects':tariffs,
            'user':user,
            'tariff':account_tariff,
            #'time':time,
            }


@ajax_request
@login_required
def change_tariff(request):
    """
        settlement_period_info
        1 - дата начала действия тарифа
        
    """
    from datetime import datetime
    if request.method == 'POST':
        rule_id = request.POST.get('id_tariff_id', None)
        if rule_id != None:
            user = request.user       
            account_tariff_id = AccountTarif.objects.filter(account = user, datetime__lt=datetime.now()).order_by('-datetime')[:1]
            account_tariff = account_tariff_id[0]
            from datetime import datetime
            rules_id =[x.id for x in TPChangeRule.objects.filter(ballance_min__lte=(user.ballance+user.credit))]
            rule = TPChangeRule.objects.get(id=rule_id)
            data_start_period = datetime.now()
            data_start_active = False
            if rule.settlement_period_id:
                td = settlement_period_info(account_tariff.datetime, rule.settlement_period.length_in, rule.settlement_period.length)
                delta = (datetime.now() - account_tariff.datetime).seconds+(datetime.now() - account_tariff.datetime).days*86400 - td[2]
                if delta < 0:
                    return {
                            'error_message':u'Вы не можете перейти на выбранный тариф. Для перехода вам необходимо отработать на старом тарифе ещё не менее %s дней' % (delta/86400*(-1), ),
                            }
            if rule.on_next_sp:
                sp = user.get_account_tarif().settlement_period
                if sp:
                    if sp.autostart:
                        start = account_tariff.datetime
                    else:
                        start = sp.time_start
                    td = settlement_period_info(start, sp.length_in, sp.length)
                    data_start_period = td[1]
                    data_start_active = True
            if not rule.id in rules_id:
                return {
                        'error_message':u'Вы не можете перейти на выбранный тариф',
                        }
            tariff = AccountTarif.objects.create(
                                                    account = user,
                                                    tarif = rule.to_tariff,
                                                    datetime = data_start_period,  
                                                )
            for service in AccountAddonService.objects.filter(account=user, deactivated__isnull=True):
                service.deactivated = datetime.now()
                service.save() 
            if rule.cost:
                cursor = connection.cursor()

                cursor.execute(u"""INSERT INTO billservice_transaction(account_id, bill, type_id, approved, tarif_id, summ, created, promise) 
                                  VALUES(%s, 'Списание средств за переход на тарифный план %s', 'TP_CHANGE', True, get_tarif(%s), %s, now(), False)""" % (user.id, tariff.tarif.name, user.id, rule.cost))
                cursor.connection.commit()
            if data_start_active:
                ok_str = u'Вы успешно сменили тариф, тарифный план будет изменён в следующем расчётном периоде c %s.<br> За переход на данный тарифный план с пользователя будет взыскано %s средств.' %(td[1], rule.cost)
                return {
                         'ok_message':ok_str,   
                        }
            else:
                return {
                        'ok_message':u'Вы успешно сменили тариф. <br> За переход на данный тарифный план с пользователя будет взыскано %s средств.' %rule.cost,
                        }
        else:
            return {
                    'error_message':u'Системная ошибка.',
                    }
    else:
        return {
                'error_message':u'Попытка взлома',
                }


@render_to('accounts/card_form.html')
@login_required
def card_form(request):
    return {
            'form':CardForm()
            }


@ajax_request
@login_required
def card_acvation(request):
    if not request.session.has_key('express_pay'):
        return {
                'error_message': u'Вам не доступна услуга активации карт экспресс оплаты!',
               }
    user = request.user
    if not user.allow_expresscards:
        return {
                'error_message': u'Вам не доступна услуга активации карт экспресс оплаты!',
                }
    if not cache.get(user.id):
        return {
                'redirect':'/login/',
               }
        #HttpResponseRedirect('/')
    cache_user = cache.get(user.id)
    if int(cache_user['count']) > settings.ACTIVATION_COUNT and not bool(cache_user['blocked']):
        cache.delete(user.id)
        cache.set(user.id, {'count':int(cache_user['count']),'last_date':cache_user['last_date'],'blocked':True,}, 86400*365)
    if int(cache_user['count']) > settings.ACTIVATION_COUNT and bool(cache_user['blocked']):
        time = datetime.datetime.now() - cache_user['last_date']
        if time.seconds > settings.BLOCKED_TIME:
            cache.delete(user.id)
            cache.set(user.id, {'count':0,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
        else:
            return {
                    'redirect':'/',
                   }   
    if request.method == 'POST':
        form = CardForm(request.POST)
        error_message = ''
        if form.is_valid():
            try:
                authenticator = rpc_protocol.MD5_Authenticator('client', 'AUTH')
                protocol = rpc_protocol.RPCProtocol(authenticator)
                connection_server = rpc_protocol.BasicClientConnection(protocol)
                transport = client_networking.BlockingTcpClient(settings.RPC_ADDRESS, settings.RPC_PORT)
                transport.connect()
                connection_server.registerConsumer_(transport)
                auth_result = connection_server.authenticate(str(settings.RPC_USER), str(settings.RPC_PASSWORD), ROLE)
                if not auth_result or not connection_server.protocol._check_status():
                    raise Exception('Status = False!')
                res = connection_server.activate_pay_card(user.id, form.cleaned_data['series'], form.cleaned_data['card_id'], form.cleaned_data['pin'])
                #print "res=", res
                if res == 'CARD_NOT_FOUND':
                    error_message = u'Ошибка активации. Карта не найдена.'
                elif res == 'CARD_NOT_SOLD':
                    error_message = u'Ошибка активации. Карта не была продана.'
                elif res == 'CARD_ALREADY_ACTIVATED':
                    error_message = u'Ошибка активации. Карта была активирована раньше.'
                elif res == 'CARD_EXPIRED':
                    error_message = u'Ошибка активации. Срок действия карты истёк.'
                elif res == 'CARD_ACTIVATED':
                    error_message = u'Карта успешно активирована.'
                elif res == 'CARD_ACTIVATION_ERROR':
                    error_message = u'Ошибка активации карты.'
            except Exception, e: 
                print e
            #if int(cache_user['count']) <= settings.ACTIVATION_COUNT:
            #    cache.delete(user.id)
            #    count = int(int(cache_user['count']))
            #    cache.set(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,}, 86400*365)
            #form = CardForm(request.POST)
            return {
                    'error_message':error_message,
                    #'form': form,
                    }
        else:
            #count = int(cache_user['count'])
            #if int(cache_user['count']) < settings.ACTIVATION_COUNT+1:
            #    cache.delete(user.id)
            #    cache.add(user.id, {'count':count+1,'last_date':cache_user['last_date'],'blocked':False,})
            return {
                    'error_message': u"Проверьте заполнение формы",
                    #'form': form,
                    }            
    else:
        #form = CardForm()
        return {
                'error_message': u"Ошибка активации карточки",
                #'form':form,
                }

@render_to('accounts/account_prepays_traffic.html')
@login_required
def account_prepays_traffic(request):
    user = request.user
    try:
        from billservice.models import AccountPrepaysTrafic, PrepaidTraffic
        account_tariff = AccountTarif.objects.get(account=user, datetime__lt=datetime.datetime.now())[:1]
        account_prepays_trafic = AccountPrepaysTrafic.objects.filter(account_tarif=account_tariff)
        prepaidtraffic = PrepaidTraffic.objects.filter(id__in=[ i.prepaid_traffic.id for i in account_prepays_trafic])
    except:
        prepaidtraffic = None
        account_tariff = None  
    return {
            'prepaidtraffic':prepaidtraffic,
            'account_tariff':account_tariff,
            }    
    
def client(request):
    user = request.user
    # CONNECTION TO RCP SERVER
    try:
        authenticator = rpc_protocol.MD5_Authenticator('client', 'AUTH')
        protocol = rpc_protocol.RPCProtocol(authenticator)
        connection_server = rpc_protocol.BasicClientConnection(protocol)
        transport = client_networking.BlockingTcpClient(settings.RPC_ADDRESS, settings.RPC_PORT)
        transport.connect()
        connection_server.registerConsumer_(transport)
        auth_result = connection_server.authenticate(str(settings.RPC_USER), str(settings.RPC_PASSWORD), ROLE)
        if not auth_result or not connection_server.protocol._check_status():
            raise Exception('Status = False!')
    except Exception, e:
        if isinstance(e, client_networking.TCPException):
            error_message = u"Отказано в авторизации."
        else:
            error_message  = u"Невозможно подключиться к серверу."
    # create image
    from django.http import HttpResponse
    t1 = datetime.timedelta(days = 30)
    a1 = datetime.datetime.now() - t1
    a2 = datetime.datetime.now()
    cargs = ('gstat_multi', a1, a2)
    ckwargs = {'return':{}, 'options':{'autoticks':False, 'antialias':True}, 'dcname': 'nfs_web', 'speed':True, 'by_col':'classes', 'users':[user.id], 'classes':[i.id for i in TrafficClass.objects.all()]}
    imgs = connection_server.makeChart(*cargs, **ckwargs)
    response = HttpResponse(imgs, content_type='image/png')
    return response
            

@render_to('accounts/traffic_limit.html') 
@login_required       
def traffic_limit(request):
    user = request.user
    tariff = user.get_account_tariff()
    traffic = TrafficLimit.objects.filter(tarif=tariff) 
    return {
            'trafficlimit':traffic,
            'user':user,
            } 
            
            
@render_to('accounts/statistics.html')
@login_required
def statistics(request):
    user = request.user
    transaction = Transaction.objects.filter(account=user).order_by('-created')[:8]
    active_session = ActiveSession.objects.filter(account=user).order_by('-date_start')[:8]
    periodical_service_history = PeriodicalServiceHistory.objects.filter(account=user).order_by('-datetime')[:8]
    addon_service_transaction = AddonServiceTransaction.objects.filter(account=user).order_by('-created')[:8]
    one_time_history = OneTimeServiceHistory.objects.filter(account=user).order_by('-datetime')[:8]
    traffic_transaction = TrafficTransaction.objects.filter(account=user).order_by('-datetime')[:8]
    if request.session.has_key('date_id_dict'):
        date_id_dict = request.session['date_id_dict']
    else:
        date_id_dict = {}
    return {
            #'net_flow_stream':net_flow_streams,
            'transactions':transaction,
            'active_session':active_session,
            #'services':services,
            'periodical_service_history':periodical_service_history,
            'addon_service_transaction':addon_service_transaction,
            'one_time_history':one_time_history,
            'traffic_transaction':traffic_transaction,
            'form':StatististicForm(),
            'date_id_dict':date_id_dict,
            'active_class':'statistic-img',
            }


@render_to('accounts/addonservice.html')
@login_required
def addon_service(request):
    user = request.user
    #account_tariff_id =  AccountTarif.objects.filter(account = user, datetime__lt=datetime.datetime.now()).order_by('id')[:1]
    #account_tariff = account_tariff_id[0] 
    services = AddonServiceTarif.objects.filter(tarif=user.get_account_tariff())
    user_services = AccountAddonService.objects.filter(account=user, deactivated__isnull=True)
    accountservices = []
    for uservice in user_services:
        if uservice.service.wyte_period_id:
            delta = settlement_period_info(uservice.activated, uservice.service.wyte_period.length_in, uservice.service.wyte_period.length)[2]
            if uservice.activated + datetime.timedelta(seconds = delta)>datetime.datetime.now():
                uservice.wyte = True
                uservice.end_wyte_date = uservice.activated + datetime.timedelta(seconds = delta)
            else:
                uservice.wyte = False
        elif uservice.service.wyte_cost:
            uservice.wyte = True
        else:
            uservice.wyte = False
        accountservices.append(uservice)  
        
    user_services_id = [x.service.id for x in accountservices if not x.deactivated]
    services = services.exclude(service__id__in=user_services_id).order_by("service__name")
    return_dict = {
                   'services':services,
                   'user_services':user_services,
                   'user':user,
                   'active_class':'services-img',
                   }
    if request.session.has_key('service_message'):
        return_dict['service_message'] = request.session['service_message']
        del(request.session['service_message']) 
    return return_dict 
    
@login_required
def service_action(request, action, id):
    """
    в случее set id являеться идентификатором добавляемой услуги
    в случее del id являеться идентификатором accountaddon_service 
    """
    user = request.user
    
    try:
        authenticator = rpc_protocol.MD5_Authenticator('client', 'AUTH')
        protocol = rpc_protocol.RPCProtocol(authenticator)
        connection_server = rpc_protocol.BasicClientConnection(protocol)
        transport = client_networking.BlockingTcpClient(settings.RPC_ADDRESS, settings.RPC_PORT)
        transport.connect()
        connection_server.registerConsumer_(transport)
        auth_result = connection_server.authenticate(str(settings.RPC_USER), str(settings.RPC_PASSWORD), ROLE)
        if not auth_result or not connection_server.protocol._check_status():
            raise Exception('Status = False!')
        #connection_server.test()
    except Exception, e:
        if isinstance(e, client_networking.TCPException):
            request.session['service_message'] = u"Ошибка при подключении к серверу"
            return HttpResponseRedirect('/services/')
        else:
            request.session['service_message']  = u"Нет связи с сервером. Обратитесь в службу поддержки"
            return HttpResponseRedirect('/services/')
        
    if action == u'set':
        try:
            account_addon_service = AddonService.objects.get(id=id)
        except:
            request.session['service_message'] = u'Вы не можете подключить данную услугу'
            return HttpResponseRedirect('/services/')
        result = connection_server.add_addonservice(user.id, id) 
        if result == True:
            request.session['service_message'] = u'Услуга подключена'
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            request.session['service_message'] = u'Указанный пользователь не найден'
            return HttpResponseRedirect('/services/') 
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = u'Указанныя подключаемая услуга не найдена'  
            return HttpResponseRedirect('/services/')   
        elif result == 'NOT_IN_PERIOD':
            request.session['service_message'] = u'Активация выбранной услуги в данный момент не доступна'  
            return HttpResponseRedirect('/services/') 
        elif result == 'ALERADY_HAVE_SPEED_SERVICE':
            request.session['service_message'] = u'У вас уже подключенны изменяющие скорость услуги'  
            return HttpResponseRedirect('/services/')  
        elif result == 'ACCOUNT_BLOCKED':
            request.session['service_message'] = u'Услуга не может быть подключена. Проверьте Ваш баланс или обратитесь в службу поддержки'  
            return HttpResponseRedirect('/services/') 
        elif result == 'ADDONSERVICE_TARIF_DOES_NOT_ALLOWED':
            request.session['service_message'] = u'На вашем тарифном плане активация выбранной услуги невозможна'  
            return HttpResponseRedirect('/services/')     
        elif result == 'TOO_MUCH_ACTIVATIONS':
            request.session['service_message'] = u'Превышенно допустимое количество активаций. Обратитесь в службу поддержки'  
            return HttpResponseRedirect('/services/') 
        elif result == 'SERVICE_ARE_ALREADY_ACTIVATED':
            request.session['service_message'] = u'Указанная услуга уже подключена и не может быть активирована дважды.'  
            return HttpResponseRedirect('/services/') 
        else:
            request.session['service_message'] = u'Услугу не возможно подключить'
            return HttpResponseRedirect('/services/')
    elif action == u'del':
        result = connection_server.del_addonservice(user.id, id)
        if result == True:
            request.session['service_message'] = u'Услуга отключена'
            return HttpResponseRedirect('/services/')
        elif result == 'ACCOUNT_DOES_NOT_EXIST':
            request.session['service_message'] = u'Указанный пользователь не найден'
            return HttpResponseRedirect('/services/') 
        elif result == 'ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = u'Указанныя подключаемая услуга не найдена'  
            return HttpResponseRedirect('/services/')   
        elif result == 'ACCOUNT_ADDON_SERVICE_DOES_NOT_EXIST':
            request.session['service_message'] = u'Вы не можите отключить выбранную услугу'  
            return HttpResponseRedirect('/services/') 
        elif result == 'NO_CANCEL_SUBSCRIPTION':
            request.session['service_message'] = u'Даннная услуга не может быть отключена. Обратитесь в службу поддержки'  
            return HttpResponseRedirect('/services/')  
        else:
            request.session['service_message'] = u'Услугу не возможно отключить'
            return HttpResponseRedirect('/services/')
    else:
        request.session['service_message'] = u'Невозможно совершить действие'
        return HttpResponseRedirect('/services/')
          
@render_to('accounts/periodical_service_history.html')
@login_required
def periodical_service_history(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'periodical_service_history')
    qs = PeriodicalServiceHistory.objects.filter(account=request.user, **addon_query).order_by('-datetime')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    periodical_service_history = paginator.get_page_items()
    if is_range:
        for periodical_service in qs:
            summ += periodical_service.summ
        for periodical_service in periodical_service_history:
            summ_on_page += periodical_service.summ
    rec_count = len(periodical_service_history) + 1
    return {
            'periodical_service_history':periodical_service_history,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }

@render_to('accounts/addon_service_transaction.html')
@login_required
def addon_service_transaction(request):
    from lib.paginator import SimplePaginator 
    is_range, addon_query = addon_queryset(request, 'addon_service_transaction', 'created')
    qs = AddonServiceTransaction.objects.filter(account=request.user, **addon_query).order_by('-created')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    addon_service_transaction = paginator.get_page_items()
    if is_range:
        for addon_service in qs:
            summ += addon_service.summ
        for addon_service in addon_service_transaction:
            summ_on_page += addon_service.summ
    addon_service_transaction = paginator.get_page_items()
    rec_count = len(addon_service_transaction)+1    
    return {
            'addon_service_transaction':addon_service_transaction,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }
    
@render_to('accounts/traffic_transaction.html')
@login_required
def traffic_transaction(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'traffic_transaction', 'created')
    qs = TrafficTransaction.objects.filter(account=request.user, **addon_query).order_by('-datetime') 
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    traffic_transaction = paginator.get_page_items()
    if is_range:
        for traffic_transaction in qs:
            summ += traffic_transaction.summ
        for traffic_transaction in traffic_transaction:
            summ_on_page += traffic_transaction.summ 
    rec_count = len(traffic_transaction)+1
    return {
            'traffic_transaction':traffic_transaction,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }
    
@render_to('accounts/one_time_history.html')
@login_required
def one_time_history(request):
    from lib.paginator import SimplePaginator
    is_range, addon_query = addon_queryset(request, 'one_time_history')
    qs = OneTimeServiceHistory.objects.filter(account=request.user, **addon_query).order_by('-datetime')
    paginator = SimplePaginator(request, qs, 100, 'page')
    summ = 0
    summ_on_page = 0
    one_time_history = paginator.get_page_items()
    if is_range:
        for one_time in qs:
            summ += one_time.summ 
        for one_time in one_time_history:
            summ_on_page += one_time.summ
    rec_count = len(one_time_history)+1
    return {
            'one_time_history':one_time_history,
            'paginator': paginator,
            'is_range':is_range,
            'summ':summ,
            'summ_on_page':summ_on_page,
            'rec_count':rec_count,
            'active_class':'statistic-img',
            }    

@ajax_request
@login_required
def news_delete(request):
    message = u'Невозможно удалить новость, попробуйте позже'
    if request.method == 'POST':
        from billservice.models import AccountViewedNews
        news_id = request.POST.get('news_id', '')
        try:
            news = AccountViewedNews.objects.get(id = news_id, account = request.user)
        except:
            return {
                    'message':message,
                    }
        news.viewed = True
        news.save()
        return {
                'message':u'Новость успешно удалена',
                }
            

@ajax_request
@login_required
def jsonaccounts(request):
    accounts = Account.objects.all()
    #from django.core import serializers
    #from django.http import HttpResponse
    res=[]
    for acc in accounts:
        res.append({"taskId":acc.id, "username":acc.username, "password":acc.password, "fullname":acc.fullname})
    
    #data = serializers.serialize('json', accounts, fields=('username','password'))
    #return HttpResponse("{data: [{username: 'Image one', password:'12345', fullname:46.5, taskId: '10'},{username: 'Image Two', password:'/GetImage.php?id=2', fullname:'Abra', taskId: '20'}]}", mimetype='application/json')
    return {"data": res}


