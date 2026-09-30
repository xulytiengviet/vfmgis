# encoding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
from addons.VFMGIS.actions import selfRegister


def main(*args):
    selfRegister()
    from java.lang import System, Throwable
    if System.getenv('VFMGIS_AUTOSTART') != '1':
        return
    from javax.swing import Timer
    import gvsig
    state = {'attempts': 0}

    def ready(event):
        state['attempts'] += 1
        try:
            project = gvsig.currentProject()
            if project is None:
                if state['attempts'] < 90:
                    return
                raise RuntimeError('gvSIG chưa tạo được dự án khởi động.')
            event.getSource().stop()
            report = System.getenv('VFMGIS_TEST_REPORT')
            if report:
                from addons.VFMGIS.native_check import run
                run(report)
            else:
                from addons.VFMGIS.native import start
                start()
        except (Exception, Throwable):
            import traceback
            from javax.swing import JOptionPane
            if state['attempts'] < 90 and event.getSource().isRunning():
                return
            event.getSource().stop()
            report = System.getenv('VFMGIS_TEST_REPORT')
            if report:
                import io
                with io.open(report, 'w', encoding='utf-8') as output:
                    output.write(traceback.format_exc().decode('utf-8', 'replace'))
                System.exit(1)
            else:
                JOptionPane.showMessageDialog(None, u'Không mở được VFMGIS:\n' + traceback.format_exc().decode('utf-8', 'replace'),
                                              'VFMGIS', JOptionPane.ERROR_MESSAGE)

    timer = Timer(1500, ready)
    timer.start()
