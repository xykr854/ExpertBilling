#-*-coding=utf-8*-
import sys
from PyQt4 import QtCore, QtGui

from helpers import Object
from helpers import connlogin
import Pyro.core
import Pyro.protocol
import Pyro.constants



import mdi_rc

from AccountFrame import AccountsMdiChild
from NasFrame import NasMdiChild
from SettlementPeriodFrame import SettlementPeriodChild
from TimePeriodFrame import TimePeriodChild
from ClassFrame import ClassChild
from MonitorFrame import MonitorFrame
from SystemUser import SystemUserChild
from CustomForms import ConnectDialog
from Reports import ReportPropertiesDialog, NetFlowReport, StatReport, ReportSelectDialog


#add speed "Загрузка канала пользователем"
# общая трафик/загрузка по типам
#динамика прибыли (кредит)
#трафик пользователей (пирог)
#скорость по портам
#сессии пользователей
#загрузка канала
#общий трафик/загрузка
#использование канала пользователями
_reportsdict = [['report3_classes.xml', ['nfs_total_classes_speed'], 'Загрузка по направлениям'],\
                ['report3_tus_nas.xml', ['nfs_u_traf'], 'Трафик пользователей'], \
                ['report3_nass.xml', ['nfs_n_traf'], 'Загрузка по серверам доступа'],\
                ['report3_pie.xml', ['userstrafpie'], 'Трафик пользователей (пирог)'], \
                ['report3_port.xml', ['nfs_port_speed'], 'Скорость по портам'], \
                ['report3_sess.xml', ['sessions'], 'Сессии пользователей'], \
                ['report3_tr.xml', ['trans_crd'], 'Динамика прибыли'], \
                ['report3_ttr_nas.xml', ['nfs_total_traf'], 'Общий трафик'], \
                ['report3_tutr_nas.xml', ['nfs_total_traf_bydir'], 'Общий трафик по типам']\
               ]

#разделитель для дат по умолчанию
dateDelim = "."

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.workspace = QtGui.QWorkspace()
        self.setCentralWidget(self.workspace)





        self.connect(self.workspace, QtCore.SIGNAL("windowActivated(QWidget *)"), self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle(u"Expert Billing Client 0.2")

    def closeEvent(self, event):
        self.workspace.closeAllWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
    
    @connlogin
    def newFile(self):
        child =  AccountsMdiChild(connection=connection, parent=self)
        self.workspace.addWindow(child)
        child.show()

    def open(self):
        child = NasMdiChild(connection=connection)
        self.workspace.addWindow(child)
        child.show()
        return child


    def save(self):
        child=SettlementPeriodChild(connection=connection)
        self.workspace.addWindow(child)
        child.show()

        #if self.activeMdiChild().save():
        #    self.statusBar().showMessage(self.tr("File saved"), 2000)

    def saveAs(self):

        child = SystemUserChild(connection=connection)
        self.workspace.addWindow(child)
        child.show()

    def cut(self):
        child=TimePeriodChild(connection=connection)
        self.workspace.addWindow(child)
        child.show()

    def copy(self):
        child=ClassChild(connection=connection)
        self.workspace.addWindow(child)
        child.show()

    def paste(self):
        child = MonitorFrame(connection=connection)
        self.workspace.addWindow(child)
        child.show()

    def about(self):
        QtGui.QMessageBox.about(self, self.tr(u"О программе"),
            self.tr(u"Expert Billing Client- клиентское приложение, предназначенное для конфигурирования<br> серверной части сстемы."))

    def reportProperties(self):
        child = ReportPropertiesDialog(connection = connection)
        self.workspace.addWindow(child)
        child.show()

    def netflowReport(self):
        child = NetFlowReport(connection = connection)
        self.workspace.addWindow(child)
        child.show()

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        #self.saveAct.setEnabled(hasMdiChild)
        #self.saveAsAct.setEnabled(hasMdiChild)
        self.pasteAct.setEnabled(True)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.arrangeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)


    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.workspace.windowList()

        self.separatorAct.setVisible(len(windows) != 0)

        i = 0

        for child in windows:
            if i < 9:
                text = self.tr("&%1 %2").arg(i + 1).arg(child.userFriendlyCurrentFile())
            else:
                text = self.tr("%1 %2").arg(i + 1).arg(child.userFriendlyFile())

            i += 1

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.windowMapper, QtCore.SLOT("map()"))
            self.windowMapper.setMapping(action, child)



    def openstatWin(self):
        self.reportseldg = ReportSelectDialog(connection=connection)
        if self.reportseldg.exec_()!=1: return
        #print self.reportseldg.zomgdata
        #print self.reportseldg.selectedId
        #f = open('tmp1', 'wb')
        #f.write(str(self.reportseldg.chartinfo))
        if self.reportseldg.selectedId != -1:
            child=StatReport(connection=connection, chartinfo=self.reportseldg.chartinfo[self.reportseldg.selectedId])
            self.workspace.addWindow(child)
            child.show()
        
    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon("images/accounts.png"),
                            self.tr("&New"), self)
        self.newAct.setShortcut(self.tr("Ctrl+N"))
        self.newAct.setStatusTip(self.tr("Create a new file"))
        self.connect(self.newAct, QtCore.SIGNAL("triggered()"), self.newFile)

        self.openAct = QtGui.QAction(QtGui.QIcon("images/nas.png"),
                        self.tr("&Open..."), self)
        self.openAct.setShortcut(self.tr("Ctrl+O"))
        self.openAct.setStatusTip(self.tr("Open an existing file"))
        self.connect(self.openAct, QtCore.SIGNAL("triggered()"), self.open)

        self.saveAct = QtGui.QAction(QtGui.QIcon("images/sp.png"),
                        self.tr("&Save"), self)
        self.saveAct.setShortcut(self.tr("Ctrl+S"))
        self.saveAct.setStatusTip(self.tr("Save the document to disk"))
        self.connect(self.saveAct, QtCore.SIGNAL("triggered()"), self.save)

        self.saveAsAct = QtGui.QAction(self.tr("Save &As..."), self)
        self.saveAsAct.setStatusTip(self.tr("Save the document under a new name"))
        self.connect(self.saveAsAct, QtCore.SIGNAL("triggered()"), self.saveAs)

        self.exitAct = QtGui.QAction(self.tr("E&xit"), self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(self.tr("Exit the application"))
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"), self.close)

        self.cutAct = QtGui.QAction(QtGui.QIcon("images/tp.png"),
                        self.tr("Cu&t"), self)
        self.cutAct.setShortcut(self.tr("Ctrl+X"))
        self.cutAct.setStatusTip(self.tr("Cut the current selection's "
                                         "contents to the clipboard"))
        self.connect(self.cutAct, QtCore.SIGNAL("triggered()"), self.cut)

        self.copyAct = QtGui.QAction(QtGui.QIcon("images/tc.png"),
                        self.tr("&Copy"), self)
        self.copyAct.setShortcut(self.tr("Ctrl+C"))
        self.copyAct.setStatusTip(self.tr("Copy the current selection's "
                                          "contents to the clipboard"))
        self.connect(self.copyAct, QtCore.SIGNAL("triggered()"), self.copy)

        self.pasteAct = QtGui.QAction(QtGui.QIcon(":/images/paste.png"),
                        self.tr("&Paste"), self)
        self.pasteAct.setShortcut(self.tr("Ctrl+V"))
        self.pasteAct.setStatusTip(self.tr("Paste the clipboard's contents "
                                           "into the current selection"))

        self.connect(self.pasteAct, QtCore.SIGNAL("triggered()"), self.paste)

        self.reportPropertiesAct = QtGui.QAction(QtGui.QIcon(":/images/paste.png"),
                        self.tr("&Paste"), self)
        #self.reportPropertiesAct.setShortcut(self.tr("Ctrl+V"))
        self.reportPropertiesAct.setStatusTip(self.tr("Настройка отчёта "))

        self.connect(self.reportPropertiesAct, QtCore.SIGNAL("triggered()"), self.reportProperties)
        
        self.netflowReportAct=QtGui.QAction(QtGui.QIcon(":/images/paste.png"), self.tr("&NetFlow"), self)
        
        self.netflowReportAct.setStatusTip(self.tr("Net Flow отчёт "))

        self.connect(self.netflowReportAct, QtCore.SIGNAL("triggered()"), self.netflowReport)

        self.reportActs = []
        i = 0
        for item in _reportsdict:
            rAct = QtGui.QAction(self.trUtf8(item[2]), self)
            rAct.setStatusTip(self.tr("Report"))
            rAct.setData(QtCore.QVariant(i))
            self.connect(rAct, QtCore.SIGNAL("triggered()"), self.reportsMenu)
            self.reportActs.append(rAct)
            i += 1

        self.closeAct = QtGui.QAction(self.tr("Cl&ose"), self)
        self.closeAct.setShortcut(self.tr("Ctrl+F4"))
        self.closeAct.setStatusTip(self.tr("Close the active window"))
        self.connect(self.closeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveWindow)

        self.closeAllAct = QtGui.QAction(self.tr("Close &All"), self)
        self.closeAllAct.setStatusTip(self.tr("Close all the windows"))
        self.connect(self.closeAllAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction(self.tr("&Tile"), self)
        self.tileAct.setStatusTip(self.tr("Tile the windows"))
        self.connect(self.tileAct, QtCore.SIGNAL("triggered()"), self.workspace.tile)

        self.cascadeAct = QtGui.QAction(self.tr("&Cascade"), self)
        self.cascadeAct.setStatusTip(self.tr("Cascade the windows"))
        self.connect(self.cascadeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascade)

        self.arrangeAct = QtGui.QAction(self.tr("Arrange &icons"), self)
        self.arrangeAct.setStatusTip(self.tr("Arrange the icons"))
        self.connect(self.arrangeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction(self.tr("Ne&xt"), self)
        self.nextAct.setShortcut(self.tr("Ctrl+F6"))
        self.nextAct.setStatusTip(self.tr("Move the focus to the next window"))
        self.connect(self.nextAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction(self.tr("Pre&vious"), self)
        self.previousAct.setShortcut(self.tr("Ctrl+Shift+F6"))
        self.previousAct.setStatusTip(self.tr("Move the focus to the previous "
                                              "window"))
        self.connect(self.previousAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtGui.QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.connect(self.aboutAct, QtCore.SIGNAL("triggered()"), self.about)

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.connect(self.aboutQtAct, QtCore.SIGNAL("triggered()"),
                     QtGui.qApp, QtCore.SLOT("aboutQt()"))
        
        self.statwinAct = QtGui.QAction(self.tr("Statwin"), self)

        self.statwinAct.setStatusTip(self.tr("Open the reports window"))
        self.connect(self.statwinAct, QtCore.SIGNAL("triggered()"),
                     self.openstatWin)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)

        self.windowMenu = self.menuBar().addMenu(self.tr("&Window"))
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)
        self.reportsMenu = self.menuBar().addMenu(self.tr("&Reports"))
        for act in self.reportActs:
            self.reportsMenu.addAction(act)
            
        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)
    
    def reportsMenu(self):
        #print self.sender().data().toInt()
        child=StatReport(connection=connection, chartinfo=_reportsdict[self.sender().data().toInt()[0]])
        self.workspace.addWindow(child)
        child.show()
    def createToolBars(self):
        self.fileToolBar = self.addToolBar(self.tr("File"))
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar(self.tr("Edit"))
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)
        self.editToolBar.addAction(self.reportPropertiesAct)
        self.editToolBar.addAction(self.netflowReportAct)
        self.editToolBar.addAction(self.statwinAct)
        
    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))

    def readSettings(self):
        settings = QtCore.QSettings("Trolltech", "MDI Example")
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(400, 400))).toSize()
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings("Trolltech", "MDI Example")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))

    def activeMdiChild(self):
        return self.workspace.activeWindow()

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.workspace.windowList():
            if window.currentFile() == canonicalFilePath:
                return window
        return None

'''class LoginConnValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
	Pyro.protocol.DefaultConnValidator.__init__(self)
	
    def acceptIdentification(self, daemon, connection, token, challenge):
	# extract tuple (login, processed password) from token as returned by createAuthToken
	# processed password is a hmac hash from the server's challenge string and the password itself.
	print "acceptIdentification_client"
	login, processedpassword = token.split(':', 1)
	try:
            obj = connection.get("SELECT * FROM billservice_systemuser WHERE username='%s'" % username)
        except Exception, e:
	    print "acceptIdentification query error"
            print e
            return (0,Pyro.constants.DENIED_SECURITY)
	
        print "connection_____request"

	knownpasswdhash = obj.password
	# Check if the username/password is valid.
	if knownpasswdhash:
		# Known passwords are stored as ascii hash, but the auth token contains a binary hash.
		# So we need to convert our ascii hash to binary to be able to validate.
		knownpasswdhash=knownpasswdhash.decode("hex")
		if hmac.new(challenge,knownpasswdhash).digest() == processedpassword:
			print "ALLOWED", login
			connection.create("UPDATE billservice_systemuser SET last_login=now() WHERE id=%d;" % obj.id)
			connection.authenticated=login  # store for later reference by Pyro object
			return(1,0)
	print "DENIED",login
	return (0,Pyro.constants.DENIED_SECURITY)
	    
    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
	print "createAuthToken"
	# authid is what mungeIdent returned, a tuple (login, hash-of-password)
	# we return a secure auth token based on the server challenge string.
	return "%s:%s" % (authid[0], hmac.new(challenge,authid[1]).digest() )

    def mungeIdent(self, ident):
	print "mungeIdent_client"
	print ident
	print ident[1].decode("hex")
	# ident is tuple (login, password), the client sets this.
	# we don't like to store plaintext passwords so store the md5 hash instead.
	return (ident[0], ident[1].decode("hex")) '''
class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
	Pyro.protocol.DefaultConnValidator.__init__(self)
    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
	print "createAuthToken_cli"
	print challenge
	# authid is what mungeIdent returned, a tuple (login, hash-of-password)
	# we return a secure auth token based on the server challenge string.
	return authid
    def mungeIdent(self, ident):
	print "mungeIdent_client"
	print ident
	# ident is tuple (login, password), the client sets this.
	# we don't like to store plaintext passwords so store the md5 hash instead.
	return ident
'''def setIdentification(self, ident, munge=False):
	if ident:
		if munge:
			self.ident=self.newConnValidator.mungeIdent(ident)   # don't store ident itself. 
		else:
			self.ident=ident # per-munged ident string
	else:
		self.ident='' '''      
def login():
    child = ConnectDialog()
    if child.exec_()==1:
        try:
            #child.address= '127.0.0.1'
            #print child.address
            #print child.name
            #child.name = 'admin'
            connection = Pyro.core.getProxyForURI("PYROLOC://%s:7766/rpc" % unicode(child.address))
            password = unicode(child.password.toHex())
            #f = open('tmp', 'wb')
            #f.write(child.password.toHex())
	    connection._setNewConnectionValidator(antiMungeValidator())
	    #connection.adapter.setIdentification = setIdentification
	    print connection._setIdentification("%s:%s" % (str(child.name), str(child.password.toHex())))
            if connection.connection_request(username=unicode(child.name), password=password)==False:
                QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Неверно введены данные."))
                login()
	    #connection._setNewConnectionValidator(LoginConnValidator())
            #connection._setIdentification((unicode(child.name),password))
	    '''print "tryutoken-------"
	    print connection.utoken
	    connection.utoken = "hhh"
	    print connection.utoken'''
        except Exception, e:
            print "login connection error"
            print e
            QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Невозможно подключиться к серверу."))
            login()
        return connection
    else:
        sys.exit()
                
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
   
    connection = login() 
    try:
	mainwindow = MainWindow()
	mainwindow.show()
	#app.setStyle("cleanlooks")
	app.setStyleSheet(open("./style.qss","r").read())
	sys.exit(app.exec_())
    except Exception, ex:
	print "main-----------"
	print ex

    #QtGui.QStyle.SH_Table_GridLineColor
    
