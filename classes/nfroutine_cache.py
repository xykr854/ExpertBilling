from operator import itemgetter, setitem
from cacheutils import CacheCollection, CacheItem, SimpleDefDictCache, SimpleDictCache
from cache_sql import nfroutine_sql
from collections import defaultdict
from nfroutine_class.AccountData import AccountData
from nfroutine_class.TrafficTransmitServiceData import TrafficTransmitServiceData
from nfroutine_class.SettlementData import SettlementData
from nfroutine_class.NodesData import NodesData

class NfroutineCaches(CacheCollection):
    __slots__ = ('account_cache', 'period_cache', 'nodes_cache', 'settlement_cache', 'traffictransmit_cache', 'prepays_cache', 'storeclass_cache')
    
    def __init__(self, date, fMem):
        super(NfroutineCaches, self).__init__(date)
        self.account_cache = AccountCache(date)
        self.period_cache  = PeriodCache(date, fMem)
        self.prepays_cache = PrepaysCache(date)
        self.nodes_cache   = NodesCache()
        self.settlement_cache = SettlementCache()
        self.traffictransmit_cache = TrafficTransmitServiceCache()
        self.storeclass_cache = StoreClassCache()
        self.caches = [self.account_cache, self.period_cache, self.prepays_cache, self.nodes_cache, self.settlement_cache, self.traffictransmit_cache, self.storeclass_cache]

class AccountCache(CacheItem):
    __slots__ = ('by_account',)
    
    datatype = AccountData
    sql = nfroutine_sql['accounts']

    def __init__(self, date):
        super(AccountCache, self).__init__()
        self.vars = (date,)
        
    def reindex(self):
        self.by_account = {}
        for acct in self.data:
            self.by_account[acct.account_id]  = acct
            
class PeriodCache(CacheItem):
    __slots__ = ('in_period', 'fMem', 'date')
    datatype = lambda: defaultdict(lambda: False)
    sql = nfroutine_sql['period']
    
    def __init__(self, date, fMem):
        super(PeriodCache, self).__init__()
        self.date = date
        self.vars = (date,)
        self.fMem = fMem
        
    def transformdata(self): pass
    def reindex(self):
        self.in_period = defaultdict(lambda: False)
        for tpnap in self.data:
            self.in_period[tpnap[3]] = self.in_period[tpnap[3]] or self.fMem.in_period_(tpnap[0], tpnap[1], tpnap[2], self.date)[3]
            
class PrepaysCache(CacheItem):
    '''(id, size) by (traffic_transmit_service_id, account_tarif_id, group_id) key'''
    __slots__ = ('by_tts_acctf_group',)
    datatype = dict
    sql = nfroutine_sql['prepays']
    
    def __init__(self, date):
        super(PrepaysCache, self).__init__()
        self.vars = (date,)
    
    def transformdata(self): pass
    
    def reindex(self):
        self.by_tts_acctf_group = {}
        for prep in self.data:
            self.by_tts_acctf_group[(prep[4],prep[2],prep[3])] = [prep[0], prep[1]]
        
class NodesCache(CacheItem):
    '''Traffictransmit- and timeperiod- nodes data by (traffic_transmit_service_id, group_id)'''
    __slots__ = ('by_tts_group',)
    datatype = NodesData
    sql = nfroutine_sql['nodes']
    
    def reindex(self):
        self.by_tts_group = defaultdict(list)
        for trnode in self.data:
            if trnode.group_id:
                self.by_tts_group[(trnode.traffic_transmit_service_id,trnode.group_id)].append(trnode)
                
class TrafficTransmitServiceCache(SimpleDictCache):
    __slots__ = ()
    datatype = TrafficTransmitServiceData
    sql = nfroutine_sql['tts']
    num = 0

class SettlementCache(SimpleDictCache):
    __slots__ = ()
    datatype = SettlementData
    sql = nfroutine_sql['settlepd']
    num = 0
    
class StoreClassCache(CacheItem):
    '''A set of classes that must be stored'''
    __slots__ = ('classes',)
    datatype = set
    sql = nfroutine_sql['sclasses']
    
    def transformdata(self): pass
    
    def reindex(self):
        try:
            self.classes = set(self.data[0][0])
        except:
            self.classes = set()
        