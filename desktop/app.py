"""Native Qt/QML frontend. No browser or HTTP server is needed."""
import argparse
import json
import os
from pathlib import Path
import sys
import threading

from PySide6.QtCore import QObject, Property, QStandardPaths, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QFileDialog

DEMO = [
    dict(id='bunny', title='Big Buck Bunny', subtitle='2008 · Animação · Curta completo',
         description='Um gigante gentil, três pequenos encrenqueiros e uma tarde que promete sair do controle.',
         url='https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_640x360.m4v',
         color='#365d46', kind='Cinema aberto', license='Blender Foundation · CC BY 3.0 · peach.blender.org'),
    dict(id='sintel', title='Sintel', subtitle='2010 · Fantasia · Trailer',
         description='Uma viajante e um pequeno dragão. Conheça o universo de Sintel neste trailer do filme aberto.',
         url='https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4',
         color='#704d42', kind='Cinema aberto', license='Blender Foundation · CC BY 3.0 · durian.blender.org'),
]
EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.avi', '.m4v'}


class Library(QObject):
    changed = Signal()
    scanFinished = Signal(list, str)
    message = Signal(str)

    def __init__(self, state_path=None):
        super().__init__()
        self.path = Path(state_path) if state_path else Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / 'library.json'
        self.state = {'favorites': [], 'progress': {}, 'local': []}
        try:
            loaded = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(loaded, dict):
                for key, typ in [('favorites', list), ('progress', dict), ('local', list)]:
                    if isinstance(loaded.get(key), typ):
                        self.state[key] = loaded[key]
        except (OSError, ValueError):
            pass
        self.scanFinished.connect(self._finish_scan)

    @Property('QVariantList', notify=changed)
    def items(self):
        items = [dict(x) for x in DEMO] + [dict(x) for x in self.state['local'] if isinstance(x, dict) and all(k in x for k in ('id', 'title', 'url', 'color'))]
        for item in items:
            item['favorite'] = item['id'] in self.state['favorites']
            progress = self.state['progress'].get(item['id'], {})
            item['position'] = progress.get('position', 0) if isinstance(progress, dict) else 0
            item['duration'] = progress.get('duration', 0) if isinstance(progress, dict) else 0
        return items

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.state, ensure_ascii=False), encoding='utf-8')
            temporary.replace(self.path)
        except OSError:
            self.message.emit('Não foi possível salvar a biblioteca neste computador.')

    @Slot(str)
    def toggleFavorite(self, identity):
        favorites = self.state['favorites']
        favorites.remove(identity) if identity in favorites else favorites.append(identity)
        self.save()
        self.changed.emit()

    @Slot(str, float, float)
    def progress(self, identity, position, duration):
        if duration <= 0:
            return
        self.state['progress'][identity] = {'position': position if position < duration - 3000 else 0, 'duration': duration}
        self.save()
        self.changed.emit()

    @Slot()
    def openFolder(self):
        folder = QFileDialog.getExistingDirectory(None, 'Escolha sua pasta de filmes e vídeos')
        if folder:
            self.scan(folder)

    @Slot()
    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(None, 'Escolha um vídeo', '', 'Vídeos (*.mp4 *.mkv *.webm *.mov *.avi *.m4v)')
        if filename:
            self._finish_scan([self.local_item(Path(filename))], '')

    @staticmethod
    def local_item(path):
        url = QUrl.fromLocalFile(str(path.absolute())).toString()
        return dict(id=url, title=path.stem.replace('_', ' ').replace('.', ' '), subtitle='Arquivo do seu computador', description='Vídeo local. Nenhum arquivo é enviado à internet.', url=url, color='#354c68', kind='Minha biblioteca', license='Arquivo local · direitos pertencem ao titular')

    def scan(self, folder):
        self.message.emit('Procurando vídeos na pasta…')
        def worker():
            items, visited = [], 0
            try:
                for directory, dirs, files in os.walk(folder, followlinks=False):
                    visited += 1
                    dirs[:] = sorted(d for d in dirs if not d.startswith('.'))
                    for name in sorted(files):
                        path = Path(directory) / name
                        if path.suffix.lower() in EXTENSIONS and not path.is_symlink():
                            items.append(self.local_item(path))
                        if len(items) >= 2000:
                            break
                    if len(items) >= 2000 or visited >= 10000:
                        break
                self.scanFinished.emit(items, 'Busca limitada a 2.000 vídeos e 10.000 pastas.' if len(items) >= 2000 or visited >= 10000 else '')
            except OSError:
                self.scanFinished.emit(items, 'Algumas pastas não puderam ser lidas.')
        threading.Thread(target=worker, daemon=True).start()

    @Slot(list, str)
    def _finish_scan(self, items, warning):
        old = {x['id']: x for x in self.state['local'] if isinstance(x, dict) and 'id' in x}
        old.update({x['id']: x for x in items})
        self.state['local'] = list(old.values())
        self.save()
        self.changed.emit()
        self.message.emit(f'{len(items)} vídeo(s) encontrado(s). ' + warning)

    @Slot()
    def reset(self):
        self.state = {'favorites': [], 'progress': {}, 'local': []}
        self.save()
        self.changed.emit()
        self.message.emit('Biblioteca, favoritos e histórico locais restaurados. Seus vídeos não foram apagados.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--windowed', action='store_true')
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setOrganizationName('AuroraTV')
    app.setApplicationName('AuroraTV')
    engine = QQmlApplicationEngine()
    library = Library()
    engine.rootContext().setContextProperty('library', library)
    engine.rootContext().setContextProperty('startFullScreen', not args.windowed)
    engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name('Main.qml'))))
    if not engine.rootObjects():
        return 1
    if args.smoke:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, app.quit)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
