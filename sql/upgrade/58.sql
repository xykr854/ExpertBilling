CREATE OR REPLACE FUNCTION get_tarif(acc_id integer, dt timestamp without time zone)
  RETURNS integer AS
  $BODY$
  declare
  xxx int;
  begin
  SELECT tarif_id INTO xxx
    FROM billservice_accounttarif WHERE account_id=acc_id and datetime<dt ORDER BY datetime DESC LIMIT 1;
    RETURN xxx;
    end;
    $BODY$
      LANGUAGE plpgsql VOLATILE
        COST 100;
        
DROP VIEW IF EXISTS billservice_totaltransactionreport;
DROP VIEW IF EXISTS billservice_totaltransactionreport;
CREATE OR REPLACE VIEW billservice_totaltransactionreport(id, service_id, service_name, created,tariff_id,summ,account_id,type_id,systemuser_id,bill,descrition,end_promise, promise_expired) AS
SELECT psh.id, 
	psh.service_id,
	(SELECT name FROM billservice_periodicalservice WHERE id=psh.service_id) as name, 
	psh.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=psh.accounttarif_id) as tarif,
	psh.summ, 
	(SELECT username FROM billservice_account WHERE id=psh.account_id) as username,
	psh.type_id, 
	'','','',Null,Null
FROM billservice_periodicalservicehistory as psh
UNION
SELECT transaction.id,
	NULL,
	'', 
	transaction.created,  
	(SELECT tarif_id FROM billservice_accounttarif where id=transaction.accounttarif_id) as tarif,
	transaction.summ*(-1),
	(SELECT username FROM billservice_account WHERE id=transaction.account_id) as username, 
	transaction.type_id as type,
	(SELECT username FROM billservice_systemuser WHERE id=transaction.systemuser_id) as systemuser,
	transaction.bill,transaction.description,end_promise,promise_expired
FROM billservice_transaction as transaction
UNION
SELECT tr.id, 
	NULL,
	'', 
	tr.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=tr.accounttarif_id) as tarif, 
	tr.summ, (SELECT username FROM billservice_account WHERE id=tr.account_id) as username ,
	'NETFLOW_BILL',
	'','','',Null,Null
FROM billservice_traffictransaction as tr
UNION
SELECT addst.id, 
	addst.service_id,
	(SELECT name FROM billservice_addonservice WHERE id=addst.service_id) as name, 
	addst.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=addst.accounttarif_id) as tarif,
	addst.summ,
	(SELECT username FROM billservice_account WHERE id=addst.account_id)
	as username,addst.type_id,
	'','','',Null,Null
FROM billservice_addonservicetransaction as addst
UNION
SELECT osh.id, 
	osh.onetimeservice_id,
	(SELECT name FROM billservice_onetimeservice WHERE id=osh.onetimeservice_id) as name, 
        osh.created,
        (SELECT tarif_id FROM billservice_accounttarif where id=osh.accounttarif_id) as tarif,
        osh.summ, 
        (SELECT username FROM billservice_account WHERE id=osh.account_id) as username, 
        'ONETIME_SERVICE','','','',Null,Null
            FROM billservice_onetimeservicehistory as osh 
UNION
SELECT tr.id, 
	NULL,
	'', 
	tr.created, 
	(SELECT tarif_id FROM billservice_accounttarif where id=tr.accounttarif_id) as tarif,
	tr.summ, 
	(SELECT username FROM billservice_account WHERE id=tr.account_id) as username, 
	'TIME_ACCESS','','','',Null,Null
            FROM billservice_timetransaction as tr 
UNION
SELECT qi.id as id, 
	NULL,
	'',
	qi.created,
	get_tarif(qi.account_id,qi.created) as tarif,
	qi.summ,
	(SELECT username FROM billservice_account WHERE id=qi.account_id) as username,
	'QIWI_PAYMENT','',qi.autoaccept::text, qi.date_accepted::text ,Null,Null
            FROM qiwi_invoice as qi            
ORDER BY 2;
