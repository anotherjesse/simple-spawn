#!/usr/bin/env python

import datetime
import os
import paramiko
import subprocess
import sys
import time

from novaclient.v1_1 import client

try:
    OS_AUTH_URL = os.environ['OS_AUTH_URL']
    OS_TENANT_NAME = os.environ['OS_TENANT_NAME']
    OS_USERNAME = os.environ['OS_USERNAME']
    OS_PASSWORD = os.environ['OS_PASSWORD']
    SSH_KEY_NAME = os.environ.get('SSH_KEY_NAME', OS_USERNAME)
except:
    print 'ERROR: download and source your openstack credentials'
    sys.exit(1)

#IMAGE_ID = 'e17a8ca3-5654-4adb-92d3-ea4d782ab4b7'   # precise
IMAGE_ID = '82e43989-6485-4cdb-a2f3-9d2a0d792d76'    # precise-32
FLAVOR_ID = '14a7581f-4c6b-4543-a7f5-f30cfdce06de'  # pl.small


def osc():
    return client.Client(OS_USERNAME, OS_PASSWORD, OS_TENANT_NAME,
                         OS_AUTH_URL, service_type="compute")


def spawn(book):
    nova = osc()
    userdata = open('books/%s.yml' % book).read()
    instance_name = book
    inst = nova.servers.create(name=instance_name,
                               image=IMAGE_ID,
                               flavor=FLAVOR_ID,
                               userdata=userdata,
                               key_name=SSH_KEY_NAME)
    return inst.id


def kill(name):
    nova = osc()
    for s in nova.servers.list():
        if s.name == name:
            print "DELETE: %s" % s
            nova.servers.delete(s.id)


def get_ip(id):
    nova = osc()
    inst = nova.servers.get(id)

    while inst.status == 'BUILD':
        time.sleep(0.5)
        inst = nova.servers.get(inst.id)

    return inst.networks['private'][0]


def connect(ip):
    path = os.path.expanduser('~/.ssh/id_rsa')
    key = paramiko.RSAKey.from_private_key_file(path)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.WarningPolicy())
    c.connect(ip, username='ubuntu', pkey=key, timeout=1)
    return c


def wait_for_ssh(ip):
    while True:
        try:
            connect(ip).exec_command('uptime')
            return True
        except Exception, e:
            time.sleep(0.5)


def delta(start):
    return (datetime.datetime.now() - start).total_seconds()


def magic(book):
    kill(book)

    start = datetime.datetime.now()

    id = spawn(book)
    print '[%05.1f] spawn: %s' % (delta(start), id)

    ip = get_ip(id)
    print '[%05.1f] ip: %s' % (delta(start), ip)

    wait_for_ssh(ip)
    print '[%05.1f] ssh: connect' % delta(start)

    subprocess.check_output(["scp", "books/%s.sh" % book, "ubuntu@%s:" % ip])
    p = subprocess.Popen(["ssh", "-A", "ubuntu@%s" % ip, "time sh %s.sh" % book])

    working = True
    while working:
        time.sleep(0.1)
        working = p.poll() is None

    print "\n[%05.1f] built: %s" % (delta(start), id)


def interactive(book):
    try:
        magic(book)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'USAGE: %s (book) [repeat]' % sys.argv[0]
        print
        print '  book: name of the recipe to run'
        print '  repeat: if set we re-run on a new vm after killing current'
        sys.exit(1)
    else:
        if len(sys.argv) == 2:
            interactive(sys.argv[1])
        else:
            while True:
                interactive(sys.argv[1])
                time.sleep(1)
