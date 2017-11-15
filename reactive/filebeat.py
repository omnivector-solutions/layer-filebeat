from charms.reactive import (
    when,
    when_not,
    set_flag,
    clear_flag
)
from charms.reactive import hook

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import restart_on_change, service_stop

import charms.apt

from elasticbeats import render_without_context
from elasticbeats import enable_beat_on_boot
from elasticbeats import push_beat_index

import os


@restart_on_change('/etc/filebeat/filebeat.yml', ['filebeat'])
@when('beat.render')
@when('apt.installed.filebeat')
def render_filebeat_template():
    connections = \
        render_without_context(
            'filebeat.yml', '/etc/filebeat/filebeat.yml')
    clear_flag('beat.render')
    if connections:
        status_set('active', 'Filebeat ready.')


@when('apt.installed.filebeat')
@when_not('filebeat.autostarted')
def enlist_packetbeat():
    enable_beat_on_boot('filebeat')
    set_flag('filebeat.autostarted')


@when('apt.installed.filebeat')
@when('elasticsearch.available')
@when_not('filebeat.index.pushed')
def push_filebeat_index(elasticsearch):
    hosts = elasticsearch.list_unit_data()
    for host in hosts:
        host_string = "{}:{}".format(host['host'], host['port'])
    push_beat_index(host_string, 'filebeat')
    set_flag('filebeat.index.pushed')


@hook('stop')
def remove_filebeat():
    service_stop('filebeat')
    try:
        os.remove('/etc/filebeat/filebeat.yml')
    except OSError:
        pass
    charms.apt.purge('filebeat')
