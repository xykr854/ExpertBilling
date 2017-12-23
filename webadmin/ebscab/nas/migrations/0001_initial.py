# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-12 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ebscab.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '__first__')
    ]

    operations = [
        migrations.CreateModel(
            name='Nas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('mikrotik2.8', b'MikroTik 2.8'), ('mikrotik2.9', b'MikroTik 2.9'), ('mikrotik3', b'Mikrotik 3'), ('mikrotik4', b'Mikrotik 4'), ('mikrotik5', b'Mikrotik 5'), ('mikrotik6', b'Mikrotik 6'), ('cisco', 'cisco'), ('common_radius', b'Common RADIUS interface'), ('common_ssh', 'common_ssh'), ('localhost', b'Local execution'), ('switch', b'Switch'), ('accel-ipoe', 'Accel IPOE'), ('accel-ipoe-l3', 'Accel IPOE L3'), ('lISG', 'lISG')], default=b'mikrotik3', max_length=32)),
                ('identify', models.CharField(max_length=255, verbose_name='RADIUS \u0438\u043c\u044f')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='\u0418\u043c\u044f')),
                ('ipaddress', models.GenericIPAddressField(verbose_name='IP \u0430\u0434\u0440\u0435\u0441')),
                ('secret', ebscab.fields.EncryptedTextField(help_text='\u0421\u043c\u043e\u0442\u0440\u0438\u0442\u0435 \u0432\u044b\u0432\u043e\u0434 \u043a\u043e\u043c\u0430\u043d\u0434\u044b /radius print', max_length=255, verbose_name='\u0421\u0435\u043a\u0440\u0435\u0442\u043d\u0430\u044f \u0444\u0440\u0430\u0437\u0430')),
                ('login', models.CharField(blank=True, default=b'admin', max_length=255, verbose_name='\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
                ('password', ebscab.fields.EncryptedTextField(blank=True, default=b'', max_length=255, verbose_name='\u041f\u0430\u0440\u043e\u043b\u044c')),
                ('snmp_version', models.CharField(blank=True, choices=[('v1', 'v1'), ('v2c', 'v2c')], max_length=10, null=True, verbose_name='\u0412\u0435\u0440\u0441\u0438\u044f SNMP')),
                ('user_add_action', models.TextField(blank=True, default=b'', null=True, verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043f\u0440\u0438 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
                ('user_enable_action', models.TextField(blank=True, default=b'', null=True, verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043f\u0440\u0438 \u0440\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0438 \u0440\u0430\u0431\u043e\u0442\u044b \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
                ('user_disable_action', models.TextField(blank=True, default=b'', null=True, verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043f\u0440\u0438 \u0437\u0430\u043f\u0440\u0435\u0449\u0435\u043d\u0438\u0438 \u0440\u0430\u0431\u043e\u0442\u044b \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
                ('user_delete_action', models.TextField(blank=True, default=b'', null=True, verbose_name='\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043f\u0440\u0438 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f')),
                ('vpn_speed_action', models.TextField(blank=True, default=b'', max_length=255, null=True)),
                ('ipn_speed_action', models.TextField(blank=True, default=b'', max_length=255, null=True)),
                ('reset_action', models.TextField(blank=True, default=b'', max_length=255, null=True)),
                ('subacc_disable_action', models.TextField(blank=True, default=b'', null=True)),
                ('subacc_enable_action', models.TextField(blank=True, default=b'', null=True)),
                ('subacc_add_action', models.TextField(blank=True, default=b'', null=True)),
                ('subacc_delete_action', models.TextField(blank=True, default=b'', null=True)),
                ('subacc_ipn_speed_action', models.TextField(blank=True, default=b'', null=True)),
                ('speed_vendor_1', models.IntegerField(blank=True, default=0, null=True)),
                ('speed_vendor_2', models.IntegerField(blank=True, default=0, null=True)),
                ('speed_attr_id1', models.IntegerField(blank=True, default=0, null=True)),
                ('speed_attr_id2', models.IntegerField(blank=True, default=0, null=True)),
                ('speed_value1', models.TextField(blank=True, default=b'')),
                ('speed_value2', models.TextField(blank=True, default=b'')),
                ('acct_interim_interval', models.IntegerField(blank=True, default=60)),
            ],
            options={
                'verbose_name': '\u0421\u0435\u0440\u0432\u0435\u0440 \u0434\u043e\u0441\u0442\u0443\u043f\u0430',
                'verbose_name_plural': '\u0421\u0435\u0440\u0432\u0435\u0440\u0430 \u0434\u043e\u0441\u0442\u0443\u043f\u0430',
                'permissions': (('nas_view', '\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440'),),
            },
        ),
        migrations.CreateModel(
            name='TrafficClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='\u041d\u0430\u0432\u0437\u0430\u043d\u0438\u0435 \u043a\u043b\u0430\u0441\u0441\u0430')),
                ('weight', models.IntegerField(blank=True, null=True, verbose_name='\u0412\u0435\u0441 \u043a\u043b\u0430\u0441\u0430 \u0432 \u0446\u0435\u043f\u043e\u0447\u043a\u0435 \u043a\u043b\u0430\u0441\u0441\u043e\u0432')),
                ('store', models.BooleanField(default=True, help_text='\u0425\u0440\u0430\u043d\u0438\u0442\u044c NetFlow \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0443 \u0432 \u0442\u0435\u043a\u0441\u0442\u043e\u0432\u043e\u043c \u0432\u0438\u0434\u0435', verbose_name='\u0425\u0440\u0430\u043d\u0438\u0442\u044c \u0441\u044b\u0440\u0443\u044e \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0443 \u043f\u043e \u043a\u043b\u0430\u0441\u0441\u0443')),
                ('passthrough', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043c\u0435\u0442\u0438\u0442\u044c \u0438 \u043f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c')),
            ],
            options={
                'ordering': ['weight'],
                'verbose_name': '\u041a\u043b\u0430\u0441\u0441 \u0442\u0440\u0430\u0444\u0438\u043a\u0430',
                'verbose_name_plural': '\u041a\u043b\u0430\u0441\u0441\u044b \u0442\u0440\u0430\u0444\u0438\u043a\u0430',
                'permissions': (('trafficclass_view', '\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440'),),
            },
        ),
        migrations.CreateModel(
            name='TrafficNode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('protocol', models.IntegerField(choices=[(0, '\u041b\u044e\u0431\u043e\u0439'), (37, b'ddp'), (98, b'encap'), (3, b'ggp'), (47, b'gre'), (20, b'hmp'), (1, b'icmp'), (38, b'idpr-cmtp'), (2, b'igmp'), (4, b'ipencap'), (94, b'ipip'), (89, b'ospf'), (27, b'rdp'), (6, b'tcp'), (17, b'udp')], default=0)),
                ('src_ip', ebscab.fields.IPNetworkField(blank=True, default=b'0.0.0.0/0', verbose_name='\u041d\u0430\u0448\u0430 \u0441\u0435\u0442\u044c')),
                ('src_port', models.IntegerField(blank=True, default=0, verbose_name='Src port')),
                ('dst_ip', ebscab.fields.IPNetworkField(blank=True, default=b'0.0.0.0/0', verbose_name='\u0423\u0434\u0430\u043b\u0451\u043d\u043d\u0430\u044f \u0441\u0435\u0442\u044c')),
                ('dst_port', models.IntegerField(blank=True, default=0, verbose_name='Dst port')),
                ('next_hop', models.GenericIPAddressField(blank=True, default=b'0.0.0.0', null=True, verbose_name='next Hop')),
                ('in_index', models.IntegerField(blank=True, default=0, verbose_name='SNMP IN')),
                ('out_index', models.IntegerField(blank=True, default=0, verbose_name='SNMP OUT')),
                ('src_as', models.IntegerField(blank=True, default=0, verbose_name='src_as')),
                ('dst_as', models.IntegerField(blank=True, default=0, verbose_name='dst_as')),
                ('traffic_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nas.TrafficClass')),
            ],
            options={
                'verbose_name': '\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0442\u0440\u0430\u0444\u0438\u043a\u0430',
                'verbose_name_plural': '\u041d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u0442\u0440\u0430\u0444\u0438\u043a\u0430',
                'permissions': (('trafficnode_view', '\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440'),),
            },
        ),
    ]