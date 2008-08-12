#-*-coding=utf-8-*-

import time, datetime, os, sys
from utilites import create_speed_string, change_speed, PoD, get_active_sessions, rosClient, DAE, SSHClient,settlement_period_info, in_period, in_period_info,create_speed_string, ipn_manipulate
import dictionary
from threading import Thread
import threading
from db import delete_transaction, get_default_speed_parameters, get_speed_parameters,transaction, ps_history, get_last_checkout, time_periods_by_tarif_id
import Pyro.core
import mdi.orm.models as models
import settings
import psycopg2
import psycopg2.extras
from types import InstanceType  
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import pickle

from chartprovider.bpplotadapter import bpplotAdapter
from chartprovider.bpcdplot import cdDrawer

#from mdi.helpers import Object

from DBUtils.PooledDB import PooledDB
#from mdi.helpers import Object as Object

pool = PooledDB(
     mincached=1,
     maxcached=60,
     blocking=True,
     creator=psycopg2,
     dsn="dbname='%s' user='%s' host='%s' password='%s'" % (settings.DATABASE_NAME,
                                                            settings.DATABASE_USER,
                                                            settings.DATABASE_HOST,
                                                            settings.DATABASE_PASSWORD)
)



def format_update (x,y):
    print 'y', y, type(y)
    if y!='Null':
        if type(y)==StringType or type(y)==UnicodeType:
            print True
            y=y.replace('\'', '\\\'').replace('"', '\"').replace("\\","\\\\")
            #print 'y', y
        return "%s='%s'" % (x,y)
    else:
        return "%s=%s" % (x,y)

def format_insert(y):
    if y=='Null':
        return y
    elif type(y)==StringType or type(y)==UnicodeType:
        print True
        return y.replace('\'', '\\\'').replace('"', '\"').replace("\\","\\\\")
    else:
        return y

class Object(object):
    def __init__(self, result=[], *args, **kwargs):
        for key in result:
            if result[key]!=None:
                setattr(self, key, result[key])
            else:
                setattr(self, key, 'Null')


        for key in kwargs:
            setattr(self, key, kwargs[key])  
        
        #print dir(self)          
            
         
    def save(self, table):
        
        
        fields=[]
        for field in self.__dict__:
            if type(field)!=InstanceType:
                # and self.__dict__[field]!=None
                fields.append(field)
        try:
            self.__dict__['id']
            sql=u"UPDATE %s SET %s WHERE id=%d;" % (table, " , ".join([format_update(x, unicode(self.__dict__[x])) for x in fields ]), self.__dict__['id'])
        except:
            sql=u"INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (table, ",".join([x for x in fields]), ("%s" % "','".join([format_insert(unicode(self.__dict__[x])) for x in fields ]).replace("'Null'", 'Null')))
        
        return sql
    
    def get(self, table):
        return "SELECT * FROM %s WHERE id=%d" % (table, int(self.id))
    
    def __call__(self):
        return self.id

def comparator(d, s):
    for key in s:
        if s[key]!='' and s[key]!='Null' and s[key]!='None':
           d[key]=s[key] 
    return d
    
class check_vpn_access(Thread):
        def __init__ (self, dict, timeout=30):
            self.dict=dict
            self.timeout=timeout
            Thread.__init__(self)

        def check_period(self, rows):
            for row in rows:
                if in_period(row['time_start'],row['length'],row['repeat_after'])==True:
                    return True
            return False

        def create_speed(self, tarif_id, nas_type):
            defaults = get_default_speed_parameters(self.cur, tarif_id)
            speeds = get_speed_parameters(self.cur, tarif_id)
            for speed in speeds:
                if in_period(speed['time_start'],speed['length'],speed['repeat_after'])==True:
                    defaults = comparator(defaults, speed)
                        
            #print "speed_result=", defaults
            return defaults
        
        def remove_sessions(self):

            self.cur.execute(
                             """
                             SELECT id, name, "type", ipaddress, secret, "login", "password", reset_action FROM nas_nas;
                             """
                             )
            nasses=self.cur.fetchall()
            

            for nas in nasses:
                sessions = get_active_sessions(nas)
                #print sessions
                for session in sessions:
                    #print 'session', session
                    self.cur.execute("""
                                    SELECT account.id, account.vpn_ip_address, account.ipn_ip_address, account.ipn_mac_address, radius.sessionid as  sessionid
                                    FROM radius_activesession as radius 
                                    JOIN billservice_account as account ON radius.account_id=account.id
                                    WHERE account.username='%s'
                                    """ % session['name'])
                    account = self.cur.fetchone()
                    #print "account", account
                    if account is not None:
                        print 'send pod'
                        res = PoD(dict=self.dict,
                            account_id=account['id'], 
                            account_name=str(session['name']), 
                            account_vpn_ip=account['vpn_ip_address'], 
                            account_ipn_ip=account['ipn_ip_address'], 
                            account_mac_address=account['ipn_mac_address'], 
                            access_type=str(session['service']), 
                            nas_ip=nas['ipaddress'], 
                            nas_type=nas['type'], 
                            nas_name=nas['name'], 
                            nas_secret=nas['secret'], 
                            nas_login=nas['login'], 
                            nas_password=nas['password'], 
                            session_id=str(account['sessionid']), 
                            format_string=str(nas['reset_action'])
                            )

                self.cur.execute("""
                UPDATE radius_activesession
                SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='ACK'
                WHERE date_end is Null and nas_id='%s';""" % nas['ipaddress'])
                self.connection.commit()


        def check_access(self):
            """
            Раз в 30 секунд происходит выборка всех пользователей
            OnLine, делается проверка,
            1. не вышли ли они за рамки временного диапазона
            2. Не ушли ли в нулевой балланс
            если срабатывает одно из двух условий-посылаем команду на отключение пользователя
            TO-DO: Переписать! Работает правильно.
            nas_id содержит в себе IP адрес. Сделано для уменьшения выборок в модуле core при старте сессии
            TO-DO: если NAS не поддерживает POD или в парметрах доступа ТП указан IPN - отсылать команды через SSH
            """

            self.connection = pool.connection()
            self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  
            
            self.remove_sessions()

            #time.sleep(10)
            while True:

                #Закрываем подвисшие сессии
                self.cur.execute("UPDATE radius_activesession SET session_time=extract(epoch FROM date_end-date_start), date_end=interrim_update, session_status='NACK' WHERE ((now()-interrim_update>=interval '00:06:00') or (now()-date_start>=interval '00:03:00' and interrim_update is Null)) and date_end is Null;")
                self.connection.commit()
                
                self.cur.execute("""
                SELECT rs.id as id, rs.account_id as account_id, rs.sessionid as session,  rs.speed_string as speed_string, lower(rs.framed_protocol) as access_type,
                nas.name as nas_name, nas.ipaddress as nas_ip, nas.secret as nas_secret, nas.login as nas_login, nas.password as nas_password, nas.type as nas_type,
                account.username as username, (SELECT tarif_id FROM billservice_accounttarif WHERE datetime<now() and account.id=account_id LIMIT 1) as tarif_id, 
                (ballance+credit) as balance, account.disabled_by_limit as disabled_by_limit, account.speed, nas.reset_action as reset_action, nas.vpn_speed_action as speed_action,
                account.vpn_ip_address as vpn_ip_address,  account.ipn_ip_address as ipn_ip_address, account.ipn_mac_address as ipn_mac_address
                FROM radius_activesession as rs
                JOIN nas_nas as nas ON nas.ipaddress=rs.nas_id
                JOIN billservice_account as account ON account.id=rs.account_id
                WHERE rs.date_end is null;
                """)
                
                rows=self.cur.fetchall()
                for row in rows:
                    result=None

                    if row['balance']>0 or self.check_period(time_periods_by_tarif_id(self.cur, row['tarif_id']))==False or row['disabled_by_limit']==True:
                       """
                       Делаем проверку на то, изменилась ли скорость.
                       """
                       speed_parameters=self.create_speed(row['tarif_id'], row['nas_type'])
                       if row['speed']=='':
                           speed=create_speed_string(speed_parameters, coa=True)
                       else:
                           speed=row['speed'] 
                           
                       print "row['speed_string'], row['speed']", row['speed_string'], speed
                       if row['speed_string']!=speed:

                           #coa_result=DAE(dict=self.dict, code=43, nas_secret=str(row['nas_secret']), nas_ip=str(row['nas_ip']), nas_id=str(row['nas_name']), username=str(row['username']), session_id=str(row['session']), login=row['nas_login'], password=row['nas_password'], access_type=row['access_type'], speed_string=speed, coa=False)
                           
                           print "set speed", speed
                           coa_result=change_speed(dict=self.dict, account_id=row['account_id'], 
                                account_name=str(row['username']), 
                                account_vpn_ip=row['vpn_ip_address'], 
                                account_ipn_ip=row['ipn_ip_address'], 
                                account_mac_address=row['ipn_mac_address'], 
                                access_type=str(row['access_type']), 
                                nas_ip=str(row['nas_ip']), 
                                nas_type=row['nas_type'], 
                                nas_name=str(row['nas_name']), 
                                nas_secret=str(row['nas_secret']), 
                                nas_login=str(row['nas_login']), 
                                nas_password=row['nas_password'], 
                                session_id=str(row['session']), 
                                format_string=str(row['speed_action']),
                                speed=speed_parameters)                           
                           
                           
                           print "coa_result=", coa_result
                           
                           if coa_result==True:
                               self.cur.execute(
                                        """
                                        UPDATE radius_activesession
                                        SET speed_string='%s'
                                        WHERE id=%s;
                                        """ % (speed, row['id'])
                                        )
                    else:
                        #result = DAE(dict=self.dict, code=40, nas_secret=row['nas_secret'], nas_ip=nas_id, nas_id=row['nas_name'], username=row['username'], session_id=row['session'],  login=row['nas_login'], password=row['nas_password'])
                        
                        result = PoD(dict=self.dict,
                            account_id=row['account_id'], 
                            account_name=str(row['username']), 
                            account_vpn_ip=row['vpn_ip_address'], 
                            account_ipn_ip=row['ipn_ip_address'], 
                            account_mac_address=row['ipn_mac_address'], 
                            access_type=str(row['access_type']), 
                            nas_ip=row['nas_ip'], 
                            nas_type=row['nas_type'], 
                            nas_name=row['nas_name'], 
                            nas_secret=row['nas_secret'], 
                            nas_login=row['nas_login'], 
                            nas_password=row['nas_password'], 
                            session_id=str(row['session']), 
                            format_string=str(row['reset_action'])
                            )
                        
                    if result==True:
                        disconnect_result=u'ACK'
                    elif result==False:
                        disconnect_result=u'NACK'

                    if result is not None:
                        self.cur.execute(
                        """
                        UPDATE radius_activesession SET session_status=%s WHERE sessionid=%s;
                        """, (disconnect_result, row['session'])
                        )

                self.connection.commit()
                #self.cur.close()

                time.sleep(self.timeout)

        def run(self):
            self.check_access()


class periodical_service_bill(Thread):
    """
    Процесс будет производить снятие денег у клиентов, у которых в ТП
    указан список периодических услуг.
    Нужно учесть что:
    1. Снятие может производиться в начале расчётного периода.
    Т.к. мы не можем производить проверку каждую секунду - нужно держать список снятий
    , чтобы проверять с какого времени мы уже не делали снятий и произвести их.
    2. Снятие может производиться в конце расчётного периода.
    ситуация аналогичная первой

    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        while True:
            connection = pool.connection()
            cur = connection.cursor()
            # Количество снятий в сутки
            transaction_number=24
            n=(24*60*60)/transaction_number

            #выбираем список тарифных планов у которых есть периодические услуги
            cur.execute("SELECT id, settlement_period_id, ps_null_ballance_checkout  FROM billservice_tariff WHERE id in (SELECT tariff_id FROM billservice_tariff_periodical_services)")
            rows=cur.fetchall()
            #print "SELECT TP"
            #перебираем тарифные планы
            for row in rows:
                #print row
                tariff_id=row[0]
                print tariff_id
                print "start PS"
                settlement_period_id=row[1]
                null_ballance_checkout=row[2]
                # Получаем список аккаунтов на ТП
                cur.execute("""
                SELECT a.account_id, a.datetime::timestamp without time zone, (b.ballance+b.credit) as ballance
                FROM billservice_account as b
                JOIN billservice_accounttarif as a ON a.id=(SELECT id FROM billservice_accounttarif WHERE account_id=b.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
                WHERE a.tarif_id=%d and b.suspended=False
                """ % tariff_id)
                accounts=cur.fetchall()
                # Получаем параметры каждой перодической услуги в выбранном ТП
                cur.execute("""
                SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start::timestamp without time zone,
                c.length, c.length_in, c.autostart
                FROM billservice_tariff_periodical_services as p
                JOIN billservice_periodicalservice as b ON p.periodicalservice_id=b.id
		        JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id
                WHERE p.tariff_id=%d
                """ % tariff_id)
                rows_ps=cur.fetchall()
                # По каждой периодической услуге из тарифного плана делаем списания для каждого аккаунта
                for row_ps in rows_ps:
                    ps_id = row_ps[0]
                    ps_name = row_ps[1]
                    ps_cost = row_ps[2]
                    ps_cash_method = row_ps[3]
                    name_sp=row_ps[4]
                    time_start_ps=row_ps[5]
                    length_ps=row_ps[6]
                    length_in_sp=row_ps[7]
                    autostart_sp=row_ps[8]

                    for account in accounts:
                        
                        account_id = account[0]
                        print "account_id for ps", ps_id, account_id
                        account_datetime = account[1]
                        account_ballance = account[2]
                        # Если балланс>0 или разрешено снятие денег при отрицательном баллансе
                        if account_ballance>0 or (null_ballance_checkout==True and account_ballance<=0):
                            #Получаем данные из расчётного периода
                            if autostart_sp==True:
                                time_start_ps=account_datetime
                            # Если в расчётном периоде указана длина в секундах-использовать её, иначе использовать предопределённые константы
                            period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, repeat_after_seconds=length_ps)
                            cur.execute("SELECT datetime::timestamp without time zone FROM billservice_periodicalservicehistory WHERE service_id=%s AND transaction_id=(SELECT id FROM billservice_transaction WHERE tarif_id=%s AND account_id=%s ORDER BY datetime DESC LIMIT 1) ORDER BY datetime DESC LIMIT 1;" % (ps_id, tariff_id, account_id))
                            now=datetime.datetime.now()
                            if ps_cash_method=="GRADUAL":
                                """
                                # Смотрим сколько расчётных периодов закончилось со времени последнего снятия
                                # Если закончился один-снимаем всю сумму, указанную в периодической услуге
                                # Если закончилось более двух-значит в системе был сбой. Делаем последнюю транзакцию
                                # а остальные помечаем неактивными и уведомляем администратора
                                """
                                last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
                                # Здесь нужно проверить сколько раз прошёл расчётный период
                                if last_checkout==None:
                                    last_checkout=account_datetime

                                if (now-last_checkout).seconds>=n:
                                    #Проверяем наступил ли новый период
                                    if now-datetime.timedelta(seconds=n)<=period_start:
                                        # Если начался новый период
                                        # Находим когда начался прошльый период
                                        # Смотрим сколько денег должны были снять за прошлый период и производим корректировку
                                        #period_start, period_end, delta = settlement_period_info(time_start=time_start_ps, repeat_after=length_in_sp, now=now-datetime.timedelta(seconds=n))
                                        pass
                                    # Смотрим сколько раз уже должны были снять деньги
                                    cash_summ=((float(n)*float(transaction_number)*float(ps_cost))/(float(delta)*float(transaction_number)))
                                    lc=now - last_checkout
                                    nums, ost=divmod(lc.seconds,n)
                                    if nums>0:
                                        #Смотрим на какую сумму должны были снять денег и снимаем её
                                        cash_summ=cash_summ*nums
                                    #print "delta", delta
                                    # Делаем проводку со статусом Approved

                                    transaction_id = transaction(cursor=cur,
                                    account=account_id,
                                    approved=True,
                                    type='PS_GRADUAL',
                                    tarif = tariff_id,
                                    summ=cash_summ,
                                    description=u"Проводка по периодической услуге со cнятием суммы в течении периода",
                                    created = now)

                                    ps_history(cursor=cur, ps_id=ps_id, transaction=transaction_id, created=now)

                            if ps_cash_method=="AT_START":
                                """
                                Смотрим когда в последний раз платили по услуге. Если в текущем расчётном периоде
                                не платили-производим снятие.
                                """
                                last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
                                # Здесь нужно проверить сколько раз прошёл расчётный период
                                # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                                # Для последней проводки ставим статус Approved=True
                                # для всех сотальных False
                                # Если последняя проводка меньше или равно дате начала периода-делаем снятие
                                summ=0
                                if last_checkout is None:
                                    first_time=True
                                    last_checkout=now
                                else:
                                    first_time=False
                                
                                if (first_time==True and account_datetime<period_start) or last_checkout<period_start:
                                    if not first_time:
                                        lc=last_checkout-period_start
                                        nums, ost=divmod(lc.seconds, n)
                                        for i in xrange(nums-1):
                                            summ+=ps_cost

                                    transaction_id = transaction(cursor=cur,
                                    account=account_id,
                                    approved=True,
                                    type='PS_AT_START',
                                    tarif = tariff_id,
                                    summ=ps_cost+summ,
                                    description=u"Проводка по периодической услуге со нятием суммы в начале периода",
                                    created = now)
                                    ps_history(cur, ps_id, transaction=transaction_id, created=now)

                            if ps_cash_method=="AT_END":
                               """
                               Смотрим завершился ли хотя бы один расчётный период.
                               Если завершился - считаем сколько уже их завершилось.
                               
                               для остальных со статусом False
                               """
                               last_checkout=get_last_checkout(cursor=cur, ps_id = ps_id, tarif = tariff_id, account = account_id)
                               # Здесь нужно проверить сколько раз прошёл расчётный период

                               # Если с начала текущего периода не было снятий-смотрим сколько их уже не было
                               # Для последней проводки ставим статус Approved=True
                               # для всех сотальных False
                               now=datetime.datetime.now()
                               # Если дата начала периода больше последнего снятия или снятий не было и наступил новый период - делаем проводки
                               # Выражение верно т.к. новая проводка совершится каждый раз только после после перехода
                               #в новый период.
                               summ=0
                               if period_start>last_checkout or (last_checkout==None and now-datetime.timedelta(seconds=n)<=period_start):

                                    lc=last_checkout-period_start
                                    nums, ost=divmod((period_end-last_checkout).seconds, n)
                                    for i in xrange(nums-1):
                                        summ+=ps_cost

                                    transaction_id = transaction(cursor=cur,
                                    account=account_id,
                                    approved=True,
                                    type='PS_AT_END',
                                    tarif = tariff_id,
                                    summ=ps_cost+summ,
                                    description=u"Проводка по периодической услуге со нятием суммы в конце периода",
                                    created = now)
                                    ps_history(cur, ps_id, transaction=transaction_id, created=now)
            connection.commit()
            cur.close()
            connection.close()
            time.sleep(180)

class TimeAccessBill(Thread):
    """
    Услуга применима только для VPN доступа, когда точно известна дата авторизации
    и дата отключения пользователя
    """
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        """
        По каждой записи делаем транзакции для пользователя в соотв с его текущим тарифным планов
        """
        while True:
            connection = pool.connection()
            cur = connection.cursor()
            cur.execute("""
            SELECT rs.account_id, rs.sessionid, rs.session_time, rs.interrim_update::timestamp without time zone, tacc.id, tacc.name, tarif.id, acc_t.id
            FROM radius_session as rs
            JOIN billservice_accounttarif as acc_t ON acc_t.account_id=rs.account_id
            JOIN billservice_tariff as tarif ON tarif.id=acc_t.tarif_id
            JOIN billservice_timeaccessservice as tacc ON tacc.id=tarif.time_access_service_id
            WHERE rs.checkouted_by_time=False and rs.date_start is NUll and acc_t.datetime<rs.interrim_update ORDER BY rs.interrim_update ASC;
            """)
            rows=cur.fetchall()

            for row in rows:

                account_id=row[0]
                session_id = row[1]
                session_time = row[2]
                interrim_update = row[3]
                ps_id=row[4]
                ps_name = row[5]
                tarif_id = row[6]
                accountt_tarif_id = row[7]
                #1. Ищем последнюю запись по которой была произведена оплата
                #2. Получаем данные из услуги "Доступ по времени" из текущего ТП пользователя
                #TODO:2. Проверяем сколько стоил трафик в начале сессии и не было ли смены периода.
                #TODO:2.1 Если была смена периода -посчитать сколько времени прошло до смены и после смены,
                # рассчитав соотв снятия.
                #2.2 Если снятия не было-снять столько, на сколько насидел пользователь
                cur.execute("""
                SELECT session_time FROM radius_session WHERE sessionid='%s' AND checkouted_by_time=True
                ORDER BY interrim_update DESC LIMIT 1
                """ % session_id)
                try:
                    old_time=cur.fetchone()[0]
                except:
                    old_time=0
                total_time=session_time-old_time

                cur.execute(
                            """
                            SELECT id, size FROM billservice_accountprepaystime WHERE account_tarif_id=%s
                            """ % accountt_tarif_id
                            )

                try:
                    prepaid_id, prepaid=cur.fetchone()
                except:
                    prepaid=0
                    prepaid_id=-1
                if prepaid>=0:
                    if prepaid>=total_time:
                        total_time=0
                        prepaid=prepaid-total_time
                    elif total_time>=prepaid:
                        total_time=total_time-prepaid
                        prepaid=0
                    cur.execute("""UPDATE billservice_accountprepaystrafic SET size=%s WHERE id=%s""" % (prepaid, prepaid_id))


                # Получаем список временных периодов и их стоимость у периодической услуги
                cur.execute(
                """
                SELECT tan.time_period_id, tan.cost
                FROM billservice_timeaccessnode as tan
                JOIN billservice_timeperiodnode as tp ON tan.time_period_id=tp.id
                WHERE tan.time_access_service_id=%s
                """ % ps_id
                )
                periods=cur.fetchall()
                for period in periods:
                    period_id=period[0]
                    period_cost=period[1]
                    #получаем данные из периода чтобы проверить попала в него сессия или нет
                    cur.execute(
                    """
                    SELECT tpn.id, tpn.name, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id
                    WHERE tptpn.timeperiod_id=%s
                    """ % period_id
                    )
                    period_nodes_data=cur.fetchall()
                    for period_node in period_nodes_data:
                        period_id=period_node[0]
                        period_name = period_node[1]
                        period_start = period_node[2]
                        period_length = period_node[3]
                        repeat_after = period_node[4]
                        if in_period(time_start=period_start,length=period_length, repeat_after=repeat_after):
                            summ=(float(total_time)/60.000)*period_cost
                            if summ>0:
                                transaction(
                                cursor=cur,
                                type='TIME_ACCESS',
                                account=account_id,
                                approved=True,
                                tarif=tarif_id,
                                summ=summ,
                                description=u"Снятие денег за время по RADIUS сессии %s" % session_id,
                                )
                                #print u"Снятие денег за время %s" % query

                query="""
                UPDATE radius_session
                SET checkouted_by_time=True
                WHERE sessionid='%s'
                AND account_id='%s'
                AND interrim_update='%s'
                """ % (session_id, account_id, interrim_update)
                cur.execute(query)
                connection.commit()
            cur.close()
            connection.close()
            time.sleep(30)


class NetFlowAggregate(Thread):
    """
    TO-DO: Вынести в NetFlow коллектор
    Алгоритм для агрегации трафика:
    Формируем таблицу с агрегированным трафиком

    1. Берём строку из netflowstream_raw
    2. Смотрим есть ли похожая строка в netflowstream за последнюю минуту-полторы и не производилось ли по ней списание.
    2.1 Если есть и списание не производилось-суммируем количество байт
    2.2 Если есть и списание производилось или если нет -пишем новую строку
    3. УДаляем из netflowstream_raw строку или помечаем, что он адолжна быть удалена.

    WHILE TRUE
    timeout(120 seconds)
    произвести агрегирование по новым строкам.
    """

    def __init__(self):
        Thread.__init__(self)

    def check_period(self, rows):
        for row in rows:
            if in_period(row[0],row[1],row[2])==True:
                return True
        return False

    def run(self):
        while True:
            print 'next aggregation cycle'
            connection = pool.connection()
            cur = connection.cursor()
            cur.execute(
            """
            SELECT nf.id, 
            nf.nas_id, nf.date_start, nf.traffic_class_id, nf.direction, nf.src_addr, 
            nf.dst_addr, nf.octets, nf.src_port, nf.dst_port, nf.protocol, ba.id,
            tariff.traffic_transmit_service_id, tariff.id, trafficclass.store
            FROM billservice_rawnetflowstream as nf
            LEFT JOIN billservice_account as ba ON ba.vpn_ip_address=nf.src_addr OR ba.vpn_ip_address=nf.dst_addr OR ba.ipn_ip_address=nf.src_addr OR ba.ipn_ip_address=nf.dst_addr
            JOIN billservice_accounttarif as account_tariff ON account_tariff.id=(SELECT id FROM billservice_accounttarif as at WHERE at.account_id=ba.id and at.datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_tariff as tariff ON tariff.id=account_tariff.tarif_id
            JOIN nas_trafficclass as trafficclass ON trafficclass.id=nf.traffic_class_id
            WHERE nf.fetched=False;
            """
            )
            raw_streams=cur.fetchall()
            
            """
            Берём строку, ищем пользователя, у которого адрес совпадает или с dst или с src.
            Если сервер доступа в тарифе подразумевает обсчёт сессий через NetFlow помечаем строку "для обсчёта"
            """
            for stream in raw_streams:
                nf_id, nas_id, date_start, traffic_class_id, direction, src_addr, dst_addr, octets, src_port, dst_port, protocol, account_id,\
                traffic_transmit_service, tarif_id, store = stream

                tarif_mode=False
                #print nf_id

                if traffic_transmit_service:

                #Выбираем временные интервалы из услуги по трафику
                    cur.execute(
                    """
                    SELECT tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
                    FROM billservice_timeperiodnode as tpn
                    JOIN billservice_timeperiod_time_period_nodes as timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                    JOIN billservice_traffictransmitnodes_time_nodes as ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                    JOIN billservice_traffictransmitnodes as ttns ON ttns.id=ttntp.traffictransmitnodes_id
                    WHERE ttns.traffic_transmit_service_id=%s
                    """ % traffic_transmit_service
                    )

                    periods=cur.fetchall()
                    #Нужно ли списывать деньги за этот трафик
                    tarif_mode=self.check_period(periods)

                if account_id is not None:
                    # Если пользователь
                    cur.execute(
                    """
                    SELECT id
                    FROM billservice_netflowstream
                    WHERE nas_id='%s' and account_id=%s and
                    tarif_id=%s and
                    '%s' - date_start < interval '00:05:00' and
                    direction='%s' and
                    src_addr='%s' and traffic_class_id='%s' and
                    dst_addr='%s' and
                    src_port='%s' and
                    dst_port='%s' and
                    protocol='%s' and
                    checkouted=False and
                    for_checkout='%s' ORDER BY id DESC LIMIT 1
                    """ % (nas_id, account_id, tarif_id, date_start, direction, src_addr, traffic_class_id, dst_addr, src_port,dst_port, protocol, tarif_mode)
                    )
                    row_for_update=cur.fetchone()
                    if row_for_update:
                        print 'updating'
                        cur.execute(
                        """
                        UPDATE billservice_netflowstream SET octets=octets+%s WHERE id=%s
                        """ % (octets, nf_id)
                        )
                    else:
                        print 'inserting'
                        cur.execute(
                        """
                        INSERT INTO billservice_netflowstream(
                        nas_id, account_id, tarif_id, direction,date_start, src_addr, traffic_class_id,
                        dst_addr, octets, src_port, dst_port, protocol, checkouted, for_checkout)
                        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s',
                        '%s', '%s', '%s', '%s', '%s', '%s', '%s');
                        """ % (nas_id, account_id, tarif_id, direction, date_start,src_addr, traffic_class_id, dst_addr, octets,src_port, dst_port, protocol, False, tarif_mode)
                        )



                if store:
                    cur.execute(
                    """
                    UPDATE billservice_rawnetflowstream SET fetched=True WHERE id=%s
                    """ % nf_id
                    )
                else:
                    cur.execute(
                    """
                    DELETE FROM billservice_rawnetflowstream WHERE id=%s;
                    """ % nf_id
                    )
                    
                connection.commit()
            cur.close()
            connection.close()
            time.sleep(60)


class NetFlowBill(Thread):
    """
    WHILE TRUE
    берём строки с for_checkout=True и checkouted=False и по каждой строке производим начисления
    timeout(120 seconds)

    """
    class Picker(object):
        def __init__(self):
            self.data={}
            
            
        def add_summ(self, account, tarif, summ):
            if self.data.has_key(account):
                self.data[account]['summ']+=summ
            else:
                self.data[account]={'tarif':tarif, 'summ':summ}
        
        def get_list(self):
            for key in self.data:
                yield {'account':key, 'tarif':self.data[key]['tarif'], 'summ': self.data[key]['summ']}
                

    def __init__(self):
        Thread.__init__(self)

    def get_actual_cost(self, cur, trafic_transmit_service_id, traffic_class_id, direction, octets_summ, stream_date):
        """
        Метод возвращает актуальную цену для направления трафика для пользователя:
        """
        
        if direction=="INPUT":
            d = "in_direction=True"
        elif direction=="OUTPUT":
            d = "out_direction=True"
        else:
            
            return 0
        #print direction
        
        #print octets_summ, trafic_transmit_service_id, traffic_class_id, d    
        cur.execute(
        """
        SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start::timestamp without time zone, tpn.length, tpn.repeat_after
        FROM billservice_traffictransmitnodes as ttsn
        JOIN billservice_traffictransmitnodes_traffic_class as tcn ON tcn.traffictransmitnodes_id=ttsn.id
        JOIN billservice_traffictransmitnodes_time_nodes as tns ON tns.traffictransmitnodes_id=ttsn.id
        JOIN billservice_timeperiod_time_period_nodes ON billservice_timeperiod_time_period_nodes.timeperiod_id=tns.timeperiod_id
        JOIN billservice_timeperiodnode AS tpn on tpn.id=billservice_timeperiod_time_period_nodes.timeperiodnode_id 
        WHERE ((ttsn.edge_start>='%s'/(1024*1024) and ttsn.edge_end<='%s'/(1024*1024)) or (ttsn.edge_start>='%s'/(1024*1024) and ttsn.edge_end='0' ) ) and ttsn.traffic_transmit_service_id='%s' and tcn.trafficclass_id='%s' and ttsn.%s;
        """ % (octets_summ, octets_summ, octets_summ, trafic_transmit_service_id, traffic_class_id, d)
        )
        
        
        trafic_transmit_nodes=cur.fetchall()
        cost=0
        min_from_start=0
        for node in trafic_transmit_nodes:
            trafic_transmit_node_id=node[0]
            trafic_cost=node[1]
            trafic_edge_start=node[2]
            trafic_edge_end=node[3]

            period_start=node[4]
            period_length=node[5]
            repeat_after=node[6]
            tnc, tkc, from_start,result=in_period_info(time_start=period_start,length=period_length, repeat_after=repeat_after, now=stream_date)
            if result:
                if from_start<min_from_start or min_from_start==0:
                    min_from_start=from_start
                    cost=trafic_cost
        return cost


    def run(self):
        while True:
            connection = pool.connection()
            cur = connection.cursor()
            cur.execute(
            """
            SELECT nf.id, nf.account_id, nf.tarif_id, nf.date_start::timestamp without time zone, nf.traffic_class_id, nf.direction, nf.octets, bs_acc.username, 
            tarif.traffic_transmit_service_id, tarif.settlement_period_id, transmitservice.cash_method, transmitservice.period_check, accounttarif.id, accounttarif.datetime,
            settlementperiod.time_start::timestamp without time zone, settlementperiod.length_in, settlementperiod.length, settlementperiod.autostart
            FROM billservice_netflowstream as nf
            JOIN billservice_account as bs_acc ON bs_acc.id=nf.account_id
            JOIN nas_trafficclass as traficclass ON traficclass.id=nf.traffic_class_id
            JOIN billservice_tariff as tarif ON tarif.id=nf.tarif_id
            JOIN billservice_traffictransmitservice as transmitservice ON transmitservice.id=tarif.traffic_transmit_service_id
            JOIN billservice_accounttarif as accounttarif ON accounttarif.id=
            (SELECT id FROM billservice_accounttarif WHERE tarif_id=tarif.id and account_id=nf.account_id ORDER BY datetime DESC LIMIT 1)
            LEFT JOIN billservice_settlementperiod as settlementperiod ON settlementperiod.id = tarif.settlement_period_id
            WHERE for_checkout=True and checkouted=False ORDER BY nf.account_id ASC;
            """
            )
            rows=cur.fetchall()
            pays=self.Picker()
            i=0
            for row in rows:
                """
                TO-DO: Пробегаемся по всем записям. Суммируем суммы денег для одного пользователя и разом списываем всю сумму
                """
                i+=1
                nf_id, \
                account_id,\
                tarif_id, \
                stream_date, \
                traffic_class_id,\
                direction, \
                octets, \
                username, \
                trafic_transmit_service_id, \
                settlement_period_id, \
                cash_method, \
                period_check, \
                accounttarif_id,\
                accounttarif_datetime, \
                sp_time_start, \
                sp_length_in, \
                sp_length, \
                sp_autostart = row
                s=False

                if trafic_transmit_service_id:
                    #Если в тарифном плане указан расчётный период
                    if settlement_period_id:
                        if sp_autostart==True:
                            # Если у расчётного периода стоит параметр Автостарт-за начало расчётного периода принимаем
                            # дату привязки тарифного плана пользователю
                            sp_time_start=accounttarif_datetime

                        settlement_period_start, settlement_period_end, deltap = settlement_period_info(time_start=sp_time_start, repeat_after=sp_length_in, repeat_after_seconds=sp_length, now=stream_date)
                        
                        #Смотрим сколько уже наработал за текущий расчётный период по этому тарифному плану
                        cur.execute(
                            """
                            SELECT sum(octets)
                            FROM billservice_netflowstream
                            WHERE tarif_id=%s and account_id=%s and checkouted=True and date_start between '%s' and '%s'
                            """ % ( tarif_id, account_id, settlement_period_start, settlement_period_end)
                            )
                        
                        octets_summ=cur.fetchone()[0] or 0
                    else:
                        octets_summ=0
                    
                    #print "octets_summ", octets_summ
                    trafic_cost=self.get_actual_cost(cur,trafic_transmit_service_id, traffic_class_id, direction, octets_summ, stream_date)
                    """
                    Использован т.н. дифференциальный подход к начислению денег за трафик
                    Тарифный план позволяет указать по какой цене считать трафик
                    в зависимости от того сколько этого трафика уже накачал пользователь за расчётный период
                    """


                    if direction=="INPUT":
                        d = "in_direction=True"
                    elif direction=="OUTPUT":
                        d = "out_direction=True"
                    else:
                        d = "out_direction=True"

                    
                    #Исправить запрос
                    #print (accounttarif_id,traffic_class_id, trafic_transmit_service_id, d)
                    query="""
                    SELECT prepais.id, prepais.size FROM billservice_accountprepaystrafic as prepais
                    JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                    JOIN billservice_prepaidtraffic_traffic_class ON billservice_prepaidtraffic_traffic_class.prepaidtraffic_id=prepaidtraffic.id
                    WHERE prepais.size>0 and prepais.account_tarif_id=%s and billservice_prepaidtraffic_traffic_class.trafficclass_id=%s and prepaidtraffic.traffic_transmit_service_id=%s and prepaidtraffic.%s""" % (accounttarif_id,traffic_class_id, trafic_transmit_service_id, d)

                    #print query
                    cur.execute(query)

                    try:
                        
                        prepaid_id, prepaid=cur.fetchone()
                        
                        #print prepaid
                    except:
                        #print "dont prepaid"
                        prepaid=0
                        prepaid_id=-1
                    if prepaid>=0:
                        if prepaid>=octets:
                            prepaid=prepaid-octets
                            octets=0
                        elif octets>=prepaid:
                            octets=octets-prepaid
                            prepaid=0
                        #print prepaid/1024/1024
                        cur.execute("""UPDATE billservice_accountprepaystrafic SET size=%s WHERE id=%s""" % (prepaid, prepaid_id))

                    summ=(trafic_cost*octets)/(1024*1024)
                    print "summ=", summ
                    if summ>0:
                        pays.add_summ(account_id, tarif_id, summ)
                    #if summ>0 and (s==True or s==None):
                    cur.execute(
                    """
                    UPDATE billservice_netflowstream
                    SET checkouted=True
                    WHERE id=%s;
                    """ % nf_id
                    )
                    
      
            for l in pays.get_list():
                #Производим списывание денег
                transaction(
                cursor=cur,
                type='NETFLOW_BILL',
                account=l['account'],
                approved=True,
                tarif=l['tarif'],
                summ=l['summ'],
                description=u"",
                )
                connection.commit()




            connection.commit()
            cur.close()
            connection.close()
            time.sleep(120)

class limit_checker(Thread):
    """
    Проверяет исчерпание лимитов. если лимит исчерпан-ставим соотв галочку в аккаунте
    """
    def __init__ (self):
        Thread.__init__(self)

    def run(self):
        while True:
            connection = pool.connection()
            cur = connection.cursor()
            """
            Выбираем тарифные планы, у которых есть лимиты
            """
            cur.execute(
            """
            SELECT tarif.id, account.id, acctt.datetime::timestamp without time zone, sp.time_start::timestamp without time zone, sp.length, sp.length_in, sp.autostart
            FROM billservice_tariff as tarif
            JOIN billservice_accounttarif as acctt ON acctt.tarif_id=tarif.id and acctt.datetime=(SELECT datetime FROM billservice_accounttarif WHERE account_id=acctt.account_id and datetime<now() ORDER BY datetime DESC LIMIT 1)
            JOIN billservice_account as account ON account.id=acctt.account_id
            JOIN billservice_tariff_traffic_limit as ttl ON ttl.tariff_id=tarif.id
            LEFT JOIN billservice_settlementperiod as sp ON sp.id=tarif.settlement_period_id
            WHERE account.status=True ORDER BY account.id ASC;
            """
            )
            account_tarifs=cur.fetchall()
            oldid=-1
            for account_tarif in account_tarifs:
                tarif_id=account_tarif[0]
                account_id=account_tarif[1]
                tarif_start=account_tarif[2]
                tarif_sp_start=account_tarif[3]
                tarif_sp_length=account_tarif[4]
                tarif_sp_length_in=account_tarif[5]
                tarif_autostart_sp=account_tarif[6]

                if oldid==account_id and block:
                    """
                    Если у аккаунта уже есть одно превышение лимита
                    то больше для него лимиты не проверяем
                    """
                    continue
                #Выбираем лимит для аккаунта
                cur.execute(
                """
                SELECT ttl.trafficlimit_id, tl.size, tl.mode, tl.in_direction, tl.out_direction,  sp.time_start::timestamp without time zone, sp.length, sp.length_in, sp.autostart
                FROM billservice_tariff_traffic_limit as ttl
                JOIN billservice_trafficlimit as tl ON tl.id=ttl.trafficlimit_id
                LEFT JOIN billservice_settlementperiod as sp ON sp.id=tl.settlement_period_id
                WHERE ttl.tariff_id=%s;
                """ % tarif_id
                )
                limit=cur.fetchone()
                limit_id, limit_size, limit_mode, in_direction, out_direction, sp_time_start, sp_length, sp_length_in, autostart_sp=limit
                """
                Если в тарифном плане указан расчётный период,
                то за длинну периода
                """
                if tarif_sp_length:
                    st_tarif_period_length=tarif_sp_length
                elif tarif_sp_length_in:
                    st_tarif_period_length=tarif_sp_length_in

                if sp_length:
                    settlement_period_length=sp_length
                else:
                    settlement_period_length=sp_length_in

                #Если в лимите указан период
                autostart_sp, tarif_autostart_sp
                if autostart_sp!=None:
                    period_length=settlement_period_length
                    if autostart_sp==True:
                        settlement_period_start=tarif_start

                    elif autostart_sp==False:
                        period_start=sp_time_start
                #иначе берём данные о расчётном периоде из тарифного плана
                elif tarif_autostart_sp:
                    period_length=st_tarif_period_length
                    if tarif_autostart_sp==True:
                        settlement_period_start=tarif_start
                    elif tarif_autostart_sp==False:
                        settlement_period_start=sp_time_start
                else:
                    #если и там не указан-пропускаем цикл
                    continue
                
                #print settlement_period_start, period_length, datetime.datetime.now()
                
                settlement_period_start, settlement_period_end, delta = settlement_period_info(time_start=settlement_period_start, repeat_after=period_length, now=datetime.datetime.now())
                #если нужно считать количество трафика за последнеие N секунд, а не за рачётный период, то переопределяем значения
                if limit_mode==True:
                    settlement_period_start=datetime.datetime.now()-datetime.timedelta(seconds=delta)
                    settlement_period_end=datetime.datetime.now()
                
                block=False
                
                d=''
                if in_direction:
                    d+=" 'INPUT'"
                if out_direction:
                    if in_direction:
                        d+=","
                    d+="'OUTPUT'"
                    
                query="""
               SELECT sum(octets) as size FROM billservice_netflowstream as nf
               JOIN billservice_trafficlimit_traffic_class as tltc ON tltc.trafficclass_id=nf.traffic_class_id
               WHERE nf.account_id=%s and tltc.trafficlimit_id=%s and date_start>'%s' and date_start<'%s' and nf.direction in (%s)

                """ % (account_id, limit_id, settlement_period_start, settlement_period_end, d)
                #print query
                cur.execute(query)
                tsize=0
                sizes=cur.fetchall()

                for size in sizes:
                    if size[0]!=None:
                        tsize+=size[0]

                if tsize>limit_size*1024:
                   block=True


                oldid=account_id
                #пишем в базу состояние пользователя
                cur.execute(
                """
                UPDATE billservice_account
                SET disabled_by_limit=%s
                WHERE id=%s;
                """ % (block, account_id)
                )

            connection.commit()
            cur.close()
            connection.close()
            time.sleep(60)


class settlement_period_service_dog(Thread):
    """
    Для каждого пользователя по тарифному плану в конце расчётного периода производит
    1. Доснятие суммы
    2. Если денег мало для активации тарифного плана, ставим статус Disabled
    2. Сброс и начисление предоплаченного времени
    3. Сброс и начисление предоплаченного трафика
    алгоритм
    1. выбираем всех пользователей с текущими тарифными планами,
    у которых указан расчётный период и галочка "делать доснятие"
    2. Считаем сколько денег было взято по транзакциям.
    3. Если сумма меньше цены тарифного плана-делаем транзакцию, в которой снимаем деньги.
    """
    def __init__ (self):
        Thread.__init__(self)


    def stop(self):
        """
        Stop the thread
        """


    def run(self):
        connection = pool.connection()
        cur = connection.cursor()
        from types import NoneType
        while True:

            cur.execute(
                        """
                        SELECT shedulelog.id, account.id, shedulelog.ballance_checkout::timestamp without time zone, shedulelog.prepaid_traffic_reset::timestamp without time zone, shedulelog.prepaid_time_reset::timestamp without time zone,
                        sp.time_start::timestamp without time zone, sp.length, sp.length_in,sp.autostart, accounttarif.id, accounttarif.datetime::timestamp without time zone,  tariff.id, tariff.reset_tarif_cost , tariff.cost, tariff.traffic_transmit_service_id, tariff.time_access_service_id, traffictransmit.reset_traffic, timeaccessservice.reset_time,
                        shedulelog.balance_blocked::timestamp without time zone, shedulelog.prepaid_traffic_accrued::timestamp without time zone, shedulelog.prepaid_time_accrued::timestamp without time zone
                        FROM billservice_account as account  
                        LEFT JOIN billservice_shedulelog as shedulelog on shedulelog.account_id=account.id
                        JOIN billservice_accounttarif AS accounttarif ON accounttarif.account_id=get_tarif(account.id)
                        JOIN billservice_tariff as tariff ON tariff.id=accounttarif.tarif_id
                        JOIN billservice_settlementperiod as sp ON sp.id=tariff.settlement_period_id
                        LEFT JOIN billservice_traffictransmitservice as traffictransmit ON traffictransmit.id=tariff.traffic_transmit_service_id
                        LEFT JOIN billservice_timeaccessservice as timeaccessservice ON timeaccessservice.id=tariff.time_access_service_id
                        WHERE 
                        shedulelog.ballance_checkout is Null
                        or shedulelog.prepaid_traffic_reset is Null
                        or shedulelog.prepaid_time_reset is Null
                        or shedulelog.prepaid_traffic_accrued is Null
                        or shedulelog.prepaid_time_accrued is Null
                        """
                        )
            rows=cur.fetchall()
            for row in rows:
                (shedulelog_id, account_id, ballance_checkout, prepaid_traffic_reset, prepaid_time_reset,
                time_start, length, length_in, autostart, accounttarif_id, acct_datetime, tarif_id,
                reset_tarif_cost, cost, traffic_transmit_service_id, time_access_service_id,
                reset_traffic, reset_time, balance_blocked, prepaid_traffic_accrued, prepaid_time_accrued) = row
                
                if autostart:
                    time_start=acct_datetime




                period_start, period_end, delta = settlement_period_info(time_start=time_start, repeat_after=length_in, repeat_after_seconds=length)

                #нужно производить в конце расчётного периода
                
                if (ballance_checkout is None and  (datetime.datetime.now()-time_start).seconds>=delta) or (ballance_checkout!=None and ballance_checkout<=period_start):
                    #Снять сумму до стоимости тарифного плана
                    if reset_tarif_cost:
                        cur.execute(
                                    """
                                    SELECT sum(summ)
                                    FROM billservice_transaction
                                    WHERE created > '%s' and created< '%s' and account_id=%s and tarif_id=%s;
                                    """ % (period_start, period_end, account_id, tarif_id)
                                    )
                        summ=cur.fetchone()[0]
                        if summ==None:
                            summ=0
                        if cost>summ:
                            s=cost-summ
                            transaction(
                            cursor=cur,
                            type='END_PS_MONEY_RESET',
                            account=account_id,
                            approved=True,
                            tarif=tarif_id,
                            summ=s,
                            description=u"Доснятие денег до стоимости тарифного плана у %s" % account_id,
                            )
                            
                        if shedulelog_id is not None:
                            cur.execute("UPDATE billservice_shedulelog SET ballance_checkout=now() WHERE account_id=%s;" % account_id)
                        else:
                            cur.execute("""
                            INSERT INTO billservice_shedulelog(account_id, ballance_checkout) values(%d, now());
                            """ % account_id)
                            
                    #Если балланса не хватает - отключить пользователя

                if (ballance_checkout is None or ballance_checkout<=period_start) and cost>0:
                    #В начале каждого расчётного периода
                    cur.execute(
                                """
                                UPDATE billservice_account SET balance_blocked=True WHERE id=%s and ballance+credit<%s;
                                """ % (account_id, cost)
                                )

                    if shedulelog_id is not None:
                        cur.execute("""
                        UPDATE billservice_shedulelog SET balance_blocked = now() WHERE id=%d;
                        """ % shedulelog_id)
                    else:
                        cur.execute("""
                        INSERT INTO billservice_shedulelog(account_id, balance_blocked) values(%d, now()); 
                        """ % account_id)
                else:
                    #Иначе Убираем отметку
                    cur.execute(
                                """
                                UPDATE billservice_account SET balance_blocked=False WHERE id=%s;
                                """ % (account_id)
                                )                            
                     
                    
                if (prepaid_traffic_reset is None or prepaid_traffic_reset<period_start):
                    cur.execute(
                        """
                        DELETE FROM billservice_accountprepaystrafic WHERE account_tarif_id=%s;
                        """ % accounttarif_id
                        )
                    if shedulelog_id is not None:
                        cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_reset=now() WHERE account_id=%s RETURNING id;" % account_id)
                    else:
                        cur.execute("""
                            INSERT INTO billservice_shedulelog(account_id, prepaid_traffic_reset) values(%d, now()) ;
                            """ % account_id)    
                         
                if (prepaid_traffic_accrued is None or prepaid_traffic_accrued<period_start):                          
                    #Начислить новый предоплаченный трафик
                    cur.execute(
                                """
                                SELECT id, size
                                FROM billservice_prepaidtraffic
                                WHERE traffic_transmit_service_id=%s;
                                """ % traffic_transmit_service_id
                                )
                    
                    prepais=cur.fetchall()
                    for prepaid_traffic_id, size in prepais:
                        print "SET PREPAID TRAFIC"
                        cur.execute(
                                    """
                                    UPDATE billservice_accountprepaystrafic SET size=size+%s, datetime=now()
                                    WHERE account_tarif_id=%s and prepaid_traffic_id=%s RETURNING id;
                                    """ % (size, accounttarif_id, prepaid_traffic_id)
                                    )
                        if cur.fetchone() is None:
                            print 'INSERT'
                            print accounttarif_id, prepaid_traffic_id, size
                            cur.execute(
                                        """
                                        INSERT INTO billservice_accountprepaystrafic (account_tarif_id, prepaid_traffic_id, size, datetime)
                                        VALUES(%d,%d, %f*1024*1024, now());
                                        """ % (accounttarif_id, prepaid_traffic_id, size)
                                        )                            
                        
                    cur.execute("UPDATE billservice_shedulelog SET prepaid_traffic_accrued=now() WHERE account_id=%s RETURNING id;" % account_id)
                    if cur.fetchone()==None:
                        cur.execute("""
                            INSERT INTO billservice_shedulelog(account_id, prepaid_traffic_accrued) values(%d, now()) ;
                            """ % account_id)  
                        
                if (prepaid_time_reset is None or prepaid_time_reset<period_start) and time_access_service_id:

                    if reset_time:
                        #снять время и начислить новое
                        cur.execute(
                                    """
                                    DELETE FROM billservice_accountprepaystime
                                    WHERE account_tarif=%s;
                                    """ % accounttarif_id
                                    )
                        if shedulelog_id is not None:
                            cur.execute("UPDATE billservice_shedulelog SET prepaid_time_reset=now() WHERE account_id=%s RETURNING id;" % account_id)
                        else:
                            cur.execute("""
                                INSERT INTO billservice_shedulelog(account_id, prepaid_time_reset) values(%d, now()) ;
                                """ % account_id)        
                        
                if (prepaid_time_accrued is None or prepaid_time_accrued<period_start) and time_access_service_id:
                    
                    cur.execute(
                                """
                                UPDATE billservice_accountprepaystime
                                SET size=size+(SELECT prepaid_time FROM billservice_timeaccessservice WHERE id=%s),
                                datetime=now()
                                WHERE account_tarif_id=%s RETURNING id;
                                """ % (time_access_service_id, accounttarif_id)
                                )
                    if cur.fetchone():
                        cur.execute(
                                    """
                                    INSERT INTO billservice_accountprepaystime(account_tarif_id, size, datetime,prepaid_time_service_id)
                                    VALUES(%d, (SELECT prepaid_time FROM billservice_timeaccessservice WHERE id=%d), now(), %d);
                                    """ % (accounttarif_id, time_access_service_id, time_access_service_id)
                                    )
                        
                    
                    if shedulelog_id is not None:
                        cur.execute("UPDATE billservice_shedulelog SET prepaid_time_accrued=now() WHERE account_id=%s RETURNING id;" % account_id)
                    else:
                        cur.execute("""
                            INSERT INTO billservice_shedulelog(account_id, prepaid_time_accrued) values(%d, now()) ;
                            """ % account_id)
                connection.commit()
            time.sleep(120)

class ipn_service(Thread):
    """
    Тред должен:
    1. Проверять не изменилась ли скорость для IPN клиентов и менять её на сервере доступа
    2. Если балланс клиента стал меньше 0 - отключать, если уже не отключен (параметр ipn_status в account) и включать, если отключен (ipn_status) и баланс стал больше 0
    3. Если клиент вышел за рамки разрешённого временного диапазона в тарифном плане-отключать
    """
    def __init__ (self):
        Thread.__init__(self)
        self.connection = pool.connection()
        self.cur = self.connection.cursor()

    def check_period(self, rows):
        for row in rows:
            if in_period(row[0],row[1],row[2])==True:
                return True
        return False

    def create_speed(self, tarif_id, nas_type):
        defaults = get_default_speed_parameters(self.cur, tarif_id)
        speeds = get_speed_parameters(self.cur, tarif_id)
        result=[]
        i=0
        for speed in speeds:
            if in_period(speed[0],speed[1],speed[2])==True:
                for s in speed[3:]:
                    if s==0:
                        res=0
                    elif s=='' or s==None:
                        res=defaults[i]
                    else:
                        res=s
                    result.append(res)
                    i+=1
        if speeds==[]:
            result=defaults

        return create_speed_string(result, nas_type, coa=False)


    def run(self):
        while True:
            self.cur.execute(
                        """
                        SELECT account.id, account.username, account.ipn_ip_address, account.ipn_mac_address,
                            (account.ballance+account.credit) as ballance, account.disabled_by_limit,
                            account.ipn_status, tariff.id,
                            nas."type", nas.user_enable_action, nas.user_disable_action, nas."login", nas."password", nas."ipaddress",
                            accessparameters.access_type, accessparameters.access_time_id, ipn_speed.speed, ipn_speed.static, ipn_speed.state
                        FROM billservice_account as account
                        JOIN billservice_accounttarif as accounttarif on accounttarif.id=(SELECT id FROM billservice_accounttarif
                        WHERE account_id=account.id and datetime<now() ORDER BY datetime DESC LIMIT 1)
                        JOIN billservice_tariff as tariff ON tariff.id=accounttarif.tarif_id
                        JOIN billservice_accessparameters as accessparameters ON accessparameters.id=tariff.access_parameters_id
                        JOIN nas_nas as nas ON nas.id=account.nas_id
                        LEFT JOIN billservice_accountipnspeed as ipn_speed ON ipn_speed.account_id=account.id
                        WHERE account.status=True and accessparameters.access_type='IPN'
                        ;"""
                        )
            rows=self.cur.fetchall()
            for row in rows:
                print "check ipn"
                account_id = row[0]
                account_username = row[1]
                account_ipaddress = row[2]
                account_mac = row[3]
                account_ballance=row[4]
                account_disabled_by_limit=row[5]
                account_ipn_status=row[6]
                tarif_id=row[7]
                nas_type=row[8]
                nas_user_enable=row[9]
                nas_user_disable=row[10]
                nas_login=row[11]
                nas_password=row[12]
                nas_ipaddress=row[13]
                access_type=row[14]
                access_time_id=row[15]
                ipn_speed=row[16]
                ipn_static=row[17]
                ipn_state=row[18]
                sended=None

                period=self.check_period(time_periods_by_tarif_id(self.cur, tarif_id))

                if account_ballance>0 and period==True and account_ipn_status==False:
                    print 1
                    #шлём команду, на включение пользователя, account_ipn_status=True
                    sended=ipn_manipulate(nas_ip=nas_ipaddress, nas_login=nas_login, nas_password=nas_password, format_string=nas_user_enable,
                                   account_data={'access_type':access_type,'username':account_username,
                                                 'user_id':account_id,'ipaddress':account_ipaddress,
                                                 'mac_address':account_mac,
                                                 }
                                   )


                elif (account_disabled_by_limit==True or account_ballance<=0 or period==False) and account_ipn_status==True:
                    print 2
                    #шлём команду на отключение пользователя,account_ipn_status=False
                    sended=ipn_manipulate(nas_ip=nas_ipaddress, nas_login=nas_login, nas_password=nas_password, format_string=nas_user_disable,
                                   account_data={'access_type':access_type,'username':account_username,
                                                 'user_id':account_id,'ipaddress':account_ipaddress,
                                                 'mac_address':account_mac,
                                                 }
                                   )

                if sended in (True, False):
                    self.cur.execute("UPDATE billservice_account SET ipn_status=%s WHERE id=%s" % (not sended, account_id))

                speed=self.create_speed(tarif_id, nas_type)
                if speed!=ipn_speed and (ipn_static==False or (ipn_static==True and ipn_state==False)):
                    #отправляем на сервер доступа новые настройки скорости, помечаем state=True
                    """
                    Если настройки скорости изменились и не стоит флажок "Не менять скорость" ИЛИ
                    если изменились настройки скорости и стоит флажёк не менять скорость и настройки скорости не были произведены
                    """
                    sended_speed=ipn_manipulate(nas_ip=nas_ipaddress, nas_login=nas_login, nas_password=nas_password, format_string=speed)
                    self.cur.execute("UPDATE billservice_accountipnspeed SET speed='%s', state=%s WHERE account_id=%s" % (speed, sended_speed, account_id))




            self.connection.commit()
            time.sleep(60)

class RPCServer(Thread, Pyro.core.ObjBase):
    def __init__ (self):
        Thread.__init__(self)
        Pyro.core.ObjBase.__init__(self)
        self.connection = pool.connection()
        #print dir(self.connection)
        self.connection._con._con.set_client_encoding('UTF8')
        self.cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  
        self.listconnection = pool.connection()
        self.listconnection._con._con.set_client_encoding('UTF8')
        self.listcur = self.listconnection.cursor()
              
        #self._cddrawer = cdDrawer()

        
    def run(self):
        Pyro.core.initServer()
        daemon=Pyro.core.Daemon()
        daemon.connect(self,"rpc")
        
        daemon.requestLoop()

    def testCredentials(self, host, login, password):
        try:
            print host, login, password
            a=SSHClient(host, 22,login, password)
            a.close()
        except Exception, e:
            print e
            return False
        return True

    def configureNAS(self, host, login, password, configuration):
        try:
            a=SSHClient(host, 22,login, password)
            print configuration
            print a.send_command(configuration)
            a.close()
        except Exception, e:
            print e
            return False
        return True

    def accountActions(self, host, login, password, action, account_id):
        if action=='disable':
            command = '/ip firewall address-list set [find comment="%s"] disabled=yes' % account_id
        elif action=='enable':
            command = '/ip firewall address-list set [find comment="%s"] disabled=no' % account_id
        try:
            a=SSHClient(host, 22,login, password)
            print a.send_command(command)
            a.close()
        except Exception, e:
            print e
            return False
        return True
        
    def get_object(self, name):
        try:
            model = models.__getattribute__(name)()
        except:
            return None


        return model
    
    def transaction_delete(self, ids):
        for i in ids:

            delete_transaction(self.cur, int(i))
            
        self.connection.commit()
        
    def get(self, sql):
        #print sql
        self.cur.execute(sql)
        #self.connection.commit()
        result=[]
        r=self.cur.fetchall()
        if len(r)>1:
            raise Exception
        
        if r==[]:
            return None
        return Object(r[0])
    
    def get_list(self, sql):
        print sql
        self.listcur.execute(sql)
        return self.listcur.fetchall()
    
    def delete(self, sql):
   
        self.cur.execute(sql)
        #self.connection.commit()
        return 

    def command(self, sql):
   
        self.cur.execute(sql)
        #self.connection.commit()
        return         
        
    def commit(self):
        self.connection.commit()
        
    def makeChart(self, *args, **kwargs):
        bpplotAdapter.rCursor = self.listcur
        cddrawer = cdDrawer()
        imgs = cddrawer.cddraw(*args, **kwargs)
        return imgs
    '''def setChartOptions(self, chartname, optdict):
        #self._cddrawer.set_options(chartname, optdict)
        pass'''
        
    def rollback(self):
        self.connection.rollback()
        
    def sql(self, sql, return_response=True, pickler=False):
        #print sql
        self.cur.execute(sql)
        #self.connection.commit()
        
        #print dir(self.connection)
        result=[]
        a=time.clock()
        if return_response:
            result = map(Object, self.cur.fetchall())
        print "Query length=", time.clock()-a
        if pickler:
            output = open('data.pkl', 'wb')
            b=time.clock()-a
            
            pickle.dump(result, output)
            output.close()
            print "Pickle length=", time.clock()-a
        return result

    def sql_as_dict(self, sql, return_response=True):
        #print sql
        self.cur.execute(sql)
        #self.connection.commit()
        
        #print dir(self.connection)
        result=[]
        a=time.clock()
        if return_response:
            #for r in self.cur.fetchall():
            #    result.append(Object(r))
            result =self.cur.fetchall()
        print "Query length=", time.clock()-a
        return result
      
  
    def create(self, sql):
        print sql
        self.cur.execute(sql)
        id=-1
        #print self.cur.fetchone()
        try:
            id = self.cur.fetchone()['id']
        except:
            pass
        #self.connection.commit()
               
        return id


    def connection_request(self, username, password):
        try:
            obj = self.get("SELECT * FROM billservice_systemuser WHERE username='%s'" % username)
        except Exception, e:
            print e
            return False
        if obj is not None and obj.password==password:
            self.create("UPDATE billservice_systemuser SET last_login=now() WHERE id=%d;" % obj.id)
            #Pyro.constants.
            
            return True
        else:
            return False
        

    def pod(self, session):
        
        session = self.cur.execute("""
        SELECT nas.ipaddress as nas_ip, nas.type as nas_type, nas.name as nas_name, nas.secret as nas_secret, nas.login as nas_login, nas.password as nas_password,
        nas.reset_action as reset_action, account.id as account_id, account.username as account_name, account.vpn_ip_address as vpn_ip_address,
        account.ipn_ip_address as ipn_ip_address, account.ipn_mac_address as ipn_mac_address, session.framed_protocol as framed_protocol
        FROM radius_activesession as session
        JOIN billservice_account as account ON account.id=session.account_id
        JOIN nas_nas as nas ON nas.id=account.nas_id
        WHERE  session.sessionid='%s'
        """ % session)
        row = self.cur.fetchone()
        PoD(dict=dict,
            account_id=row['account_id'], 
            account_name=str(row['account_name']), 
            account_vpn_ip=row['vpn_ip_address'], 
            account_ipn_ip=row['ipn_ip_address'], 
            account_mac_address=row['ipn_mac_address'], 
            access_type=str(row['framed_protocol']), 
            nas_ip=row['nas_ip'], 
            nas_type=row['nas_type'], 
            nas_name=row['nas_name'], 
            nas_secret=row['nas_secret'], 
            nas_login=row['nas_login'], 
            nas_password=row['nas_password'], 
                session_id=str(session), 
                format_string=str(row['reset_action'])
                )



if __name__ == "__main__":

    dict=dictionary.Dictionary("dicts/dictionary","dicts/dictionary.microsoft","dicts/dictionary.mikrotik","dicts/dictionary.rfc3576")
#===============================================================================
    threads=[]
    threads.append(check_vpn_access(timeout=60, dict=dict))

#    traficaccessbill = TraficAccessBill()
#    traficaccessbill.start()

    threads.append(periodical_service_bill())
    threads.append(TimeAccessBill())
    threads.append(NetFlowAggregate())
    threads.append(NetFlowBill())

    #threads.append(limit_checker())


    #threads.append(ipn_service())


    threads.append(settlement_period_service_dog())

    threads.append(RPCServer())
    #print rosClient("10.20.3.1", 'dolph', '12345', r'/interface/pppoe-server/remove [/interface/pppoe-server/find]')
    ssh=SSHClient(host='10.10.1.100', port=22, username='admin', password='admin')
    response=ssh.send_command("/queue simple print detail without-paging")[0]
    response = response.readlines()
    print response
    for th in threads:
        th.start()

    while True:
        for t in threads:

            if not t.isAlive():
                print 'restarting thread', t.getName()
                #t.__init__()
                #t.start()
                print 'thread status', t.getName(), t.isAlive()
        time.sleep(15)


#===============================================================================
