# Copyright 2009-2014 Eucalyptus Systems, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
# Please contact Eucalyptus Systems, Inc., 6755 Hollister Ave., Goleta
# CA 93117, USA or visit http://www.eucalyptus.com/licenses/ if you need
# additional information or have any questions.

#
# Order matters here. We want to make sure we initialize logging before anything
# else happens. We need to initialize the logger that boto will be using.
#
from worker.logutil import log, set_loglevel
from worker.config import set_pidfile, set_boto_config
from worker.main_loop import WorkerLoop
import worker.config as config
import worker
import subprocess
import os

__version__ = '1.0.0-dev'
Version = __version__

def get_block_devices():
    retlist=[]
    for filename in os.listdir('/dev'):
        if any(filename.startswith(prefix) for prefix in ('sd', 'xvd', 'vd', 'xd')):
            retlist.append('/dev/' + filename)
    retlist.sort(reverse=True)
    return retlist

def start_worker():
    if subprocess.call('sudo modprobe floppy > /dev/null', shell=True) != 0:
        log.error('failed to load floppy driver')
    try:
        last_dev = get_block_devices()[0]
        worker.config.get_worker_id()
        if subprocess.call('ls -la %s > /dev/null' % last_dev, shell=True) != 0 or subprocess.call('ls -la /mnt > /dev/null', shell=True) != 0:
            log.error('failed to find %s or /mnt' % last_dev)
        else:
            if subprocess.call('sudo mount | grep /mnt > /dev/null', shell=True) == 1:
                if subprocess.call('sudo mkfs.ext3 %s 2>> /tmp/init.log' % last_dev, shell=True) != 0 or subprocess.call('sudo mount %s /mnt 2>> /tmp/init.log' % last_dev, shell=True) != 0:
                    log.error('failed to format and mount %s ' % last_dev)
                else:
                    log.info('%s was successfully formatted and mounted to /mnt' % last_dev)
            else:
                log.info('%s is alredy mounted to /mnt' % last_dev)
    except Exception, err:
        log.error("Can't detect VM's id or set up worker due to %s", err)
        sys.exit(1)
    WorkerLoop().start()
