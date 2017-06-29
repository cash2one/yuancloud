# -*- coding: utf-8 -*-
import os
import tempfile

import datetime

from yuancloud import api, models

try:
    import pysftp
except ImportError:
    raise ImportError(
        'This module needs pysftp to automaticly write backups to the FTP through SFTP. Please install pysftp on your system. (sudo pip install pysftp)')

import logging

_logger = logging.getLogger(__name__)


class SaasServerClient(models.Model):
    _inherit = 'saas_server.client'

    @api.model
    def _transport_backup(self, dump_db, filename=None):
        server = self.env['ir.config_parameter'].get_param('saas_server.sftp_server', None)
        username = self.env['ir.config_parameter'].get_param('saas_server.sftp_username', None)
        password = self.env['ir.config_parameter'].get_param('saas_server.sftp_password', None)
        path = self.env['ir.config_parameter'].get_param('saas_server.sftp_path', None)
        daystokeep = self.env['ir.config_parameter'].get_param('saas_server.sftp_daystokeep', 30)
        daystokeep = int(daystokeep)
        srv = pysftp.Connection(host=server, username=username, password=password)
        # set keepalive to prevent socket closed / connection dropped error
        srv._transport.set_keepalive(30)

        for file in srv.listdir(path):
            # Get the full path
            fullpath = os.path.join(path, file)
            # Get the timestamp from the file on the external server
            timestamp = srv.stat(fullpath).st_atime
            createtime = datetime.datetime.fromtimestamp(timestamp)
            now = datetime.datetime.now()
            delta = now - createtime
            # If the file is older than the daystokeepsftp (the days to keep that the user filled in on the YuanCloud form it will be removed.
            if delta.days >= daystokeep:
                # Only delete files, no directories!
                if srv.isfile(fullpath) and (".dump" in file or ".zip" in file):
                    _logger.info("Delete too old file from SFTP servers: " + file)
                    srv.unlink(fullpath)
        try:
            srv.chdir(path)
        except IOError:
            # Create directory and subdirs if they do not exist.
            currentDir = ''
            for dirElement in path.split('/'):
                currentDir += dirElement + '/'
                try:
                    srv.chdir(currentDir)
                except:
                    print('(Part of the) path didn\'t exist. Creating it now at ' + currentDir)
                    # Make directory and then navigate into it
                    srv.mkdir(currentDir, mode=777)
                    srv.chdir(currentDir)
                    pass

        srv.chdir(path)
        with tempfile.TemporaryFile() as t:
            dump_db(t)
            t.seek(0)
            srv.putfo(t, filename)

        srv.close()

    @api.model
    def schedule_saas_databases_backup(self):
        self.search([('state', '!=', 'deleted')]).backup_database()
