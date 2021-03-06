#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui

from ebsWindow import ebsTableWindow
from helpers import tableFormat
from db import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from helpers import connlogin
from helpers import HeaderUtil
from helpers import humanable_bytes
from helpers import Worker
from helpers import prntime
from AccountEditFrame import AccountWindow
import time
import datetime
from customwidget import CustomDateTimeWidget

#from helpers import GenericThread
        #return
  
class MonitorEbs(ebsTableWindow):
    def __init__(self, connection, parent):
        columns=[u'#', u'Аккаунт',u"Субаккаунт", u"Баланс", u"Кредит", u'Caller ID', 'VPN IP', u'Сервер доступа', u'Способ доступа', u'Начало', u'Конец', u'Передано', u'Принято', u'Длительность, с', u'Статус', u'Причина разрыва']
        initargs = {"setname":"monitor_frame_header", "objname":"MonitorEbsMDI", "winsize":(0,0,1102,593), "wintitle":"Монитор активности", "tablecolumns":columns, "tablesize":(0,0,801,541)}
        super(MonitorEbs, self).__init__(connection, initargs)
        self.parent=parent
        
    def ebsPreInit(self, initargs):
        self.thread = Worker()
        self.selected_user=None
        
    def ebsInterInit(self, initargs):
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.userCombobox = QtGui.QComboBox()
        self.userCombobox.setGeometry(QtCore.QRect(100,12,201,20))
        self.user_label = QtGui.QLabel(u" Пользователь  ")
        self.allTimeCheckbox = QtGui.QCheckBox(u"Включая завершённые")
        
        self.checkBoxAutoRefresh = QtGui.QCheckBox(u"Автоматически обновлять")
        
        self.menubar = QtGui.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0,0,802,21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        self.pushbutton = QtGui.QPushButton()
        self.pushbutton.setText(u"Обновить")
        
        self.date_start_label = QtGui.QLabel(self)
        self.date_start_label.setMargin(10)
        self.date_start_label.setObjectName("date_start_label")

        self.date_end_label = QtGui.QLabel(self)
        self.date_end_label.setMargin(10)
        self.date_end_label.setObjectName("date_end_label")
        
        dt_now = datetime.datetime.now()
        
        self.date_start = CustomDateTimeWidget()
        #self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        #self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")
        #self.date_start.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        self.date_end = CustomDateTimeWidget()
        #self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setDate(QtCore.QDate(dt_now.year, dt_now.month, dt_now.day))
        #self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        #self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")
        
        
        #self.date_end.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)

        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.date_start.setDateTime(settings.value("monitor_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("monitor_date_end", QtCore.QVariant(QtCore.QDateTime(2099,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Monitor settings error: ", ex
            
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        
        self.toolBar.addWidget(self.user_label)
        self.toolBar.addWidget(self.userCombobox)
        self.toolBar.addWidget(self.date_start_label)
        self.toolBar.addWidget(self.date_start)
        self.toolBar.addWidget(self.date_end_label)
        self.toolBar.addWidget(self.date_end)

        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.allTimeCheckbox)
        self.toolBar.addWidget(self.checkBoxAutoRefresh)
        self.toolBar.addWidget(self.pushbutton)
        
        QtCore.QObject.connect(self.pushbutton, QtCore.SIGNAL("clicked()"), self.fixtures)        
        QtCore.QObject.connect(self.checkBoxAutoRefresh, QtCore.SIGNAL("stateChanged(int)"), self.autorefresh_state)
        self.connect(self.thread, QtCore.SIGNAL("refresh()"), self.fixtures)
        self.connect(self, QtCore.SIGNAL("refresh()"), self.fixtures)
        self.refresh_users()
        #???Проверить нужно лиQtCore.QObject.connect(self.userCombobox, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.fixtures)

        
    
    def ebsPostInit(self, initargs):
        actList=[("actionResetSession", "Сбросить сессию", "images/del.png", self.reset_action)]
        objDict = {self.tableWidget:["actionResetSession"]}
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editframe)
        self.date_start_label.setText(QtGui.QApplication.translate("Dialog", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.date_end_label.setText(QtGui.QApplication.translate("Dialog", "По", None, QtGui.QApplication.UnicodeUTF8))
        
        self.actionCreator(actList, objDict)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.emit(QtCore.SIGNAL("refresh()"))
        
    def retranslateUI(self, initargs):
        super(MonitorEbs, self).retranslateUI(initargs)
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
    def autorefresh_state(self):
        """
        Метод, стартующий трэд, эмитирующий в родительское окно сигнал refresh()
        """
        if self.checkBoxAutoRefresh.checkState()==2:
            self.thread.go(interval=25)
        else:
            self.thread.terminate()
            
    def closeEvent(self, event):
        """
        Terminate thread
        """
        self.thread.terminate()
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("monitor_date_start", QtCore.QVariant(self.date_start.dateTime()))
            settings.setValue("monitor_date_end", QtCore.QVariant(self.date_end.dateTime()))
        except Exception, ex:
            print "Monitor settings save error: ", ex
            
        event.accept()

    def addrow(self, widget, value, x, y, color=False, id=None, sessionid=None, account_id=None):
        
        item_type = QtGui.QTableWidgetItem()
        if value==None:
            value=''

        text=value

        if color and y==3:
            #print value
            if float(value)<0:
                item_type.setBackgroundColor(QtGui.QColor("red"))
                item_type.setTextColor(QtGui.QColor('#ffffff'))
            elif float(value)==0:
                item_type.setBackgroundColor(QtGui.QColor("#ffdc51"))
                        
        if widget.item(x,y):
            widget.item(x,y).setText(unicode(text))
        else:
            item_type.setText(unicode(text))
            widget.setItem(x, y, item_type)
        if y==1:
            item_type.setIcon(QtGui.QIcon("images/user.png"))
        if y==0:
            item_type.account_id=account_id
            
        if id:
            item_type.id = id
            
        if sessionid:
            item_type.sessionid = sessionid
            
        if color:
            if value=='ACTIVE':
                item_type.setBackgroundColor(QtGui.QColor('green'))
                item_type.setTextColor(QtGui.QColor('#ffffff'))
            elif value=='ACK':
                item_type.setBackgroundColor(QtGui.QColor('#4d4d4d'))
                item_type.setTextColor(QtGui.QColor('#ffffff'))
            elif value=='NACK':
                item_type.setBackgroundColor(QtGui.QColor('#e8ff6a'))
                item_type.setTextColor(QtGui.QColor('#000000'))
        
    def reset_action(self):
        try:
            sessionid = unicode(self.tableWidget.item(self.tableWidget.currentRow(), 0).sessionid)
            id = unicode(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
            self.connection.pod(session=sessionid, id=id)
        except:
            pass

        
    def fixtures(self, user=None):
        self.statusBar().showMessage(u"Идёт получение данных")
        self.tableWidget.setRowCount(0)
        self.tableWidget.clearContents()
        self.tableWidget.setSortingEnabled(False)
        date_start = self.date_start.currentDate()
        date_end = self.date_end.currentDate()
        self.statusBar().showMessage(u"Ожидание ответа")

        only_active = True if self.allTimeCheckbox.checkState()==QtCore.Qt.Unchecked else False 
        print 'only_active', only_active
        sessions = self.connection.get_sessions(account_id=user, only_active = only_active, date_start=date_start, date_end=date_end)
        print "fot sessions", len(sessions)
        i=0        
        sess_time = 0
        self.tableWidget.setRowCount(len(sessions))        
        self.tableWidget.setSortingEnabled(False)
        ("id","sessionid","account__username","account__id","subaccount__username", "account__ballance", "account__credit", "caller_id", "framed_ip_address", "nas_int_id__name", "framed_protocol", "date_start", "date_end", "bytes_out", "bytes_in", "session_time", "session_status","acct_terminate_cause")
        for session in sessions:
            if session.date_end==None:
                date_end=""
            else:
                date_end = session.date_end.strftime(self.strftimeFormat)
            #print session.id
            self.addrow(self.tableWidget, session.sessionid, i, 0, id=session.id, sessionid = session.sessionid, account_id=session.account__id)
            self.addrow(self.tableWidget, session.account__username, i, 1)
            self.addrow(self.tableWidget, session.subaccount__username, i, 2)
            self.addrow(self.tableWidget, "%.2f" % session.account__ballance, i, 3, color=True)
            self.addrow(self.tableWidget, session.account__credit, i, 4)
            self.addrow(self.tableWidget, session.caller_id, i, 5)
            self.addrow(self.tableWidget, session.framed_ip_address, i, 6)
            self.addrow(self.tableWidget, session.nas_int_id__name, i, 7)
            self.addrow(self.tableWidget, session.framed_protocol, i, 8)
            self.addrow(self.tableWidget, session.date_start.strftime(self.strftimeFormat), i, 9)
            self.addrow(self.tableWidget, date_end, i, 10)
            self.addrow(self.tableWidget, humanable_bytes(session.bytes_out), i, 11)
            self.addrow(self.tableWidget, humanable_bytes(session.bytes_in), i, 12)
            self.addrow(self.tableWidget, prntime(session.session_time), i, 13)
            self.addrow(self.tableWidget, session.session_status, i, 14, color=True)
            self.addrow(self.tableWidget, session.acct_terminate_cause, i, 15)
            sess_time += float(session.session_time) if float(session.session_time) else 0
            i+=1
        if self.firsttime and sessions and HeaderUtil.getBinaryHeader("monitor_frame_header").isEmpty():
            self.tableWidget.resizeColumnsToContents()
            self.firsttime = False
        else:
            if sessions:
                HeaderUtil.getHeader("monitor_frame_header", self.tableWidget)
        self.statusBar().showMessage(u'Сессий:%s. Среднее время сессии: %s минут' % (len(sessions), (sess_time/(1 if len(sessions)==0 else len(sessions))/60)))
        self.tableWidget.setColumnHidden(0, False)
        self.tableWidget.setSortingEnabled(True)
        #self.tableWidget.setSortingEnabled(True)

        
                
    def refresh_users(self):
        if self.selected_user is None:
            self.userCombobox.addItem('---')
            users = self.connection.get_account(fields=['id', 'username'])
            self.connection.commit()
            if users==None:
                users=[]
            for user in users:
                self.userCombobox.addItem(unicode(user.username), user.id)
                
    def refresh(self):
        pass
        #self.fixtures()
        #self.emit(QtCore.SIGNAL("refresh()"))
        
        
    @connlogin
    def editframe(self, *args, **kwargs):
        #print self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
        id=self.getSelectedId()
        #print id
        if id == 0:
            return
        try:
            model = self.connection.get_account(id)
        except Exception, e:
            print e
            return
        #print 'model', model

        

        #addf = AddAccountFrame(connection=self.connection,tarif_id=self.getTarifId(), ttype=tarif_type, model=model, ipn_for_vpn=ipn_for_vpn)
        child = AccountWindow(connection=self.connection,tarif_id=None, ttype=None, model=model)
        
        self.parent.workspace.addWindow(child)
        self.connect(child, QtCore.SIGNAL("refresh()"), self.refresh)
        child.show()
        return
    
    def getSelectedId(self):
        return self.tableWidget.item(self.tableWidget.currentRow(), 0).account_id
    
    