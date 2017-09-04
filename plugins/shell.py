import os, subprocess, dotbot

class Shell(dotbot.Plugin):
    '''
    Run arbitrary shell commands.
    '''

    _directive = 'shell'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Shell cannot handle directive %s' %
                directive)
        return self._process_commands(data)

    def _process_commands(self, data):
        success = True
        suppress_shell_cmd = False
        defaults = self._context.defaults().get('shell', {})
        with open(os.devnull, 'w') as devnull:
            for item in data:
                stdin = stdout = stderr = devnull
                suppress_shell_cmd = suppress_shell_cmd = False
                if defaults.get('stdin', False) == True:
                    stdin = None
                if defaults.get('stdout', False) == True:
                    stdout = None
                if defaults.get('stderr', False) == True:
                    stderr = None
                if defaults.get('quiet', False) == True:
                    suppress_shell_cmd = True
                if isinstance(item, dict):
                    cmd = item['command']
                    msg = item.get('description', None)
                    if 'stdin' in item:
                        stdin = None if item['stdin'] == True else devnull
                    if 'stdout' in item:
                        stdout = None if item['stdout'] == True else devnull
                    if 'stderr' in item:
                        stderr = None if item['stderr'] == True else devnull
                    if 'quiet' in item:
                        suppress_shell_cmd = True if item['quiet'] == True else False
                elif isinstance(item, list):
                    cmd = item[0]
                    msg = item[1] if len(item) > 1 else None
                else:
                    cmd = item
                    msg = None
                if msg is None:
                    self._log.lowinfo(cmd)
                else:
                    if suppress_shell_cmd is False:
                        self._log.lowinfo('%s [%s]' % (msg, cmd))
                    else:
                        self._log.lowinfo('%s' % (msg))
                executable = os.environ.get('SHELL')
                ret = subprocess.call(cmd, shell=True, stdin=stdin, stdout=stdout,
                    stderr=stderr, cwd=self._context.base_directory(),
                    executable=executable)
                if ret != 0:
                    success = False
                    self._log.warning('Command [%s] failed' % cmd)
        if success:
            self._log.info('All commands have been executed')
        else:
            self._log.error('Some commands were not successfully executed')
        return success
