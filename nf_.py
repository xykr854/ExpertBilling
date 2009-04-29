#-*-coding=utf-8-*-

from __future__ import with_statement
import gc
import glob
import random
import signal
import os, sys
import marshal
import asyncore
import psycopg2
import threading
import traceback
import ConfigParser
import socket, select, struct, datetime, time

import isdlogger
import saver


from threading import Thread, Lock
from daemonize import daemonize
from DBUtils.PooledDB import PooledDB
from IPy import IP, IPint, parseAddress
from collections import deque, defaultdict
from saver import graceful_loader, graceful_saver, allowedUsersChecker, setAllowedUsers

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import pollreactor
pollreactor.install()
from twisted.internet import reactor

from classes.nf_cache import *
from classes.common.Flow5Data import Flow5Data
from classes.cacheutils import CacheMaster
from classes.flags import NfFlags
from classes.vars import NfVars, NfQueues



try:    import mx.DateTime
except: pass

class Reception(DatagramProtocol):
    '''
    Twisted Asynchronous server that recieves datagrams with NetFlow packets
    and appends them to 'nfQueue' queue.
    '''
    def datagramReceived(self, data, addrport):
        if len(data)<=8192:
            nfQueue.append((data, addrport))
        else:
            logger.error("NF server exception: packet <= 8192")
             
class nfDequeThread(Thread):
    '''Thread that gets packets received by the server from nfQueue queue and puts them onto the conveyour
    that gets flows and caches them.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)
        
    def run(self):
        global nfFlowCache
        while True:
            if suicideCondition[self.tname]: break
            #TODO: add locks if deadlocking issues arise
            try:
                data, addrport = nfQueue.popleft()        
                nfPacketHandle(data, addrport, nfFlowCache)
            except IndexError, ierr:
                time.sleep(3); continue    
            except Exception, ex:
                logger.error("NFP exception: %s \n %s", (repr(ex), traceback.format_exc()))


def flow5(data):
    if len(data) != vars.flowLENGTH:
        raise ValueError, "Short flow: data length: %d; LENGTH: %d" % (len(data), flowLENGTH)
    #must turn tuples into lists because they are to be modified
    return Flow5Data(*struct.unpack("!LLLHHIIIIHHBBBBHHBBH", data))


def header5(data):
    """
    Function that unpacks Netflow packet header binary string into a tuple.
    data legend:
        _nh = struct.unpack("!HHIIIIBBH", data)
        self.version = _nh[0]
        self.num_flows = _nh[1]
        self.sys_uptime = _nh[2]
        self.time_secs = _nh[3]
        self.time_nsecs = _nh[4]
    """
    if len(data) != headerLENGTH:
        raise ValueError, "Short flow header"
    return struct.unpack("!HHIIIIBBH", data)

def nfPacketHandle(data, addrport, flowCache):
    '''
    Function receiving a binary Netflow packet, sender addrport and FlowCache reference.
    Gets, unpacks and checks flows from packets.
    Approved packets are added to FlowCache.
    '''    
    if len(data) < 16:
        #raise ValueError, "Short packet"
        return
    caches = cacheMaster.cache
    if 0: assert isinstance(caches, NfCaches)
    nas_id = caches.nas_cache.ip_id.get(addrport[0])
    if not nas_id: return
          
    flows=[]
    _nf = struct.unpack("!H", data[:2])
    pVersion = _nf[0]
    if not pVersion in vars.FLOW_TYPES.keys():
        raise RuntimeWarning, "NetFlow version %d is not yet implemented" % pVersion
    hdr_class, flow_class  = vars.FLOW_TYPES[pVersion]
    hdr = hdr_class(data[:headerLENGTH])
    #======
    #runs through flows
    for n in xrange(hdr[1]):
        offset = vars.headerLENGTH + (vars.flowLENGTH * n)
        flow_data = data[offset:offset + vars.flowLENGTH]
        flow = flow_class(flow_data)
        if 0: assert isinstance(flow, Flow5Data)
        #look for account for ip address
        acc_acct_tf = (caches.account_cache.vpn_ips.get(flow.src_addr) or caches.account_cache.vpn_ips.get(flow.dst_addr) \
                    or caches.account_cache.ipn_ips.get(flow.src_addr) or caches.account_cache.ipn_ips.get(flow.dst_addr) )
        if acc_acct_tf:
            flow.nas_id = nas_id
            #acc_id, acctf_id, tf_id = (acc_acct_tf)
            flow.padding = acc_acct_tf
            if flags.checkClasses:
                break_outer = False
                for nclass, nnodes in caches.class_cache.classes:                        
                    for nnode in nnodes:
                        if 0: assert isinstance(nnode,ClassData)
                        if (((flow.src_addr & nnode.src_mask) == nnode.src_ip) and \
                            ((flow.dst_addr & nnode.dst_mask) == nnode.dst_ip) and \
                            ((flow.next_hop == nnode.next_hop) or (not nnode.next_hop)) and \
                            ((flow.src_port == nnode.src_port) or (not nnode.src_port)) and \
                            ((flow.dst_port == nnode.dst_port) or (not nnode.dst_port)) and \
                            ((flow.protocol == nnode.protocol) or (not nnode.protocol))):
                            
                            flowCache.addflow5(flow)
                            break_outer = True
                            break
                    if break_outer: break
                continue
            
            flowCache.addflow5(flow)         
                
                        

class FlowCache(object):
    '''Aggregates flows.'''
    def __init__(self):
        queues.dcache = {}
        #list for keeping keys
        self.keylist = []
        self.stime = time.time()

    def addflow(self, version, flow):
        method = getattr(self, "addflow" + str(version), None)
        return method(flow)

    def reset(self):
        if ((self.stime + 60.0) < time.time()) and self.keylist:
            #appends keylist to flowQueue
            with queues.fqueueLock:
                queues.flowQueue.append((self.keylist, time.time()))
            #-----------------
            #nullifies keylist
            self.keylist = []
            self.stime = time.time()
            
    def addflow5(self, flow):
        global queues, vars
        if 0: assert isinstance(flow, Flow5Data)
        #constructs a key
        key = (flow.src_addr, flow.dst_addr, flow.next_hop, flow.src_port, flow.dst_port, flow.protocol)
        
        queues.dcacheLock.acquire()
        dflow = queues.dcache.get(key)
        #no such value, must add        
        if dflow:
            dflow.octets  += flow.octets
            dflow.packets += flow.packets
            dflow.finish = flow.finish
            queues.dcacheLock.release()
        else:
            queues.dcache[key] = flow
            queues.dcacheLock.release()
            #stores key in a list
            self.keylist.append(key)
            #time to start over?
            if (len(self.keylist) > vars.aggrNum) or ((self.stime + 10.0) < time.time()):
                #appends keylist to flowQueue
                with queues.fqueueLock:
                    queues.flowQueue.append((self.keylist, time.time()))
                #nullifies keylist
                self.keylist = []
                self.stime = time.time()            
                
class FlowDequeThread(Thread):
    '''Gets a keylist with keys to flows that are to be aggregated, waits for aggregation time, pops them from aggregation cache,
    constructs small lists of flows and appends them to 'databaseQueue'.'''
    
    def __init__(self):
        self.tname = self.__class__.__name__
        Thread.__init__(self)        
    
    def add_classes_groups(self, flow, classLst, nnode, acctf_id, has_groups, tarifGroups):
        ptime =  time.time()
        ptime = ptime - (ptime % 20)
        if 0: assert isinstance(flow, Flow5Data); assert isinstance(nnode, ClassData)
        flow.datetime = ptime; flow.class_id = tuple(classLst)
        flow.node_direction = nnode.direction; flow.class_store = nnode.store
        flow.class_passthrough = nnode.passthrough; flow.acctf_id = acctf_id
        flow.groups = None; flow.has_groups = has_groups
        #add groups, check if any
        if has_groups:
            dr = 0
            if   nnode.direction == 'INPUT' : dr = 2
            elif nnode.direction == 'OUTPUT': dr = 1
            groupLst = []
            fcset = set(classLst)
            for tgrp in tarifGroups:
                if 0: assert isinstance(tgrp, GroupsData)
                if (not tgrp.trafficclass) or (tgrp.direction == dr):
                    continue
                group_cls = fcset.intersection(tgrp.trafficclass)
                if group_cls:
                    group_add = tgrp[:]
                    group_add[1] = tuple(group_cls)
                    groupLst.append(tuple(group_add))
            flow.groups = tuple(groupLst)

    def run(self):
        j = 0
        while True:
            if suicideCondition[self.tname]: break
            try:       
                stime = 0
                queues.fqueueLock.acquire()
                try:
                    #get keylist and time
                    keylist, stime = queues.flowQueue.popleft()
                except Exception, ex:
                    logger.debug("fdqThread indexerror exception: %s", repr(ex))
                finally:
                    queues.fqueueLock.release()
                if not stime: time.sleep(5); continue
                
                #if aggregation time was still not reached -> sleep
                wtime = time.time() - vars.aggrTime - stime
                if wtime < 0: time.sleep(abs(wtime))
                

                fcnt = 0
                flst = []
                for key in keylist:
                    with queues.dcacheLock:
                        flow = queues.dcache.pop(key, None)
                    if not flow: continue
                    if 0: assert isinstance(flow, Flow5Data)
                    #get id's
                    acc_id, acctf_id, tf_id = flow.padding; flow.padding = 0
                    flow.account_id = acc_id
                    #get groups for tarif
                    tarifGroups = cacheMaster.cache.tfgroup_cache.by_tarif.get(tf_id)
                    has_groups = True if tarifGroups else False
                    
                    passthr = True; direction=None
                    #checks classes                    
                    fnode = None; classLst = []                    
                    #Direction is taken from the first approved node
                    for nclass, nnodes in nodesCache:                    
                        for nnode in nnodes:
                            if 0: assert isinstance(nnode, ClassData)
                            if (((flow.src_addr & nnode.src_mask) == nnode.src_ip) and \
                                ((flow.dst_addr & nnode.dst_mask) == nnode.dst_ip) and \
                                ((flow.next_hop == nnode.next_hop) or (not nnode.next_hop)) and \
                                ((flow.src_port == nnode.src_port) or (not nnode.src_port)) and \
                                ((flow.dst_port == nnode.dst_port) or (not nnode.dst_port)) and \
                                ((flow.protocol == nnode.protocol) or (not nnode.protocol))):
                                
                                if not classLst:
                                    fnode = nnode
                                elif nnode.direction != fnode.direction:
                                    continue
                                classLst.append(nclass)
                                if not nnode.passthrough:
                                    passthr = False
                                break
                        #found passthrough=false
                        if not passthr:
                            self.add_classes_groups(flow, classLst, fnode, acctf_id, has_groups, tarifGroups)
                            break                   
                    #traversed all the nodes
                    else:
                        if classLst:
                            self.add_classes_groups(flow, classLst, fnode, acctf_id, has_groups, tarifGroups)
                        else: continue
                        
                    #construct a list
                    flst.append(tuple(flow)); fcnt += 1                    
                    #append to databaseQueue
                    if fcnt == 37:
                        with queues.dbLock:
                            queues.databaseQueue.append(flst)
                        flst = []; fcnt = 0
                if len(flst) > 0:
                    with queues.dbLock:
                        queues.databaseQueue.append(flst)
                    flst = []
                del keylist
            except Exception, ex:
                    logger.error("fdqThread exception: %s", repr(ex))
            
            
class NfUDPSenderThread(Thread):
    '''Thread that gets packet lists from databaseQueue, marshals them and sends to Core module
    If there are errors, flow data are written to a file. When connection is established again, NfFileReadThread to clean up that files and resend data is started.
    '''
    def __init__(self): 
        self.tname = self.__class__.__name__
        self.outbuf = []
        self.hpath = ''.join((vars.dumpDir,'/','nf_'))
        Thread.__init__(self)
        
    def run(self):
        addrport = vars.clientAddr
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        nfsock.settimeout(vars.sockTimeout)
        errflag, flnumpack = 0, 0
        dfile, fname = None, None
        while True:     
            try:
                if suicideCondition[self.tname]:
                    if errflag: dfile.close(); queues.fnameQueue.append(fname)
                    break
                #get a bunch of packets
                fpacket = None
                queues.dbLock.acquire()
                try:     fpacket = databaseQueue.popleft()
                except:  pass
                finally: queues.dbLock.release()
                if not fpacket: time.sleep(5); continue
                
                flst = marshal.dumps(fpacket)
                #send data
                nfsock.sendto(flst,addrport)
                #recover reply
                dtrc, addr = nfsock.recvfrom(128)
                #if wrong length (probably zero reply) - raise exception
                if dtrc is None: raise Exception("Empty!")
                
                if dtrc[:4] == 'SLP!':
                    logger.lprint("sleepFlag detected!")
                    time.sleep(10); continue
                
                if (len(flst) != int(dtrc)): raise Exception("Sizes not equal!")
                
                #if the connection is OK but there were errors earlier
                if errflag:
                    logger.info('%s errflag detected - time %d', (self.getName(), time.time()))
                    dfile.close()
                    with queues.fnameLock: queues.fnameQueue.append(fname)
                    #clear errflag
                    errflag = 0
                    
            except Exception, ex:
                logger.debug('%s exp: %s \n %s', (self.getName(), repr(ex), traceback.format_exc()))
                #if no errors were detected earlier
                if not errflag:
                    try:
                        errflag = 1                        
                        #open a new file
                        fname = ''.join((self.hpath, str(time.time()), '_', str(random.random()), '.dmp'))
                        dfile = open(fname, 'ab')
                        logger.info('%s: opened a new file: %s', (self.getName(), fname))
                    except Exception, ex:
                        logger.error("%s file creation exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        continue
                try:   
                    #append data
                    dfile.write(flst); dfile.write('!FLW')
                    flnumpack += 1
                    #if got enough packets - open a new file
                    if flnumpack == 300:
                        flnumpack = 0
                        dfile.close()
                        with queues.fnameLock: queues.fnameQueue.append(fname)
                        fname = ''.join((self.hpath, str(time.time()), '_', str(random.random()), '.dmp'))
                        dfile = open(fname, 'ab')
                except Exception, ex:
                        logger.error("%s file write exception: %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                        continue
            del flst
            
class NfFileReadThread(Thread):
    '''Thread that reads previously written data dumps and resends data.'''
    def __init__(self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        self.hpath  = ''.join((vars.dumpDir,'/','nf_'))
    
    def run(self):
        addrport = vars.clientAddr
        nfsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        nfsock.settimeout(vars.sockTimeout)
        fname, dfile = None, None
        while True:
            try:
                if suicideCondition[self.tname]: break
                
                #get a file name from a queue
                fname = None
                queues.fnameLock.acquire()
                try:     fname = queues.fnameQueue.popleft()
                except:  pass
                finally: queues.fnameLock.release()
                if not fname: time.sleep(240); continue
                #open the file
                dfile = open(fname, 'rb')
                #read flows
                flows = dfile.read()
                dfile.close()
                #create/open counter file
                fcname  = fname + 'c'
                flows  = flows.split('!FLW')[:-1]
                if not os.path.exists(fcname):
                    cfile = open(fcname, 'wb')
                else:
                    cfile = open(fcname, 'rb')
                    fwrt = len(cfile.read())
                    flows = flows[fwrt:]
                    cfile.close()
                    cfile = open(fcname, 'ab')
                    
                fcnt = 0
                try:
                    #send flows
                    for flow in flows:
                        nfsock.sendto(flow,addrport)                    
                        dtrc, addr = nfsock.recvfrom(128)
                        if dtrc is None: raise Exception("Empty!")
                
                        if dtrc[:4] == 'SLP!':
                            logger.lprint("NfFileReadThread: sleepFlag detected!")
                            time.sleep(10)
                    
                        elif (len(flow) != int(dtrc)):
                            raise Exception("Sizes not equal!")
                        
                        fcnt += 1; cfile.write('\n')
                        #flush every 4 packets
                        if fcnt % 4 == 0:
                            cfile.flush()
                        time.sleep(0.1)
                    cfile.close()
                    os.remove(fname); os.remove(fcname)
                    logger.info("NfFileReadThread: file processed: %s", (fname,))
                except Exception, ex:
                    #if errors - write data to another file
                    logger.error("NfFileReadThread flowsend exception: %s \n %s", (repr(ex),traceback.format_exc()))
                    dfile.close(); cfile.close()
                    #append file again
                    with queues.fnameLock: queues.fnameQueue.append(fname)
                    #run a cleanup thread
                    time.sleep(60)
                    continue 
            except Exception, ex:
                logger.error("NfFileReadThread fileread exception: %s \n %s", (repr(ex), traceback.format_exc()))
                with queues.fnameLock: queues.fnameQueue.append(fname)
                return                   
                           
                    
class ServiceThread(Thread):
    '''Thread that forms and renews caches.'''
    
    def __init__(self):
        Thread.__init__(self)
        self.tname = self.__class__.__name__
        
    def run(self):
        connection = pool.connection()
        connection._con._con.set_client_encoding('UTF8')
        global suicideCondition, cacheMaster, flags, queues
        counter = 0; now = datetime.datetime.now
        while True:
            if suicideCondition[self.__class__.__name__]: break
            a = time.clock()
            queues.nfFlowCache.reset()
            try: 
                time_run = (now() - cacheMaster.date).seconds > 300
                if flags.cacheFlag or time_run:
                    run_time = time.clock()                    
                    cur = connection.cursor()
                    renewCaches(cur)
                    cur.close()
                    if counter % 5 == 0 or time_run:
                        allowedUsersChecker(allowedUsers, lambda: len(cacheMaster.cache.account_cache.data)); counter = 0
                        flags.writeProf = logger.writeInfoP()
                        if flags.writeProf:
                            logger.info("len flowCache %s", len(queues.dcache))
                            logger.info("len flowQueue %s", len(queues.flowQueue))
                            logger.info("len dbQueue: %s", len(queues.databaseQueue))
                            logger.info("len fnameQueue: %s", len(queues.fnameQueue))
                            logger.info("len nfqueue: %s", len(queues.nfQueue))
                    counter += 1
                    if flags.cacheFlag:
                        with flags.cacheLock: flags.cacheFlag = False
                    
                    logger.info("ast time : %s", time.clock() - run_time)
            except Exception, ex:
                logger.error("%s : #30110004 : %s \n %s", (self.getName(), repr(ex), traceback.format_exc()))
                
            gc.collect()
            time.sleep(20)
    

class RecoveryThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global vars,queues
        try:
            fllist = glob.glob(''.join((vars.dumpDir, '/', 'nf_*.dmp')))
            if fllist:
                with queues.fnameLock:
                    for fl in fllist: queues.fnameQueue.appendleft(fl)
        except Exception, ex:
            logger.error("%s: exception: %s", (self.getName(),repr(ex)))  


def renewCaches(cur):
    ptime =  time.time()
    ptime = ptime - (ptime % 20)
    cacheDate = datetime.datetime.fromtimestamp(ptime)
    try:
        caches = NfCaches(cacheDate)
        caches.getdata(cur)
        cur.connection.commit()
        caches.reindex()
    except Exception, ex:
        if isinstance(ex, psycopg2.DatabaseError):
            logger.error('#30110001 renewCaches attempt failed due to database error: %s', repr(ex))
        else: 
            logger.error('#30110002 renewCaches attempt failed due to error: %s \n %s', (repr(ex), traceback.format_exc()))
    else:
        cacheMaster.read = True
            
    with cacheMaster.lock:
        cacheMaster.cache, cacheMaster.date = caches, cacheDate  
        
def SIGTERM_handler(signum, frame):
    graceful_save()

def SIGHUP_handler(signum, frame):
    config.read("ebs_config.ini")
    logger.setNewLevel(int(config.get("nf", "log_level")))

def SIGUSR1_handler(signum, frame):
    global flags
    logger.lprint("SIGUSR1 recieved")
    with flags.cacheLock: flags.cacheFlag = True
    
def graceful_save():
    global cacheThr, threads, suicideCondition
    #asyncore.close_all()
    
    suicideCondition[cacheThr.tname] = True
    for thr in threads:
            suicideCondition[thr.tname] = True
    time.sleep(10)
    
    graceful_saver([['dcache','nfFlowCache'], ['flowQueue'], ['databaseQueue']],
                   queues, 'nf_', saveDir)
    
    pool.close()
    time.sleep(2)
    sys.exit()
        
def graceful_recover():
    graceful_loader(['dcache','nfFlowCache','flowQueue','databaseQueue'],
                    queues, 'nf_', saveDir)
                
def main ():        
    global flags, queues, cacheMaster, threads, cacheThr, caches

    queues.nfFlowCache = FlowCache()
    graceful_recover()
    #recover leftover dumps?
    if flags.recover:
        recThr = RecoveryThread()
        recThr.setName('Recovery thread')
        recThr.start()
        time.sleep(0.5)
        
    threads = []
    thrnames = [(NfFileReadThread, 'NfFileReadThread'), (NfUDPSenderThread, 'NfUDPSenderThread'), \
                (FlowDequeThread, 'NfFlowDequeThread'), (nfDequeThread, 'nfDequeThread')]
    
    for thClass, thName in thrnames:
        threads.append(thClass())
        threads[-1].setName(thName)

    #-----
    cacheThr = ServiceThread()
    suicideCondition[cacheThr.__class__.__name__] = False
    cacheThr.setName('NfCacheThread')
    cacheThr.start()
    
    #sleep until all caches are read
    while not cacheMaster.date:
        time.sleep(0.2)
        if not cacheThr.isAlive:
            sys.exit()
    if 0: assert isinstance(cacheMaster.cache, NfCaches)  
    for th in threads:
        suicideCondition[th.__class__.__name__] = False
        th.start()
        time.sleep(0.5)
        
    try:
        signal.signal(signal.SIGTERM, SIGTERM_handler)
    except: logger.lprint('NO SIGTERM!')
    try:
        signal.signal(signal.SIGHUP, SIGHUP_handler)
    except: logger.lprint('NO SIGHUP!')
    try:
        signal.signal(signal.SIGUSR1, SIGUSR1_handler)
    except: logger.lprint('NO SIGUSR1!')

    reactor.listenUDP(int(config.get("nf", "port")), Reception())
    print "ebs: nf: started"
    reactor.run()


if __name__=='__main__':
    if "-D" in sys.argv:
        daemonize("/dev/null", "log.txt", "log.txt")
        
    flags = NfFlags()
    vars  = NfVars()
    queues= NfQueues()
    
    cacheMaster = CacheMaster()
    cacheMaster.date = None
    caches = None
    
    config = ConfigParser.ConfigParser()
    config.read("ebs_config.ini")
    
    logger = isdlogger.isdlogger(config.get("nf", "log_type"), loglevel=int(config.get("nf", "log_level")), ident=config.get("nf", "log_ident"), filename=config.get("nf", "log_file")) 
    saver.log_adapt = logger.log_adapt
    logger.lprint('Nf start')
    
    try:
        #write profiling info predicate
        flags.writeProf = logger.writeInfoP()
        
        pool = PooledDB(
        mincached=1,  maxcached=9,
        blocking=True,creator=psycopg2,
        dsn="dbname='%s' user='%s' host='%s' password='%s'" % (config.get("db", "name"), config.get("db", "username"),
                                                               config.get("db", "host"), config.get("db", "password")))
    
            
        #get socket parameters. AF_UNIX support
        if config.get("nfroutine_nf", "usock") == '0':
            vars.clientHost = config.get("nfroutine_nf_inet", "host")
            vars.clientPort = int(config.get("nfroutine_nf_inet", "port"))
            vars.clientAddr = (coreHost, corePort)
            
        elif config.get("nfroutine_nf", "usock") == '1':
            vars.clientHost = config.get("nfroutine_nf_unix", "host")
            vars.clientPort = 0
            vars.clientAddr = (coreHost,)
        else:
            raise Exception("Config '[nfroutine_nf] -> usock' value is wrong, must be 0 or 1")
        
        
        flags.recover    = (config.get("nfroutine_nf", "recover") == '1')
        flags.recoverAtt = (config.get("nfroutine_nf", "recoverAttempted") == '1')   
        flags.checkClasses = (config.get("nf", "checkclasses") == '1')
        
        vars.sockTimeout = float(config.get("nfroutine_nf", "sock_timeout"))
        vars.saveDir = config.get("nf", "save_dir")       
        #get a dump' directrory string and check whethet it's writable
        vars.dumpDir = config.get("nfroutine_nf", "dump_dir")
        try:
            tfname = ''.join((vars.dumpDir,'/','nf_', str(time.time()), '.dmp'))
            dfile = open(tfname, 'wb')
            dfile.write("testtesttesttesttest")
            dfile.close()
            os.remove(tfname)
        except Exception, ex:
            raise Exception("Dump directory '"+ vars.dumpDir+ "' is not accesible/writable: errors were encountered upun executing test operations with filenames like '" +tfname+ "'!")
    
        suicideCondition = {}    
        vars.FLOW_TYPES = {5 : (header5, flow5)}        
        #numeric values
        try:
            vars.aggrTime  = float(config.get("nf", "aggrtime"))
            vars.aggrNum   = float(config.get("nf", "aggrnum"))
        except Exception, ex: logger.info('numeric values ex %s', repr(ex)); print ex
        
        allowedUsers = setAllowedUsers(pool.connection(), "license.lic")        
        allowedUsers()
        test_now = time.time()
        #-------------------
        print "ebs: nf: configs read, about to start"
        main()
    except Exception, ex:
        print 'Exception in nf, exiting: ', repr(ex)
        logger.error('Exception in nf, exiting: %s \n %s', (repr(ex), traceback.format_exc()))
    
    
    
