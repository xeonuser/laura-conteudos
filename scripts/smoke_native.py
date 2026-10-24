import tempfile
import subprocess
import os
from pathlib import Path
from PySide6.QtCore import QUrl, Qt
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from desktop.app import Library
app=QApplication([])
with tempfile.TemporaryDirectory() as d:
 fixture=Path(d)/'sample.mp4'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','testsrc=size=320x180:rate=24','-t','3','-c:v','mpeg4','-y',str(fixture)],check=True)
 library=Library(Path(d)/'library.json')
 library._finish_scan([Library.local_item(fixture)],'')
 engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('library',library);engine.rootContext().setContextProperty('startFullScreen',False)
 engine.load(QUrl.fromLocalFile(str(Path('desktop/Main.qml').absolute())))
 assert engine.rootObjects(),'QML did not load'
 window=engine.rootObjects()[0];QTest.qWait(500)
 assert len(window.property('displayed').toVariant())==3
 if os.environ.get('AURORA_SCREENSHOT'):
  assert window.grabWindow().save(os.environ['AURORA_SCREENSHOT'])
 QTest.keyClick(window,Qt.Key_Right);QTest.qWait(100)
 assert window.property('selected')==1
 QTest.keyClick(window,Qt.Key_F);QTest.qWait(100)
 assert library.items[1]['favorite']
 QTest.keyClick(window,Qt.Key_Up);QTest.keyClick(window,Qt.Key_Right);QTest.keyClick(window,Qt.Key_Return);QTest.qWait(100)
 assert window.property('page')=='Minha biblioteca'
 assert len(window.property('displayed').toVariant())==1
 QTest.keyClick(window,Qt.Key_Return);QTest.qWait(1000)
 assert window.property('playing')

 QTest.keyClick(window,Qt.Key_Escape);QTest.qWait(100)
 assert not window.property('playing')
 window.close()
 print('Native UI: load, keyboard navigation, favorites, local library and player start/exit passed.')
