
nf_sql = {'nas':"SELECT ipaddress, id from nas_nas;",
          'accounts':"SELECT ba.id as account_id,ba.vpn_ip_address,ba.ipn_ip_address, bacct.id as acctf_id, bacct.tarif_id FROM billservice_account AS ba JOIN billservice_accounttarif AS bacct ON bacct.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1);",
          'nnodes':"SELECT weight, traffic_class_id, store, direction, passthrough, protocol, dst_port, src_port, src_ip as src_ip_src_mask, dst_ip as dst_ip_dst_mask, next_hop FROM nas_trafficnode AS tn JOIN nas_trafficclass AS tc ON tn.traffic_class_id=tc.id ORDER BY tc.weight, tc.passthrough;",
          'groups':"SELECT id, ARRAY(SELECT trafficclass_id from billservice_group_trafficclass as bgtc WHERE bgtc.group_id = bsg.id) AS trafficclass, direction, type FROM billservice_group AS bsg;",
          'tgroups':"SELECT tarif_id, int_array_aggregate(group_id) AS group_ids FROM (SELECT tarif_id, group_id FROM billservice_trafficlimit UNION SELECT bt.id, btn.group_id FROM billservice_tariff AS bt JOIN billservice_traffictransmitnodes AS btn ON bt.traffic_transmit_service_id=btn.traffic_transmit_service_id WHERE btn.group_id IS NOT NULL UNION SELECT bt.id, bpt.group_id FROM billservice_tariff AS bt JOIN billservice_prepaidtraffic AS bpt ON bt.traffic_transmit_service_id=bpt.traffic_transmit_service_id WHERE bpt.group_id IS NOT NULL) AS tarif_group GROUP BY tarif_id;"}

nfroutine_sql = \
              {'accounts':"""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, ba.status   
                                FROM billservice_account as ba
                                LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                                LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id;""",
               'tts'     :"""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""",
               'settlepd':"""SELECT id, time_start, length, length_in, autostart FROM billservice_settlementperiod;""",
               'period'  :"""SELECT tpn.time_start, tpn.length, tpn.repeat_after, ttns.traffic_transmit_service_id
                                FROM billservice_timeperiodnode AS tpn
                                JOIN billservice_timeperiod_time_period_nodes AS timeperiod_timenodes ON timeperiod_timenodes.timeperiodnode_id=tpn.id
                                JOIN billservice_traffictransmitnodes_time_nodes AS ttntp ON ttntp.timeperiod_id=timeperiod_timenodes.timeperiod_id
                                JOIN billservice_traffictransmitnodes AS ttns ON ttns.id=ttntp.traffictransmitnodes_id;""",
               'nodes'   :"""SELECT ttsn.id, ttsn.cost, ttsn.edge_start, ttsn.edge_end, tpn.time_start, tpn.length, tpn.repeat_after,
                                        ttsn.group_id, ttsn.traffic_transmit_service_id 
                                        FROM billservice_traffictransmitnodes as ttsn
                                        JOIN billservice_timeperiodnode AS tpn on tpn.id IN 
                                        (SELECT timeperiodnode_id FROM billservice_timeperiod_time_period_nodes WHERE timeperiod_id IN 
                                        (SELECT timeperiod_id FROM billservice_traffictransmitnodes_time_nodes WHERE traffictransmitnodes_id=ttsn.id));""",
               'prepays' :"""SELECT prepais.id, prepais.size, prepais.account_tarif_id, prepaidtraffic.group_id, prepaidtraffic.traffic_transmit_service_id 
                                        FROM billservice_accountprepaystrafic as prepais
                                        JOIN billservice_prepaidtraffic as prepaidtraffic ON prepaidtraffic.id=prepais.prepaid_traffic_id
                                        WHERE prepais.size>0 AND (ARRAY[prepais.account_tarif_id] && get_cur_acct(%s));""",
               'sclasses':"""SELECT int_array_aggregate(id) FROM nas_trafficclass WHERE FALSE=TRUE;"""}

core_sql = \
         {'accounts':"""SELECT ba.id, ba.ballance, ba.credit, act.datetime, bt.id, bt.access_parameters_id, bt.time_access_service_id, bt.traffic_transmit_service_id, bt.cost,bt.reset_tarif_cost, bt.settlement_period_id, bt.active, act.id, FALSE, ba.created, ba.disabled_by_limit, ba.balance_blocked, ba.nas_id, ba.vpn_ip_address, ba.ipn_ip_address,ba.ipn_mac_address, ba.assign_ipn_ip_from_dhcp, ba.ipn_status, ba.ipn_speed, ba.vpn_speed, ba.ipn_added, bt.ps_null_ballance_checkout, bt.deleted, bt.allow_express_pay, ba.status, ba.allow_vpn_null, ba.allow_vpn_block, ba.username, ba.password, bt.require_tarif_cost   
                        FROM billservice_account as ba
                        LEFT JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                        LEFT JOIN billservice_tariff AS bt ON bt.id=act.tarif_id WHERE bt.active;""",
          'traftrss':"""SELECT id, reset_traffic, cash_method, period_check FROM billservice_traffictransmitservice;""",
          'settlper':"""SELECT id, time_start, length, length_in, autostart FROM billservice_settlementperiod;""",
          'nas'     :"""SELECT id, type, name, ipaddress, secret, login, password, allow_pptp, allow_pppoe, allow_ipn, user_add_action, user_enable_action, user_disable_action, user_delete_action, vpn_speed_action, ipn_speed_action, reset_action, confstring, multilink FROM nas_nas;""",
          'defsp'   :"""SELECT accessparameters.max_limit,accessparameters.burst_limit,
                        accessparameters.burst_treshold, accessparameters.burst_time,
                        accessparameters.priority, accessparameters.min_limit,
                        tariff.id
                        FROM billservice_accessparameters as accessparameters
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id;""",
          'newsp'   :"""SELECT timespeed.max_limit,timespeed.burst_limit,
                        timespeed.burst_treshold,timespeed.burst_time,
                        timespeed.priority, timespeed.min_limit,
                        timenode.time_start, timenode.length, timenode.repeat_after,
                        tariff.id 
                        FROM billservice_timespeed as timespeed
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                        JOIN billservice_timeperiod_time_period_nodes as tp ON tp.timeperiod_id=timespeed.time_id
                        JOIN billservice_timeperiodnode as timenode ON tp.timeperiodnode_id=timenode.id;""",
          'periodtf':"""SELECT id, settlement_period_id FROM billservice_tariff  as tarif
                        WHERE id in (SELECT tarif_id FROM billservice_periodicalservice) AND tarif.active=True""",
          'periodset':"""SELECT b.id, b.name, b.cost, b.cash_method, c.name, c.time_start,
                        c.length, c.length_in, c.autostart, b.tarif_id, b.condition, b.created
                        FROM billservice_periodicalservice as b 
                        JOIN billservice_settlementperiod as c ON c.id=b.settlement_period_id;""",
          'timeaccnode':"""SELECT tan.time_period_id, tan.cost, tan.time_access_service_id
                        FROM billservice_timeaccessnode as tan
                        JOIN billservice_timeperiod as tp ON tan.time_period_id=tp.id;""",
          'timepnode':"""SELECT tpn.id, tpn.name, tpn.time_start, tpn.length, tpn.repeat_after, tptpn.timeperiod_id 
                        FROM billservice_timeperiodnode as tpn
                        JOIN billservice_timeperiod_time_period_nodes as tptpn ON tpn.id=tptpn.timeperiodnode_id;""",
          'tlimits'  :"""SELECT trafficlimit.id, trafficlimit.tarif_id, trafficlimit."name", 
                        trafficlimit.settlement_period_id, trafficlimit.size, trafficlimit.group_id, 
                        trafficlimit."mode", trafficlimit.action,
                        speedlimit.id
                        FROM billservice_trafficlimit as trafficlimit
                        LEFT JOIN billservice_speedlimit as speedlimit ON speedlimit.limit_id=trafficlimit.id
                        ORDER BY trafficlimit.size DESC;""",
          'shllog'  :"""SELECT id,account_id, ballance_checkout, prepaid_traffic_reset,prepaid_traffic_accrued, 
                        prepaid_time_reset, prepaid_time_accrued, balance_blocked, accounttarif_id 
                        FROM billservice_shedulelog;""",
          'timeaccs' :"""SELECT id, prepaid_time, reset_time FROM billservice_timeaccessservice;""",
          'onetimes' :"""SELECT id, tarif_id, cost FROM billservice_onetimeservice;""",
          'accpars'  :"""SELECT id, access_type, access_time_id, max_limit, min_limit, 
                        burst_limit,burst_treshold,burst_time, priority, ipn_for_vpn FROM billservice_accessparameters;""",
          'ipnspeed' :"""SELECT id, account_id, speed, state, static, datetime FROM billservice_accountipnspeed;""",
          'otshist'  :"""SELECT id, accounttarif_id, onetimeservice_id FROM billservice_onetimeservicehistory WHERE ARRAY[accounttarif_id] && get_cur_acct(%s);""", 
          'suspended':"""SELECT id, account_id FROM billservice_suspendedperiod WHERE (%s BETWEEN start_date AND end_date)""",
          'tpnaccess':"""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                        FROM billservice_timeperiodnode as tpn
                        JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                        JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                        JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id"""}
rad_sql = \
        {'accounts'  :"""SELECT ba.id, ba.username, ba.ipn_mac_address, bt.time_access_service_id, 
                        ba.password, ba.nas_id, ba.vpn_ip_address, bt.id, accps.access_type, 
                        ba.status, ba.balance_blocked, (ba.ballance+ba.credit) as ballance, 
                        ba.disabled_by_limit, ba.vpn_speed, bt.active, 
                        ba.allow_vpn_null, ba.allow_vpn_block, ba.ipn_ip_address, ba.netmask, ba.ipn_speed, ba.assign_dhcp_null, ba.assign_dhcp_block
                        FROM billservice_account as ba
                        JOIN billservice_accounttarif AS act ON act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=ba.id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)
                        JOIN billservice_tariff AS bt ON bt.id=act.tarif_id
                        LEFT JOIN billservice_accessparameters as accps on accps.id = bt.access_parameters_id ;""",
         'nas'      :"""SELECT id, secret, type, multilink, ipaddress FROM nas_nas;""",
         'period'   :"""SELECT tpn.time_start::timestamp without time zone as time_start, tpn.length as length, tpn.repeat_after as repeat_after, bst.id
                        FROM billservice_timeperiodnode as tpn
                        JOIN billservice_timeperiod_time_period_nodes as tpnds ON tpnds.timeperiodnode_id=tpn.id
                        JOIN billservice_accessparameters AS ap ON ap.access_time_id=tpnds.timeperiod_id
                        JOIN billservice_tariff AS bst ON bst.access_parameters_id=ap.id""",
         'defspeed' :"""SELECT accessparameters.max_limit,accessparameters.burst_limit,
                        accessparameters.burst_treshold, accessparameters.burst_time,
                        accessparameters.priority, accessparameters.min_limit,
                        tariff.id
                        FROM billservice_accessparameters as accessparameters
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=accessparameters.id;""",
         'speed'    :"""SELECT timespeed.max_limit,timespeed.burst_limit,
                        timespeed.burst_treshold,timespeed.burst_time,
                        timespeed.priority, timespeed.min_limit,
                        timenode.time_start, timenode.length, timenode.repeat_after,
                        tariff.id 
                        FROM billservice_timespeed as timespeed
                        JOIN billservice_tariff as tariff ON tariff.access_parameters_id=timespeed.access_parameters_id
                        JOIN billservice_timeperiod_time_period_nodes as tp ON tp.timeperiod_id=timespeed.time_id
                        JOIN billservice_timeperiodnode as timenode ON tp.timeperiodnode_id=timenode.id;""",
         'limit'    :"""SELECT speedlimit.max_tx, speedlimit.max_rx, 
                        speedlimit.burst_tx, speedlimit.burst_rx, 
                        speedlimit.burst_treshold_tx, speedlimit.burst_treshold_rx, 
                        speedlimit.burst_time_tx, speedlimit.burst_time_rx, 
                        speedlimit.priority,
                        speedlimit.min_tx, speedlimit.min_rx, accountspeedlimit.account_id
                        FROM billservice_speedlimit as speedlimit, billservice_accountspeedlimit as accountspeedlimit
                        WHERE accountspeedlimit.speedlimit_id=speedlimit.id;""",
         'attrs'    :"""SELECT vendor, attrid, value, tarif_id FROM billservice_radiusattrs;"""}