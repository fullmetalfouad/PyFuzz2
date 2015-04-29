__author__ = 'susperius'

import pykd
import logging


class ExceptionHandler(pykd.eventHandler):
    def __init__(self):
        pykd.eventHandler.__init__(self)
        self.count = 0
        self.exception_occurred = False
        self.interesting_exceptions = {0x80000001: "GUARD_PAGE_VIOLATION",
                                       0x80000005: "BUFFER_OVERFLOW",
                                       0xC0000005: "ACCESS_VIOLATION",
                                       0xC000001D: "ILLEGAL_INSTRUCTION",
                                       0xC0000144: "UNHANDLED_EXCEPTION",
                                       0xC0000409: "STACK_BUFFER_OVERRUN",
                                       0xC0000602: "UNKNOWN_EXCEPTION",
                                       0xC00000FD: "STACK_OVERFLOW",
                                       0XC000009D: "PRIVILEGED_INSTRUCTION"}
        self.exception_info = None

    def exceptionOccurred(self):
        return self.exception_occurred

    def getExceptionInfo(self):
        return self.exception_info

    def onException(self, exceptInfo):
        if (exceptInfo.ExceptionCode in self.interesting_exceptions.keys()) and not exceptInfo.FirstChance:
            self.exception_info = (exceptInfo.ExceptionCode, self.interesting_exceptions[exceptInfo.ExceptionCode],
                                   exceptInfo)
            self.exception_occurred = True
            return pykd.eventResult.Break
        return pykd.eventResult.NoChange


class Debugger:
    def __init__(self, program_path, debug_child=False):
        self._program_path = program_path
        self._debug_child = debug_child
        self._process_id = None
        self._event_handler = ExceptionHandler()
        self._crash_occurred = False
        self._logger = logging.getLogger(__name__)

    def start_process(self, arguments):
        self._process_id = pykd.startProcess(self._program_path + " " + arguments, debugChildren=self._debug_child)
        self._logger.debug("Process created")

    def run(self):
        while not self._event_handler.exceptionOccurred():
            pykd.go()
        self._logger.debug("Crash occurred")
        self._crash_occurred = True

    def get_except_info(self):
        return self._event_handler.exception_info

    def involve_msec(self):
        pykd.dbgCommand(u"!load debugging\\msec\\MSEC.dll")
        return pykd.dbgCommand(u"!exploitable -v")

    def issue_dbg_command(self, cmd):
        return pykd.dbgCommand(unicode(cmd))

    def kill_process(self):
        pykd.killAllProcesses()