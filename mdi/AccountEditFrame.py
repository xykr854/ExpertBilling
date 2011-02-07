#-*-coding=utf-8-*-


from PyQt4 import QtCore, QtGui

import traceback
import psycopg2
from ebsWindow import ebsTable_n_TreeWindow
from db import Object as Object
from helpers import dateDelim
from helpers import connlogin
from helpers import setFirstActive
from helpers import tableHeight
from helpers import HeaderUtil, SplitterUtil, transip
from types import BooleanType
import copy

from randgen import nameGen, GenPasswd2
import datetime, time, calendar
from time import mktime
from CustomForms import RadiusAttrsDialog, CheckBoxDialog, ComboBoxDialog, SpeedEditDialog , TransactionForm
import time
from Reports import TransactionsReportEbs as TransactionsReport, SimpleReportEbs

from helpers import tableFormat, check_speed
from helpers import transaction, makeHeaders
from helpers import Worker
from CustomForms import simpleTableImageWidget, tableImageWidget, IPAddressSelectForm, TemplateSelect, RrdReportMainWindow
from CustomForms import CustomWidget, CardPreviewDialog, SuspendedPeriodForm, GroupsDialog, SpeedLimitDialog, InfoDialog, PSCreatedForm, AccountAddonServiceEdit
from MessagesFrame import MessageDialog
from mako.template import Template
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
qtTimeFormat = "YYYY-MM-DD HH:MM:SS"
import IPy

class CashType(object):
    def __init__(self, id, name):
        self.id = id
        self.name=name
        
cash_types = [CashType(0, "AT_START"), CashType(1,"AT_END"), CashType(2, "GRADUAL")]

limit_actions = [CashType(0, u"Заблокировать пользователя"), CashType(1,u"Изменить скорость")]

la_list = [u"Заблокировать пользователя", u"Изменить скорость"]

ps_conditions = [CashType(0, u"При любом балансе"), CashType(1,u"При положительном и нулевом балансе"), CashType(2,u"При отрицательном балансе"), CashType(3,u"При положительнои балансе")]
ps_list = [u"При любом балансе", u"При положительном и нулевом балансе", u"При отрицательном балансе", u"При положительнои балансе"]

class SubaccountLinkDialog(QtGui.QDialog):
    def __init__(self, connection, account, model = None):
        super(SubaccountLinkDialog, self).__init__()
        #self.setObjectName("SubaccountLinkDialog")
        self.connection = connection
        self.account = account
        self.model = model
        self.resize(690, 729)
        self.gridLayout_2 = QtGui.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_3 = QtGui.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_link_parameters = QtGui.QGroupBox(self.tab)
        self.groupBox_link_parameters.setObjectName("groupBox_link_parameters")
        self.gridLayout = QtGui.QGridLayout(self.groupBox_link_parameters)
        self.gridLayout.setObjectName("gridLayout")
        self.label_nas = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout.addWidget(self.label_nas, 0, 1, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout.addWidget(self.comboBox_nas, 0, 2, 1, 1)
        self.label_link_login = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_login.setObjectName("label_link_login")
        self.gridLayout.addWidget(self.label_link_login, 1, 1, 1, 1)
        self.lineEdit_link_login = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_login.setObjectName("lineEdit_link_login")
        self.gridLayout.addWidget(self.lineEdit_link_login, 1, 2, 1, 3)
        self.label_link_password = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_password.setObjectName("label_link_password")
        self.gridLayout.addWidget(self.label_link_password, 3, 1, 1, 1)
        self.lineEdit_link_password = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_password.setObjectName("lineEdit_link_password")
        self.gridLayout.addWidget(self.lineEdit_link_password, 3, 2, 1, 3)
        self.label_link_vpn_ip_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_vpn_ip_address.setObjectName("label_link_vpn_ip_address")
        self.gridLayout.addWidget(self.label_link_vpn_ip_address, 5, 1, 1, 1)
        self.lineEdit_vpn_ip_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_ip_address.setObjectName("lineEdit_vpn_ip_address")
        self.gridLayout.addWidget(self.lineEdit_vpn_ip_address, 5, 2, 1, 1)
        self.comboBox_vpn_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_vpn_pool.setObjectName("comboBox_vpn_pool")
        self.gridLayout.addWidget(self.comboBox_vpn_pool, 5, 3, 1, 2)
        self.label_link_vpn = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_vpn.setObjectName("label_link_vpn")
        self.gridLayout.addWidget(self.label_link_vpn, 7, 1, 1, 1)
        self.lineEdit_ipn_ip_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_ip_address.setObjectName("lineEdit_ipn_ip_address")
        self.gridLayout.addWidget(self.lineEdit_ipn_ip_address, 7, 2, 1, 1)
        self.comboBox_ipn_pool = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_ipn_pool.setObjectName("comboBox_ipn_pool")
        self.gridLayout.addWidget(self.comboBox_ipn_pool, 7, 3, 1, 2)
        self.label_link_ipn_mac_address = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_ipn_mac_address.setObjectName("label_link_ipn_mac_address")
        self.gridLayout.addWidget(self.label_link_ipn_mac_address, 8, 1, 1, 1)
        self.lineEdit_link_ipn_mac_address = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_link_ipn_mac_address.setObjectName("lineEdit_link_ipn_mac_address")
        self.gridLayout.addWidget(self.lineEdit_link_ipn_mac_address, 8, 2, 1, 4)
        self.label_link_switch = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_switch.setObjectName("label_link_switch")
        self.gridLayout.addWidget(self.label_link_switch, 9, 1, 1, 1)
        self.comboBox_link_switch_id = QtGui.QComboBox(self.groupBox_link_parameters)
        self.comboBox_link_switch_id.setObjectName("comboBox_link_switch_id")
        self.gridLayout.addWidget(self.comboBox_link_switch_id, 9, 2, 1, 4)
        self.label_link_port = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_link_port.setObjectName("label_link_port")
        self.gridLayout.addWidget(self.label_link_port, 10, 1, 1, 1)
        self.spinBox_link_port = QtGui.QSpinBox(self.groupBox_link_parameters)
        self.spinBox_link_port.setMaximum(512)
        self.spinBox_link_port.setObjectName("spinBox_link_port")
        self.gridLayout.addWidget(self.spinBox_link_port, 10, 2, 1, 4)
        self.label_vpn_speed = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_vpn_speed.setObjectName("label_vpn_speed")
        self.gridLayout.addWidget(self.label_vpn_speed, 24, 1, 1, 1)
        self.lineEdit_vpn_speed = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_vpn_speed.setObjectName("lineEdit_vpn_speed")
        self.gridLayout.addWidget(self.lineEdit_vpn_speed, 24, 2, 1, 5)
        self.label_ipn_speed = QtGui.QLabel(self.groupBox_link_parameters)
        self.label_ipn_speed.setObjectName("label_ipn_speed")
        self.gridLayout.addWidget(self.label_ipn_speed, 25, 1, 1, 1)
        self.lineEdit_ipn_speed = QtGui.QLineEdit(self.groupBox_link_parameters)
        self.lineEdit_ipn_speed.setObjectName("lineEdit_ipn_speed")
        self.gridLayout.addWidget(self.lineEdit_ipn_speed, 25, 2, 1, 5)
        self.checkBox_allow_addonservice = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_addonservice.setObjectName("checkBox_allow_addonservice")
        self.gridLayout.addWidget(self.checkBox_allow_addonservice, 23, 1, 1, 6)
        self.checkBox_associate_pppoe_ipn_mac = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_associate_pppoe_ipn_mac.setObjectName("checkBox_associate_pppoe_ipn_mac")
        self.gridLayout.addWidget(self.checkBox_associate_pppoe_ipn_mac, 22, 1, 1, 5)
        self.checkBox_associate_pptp_ipn_ip = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_associate_pptp_ipn_ip.setObjectName("checkBox_associate_pptp_ipn_ip")
        self.gridLayout.addWidget(self.checkBox_associate_pptp_ipn_ip, 21, 1, 1, 5)
        self.checkBox_allow_vpn_with_null = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_vpn_with_null.setObjectName("checkBox_allow_vpn_with_null")
        self.gridLayout.addWidget(self.checkBox_allow_vpn_with_null, 15, 1, 1, 5)
        self.checkBox_allow_vpn_with_block = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_vpn_with_block.setObjectName("checkBox_allow_vpn_with_block")
        self.gridLayout.addWidget(self.checkBox_allow_vpn_with_block, 17, 1, 1, 5)
        self.checkBox_allow_vpn_with_minus = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_vpn_with_minus.setObjectName("checkBox_allow_vpn_with_minus")
        self.gridLayout.addWidget(self.checkBox_allow_vpn_with_minus, 16, 1, 1, 5)
        self.checkBox_allow_dhcp_with_block = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_block.setObjectName("checkBox_allow_dhcp_with_block")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp_with_block, 14, 1, 1, 5)
        self.checkBox_allow_dhcp_with_minus = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_minus.setObjectName("checkBox_allow_dhcp_with_minus")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp_with_minus, 13, 1, 1, 5)
        self.checkBox_allow_dhcp_with_null = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_null.setObjectName("checkBox_allow_dhcp_with_null")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp_with_null, 12, 1, 1, 5)
        
        self.checkBox_allow_ipn_with_block = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp_with_block.setObjectName("checkBox_allow_ipn_with_block")
        self.gridLayout.addWidget(self.checkBox_allow_ipn_with_block, 18, 1, 1, 5)
        self.checkBox_allow_ipn_with_minus = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_ipn_with_minus.setObjectName("checkBox_allow_ipn_with_minus")
        self.gridLayout.addWidget(self.checkBox_allow_ipn_with_minus, 19, 1, 1, 5)
        self.checkBox_allow_ipn_with_null = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_ipn_with_null.setObjectName("checkBox_allow_ipn_with_null")
        self.gridLayout.addWidget(self.checkBox_allow_ipn_with_null, 20, 1, 1, 5)        
        
        self.groupBox = QtGui.QGroupBox(self.groupBox_link_parameters)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.toolButton_ipn_added = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_added.setCheckable(True)
        self.toolButton_ipn_added.setArrowType(QtCore.Qt.NoArrow)
        self.toolButton_ipn_added.setObjectName("toolButton_ipn_added")
        self.horizontalLayout.addWidget(self.toolButton_ipn_added)
        self.toolButton_ipn_enabled = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_enabled.setCheckable(True)
        self.toolButton_ipn_enabled.setObjectName("toolButton_ipn_enabled")
        self.horizontalLayout.addWidget(self.toolButton_ipn_enabled)
        self.toolButton_ipn_sleep = QtGui.QToolButton(self.groupBox)
        self.toolButton_ipn_sleep.setCheckable(True)
        self.toolButton_ipn_sleep.setObjectName("toolButton_ipn_sleep")
        self.horizontalLayout.addWidget(self.toolButton_ipn_sleep)
        self.gridLayout.addWidget(self.groupBox, 0, 3, 1, 3)
        self.toolButton_assign_ipn_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_ipn_from_pool.setObjectName("toolButton_assign_ipn_from_pool")
        self.gridLayout.addWidget(self.toolButton_assign_ipn_from_pool, 7, 5, 1, 1)
        self.toolButton_assign_vpn_from_pool = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_assign_vpn_from_pool.setObjectName("toolButton_assign_vpn_from_pool")
        self.gridLayout.addWidget(self.toolButton_assign_vpn_from_pool, 5, 5, 1, 1)
        self.toolButton_password = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_password.setObjectName("toolButton_password")
        self.gridLayout.addWidget(self.toolButton_password, 3, 5, 1, 1)
        self.toolButton_login = QtGui.QToolButton(self.groupBox_link_parameters)
        self.toolButton_login.setObjectName("toolButton_login")
        self.gridLayout.addWidget(self.toolButton_login, 1, 5, 1, 1)
        self.checkBox_allow_dhcp = QtGui.QCheckBox(self.groupBox_link_parameters)
        self.checkBox_allow_dhcp.setObjectName("checkBox_allow_dhcp")
        self.gridLayout.addWidget(self.checkBox_allow_dhcp, 11, 1, 1, 5)
        self.gridLayout_3.addWidget(self.groupBox_link_parameters, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.frame = QtGui.QFrame(self.tab_2)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_4 = QtGui.QGridLayout(self.frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.commandLinkButton = QtGui.QCommandLinkButton(self.frame)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.gridLayout_4.addWidget(self.commandLinkButton, 0, 0, 1, 1)
        self.gridLayout_5.addWidget(self.frame, 1, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.tab_2)
        self.tableWidget.setObjectName("tableWidget")
        self.gridLayout_5.addWidget(self.tableWidget, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.fixtures()
        self.accountAddonServiceRefresh()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)
        
        self.connect(self.toolButton_assign_ipn_from_pool,QtCore.SIGNAL("clicked()"),self.get_ipn_from_pool)
        self.connect(self.toolButton_assign_vpn_from_pool,QtCore.SIGNAL("clicked()"),self.get_vpn_from_pool)
        
        self.connect(self.toolButton_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_password,QtCore.SIGNAL("clicked()"),self.generate_password)

        self.connect(self.toolButton_ipn_added,QtCore.SIGNAL("clicked()"),self.subaccountAddDel)
        self.connect(self.toolButton_ipn_enabled,QtCore.SIGNAL("clicked()"),self.subaccountEnableDisable)
        
        self.connect(self.commandLinkButton, QtCore.SIGNAL("clicked()"), self.addAddonService)
        self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAddonService)
        
        self.connect(self.comboBox_vpn_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_vpn_pool_action)
        self.connect(self.comboBox_ipn_pool, QtCore.SIGNAL("currentIndexChanged(int)"), self.combobox_ipn_pool_action)



    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры субаккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_link_parameters.setTitle(QtGui.QApplication.translate("SubAccountDialog", "Параметры связки", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("SubAccountDialog", "NAS", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_login.setText(QtGui.QApplication.translate("SubAccountDialog", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_password.setText(QtGui.QApplication.translate("SubAccountDialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_vpn_ip_address.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_vpn.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_ipn_mac_address.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_switch.setText(QtGui.QApplication.translate("SubAccountDialog", "Коммутатор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_link_port.setText(QtGui.QApplication.translate("SubAccountDialog", "Порт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_vpn_speed.setText(QtGui.QApplication.translate("SubAccountDialog", "VPN скорость", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ipn_speed.setText(QtGui.QApplication.translate("SubAccountDialog", "IPN скорось", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_addonservice.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить активацию подключаемых услуг через веб-кабинет", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pppoe_ipn_mac.setText(QtGui.QApplication.translate("SubAccountDialog", "Привязать PPPOE авторизацию к IPN MAC", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_associate_pptp_ipn_ip.setText(QtGui.QApplication.translate("SubAccountDialog", "Привязать PPTP авторизацию к IPN IP", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG авторизацию при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG авторизацию при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_vpn_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить PPTP/L2TP/PPPOE/lISG авторизацию при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Выдавать IP адрес по DHCP при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))
        
        self.checkBox_allow_ipn_with_block.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить IPN доступ при наличии блокировок или неактивности", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_minus.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить IPN доступ при отрицательном балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_ipn_with_null.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить IPN доступ при нулевом балансе", None, QtGui.QApplication.UnicodeUTF8))


        self.groupBox.setTitle(QtGui.QApplication.translate("SubAccountDialog", "IPN статусы", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_added.setText(QtGui.QApplication.translate("SubAccountDialog", "Добавлен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_enabled.setText(QtGui.QApplication.translate("SubAccountDialog", "Активен", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_ipn_sleep.setText(QtGui.QApplication.translate("SubAccountDialog", "Не управлять", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_ipn_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_assign_vpn_from_pool.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_password.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_login.setText(QtGui.QApplication.translate("SubAccountDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_allow_dhcp.setText(QtGui.QApplication.translate("SubAccountDialog", "Разрешить выдачу адресов по DHCP", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("SubAccountDialog", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setText(QtGui.QApplication.translate("SubAccountDialog", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton.setDescription(QtGui.QApplication.translate("SubAccountDialog", "Добавить подключаемую услугу", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("SubAccountDialog", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_vpn_speed.setToolTip(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_vpn_speed.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_ipn_speed.setToolTip(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_ipn_speed.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Формат: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] \n"
        " Примеры: \n"
        " 128k  - rx-rate=128000, tx-rate=128000 (no bursts) \n"
        " 64k/128M - rx-rate=64000, tx-rate=128000000 \n"
        " 64k 256k - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=64000, rx/tx-burst-time=1s \n"
        "64k/64k 256k/256k 128k/128k 10/10 - rx/tx-rate=64000, rx/tx-burst-rate=256000, rx/tx-burst-threshold=128000, rx/tx-burst-time=10s \n"
        "", None, QtGui.QApplication.UnicodeUTF8))
        columns=[u'#', u'Название', u'Начата', u'Закрыта', u'Активирована на сервере доступа', u"Временная блокировка"]
        self.tableWidget = tableFormat(self.tableWidget)
        makeHeaders(columns, self.tableWidget)
        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        
        self.ipnRx = QtCore.QRegExp(r"\b(?:0\.0\.0\.0(/0)?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.0\.0\.0(?:/[1-8])?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){2}0\.0(?:/(?:9|1[0-6]))?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}0(?:/(?:1[7-9]|2[0-4]))?)|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:2[5-9]|3[0-2]))?)\b")
        self.ipnValidator = QtGui.QRegExpValidator(self.ipnRx, self)
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)  

    def addrow(self, widget, value, x, y, id=None, editable=False, widget_type = None):
        headerItem = QtGui.QTableWidgetItem()
        if widget_type == 'checkbox':
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        if value==None or value=="None":
            value=''
        if y==0:
            headerItem.id=value
        headerItem.setText(unicode(value))
        if id:
            headerItem.id=id
            
           
        widget.setItem(x,y,headerItem)
        
          
    def getSelectedId(self, table):
        try:
            return int(table.item(table.currentRow(), 0).text())
        except:
            return -1
              
    def subaccountEnableDisable(self):
        if not self.model: return
        state = True if self.toolButton_ipn_enabled.isChecked() else False
        if state:
            if not self.connection.accountActions(None, self.model.id, 'enable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        else:
             if not self.connection.accountActions(None, self.model.id, 'disable'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        #self.refresh()
        

    def subaccountAddDel(self):
        if not self.model: return
        state = True if self.toolButton_ipn_added.isChecked() else False
        if state==True:
            if not self.connection.accountActions(None, self.model.id,  'create'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))
        else:
            if not self.connection.accountActions(None, self.model.id,  'delete'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Сервер доступа настроен неправильно."))            


    def addAddonService(self):
        i=self.getSelectedId(self.tableWidget)
        child = AccountAddonServiceEdit(connection=self.connection, subaccount_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editAddonService(self):
        i=self.getSelectedId(self.tableWidget)
        try:
            model = self.connection.get_model(i, "billservice_accountaddonservice")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = AccountAddonServiceEdit(connection=self.connection, model=model, subaccount_model = self.model)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()


    def combobox_ipn_pool_action(self):
		#print self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
		if self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]:
			self.lineEdit_ipn_ip_address.setDisabled(True)
			self.lineEdit_ipn_ip_address.setText(u"0.0.0.0")
		else:
			self.lineEdit_ipn_ip_address.setDisabled(False)

    def combobox_vpn_pool_action(self):
		#print self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
		if self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]:
			self.lineEdit_vpn_ip_address.setDisabled(True)
			self.lineEdit_vpn_ip_address.setText(u"0.0.0.0")
		else:
			self.lineEdit_vpn_ip_address.setDisabled(False)

    def accountAddonServiceRefresh(self):
        if self.model:
            sp = self.connection.sql("""
            SELECT accadd.*, adds.name as addonservice_name, adds.id as addonservice_id FROM billservice_accountaddonservice as accadd
            JOIN billservice_addonservice as adds ON adds.id=accadd.service_id
            WHERE subaccount_id=%s ORDER BY id DESC
            """ % self.model.id)
            self.connection.commit()
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget, a.id, i, 0)
                self.addrow(self.tableWidget, a.addonservice_name, i, 1)
                self.addrow(self.tableWidget, a.activated.strftime(strftimeFormat), i, 2)
                try:
                    self.addrow(self.tableWidget, a.deactivated.strftime(strftimeFormat), i, 3)
                except:
                    self.addrow(self.tableWidget, u"Не закончен", i, 3)
                self.addrow(self.tableWidget, a.action_status, i, 4)
                try:
                    self.addrow(self.tableWidget, a.temporary_blocked.strftime(strftimeFormat), i, 5)
                except:
                    self.addrow(self.tableWidget, u"Нет", i, 5)
                i+=1
            self.tableWidget.setColumnHidden(0, True)
            self.tableWidget.resizeColumnsToContents()
                    
    def fixtures(self):
        nasses=self.connection.sql("SELECT id, name FROM nas_nas ORDER BY name;")
        self.connection.commit()
        self.comboBox_nas.addItem(u"---Любой---", QtCore.QVariant(0))
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name, QtCore.QVariant(nas.id))

        self.comboBox_link_switch_id.addItem(u"---Не указан---", QtCore.QVariant(0))
        for nas in nasses:
            self.comboBox_link_switch_id.addItem(nas.name, QtCore.QVariant(nas.id))
            
        #print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            if self.model.isnull('vpn_ipinuse_id')==False:
                pool_id = self.connection.sql("SELECT pool_id FROM billservice_ipinuse WHERE id=%s" % self.model.vpn_ipinuse_id, return_response=True)[0]
                #print "vpnipinuse pool_id", pool_id
            
        pools = self.connection.get_models("billservice_ippool", where={'type':'0',})
        
        self.connection.commit()
        i=1
        self.comboBox_vpn_pool.clear()
        self.comboBox_vpn_pool.addItem('---')
        self.comboBox_vpn_pool.setItemData(0, QtCore.QVariant(0))
        for pool in pools:
            self.comboBox_vpn_pool.addItem(pool.name)
            self.comboBox_vpn_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.isnull('vpn_ipinuse_id')==False:
                    if pool.id==pool_id.pool_id:
                        self.comboBox_vpn_pool.setCurrentIndex(i)
                        self.lineEdit_vpn_ip_address.setDisabled(True)
            
            i+=1

        if not self.model: self.groupBox.setDisabled(True)
        if self.model:
            if self.model.isnull('ipn_ipinuse_id')==False:
                pool_id = self.connection.sql("SELECT pool_id FROM billservice_ipinuse WHERE id=%s" % self.model.ipn_ipinuse_id, return_response=True)[0]
            
        pools = self.connection.get_models("billservice_ippool", where={'type':'1',})
        self.connection.commit()
        i=1
        self.comboBox_ipn_pool.clear()
        self.comboBox_ipn_pool.addItem('---')
        self.comboBox_ipn_pool.setItemData(i, QtCore.QVariant(0))
        for pool in pools:
            self.comboBox_ipn_pool.addItem(pool.name)
            self.comboBox_ipn_pool.setItemData(i, QtCore.QVariant(pool.id))
            if self.model:
                if self.model.isnull('ipn_ipinuse_id')==False:
                    if pool.id==pool_id.pool_id:
                        self.comboBox_ipn_pool.setCurrentIndex(i)
                        self.lineEdit_ipn_ip_address.setDisabled(True)
            i+=1

            
        if self.model:
            #print "NAS_ID", self.model.nas_id
            if self.model.nas_id:
                self.comboBox_nas.setCurrentIndex(self.comboBox_nas.findData(self.model.nas_id))
            if self.model.switch_id:
                self.comboBox_link_switch_id.setCurrentIndex(self.comboBox_link_switch_id.findData(self.model.switch_id))                
            self.lineEdit_link_login.setText(unicode(self.model.username))
            self.lineEdit_link_password.setText(unicode(self.model.password))
            self.lineEdit_vpn_ip_address.setText(unicode(self.model.vpn_ip_address))
            self.lineEdit_ipn_ip_address.setText(unicode(self.model.ipn_ip_address))
            self.lineEdit_link_ipn_mac_address.setText(unicode(self.model.ipn_mac_address))
            self.spinBox_link_port.setValue(self.model.switch_port if self.model.switch_port else 0)
            self.checkBox_allow_dhcp.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_dhcp_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_dhcp_with_block==True else QtCore.Qt.Unchecked )
            
            self.checkBox_allow_vpn_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_vpn_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_vpn_with_block==True else QtCore.Qt.Unchecked )

            self.checkBox_allow_ipn_with_null.setCheckState(QtCore.Qt.Checked if self.model.allow_ipn_with_null==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_ipn_with_minus.setCheckState(QtCore.Qt.Checked if self.model.allow_ipn_with_minus==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_ipn_with_block.setCheckState(QtCore.Qt.Checked if self.model.allow_ipn_with_block==True else QtCore.Qt.Unchecked )
            
            self.checkBox_associate_pppoe_ipn_mac.setCheckState(QtCore.Qt.Checked if self.model.associate_pppoe_ipn_mac==True else QtCore.Qt.Unchecked )
            self.checkBox_associate_pptp_ipn_ip.setCheckState(QtCore.Qt.Checked if self.model.associate_pptp_ipn_ip==True else QtCore.Qt.Unchecked )
            self.checkBox_allow_addonservice.setCheckState(QtCore.Qt.Checked if self.model.allow_addonservice==True else QtCore.Qt.Unchecked )
            self.lineEdit_vpn_speed.setText(unicode(self.model.vpn_speed))
            self.lineEdit_ipn_speed.setText(unicode(self.model.ipn_speed))
            self.toolButton_ipn_sleep.setChecked(self.model.ipn_sleep)
            self.toolButton_ipn_added.setChecked(self.model.ipn_added)
            self.toolButton_ipn_enabled.setChecked(self.model.ipn_enabled)
            
            
            #self.combobox_vpn_pool_action()
            #self.combobox_ipn_pool_action()
                        
    def accept(self):
        if self.model:
            model=self.model
        else:
            model = Object()
            model.account_id = self.account.id
        if self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]!=0:
            model.nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
        else:
            model.nas_id = None
        
        if self.comboBox_link_switch_id.itemData(self.comboBox_link_switch_id.currentIndex()).toInt()[0]!=0:
            model.switch_id = self.comboBox_link_switch_id.itemData(self.comboBox_link_switch_id.currentIndex()).toInt()[0]
        else:
            model.switch_id = None
        
        model.switch_port = int(self.spinBox_link_port.value() or 0)
        model.username = unicode(self.lineEdit_link_login.text()) or ""
        model.password = unicode(self.lineEdit_link_password.text()) or ""
        #model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text()) or "0.0.0.0"
        #model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text()) or "0.0.0.0"
        #------------------
        if self.lineEdit_ipn_ip_address.text():
			if self.ipnValidator.validate(self.lineEdit_ipn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания IPN IP адреса."))
				self.connection.rollback()
				return
			try:
				ipn_address_account_id = self.connection.get("SELECT id FROM billservice_subaccount WHERE ipn_ip_address='%s'" % unicode(self.lineEdit_ipn_ip_address.text())).id
				if ipn_address_account_id!=model.id and unicode(self.lineEdit_ipn_ip_address.text())!='0.0.0.0':
					QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе уже существует такой IPN IP адрес."))
					#self.connection.rollback()
					#return  			  
			except Exception, ex:
				pass
        model.ipn_ip_address = unicode(self.lineEdit_ipn_ip_address.text()) or "0.0.0.0"
		
				
        if self.lineEdit_vpn_ip_address.text():
			if self.ipValidator.validate(self.lineEdit_vpn_ip_address.text(), 0)[0]  != QtGui.QValidator.Acceptable:
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте правильность написания VPN IP адреса."))
				self.connection.rollback()
				return
			try:
				vpn_address_account_id = self.connection.get("SELECT id FROM billservice_subaccount WHERE vpn_ip_address='%s'" % unicode(self.lineEdit_vpn_ip_address.text())).id
				#print "vpn_address_account_id", vpn_address_account_id
				if vpn_address_account_id!=model.id and unicode(self.lineEdit_vpn_ip_address.text())!='0.0.0.0':
					QtGui.QMessageBox.information(self, u"Внимание!", unicode(u"В системе уже существует такой VPN IP адрес."))	  
			except Exception, ex:
				pass
			
        model.vpn_ip_address = unicode(self.lineEdit_vpn_ip_address.text()) or "0.0.0.0"

        #---------------
        if self.lineEdit_link_ipn_mac_address.text().isEmpty()==False:
			if self.macValidator.validate(self.lineEdit_link_ipn_mac_address.text(), 0)[0]  == QtGui.QValidator.Acceptable:
				try:
					id = self.connection.get("SELECT id FROM billservice_account WHERE ipn_mac_address='%s'" % unicode(self.lineEdit_ipn_mac_address.text()).upper()).id
					if id!=model.id :
						QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"В системе уже есть такой MAC."))
						#self.connection.rollback()
						return
				except:
					pass
				model.ipn_mac_address = unicode(self.lineEdit_link_ipn_mac_address.text()).upper()
			else:
				QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Указан некорректный MAC адрес."))
				self.connection.rollback()
				return
        else:
			model.ipn_mac_address=u""
                
        #model.ipn_mac_address = unicode(self.lineEdit_link_ipn_mac_address.text()) or ""
            
        model.allow_dhcp = self.checkBox_allow_dhcp.checkState()==QtCore.Qt.Checked
        model.allow_dhcp_with_null = self.checkBox_allow_dhcp_with_null.checkState()==QtCore.Qt.Checked
        model.allow_dhcp_with_minus = self.checkBox_allow_dhcp_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_dhcp_with_block = self.checkBox_allow_dhcp_with_block.checkState()==QtCore.Qt.Checked
        model.allow_vpn_with_null = self.checkBox_allow_vpn_with_null.checkState()==QtCore.Qt.Checked
        model.allow_vpn_with_minus = self.checkBox_allow_vpn_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_vpn_with_block = self.checkBox_allow_vpn_with_block.checkState()==QtCore.Qt.Checked
        
        model.allow_ipn_with_null = self.checkBox_allow_ipn_with_null.checkState()==QtCore.Qt.Checked
        model.allow_ipn_with_minus = self.checkBox_allow_ipn_with_minus.checkState()==QtCore.Qt.Checked
        model.allow_ipn_with_block = self.checkBox_allow_ipn_with_block.checkState()==QtCore.Qt.Checked


        model.associate_pppoe_ipn_mac = self.checkBox_associate_pppoe_ipn_mac.checkState()==QtCore.Qt.Checked
        model.associate_pptp_ipn_ip = self.checkBox_associate_pptp_ipn_ip.checkState()==QtCore.Qt.Checked
        model.allow_addonservice = self.checkBox_allow_addonservice.checkState()==QtCore.Qt.Checked
        model.vpn_speed=unicode(self.lineEdit_vpn_speed.text()) or ""
        model.ipn_speed=unicode(self.lineEdit_ipn_speed.text()) or ""
        model.ipn_sleep = self.toolButton_ipn_sleep.isChecked()
        model.ipn_added = self.toolButton_ipn_added.isChecked()
        model.ipn_enabled = self.toolButton_ipn_enabled.isChecked()
        
        if self.model:
            if model.ipn_ip_address!=self.model.ipn_ip_address:
    			"""
    			Если изменили IPN IP адрес-значит нужно добавить новый адрес в лист доступа
    			"""
    			model.ipn_added=False        
    			model.ipn_enabled=False        
        model.speed=''
		 #Операции с пулом    
        try:
			pool_id = self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
			if pool_id!=0 and model.ipn_ip_address==u'0.0.0.0':
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Вы указали IPN пул, но не назначили ip адрес."))
				self.connection.rollback()
				return 
			if  model.__dict__.get('ipn_ipinuse_id'):
				ipninuse_model = self.connection.get_model(model.ipn_ipinuse_id, "billservice_ipinuse")
				
				if ipninuse_model.id!=pool_id or ipninuse_model.ip!=model.ipn_ip_address:
					self.connection.iddelete(ipninuse_model.id, "billservice_ipinuse")
					model.ipn_ipinuse_id=None
					
			
			if pool_id!=0:
				ipninuse_model= Object()
				ipninuse_model.pool_id=pool_id
				ipninuse_model.ip=model.ipn_ip_address
				ipninuse_model.datetime='now()'
				ipninuse_model.id = self.connection.save(ipninuse_model, "billservice_ipinuse")
				model.ipn_ipinuse_id=ipninuse_model.id
				#self.connection.save(model, "billservice_account")
        except Exception, e:
			print e
			QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте настройки IPN IP адресов. Возможно выбранный IP адрес не принадлежит пулу."))
			self.connection.rollback()
			return 

		 #Операции с пулом    
        try:
			pool_id = self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
			if pool_id!=0 and model.vpn_ip_address==u'0.0.0.0':
				QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Вы указали VPN пул, но не назначили ip адрес."))
				self.connection.rollback()
				return 			
			if  model.__dict__.get('vpn_ipinuse_id'):
				ipninuse_model = self.connection.get_model(model.vpn_ipinuse_id, "billservice_ipinuse")
				
				if ipninuse_model.id!=pool_id or ipninuse_model.ip!=model.vpn_ip_address:
					self.connection.iddelete(ipninuse_model.id, "billservice_ipinuse")
					model.vpn_ipinuse_id=None
					
			
			if pool_id!=0:
				ipninuse_model= Object()
				ipninuse_model.pool_id=pool_id
				ipninuse_model.ip=model.vpn_ip_address
				ipninuse_model.datetime='now()'
				ipninuse_model.id = self.connection.save(ipninuse_model, "billservice_ipinuse")
				model.vpn_ipinuse_id=ipninuse_model.id
				#self.connection.save(model, "billservice_account")
        except Exception, e:
			print e
			QtGui.QMessageBox.critical(self, u"Ошибка", unicode(u"Проверьте настройки VPN IP адресов. Возможно выбранный IP адрес не принадлежит пулу."))
			self.connection.rollback()
			return 
                
                
            
        try:
            self.connection.save(model,"billservice_subaccount")
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
        QtGui.QDialog.accept(self)

    def generate_login(self):
        self.lineEdit_link_login.setText(nameGen())

    def generate_password(self):
        self.lineEdit_link_password.setText(GenPasswd2())
        
    def get_ipn_from_pool(self):
        pool_id = self.comboBox_ipn_pool.itemData(self.comboBox_ipn_pool.currentIndex()).toInt()[0]
        if pool_id!=0:
            child = IPAddressSelectForm(self.connection, pool_id)
            if child.exec_()==1:
                self.lineEdit_ipn_ip_address.setText(child.selected_ip)

                
    def get_vpn_from_pool(self):
        pool_id = self.comboBox_vpn_pool.itemData(self.comboBox_vpn_pool.currentIndex()).toInt()[0]
        if pool_id!=0:
            child = IPAddressSelectForm(self.connection, pool_id)
            if child.exec_()==1:
                self.lineEdit_vpn_ip_address.setText(child.selected_ip)


class AddAccountTarif(QtGui.QDialog):
    def __init__(self, connection, account=None, get_info=False, model=None):
        super(AddAccountTarif, self).__init__()
        self.model=model
        self.get_info = get_info
        self.account=account
        self.connection = connection
        self.connection.commit()

        self.setObjectName("Dialog")
        self.resize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()).expandedTo(self.minimumSizeHint()))
        self.setMinimumSize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()))
        self.setMaximumSize(QtCore.QSize(QtCore.QRect(0,0,299,182).size()))
                            
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(130,140,161,32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.hint_label = QtGui.QLabel(self)
        self.hint_label.setGeometry(QtCore.QRect(10,10,371,31))
        self.hint_label.setObjectName("hint_label")

        self.widget = QtGui.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(10,40,281,101))
        self.widget.setObjectName("widget")

        self.gridlayout = QtGui.QGridLayout(self.widget)
        self.gridlayout.setObjectName("gridlayout")

        self.tarif_label = QtGui.QLabel(self.widget)
        self.tarif_label.setObjectName("tarif_label")
        self.gridlayout.addWidget(self.tarif_label,0,0,1,1)

        self.tarif_edit = QtGui.QComboBox(self.widget)
        self.tarif_edit.setMaxVisibleItems(10)
        self.tarif_edit.setObjectName("tarif_edit")
        self.gridlayout.addWidget(self.tarif_edit,0,1,1,1)

        self.date_label = QtGui.QLabel(self.widget)
        self.date_label.setObjectName("date_label")
        self.gridlayout.addWidget(self.date_label,1,0,1,1)

        self.date_edit = QtGui.QDateTimeEdit(self.widget)
        self.date_edit.setFrame(True)
        self.date_edit.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_edit.setMinimumDate(QtCore.QDate(2008,1,1))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setObjectName("date_edit")
        self.date_edit.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.gridlayout.addWidget(self.date_edit,1,1,1,1)


        self.retranslateUi()
        self.fixtures()
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.reject)

    def accept(self):
        if self.get_info==False:
            date=self.date_edit.dateTime().toPyDateTime()
            #print repr(date)
            #print str(self.date_edit.dateTime().toString())
            date = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second)
            if self.model:
                model=self.model
                model.datetime = date
            else:
                model = Object()
                model.account_id = self.account.id
                model.tarif_id =self.tarif_edit.itemData(self.tarif_edit.currentIndex()).toInt()[0]
                model.datetime = date
                
                #AccountTarif.objects.create(account=self.account, tarif=tarif, datetime=date)
            try:
                self.connection.save(model,"billservice_accounttarif")
                self.connection.commit()
            except Exception, e:
                #print e
                self.conection.rollback()
        QtGui.QDialog.accept(self)


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Редактирование плана", None, QtGui.QApplication.UnicodeUTF8))
        self.hint_label.setText(QtGui.QApplication.translate("Dialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Выберите тарифный план и время, </span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\">когда должен быть осуществлён переход</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tarif_label.setText(QtGui.QApplication.translate("Dialog", "Тарифный план", None, QtGui.QApplication.UnicodeUTF8))
        self.date_label.setText(QtGui.QApplication.translate("Dialog", "Дата и время", None, QtGui.QApplication.UnicodeUTF8))

    def fixtures(self):
        tarifs=self.connection.sql("SELECT id, name FROM billservice_tariff WHERE deleted IS NOT TRUE ORDER BY name;")
        self.connection.commit()
        for tarif in tarifs:
            self.tarif_edit.addItem(tarif.name, QtCore.QVariant(tarif.id))
        now=datetime.datetime.now()
        #print self.tarif_edit.itemText(self.tarif_edit.findData(QtCore.QVariant(1)))
        if self.model:
            self.tarif_edit.setCurrentIndex(self.tarif_edit.findData(self.model.tarif_id))

            now = QtCore.QDateTime()

            now.setTime_t((mktime(self.model.datetime.timetuple())))
        self.date_edit.setDateTime(now)

    def reject(self):
        self.connection.rollback()
        QtGui.QDialog.reject(self)
        

            
            
class AccountWindow(QtGui.QMainWindow):
    def __init__(self, connection, tarif_id, ttype, model=None, ipn_for_vpn=False):
        super(AccountWindow, self).__init__()
        self.model=model
        self.ttype = ttype
        self.connection = connection
        self.ipn_for_vpn = ipn_for_vpn
        self.tarif_id = tarif_id
        self.organization = None
        self.bank = None
        
        self.setObjectName("AccountWindow")
        bhdr = HeaderUtil.getBinaryHeader('AccountWindow-account_info')
        self.resize(851, 680)
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_general = QtGui.QWidget()
        self.tab_general.setObjectName("tab_general")
        self.gridLayout_8 = QtGui.QGridLayout(self.tab_general)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.groupBox_account_data = QtGui.QGroupBox(self.tab_general)
        #self.groupBox_account_data.setMinimumSize(QtCore.QSize(381, 82))
        #self.groupBox_account_data.setMaximumSize(QtCore.QSize(381, 86))
        self.groupBox_account_data.setObjectName("groupBox_account_data")
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_account_data)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_username = QtGui.QLabel(self.groupBox_account_data)
        self.label_username.setMinimumSize(QtCore.QSize(70, 0))
        self.label_username.setObjectName("label_username")
        self.gridLayout_3.addWidget(self.label_username, 0, 0, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.groupBox_account_data)
        self.lineEdit_username.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.gridLayout_3.addWidget(self.lineEdit_username, 0, 1, 1, 1)
        self.toolButton_generate_login = QtGui.QToolButton(self.groupBox_account_data)
        self.toolButton_generate_login.setEnabled(True)
        self.toolButton_generate_login.setObjectName("toolButton_generate_login")
        self.gridLayout_3.addWidget(self.toolButton_generate_login, 0, 2, 1, 1)
        self.label_password = QtGui.QLabel(self.groupBox_account_data)
        self.label_password.setObjectName("label_password")
        self.gridLayout_3.addWidget(self.label_password, 1, 0, 1, 1)
        self.lineEdit_password = QtGui.QLineEdit(self.groupBox_account_data)
        self.lineEdit_password.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.gridLayout_3.addWidget(self.lineEdit_password, 1, 1, 1, 1)
        self.toolButton_generate_password = QtGui.QToolButton(self.groupBox_account_data)
        self.toolButton_generate_password.setObjectName("toolButton_generate_password")
        self.gridLayout_3.addWidget(self.toolButton_generate_password, 1, 2, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_account_data, 0, 0, 1, 1)
        self.groupBox_agreement = QtGui.QGroupBox(self.tab_general)
        self.groupBox_agreement.setMinimumSize(QtCore.QSize(391, 86))
        self.groupBox_agreement.setMaximumSize(QtCore.QSize(3910, 84))
        self.groupBox_agreement.setObjectName("groupBox_agreement")
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_agreement)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_agreement_date = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_date.setObjectName("label_agreement_date")
        self.gridLayout_4.addWidget(self.label_agreement_date, 0, 0, 1, 1)
        self.label_agreement_num = QtGui.QLabel(self.groupBox_agreement)
        self.label_agreement_num.setObjectName("label_agreement_num")
        self.gridLayout_4.addWidget(self.label_agreement_num, 1, 0, 1, 1)
        self.lineEdit_agreement_num = QtGui.QLineEdit(self.groupBox_agreement)
        self.lineEdit_agreement_num.setEnabled(True)
        self.lineEdit_agreement_num.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_agreement_num.setObjectName("lineEdit_agreement_num")
        self.gridLayout_4.addWidget(self.lineEdit_agreement_num, 1, 2, 1, 1)
        self.toolButton_agreement_print = QtGui.QToolButton(self.groupBox_agreement)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_agreement_print.setIcon(icon)
        self.toolButton_agreement_print.setObjectName("toolButton_agreement_print")
        self.gridLayout_4.addWidget(self.toolButton_agreement_print, 1, 3, 1, 1)
        self.dateTimeEdit_agreement_date = QtGui.QDateTimeEdit(self.groupBox_agreement)
        self.dateTimeEdit_agreement_date.setCalendarPopup(True)
        self.dateTimeEdit_agreement_date.setObjectName("dateTimeEdit_agreement_date")
        self.gridLayout_4.addWidget(self.dateTimeEdit_agreement_date, 0, 2, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_agreement, 0, 1, 1, 1)
        self.groupBox_account_info = QtGui.QGroupBox(self.tab_general)
        #self.groupBox_account_info.setMinimumSize(QtCore.QSize(381, 211))
        #self.groupBox_account_info.setMaximumSize(QtCore.QSize(381, 16381))
        self.groupBox_account_info.setObjectName("groupBox_account_info")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_account_info)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidget = QtGui.QTableWidget(self.groupBox_account_info)
        #self.tableWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setObjectName("AccountWindow-account_info")
        self.gridLayout_2.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_account_info, 1, 0, 4, 1)

        self.groupBox_urdata = QtGui.QGroupBox(self.tab_general)
        self.groupBox_urdata.setMinimumSize(QtCore.QSize(391, 0))
        self.groupBox_urdata.setMaximumSize(QtCore.QSize(16381, 16381))
        self.groupBox_urdata.setCheckable(True)
        self.groupBox_urdata.setChecked(False)
        self.groupBox_urdata.setObjectName("groupBox_urdata")
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_urdata)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_organization = QtGui.QLabel(self.groupBox_urdata)
        self.label_organization.setObjectName("label_organization")
        self.gridLayout_7.addWidget(self.label_organization, 0, 0, 1, 1)
        self.lineEdit_organization = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_organization.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_organization.setObjectName("lineEdit_organization")
        self.gridLayout_7.addWidget(self.lineEdit_organization, 0, 1, 1, 4)
        self.label_bank = QtGui.QLabel(self.groupBox_urdata)
        self.label_bank.setObjectName("label_bank")
        self.gridLayout_7.addWidget(self.label_bank, 13, 0, 1, 1)
        self.lineEdit_bank = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_bank.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_bank.setObjectName("lineEdit_bank")
        self.gridLayout_7.addWidget(self.lineEdit_bank, 13, 1, 1, 1)
        self.lineEdit_uraddress = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_uraddress.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_uraddress.setObjectName("lineEdit_uraddress")
        self.gridLayout_7.addWidget(self.lineEdit_uraddress, 6, 1, 1, 4)
        self.label_uraddress = QtGui.QLabel(self.groupBox_urdata)
        self.label_uraddress.setObjectName("label_uraddress")
        self.gridLayout_7.addWidget(self.label_uraddress, 6, 0, 1, 1)
        self.lineEdit_urphone = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_urphone.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_urphone.setObjectName("lineEdit_urphone")
        self.gridLayout_7.addWidget(self.lineEdit_urphone, 7, 1, 1, 4)
        self.label_urphone = QtGui.QLabel(self.groupBox_urdata)
        self.label_urphone.setObjectName("label_urphone")
        self.gridLayout_7.addWidget(self.label_urphone, 7, 0, 1, 1)
        self.lineEdit_fax = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_fax.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_fax.setObjectName("lineEdit_fax")
        self.gridLayout_7.addWidget(self.lineEdit_fax, 8, 1, 1, 4)
        self.label_fax = QtGui.QLabel(self.groupBox_urdata)
        self.label_fax.setObjectName("label_fax")
        self.gridLayout_7.addWidget(self.label_fax, 8, 0, 1, 1)
        self.label_bank_code = QtGui.QLabel(self.groupBox_urdata)
        self.label_bank_code.setObjectName("label_bank_code")
        self.gridLayout_7.addWidget(self.label_bank_code, 13, 3, 1, 1)
        self.lineEdit_bank_code = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_bank_code.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_bank_code.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEdit_bank_code.setObjectName("lineEdit_bank_code")
        self.gridLayout_7.addWidget(self.lineEdit_bank_code, 13, 4, 1, 1)
        self.lineEdit_unp = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_unp.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_unp.setObjectName("lineEdit_unp")
        self.gridLayout_7.addWidget(self.lineEdit_unp, 1, 1, 1, 4)
        self.label_unp = QtGui.QLabel(self.groupBox_urdata)
        self.label_unp.setObjectName("label_unp")
        self.gridLayout_7.addWidget(self.label_unp, 1, 0, 1, 1)
        self.lineEdit_okpo = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_okpo.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_okpo.setObjectName("lineEdit_okpo")
        self.gridLayout_7.addWidget(self.lineEdit_okpo, 3, 1, 1, 4)
        self.label_okpo = QtGui.QLabel(self.groupBox_urdata)
        self.label_okpo.setObjectName("label_okpo")
        self.gridLayout_7.addWidget(self.label_okpo, 3, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_urdata)
        self.label.setObjectName("label")
        self.gridLayout_7.addWidget(self.label, 2, 0, 1, 1)
        self.lineEdit_kpp = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_kpp.setObjectName("lineEdit_kpp")
        self.gridLayout_7.addWidget(self.lineEdit_kpp, 2, 1, 1, 4)
        self.lineEdit_rs = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_rs.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_rs.setObjectName("lineEdit_rs")
        self.gridLayout_7.addWidget(self.lineEdit_rs, 4, 1, 1, 4)
        self.label_rs = QtGui.QLabel(self.groupBox_urdata)
        self.label_rs.setObjectName("label_rs")
        self.gridLayout_7.addWidget(self.label_rs, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_urdata)
        self.label_2.setObjectName("label_2")
        self.gridLayout_7.addWidget(self.label_2, 5, 0, 1, 1)
        self.lineEdit_kor_s = QtGui.QLineEdit(self.groupBox_urdata)
        self.lineEdit_kor_s.setObjectName("lineEdit_kor_s")
        self.gridLayout_7.addWidget(self.lineEdit_kor_s, 5, 1, 1, 4)
        self.gridLayout_8.addWidget(self.groupBox_urdata, 1, 1, 1, 1)
        self.groupBox_balance_info = QtGui.QGroupBox(self.tab_general)
        self.groupBox_balance_info.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_balance_info.setMaximumSize(QtCore.QSize(3910, 1656465))
        self.groupBox_balance_info.setObjectName("groupBox_balance_info")
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_balance_info)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_balance = QtGui.QLabel(self.groupBox_balance_info)
        self.label_balance.setObjectName("label_balance")
        self.gridLayout_9.addWidget(self.label_balance, 0, 0, 1, 1)
        self.lineEdit_balance = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_balance.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_balance.setDisabled(True)
        self.lineEdit_balance.setObjectName("lineEdit_balance")
        self.gridLayout_9.addWidget(self.lineEdit_balance, 0, 1, 1, 1)
        self.label_credit = QtGui.QLabel(self.groupBox_balance_info)
        self.label_credit.setObjectName("label_credit")
        self.gridLayout_9.addWidget(self.label_credit, 1, 0, 1, 1)
        self.lineEdit_credit = QtGui.QLineEdit(self.groupBox_balance_info)
        self.lineEdit_credit.setMinimumSize(QtCore.QSize(0, 20))
        self.lineEdit_credit.setObjectName("lineEdit_credit")
        self.gridLayout_9.addWidget(self.lineEdit_credit, 1, 1, 1, 1)
        self.checkBox_credit = QtGui.QCheckBox(self.groupBox_balance_info)
        self.checkBox_credit.setEnabled(False)
        self.checkBox_credit.setChecked(True)
        self.checkBox_credit.setObjectName("checkBox_credit")
        self.gridLayout_9.addWidget(self.checkBox_credit, 2, 0, 1, 2)
        self.gridLayout_8.addWidget(self.groupBox_balance_info, 2, 1, 2, 1)
        self.groupBox_status = QtGui.QGroupBox(self.tab_general)
        self.groupBox_status.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_status.setObjectName("groupBox_status")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_status)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox_status = QtGui.QComboBox(self.groupBox_status)
        self.comboBox_status.setObjectName("comboBox_status")
        self.horizontalLayout.addWidget(self.comboBox_status)
        
        self.groupBox_management_info = QtGui.QGroupBox(self.tab_general)
        self.gridLayout_management = QtGui.QGridLayout(self.groupBox_management_info)
        self.label_manager = QtGui.QLabel(self.groupBox_management_info)
        self.gridLayout_management.addWidget(self.label_manager,0,0,1,1)
        self.comboBox_manager = QtGui.QComboBox(self.groupBox_management_info)
        self.gridLayout_management.addWidget(self.comboBox_manager,0,1,1,1)
        self.gridLayout_8.addWidget(self.groupBox_management_info, 5, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox_status, 6, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.tab_general)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_19 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_19.setObjectName("gridLayout_19")
        self.plainTextEdit_comment = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit_comment.setObjectName("plainTextEdit_comment")
        self.gridLayout_19.addWidget(self.plainTextEdit_comment, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.groupBox, 5, 1, 2, 1)
        self.tabWidget.addTab(self.tab_general, "")
        
        #-----
        self.tab_network_settings = QtGui.QWidget()
        self.tab_network_settings.setObjectName("tab_network_settings")
        self.gridLayout_17 = QtGui.QGridLayout(self.tab_network_settings)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.groupBox_nas = QtGui.QGroupBox(self.tab_network_settings)
        self.groupBox_nas.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_nas.setMaximumSize(QtCore.QSize(11791, 11791))
        self.groupBox_nas.setObjectName("groupBox_nas")
        self.gridLayout_14 = QtGui.QGridLayout(self.groupBox_nas)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.label_nas = QtGui.QLabel(self.groupBox_nas)
        self.label_nas.setObjectName("label_nas")
        self.gridLayout_14.addWidget(self.label_nas, 0, 0, 1, 1)
        self.comboBox_nas = QtGui.QComboBox(self.groupBox_nas)
        self.comboBox_nas.setMinimumSize(QtCore.QSize(350, 20))
        self.comboBox_nas.setMaximumSize(QtCore.QSize(16777215, 20))
        self.comboBox_nas.setObjectName("comboBox_nas")
        self.gridLayout_14.addWidget(self.comboBox_nas, 0, 1, 1, 1)
        self.gridLayout_17.addWidget(self.groupBox_nas, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_network_settings, "")
        self.tab_suspended = QtGui.QWidget()
        self.tab_suspended.setObjectName("tab_suspended")
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_suspended)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.tableWidget_suspended = QtGui.QTableWidget(self.tab_suspended)
        self.tableWidget_suspended.setObjectName("tableWidget_suspended")
        self.gridLayout_5.addWidget(self.tableWidget_suspended, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_suspended, "")
#        
        self.tab_subaccounts = QtGui.QWidget()
        self.tab_subaccounts.setObjectName("tab_subaccounts")
        self.gridLayout_51 = QtGui.QGridLayout(self.tab_subaccounts)
        self.gridLayout_51.setObjectName("gridLayout_51")
        self.tableWidget_subaccounts = QtGui.QTableWidget(self.tab_subaccounts)
        self.tableWidget_subaccounts.setObjectName("tableWidget_subaccounts")
        self.tableWidget_subaccounts = tableFormat(self.tableWidget_subaccounts)
        self.gridLayout_51.addWidget(self.tableWidget_subaccounts, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_subaccounts, "")        
        
#        
        self.tab_tarifs = QtGui.QWidget()
        self.tab_tarifs.setObjectName("tab_tarifs")
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_tarifs)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.tableWidget_accounttarif = QtGui.QTableWidget(self.tab_tarifs)
        self.tableWidget_accounttarif.setObjectName("tableWidget_accounttarif")
        self.gridLayout_6.addWidget(self.tableWidget_accounttarif, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_tarifs, "")
        self.tab_addonservice = QtGui.QWidget()
        self.tab_addonservice.setObjectName("tab_addonservice")
        self.gridLayout_7 = QtGui.QGridLayout(self.tab_addonservice)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.tableWidget_addonservice = QtGui.QTableWidget(self.tab_addonservice)
        self.tableWidget_addonservice.setObjectName("tableWidget_addonservice")
        self.gridLayout_7.addWidget(self.tableWidget_addonservice, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_addonservice, "")
        
        
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSave = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon1)
        self.actionSave.setObjectName("actionSave")
        self.actionAdd = QtGui.QAction(self)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd.setIcon(icon2)
        self.actionAdd.setObjectName("actionAdd")
        self.actionDel = QtGui.QAction(self)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDel.setIcon(icon3)
        self.actionDel.setObjectName("actionDel")
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionAdd)
        self.toolBar.addAction(self.actionDel)

        self.comboBox_city = QtGui.QComboBox(self.tableWidget)
        self.comboBox_street = QtGui.QComboBox(self.tableWidget)
        self.comboBox_house = QtGui.QComboBox(self.tableWidget)
        
        self.comboBox_city.setEditable(True)
        self.comboBox_street.setEditable(True)
        self.comboBox_house.setEditable(True)
        
        self.retranslateUi()
        HeaderUtil.nullifySaved(self.tableWidget.objectName())
        self.firsttime = True
        
        self.tabWidget.setCurrentIndex(0)
        
        QtCore.QMetaObject.connectSlotsByName(self)

        
        self.connect(self.toolButton_generate_login,QtCore.SIGNAL("clicked()"),self.generate_login)
        self.connect(self.toolButton_generate_password,QtCore.SIGNAL("clicked()"),self.generate_password)
        self.connect(self.actionSave, QtCore.SIGNAL("triggered()"),  self.accept)
        #self.connect(self.checkBox_assign_ipn_ip_from_dhcp, QtCore.SIGNAL("stateChanged(int)"), self.dhcpActions)
        self.connect(self.tableWidget_accounttarif, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_accounttarif)
        self.connect(self.tableWidget_addonservice, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editAddonService)
        self.connect(self.tableWidget_suspended, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.edit_suspendedperiod)
        self.connect(self.tableWidget_subaccounts, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.editSubAccount)
        
        self.connect(self.comboBox_city, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_street)
        self.connect(self.comboBox_street, QtCore.SIGNAL("currentIndexChanged(int)"), self.refresh_combo_house)
        
        
        self.connect(self.tableWidget, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem *)"), self.editAccountInfo)
        
        self.connect(self.actionAdd, QtCore.SIGNAL("triggered()"), self.add_action)
        self.connect(self.actionDel, QtCore.SIGNAL("triggered()"), self.del_action)
        self.connect(self.toolButton_agreement_print, QtCore.SIGNAL("clicked()"), self.printAgreement)

        
        self.fixtures()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader(self.tableWidget.objectName(), bhdr)
            HeaderUtil.getHeader(self.tableWidget.objectName(), self.tableWidget)
        else: self.firsttime = False
        tableHeader = self.tableWidget.horizontalHeader()
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        self.dhcpActions()
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Профиль аккаунта", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_management_info.setTitle(QtGui.QApplication.translate("MainWindow", "Менеджмент", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_account_data.setTitle(QtGui.QApplication.translate("MainWindow", "Учётные данные", None, QtGui.QApplication.UnicodeUTF8))
        self.label_username.setText(QtGui.QApplication.translate("MainWindow", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_generate_login.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.label_password.setText(QtGui.QApplication.translate("MainWindow", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_generate_password.setText(QtGui.QApplication.translate("MainWindow", "#", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_agreement.setTitle(QtGui.QApplication.translate("MainWindow", "Договор", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement_date.setText(QtGui.QApplication.translate("MainWindow", "Дата подключения", None, QtGui.QApplication.UnicodeUTF8))
        self.label_agreement_num.setText(QtGui.QApplication.translate("MainWindow", "Номер договора", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_urdata.setTitle(QtGui.QApplication.translate("MainWindow", "Юридическое лицо", None, QtGui.QApplication.UnicodeUTF8))
        self.label_organization.setText(QtGui.QApplication.translate("MainWindow", "Организация", None, QtGui.QApplication.UnicodeUTF8))
        self.label_rs.setText(QtGui.QApplication.translate("MainWindow", "Расчётный счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_okpo.setText(QtGui.QApplication.translate("MainWindow", "ОКПО", None, QtGui.QApplication.UnicodeUTF8))
        self.label_unp.setText(QtGui.QApplication.translate("MainWindow", "УНП", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "КПП", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Корресп. счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank.setText(QtGui.QApplication.translate("MainWindow", "Банк, код банка", None, QtGui.QApplication.UnicodeUTF8))
        self.label_uraddress.setText(QtGui.QApplication.translate("MainWindow", "Юридический адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.label_urphone.setText(QtGui.QApplication.translate("MainWindow", "Телефон", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fax.setText(QtGui.QApplication.translate("MainWindow", "Факс", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_balance_info.setTitle(QtGui.QApplication.translate("MainWindow", "Информация о балансе", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Комментарий", None, QtGui.QApplication.UnicodeUTF8))
        self.label_balance.setText(QtGui.QApplication.translate("MainWindow", "Текущий баланс", None, QtGui.QApplication.UnicodeUTF8))
        self.label_credit.setText(QtGui.QApplication.translate("MainWindow", "Максимальный кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_credit.setText(QtGui.QApplication.translate("MainWindow", "Работать в кредит", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_general), QtGui.QApplication.translate("MainWindow", "Общее", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_nas.setTitle(QtGui.QApplication.translate("MainWindow", "Сервер доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nas.setText(QtGui.QApplication.translate("MainWindow", "Основной сервера доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_bank_code.setText(QtGui.QApplication.translate("MainWindow", "Код", None, QtGui.QApplication.UnicodeUTF8))
        self.label_manager.setText(QtGui.QApplication.translate("MainWindow", "Менеджер", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setColumnHidden(0, False)
        columns = [u"Название", u"Значение"]
        makeHeaders(columns, self.tableWidget)
        #self.tableWidget.
        
        cities = self.connection.sql("SELECT id, name FROM billservice_city ORDER BY name ASC;")
        streets = self.connection.sql("SELECT id, name FROM billservice_street ORDER BY name ASC;")
        houses = self.connection.sql("SELECT id, name FROM billservice_house ORDER BY name ASC;")
        self.connection.commit()
        self.tableInfo=[
            #['ur', u'Юридическое лицо','checkbox'],
            ['contactperson', u'Контактное лицо',''],
            ['contactperson_phone', u'Тел. Контактного лица',''],
            ['fullname', u'ФИО абонента',''],
            ['email',u'e-mail',''],
            ['phone_h',u'Телефон дом.',''],
            ['phone_m',u'Телефон моб.',''],
            ['passport',u'Паспорт №',''],
            ['private_passport_number',u'Личный номер',''],
            ['passport_given',u'Кем выдан',''],
            ['passport_date',u'Когда выдан',''],
            ['city', u'Город','combobox', self.comboBox_city],
            ['postcode',u'Индекс',''],
            ['region',u'Район',''],
            ['street',u'Улица','combobox', self.comboBox_street],
            ['house',u'Дом','combobox', self.comboBox_house],
            ['house_bulk',u'Корпус',''],
            ['entrance',u'Подъезд',''],
            ['entrance_code',u'Код домофона',''],
            ['row',u'Этаж',''],
            ['elevator_direction',u'Направление от лифта',''],
            ['room', u'Квартира',''],
            ]
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.tableInfo))
        i=0
        for item in self.tableInfo:
            self.addrow(self.tableWidget, item[1], i, 0, id=item[0])
            if item[2]:
                self.addrow(self.tableWidget, '', i, 1, widget_type = item[2], widget_item=item[3])
            i+=1
            

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_network_settings), QtGui.QApplication.translate("MainWindow", "Сетевые параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_subaccounts), QtGui.QApplication.translate("MainWindow", "Субаккаунты", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_suspended), QtGui.QApplication.translate("MainWindow", "Не списывать ПУ", None, QtGui.QApplication.UnicodeUTF8))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tarifs), QtGui.QApplication.translate("MainWindow", "Тарифные планы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addonservice), QtGui.QApplication.translate("MainWindow", "Подключаемые услуги", None, QtGui.QApplication.UnicodeUTF8))

        self.actionSave.setText(QtGui.QApplication.translate("MainWindow", "Сохранить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd.setText(QtGui.QApplication.translate("MainWindow", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDel.setText(QtGui.QApplication.translate("MainWindow", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_status.setTitle(QtGui.QApplication.translate("MainWindow", "Статус аккаунта", None, QtGui.QApplication.UnicodeUTF8))

        self.ipRx = QtCore.QRegExp(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
        self.ipValidator = QtGui.QRegExpValidator(self.ipRx, self)
        
        self.ipnRx = QtCore.QRegExp(r"\b(?:0\.0\.0\.0(/0)?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.0\.0\.0(?:/[1-8])?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){2}0\.0(?:/(?:9|1[0-6]))?)|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?\.){3}0(?:/(?:1[7-9]|2[0-4]))?)|(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:2[5-9]|3[0-2]))?)\b")
        self.ipnValidator = QtGui.QRegExpValidator(self.ipnRx, self)
        self.macValidator = QtGui.QRegExpValidator(QtCore.QRegExp(r"([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$"), self)
        
        #self.lineEdit_ipn_ip_address.setValidator(self.ipnValidator)
        #self.lineEdit_vpn_ip_address.setValidator(self.ipValidator)
        #self.lineEdit_ipn_ip_mask.setValidator(self.ipValidator)
        #self.lineEdit_ipn_mac_address.setValidator(self.macValidator)
        
        self.tableWidget_accounttarif.clear()

        columns = ["#", u"С",u"По"]
        self.tableWidget_suspended = tableFormat(self.tableWidget_suspended)
        makeHeaders(columns, self.tableWidget_suspended)
 
        columns=[u'#', u'Имя пользователя', u'Пароль', u'VPN IP', u'IPN IP', u'IPN MAC', u'Сервер доступа', u'IPN статус',]
        self.tableWidget_subaccounts = tableFormat(self.tableWidget_subaccounts)
        makeHeaders(columns, self.tableWidget_subaccounts)
                
        columns=[u'#', u'Тарифный план', u'Дата', u'Расчётный период закрыт']
        self.tableWidget_accounttarif = tableFormat(self.tableWidget_accounttarif)
        makeHeaders(columns, self.tableWidget_accounttarif)


        columns=[u'#', u'Название услуги', u'Дата активации', u'Дата окончания', u'Активирована на сервере доступа', u"Временная блокировка"]
        self.tableWidget_addonservice = tableFormat(self.tableWidget_addonservice)
        makeHeaders(columns, self.tableWidget_addonservice)
        
        self.comboBox_status.addItem(u"Активен")
        self.comboBox_status.setItemData(0, QtCore.QVariant(1))
        self.comboBox_status.addItem(u"Неактивен, не списывать периодические услуги")
        self.comboBox_status.setItemData(1, QtCore.QVariant(2))
        self.comboBox_status.addItem(u"Неактивен, списывать периодические услуги")
        self.comboBox_status.setItemData(2, QtCore.QVariant(3))
    
    def refresh_combo_city(self):
        pass
    def refresh_combo_street(self):
        city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
        if not city_id: return
        streets = self.connection.sql("SELECT id, name FROM billservice_street WHERE city_id=%s ORDER BY name ASC;" % city_id)
        self.connection.commit()
        self.comboBox_street.clear()
        self.comboBox_house.clear()
        i=0
        for street in streets:
            self.comboBox_street.addItem(street.name, QtCore.QVariant(street.id))
            if self.model:
                if self.model.street_id==street.id:
                    self.comboBox_street.setCurrentIndex(i)
            i+=1

    def refresh_combo_house(self):
        street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
        if not street_id: return        
        items = self.connection.sql("SELECT id, name FROM billservice_house WHERE street_id=%s ORDER BY name ASC;" % street_id)
        self.connection.commit()
        self.comboBox_house.clear()
        i=0
        for item in items:
            self.comboBox_house.addItem(item.name, QtCore.QVariant(item.id))
            if self.model:
                if self.model.house_id==item.id:
                    self.comboBox_house.setCurrentIndex(i)
            i+=1
    def saveHeader(self, *args):

        HeaderUtil.saveHeader(self.tableWidget.objectName(), self.tableWidget)
            
    def printAgreement(self):
       
        tarif = self.connection.get("SELECT name FROM billservice_tariff WHERE id = get_tarif(%s)" % self.model.id)
        operator = self.connection.get("SELECT * FROM billservice_operator LIMIT 1")
        child = TemplateSelect(connection = self.connection)
        if child.exec_():
            template_id = child.id
        else:
            return
        template = self.connection.get_model(template_id, "billservice_template")
        templ = Template(template.body, input_encoding='utf-8')
        if self.groupBox_urdata.isChecked()==True:
            
            try:
                data=templ.render_unicode(account=self.model, tarif=tarif, operator=operator, organization = self.organization, bank=self.bank, created=datetime.datetime.now().strftime(strftimeFormat))
            except Exception, e:
                data=unicode(u"Ошибка ендеринга документа: %s" % e)
            
        else:
            try:
                data=templ.render_unicode(account=self.model, tarif=tarif, created=datetime.datetime.now().strftime(strftimeFormat))
            except Exception, e:
                data=unicode(u"Ошибка ендеринга документа: %s" % e)
            self.connection.commit()
            file= open('templates/tmp/temp.html', 'wb')
            file.write(data.encode("utf-8", 'replace'))
            file.flush()
            a=CardPreviewDialog(url="templates/tmp/temp.html")
            a.exec_()
       
            
  
    def generate_login(self):
        self.lineEdit_username.setText(nameGen())

    def generate_password(self):
        self.lineEdit_password.setText(GenPasswd2())
        
    def dhcpActions(self, newstate=0):
        pass
    
    def fixtures(self):


        pools = []

        nasses = self.connection.get_models("nas_nas")
        self.connection.commit()
        i=0
        self.comboBox_nas.clear()
        self.comboBox_nas.addItem("---")
        self.comboBox_nas.setItemData(i, QtCore.QVariant(0))
        for nas in nasses:
            self.comboBox_nas.addItem(nas.name)
            self.comboBox_nas.setItemData(i+1, QtCore.QVariant(nas.id))
            if self.model:
                if nas.id==self.model.nas_id:
                    self.comboBox_nas.setCurrentIndex(i+1)
            
            i+=1
            

        managers = self.connection.get_models("billservice_systemuser")
        self.connection.commit()
        
        self.comboBox_manager.clear()
        self.comboBox_manager.addItem("---")
        self.comboBox_manager.setItemData(0, QtCore.QVariant(0))
        i=1
        for manager in managers:
            self.comboBox_manager.addItem(manager.username)
            self.comboBox_manager.setItemData(i, QtCore.QVariant(manager.id))
            if self.model:
                if manager.id==self.model.systemuser_id:
                    self.comboBox_manager.setCurrentIndex(i)
            
            i+=1
                        

        cities = self.connection.sql("SELECT id, name FROM billservice_city ORDER BY name ASC;")
        self.connection.commit()
        self.comboBox_city.clear()
        i=0
        for city in cities:
            self.comboBox_city.addItem(city.name, QtCore.QVariant(city.id))
            if self.model:
                if self.model.city_id==city.id:
                    self.comboBox_city.setCurrentIndex(i)
            i+=1
                  
        if not self.model:
            self.actionAdd.setDisabled(True)
            self.actionDel.setDisabled(True)
            self.toolButton_agreement_print.setDisabled(True)
            self.lineEdit_balance.setText(u"0")
            self.lineEdit_credit.setText(u"0")

        self.dateTimeEdit_agreement_date.setDateTime(datetime.datetime.now())
        if self.model:
            self.lineEdit_agreement_num.setText(unicode(self.model.contract))
            self.dateTimeEdit_agreement_date.setDateTime(self.model.created)
            self.dateTimeEdit_agreement_date.setDisabled(True)

            self.comboBox_status.setCurrentIndex(self.model.status-1)

            self.lineEdit_username.setText(unicode(self.model.username))
            self.lineEdit_password.setText(unicode(self.model.password))
            
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, unicode(self.model.__dict__.get(self.tableInfo[i][0],'')), i,1)


            self.plainTextEdit_comment.setPlainText(unicode(self.model.comment))
            

            self.lineEdit_balance.setText(unicode(self.model.ballance))
            self.lineEdit_credit.setText(unicode(self.model.credit))
            
            organization = self.connection.get_models("billservice_organization", where={'account_id':self.model.id})
            self.connection.commit()
            if organization:
                
                org = organization[0]
                self.organization = org
                self.groupBox_urdata.setChecked(True)
                self.lineEdit_organization.setText(unicode(org.name))
                self.lineEdit_uraddress.setText(unicode(org.uraddress))
                self.lineEdit_urphone.setText(unicode(org.phone))
                self.lineEdit_fax.setText(unicode(org.fax))
                self.lineEdit_okpo.setText(unicode(org.okpo))
                self.lineEdit_unp.setText(unicode(org.unp))
                self.lineEdit_kpp.setText(unicode(org.kpp))
                self.lineEdit_kor_s.setText(unicode(org.kor_s))
                
                #print "bank_id",org.bank_id
                bank = self.connection.get_model(org.bank_id, "billservice_bankdata")
                self.connection.commit()
                if bank:
                    self.lineEdit_bank.setText(unicode(bank.bank))
                    self.lineEdit_bank_code.setText(unicode(bank.bankcode))
                    self.lineEdit_rs.setText(unicode(bank.rs))
            
            else:
                #self.groupBox_urdata.setChecked(False)
                pass
            self.accountTarifRefresh()
            self.suspendedPeriodRefresh()
            self.accountAddonServiceRefresh()
            self.subAccountLinkRefresh()
        else:
            for i in xrange(self.tableWidget.rowCount()):
                self.addrow(self.tableWidget, '', i,1)

    def accept(self):
        """
        понаставить проверок
        """
        try:
            
            if self.model:
                model=self.model
            else:
                #print 'New account'
                if self.connection.get("SELECT count(*) as count FROM billservice_account WHERE username='%s'" % unicode(self.lineEdit_username.text())).count > 0:
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Пользователь с таким логином уже существует."))
                    self.connection.rollback()
                    return

                model=Object()
                model.created = self.dateTimeEdit_agreement_date.dateTime().toPyDateTime()
                #model.user_id=1
                model.ipn_status = False
                model.ipn_added = False
                model.disabled_by_limit = False
                model.vpn_ipinuse_id = None
                model.ipn_ipinuse_id = None
                
                
            model.username = unicode(self.lineEdit_username.text())
            
            if model.username=='':
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не указали имя пользователя."))
                return 
            #print 1
            model.password = unicode(self.lineEdit_password.text())
            model.contract = unicode(self.lineEdit_agreement_num.text())
            model.status = self.comboBox_status.itemData(self.comboBox_status.currentIndex()).toInt()[0]
            for i in xrange(self.tableWidget.rowCount()):
                model.__dict__[self.tableInfo[i][0]] = unicode(self.tableWidget.item(i,1).text()) 
                #self.tableWidget.item(i,1).setText(unicode(self.model.__dict__.get(self.tableInfo[i][0])))
                

            model.nas_id = self.comboBox_nas.itemData(self.comboBox_nas.currentIndex()).toInt()[0]
            model.systemuser_id = self.comboBox_manager.itemData(self.comboBox_manager.currentIndex()).toInt()[0]

            model.ballance = unicode(self.lineEdit_balance.text()) or 0
            model.credit = unicode(self.lineEdit_credit.text()) or 0
            model.comment = unicode(self.plainTextEdit_comment.toPlainText())
            
            city_id = self.comboBox_city.itemData(self.comboBox_city.currentIndex()).toInt()[0]
            if city_id:
                model.city_id = city_id
                
            street_id = self.comboBox_street.itemData(self.comboBox_street.currentIndex()).toInt()[0]
            if street_id:
                model.street_id = street_id
                
            house_id = self.comboBox_house.itemData(self.comboBox_house.currentIndex()).toInt()[0]
            if house_id:
                model.house_id = house_id
                
                                
            if self.model:
                model.id = self.connection.save(model, "billservice_account")
            else:
                #print 123
                model.id=self.connection.save(model, "billservice_account")
                accounttarif = Object()
                accounttarif.account_id=model.id
                accounttarif.tarif_id=self.tarif_id
                accounttarif.datetime = "now()"
                self.connection.save(accounttarif,"billservice_accounttarif")

            if self.groupBox_urdata.isChecked():
                if unicode(self.lineEdit_organization.text())=="" or unicode(self.lineEdit_bank.text())=="":
                    QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указаны реквизиты юридического лица(название организации, банк)."))
                    return
                if self.organization:
                    org = self.organization
                    bank = self.connection.get_model(org.bank_id, "billservice_bankdata")
                else:
                    org = Object()
                    bank = Object()
                
                bank.bank = unicode(self.lineEdit_bank.text())
                bank.bankcode = unicode(self.lineEdit_bank_code.text())
                bank.rs = unicode(self.lineEdit_rs.text())
                bank.currency = ''
                bank.id = self.connection.save(bank, "billservice_bankdata")
                self.bank = bank
                
                org.name = unicode(self.lineEdit_organization.text())
                org.uraddress = unicode(self.lineEdit_uraddress.text())
                org.phone = unicode(self.lineEdit_urphone.text())
                org.fax = unicode(self.lineEdit_fax.text())
                org.okpo = unicode(self.lineEdit_okpo.text())
                org.unp = unicode(self.lineEdit_unp.text())
                org.kpp = unicode(self.lineEdit_kpp.text())
                org.kor_s = unicode(self.lineEdit_kor_s.text())
                org.account_id = model.id
                org.bank_id = bank.id
                org.id = self.connection.save(org, "billservice_organization")
                self.organization = org
                #print "save org.data"
            else:
                if self.organization:
                    self.connection.iddelete(self.organization.id, "billservice_organization")    
            
                    
            #x8021 = self.connection.get
            self.connection.commit()
            self.model = model
            self.fixtures()
            self.emit(QtCore.SIGNAL("refresh()"))
        except Exception, e:
            import traceback
            traceback.print_exc()
            if isinstance(e, psycopg2.InternalError) and e.args[0].startswith('Amount'):
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Достигнуто максимальное число пользователей. \n" + e.args[0]))
            else:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Ошибка при сохранении."))
            self.connection.rollback()
            return
        
    def accountTarifRefresh(self):
        if self.model:
            ac=self.connection.sql("""SELECT accounttarif.*, tarif.name as tarif_name FROM billservice_accounttarif as accounttarif 
            JOIN billservice_tariff as tarif ON tarif.id=accounttarif.tarif_id
            WHERE account_id=%d AND tarif.deleted IS NOT TRUE ORDER BY datetime ASC""" % self.model.id)
            self.tableWidget_accounttarif.setRowCount(len(ac))
            i=0
            #print ac
            for a in ac:

                self.addrow(self.tableWidget_accounttarif, a.id, i,0)
                self.addrow(self.tableWidget_accounttarif, a.tarif_name, i,1)
                self.addrow(self.tableWidget_accounttarif, a.datetime.strftime(strftimeFormat), i,2)
                self.addrow(self.tableWidget_accounttarif, u"Да" if a.periodical_billed else u"Нет", i,3)
                i+=1

            self.tableWidget_accounttarif.setColumnHidden(0, True)
            self.tableWidget_accounttarif.resizeColumnsToContents()
            self.connection.commit()
    
    def editAccountInfo(self, item):
        if item.column()==1:
            self.tableWidget.editItem(item)
            
    def suspendedPeriodRefresh(self):
        if self.model:
            sp = self.connection.get_models("billservice_suspendedperiod", where={'account_id':self.model.id})
            self.connection.commit()
            self.tableWidget_suspended.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_suspended, a.id, i, 0)
                self.addrow(self.tableWidget_suspended, a.start_date.strftime(strftimeFormat), i, 1)
                try:
                    self.addrow(self.tableWidget_suspended, a.end_date.strftime(strftimeFormat), i, 2)
                except:
                    self.addrow(self.tableWidget_suspended, u"Не закончен", i, 2)
                i+=1
            self.tableWidget_suspended.setColumnHidden(0, True)
      
      
    def accountAddonServiceRefresh(self):
        if self.model:
            sp = self.connection.sql("""
            SELECT accadd.*, adds.name as addonservice_name, adds.id as addonservice_id FROM billservice_accountaddonservice as accadd
            JOIN billservice_addonservice as adds ON adds.id=accadd.service_id
            WHERE account_id=%s and subaccount_id is Null ORDER BY id DESC
            """ % self.model.id)
            self.connection.commit()
            self.tableWidget_addonservice.clearContents()
            self.tableWidget_addonservice.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_addonservice, a.id, i, 0)
                self.addrow(self.tableWidget_addonservice, a.addonservice_name, i, 1)
                self.addrow(self.tableWidget_addonservice, a.activated.strftime(strftimeFormat), i, 2)
                try:
                    self.addrow(self.tableWidget_addonservice, a.deactivated.strftime(strftimeFormat), i, 3)
                except:
                    self.addrow(self.tableWidget_addonservice, u"Не закончен", i, 3)
                self.addrow(self.tableWidget_addonservice, a.action_status, i, 4)
                try:
                    self.addrow(self.tableWidget_addonservice, a.temporary_blocked.strftime(strftimeFormat), i, 5)
                except:
                    pass
                i+=1
            self.tableWidget_addonservice.setColumnHidden(0, True)
            self.tableWidget_addonservice.resizeColumnsToContents()
            
    def subAccountLinkRefresh(self):
        if self.model:
            sp = self.connection.get_models("billservice_subaccount", where={'account_id':self.model.id})
            
            sp = self.connection.sql("""
            SELECT *, (SELECT name FROM nas_nas WHERE id=subaccount.nas_id) as nas_name FROM billservice_subaccount as subaccount
            WHERE account_id=%s ORDER BY id DESC
            """ % self.model.id)            
            self.connection.commit()
            self.tableWidget_subaccounts.setRowCount(len(sp))
            i=0
            for a in sp:
                self.addrow(self.tableWidget_subaccounts, a.id, i, 0)
                self.addrow(self.tableWidget_subaccounts, a.username, i, 1)
                self.addrow(self.tableWidget_subaccounts, a.password, i, 2)
                self.addrow(self.tableWidget_subaccounts, a.vpn_ip_address, i, 3)
                self.addrow(self.tableWidget_subaccounts, a.ipn_ip_address, i, 4)
                self.addrow(self.tableWidget_subaccounts, a.ipn_mac_address, i, 5)
                self.addrow(self.tableWidget_subaccounts, a.nas_name, i, 6)
                self.tableWidget_subaccounts.setCellWidget(i,7,tableImageWidget(ipn_sleep=a.ipn_sleep, ipn_status=a.ipn_enabled, ipn_added=a.ipn_added))
                #self.addrow(self.tableWidget_subaccounts, a.start_date.strftime(strftimeFormat), i, 1)
                #try:
                #    self.addrow(self.tableWidget_subaccounts, a.end_date.strftime(strftimeFormat), i, 2)
                #except:
                #    self.addrow(self.tableWidget_subaccounts, u"Не закончен", i, 2)
                i+=1
            self.tableWidget_subaccounts.setColumnHidden(0, True)  
    
    def addrow(self, widget, value, x, y, id=None, editable=False, widget_type = None, widget_item=None):
        headerItem = QtGui.QTableWidgetItem()
        if widget_type == 'checkbox':
            headerItem.setCheckState(QtCore.Qt.Unchecked)
        if widget_type == 'combobox':
            #headerItem = QtGui.QComboBox(self)
            widget.setCellWidget(x,y,widget_item)
            return
        if value==None or value=="None":
            value=''
        if y==0:
            headerItem.id=value
        headerItem.setText(unicode(value))
        if id:
            headerItem.id=id
            
           
        widget.setItem(x,y,headerItem)
        
    
    def getSelectedId(self, table):
        try:
            return int(table.item(table.currentRow(), 0).text())
        except:
            return -1

    def add_action(self):
        if self.tabWidget.currentIndex()==4:
            self.add_accounttarif()
        elif self.tabWidget.currentIndex()==2:
            self.add_suspendedperiod()
        elif self.tabWidget.currentIndex()==5:
            self.addAddonService()
        elif self.tabWidget.currentIndex()==3:
            self.addSubAccountLink()
    
    def del_action(self):
        if self.tabWidget.currentIndex()==4:
            self.del_accounttarif()
        elif self.tabWidget.currentIndex()==2:
            self.del_suspendedperiod()
        elif self.tabWidget.currentIndex()==3:
            self.delSubAccountLink()
           
    def addSubAccountLink(self):
        child=SubaccountLinkDialog(connection=self.connection, account=self.model)
        if child.exec_()==1:
            self.subAccountLinkRefresh()
            
    def add_accounttarif(self):

        child=AddAccountTarif(connection=self.connection, account=self.model)
        
        if child.exec_()==1:
            self.accountTarifRefresh()

    def addAddonService(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        child = AccountAddonServiceEdit(connection=self.connection, account_model = self.model.id)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editAddonService(self):
        i=self.getSelectedId(self.tableWidget_addonservice)
        try:
            model = self.connection.get_model(i, "billservice_accountaddonservice")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = AccountAddonServiceEdit(connection=self.connection, model=model, account_model = self.model.id)
        if child.exec_()==1:
            self.accountAddonServiceRefresh()
        
    def editSubAccount(self):
        i=self.getSelectedId(self.tableWidget_subaccounts)
        try:
            model = self.connection.get_model(i, "billservice_subaccount")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        child = SubaccountLinkDialog(connection=self.connection, model=model, account = self.model)
        if child.exec_()==1:
            self.subAccountLinkRefresh()
            
    def del_accounttarif(self):
        i=self.getSelectedId(self.tableWidget_accounttarif)
        try:
            model = self.connection.get_model(i, "billservice_accounttarif")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        
        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_accounttarif")
            self.accountTarifRefresh()

    def delSubAccountLink(self):
        i=self.getSelectedId(self.tableWidget_subaccounts)
        try:
            model = self.connection.get_model(i, "billservice_subaccount")
        except:
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Запись не найдена."))
            return
        
        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_subaccount")
            self.subAccountLinkRefresh()
            
    def add_suspendedperiod(self):
        child=SuspendedPeriodForm()

        if child.exec_()==1:
            model = Object()
            model.account_id = self.model.id
            model.start_date = child.start_date
            model.end_date = child.end_date
            self.connection.save(model, "billservice_suspendedperiod")
            self.connection.commit()
            self.suspendedPeriodRefresh()

    def edit_suspendedperiod(self):
        
        i=self.getSelectedId(self.tableWidget_suspended)
        model = self.connection.get_model(i, "billservice_suspendedperiod")
        self.connection.commit()
        child=SuspendedPeriodForm(model)

        if child.exec_()==1:
            model.start_date = child.start_date
            model.end_date = child.end_date
            self.connection.save(model, "billservice_suspendedperiod")
            self.connection.commit()
            self.suspendedPeriodRefresh()
            
    def del_suspendedperiod(self):
        i=self.getSelectedId(self.tableWidget_suspended)
        ###

        if QtGui.QMessageBox.question(self, u"Удалить запись?" , u"Вы уверены, что хотите удалить эту запись из системы?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)==QtGui.QMessageBox.Yes:
            self.connection.iddelete(i, "billservice_suspendedperiod")
            self.suspendedPeriodRefresh()
    
    def edit_accounttarif(self):
        i=self.getSelectedId(self.tableWidget_accounttarif)
        try:
            model=self.connection.get_model(i, "billservice_accounttarif")
        except:
            return

        if model.datetime<datetime.datetime.now():
            QtGui.QMessageBox.warning(self, u"Внимание", unicode(u"Эту запись отредактировать или удалить нельзя,\n так как с ней уже связаны записи статистики и другая информация,\n необходимая для обеспечения целостности системы."))
            return

        child=AddAccountTarif(connection=self.connection, ttype=self.ttype, model=model)
        if child.exec_()==1:
            self.accountTarifRefresh()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() in (QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter) and self.tableWidget.hasFocus():
            i=self.tableWidget.currentRow()
            #print i
            self.tableWidget.setCurrentCell(i+1,1)
            self.tableWidget.editItem(self.tableWidget.currentItem())
