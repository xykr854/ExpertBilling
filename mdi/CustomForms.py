#-*-coding=utf-8-*-

import os, sys
from PyQt4 import QtCore, QtGui, QtSql, QtWebKit
#from Reports import TransactionsReport
from helpers import makeHeaders
from helpers import tableFormat
from helpers import tableHeight
from helpers import sqliteDbAccess, connectDBName , get_free_addreses_from_pool
from db import Object as Object
from db import AttrDict
from helpers import dateDelim, settlement_period_info
from mako.template import Template
from template_higlight import Highlighter
import time
from customwidget import CustomDateTimeWidget
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
import datetime
from decimal import Decimal
from PyQt4.QtNetwork import QNetworkCookie, QNetworkAccessManager, QNetworkReply
from PyQt4.QtNetwork import QNetworkCookieJar, QNetworkRequest
from PyQt4.QtWebKit import QWebPage

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class RRDPropertiesDialog(QtGui.QDialog):
    def __init__(self, connection, report_type):
        super(RRDPropertiesDialog, self).__init__()
        self.connection=connection
        self.report_type=report_type
        self.item_ids=[]
        self.request_params = ''
        self.setObjectName(_fromUtf8("self"))
        self.resize(557, 507)
        self.gridLayout_3 = QtGui.QGridLayout(self)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox_period = QtGui.QGroupBox(self)
        self.groupBox_period.setObjectName(_fromUtf8("groupBox_period"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_period)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_last = QtGui.QLabel(self.groupBox_period)
        self.label_last.setObjectName(_fromUtf8("label_last"))
        self.gridLayout_2.addWidget(self.label_last, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkBox_day = QtGui.QCheckBox(self.groupBox_period)
        self.checkBox_day.setObjectName(_fromUtf8("checkBox_day"))
        self.horizontalLayout.addWidget(self.checkBox_day)
        self.checkBox_week = QtGui.QCheckBox(self.groupBox_period)
        self.checkBox_week.setObjectName(_fromUtf8("checkBox_week"))
        self.horizontalLayout.addWidget(self.checkBox_week)
        self.checkBox_month = QtGui.QCheckBox(self.groupBox_period)
        self.checkBox_month.setObjectName(_fromUtf8("checkBox_month"))
        self.horizontalLayout.addWidget(self.checkBox_month)
        self.checkBox_year = QtGui.QCheckBox(self.groupBox_period)
        self.checkBox_year.setObjectName(_fromUtf8("checkBox_year"))
        self.horizontalLayout.addWidget(self.checkBox_year)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 3, 1, 3)
        self.label_or = QtGui.QLabel(self.groupBox_period)
        self.label_or.setObjectName(_fromUtf8("label_or"))
        self.gridLayout_2.addWidget(self.label_or, 1, 3, 1, 1)
        self.dateTimeEdit_from_period = CustomDateTimeWidget()
        self.dateTimeEdit_from_period.setCalendarPopup(True)
        self.dateTimeEdit_from_period.setObjectName(_fromUtf8("dateTimeEdit_from_period"))
        self.gridLayout_2.addWidget(self.dateTimeEdit_from_period, 2, 3, 1, 1)
        self.label_to = QtGui.QLabel(self.groupBox_period)
        self.label_to.setObjectName(_fromUtf8("label_to"))
        self.gridLayout_2.addWidget(self.label_to, 2, 4, 1, 1)
        self.dateTimeEdit_to_period = CustomDateTimeWidget()
        self.dateTimeEdit_to_period.setCalendarPopup(True)
        self.dateTimeEdit_to_period.setObjectName(_fromUtf8("dateTimeEdit_to_period"))
        self.gridLayout_2.addWidget(self.dateTimeEdit_to_period, 2, 5, 1, 1)
        self.label_from_period = QtGui.QLabel(self.groupBox_period)
        self.label_from_period.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_from_period.setObjectName(_fromUtf8("label_from_period"))
        self.gridLayout_2.addWidget(self.label_from_period, 2, 2, 1, 1)
        self.radioButton_for_period = QtGui.QRadioButton(self.groupBox_period)
        self.radioButton_for_period.setText(_fromUtf8(""))
        self.radioButton_for_period.setObjectName(_fromUtf8("radioButton_for_period"))
        self.gridLayout_2.addWidget(self.radioButton_for_period, 2, 1, 1, 1)
        self.radioButton_for_last = QtGui.QRadioButton(self.groupBox_period)
        self.radioButton_for_last.setText(_fromUtf8(""))
        self.radioButton_for_last.setChecked(True)
        self.radioButton_for_last.setObjectName(_fromUtf8("radioButton_for_last"))
        self.gridLayout_2.addWidget(self.radioButton_for_last, 0, 1, 1, 1)
        self.label_period = QtGui.QLabel(self.groupBox_period)
        self.label_period.setObjectName(_fromUtf8("label_period"))
        self.gridLayout_2.addWidget(self.label_period, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 6, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_period, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.groupBox_select = QtGui.QGroupBox(self)
        self.groupBox_select.setObjectName(_fromUtf8("groupBox_select"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_select)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_select_all = QtGui.QLabel(self.groupBox_select)
        self.label_select_all.setObjectName(_fromUtf8("label_select_all"))
        self.verticalLayout.addWidget(self.label_select_all)
        self.listWidget_all = QtGui.QListWidget(self.groupBox_select)
        self.listWidget_all.setObjectName(_fromUtf8("listWidget_all"))
        self.listWidget_all.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.verticalLayout.addWidget(self.listWidget_all)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 4, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 117, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_select_selected = QtGui.QLabel(self.groupBox_select)
        self.label_select_selected.setObjectName(_fromUtf8("label_select_selected"))
        self.verticalLayout_2.addWidget(self.label_select_selected)
        self.listWidget_selected = QtGui.QListWidget(self.groupBox_select)
        self.listWidget_selected.setObjectName(_fromUtf8("listWidget_selected"))
        self.listWidget_selected.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.verticalLayout_2.addWidget(self.listWidget_selected)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 2, 4, 1)
        self.toolButton_to_selected = QtGui.QToolButton(self.groupBox_select)
        self.toolButton_to_selected.setObjectName(_fromUtf8("toolButton_to_selected"))
        self.gridLayout.addWidget(self.toolButton_to_selected, 1, 1, 1, 1)
        self.toolButton_from_selected = QtGui.QToolButton(self.groupBox_select)
        self.toolButton_from_selected.setObjectName(_fromUtf8("toolButton_from_selected"))
        self.gridLayout.addWidget(self.toolButton_from_selected, 2, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 116, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_select, 1, 0, 1, 1)

        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.dateTimeEdit_from_period.setDateTime(settings.value("rrdreportprop_date_start", QtCore.QVariant(QtCore.QDateTime(2011,1,1,0,0))).toDateTime())
            self.dateTimeEdit_to_period.setDateTime(settings.value("rrdreportprop_date_end", QtCore.QVariant(QtCore.QDateTime(2012,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex
 
        self.fixtures()
        self.retranslateUi()
        self.periodLogic()
        QtCore.QObject.connect(self.toolButton_to_selected, QtCore.SIGNAL("clicked()"),self.addItem)
        QtCore.QObject.connect(self.toolButton_from_selected, QtCore.SIGNAL("clicked()"),self.delItem)

        QtCore.QObject.connect(self.listWidget_all, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.addItem)
        QtCore.QObject.connect(self.listWidget_selected, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"),self.delItem)        

        QtCore.QObject.connect(self.radioButton_for_last, QtCore.SIGNAL("clicked()"),self.periodLogic)
        QtCore.QObject.connect(self.radioButton_for_period, QtCore.SIGNAL("clicked()"),self.periodLogic)

        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("RRDPropertiesDialog", "Настройка отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_period.setTitle(QtGui.QApplication.translate("RRDPropertiesDialog", "Период", None, QtGui.QApplication.UnicodeUTF8))
        self.label_last.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "За последний", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_day.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "День", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_week.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "Неделя", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_month.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "Месяц", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_year.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "Год", None, QtGui.QApplication.UnicodeUTF8))
        self.label_or.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "или", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_from_period.setDisplayFormat(QtGui.QApplication.translate("RRDPropertiesDialog", "dd.MM.yy HH:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.label_to.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_to_period.setDisplayFormat(QtGui.QApplication.translate("RRDPropertiesDialog", "dd.MM.yy HH:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.label_from_period.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.label_period.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "За промежуток", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_select.setTitle(QtGui.QApplication.translate("RRDPropertiesDialog", "Выбор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_select_all.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "Все", None, QtGui.QApplication.UnicodeUTF8))
        self.label_select_selected.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "Выбранные", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_to_selected.setText(QtGui.QApplication.translate("RRDPropertiesDialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_from_selected.setText(QtGui.QApplication.translate("RRDPropertiesDialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        
    def fixtures(self):
        if self.report_type=='accounts':
            accounts = self.connection.get_account(fields=['id', 'username'],)
            self.connection.commit()
            for account in accounts:
                item = QtGui.QListWidgetItem()
                item.setText(account.username)
                item.id = account.id
                self.listWidget_all.addItem(item)
        elif self.report_type=='nasses':
            items = self.connection.get_nasses(fields=['id', 'name'])
            self.connection.commit()
            for item in items:
                litem = QtGui.QListWidgetItem()
                litem.setText(item.name)
                litem.id = item.id
                self.listWidget_all.addItem(litem)

    def addItem(self):
        selected_items = self.listWidget_all.selectedItems()
        
        for item in selected_items:
            self.listWidget_all.takeItem(self.listWidget_all.row(item))
            self.listWidget_selected.addItem(item)
            
        self.listWidget_selected.sortItems()
        
    def delItem(self):
        selected_items = self.listWidget_selected.selectedItems()
        
        for item in selected_items:
            self.listWidget_selected.takeItem(self.listWidget_selected.row(item))
            self.listWidget_all.addItem(item)
        self.listWidget_all.sortItems()
        
    def periodLogic(self):
        
        if self.radioButton_for_last.isChecked():
            self.dateTimeEdit_from_period.setDisabled(True)
            self.dateTimeEdit_to_period.setDisabled(True)
        else:
            self.dateTimeEdit_from_period.setDisabled(False)
            self.dateTimeEdit_to_period.setDisabled(False)
                        
    def accept(self):
        
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("rrdreportprop_date_start", QtCore.QVariant(self.dateTimeEdit_from_period.dateTime()))
            settings.setValue("rrdreportprop_date_end", QtCore.QVariant(self.dateTimeEdit_to_period.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex
        
        self.item_ids=[]
        for i in xrange(0, self.listWidget_selected.count()):
            self.item_ids.append(str(self.listWidget_selected.item(i).id))
            
        day = self.checkBox_day.isChecked()    
        week = self.checkBox_week.isChecked()
        month = self.checkBox_month.isChecked()
        year = self.checkBox_year.isChecked()
        
        date_start=self.dateTimeEdit_from_period.currentDate()
        date_end=self.dateTimeEdit_to_period.currentDate()
        #dt = 
    
        if self.report_type=='accounts':
            if self.radioButton_for_last.isChecked():
                self.request_params='/statistics/subaccount_filter/?items=%s&day=%s&week=%s&month=%s&year=%s' % (','.join(self.item_ids),day,week,month,year)
            else:
                self.request_params='/statistics/subaccount_period_filter/?items=%s&from=%s&to=%s' % (','.join(self.item_ids),time.mktime(date_start.timetuple()),time.mktime(date_end.timetuple()))
        elif self.report_type=='nasses':
            if self.radioButton_for_last.isChecked():
                self.request_params='/statistics/nasses_filter/?items=%s&day=%s&week=%s&month=%s&year=%s' % (','.join(self.item_ids),day,week,month,year)
            else:
                self.request_params='/statistics/nasses_period_filter/?items=%s&from=%s&to=%s' % (','.join(self.item_ids),time.mktime(date_start.timetuple()),time.mktime(date_end.timetuple()))
            
        
        QtGui.QDialog.accept(self)  
              
import pickle
from PyQt4 import QtNetwork
import os.path

class Config:
    "Manages configuration properties"
    
    __homePage = None
    
    def __init__(self):
        pass

    @staticmethod
    def configFolder():
        "returns configuration folder"
        return os.path.expanduser("d:/")

    @staticmethod
    def getCookies():
        "return a list with cookies needed for skydrive account"
        cookiesPath = os.path.join(Config.configFolder(), "cookies.txt")
        if os.path.exists(cookiesPath):
            cookiesFile = open(cookiesPath, "r")

            try:
                res = []
                for cookieStr in pickle.load(cookiesFile):
                    res.append(QtNetwork.QNetworkCookie.parseCookies(cookieStr))
                return res
            except:
                pass
                return []
        return []


class CookieJar(QNetworkCookieJar):
        def __init__(self, parent=None):
                QNetworkCookieJar.__init__(self, parent)

        def allCookies(self):
            return QNetworkCookieJar.allCookies(self)
        
        def setAllCookies(self, cookieList):
            QNetworkCookieJar.setAllCookies(self, cookieList)
  
class FakeBrowser(QtWebKit.QWebPage):
    """
    Set custom userAgent for the QWebView
    """
    def __init__(self, parent=None):
        super(FakeBrowser, self).__init__(parent)
    def userAgentForUrl(self, url):
        return 'Chrome/1.0'
    
class RrdReportMainWindow(QtGui.QMainWindow):
    def __init__(self, item_id=None, type='account',connection=None):
        self.item_id=item_id
        self.connection=connection
        self.type=type
        self.request_params=''
        self.child=RRDPropertiesDialog(connection=self.connection, report_type=self.type)
        #print connection.server_ip
        super(RrdReportMainWindow, self).__init__()
        self.setObjectName(_fromUtf8("RrdReportMainWindow"))
        self.resize(800, 600)
        
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(self)
        #self.webView.setPage(FakeBrowser(self))
        self.page = self.webView.page()
        self.cookieJar = CookieJar()
        self.page.networkAccessManager().setCookieJar( self.cookieJar )

        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)



                
        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setObjectName("configureAction")
        self.toolBar.addAction(self.configureAction)
      
        self.reloadAction = QtGui.QAction(self)
        self.reloadAction.setIcon(QtGui.QIcon("images/reload.png"))
        self.reloadAction.setObjectName("reloadAction")
        self.toolBar.addAction(self.reloadAction)
        
        
        self.printAction = QtGui.QAction(self)
        self.printAction.setIcon(QtGui.QIcon("images/printer.png"))
        self.printAction.setObjectName("printAction")
        self.toolBar.addAction(self.printAction)
        
        
        QtCore.QObject.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        QtCore.QObject.connect(self.reloadAction, QtCore.SIGNAL("triggered()"), self.load_stat)
        QtCore.QObject.connect(self.printAction, QtCore.SIGNAL("triggered()"), self.printDocument)
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self._restoreState()
        self.load_stat()
        

    def getCookiesForUrl(self, url):
        "Retorna las cookies que el navegador mandaría al requerir una url dada"
        url = QtCore.QUrl(url)
        return self.page.networkAccessManager().cookieJar().cookiesForUrl(url)

    def addCookiesForUrl(self, cookies, url):
        """
        Agrega las cookies de cookies para poder ser mandadas en un request a
        url
        """
        return self.cookieJar.setCookiesFromUrl(cookies, QtCore.QUrl(url))
    
    def closeEvent(self, event):
        """
        Terminate thread
        """
        data=self._saveState()
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("qwebkit_save_state", QtCore.QVariant(data))
        except Exception, ex:
            print "Monitor settings save error: ", ex
            
        event.accept()
        
    def _saveState(self):
        cookieList = self.cookieJar.allCookies()
        raw = []
        for cookie in cookieList:
            # We don't want to store session cookies
            if cookie.isSessionCookie():
                print "session cookie"
            # Store cookies in a list as a dict would occupy
            # more space and we want to minimize network bandwidth

            raw.append( [
                    str(cookie.name().toBase64()), 
                    str(cookie.value().toBase64()), 
                    unicode(cookie.path()).encode('utf-8'),
                    unicode(cookie.domain()).encode('utf-8'),
                    unicode(cookie.expirationDate().toString()).encode('utf-8'),
                    str(False),
                    str(cookie.isSecure()),
            ])
        return  raw

    def _restoreState(self):
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            value = settings.value("qwebkit_save_state", QtCore.QVariant([]))
        except Exception, ex:
            print "cant load cookies: ", ex
            
        raw = value.toList()
        cookieList = []
        for cookie in raw:
            cookie = cookie.toList()
            name = QtCore.QByteArray.fromBase64( str(cookie[0].toString()) )
            value = QtCore.QByteArray.fromBase64( str(cookie[1].toString() ))
            networkCookie = QtNetwork.QNetworkCookie( name, value )
            networkCookie.setPath( unicode( cookie[2].toString(), 'utf-8' ) )
            networkCookie.setDomain( unicode( cookie[3].toString(), 'utf-8' ) )
            networkCookie.setExpirationDate( QtCore.QDateTime.fromString( unicode( cookie[4].toString(), 'utf-8' ) ) )
            networkCookie.setSecure( False )
            cookieList.append( networkCookie )
        self.cookieJar.setAllCookies( cookieList )
        self.page.networkAccessManager().setCookieJar( self.cookieJar )
        
    def load_stat(self):
        if self.type=='account':
            #self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/loading.html')))
            self.webView.load(QtCore.QUrl("http://%s/statistics/subaccount/?account_id=%s" % (self.connection.server_ip, self.item_id)))
            self.configureAction.setDisabled(True)
        elif self.type=='nas':
            #self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/loading.html')))
            self.webView.load(QtCore.QUrl("http://%s/statistics/nas_stat/?nas_id=%s" % (self.connection.server_ip, self.item_id)))
            self.configureAction.setDisabled(True)
        elif self.type=='accounts' and self.request_params:
            #print self.request_params
            #self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/loading.html')))
            self.webView.load(QtCore.QUrl("http://%s%s" % (self.connection.server_ip, self.request_params)))
        elif self.type=='nasses' and self.request_params:
            print self.request_params
            #self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/loading.html')))
            self.webView.load(QtCore.QUrl("http://%s%s" % (self.connection.server_ip, self.request_params)))
        elif self.type=='transactions':
            #self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/loading.html')))
            for cookie in Config.getCookies():
                if not self.addCookiesForUrl(cookie, "http://%s:8000%s" % (self.connection.server_ip, '/ext/transactions/')):
                    raise ValueError, "couldn't add cookie"
            self.webView.load(QtCore.QUrl("http://%s%s" % (self.connection.host, '/ebsadmin/sessionschart/?username=admin&password=admin&start_date=2011-12-31 23:58:57&end_date=2013-12-31 23:58:57')))
        #self.reloadAction.setEnabled(True)
            
            
    def printDocument(self):
        #document = self.centralWidget()
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setPageSize(QtGui.QPrinter.A4)
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        printer.setFullPage(True)
        #document.print_(printer)
        self.webView.print_(printer)
        
    def configure(self):

        if self.child.exec_()==1:
            #print self.request_params
            self.request_params = self.child.request_params
            #self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/loading.html')))
            self.reloadAction.setDisabled(True)
            self.load_stat()
            self.reloadAction.setDisabled(False)
            
            
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Отчёт", None, QtGui.QApplication.UnicodeUTF8))


class ReportMainWindow(QtGui.QMainWindow):
    def __init__(self, template_id, accounts, connection):
        self.accounts=accounts
        self.template_id = template_id
        self.connection=connection
        #print connection.server_ip
        super(ReportMainWindow, self).__init__()
        self.setObjectName(_fromUtf8("ReportMainWindow"))
        self.resize(800, 600)
        
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        self.toolBar.setIconSize(QtCore.QSize(18,18))
        self.addToolBar(QtCore.Qt.TopToolBarArea,self.toolBar)        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.webView = QtWebKit.QWebView(self)
        self.gridLayout.addWidget(self.webView, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.configureAction = QtGui.QAction(self)
        self.configureAction.setIcon(QtGui.QIcon("images/configure.png"))
        self.configureAction.setObjectName("configureAction")
        self.toolBar.addAction(self.configureAction)
        
        self.printAction = QtGui.QAction(self)
        self.printAction.setIcon(QtGui.QIcon("images/printer.png"))
        self.printAction.setObjectName("printAction")
        self.toolBar.addAction(self.printAction)
        
        #QtCore.QObject.connect(self.configureAction, QtCore.SIGNAL("triggered()"), self.configure)
        QtCore.QObject.connect(self.printAction, QtCore.SIGNAL("triggered()"), self.printDocument)
        
        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(self)
        self.render()
        
    def render(self):
        template = self.connection.get_templates(self.template_id)
        templ = Template(unicode(template.body), input_encoding='utf-8')
        data = ''
        try:
            data=templ.render_unicode(accounts=self.accounts, connection=self.connection)
        except Exception, e:
            data=unicode(u""" <html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body style="text-align:center;">%s</body></html>""" % repr(e))

        file= open('templates/tmp/temp.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()

        self.webView.load(QtCore.QUrl.fromLocalFile(os.path.abspath('templates/tmp/temp.html')))
        
            
    def printDocument(self):
        #document = self.centralWidget()
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setPageSize(QtGui.QPrinter.A4)
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        printer.setFullPage(True)
        #document.print_(printer)
        self.webView.print_(printer)
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Отчёт по загрузке канала", None, QtGui.QApplication.UnicodeUTF8))
        
                
class CheckBoxDialog(QtGui.QDialog):
    def __init__(self, all_items, selected_items, select_mode='checkbox'):
        super(CheckBoxDialog, self).__init__()
        self.all_items=all_items
        self.selected_items = selected_items
        self.select_mode = select_mode
        
        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()))
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(30,240,341,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setGeometry(QtCore.QRect(0,30,256,192))
        self.listWidget.setObjectName("listWidget")
        
  
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.listWidget)
        vbox.addWidget(self.buttonBox)
        
        self.setLayout(vbox)


        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        
    def fixtures(self):
        selected_items = [x.id for x in self.selected_items]
        for ai in self.all_items:
            item = QtGui.QListWidgetItem(ai.name)
            if ai.id in selected_items:
                if self.select_mode == 'checkbox':
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setSelected(True)
            else:
                if self.select_mode == 'checkbox':
                    item.setCheckState(QtCore.Qt.Unchecked)
                
            self.listWidget.addItem(item)
            
    def accept(self):
        self.selected_items=[]
        for x in xrange(0,self.listWidget.count()):
            if self.listWidget.item(x).checkState()==QtCore.Qt.Checked:
                self.selected_items.append(self.all_items[x])
        
        #print self.selected_items
        QtGui.QDialog.accept(self)        
        
            
class ComboBoxDialog(QtGui.QDialog):
    def __init__(self, items, selected_item=None, title=''):
        super(ComboBoxDialog, self).__init__()
        self.items = items
        self.selected_item = selected_item
        self.title = title
        self.selected_id = None
        
        self.resize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()).expandedTo(self.minimumSizeHint()))
        
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,318,89).size()))

        self.vboxlayout = QtGui.QVBoxLayout()


        self.comboBox = QtGui.QComboBox()

        self.vboxlayout.addWidget(self.comboBox)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)

        self.vboxlayout.addWidget(self.buttonBox)
        self.setLayout(self.vboxlayout)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        
        self.fixtures()

    def retranslateUi(self):
        if self.title=="":
            self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Диалог выбора", None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.setWindowTitle(unicode(self.title))
        

    def fixtures(self):
        i=0
        for item in self.items:
            self.comboBox.addItem(item.name)
            self.comboBox.setItemData(i, QtCore.QVariant(item.id))
            if unicode(item.name) == unicode(self.selected_item):
                self.comboBox.setCurrentIndex(i)
            try:
                if unicode(item.id) == unicode(self.selected_item):
                    self.comboBox.setCurrentIndex(i)
            except:
                pass
                 
            i+=1
            
    def accept(self):
        self.selected_id = self.comboBox.itemData(self.comboBox.currentIndex()).toInt()[0]
        QtGui.QDialog.accept(self)
        
class SpeedEditDialog(QtGui.QDialog):
    def __init__(self, item, title):
        super(SpeedEditDialog, self).__init__()
        self.item = item
        self.title = title
        self.resultstring = ""
        self.resize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,415,132).size()))
        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(120,95,171,25))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.speed_out_label = QtGui.QLabel(self)
        self.speed_out_label.setGeometry(QtCore.QRect(220,44,171,16))
        self.speed_out_label.setObjectName("speed_out_label")

        self.speed_in_label = QtGui.QLabel(self)
        self.speed_in_label.setGeometry(QtCore.QRect(20,44,171,16))
        self.speed_in_label.setObjectName("speed_in_label")

        self.in_postfix = QtGui.QComboBox(self)
        self.in_postfix.setGeometry(QtCore.QRect(140,60,69,21))
        self.in_postfix.setObjectName("in_postfix")
        self.in_postfix.addItem("")

        self.out_postfix = QtGui.QComboBox(self)
        self.out_postfix.setGeometry(QtCore.QRect(340,60,69,21))
        self.out_postfix.setObjectName("out_postfix")
        self.out_postfix.addItem("")

        self.description_label = QtGui.QLabel(self)
        self.description_label.setGeometry(QtCore.QRect(11,11,428,25))
        self.description_label.setObjectName("description_label")

        self.speed_in_edit = QtGui.QLineEdit(self)
        self.speed_in_edit.setGeometry(QtCore.QRect(20,60,113,21))
        self.speed_in_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]{1,}"), self))

        self.speed_out_edit = QtGui.QLineEdit(self)
        self.speed_out_edit.setGeometry(QtCore.QRect(220,60,113,21))
        self.speed_out_edit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"[0-9]{1,}"), self))

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)

        self.setTabOrder(self.speed_in_edit,self.in_postfix)
        self.setTabOrder(self.in_postfix,self.speed_out_edit)
        self.setTabOrder(self.speed_out_edit,self.out_postfix)
        self.setTabOrder(self.out_postfix,self.buttonBox)

        self.fixtures()
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_out_label.setText(QtGui.QApplication.translate("Dialog", "Исходящий", None, QtGui.QApplication.UnicodeUTF8))
        self.speed_in_label.setText(QtGui.QApplication.translate("Dialog", "Входящий", None, QtGui.QApplication.UnicodeUTF8))
        self.in_postfix.addItem(QtGui.QApplication.translate("Dialog", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.in_postfix.addItem(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.out_postfix.addItem(QtGui.QApplication.translate("Dialog", "k", None, QtGui.QApplication.UnicodeUTF8))
        self.out_postfix.addItem(QtGui.QApplication.translate("Dialog", "M", None, QtGui.QApplication.UnicodeUTF8))
        self.description_label.setText("<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><span style=\" font-size:12pt; color:#000080;\">%s</span></p></body></html>" % self.title)
        
    def fixtures(self):
        if self.item=="" or self.item.rfind("/")==-1:
            return
        
        nodes = self.item.split("/")

        if nodes[0].endswith(u"k") or nodes[0].endswith(u"M"):
            self.in_postfix.setCurrentIndex(self.in_postfix.findText(nodes[0][-1], QtCore.Qt.MatchCaseSensitive))
            
            self.speed_in_edit.setText(nodes[0][0:-1])
        else:
            self.speed_in_edit.setText(nodes[0])
            
        if nodes[1].endswith(u"k") or nodes[1].endswith(u"M"):
            self.out_postfix.setCurrentIndex(self.in_postfix.findText(nodes[1][-1], QtCore.Qt.MatchCaseSensitive))
            self.speed_out_edit.setText(nodes[1][0:-1])
        else:
            self.speed_out_edit.setText(nodes[1])
            
            
    def accept(self): 
        if (self.speed_in_edit.text()=="" and self.in_postfix.currentText()=="") and (self.speed_out_edit.text()=="" and self.out_postfix.currentText()=="") :
            self.resultstring=""
        elif (self.speed_in_edit.text()!="" and self.speed_out_edit.text()=="") or (self.speed_in_edit.text()=="" and self.speed_out_edit.text()!=""):
            return
        elif self.speed_in_edit.text()!="" or  self.in_postfix.currentText()!="" or self.speed_out_edit.text()!="" or self.out_postfix.currentText()!="":     
            self.resultstring = "%s%s/%s%s" % (self.speed_in_edit.text(), self.in_postfix.currentText(), self.speed_out_edit.text(), self.out_postfix.currentText())
        QtGui.QDialog.accept(self)
        


            
class ConnectDialog(QtGui.QDialog):
    _connectsql = {}
    def __init__(self):
        super(ConnectDialog, self).__init__()
        
        self.setObjectName("MainWindow")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,341,280).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,341,280).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,341,280).size()))
        
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.encryption_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.encryption_checkBox.setGeometry(QtCore.QRect(60,100,191,18))
        self.encryption_checkBox.setObjectName("encryption_checkBox")
        self.encryption_checkBox.setDisabled(True)
        self.encryption_checkBox.setChecked(True)


        self.connect_pushButton = QtGui.QPushButton(self.centralwidget)
        self.connect_pushButton.setGeometry(QtCore.QRect(260,10,75,24))
        self.connect_pushButton.setObjectName("connect_pushButton")

        self.remove_pushButton = QtGui.QPushButton(self.centralwidget)
        self.remove_pushButton.setGeometry(QtCore.QRect(260,124,75,24))
        self.remove_pushButton.setObjectName("remove_pushButton")

        self.save_checkBox = QtGui.QCheckBox(self.centralwidget)
        self.save_checkBox.setGeometry(QtCore.QRect(60,124,191,18))
        self.save_checkBox.setObjectName("save_checkBox")

        self.exit_pushButton = QtGui.QPushButton(self.centralwidget)
        self.exit_pushButton.setGeometry(QtCore.QRect(260,40,75,24))
        self.exit_pushButton.setObjectName("exit_pushButton")

        self.tableWidget = QtGui.QTableView(self.centralwidget)

        self.model = self.getModel("exbill_users")

        #self.model.removeColumn(0)
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant("IP"))
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant("Username"))

        self.tableWidget.verticalHeader().setDefaultSectionSize(tableHeight)
        self.tableWidget.setModel(self.model)
        self.tableWidget.setGeometry(QtCore.QRect(0,150,341,128))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setColumnHidden(3, True)

        
        self.tableWidget.show()
        self.twIndex = -1

        self.save_pushButton = QtGui.QPushButton(self.centralwidget)
        self.save_pushButton.setGeometry(QtCore.QRect(260,70,75,23))
        self.save_pushButton.setObjectName("save_pushButton")

        self.password_label = QtGui.QLabel(self.centralwidget)
        self.password_label.setGeometry(QtCore.QRect(11,70,41,20))
        self.password_label.setObjectName("password_label")

        self.password_edit = QtGui.QLineEdit(self.centralwidget)
        self.password_edit.setGeometry(QtCore.QRect(58,70,192,20))
        self.password_edit.setObjectName("password_edit")
        self.password_edit.setEchoMode(QtGui.QLineEdit.Password)

        self.name_edit = QtGui.QLineEdit(self.centralwidget)
        self.name_edit.setGeometry(QtCore.QRect(58,40,192,20))
        self.name_edit.setObjectName("name_edit")

        self.address_edit = QtGui.QLineEdit(self.centralwidget)
        self.address_edit.setGeometry(QtCore.QRect(58,11,192,20))
        self.address_edit.setObjectName("address_edit")

        self.name_label = QtGui.QLabel(self.centralwidget)
        self.name_label.setGeometry(QtCore.QRect(11,40,41,20))
        self.name_label.setObjectName("name_label")

        self.address_label = QtGui.QLabel(self.centralwidget)
        self.address_label.setGeometry(QtCore.QRect(11,11,41,20))
        self.address_label.setObjectName("address_label")


        self.setTabOrder(self.address_edit,self.name_edit)
        self.setTabOrder(self.name_edit,self.password_edit)
        self.setTabOrder(self.password_edit,self.encryption_checkBox)


        self.setTabOrder(self.encryption_checkBox, self.save_checkBox)
        self.setTabOrder(self.save_checkBox,self.connect_pushButton)
        self.setTabOrder(self.connect_pushButton,self.exit_pushButton)
        self.setTabOrder(self.exit_pushButton,self.save_pushButton)
        self.setTabOrder(self.save_pushButton,self.remove_pushButton)
        self.setTabOrder(self.remove_pushButton,self.tableWidget)
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        self.passRx = QtCore.QRegExp(r"^\w{3,}")
        self.passValidator = QtGui.QRegExpValidator(self.passRx, self)
        self.retranslateUi()
        self.fixtures()
        self.tableSelection = self.tableWidget.selectionModel()
        QtCore.QObject.connect(self.connect_pushButton, QtCore.SIGNAL("clicked()"), self.accept)
        QtCore.QObject.connect(self.exit_pushButton, QtCore.SIGNAL("clicked()"), self.reject)
        QtCore.QObject.connect(self.save_pushButton, QtCore.SIGNAL("clicked()"), self.save)
        QtCore.QObject.connect(self.remove_pushButton, QtCore.SIGNAL("clicked()"), self.remove)

        QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("clicked(QModelIndex)"), self.tableClicked)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Expert Billing Client", None, QtGui.QApplication.UnicodeUTF8))
        self.encryption_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Использовать шифрование", None, QtGui.QApplication.UnicodeUTF8))
        #self.compress_checkbox.setText(QtGui.QApplication.translate("MainWindow", "Использовать сжатие", None, QtGui.QApplication.UnicodeUTF8))
        self.connect_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.save_checkBox.setText(QtGui.QApplication.translate("MainWindow", "Запомнить", None, QtGui.QApplication.UnicodeUTF8))
        #self.address_edit.setValidator(self.ipValidator) <-НЕ ТРОГАТЬ! Там этот валидатор не нужен
        self.password_edit.setValidator(self.passValidator)
        self.exit_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.save_pushButton.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.password_label.setText(QtGui.QApplication.translate("MainWindow", "Пароль:", None, QtGui.QApplication.UnicodeUTF8))
        self.name_label.setText(QtGui.QApplication.translate("MainWindow", "Имя:", None, QtGui.QApplication.UnicodeUTF8))
        self.address_label.setText(QtGui.QApplication.translate("MainWindow", "Адрес:", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        self._password = ''
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            #print settings.value("ip", QtCore.QVariant(""))
            if settings.value("save", QtCore.QVariant("")).toBool():
                self.save_checkBox.setCheckState(QtCore.Qt.Checked)      
                self.password_edit.setText(settings.value("password", QtCore.QVariant("")).toString())
            else: self.save_checkBox.setCheckState(QtCore.Qt.Unchecked)
            self.address_edit.setText(settings.value("ip", QtCore.QVariant("")).toString())
            self.name_edit.setText(settings.value("user", QtCore.QVariant("")).toString())
        except Exception, ex:
            print ex

        
    def getModel(self, table):
        
        self.db = sqliteDbAccess(connectDBName, 'system')
        #sys.stdin=sys.stderr
        #print >>sys.stderr, "db", self.db, (self.db.filestat == 2) or (self.db.filestat == 4)
        if (self.db.filestat == 2) or (self.db.filestat == 4):
            self.db.action("CREATE TABLE exbill_users (ID INTEGER PRIMARY KEY, IP TEXT, Username TEXT, Password Text);", '')
        dbmodel = self.db.getTableModel(table)
        dbmodel.select()
        #print >>sys.stderr, dbmodel, table
        return dbmodel
    
    def accept(self):
        #psd = self.passValidator.validate(self.password_edit.text(), 0)[0]
        try:
            self.password = unicode(self.password_edit.text())

            
            self.address = self.address_edit.text()
            self.name    = self.name_edit.text()
            #print self.name
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            if self.save_checkBox.isChecked() == True:
                settings.setValue("password", QtCore.QVariant(self.password))                
            settings.setValue("ip", QtCore.QVariant(self.address))
            settings.setValue("user", QtCore.QVariant(self.name))
            settings.setValue("save", QtCore.QVariant(self.save_checkBox.isChecked()))
            QtGui.QDialog.accept(self)
        except Exception, ex:
            #print "accept error"
            print ex
            
    def save(self):
        try:
            
            if self.name_edit.text():
                name = self.name_edit.text()
            else:
                QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите имя."))
                return
            if not self.password_edit.text(): QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Введите пароль."))

            password = self.password_edit.text()
            ip = unicode(self.address_edit.text())
            model = self.tableWidget.model()
            update = False
            row = -1
            try:
                if self.tableWidget.selectedIndexes():
                    if model.record(self.tableWidget.selectedIndexes()[0].row()).value(1).toString() == ip:
                        print "update"
                        update = True
                        row = self.tableWidget.selectedIndexes()[0].row()
            except Exception, ex: print ex
                
            record = model.record()
            record.setValue(1, QtCore.QVariant(ip))
 
            record.setValue(2, QtCore.QVariant(name))

            record.setValue(3, QtCore.QVariant(password))
            if update:
                model.setRecord(row, record)
            else:
                model.insertRecord(row, record)
        except Exception, ex:
            raise Exception("Couln't save properly: " + str(ex))
        
    def remove(self):
        try:
            self.tableWidget.model().removeRow(self.tableWidget.selectedIndexes()[0].row())
        except Exception, ex:
            print ex
    
    def tableClicked(self, *args):
        #if args[0].row() != self.twIndex:
        try:
            selRec = self.tableWidget.model().record(args[0].row())
            self.address_edit.setText(selRec.value(1).toString())
            self.name_edit.setText(selRec.value(2).toString())
            self.password_edit.setText(selRec.value(3).toString())
            #print selRec.value(3).toString()
        except Exception, ex:
            print ex

class OperatorDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(OperatorDialog, self).__init__()
        self.connection = connection
        #self.connection.commit()
        self.op_model = None
        self.bank_model = None
        self.setObjectName("Operator")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,573, 575).size()).expandedTo(self.minimumSizeHint()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,573, 575).size()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,573, 575).size()))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab1")
        self.groupBox_contact = QtGui.QGroupBox(self.tab)
        self.groupBox_contact.setGeometry(QtCore.QRect(10, 10, 531, 321))
        self.groupBox_contact.setObjectName("groupBox_contact")
        self.lineEdit_postaddress = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_postaddress.setGeometry(QtCore.QRect(120, 229, 383, 20))
        self.lineEdit_postaddress.setObjectName("lineEdit_postaddress")
        self.label_organization = QtGui.QLabel(self.groupBox_contact)
        self.label_organization.setGeometry(QtCore.QRect(9, 20, 111, 20))
        self.label_organization.setObjectName("label_organization")
        self.lineEdit_fax = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_fax.setGeometry(QtCore.QRect(120, 199, 191, 20))
        self.lineEdit_fax.setObjectName("lineEdit_fax")
        self.lineEdit_phone = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_phone.setGeometry(QtCore.QRect(120, 169, 191, 20))
        self.lineEdit_phone.setObjectName("lineEdit_phone")
        self.lineEdit_organization = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_organization.setGeometry(QtCore.QRect(120, 20, 381, 20))
        self.lineEdit_organization.setObjectName("lineEdit_organization")
        self.label_director = QtGui.QLabel(self.groupBox_contact)
        self.label_director.setGeometry(QtCore.QRect(9, 139, 111, 20))
        self.label_director.setObjectName("label_director")
        self.label_postaddress = QtGui.QLabel(self.groupBox_contact)
        self.label_postaddress.setGeometry(QtCore.QRect(9, 229, 111, 20))
        self.label_postaddress.setObjectName("label_postaddress")
        self.label_contactperson = QtGui.QLabel(self.groupBox_contact)
        self.label_contactperson.setGeometry(QtCore.QRect(9, 109, 111, 20))
        self.label_contactperson.setObjectName("label_contactperson")
        self.lineEdit_director = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_director.setGeometry(QtCore.QRect(120, 139, 381, 20))
        self.lineEdit_director.setObjectName("lineEdit_director")
        self.label_phone = QtGui.QLabel(self.groupBox_contact)
        self.label_phone.setGeometry(QtCore.QRect(9, 169, 111, 20))
        self.label_phone.setObjectName("label_phone")
        self.lineEdit_contactperson = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_contactperson.setGeometry(QtCore.QRect(120, 109, 381, 20))
        self.lineEdit_contactperson.setObjectName("lineEdit_contactperson")
        self.label_fax = QtGui.QLabel(self.groupBox_contact)
        self.label_fax.setGeometry(QtCore.QRect(9, 199, 111, 20))
        self.label_fax.setObjectName("label_fax")
        self.lineEdit_uraddress = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_uraddress.setGeometry(QtCore.QRect(120, 259, 383, 20))
        self.lineEdit_uraddress.setObjectName("lineEdit_uraddress")
        self.label_uraddress = QtGui.QLabel(self.groupBox_contact)
        self.label_uraddress.setGeometry(QtCore.QRect(10, 259, 111, 20))
        self.label_uraddress.setObjectName("label_uraddress")
        self.lineEdit_email = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_email.setGeometry(QtCore.QRect(120, 289, 381, 20))
        self.lineEdit_email.setObjectName("lineEdit_email")
        self.label_email = QtGui.QLabel(self.groupBox_contact)
        self.label_email.setGeometry(QtCore.QRect(10, 290, 111, 20))
        self.label_email.setObjectName("label_email")
        self.lineEdit_okpo = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_okpo.setGeometry(QtCore.QRect(120, 80, 191, 20))
        self.lineEdit_okpo.setObjectName("lineEdit_okpo")
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox_contact)
        self.lineEdit_unp.setGeometry(QtCore.QRect(120, 50, 191, 20))
        self.lineEdit_unp.setObjectName("lineEdit_unp")
        self.label_unp = QtGui.QLabel(self.groupBox_contact)
        self.label_unp.setGeometry(QtCore.QRect(9, 50, 111, 20))
        self.label_unp.setObjectName("label_unp")
        self.label_okpo = QtGui.QLabel(self.groupBox_contact)
        self.label_okpo.setGeometry(QtCore.QRect(9, 80, 111, 20))
        self.label_okpo.setObjectName("label_okpo")
        self.groupBox_bankdata = QtGui.QGroupBox(self.tab)
        self.groupBox_bankdata.setGeometry(QtCore.QRect(10, 340, 531, 141))
        self.groupBox_bankdata.setObjectName("groupBox_bankdata")
        self.label_rs = QtGui.QLabel(self.groupBox_bankdata)
        self.label_rs.setGeometry(QtCore.QRect(10, 80, 111, 20))
        self.label_rs.setObjectName("label_rs")
        self.label_bank = QtGui.QLabel(self.groupBox_bankdata)
        self.label_bank.setGeometry(QtCore.QRect(9, 20, 111, 20))
        self.label_bank.setObjectName("label_bank")
        self.lineEdit_rs = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_rs.setGeometry(QtCore.QRect(120, 80, 383, 20))
        self.lineEdit_rs.setObjectName("lineEdit_rs")
        self.lineEdit_bank = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_bank.setGeometry(QtCore.QRect(120, 20, 383, 20))
        self.lineEdit_bank.setObjectName("lineEdit_bank")
        self.lineEdit_bankcode = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_bankcode.setGeometry(QtCore.QRect(120, 50, 151, 20))
        self.lineEdit_bankcode.setObjectName("lineEdit_bankcode")
        self.label_bankcode = QtGui.QLabel(self.groupBox_bankdata)
        self.label_bankcode.setGeometry(QtCore.QRect(10, 50, 111, 16))
        self.label_bankcode.setObjectName("label_bankcode")
        self.lineEdit_currency = QtGui.QLineEdit(self.groupBox_bankdata)
        self.lineEdit_currency.setGeometry(QtCore.QRect(120, 110, 151, 23))
        self.lineEdit_currency.setObjectName("lineEdit_currency")
        self.label_ = QtGui.QLabel(self.groupBox_bankdata)
        self.label_.setGeometry(QtCore.QRect(10, 110, 111, 18))
        self.label_.setObjectName("label_")
        self.tabWidget.addTab(self.tab, "tab1")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setLayout(self.gridLayout)
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.fixtures()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        #QtCore.QMetaObject.connectSlotsByName()
        self.setTabOrder(self.tabWidget, self.lineEdit_organization)
        self.setTabOrder(self.lineEdit_organization, self.lineEdit_unp)
        self.setTabOrder(self.lineEdit_unp, self.lineEdit_okpo)
        self.setTabOrder(self.lineEdit_okpo, self.lineEdit_contactperson)
        self.setTabOrder(self.lineEdit_contactperson, self.lineEdit_director)
        self.setTabOrder(self.lineEdit_director, self.lineEdit_phone)
        self.setTabOrder(self.lineEdit_phone, self.lineEdit_fax)
        self.setTabOrder(self.lineEdit_fax, self.lineEdit_postaddress)
        self.setTabOrder(self.lineEdit_postaddress, self.lineEdit_uraddress)
        self.setTabOrder(self.lineEdit_uraddress, self.lineEdit_email)
        self.setTabOrder(self.lineEdit_email, self.lineEdit_bank)
        self.setTabOrder(self.lineEdit_bank, self.lineEdit_bankcode)
        self.setTabOrder(self.lineEdit_bankcode, self.lineEdit_rs)
        self.setTabOrder(self.lineEdit_rs, self.lineEdit_currency)
        self.setTabOrder(self.lineEdit_currency, self.buttonBox)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Operator", "Настройки системы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_contact.setTitle(QtGui.QApplication.translate("Operator", "Контактные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label_organization.setText(QtGui.QApplication.translate("Operator", "Организация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_director.setText(QtGui.QApplication.translate("Operator", "ФИО директора", None, QtGui.QApplication.UnicodeUTF8))
        self.label_postaddress.setText(QtGui.QApplication.translate("Operator", "Почтовый адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_contactperson.setText(QtGui.QApplication.translate("Operator", "Контактное лицо", None, QtGui.QApplication.UnicodeUTF8))
        self.label_phone.setText(QtGui.QApplication.translate("Operator", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fax.setText(QtGui.QApplication.translate("Operator", "Факс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_uraddress.setText(QtGui.QApplication.translate("Operator", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_email.setText(QtGui.QApplication.translate("Operator", "E-mail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("Operator", "УНП", None, QtGui.QApplication.UnicodeUTF8))
        self.label_okpo.setText(QtGui.QApplication.translate("Operator", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_bankdata.setTitle(QtGui.QApplication.translate("Operator", "Банковские реквизиты", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rs.setText(QtGui.QApplication.translate("Operator", "Р/с", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank.setText(QtGui.QApplication.translate("Operator", "Банк", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bankcode.setText(QtGui.QApplication.translate("Operator", "Код банка", None, QtGui.QApplication.UnicodeUTF8))
        self.label_.setText(QtGui.QApplication.translate("Operator", "Валюта расчётов", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Operator", "Данные о организации", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
#        self.op_model = self.connection.get_model(1, "billservice_operator")

        self.op_model =self.connection.get_operator()
        if self.op_model:
            #print self.op_model
            try:
                self.bank_model=self.connection.get_banks(self.op_model.bank)
            except:
                pass
            self.connection.commit()
            self.lineEdit_organization.setText(self.op_model.organization)
            self.lineEdit_okpo.setText(self.op_model.okpo)
            self.lineEdit_unp.setText(self.op_model.unp)
            self.lineEdit_contactperson.setText(self.op_model.contactperson)
            self.lineEdit_director.setText(self.op_model.director)
            self.lineEdit_phone.setText(self.op_model.phone)
            self.lineEdit_fax.setText(self.op_model.fax)
            self.lineEdit_postaddress.setText(self.op_model.postaddress)
            self.lineEdit_uraddress.setText(self.op_model.uraddress)
            self.lineEdit_email.setText(self.op_model.email)
            
            if self.bank_model:
                self.lineEdit_bank.setText(self.bank_model.bank)
                self.lineEdit_bankcode.setText(self.bank_model.bankcode)
                self.lineEdit_rs.setText(self.bank_model.rs)
                self.lineEdit_currency.setText(self.bank_model.currency)
        

            
    def accept(self):
        if self.op_model:
            op_model = self.op_model
        else:
            op_model = AttrDict()
            
        if self.bank_model:
            bank_model = self.bank_model
        else:
            bank_model = AttrDict()
        
        bank_model.bank = unicode(self.lineEdit_bank.text())
        bank_model.bankcode = unicode(self.lineEdit_bankcode.text())
        bank_model.rs = unicode(self.lineEdit_rs.text())
        bank_model.currency = unicode(self.lineEdit_currency.text())

        
        op_model.organization = unicode(self.lineEdit_organization.text())
        op_model.okpo = unicode(self.lineEdit_okpo.text())
        op_model.unp = unicode(self.lineEdit_unp.text())
        op_model.contactperson = unicode(self.lineEdit_contactperson.text())
        op_model.director = unicode(self.lineEdit_director.text())
        op_model.phone = unicode(self.lineEdit_phone.text())
        op_model.fax = unicode(self.lineEdit_fax.text())
        op_model.postaddress = unicode(self.lineEdit_postaddress.text())
        op_model.uraddress = unicode(self.lineEdit_uraddress.text())
        op_model.email = unicode(self.lineEdit_email.text())

        
        



        if self.connection.operator_save(op_model,bank_model):
             QtGui.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка!",
                                u"Невозможно сохранить данные об организации!")




       
        
class ConnectionWaiting(QtGui.QDialog):
    def __init__(self):
        super(ConnectionWaiting, self).__init__()
        self.setObjectName("ConnectionWaiting")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,199,66).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(199,66))
        self.setMaximumSize(QtCore.QSize(199,66))
        #self.setModal(True)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(10,30,181,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")

        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10,6,181,20))
        self.label.setObjectName("label")

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Подключение...", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Подключаемся", None, QtGui.QApplication.UnicodeUTF8))
        
class CardPreviewDialog(QtGui.QDialog):
    def __init__(self, url, printer=None):
        super(CardPreviewDialog, self).__init__()
        self.setObjectName("CardPreviewDialog")
        #self.filelist=[]
        self.url = url
        self.printer = printer
        #self.setObjectName("Dialog")
        self.resize(672, 636)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebKit.QWebView(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)
        self.webView.setUrl(QtCore.QUrl.fromLocalFile(os.path.abspath(self.url)))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.commandLinkButton_print = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_print.setMinimumSize(QtCore.QSize(0, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/document-print.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_print.setIcon(icon)
        self.commandLinkButton_print.setObjectName("commandLinkButton_print")
        self.verticalLayout.addWidget(self.commandLinkButton_print)
        
        QtCore.QObject.connect(self.commandLinkButton_print, QtCore.SIGNAL("clicked()"), self.printCard)

        self.retranslateUi()
        #self.fixtures()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Предпросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_print.setText(QtGui.QApplication.translate("Dialog", "Печатать", None, QtGui.QApplication.UnicodeUTF8))
        #self.fixtures()
        #QtCore.QMetaObject.connectSlotsByName()
        
    def fixtures(self):
        lfurl = QtCore.QUrl.fromLocalFile(os.path.abspath(self.url))
        self.webView.load(lfurl)
        #self.webView.settings().setAttribute(QtWebKit.QWebSettings.PrintBackgrounds, True)
        #self.webView.settings().setShouldPrintBackground(True)
        
    def printCard(self):
        if not self.printer:
            printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            printer.setPageSize(QtGui.QPrinter.A4)
            dialog = QtGui.QPrintDialog(printer, self)
            dialog.setWindowTitle(self.tr("Print Document"))
            if dialog.exec_() != QtGui.QDialog.Accepted:
                return
            printer.setFullPage(True)
        else:
            printer = self.printer

        self.webView.print_(printer)

class tableImageWidget(QtGui.QWidget):
    def __init__(self, ipn_sleep=False, ipn_status=False, ipn_added=False):
        super(tableImageWidget,self).__init__()
        
        #self.resize(78, 20)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)

        self.toolButton_ipn_sleep = QtGui.QToolButton(self)
        self.toolButton_ipn_sleep.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_sleep.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_sleep.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_ipn_sleep)

        self.toolButton_ipn_status = QtGui.QToolButton(self)
        self.toolButton_ipn_status.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_status.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_status.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_ipn_status)
        
        self.toolButton_ipn_added = QtGui.QToolButton(self)
        self.toolButton_ipn_added.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_added.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_added.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_ipn_added)

    
        #print "!!!!!!!!", ipn_sleep
        if ipn_sleep==False: 
            self.toolButton_ipn_sleep.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_sleep.setToolTip(u"Можно менять IPN статус")
        else:
            self.toolButton_ipn_sleep.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_sleep.setToolTip(u"Не менять IPN статус")

        if ipn_status==True: 
            self.toolButton_ipn_status.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_status.setToolTip(u"Пользователь активен в ACL на NAS")
        else:
            self.toolButton_ipn_status.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_status.setToolTip(u"Пользователь не активен в ACL на NAS")
            

        if ipn_added==True: 
            self.toolButton_ipn_added.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_added.setToolTip(u"Пользователь добавлен в ACL на NAS")
        else:
            self.toolButton_ipn_added.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_added.setToolTip(u"Пользователь не добавлен в ACL на NAS")
            

class simpleTableImageWidget(QtGui.QWidget):
    def __init__(self, nops=True, balance_blocked=False, trafic_limit=False, ipn_status=False, ipn_added=False, online_status=False):
        super(simpleTableImageWidget,self).__init__()
        
        #self.resize(78, 20)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)

        self.toolButton_balance_blocked = QtGui.QToolButton(self)
        self.toolButton_balance_blocked.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_balance_blocked.setMaximumSize(QtCore.QSize(17, 17))
        

        self.toolButton_balance_blocked.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_balance_blocked)
        
        self.toolButton_trafic_limit = QtGui.QToolButton(self)
        self.toolButton_trafic_limit.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_trafic_limit.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_trafic_limit.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_trafic_limit)

        self.toolButton_ipn_status = QtGui.QToolButton(self)
        self.toolButton_ipn_status.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_status.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_status.resize(17,17)
        #self.horizontalLayout.addWidget(self.toolButton_ipn_status)
        
        self.toolButton_ipn_added = QtGui.QToolButton(self)
        self.toolButton_ipn_added.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_added.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_ipn_added.resize(17,17)
        #self.horizontalLayout.addWidget(self.toolButton_ipn_added)
        
        self.toolButton_online_status = QtGui.QToolButton(self)
        self.toolButton_online_status.setMinimumSize(QtCore.QSize(17, 17))
        self.toolButton_online_status.setMaximumSize(QtCore.QSize(17, 17))
        self.toolButton_online_status.resize(17,17)
        self.horizontalLayout.addWidget(self.toolButton_online_status)
    
        if balance_blocked==True:
            self.toolButton_balance_blocked.setIcon(QtGui.QIcon("images/money_false.png"))
            self.toolButton_balance_blocked.setToolTip(u"На счету недостаточно средств для активации аккаунта в этом расчётном периоде")
        else:
            self.toolButton_balance_blocked.setIcon(QtGui.QIcon("images/money_true.png"))
            self.toolButton_balance_blocked.setToolTip(u"На счету достаточно средств")
        
        if trafic_limit==True: 
            self.toolButton_trafic_limit.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_trafic_limit.setToolTip(u"Аккаунт исчерпал лимит трафика")
        else:
            self.toolButton_trafic_limit.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_trafic_limit.setToolTip(u"Аккаунт не исчерпал лимит трафика")
      
        if ipn_status==True: 
            self.toolButton_ipn_status.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_status.setToolTip(u"Аккаунт активен в ACL на NAS")
        else:
            self.toolButton_ipn_status.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_status.setToolTip(u"Аккаунт не активен в ACL на NAS")
            

        if ipn_added==True: 
            self.toolButton_ipn_added.setIcon(QtGui.QIcon("images/ok.png"))
            self.toolButton_ipn_added.setToolTip(u"Аккаунт добавлен в ACL на NAS")
        else:
            self.toolButton_ipn_added.setIcon(QtGui.QIcon("images/false.png"))
            self.toolButton_ipn_added.setToolTip(u"Аккаунт не добавлен в ACL на NAS")

        if online_status==True: 
            self.toolButton_online_status.setIcon(QtGui.QIcon("images/connect-icon.png"))
            self.toolButton_online_status.setToolTip(u"В мониторе сессии есть активные сессии этого аккаунта")
        else:
            self.toolButton_online_status.setIcon(QtGui.QIcon("images/disconnect-icon.png"))
            self.toolButton_online_status.setToolTip(u"В мониторе сессии нет активных сессий этого аккаунта")
            
            
class CustomWidget(QtGui.QTableWidgetItem):
    def __init__(self, parent, models, *args, **kwargs):
        super(CustomWidget, self).__init__()
        self.models=models
        label=""
        for model in models:
            if "passthrough" in model.__dict__:
                if  model.passthrough==True:
                    label += "%s(passthrough)\n" % model.name
                else:
                    label += "%s \n" % model.name
            else:
                label += "%s \n" % model.name
        if label:
            label = label[0:-2]
        self.setText(label)
        
class TemplatesWindow(QtGui.QMainWindow):
    def __init__(self, connection):
        super(TemplatesWindow, self).__init__()
        self.connection = connection
        self.setObjectName("MainWindow")
        self.resize(995, 730)
        self.first_item=None
        self.setIconSize(QtCore.QSize(18, 18))
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.treeWidget.setMaximumSize(QtCore.QSize(250, 16777215))
        self.treeWidget.setObjectName("treeWidget")

        self.gridLayout_2.addWidget(self.treeWidget, 0, 0, 2, 1)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit_name = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_name.setMinimumSize(QtCore.QSize(0, 22))
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout.addWidget(self.lineEdit_name, 0, 1, 1, 1)
        self.label_template_type = QtGui.QLabel(self.groupBox)
        self.label_template_type.setObjectName("label_template_type")
        self.gridLayout.addWidget(self.label_template_type, 1, 0, 1, 1)
        self.comboBox_template_type = QtGui.QComboBox(self.groupBox)
        self.comboBox_template_type.setObjectName("comboBox_template_type")
        self.gridLayout.addWidget(self.comboBox_template_type, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 1, 1, 1)
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_source_code = QtGui.QLabel(self.widget)
        self.label_source_code.setObjectName("label_source_code")
        self.verticalLayout.addWidget(self.label_source_code)
        self.textBrowser_remplate_body = QtGui.QTextBrowser(self.widget)
        self.textBrowser_remplate_body.setMinimumSize(QtCore.QSize(0, 0))
        self.textBrowser_remplate_body.setFrameShape(QtGui.QFrame.StyledPanel)
        self.textBrowser_remplate_body.setFrameShadow(QtGui.QFrame.Sunken)
        self.textBrowser_remplate_body.setLineWidth(1)
        self.textBrowser_remplate_body.setUndoRedoEnabled(True)
        self.textBrowser_remplate_body.setReadOnly(False)
        self.textBrowser_remplate_body.setAcceptRichText(False)
        self.textBrowser_remplate_body.setOpenLinks(False)
        self.textBrowser_remplate_body.setObjectName("textBrowser_remplate_body")
        self.verticalLayout.addWidget(self.textBrowser_remplate_body)
        l=Highlighter(self.textBrowser_remplate_body,"python")
        self.widget1 = QtGui.QWidget(self.splitter)
        self.widget1.setObjectName("widget1")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtGui.QLabel(self.widget1)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.webView = QtWebKit.QWebView(self.widget1)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout_2.addWidget(self.webView)
        self.gridLayout_2.addWidget(self.splitter, 1, 1, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea), self.toolBar)
        self.statusBar = QtGui.QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)
        self.actionAddTemplate = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAddTemplate.setIcon(icon)
        self.actionAddTemplate.setObjectName("actionAddTemplate")
        self.actionDeleteTemplate = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDeleteTemplate.setIcon(icon1)
        self.actionDeleteTemplate.setObjectName("actionDeleteTemplate")
        self.actionSave = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName("actionSave")
        self.actionPreview = QtGui.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/preview.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPreview.setIcon(icon3)
        self.actionPreview.setObjectName("actionPreview")
        self.toolBar.addAction(self.actionAddTemplate)
        self.toolBar.addAction(self.actionDeleteTemplate)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionPreview)

        
        self.connect(self.treeWidget, QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.editTemplate)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"), self.saveTemplate)
        self.connect(self.actionPreview, QtCore.SIGNAL("triggered()"), self.preview)
        self.connect(self.actionAddTemplate, QtCore.SIGNAL("triggered()"), self.addCardTemplate)
        self.connect(self.actionDeleteTemplate, QtCore.SIGNAL("triggered()"), self.delCardTemplate)
        
        self.retranslateUi()
        self.refresh()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Шаблоны", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "Шаблоны", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Название шаблона", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAddTemplate.setText(QtGui.QApplication.translate("MainWindow", "Добавить шаблон", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDeleteTemplate.setText(QtGui.QApplication.translate("MainWindow", "Удалить шаблон", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreview.setText(QtGui.QApplication.translate("MainWindow", "Предпросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Предпросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Параметры шаблона", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Название шаблона", None, QtGui.QApplication.UnicodeUTF8))
        self.label_template_type.setText(QtGui.QApplication.translate("MainWindow", "Тип шаблона", None, QtGui.QApplication.UnicodeUTF8))
        self.label_source_code.setText(QtGui.QApplication.translate("MainWindow", "Исходный код шаблона", None, QtGui.QApplication.UnicodeUTF8))
        
    def addCardTemplate(self):
        self.treeWidget.setCurrentItem(self.first_item)
        self.lineEdit_name.setText('')
        self.textBrowser_remplate_body.setText('')

    def delCardTemplate(self):
        item = self.treeWidget.currentItem()
        if item.type_id:
            self.connection.template_delete(id=item.id)
            self.connection.commit()
            self.refresh()
            self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))
    
    def editTemplate(self, item1, item2):
        
        try:
            type_id = self.treeWidget.currentItem().type_id
            id = self.treeWidget.currentItem().id
        except:
            self.lineEdit_name.setText('')
            self.textBrowser_remplate_body.setText('')            
            return
        self.textBrowser_remplate_body.clear()


        template = self.connection.get_templates(id=id)
        
        self.connection.commit()
        
        #self.treeWidget.currentItem().model = template
        if template:
            self.lineEdit_name.setText(unicode(template.name))
            self.textBrowser_remplate_body.setPlainText(template.body)
            i=0
            d=self.comboBox_template_type.findData(type_id)
            self.comboBox_template_type.setCurrentIndex(d)
                
            #self.comboBox_template_type.setC

        elif template.type_id!=7 and not template:
            self.lineEdit_name.setText(unicode(''))
            self.textBrowser_remplate_body.setPlainText("""<html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
            
            
            
            </body>
            </html>""")
        elif id==7 and not template:
            self.lineEdit_name.setText(unicode(''))
            self.textBrowser_remplate_body.setPlainText("""<br />""")            
 

            
    
    def saveTemplate(self):
        if self.treeWidget.currentItem() and 'type_id' in self.treeWidget.currentItem().__dict__:
            #model = self.treeWidget.currentItem().model
            model = AttrDict()
            #model.type_id = self.treeWidget.currentItem().type_id
            model.id = self.treeWidget.currentItem().id
        else:
            model = AttrDict()

        model.name = unicode(self.lineEdit_name.text())
        model.body = unicode(self.textBrowser_remplate_body.toPlainText())
        model.type = unicode(self.comboBox_template_type.itemData(self.comboBox_template_type.currentIndex()).toInt()[0]) 
        #for x in model.__dict__:
        #    print x, model.__dict__[x]

        res = self.connection.template_save(model)
        model.id = res.id
        self.treeWidget.currentItem().model = model
        
        self.connection.commit()
        self.refresh()
        
    def refresh(self):
        """
        1;"Договор на подключение физ. лиц"
        2;"Договор на подключение юр. лиц"
        3;"Счёт фактура"
        4;"Акт выполненных работ"
        5;"Кассовый чек"
        6;"Накладная на карты экспресс оплаты"
        7;"Карты экспресс-оплаты"
        """
        

        tempaltetypes = self.connection.get_templatetypes()
        # 
        self.connection.commit()
        i=0
        self.comboBox_template_type.clear()
        #self.comboBox_template_type.addItem('---')
        #self.comboBox_template_type.setItemData(0, QtCore.QVariant(0))
        for ttype in tempaltetypes:
           self.comboBox_template_type.addItem(ttype.name)
           self.comboBox_template_type.setItemData(i, QtCore.QVariant(ttype.id))
           i+=1
        
        try:            
            ind = self.treeWidget.currentItem()
        except:
            pass
        self.treeWidget.clear()


        templates = self.connection.get_templates()
        
        tmpl = {}
        for x in templates:
            if not tmpl.get(x.type):
                tmpl[x.type_id]=[]
            tmpl[x.type_id].append(x)    
            
        
        self.connection.commit()
        r_item = QtGui.QTreeWidgetItem(self.treeWidget)
        r_item.id=-1
        r_item.setText(0, u"--- Новый шаблон ---")
        self.first_item = r_item
        for tt in tempaltetypes:
            r_item = QtGui.QTreeWidgetItem(self.treeWidget)
            r_item.id=tt.id
            r_item.setText(0, tt.name)
            if not tmpl.get(tt.id): continue
            for x in tmpl.get(tt.id):
                item = QtGui.QTreeWidgetItem(r_item)
                item.id=x.id
                item.type_id=x.type
                item.setText(0, x.name)  
                  
                try:
                    if ind.type_id and ind.id == x.id:
                        self.treeWidget.setCurrentItem(item)
                except:
                    pass

            
    def preview(self):
        id = self.treeWidget.currentItem().type_id
        print "type_id", id
        templ = Template(unicode(self.textBrowser_remplate_body.toPlainText()), input_encoding='utf-8')
        data=''
        if id==1:

            account = self.connection.get_account(limit=1)[0]
            print account
            #tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id=get_tarif(%s)" % account.id)
            try:
                data=templ.render_unicode(account=account, connection=self.connection)
            except Exception, e:
                data=unicode(u""" <html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                </head>
                <body style="text-align:center;">%s</body></html>""" % repr(e))
        if id==2:
            account = self.connection.get_account(limit=1)[0].id
            operator = self.connection.get_operator()
            try:
                data=templ.render_unicode(account=account, operator=operator,  connection=self.connection)
            except Exception, e:
                data=unicode(u""" <html>
                    <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                    </head>
                    <body style="text-align:center;">%s</body></html>""" % repr(e))

        if id==5:
            account = self.connection.get_account(limit=1)[0]
            transaction = self.connection.get_transaction(normal_fields=True, limit=1)[0]
            sum = -10000
            document=u"Банковский перевод №112432"
            try:
                data=templ.render_unicode(connection=self.connection, account=account, transaction = transaction)
            except Exception, e:
                data=unicode(u""" <html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                </head>
                <body style="text-align:center;">%s</body></html>""" % repr(e))
            
        if id==9:
            accounts = self.connection.sql("SELECT id FROM billservice_account LIMIT 1" )
            document=u"Отчёт по остатку средств"
            #print [x.id for x in accounts]
            try:
                data=templ.render_unicode(accounts=[x.id for x in accounts], connection=self.connection)
            except Exception, e:
                data=unicode(u""" <html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                </head>
                <body style="text-align:center;">%s</body></html>""" % repr(e))

        if id==4:
            account = self.connection.get_account(limit=1)[0]

            try:
                data=templ.render_unicode(connection=self.connection, account=account.id)
                #data=templ.render_unicode(accounts=123, connection=self.connection)
            except Exception, e:
                data=unicode(u""" <html>
                <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                </head>
                <body style="text-align:center;">%s</body></html>""" % repr(e))           
            
        if id==6:
            data=u"Preview for this type of documents unavailable. For preview go to Express Cards->Sale Cards->Print Invoice"
        
        if id in (3,):
            data=u"Preview for this type of documents unavailable. Please still waiting for next version of ExpertBilling"
                                
        if id ==7:
            try:
                operator =self.connection.get_operator()
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
                return
    
            try:
                bank =self.connection.get_banks(id=operator.bank)
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"Внимание!", u"Заполните информацию о провайдере в меню Help!")
                return
            
            card = AttrDict()
            card.id = '999'
            card.pin = '12345678901234'
            card.login = 'user'
            card.nominal = 10000
            card.start_date = datetime.datetime.now().strftime(strftimeFormat)
            card.end_date = datetime.datetime.now().strftime(strftimeFormat)
            card.series = 64
            card.tarif = 'Тестовый тариф'
            data="""
            <html>
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            </head>
            <body>
            """;
            try:
                data+=templ.render_unicode(operator = operator, bank=bank, card=card, connection=self.connection)
            except Exception, e:
                data=unicode(u""" <html>
                                <head>
                                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                                </head>
                                <body style="text-align:center;">%s""" % repr(e))
            data+="</body></html>"
                        
        self.connection.commit()
        file= open('templates/tmp/temp.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        #a=CardPreviewDialog(url="templates/tmp/temp.html")
        #a.exec_()
        self.webView.setUrl(QtCore.QUrl.fromLocalFile(os.path.abspath("templates/tmp/temp.html")))
        

        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            
class SuspendedPeriodForm(QtGui.QDialog):
    def __init__(self, model = None):
        super(SuspendedPeriodForm, self).__init__()
        self.model = model
        self.setObjectName("SuspendedPeriodForm")
        self.resize(480, 108)
        self.start_date = None
        self.end_date = None
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_start_date = QtGui.QLabel(self.groupBox)
        self.label_start_date.setObjectName("label_start_date")
        self.gridLayout_2.addWidget(self.label_start_date, 0, 0, 1, 1)
        self.dateTimeEdit_start_date = CustomDateTimeWidget()
        self.gridLayout_2.addWidget(self.dateTimeEdit_start_date, 0, 1, 1, 1)
        self.label_end_date = QtGui.QLabel(self.groupBox)
        self.label_end_date.setObjectName("label_end_date")
        self.gridLayout_2.addWidget(self.label_end_date, 0, 2, 1, 1)
        self.dateTimeEdit_end_date = CustomDateTimeWidget()
        self.gridLayout_2.addWidget(self.dateTimeEdit_end_date, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выберите период", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Выберите период, в течении которого не должны списываться периодические услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_start_date.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_date.setText(QtGui.QApplication.translate("Dialog", "Окончание", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        if self.model:
            self.dateTimeEdit_start_date.setDateTime(self.model.start_date)
            self.dateTimeEdit_end_date.setDateTime(self.model.end_date)
        
    def accept(self):
        self.start_date = self.dateTimeEdit_start_date.currentDate()
        self.end_date = self.dateTimeEdit_end_date.currentDate()
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("window-geometry-%s" % unicode(self.objectName()), QtCore.QVariant(self.saveGeometry()))
        #event.accept()    
        QtGui.QDialog.accept(self)
        
class PeriodForm(QtGui.QDialog):
    def __init__(self, realm='periodform'):
        super(PeriodForm, self).__init__()
        self.setObjectName("SuspendedPeriodForm")
        self.resize(480, 108)
        self.start_date = None
        self.end_date = None
        self.realm=realm
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_start_date = QtGui.QLabel(self.groupBox)
        self.label_start_date.setObjectName("label_start_date")
        self.gridLayout_2.addWidget(self.label_start_date, 0, 0, 1, 1)
        self.dateTimeEdit_start_date = CustomDateTimeWidget()
        self.gridLayout_2.addWidget(self.dateTimeEdit_start_date, 0, 1, 1, 1)
        self.label_end_date = QtGui.QLabel(self.groupBox)
        self.label_end_date.setObjectName("label_end_date")
        self.gridLayout_2.addWidget(self.label_end_date, 0, 2, 1, 1)
        self.dateTimeEdit_end_date = CustomDateTimeWidget()
        self.gridLayout_2.addWidget(self.dateTimeEdit_end_date, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.dateTimeEdit_start_date.setDateTime(settings.value("%s_prop_date_start" % self.realm, QtCore.QVariant(QtCore.QDateTime(2011,1,1,0,0))).toDateTime())
            self.dateTimeEdit_end_date.setDateTime(settings.value("%s_prop_date_end" % self.realm, QtCore.QVariant(QtCore.QDateTime(2012,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "123 ", ex

        self.retranslateUi()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выберите период", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Выберите период времени", None, QtGui.QApplication.UnicodeUTF8))
        self.label_start_date.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_date.setText(QtGui.QApplication.translate("Dialog", "Окончание", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_start_date.setDisplayFormat(QtGui.QApplication.translate("Dialog", "dd.MM.yyyy HH:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit_end_date.setDisplayFormat(QtGui.QApplication.translate("Dialog", "dd.MM.yyyy HH:mm:ss", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        pass
        #if self.model:
        #    self.dateTimeEdit_start_date.setDateTime(self.model.start_date)
        #    self.dateTimeEdit_end_date.setDateTime(self.model.end_date)
        
    def accept(self):
        self.start_date = self.dateTimeEdit_start_date.currentDate()
        self.end_date = self.dateTimeEdit_end_date.currentDate()
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("%s_prop_date_start" % self.realm, QtCore.QVariant(self.dateTimeEdit_start_date.dateTime()))
            settings.setValue("%s_prop_date_end" % self.realm, QtCore.QVariant(self.dateTimeEdit_end_date.dateTime()))
        except Exception, ex:
            print "settings save error: ", ex
        QtGui.QDialog.accept(self)
        
class GroupsDialog(QtGui.QDialog):
    def __init__(self, connection,default_id=None):
        super(GroupsDialog, self).__init__()
        self.connection = connection
        self.selected_group = -1
        self.default_id=default_id
        self.directions = {"1":u"Входящий", "2":u"Исходящий", "3":u"Сумма Вх + Исх", "4":u"Максимальный"}
        self.types = {"1":u"Сумма классов", "2":u"Максимальный класс"}
        self.setObjectName("GroupsDialog")
        self.resize(655, 278)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.commandLinkButton = QtGui.QCommandLinkButton(self)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.horizontalLayout.addWidget(self.commandLinkButton)
        self.commandLinkButton_2 = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")
        self.horizontalLayout.addWidget(self.commandLinkButton_2)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        
        self.connect(self.commandLinkButton, QtCore.SIGNAL("clicked()"), self.add_group)
        self.connect(self.commandLinkButton_2, QtCore.SIGNAL("clicked()"), self.del_group)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_group)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выберите группу трафика", None, QtGui.QApplication.UnicodeUTF8))
        columns = [u"#",u"Название группы",u"Классы",u"Направления", u"Тип"]
        makeHeaders(columns, self.tableWidget)
        
        self.commandLinkButton.setText(QtGui.QApplication.translate("Dialog", "Добавить группу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setDescription(QtGui.QApplication.translate("Dialog", "Добавить новую группу трафика", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_2.setText(QtGui.QApplication.translate("Dialog", "Удалить группу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_2.setDescription(QtGui.QApplication.translate("Dialog", "Удалить существующую группу", None, QtGui.QApplication.UnicodeUTF8))

    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        if y==0:
            headerItem.id=value
        if y!=0:
            if y==2:
                
                value = u", ".join(value)
                headerItem.setText(value)
            else:
                headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        
    def fixtures(self):
        groups = self.connection.groups_detail()
        self.connection.commit()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(groups))
        i=0
        for a in groups:
            
            self.addrow(a.id, i, 0)
            self.addrow(a.name, i, 1)
            self.addrow(a.classnames, i, 2)
            self.addrow(self.directions["%s" % a.direction], i, 3)
            self.addrow(self.types["%s" % a.type], i, 4)
            if a.id==self.default_id:
                self.tableWidget.selectRow(i)
            i+=1
        self.tableWidget.resizeColumnsToContents()
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).id)
    
    def add_group(self):
        child = GroupEditDialog(connection=self.connection)
        if child.exec_()==1:
            self.fixtures()
        
    def edit_group(self):
        model = self.connection.get_groups(id=self.getSelectedId())

        child = GroupEditDialog(connection=self.connection, model=model)
        if child.exec_()==1:
            self.fixtures()
        
    def del_group(self):
        if QtGui.QMessageBox.question(self, u"Удалить группу?" , u"При удалении группы будут удалены все её связи с лимитами трафика.\nВы уверены что хотите это сделать?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.group_delete(id = self.getSelectedId())
            self.connection.commit()
            self.fixtures()
    
    def accept(self):
        self.selected_group = self.getSelectedId()
        QtGui.QDialog.accept(self)
        
class GroupEditDialog(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(GroupEditDialog, self).__init__()
        self.connection=connection
        self.model = model
        self.directions = {"1":u"Входящий", "2":u"Исходящий", "3":u"Сумма Вх + Исх", "4":u"Максимальный"}
        self.types = {"1":u"Сумма классов", "2":u"Максимальный класс"}
        
        self.setObjectName("GroupEditDialog")
        self.resize(346, 376)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.groupBox_params = QtGui.QGroupBox(self)
        self.groupBox_params.setObjectName("groupBox_params")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_params)
        self.gridLayout.setObjectName("gridLayout")
        self.label_directions = QtGui.QLabel(self.groupBox_params)
        self.label_directions.setObjectName("label_directions")
        self.gridLayout.addWidget(self.label_directions, 0, 0, 1, 1)
        self.comboBox_directions = QtGui.QComboBox(self.groupBox_params)
        self.comboBox_directions.setObjectName("comboBox_directions")

        self.gridLayout.addWidget(self.comboBox_directions, 0, 1, 1, 1)
        self.comboBox_grouptype = QtGui.QComboBox(self.groupBox_params)
        self.comboBox_grouptype.setObjectName("comboBox_grouptype")

        self.gridLayout.addWidget(self.comboBox_grouptype, 1, 1, 1, 1)
        self.label_grouptype = QtGui.QLabel(self.groupBox_params)
        self.label_grouptype.setObjectName("label_grouptype")
        self.gridLayout.addWidget(self.label_grouptype, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_params, 2, 0, 1, 2)
        self.lineEdit_name = QtGui.QLineEdit(self)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout_2.addWidget(self.lineEdit_name, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.groupBox_classes = QtGui.QGroupBox(self)
        self.groupBox_classes.setObjectName("groupBox_classes")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_classes)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.listWidget_classes = QtGui.QListWidget(self.groupBox_classes)
        self.listWidget_classes.setObjectName("listWidget_classes")
        QtGui.QListWidgetItem(self.listWidget_classes)
        QtGui.QListWidgetItem(self.listWidget_classes)
        self.gridLayout_3.addWidget(self.listWidget_classes, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_classes, 1, 0, 1, 2)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование группы", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Название", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_params.setTitle(QtGui.QApplication.translate("Dialog", "Параметры группы", None, QtGui.QApplication.UnicodeUTF8))
        self.label_directions.setText(QtGui.QApplication.translate("Dialog", "Направление в классах", None, QtGui.QApplication.UnicodeUTF8))
        self.label_grouptype.setText(QtGui.QApplication.translate("Dialog", "Тип группы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_classes.setTitle(QtGui.QApplication.translate("Dialog", "Классы", None, QtGui.QApplication.UnicodeUTF8))
        #self.listWidget_classes.setSortingEnabled(True)

        
        
    def fixtures(self):
        
        selected_classes = []
        if self.model:
            self.setWindowTitle(u"Редактирование группы %s" % unicode(self.model.name))
            self.lineEdit_name.setText(unicode(self.model.name))
            selected_classes = self.connection.get_class_for_group(group=self.model.id) #sql("SELECT trafficclass_id as id FROM billservice_group_trafficclass WHERE group_id=%s" % self.model.id)
        classes = self.connection.get_trafficclasses()
        self.connection.commit()
        self.listWidget_classes.clear()
        for clas in classes:
            item = QtGui.QListWidgetItem(unicode(clas.name))
            item.setCheckState(QtCore.Qt.Unchecked)
            for x in selected_classes:
                if  clas.id in selected_classes: 
                    item.setCheckState(QtCore.Qt.Checked) 
                    
            item.id = clas.id
            self.listWidget_classes.addItem(item)
            
        
        
        i=0
        for direction in self.directions:
            self.comboBox_directions.addItem(self.directions[direction])
            self.comboBox_directions.setItemData(i, QtCore.QVariant(direction))
            if self.model:
                #print direction, self.model.direction,type(direction), type(self.model.direction) 
                if int(direction)==self.model.direction:
                    #print "current index=", i
                    self.comboBox_directions.setCurrentIndex(i)
            i+=1

        
        
        i=0
        for gtype in self.types:
            self.comboBox_grouptype.addItem(self.types[gtype])
            self.comboBox_grouptype.setItemData(i, QtCore.QVariant(gtype))
            if self.model:
                if int(gtype)==self.model.type:
                    #print "current index=", i
                    self.comboBox_grouptype.setCurrentIndex(i)
            i+=1            
        

            
    def accept(self):
        if self.model:
            model = self.model
        else:
            model = AttrDict()
            
        traffic_classes=[]
        for i in xrange(self.listWidget_classes.count()):
            clas = self.listWidget_classes.item(i)
            if clas.checkState()==QtCore.Qt.Checked:
                traffic_classes.append(clas.id)
        if unicode(self.lineEdit_name.text())=="" or self.listWidget_classes.count()==0 or traffic_classes==[]: 
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверьте введённые вами данные."))
            return
        
        try:
            
            
            model.name = u"%s" % self.lineEdit_name.text()
            model.direction = self.comboBox_directions.itemData(self.comboBox_directions.currentIndex()).toInt()[0]
            model.type = self.comboBox_grouptype.itemData(self.comboBox_grouptype.currentIndex()).toInt()[0]
            model.traffic_classes = traffic_classes
            self.connection.group_save(model)
            

            #Удаляем старые связи и добавляем только нужные новые
            #self.connection.command("DELETE FROM billservice_group_trafficclass WHERE group_id=%s;" % model.id)


            self.connection.commit()
        except Exception, e:
            self.connection.rollback()
            print e
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при создании группы."))
            return
        QtGui.QDialog.accept(self)


class SpeedLimitDialog(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(SpeedLimitDialog, self).__init__()
        self.setObjectName("SpeedLimitDialog")
        self.resize(421, 329)
        self.model = model
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.groupBox_speed_settings = QtGui.QGroupBox(self)
        self.groupBox_speed_settings.setObjectName("groupBox_speed_settings")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_speed_settings)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_tx = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_tx.setObjectName("label_tx")
        self.gridLayout_2.addWidget(self.label_tx, 4, 1, 1, 1)
        self.label_rx = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_rx.setObjectName("label_rx")
        self.gridLayout_2.addWidget(self.label_rx, 4, 2, 1, 1)
        self.label_max = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_max.setObjectName("label_max")
        self.gridLayout_2.addWidget(self.label_max, 5, 0, 1, 1)
        self.spinBox_max_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_max_tx.setMaximum(100000)
        self.spinBox_max_tx.setObjectName("spinBox_max_tx")
        self.gridLayout_2.addWidget(self.spinBox_max_tx, 5, 1, 1, 1)
        self.label_burst_treshold = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_burst_treshold.setObjectName("label_burst_treshold")
        self.gridLayout_2.addWidget(self.label_burst_treshold, 8, 0, 1, 1)
        self.spinBox_burst_treshold_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_treshold_tx.setMaximum(100000)
        self.spinBox_burst_treshold_tx.setObjectName("spinBox_burst_treshold_tx")
        self.gridLayout_2.addWidget(self.spinBox_burst_treshold_tx, 8, 1, 1, 1)
        self.label_burst_time = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_burst_time.setObjectName("label_burst_time")
        self.gridLayout_2.addWidget(self.label_burst_time, 9, 0, 1, 1)
        self.spinBox_burst_time_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_time_tx.setMaximum(100000)
        self.spinBox_burst_time_tx.setObjectName("spinBox_burst_time_tx")
        self.gridLayout_2.addWidget(self.spinBox_burst_time_tx, 9, 1, 1, 1)
        self.label_min = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_min.setObjectName("label_min")
        self.gridLayout_2.addWidget(self.label_min, 10, 0, 1, 1)
        self.spinBox_min_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_min_tx.setMaximum(100000)
        self.spinBox_min_tx.setObjectName("spinBox_min_tx")
        self.gridLayout_2.addWidget(self.spinBox_min_tx, 10, 1, 1, 1)
        self.label_priority = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_priority.setObjectName("label_priority")
        self.gridLayout_2.addWidget(self.label_priority, 11, 0, 1, 1)
        self.spinBox_priority = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_priority.setMinimum(1)
        self.spinBox_priority.setMaximum(8)
        self.spinBox_priority.setProperty("value", QtCore.QVariant(1))
        self.spinBox_priority.setObjectName("spinBox_priority")
        self.gridLayout_2.addWidget(self.spinBox_priority, 11, 1, 1, 1)
        self.label_burst = QtGui.QLabel(self.groupBox_speed_settings)
        self.label_burst.setObjectName("label_burst")
        self.gridLayout_2.addWidget(self.label_burst, 7, 0, 1, 1)
        self.spinBox_burst_tx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_tx.setMaximum(100000)
        self.spinBox_burst_tx.setObjectName("spinBox_burst_tx")
        self.gridLayout_2.addWidget(self.spinBox_burst_tx, 7, 1, 1, 1)
        self.spinBox_max_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_max_rx.setMaximum(100000)
        self.spinBox_max_rx.setObjectName("spinBox_max_rx")
        self.gridLayout_2.addWidget(self.spinBox_max_rx, 5, 2, 1, 1)
        self.spinBox_burst_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_rx.setMaximum(100000)
        self.spinBox_burst_rx.setObjectName("spinBox_burst_rx")
        self.gridLayout_2.addWidget(self.spinBox_burst_rx, 7, 2, 1, 1)
        self.spinBox_burst_treshold_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_treshold_rx.setMaximum(100000)
        self.spinBox_burst_treshold_rx.setObjectName("spinBox_burst_treshold_rx")
        self.gridLayout_2.addWidget(self.spinBox_burst_treshold_rx, 8, 2, 1, 1)
        self.spinBox_burst_time_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_burst_time_rx.setMaximum(100000)
        self.spinBox_burst_time_rx.setObjectName("spinBox_burst_time_rx")
        self.gridLayout_2.addWidget(self.spinBox_burst_time_rx, 9, 2, 1, 1)
        self.spinBox_min_rx = QtGui.QSpinBox(self.groupBox_speed_settings)
        self.spinBox_min_rx.setMaximum(100000)
        self.spinBox_min_rx.setObjectName("spinBox_min_rx")
        self.gridLayout_2.addWidget(self.spinBox_min_rx, 10, 2, 1, 1)
        self.comboBox_unit = QtGui.QComboBox(self.groupBox_speed_settings)
        self.comboBox_unit.setObjectName("comboBox_unit")
        self.gridLayout_2.addWidget(self.comboBox_unit, 2, 1, 1, 2)
        self.radioButton_speed_add = QtGui.QRadioButton(self.groupBox_speed_settings)
        self.radioButton_speed_add.setChecked(True)
        self.radioButton_speed_add.setObjectName("radioButton_speed_add")
        self.gridLayout_2.addWidget(self.radioButton_speed_add, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_speed_settings)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.radioButton_speed_abs = QtGui.QRadioButton(self.groupBox_speed_settings)
        self.radioButton_speed_abs.setObjectName("radioButton_speed_abs")
        self.gridLayout_2.addWidget(self.radioButton_speed_abs, 0, 2, 1, 1)
        self.pushButton_advanced = QtGui.QPushButton(self.groupBox_speed_settings)
        self.pushButton_advanced.setMinimumSize(QtCore.QSize(0, 0))
        self.pushButton_advanced.setMaximumSize(QtCore.QSize(16777215, 16))
        self.pushButton_advanced.setObjectName("pushButton_advanced")
        self.gridLayout_2.addWidget(self.pushButton_advanced, 6, 1, 1, 2)
        self.gridLayout.addWidget(self.groupBox_speed_settings, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.pushButton_advanced, QtCore.SIGNAL("clicked()"), self.advancedAction)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        self.layout().setSizeConstraint(QtGui.QLayout.SetFixedSize)
        #self.advancedAction()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Изменить скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_speed_settings.setTitle(QtGui.QApplication.translate("Dialog", "Настройки скорости", None, QtGui.QApplication.UnicodeUTF8))
        self.label_tx.setText(QtGui.QApplication.translate("Dialog", "TX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rx.setText(QtGui.QApplication.translate("Dialog", "RX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_max.setText(QtGui.QApplication.translate("Dialog", "MAX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst_treshold.setText(QtGui.QApplication.translate("Dialog", "Burst Treshold", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst_time.setText(QtGui.QApplication.translate("Dialog", "Burst time", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_burst_time_tx.setSuffix(QtGui.QApplication.translate("Dialog", " c", None, QtGui.QApplication.UnicodeUTF8))
        self.label_min.setText(QtGui.QApplication.translate("Dialog", "MIN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_priority.setText(QtGui.QApplication.translate("Dialog", "Priority", None, QtGui.QApplication.UnicodeUTF8))
        self.label_burst.setText(QtGui.QApplication.translate("Dialog", "Burst", None, QtGui.QApplication.UnicodeUTF8))
        self.spinBox_burst_time_rx.setSuffix(QtGui.QApplication.translate("Dialog", " c", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_speed_add.setText(QtGui.QApplication.translate("Dialog", "Добавить к текущей", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Единицы измерения", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_speed_abs.setText(QtGui.QApplication.translate("Dialog", "Абсолютные значения", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_advanced.setText(QtGui.QApplication.translate("Dialog", "Advanced", None, QtGui.QApplication.UnicodeUTF8))

    def advancedAction(self):
        if self.label_burst.isHidden()==False:
            self.label_burst.hide()
            self.spinBox_burst_tx.hide()
            self.spinBox_burst_rx.hide()
            self.label_burst_treshold.hide()
            self.spinBox_burst_treshold_tx.hide()
            self.spinBox_burst_treshold_rx.hide()
            self.label_burst_time.hide()
            self.spinBox_burst_time_tx.hide()
            self.spinBox_burst_time_rx.hide()
            self.label_min.hide()
            self.spinBox_min_tx.hide()
            self.spinBox_min_rx.hide()
            self.label_priority.hide()
            self.spinBox_priority.hide()
            self.setMaximumHeight(150)
            self.setMinimumHeight(150)
            

        else:
            self.label_burst.show()
            self.spinBox_burst_tx.show()
            self.spinBox_burst_rx.show()
            self.label_burst_treshold.show()
            self.spinBox_burst_treshold_tx.show()
            self.spinBox_burst_treshold_rx.show()
            self.label_burst_time.show()
            self.spinBox_burst_time_tx.show()
            self.spinBox_burst_time_rx.show()
            self.label_min.show()
            self.spinBox_min_tx.show()
            self.spinBox_min_rx.show()
            self.label_priority.show()
            self.spinBox_priority.show()
            self.setMaximumHeight(350)
            self.setMinimumHeight(350)

            
        
    def fixtures(self):
        
        x = ['Kbps', 'Mbps','%']
        i=0
        for a in x:
            self.comboBox_unit.addItem(unicode(a))
            
            if self.model:
                if self.model.speed_units == a:
                    self.comboBox_unit.setCurrentIndex(i)
            i+=1
                    
        if self.model:
            #self.model = self.connection.get_model(self.model.id, "billservice_speedlimit")
            #self.connection.commit()
            #print "fixturemodel", self.model
            if self.model.change_speed_type=='abs':
                self.radioButton_speed_abs.setChecked(True)
                
            self.spinBox_max_tx.setValue(int(self.model.max_tx))
            self.spinBox_max_rx.setValue(int(self.model.max_rx))
            #print int(self.model.burst_tx) or int(self.model.burst_rx) or int(self.model.burst_treshold_tx) or int(self.model.burst_treshold_rx) or int(self.model.burst_time_tx) or int(self.model.burst_time_rx) or int(self.model.min_tx) or int(self.model.min_rx)
            #print int(self.model.burst_tx) , int(self.model.burst_rx) , int(self.model.burst_treshold_tx) , int(self.model.burst_treshold_rx) , int(self.model.burst_time_tx) , int(self.model.burst_time_rx) , int(self.model.min_tx) , int(self.model.min_rx)
            if int(self.model.burst_tx) or int(self.model.burst_rx) or int(self.model.burst_treshold_tx) or int(self.model.burst_treshold_rx) or int(self.model.burst_time_tx) or int(self.model.burst_time_rx) or int(self.model.min_tx) or int(self.model.min_rx):
                self.spinBox_burst_tx.setValue(int(self.model.burst_tx))
                self.spinBox_burst_rx.setValue(int(self.model.burst_rx))
    
                self.spinBox_burst_treshold_tx.setValue(int(self.model.burst_treshold_tx))
                self.spinBox_burst_treshold_rx.setValue(int(self.model.burst_treshold_rx))
    
                self.spinBox_burst_time_tx.setValue(int(self.model.burst_time_tx))
                self.spinBox_burst_time_rx.setValue(int(self.model.burst_time_rx))
                
                self.spinBox_min_tx.setValue(int(self.model.min_tx))
                self.spinBox_min_rx.setValue(int(self.model.min_rx))
                
                self.spinBox_priority.setValue(int(self.model.priority))
                self.label_burst.show()
                self.spinBox_burst_tx.show()
                self.spinBox_burst_rx.show()
                self.label_burst_treshold.show()
                self.spinBox_burst_treshold_tx.show()
                self.spinBox_burst_treshold_rx.show()
                self.label_burst_time.show()
                self.spinBox_burst_time_tx.show()
                self.spinBox_burst_time_rx.show()
                self.label_min.show()
                self.spinBox_min_tx.show()
                self.spinBox_min_rx.show()
                self.label_priority.show()
                self.spinBox_priority.show()
            else:
                #self.spinBox_max_tx.setValue(0)
                #self.spinBox_max_rx.setValue(0)
                
                self.spinBox_burst_tx.setValue(0)
                self.spinBox_burst_rx.setValue(0)
    
                self.spinBox_burst_treshold_tx.setValue(0)
                self.spinBox_burst_treshold_rx.setValue(0)
    
                self.spinBox_burst_time_tx.setValue(0)
                self.spinBox_burst_time_rx.setValue(0)
                
                self.spinBox_min_tx.setValue(0)
                self.spinBox_min_rx.setValue(0)
                
                self.spinBox_priority.setValue(8)
                self.label_burst.hide()
                self.spinBox_burst_tx.hide()
                self.spinBox_burst_rx.hide()
                self.label_burst_treshold.hide()
                self.spinBox_burst_treshold_tx.hide()
                self.spinBox_burst_treshold_rx.hide()
                self.label_burst_time.hide()
                self.spinBox_burst_time_tx.hide()
                self.spinBox_burst_time_rx.hide()
                self.label_min.hide()
                self.spinBox_min_tx.hide()
                self.spinBox_min_rx.hide()
                self.label_priority.hide()
                self.spinBox_priority.hide()
            
        else:
            self.spinBox_max_tx.setValue(0)
            self.spinBox_max_rx.setValue(0)
            
            self.spinBox_burst_tx.setValue(0)
            self.spinBox_burst_rx.setValue(0)

            self.spinBox_burst_treshold_tx.setValue(0)
            self.spinBox_burst_treshold_rx.setValue(0)

            self.spinBox_burst_time_tx.setValue(0)
            self.spinBox_burst_time_rx.setValue(0)
            
            self.spinBox_min_tx.setValue(0)
            self.spinBox_min_rx.setValue(0)
            
            self.spinBox_priority.setValue(8)
            self.label_burst.hide()
            self.spinBox_burst_tx.hide()
            self.spinBox_burst_rx.hide()
            self.label_burst_treshold.hide()
            self.spinBox_burst_treshold_tx.hide()
            self.spinBox_burst_treshold_rx.hide()
            self.label_burst_time.hide()
            self.spinBox_burst_time_tx.hide()
            self.spinBox_burst_time_rx.hide()
            self.label_min.hide()
            self.spinBox_min_tx.hide()
            self.spinBox_min_rx.hide()
            self.label_priority.hide()
            self.spinBox_priority.hide()
            
    def accept(self):
        if self.model==None:
            self.model = AttrDict()
            
        self.model.speed_units = unicode(self.comboBox_unit.currentText())
        self.model.change_speed_type = "add" if self.radioButton_speed_add.isChecked() == True else "abs"
        self.model.max_tx = unicode(self.spinBox_max_tx.value())
        self.model.max_rx = unicode(self.spinBox_max_rx.value())
        
        if self.label_burst.isHidden()==False:
            self.model.burst_tx = unicode(self.spinBox_burst_tx.value())
            self.model.burst_rx = unicode(self.spinBox_burst_rx.value())
    
            self.model.burst_treshold_tx = unicode(self.spinBox_burst_treshold_tx.value())
            self.model.burst_treshold_rx = unicode(self.spinBox_burst_treshold_rx.value())
    
            self.model.burst_time_tx = unicode(self.spinBox_burst_time_tx.value())
            self.model.burst_time_rx = unicode(self.spinBox_burst_time_rx.value())
    
            self.model.min_tx = unicode(self.spinBox_min_tx.value())
            self.model.min_rx = unicode(self.spinBox_min_rx.value())
    
            self.model.priority = unicode(self.spinBox_priority.value())
        else:
            self.model.burst_tx = 0
            self.model.burst_rx = 0
    
            self.model.burst_treshold_tx = 0
            self.model.burst_treshold_rx = 0
    
            self.model.burst_time_tx = 0
            self.model.burst_time_rx = 0
    
            self.model.min_tx = 0
            self.model.min_rx = 0
    
            self.model.priority = 8
            
        #self.model.limit_id = self.limit_id
        #for x in self.model.__dict__:
        #    print x, self.model.__dict__[x]

        #self.model.id = self.connection.save(self.model, "billservice_speedlimit")
        #self.connection.commit()
        QtGui.QDialog.accept(self)


class SqlDialog(QtGui.QDialog):
    def __init__(self, connection):
        super(SqlDialog, self).__init__()
        self.connection = connection
        self.setObjectName("Dialog")
        self.resize(604, 358)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtGui.QPlainTextEdit(self)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "SQL Command Window", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def accept(self):
        
        if unicode(self.plainTextEdit.toPlainText()):
            try:
                self.connection.sql(unicode(self.plainTextEdit.toPlainText()))
                self.connection.commit()
                QtGui.QMessageBox.information(self, u"Ok", unicode(u"Запрос успешно выполнен."))
            except:
                self.connection.rollback()
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"При выполнении запроса возникла ошибка."))
                return
        else:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Введите текст запроса."))
            return
        QtGui.QDialog.accept(self)
    
        
class InfoDialog(QtGui.QDialog):
    def __init__(self, connection, type, account_id):
        super(InfoDialog, self).__init__()
        self.connection = connection
        self.connection.commit()
        self.type = type
        self.account_id = account_id
        self.first_time = True
        self.setObjectName("InfoDialog")
        dateDelim = '.'
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        self.resize(650, 300)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget= tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.dateTimeEdit = CustomDateTimeWidget()
        #self.dateTimeEdit.setSpecialValueText(_fromUtf8(""))
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setObjectName(_fromUtf8("dateTimeEdit"))
        self.gridLayout_2.addWidget(self.dateTimeEdit, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        if self.type != "limit":
            QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.prepaidTrafficCellEdit)
        if self.type != 'settlementperiods':
            self.groupBox.setHidden(True)
        
        if self.type == 'settlementperiods':
            QtCore.QObject.connect(self.dateTimeEdit, QtCore.SIGNAL("dateTimeChanged(const QDateTime&)"), self.refresh)
            
        QtCore.QMetaObject.connectSlotsByName(self)
        self.refresh()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Информация", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.dateTimeEdit.setDisplayFormat(QtGui.QApplication.translate("Dialog", "dd.MM.yyyy H:mm:ss", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Начало периодов в опцией автостарт", None, QtGui.QApplication.UnicodeUTF8))
        
    def prepaidTrafficCellEdit(self,y,x):
        if self.type=='radiusprepaidtraffic':
            
            if x==2:
                item = self.tableWidget.item(y,x)
                try:
                    default_text=float(item.raw_value/1048576)
                except Exception, e:
                    print e
                    default_text=0
                
                text = QtGui.QInputDialog.getDouble(self, u"Осталось МБ:", u"Количество мегабайт", default_text,0,99999999999,2)      
               
                if text[1]:
                    item=QtGui.QTableWidgetItem(unicode(text[0]))
                    item.raw_value=int(text[0])*1048576
                    self.tableWidget.setItem(y,x, item)     
                    id=self.getSelectedId(self.tableWidget)
                    
                    if id>0:
                        model = self.connection.get_accountprepaysradiustrafic(id)
                        model.size=int(text[0])*1048576
                        self.connection.accountprepaysradiustrafic_save(model)
        elif self.type=='prepaidtraffic':
            if x==3:
                item = self.tableWidget.item(y,x)
                try:
                    default_text=float(item.raw_value/1048576)
                except Exception, e:
                    print e
                    default_text=0
                
                text = QtGui.QInputDialog.getDouble(self, u"Осталось МБ:", u"Введите количество мегабайт", default_text,0,99999999999,2)      
               
                if text[1]:
                    item=QtGui.QTableWidgetItem(unicode(text[0]))
                    item.raw_value=int(text[0])*1048576
                    self.tableWidget.setItem(y,x, item)     
                    id=self.getSelectedId(self.tableWidget)
                    
                    if id>0:
                        model = self.connection.get_accountprepaystraffic(id)
                        model.size=int(text[0])*1048576
                        self.connection.accountprepaystrafic_save(model)
            
            
    def addrow(self, value, x, y, id=None, raw_value=None, color=None, enabled=True, ctext=None, setdata=False, widget = None):
        headerItem = QtGui.QTableWidgetItem()
        if value==None:
            value=''
        if color:
            if float(value)<0:
                headerItem.setBackgroundColor(QtGui.QColor(color))
                headerItem.setTextColor(QtGui.QColor('#ffffff'))
            elif float(value)==0:
                headerItem.setBackgroundColor(QtGui.QColor("#ffdc51"))
                #headerItem.setTextColor(QtGui.QColor('#ffffff'))
                                
        if not enabled:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        
            
        if y==1:
            if enabled==True:
                if self.type=='settlementperiods':
                    headerItem.setIcon(QtGui.QIcon("images/sp.png"))
                else:
                    headerItem.setIcon(QtGui.QIcon("images/user.png"))
            else:
                headerItem.setIcon(QtGui.QIcon("images/user_inactive.png"))
        if setdata:
            headerItem.setData(39, QtCore.QVariant(value))   
        if ctext is not None:
            headerItem.setText(unicode(ctext))
        else:
            headerItem.setText(unicode(value))
        
        headerItem.id = id
        headerItem.raw_value = raw_value
        self.tableWidget.setItem(x,y,headerItem)
    
    def getSelectedId(self, table):
        try:
            return int(table.item(table.currentRow(), 0).id)
        except:
            return -1
        
    def refresh(self):
        
        if self.type == "limit":
            columns=["#", u"Название", u"Всего", u"Израсходовано", u"Осталось", u"Начало", u"Окончание"]
            makeHeaders(columns, self.tableWidget)
            items = self.connection.get_limites(self.account_id)

            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:            
                self.addrow(i, i,0)
                self.addrow(a['limit_name'], i,1)
                self.addrow("%s MB" % (a['limit_size']/1048576), i,2)
                self.addrow("%s MB" % int((a['size'] or 0)/1048576), i,3)
                self.addrow("%s MB" % (int((a['limit_size']-a['size']) or 0)/1048576), i,4)
                try:
                    self.addrow(a.get('settlement_period_start').strftime(self.strftimeFormat), i,5)
                    self.addrow(a.get('settlement_period_end').strftime(self.strftimeFormat), i,6)
                except Exception, e:
                    print e
                i+=1
            self.tableWidget.resizeColumnsToContents()
            
        elif self.type=='prepaidtraffic':
            columns=["#", u"Группа", u"Всего", u"Осталось", u"Дата начисления", u"Активно"]
            makeHeaders(columns, self.tableWidget)
            items = self.connection.sql("""
            SELECT   ppt.id as ppt_id, ppt.size as size, ppt.datetime, pp.size as pp_size, (SELECT name FROM billservice_group WHERE id=pp.group_id) as group_name, ppt.datetime as datetime, ppt.current FROM billservice_accountprepaystrafic as ppt
            LEFT JOIN billservice_prepaidtraffic as pp ON pp.id=ppt.prepaid_traffic_id
            WHERE account_tarif_id=(SELECT id FROM billservice_accounttarif WHERE account_id=%s and datetime<now() ORDER BY datetime DESC LIMIT 1) ORDER BY ppt.datetime DESC;""" % (self.account_id,)            
            )

            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:            
                self.addrow(i, i,0, id=a.ppt_id)
                self.addrow(a.group_name, i,1)
                self.addrow("%s MB" % int((a.pp_size or 0)/(1048576)), i, 2)
                self.addrow("%s MB" % int((a.size or 0)/1048576.00), i, 3, raw_value=a.size)
                self.addrow(a.datetime.strftime(strftimeFormat), i,4)
                self.addrow(a.current, i,5)
                i+=1
            self.tableWidget.resizeColumnsToContents()    
        elif self.type=='radiusprepaidtraffic':
            columns=["#", u"Направление", u"Осталось", u"Дата начисления", u"Активно"]
            makeHeaders(columns, self.tableWidget)
            items = self.connection.sql("""
            SELECT apst.id, apst.size, apst.direction, apst.datetime, apst.current FROM billservice_accountprepaysradiustrafic as apst 
            JOIN billservice_accounttarif as act ON act.id=apst.account_tarif_id
            WHERE act.account_id=%s ORDER BY apst.datetime DESC;""" % (self.account_id,)            
            )
            direction_types = [u"Входящий", u"Исходящий", u"Вх.+Исх.", u"Большее направление"]
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:            
                self.addrow(i, i,0, id=a.id)
                self.addrow(direction_types[a.direction], i,1)
                self.addrow("%s MB" % int((a.size or 0)/(1048576)), i, 2, raw_value=a.size)
                self.addrow(a.datetime.strftime(strftimeFormat), i, 3)
                self.addrow(a.current, i, 4)
                i+=1
            self.tableWidget.resizeColumnsToContents()  
        elif self.type=='radiusprepaidtime':
            columns=["#", u"Осталось", u"Дата начисления", u"Активно"]
            makeHeaders(columns, self.tableWidget)
            items = self.connection.sql("""
            SELECT apst.id, apst.size, apst.datetime, apst.current FROM billservice_accountprepaystime as apst 
            JOIN billservice_accounttarif as act ON act.id=apst.account_tarif_id
            WHERE act.account_id=%s ORDER BY apst.datetime DESC;""" % (self.account_id,)            
            )
            #direction_types = [u"Входящий", u"Исходящий", u"Вх.+Исх.", u"Большее направление"]
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:            
                self.addrow(i, i,0, id=a.id)
                self.addrow(u"%s мин." % int((a.size or 0)/(60)), i, 1, raw_value=a.size)
                self.addrow(a.datetime.strftime(strftimeFormat), i, 2)
                self.addrow(a.current, i, 3)
                i+=1
            self.tableWidget.resizeColumnsToContents()  
        elif self.type=='settlementperiods':
            columns=["#", u"Название периода ", u'Длина', u'Начало', u'Конец' ]
            makeHeaders(columns, self.tableWidget)
            
            account_datetime = self.connection.get("""
            SELECT datetime FROM billservice_accounttarif
            WHERE account_id=%s and datetime<now() order BY datetime desc LIMIT 1;""" % (self.account_id,)            
            )
            
            if self.first_time:
                self.dateTimeEdit.setDateTime(account_datetime.datetime)
                self.first_time=False
            items = self.connection.sql("""SELECT * FROM billservice_settlementperiod;""")

            
            #settlement_period_info(time_start, repeat_after='', repeat_after_seconds=0,  now=None, prev = False)
            
            self.connection.commit()
            self.tableWidget.setRowCount(len(items))
            i=0
            for a in items:
                if a.autostart:
                    time_start=self.dateTimeEdit.currentDate()
                else:
                    time_start = a.time_start
                start, end, length = settlement_period_info(time_start, repeat_after=a.length_in, repeat_after_seconds=a.length)            
                self.addrow(i, i,0, id=a.id)
                self.addrow(a.name, i,1)
                self.addrow(length, i, 2)
                self.addrow(start.strftime(strftimeFormat), i, 3)
                self.addrow(end.strftime(strftimeFormat), i, 4)
                i+=1
            self.tableWidget.resizeColumnsToContents()   
               

        
class RadiusAttrsDialog(QtGui.QDialog):
    def __init__(self, tarif_id=None, nas_id=None, connection=None):
        super(RadiusAttrsDialog, self).__init__()
        self.tarif_id = tarif_id
        self.nas_id=nas_id
        self.connection = connection
        
        self.setObjectName("RadiusAttrsDialog")
        self.resize(450, 475)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox_edit = QtGui.QGroupBox(self)
        self.groupBox_edit.setObjectName("groupBox_edit")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_edit)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_vendor = QtGui.QLabel(self.groupBox_edit)
        self.label_vendor.setObjectName("label_vendor")
        self.gridLayout_3.addWidget(self.label_vendor, 0, 0, 1, 1)
        self.lineEdit_vendor = QtGui.QLineEdit(self.groupBox_edit)
        self.lineEdit_vendor.setObjectName("lineEdit_vendor")
        self.gridLayout_3.addWidget(self.lineEdit_vendor, 0, 1, 1, 1)
        self.label_attrid = QtGui.QLabel(self.groupBox_edit)
        self.label_attrid.setObjectName("label_attrid")
        self.gridLayout_3.addWidget(self.label_attrid, 0, 2, 1, 1)
        self.lineEdit_attrid = QtGui.QLineEdit(self.groupBox_edit)
        self.lineEdit_attrid.setObjectName("lineEdit_attrid")
        self.gridLayout_3.addWidget(self.lineEdit_attrid, 0, 3, 1, 1)
        self.label_value = QtGui.QLabel(self.groupBox_edit)
        self.label_value.setObjectName("label_value")
        self.gridLayout_3.addWidget(self.label_value, 0, 4, 1, 1)
        self.lineEdit_value = QtGui.QLineEdit(self.groupBox_edit)
        self.lineEdit_value.setObjectName("lineEdit_value")
        self.gridLayout_3.addWidget(self.lineEdit_value, 0, 5, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.commandLinkButton_add = QtGui.QCommandLinkButton(self.groupBox_edit)
        self.commandLinkButton_add.setCheckable(False)
        self.commandLinkButton_add.setObjectName("commandLinkButton_add")
        self.horizontalLayout.addWidget(self.commandLinkButton_add)
        self.commandLinkButton_del = QtGui.QCommandLinkButton(self.groupBox_edit)
        self.commandLinkButton_del.setObjectName("commandLinkButton_del")
        self.horizontalLayout.addWidget(self.commandLinkButton_del)
        self.gridLayout_3.addLayout(self.horizontalLayout, 1, 0, 1, 6)
        self.gridLayout_2.addWidget(self.groupBox_edit, 0, 0, 1, 1)
        self.groupBox_table = QtGui.QGroupBox(self)
        self.groupBox_table.setObjectName("groupBox_table")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_table)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtGui.QTableWidget(self.groupBox_table)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_table, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.commandLinkButton_add, QtCore.SIGNAL("clicked()"), self.save)
        QtCore.QObject.connect(self.commandLinkButton_del, QtCore.SIGNAL("clicked()"), self.delete)
        #self.connect(self.tableWidget, QtCore.SIGNAL("itemClicked(QTableWidgetItem *)"), self.set_data)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройка RADIUS атрибутов", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_edit.setTitle(QtGui.QApplication.translate("Dialog", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vendor.setText(QtGui.QApplication.translate("Dialog", "Vendor ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_attrid.setText(QtGui.QApplication.translate("Dialog", "Attr.ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_value.setText(QtGui.QApplication.translate("Dialog", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add.setText(QtGui.QApplication.translate("Dialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_add.setDescription(QtGui.QApplication.translate("Dialog", "Поместить в таблицу", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_del.setDescription(QtGui.QApplication.translate("Dialog", "Удалить из таблицы", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_table.setTitle(QtGui.QApplication.translate("Dialog", "Сохранённые значения", None, QtGui.QApplication.UnicodeUTF8))
        columns = ["Vendor ID", "Attr ID", "Value"]
        makeHeaders(columns, self.tableWidget)
        
    def addrow(self, value, x, y, id=None):
        headerItem = QtGui.QTableWidgetItem()
        if id:
            headerItem.id=id

        headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        
#===============================================================================
#    def set_data(self):
#        id = self.getSelectedId()
#        item = self.connection.get_model(id, "billservice_radiusattrs")
#        self.connection.commit()
#        self.lineEdit_vendor.setText(unicode(item.vendor))
#        self.lineEdit_attrid.setText(unicode(item.attrid))
#        self.lineEdit_value.setText(unicode(item.value))
#===============================================================================
        
    def save(self):
        model = AttrDict()
        if self.tarif_id:
            model.tarif = self.tarif_id
        elif self.nas_id:
            model.nas = self.nas_id
        model.vendor = unicode(self.lineEdit_vendor.text()) or 0
        model.attrid = unicode(self.lineEdit_attrid.text())
        model.value = unicode(self.lineEdit_value.text())
        print "self.nas_id", self.nas_id

            
        self.connection.radiusattrs_save(model)
        self.connection.commit()


        self.fixtures()
      
    def delete(self):
        id = self.getSelectedId()
        self.connection.radiusattrs_delete(id)
        self.connection.commit()
        self.fixtures()
              
    def getSelectedId(self):
        return self.tableWidget.item(self.tableWidget.currentRow(), 0).id
    
    def fixtures(self):
        if self.tarif_id:
            attrs = self.connection.get_radiusattrs(tarif_id=self.tarif_id)
        elif self.nas_id:
            attrs = self.connection.get_radiusattrs(nas_id=self.nas_id)
        else:
            return
        self.connection.commit()
        self.tableWidget.setRowCount(len(attrs))
        i=0
        for attr in attrs:
            #print attr.vendor
            self.addrow(attr.vendor, i, 0, id = attr.id)
            self.addrow(attr.attrid, i, 1)
            self.addrow(attr.value, i, 2)
            i+=1
            

class PSCreatedForm(QtGui.QDialog):
    def __init__(self, date, only_date=False):
        super(PSCreatedForm, self).__init__()
        self.date = date
        self.only_date = only_date
        self.setObjectName("PSCreatedForm")
        self.resize(266, 95)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.dateTimeEdit = CustomDateTimeWidget()
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.gridLayout.addWidget(self.dateTimeEdit, 0, 0, 1, 1)
        self.checkBox_as_start_ps = QtGui.QCheckBox(self)
        self.checkBox_as_start_ps.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox_as_start_ps, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        self.checkBoxAction()
        if self.only_date:
            self.checkBox_as_start_ps.setHidden(True)
        self.connect(self.checkBox_as_start_ps, QtCore.SIGNAL("stateChanged(int)"), self.checkBoxAction)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        #self.connect(self.checkBox_temporary_blocked, QtCore.SIGNAL("stateChanged(int)"), self.checkBox_temporary_blockedAction)
        
        #QtCore.QMetaObject.connectSlotsByName(self)
        
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки периодической услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_as_start_ps.setText(QtGui.QApplication.translate("Dialog", "С начала расчётного периода", None, QtGui.QApplication.UnicodeUTF8))
        
        
    def checkBoxAction(self):
        if self.checkBox_as_start_ps.checkState() == QtCore.Qt.Checked:
            self.dateTimeEdit.setDisabled(True)
        else:
            self.dateTimeEdit.setDisabled(False)
            
        if self.only_date:
            self.dateTimeEdit.setDisabled(False)
            
            
    def fixtures(self):
        if self.date:
            self.dateTimeEdit.setDateTime(self.date)
        else:
            self.checkBox_as_start_ps.setChecked(True)
            self.dateTimeEdit.setDateTime(datetime.datetime.now())
            
            
    def accept(self):
        if self.checkBox_as_start_ps.checkState() == QtCore.Qt.Checked:
            self.date = None
        else:
            self.date = self.dateTimeEdit.currentDate()
        QtGui.QDialog.accept(self)
        
        
class AccountAddonServiceEdit(QtGui.QDialog):
    def __init__(self, connection, model=None, account_model = None, subaccount_model = None):
        super(AccountAddonServiceEdit, self).__init__()
        self.setObjectName("AccountAddonServiceEdit")
        self.model = model
        self.account_model = account_model
        self.subaccount_model = subaccount_model
        self.connection = connection
        self.resize(437, 194)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_service = QtGui.QLabel(self.groupBox)
        self.label_service.setObjectName("label_service")
        self.gridLayout.addWidget(self.label_service, 0, 0, 1, 1)
        self.comboBox_service = QtGui.QComboBox(self.groupBox)
        self.comboBox_service.setObjectName("comboBox_service")
        self.gridLayout.addWidget(self.comboBox_service, 0, 1, 1, 2)
        self.label_activation = QtGui.QLabel(self.groupBox)
        self.label_activation.setObjectName("label_activation")
        self.gridLayout.addWidget(self.label_activation, 1, 0, 1, 1)
        self.dateTimeEdit_activation = CustomDateTimeWidget()
        self.dateTimeEdit_activation.setCalendarPopup(True)
        self.dateTimeEdit_activation.setObjectName("dateTimeEdit_activation")
        self.gridLayout.addWidget(self.dateTimeEdit_activation, 1, 1, 1, 2)
        self.toolButton_activation_now = QtGui.QToolButton(self.groupBox)
        self.toolButton_activation_now.setObjectName("toolButton_activation_now")
        self.gridLayout.addWidget(self.toolButton_activation_now, 1, 3, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setChecked(False)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_deactivation = QtGui.QLabel(self.groupBox_2)
        self.label_deactivation.setObjectName("label_deactivation")
        self.gridLayout_3.addWidget(self.label_deactivation, 0, 0, 1, 1)
        self.dateTimeEdit_deactivation = CustomDateTimeWidget()
        self.dateTimeEdit_deactivation.setMinimumSize(QtCore.QSize(230, 0))
        self.dateTimeEdit_deactivation.setCalendarPopup(True)
        self.dateTimeEdit_deactivation.setObjectName("dateTimeEdit_deactivation")
        self.gridLayout_3.addWidget(self.dateTimeEdit_deactivation, 0, 1, 1, 1)
        self.toolButton_deactivation = QtGui.QToolButton(self.groupBox_2)
        self.toolButton_deactivation.setObjectName("toolButton_deactivation")
        self.gridLayout_3.addWidget(self.toolButton_deactivation, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 3, 0, 1, 4)
        self.checkBox_temporary_blocked = QtGui.QCheckBox(self.groupBox)
        self.checkBox_temporary_blocked.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox_temporary_blocked.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox_temporary_blocked, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.toolButton_activation_now,QtCore.SIGNAL("clicked()"),self.setActivatedTime)
        QtCore.QObject.connect(self.toolButton_deactivation,QtCore.SIGNAL("clicked()"),self.setDeactivatedTime)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры подключаемой услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры подключаемой услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_service.setText(QtGui.QApplication.translate("Dialog", "Услуга", None, QtGui.QApplication.UnicodeUTF8))
        self.label_activation.setText(QtGui.QApplication.translate("Dialog", "Дата активации", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_activation_now.setText(QtGui.QApplication.translate("Dialog", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Закончить действие услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.label_deactivation.setText(QtGui.QApplication.translate("Dialog", "Дата деактивации", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_deactivation.setText(QtGui.QApplication.translate("Dialog", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_temporary_blocked.setText(QtGui.QApplication.translate("Dialog", "Временная блокировка", None, QtGui.QApplication.UnicodeUTF8))
    
    def fixtures(self):
        addonservices = self.connection.get_addonservices(normal_fields=False)
        print "addonservices", addonservices
        self.connection.commit()
        i=0
        for adds in addonservices:
           self.comboBox_service.addItem(unicode(adds.name))
           self.comboBox_service.setItemData(i, QtCore.QVariant(adds.id))
           i+=1
        
        if self.model:
            for i in xrange(self.comboBox_service.count()):
                if self.comboBox_service.itemData(i).toInt()[0]==self.model.service:
                    self.comboBox_service.setCurrentIndex(i)
                       

            self.checkBox_temporary_blocked.setChecked(self.model.temporary_blocked is not None)
            if self.model.deactivated:
                self.groupBox_2.setDisabled(True)
            self.dateTimeEdit_activation.setDateTime(self.model.activated)
            
            if self.model.deactivated:
                self.dateTimeEdit_deactivation.setDateTime(self.model.deactivated)
                self.dateTimeEdit_deactivation.setDisabled(True)
                
            self.comboBox_service.setDisabled(True)
        else:
            self.dateTimeEdit_activation.setDateTime(datetime.datetime.now())
            self.dateTimeEdit_deactivation.setDateTime(datetime.datetime.now())
            
    def accept(self):
        if self.model:
            model = self.model
        else:
            model = AttrDict()
        if self.account_model:    
            model.account = self.account_model
        if self.subaccount_model:    
            model.subaccount = self.subaccount_model.id
            model.account = self.subaccount_model.account
            
        model.service = self.comboBox_service.itemData(self.comboBox_service.currentIndex()).toInt()[0]
        date = self.dateTimeEdit_activation.currentDate()
        date = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
        model.activated = date
        if self.model:
            if not self.model.temporary_blocked:
                model.temporary_blocked = "now()" if   self.checkBox_temporary_blocked.isChecked()==True else None
            elif self.checkBox_temporary_blocked.isChecked()==False:
                model.temporary_blocked = None
        else:
            model.temporary_blocked = "now()" if   self.checkBox_temporary_blocked.isChecked()==True else None
            
        
        if self.groupBox_2.isChecked()==True:
            if self.dateTimeEdit_deactivation.currentDate()<model.activated:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Дата окончания действия услуги не должна быть меньше даты начала действия"))
                return
            date = self.dateTimeEdit_deactivation.currentDate()
            date = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
            model.deactivated = date
            

        if not self.connection.accountaddonservice_save(model):
            return

        
        QtGui.QDialog.accept(self)
    
    def setActivatedTime(self):
        self.dateTimeEdit_activation.setDateTime(datetime.datetime.now())

    def setDeactivatedTime(self):
        self.dateTimeEdit_deactivation.setDateTime(datetime.datetime.now())
        
class IPAddressSelectForm(QtGui.QDialog):
    def __init__(self, connection, pool_id, default_ip=''):
        super(IPAddressSelectForm, self).__init__()
        self.connection = connection
        self.pool_id = pool_id
        self.selected_ip = None
        self.default_ip = default_ip
        self.setObjectName("IPAddressSelectForm")
        self.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, -1)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox_only_pool = QtGui.QCheckBox(self)
        self.checkBox_only_pool.setChecked(True)
        self.gridLayout.addWidget(self.checkBox_only_pool, 0, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.checkBox_only_pool, QtCore.SIGNAL("stateChanged(int)"), self.refresh)
        QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.accept)
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Свободные IP адреса в выбранном пуле", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_only_pool.setText(QtGui.QApplication.translate("Dialog", "Только не занятые из этого пула", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget = tableFormat(self.tableWidget)
        columns=['#', 'IP']
        makeHeaders(columns, self.tableWidget)
        self.refresh()

        
    def accept(self):
        self.selected_ip = unicode(self.tableWidget.item(self.tableWidget.currentRow(),1).text())
        QtGui.QDialog.accept(self)
    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        if y==1:
            headerItem.setIcon(QtGui.QIcon("images/tp_small.png"))
        if y==0:
            headerItem.id=value
            #headerItem.setCheckState(QtCore.Qt.Unchecked)
        if y!=0:
            headerItem.setText(unicode(value))
        self.tableWidget.setItem(x,y,headerItem)
        
    def refresh(self):
        items = get_free_addreses_from_pool(self.connection, self.pool_id, only_from_pool=self.checkBox_only_pool.isChecked(), default_ip=self.default_ip)
        self.connection.commit()
        self.tableWidget.setRowCount(len(items))
        i=0
        for item in items:
            self.addrow('', i, 0)
            self.addrow(item, i, 1)
            i+=1
            
        self.tableWidget.resizeColumnsToContents()
            
        
class TransactionForm(QtGui.QDialog):
    def __init__(self, connection, model=None, account=None):
        super(TransactionForm, self).__init__()
        self.model = model
        self.account = account
        self.connection = connection
        self.transaction = None 
        self.printer = None
        self.resize(474, 300)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.summ_label = QtGui.QLabel(self.groupBox)
        self.summ_label.setObjectName(_fromUtf8("summ_label"))
        self.gridLayout.addWidget(self.summ_label, 1, 0, 1, 1)
        self.summ_edit = QtGui.QLineEdit(self.groupBox)
        self.summ_edit.setObjectName(_fromUtf8("summ_edit"))
        self.summ_edit.setFocus(True)
        self.gridLayout.addWidget(self.summ_edit, 1, 1, 1, 1)
        self.payed_document_label = QtGui.QLabel(self.groupBox)
        self.payed_document_label.setObjectName(_fromUtf8("payed_document_label"))
        self.gridLayout.addWidget(self.payed_document_label, 2, 0, 1, 1)
        self.payed_document_edit = QtGui.QLineEdit(self.groupBox)
        self.payed_document_edit.setFrame(True)
        self.payed_document_edit.setObjectName(_fromUtf8("payed_document_edit"))
        self.gridLayout.addWidget(self.payed_document_edit, 2, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 3, 1, 1, 1)
        self.label_paymend_date = QtGui.QLabel(self.groupBox)
        self.label_paymend_date.setObjectName(_fromUtf8("label_paymend_date"))
        self.gridLayout.addWidget(self.label_paymend_date, 4, 0, 1, 1)
        self.dateTimeEdit_paymend_date = CustomDateTimeWidget()
        self.gridLayout.addWidget(self.dateTimeEdit_paymend_date, 4, 1, 1, 1)
        self.label_promise = QtGui.QLabel(self.groupBox)
        self.label_promise.setObjectName(_fromUtf8("label_promise"))
        self.gridLayout.addWidget(self.label_promise, 5, 0, 1, 1)
        self.checkBox_promise = QtGui.QCheckBox(self.groupBox)
        self.checkBox_promise.setObjectName(_fromUtf8("checkBox_promise"))
        self.gridLayout.addWidget(self.checkBox_promise, 5, 1, 1, 1)
        self.label_end_promise = QtGui.QLabel(self.groupBox)
        self.label_end_promise.setObjectName(_fromUtf8("label_end_promise"))
        self.gridLayout.addWidget(self.label_end_promise, 6, 0, 1, 1)
        self.dateTimeEdit_end_promise = CustomDateTimeWidget()
        self.dateTimeEdit_end_promise.setObjectName(_fromUtf8("dateTimeEdit_end_promise"))
        self.gridLayout.addWidget(self.dateTimeEdit_end_promise, 6, 1, 1, 1)
        self.checkBox_promise_infinite = QtGui.QCheckBox(self.groupBox)
        self.checkBox_promise_infinite.setObjectName(_fromUtf8("checkBox_promise_infinite"))
        self.gridLayout.addWidget(self.checkBox_promise_infinite, 6, 2, 1, 1)
        self.pay_type_label = QtGui.QLabel(self.groupBox)
        self.pay_type_label.setObjectName(_fromUtf8("pay_type_label"))
        self.gridLayout.addWidget(self.pay_type_label, 0, 0, 1, 1)
        self.comboBox_transactiontype = QtGui.QComboBox(self.groupBox)
        self.comboBox_transactiontype.setObjectName(_fromUtf8("comboBox_transactiontype"))
        self.gridLayout.addWidget(self.comboBox_transactiontype, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 1, 3)
        self.pushButton_pay = QtGui.QPushButton(self)
        self.pushButton_pay.setDefault(True)
        self.pushButton_pay.setObjectName(_fromUtf8("pushButton_pay"))
        self.gridLayout_2.addWidget(self.pushButton_pay, 2, 0, 1, 1)
        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_2.addWidget(self.pushButton, 2, 1, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout_2.addWidget(self.pushButton_2, 2, 2, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.pushButton_pay,QtCore.SIGNAL("clicked()"),self.pay)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),self.cheque_print)
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),self.reject)
        QtCore.QObject.connect(self.checkBox_promise,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)
        QtCore.QObject.connect(self.checkBox_promise_infinite,QtCore.SIGNAL("stateChanged(int)"),self.promise_actions)

        self.setTabOrder(self.comboBox_transactiontype, self.summ_edit)
        self.setTabOrder(self.summ_edit, self.payed_document_edit)
        self.setTabOrder(self.payed_document_edit, self.lineEdit)
        self.setTabOrder(self.lineEdit, self.dateTimeEdit_paymend_date)
        self.setTabOrder(self.dateTimeEdit_paymend_date, self.checkBox_promise)
        self.setTabOrder(self.checkBox_promise, self.dateTimeEdit_end_promise)
        self.setTabOrder(self.dateTimeEdit_end_promise, self.checkBox_promise_infinite)
        self.setTabOrder(self.checkBox_promise_infinite, self.pushButton_pay)
        self.setTabOrder(self.pushButton_pay, self.pushButton)
        self.setTabOrder(self.pushButton, self.pushButton_2)
        #QtCore.QObject.connect(self.pushButton_cheque_print,QtCore.SIGNAL("clicked()"),self.cheque_print)
        
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        self._name = settings.value("user", QtCore.QVariant("")).toString()

        self.fixtures()
        self.promise_actions()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Платёжные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.summ_label.setText(QtGui.QApplication.translate("Dialog", "Сумма", None, QtGui.QApplication.UnicodeUTF8))
        self.payed_document_label.setText(QtGui.QApplication.translate("Dialog", "На основании док.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_paymend_date.setText(QtGui.QApplication.translate("Dialog", "Дата платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_promise.setText(QtGui.QApplication.translate("Dialog", "Обещаный платёж", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_promise.setText(QtGui.QApplication.translate("Dialog", "Да", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_promise.setText(QtGui.QApplication.translate("Dialog", "Истекает", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_promise_infinite.setText(QtGui.QApplication.translate("Dialog", "Никогда", None, QtGui.QApplication.UnicodeUTF8))
        self.pay_type_label.setText(QtGui.QApplication.translate("Dialog", "Тип платежа", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_pay.setText(QtGui.QApplication.translate("Dialog", "Оплатить", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Печать чека", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("Dialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setDisabled(True)

    def fixtures(self):
        now = datetime.datetime.now()
        self.dateTimeEdit_paymend_date.setDateTime(now)
        self.dateTimeEdit_end_promise.setDateTime(now)
    
        items = self.connection.get_transactiontypes()
        
        self.comboBox_transactiontype.clear()
        i=0
        for item in items:
            self.comboBox_transactiontype.addItem(item.name, userData=QtCore.QVariant(item.internal_name))
            if item.internal_name==u'MANUAL_TRANSACTION':
                self.comboBox_transactiontype.setCurrentIndex(i)
            i+=1
                
        #self.payed_type_edit.setItemData(0, QtCore.QVariant(0))
        #self.payed_type_edit.setItemData(1, QtCore.QVariant(1))
        
    def promise_actions(self):
        if self.checkBox_promise.isChecked():
            self.dateTimeEdit_end_promise.setEnabled(True)
            self.checkBox_promise_infinite.setEnabled(True)
            if self.checkBox_promise_infinite.isChecked():
                self.dateTimeEdit_end_promise.setEnabled(False)
            
        else:
            self.dateTimeEdit_end_promise.setEnabled(False)
            self.checkBox_promise_infinite.setEnabled(False)
            
    def pay(self):
        #print self.payed_type_edit.itemData(self.payed_type_edit.currentIndex()).toInt()[0]
        
        self.result = Decimal("%s" % self.summ_edit.text()) * (-1)
        
        transaction = AttrDict()
        transaction.account=self.account.id
        transaction.type = unicode(self.comboBox_transactiontype.itemData(self.comboBox_transactiontype.currentIndex()).toString())
        transaction.approved = True
        transaction.description = unicode(self.lineEdit.text())
        transaction.summ=self.result
        transaction.bill=unicode(self.payed_document_edit.text())
        transaction.created = self.dateTimeEdit_paymend_date.currentDate()
        
        transaction.promise = self.checkBox_promise.isChecked()
        if self.checkBox_promise.isChecked() and not self.checkBox_promise_infinite.isChecked():
            transaction.end_promise = self.dateTimeEdit_end_promise.currentDate()


        try:
            d = self.connection.make_transaction(transaction)
            if d.status==False:
                QtGui.QMessageBox.warning(self, unicode(u"Ошибка"), unicode('\n'.join(["%s %s" % (x, ';'.join(d.errors.get(x))) for x in d.errors])))
                return
            
            transaction.id = d.transaction_id
            print "transaction.id",transaction.id
            self.transaction = transaction
            self.connection.commit()
            self.pushButton_pay.setDisabled(True)
            self.pushButton.setDisabled(False)
        except Exception, e:
            print "Exception", e
            self.connection.rollback()
        #
        
    def reject(self):
        QtGui.QDialog.accept(self)
        
    def cheque_print(self):
        if not self.printer:
            #QtGui.QMessageBox.warning(self, unicode(u"Ок"), unicode(u"Настройка принтера не была произведена!"))
            self.getPrinter()
        
        template = self.connection.get_templates(type_id=5)[0]
        
        print template.body
        templ = Template(unicode(template.body), input_encoding='utf-8')
        account = self.connection.get_account(id=self.transaction.account)

        tarif = self.connection.get_tariff_for_account(id = account.id)
        #transaction = self.connection.get("SELECT * FROM billservice_transaction WHERE id=%s" % self.transaction)
        transaction = self.transaction
        self.connection.commit()
        sum = 10000
        transaction.summ = transaction.summ*(-1)
        try:
            data=templ.render_unicode(connection=self.connection, account=account, tarif=tarif, transaction=transaction)

        except Exception, e:
            data=unicode(u""" <html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body style="text-align:center;">%s</body></html>""" % repr(e))

        
        #it seem that software printers can change the path!
        file= open('templates/tmp/temp.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        file.close()
        
        a=CardPreviewDialog(url="templates/tmp/temp.html", printer=self.printer)
        a.exec_()
            
    def getPrinter(self):
        printer = QtGui.QPrinter()
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Печать"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        self.printer = printer
        
        
class TemplateSelect(QtGui.QDialog):
    def __init__(self, connection):
        super(TemplateSelect, self).__init__()
        self.connection = connection
        self.id = None
        self.setObjectName("TemplateSelect")
        self.resize(504, 243)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.listWidget, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.accept)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Выбор шаблона", None, QtGui.QApplication.UnicodeUTF8))


    def fixtures(self):
        templates = self.connection.get_templates(fields=['id', 'name'])
        
        self.listWidget.clear()
        for templ in templates:
            item = QtGui.QListWidgetItem()
            item.setText(unicode(templ.name))
            item.id = templ.id
            self.listWidget.addItem(item)
            
    def accept(self):
        self.id = self.listWidget.currentItem().id
        QtGui.QDialog.accept(self)


class ContractTemplateEdit(QtGui.QDialog):
    def __init__(self, connection, model=None):
        super(ContractTemplateEdit, self).__init__()
        self.model=model
        self.connection = connection
        self.setObjectName(_fromUtf8("ContractTemplateEdit"))
        self.resize(478, 210)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setScaledContents(False)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout_2.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.pushButton_delete = QtGui.QPushButton(self)
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.gridLayout.addWidget(self.pushButton_delete, 1, 1, 1, 1)
        
        self.pushButton_test = QtGui.QPushButton(self)
        self.pushButton_test.setObjectName(_fromUtf8("pushButton_test"))
        self.gridLayout.addWidget(self.pushButton_test, 1, 2, 1, 1)
        
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QObject.connect(self.pushButton_delete, QtCore.SIGNAL(_fromUtf8("clicked()")), self.delete)
        QtCore.QObject.connect(self.pushButton_test, QtCore.SIGNAL(_fromUtf8("clicked()")), self.test)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fixtures()
        self.pushButton_test.setFocus(True)
        self.buttonBox.setDisabled(True)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("ContractTemplateEdit", "Редактирование шаблона номера договора", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ContractTemplateEdit", "Шаблон номера договора", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ContractTemplateEdit", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">%(tarif_id)i</span><span style=\" font-size:8pt;\"> - идентификатор тарифа</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">%(contract_num)i</span><span style=\" font-size:8pt;\"> - номер заключаемого договора этого типа</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\"> %(account_id)i</span><span style=\" font-size:8pt;\"> - идентификатор аккаунта</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">%(day)i,%(month)i,%(year)i,%(hour)i,%(minute)i,%(second)i</span><span style=\" font-size:8pt;\"> - дата подключения на тариф</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">%(tarif_type)s</span><span style=\" font-size:8pt;\"> - тип тарифного плана</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_delete.setText(QtGui.QApplication.translate("Dialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_test.setText(QtGui.QApplication.translate("Dialog", "Проверить", None, QtGui.QApplication.UnicodeUTF8))

    def accept(self):
        template = unicode(self.lineEdit.text())
        
        if template:
            if self.model:
                model=self.model
            else:
                model = AttrDict()
                
            model.template=template
            model.counter=0
            self.connection.contracttemplate_save(model)
            self.connection.commit()
        QtGui.QDialog.accept(self)
        
    def delete(self):
        if self.model:
            self.connection.contracttemplate_delete(self.model.id)
            self.connection.commit()
        QtGui.QDialog.accept(self)
        
    def fixtures(self):
        if self.model:
            self.lineEdit.setText(unicode(self.model.template))
            
    def test(self):
        try:
            d={'comment': u'', 'username': u'22196', 'allow_webcab': True, 'allow_ipn_with_minus': False, 'city_id': 1, 'house': u'', 
            'ipn_speed': u'', 'vpn_ip_address': '0.0.0.0', 'postcode': u'', 'suspended': True, 'systemuser_id': 1, 
            'allow_vpn_block': True, 'allow_vpn_null': True, 'id': 32, 'row': u'', 'ipn_mac_address': u'', 
            'assign_ipn_ip_from_dhcp': False, 'contactperson_phone': u'', 'ipn_status': False, 'entrance_code': u'', 
            'passport_date': u'', 'elevator_direction': u'', 'passport': u'', 'ipn_ipinuse_id': None, 'nas_id': 0, 
            'last_balance_null': datetime.datetime(2011, 9, 1, 23, 57, 32, 872284), 'email': u'', 'status': 1, 
            'entrance': u'', 'phone_m': u'8-029-870-35-52 \u042e\u0440\u0438\u0439', 'associate_pptp_ipn_ip': False, 
            'street_id': 8, 'phone_h': u'228-03-97', 'city': u'', 'allow_ipn_with_block': False, 'vlan': None, 
            'allow_expresscards': False, 'assign_dhcp_block': True, 'netmask': '0.0.0.0/0', 'address': u'', 
            'private_passport_number': u'', 'password': u'YURA1194', 'associate_pppoe_mac': False, 'ipn_added': False, 
            'vpn_ipinuse_id': None, 'disabled_by_limit': False, 'balance_blocked': False, 'house_id': 51, 'room': u'54', 
            'created': datetime.datetime(2011, 6, 21, 14, 58, 27, 599000), 'region': u'', 'contract': u'22196', 'assign_dhcp_null': True, 
            'credit': u'0', 'ballance': u'-38860.72777777777777777777777780', 'street': u'', 
            'contactperson': u'Иван Иванов', 'ipn_ip_address': '0.0.0.0', 'house_bulk': u'', 
            'fullname': u'Иванов Иван', 'vpn_speed': u'', 'allow_ipn_with_null': False, 'passport_given': u'',
            'tarif_id':111, 'account_id':99,'year':2011,'month':11, 'day':22, 'hour':9, 'minute':4,'second':59, 'tarif_type':'VPN', 'contract_num':44}
            result = unicode(self.lineEdit.text()) % d
            QtGui.QMessageBox.information(self, u"Успешно", unicode(u"Проверка синтаксиса завершилась успешно.\nРезультат:%s" % result))
            self.buttonBox.setDisabled(False)
        except Exception, e:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Проверка синтаксиса завершилась неудачно. %s" % str(e)))
            
        
            