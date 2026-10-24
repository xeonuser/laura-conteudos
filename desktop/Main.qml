import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

ApplicationWindow {
    id: app
    visible: true
    width: 1440; height: 900
    minimumWidth: 960; minimumHeight: 600
    visibility: startFullScreen ? Window.FullScreen : Window.Windowed
    title: "Aurora TV"
    color: "#0c1211"
    property string page: "Descobrir"
    property int selected: 0
    property int navigation: 0
    property bool onMenu: false
    property bool settings: false
    property bool confirmReset: false
    property bool playing: false
    property var current: ({})
    property var displayed: []
    property string notice: ""
    property string query: ""
    property bool searching: false
    property bool pendingSeek: false
    property var destinations: ["Descobrir", "Minha biblioteca", "Continuar", "Favoritos"]
    property real unit: Math.min(width / 1440, height / 900)

    function refresh() {
        let items = library.items;
        displayed = items.filter(function(i) {
            let match = page === "Descobrir" || page === "Minha biblioteca" && i.kind === "Minha biblioteca" || page === "Continuar" && i.position > 0 || page === "Favoritos" && i.favorite;
            return match && (!query || i.title.toLowerCase().indexOf(query.toLowerCase()) >= 0);
        });
        selected = Math.max(0, Math.min(selected, displayed.length - 1));
    }
    function choose(index) { navigation = index; page = destinations[index]; selected = 0; onMenu = false; query = ""; refresh(); }
    function start(item) {
        current = item; pendingSeek = true; playing = true;
        media.source = item.url; media.play();
        controlsVisible.restart(); screen.forceActiveFocus();
    }
    function stop() {
        if (!playing) return;
        library.progress(current.id, media.position, media.duration);
        media.stop(); playing = false; refresh(); screen.forceActiveFocus();
    }
    function togglePlayback() { if (media.playbackState === MediaPlayer.PlayingState) media.pause(); else media.play(); controlsVisible.restart(); }
    Component.onCompleted: { refresh(); screen.forceActiveFocus(); }
    Connections {
        target: library
        function onChanged() { app.refresh(); }
        function onMessage(text) { notice = text; toastTimer.restart(); }
    }
    Timer { id: toastTimer; interval: 5000; onTriggered: notice = "" }
    Timer { id: controlsVisible; interval: 4500 }
    Timer { interval: 5000; running: playing; repeat: true; onTriggered: library.progress(current.id, media.position, media.duration) }
    onClosing: { if (playing) library.progress(current.id, media.position, media.duration); }

    component Action: Rectangle {
        id: action
        property string text: ""
        property bool primary: false
        property bool highlighted: false
        signal activated()
        implicitWidth: caption.implicitWidth + 48
        implicitHeight: 54
        radius: 10
        color: primary ? "#d4eda9" : highlighted || pointer.containsMouse ? "#34463c" : "#12ffffff"
        border.width: highlighted ? 2 : 1
        border.color: highlighted ? "#e7ffc0" : "#20ffffff"
        Text { id: caption; anchors.centerIn: parent; text: action.text; color: action.primary ? "#172317" : "#f0f5eb"; font.pixelSize: 17; font.weight: Font.DemiBold }
        MouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: action.activated() }
    }

    FocusScope {
        id: screen
        anchors.fill: parent
        focus: true
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_F11) { app.visibility = app.visibility === Window.FullScreen ? Window.Windowed : Window.FullScreen; event.accepted = true; return; }
            if (event.key === Qt.Key_Escape || event.key === Qt.Key_Back) {
                if (playing) stop(); else if (settings) { settings = false; confirmReset = false; } else if (searching) searching = false; else { choose(0); onMenu = false; }
                event.accepted = true; return;
            }
            if (playing) {
                if (event.key === Qt.Key_Space || event.key === Qt.Key_Return || event.key === Qt.Key_Enter) togglePlayback();
                else if (event.key === Qt.Key_Right) media.setPosition(Math.min(media.duration, media.position + 10000));
                else if (event.key === Qt.Key_Left) media.setPosition(Math.max(0, media.position - 10000));
                else if (event.key === Qt.Key_Up) audio.volume = Math.min(1, audio.volume + 0.1);
                else if (event.key === Qt.Key_Down) audio.volume = Math.max(0, audio.volume - 0.1);
                controlsVisible.restart(); event.accepted = true; return;
            }
            if (settings) { if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) settings = false; event.accepted = true; return; }
            if (event.key === Qt.Key_Up) onMenu = true;
            else if (event.key === Qt.Key_Down) onMenu = false;
            else if (event.key === Qt.Key_Right) { if (onMenu) navigation = Math.min(destinations.length-1, navigation+1); else selected = Math.min(displayed.length-1, selected+1); }
            else if (event.key === Qt.Key_Left) { if (onMenu) navigation = Math.max(0,navigation-1); else selected = Math.max(0,selected-1); }
            else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) { if (onMenu) choose(navigation); else if (displayed.length) start(displayed[selected]); }
            else if (event.key === Qt.Key_F && displayed.length) library.toggleFavorite(displayed[selected].id);
            else if (event.key === Qt.Key_O) library.openFolder();
            else if (event.key === Qt.Key_S) { searching = true; searchInput.forceActiveFocus(); }
            event.accepted = true;
        }

        Item {
            id: stage
            width: 1440; height: 900
            scale: app.unit
            anchors.centerIn: parent
            Rectangle {
                x: 570; y: 0; width: 870; height: 590; clip: true
                gradient: Gradient { GradientStop { position: 0; color: "#475e49" } GradientStop { position: 1; color: "#0c1211" } }
                Rectangle { x: 570; y: 100; width: 140; height: 140; radius: 70; color: "#d4ce9b"; opacity: 0.65 }
                Repeater {
                    model: 5
                    Rectangle { required property int index; x: 60 + index*180; y: 240 + index*30; width: 450; height: 600; rotation: 40; radius: 55; color: Qt.rgba(0.06+index*0.012,0.15+index*0.012,0.12+index*0.01,1) }
                }
            }
            Rectangle { x: 0; y: 0; width: 1000; height: 590; rotation: 0; gradient: Gradient { orientation: Gradient.Horizontal; GradientStop { position: 0.45; color: "#0c1211" } GradientStop { position: 1; color: "transparent" } } }
            Row {
                x: 65; y: 36; spacing: 13
                Text { text: "✳"; color: "#d4eda9"; font.pixelSize: 36 }
                Text { text: "A U R O R A"; color: "#f2f5eb"; font.pixelSize: 25; font.weight: Font.DemiBold; anchors.verticalCenter: parent.verticalCenter }
                Text { text: "TV"; color: "#98a88f"; font.pixelSize: 12; anchors.verticalCenter: parent.verticalCenter }
            }
            Row {
                x: 490; y: 35; spacing: 8
                Repeater {
                    model: app.destinations
                    Action {
                        required property string modelData
                        required property int index
                        text: modelData; highlighted: onMenu && navigation === index
                        color: page === modelData ? "#2b382b" : "transparent"
                        onActivated: { choose(index); screen.forceActiveFocus(); }
                    }
                }
            }
            Action { x: 1275; y: 35; text: "⚙"; onActivated: { settings = true; screen.forceActiveFocus(); } }
            Text { x: 70; y: 165; text: page === "Descobrir" ? "CINEMA ABERTO. DO SEU JEITO." : "SEU ESPAÇO. SUAS HISTÓRIAS."; color: "#d4eda9"; font.pixelSize: 13; font.letterSpacing: 3 }
            Text { x: 65; y: 210; text: page === "Descobrir" ? "Sua próxima\ngrande história." : page; color: "#f5f6ed"; font.pixelSize: 68; font.weight: Font.Medium; lineHeight: 1.05 }
            Text { x: 70; y: 385; width: 580; text: page === "Descobrir" ? "Cinema independente e os vídeos que você ama.\nAcomode-se. O controle é seu." : "Adicione seus vídeos e transforme sua pasta\nem uma experiência de cinema."; color: "#b8c5b6"; font.pixelSize: 20; lineHeight: 1.5 }
            Row { x: 70; y: 470; spacing: 14
                Action { text: "▶  Assistir"; primary: true; onActivated: { if (displayed.length) start(displayed[selected]); else library.openFolder(); } }
                Action { text: "+  Adicionar pasta"; onActivated: library.openFolder() }
                Action { text: "⌕  Buscar"; onActivated: { searching = true; searchInput.forceActiveFocus(); } }
            }
            Text { x: 70; y: 565; text: query ? "Resultados para: " + query : page === "Descobrir" ? "Escolha seu próximo play" : page; color: "#eef3e9"; font.pixelSize: 25; font.weight: Font.Medium }
            Text { x: 1070; y: 575; text: "EDIÇÃO COMPUTADOR  /  0.2"; color: "#899a85"; font.pixelSize: 11; font.letterSpacing: 2 }
            ListView {
                id: shelf
                x: 60; y: 612; width: 1320; height: 235
                orientation: ListView.Horizontal; spacing: 22; clip: true
                model: displayed
                currentIndex: selected
                highlightMoveDuration: 180
                preferredHighlightBegin: 0; preferredHighlightEnd: width - 320
                highlightRangeMode: ListView.ApplyRange
                delegate: Item {
                    required property var modelData
                    required property int index
                    width: 306; height: 225
                    Rectangle {
                        x: 7; y: 7; width: 292; height: 164; radius: 12
                        color: modelData.color
                        clip: true
                        border.color: index === selected && !onMenu ? "#d4eda9" : "#16ffffff"
                        border.width: index === selected && !onMenu ? 3 : 1
                        scale: index === selected && !onMenu ? 1.02 : 1
                        Behavior on scale { NumberAnimation { duration: 130 } }
                        Text { x: 174; y: -16; text: "✳"; color: "#18ffffff"; font.pixelSize: 155 }
                        Text { x: 22; y: 40; width: 220; text: modelData.title; color: "#f5f6eb"; font.pixelSize: 30; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; maximumLineCount: 2; elide: Text.ElideRight }
                        Text { x: 22; y: 135; text: modelData.kind.toUpperCase(); color: "#cad6c2"; font.pixelSize: 10; font.letterSpacing: 1 }
                        Text { anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; text: modelData.favorite ? "♥" : ""; color: "#d4eda9"; font.pixelSize: 23 }
                        Rectangle { anchors.left: parent.left; anchors.bottom: parent.bottom; height: 4; radius: 2; width: modelData.duration > 0 ? parent.width * modelData.position / modelData.duration : 0; color: "#d4eda9" }
                        MouseArea { anchors.fill: parent; onClicked: { selected = index; onMenu = false; screen.forceActiveFocus(); } onDoubleClicked: start(modelData) }
                    }
                    Text { x: 9; y: 188; width: 292; text: modelData.subtitle; color: "#a9b7a4"; font.pixelSize: 13; elide: Text.ElideRight }
                }
            }
            Text { x: 75; y: 660; visible: displayed.length === 0; text: page === "Minha biblioteca" ? "Sua biblioteca começa com uma pasta.\nEscolha Adicionar pasta para encontrar seus vídeos." : "Ainda não há títulos aqui.\nAdicione vídeos ou marque favoritos com a tecla F."; color: "#b6c4ad"; font.pixelSize: 22; lineHeight: 1.6 }
            Row { x: 70; y: 849; spacing: 16
                Text { text: "← →  Escolher     ↑  Menu     Enter  Assistir     F  Favoritar     Esc  Voltar"; color: "#83957e"; font.pixelSize: 13 }
                Text { text: "F11  Janela / tela cheia"; color: "#83957e"; font.pixelSize: 13 }
            }
            Text { x: 70; y: 812; width: 1250; text: displayed.length ? displayed[selected].description : ""; color: "#a8b7a1"; font.pixelSize: 14; elide: Text.ElideRight }
        }
    }

    Rectangle {
        anchors.fill: parent; color: "#000000"; visible: playing
        VideoOutput { id: output; anchors.fill: parent }
        MouseArea { anchors.fill: parent; hoverEnabled: true; onPositionChanged: controlsVisible.restart(); onClicked: { controlsVisible.restart(); screen.forceActiveFocus(); } onDoubleClicked: togglePlayback() }
        Rectangle {
            anchors.bottom: parent.bottom; width: parent.width; height: 185; color: "#e6151d18"; visible: controlsVisible.running || media.playbackState !== MediaPlayer.PlayingState
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 24; spacing: 8
                Text { text: current.title || ""; color: "#edf3e7"; font.pixelSize: 25 }
                Slider { Layout.fillWidth: true; from: 0; to: Math.max(1,media.duration); value: media.position; onMoved: media.setPosition(value) }
                RowLayout {
                    spacing: 15
                    Action { text: "← Voltar"; onActivated: stop() }
                    Action { text: media.playbackState === MediaPlayer.PlayingState ? "Ⅱ Pausar" : "▶ Reproduzir"; primary: true; onActivated: togglePlayback() }
                    Action { text: "−10s"; onActivated: media.setPosition(Math.max(0,media.position-10000)) }
                    Action { text: "+10s"; onActivated: media.setPosition(Math.min(media.duration,media.position+10000)) }
                    Text { text: Math.floor(media.position/60000) + ":" + String(Math.floor(media.position/1000)%60).padStart(2,"0") + " / " + Math.floor(media.duration/60000) + ":" + String(Math.floor(media.duration/1000)%60).padStart(2,"0"); color: "#c2d0ba" }
                    ComboBox { model: media.audioTracks.map(t => t.stringValue(MediaMetaData.Language) || "Áudio"); visible: media.audioTracks.length > 1; onActivated: media.activeAudioTrack = currentIndex }
                    ComboBox { model: ["Sem legenda"].concat(media.subtitleTracks.map((t,i) => t.stringValue(MediaMetaData.Language) || "Legenda " + (i+1))); visible: media.subtitleTracks.length > 0; onActivated: media.activeSubtitleTrack = currentIndex-1 }
                }
                Text { text: current.license || ""; color: "#94a58e"; font.pixelSize: 11 }
            }
        }
        Text { anchors.centerIn: parent; width: parent.width*0.7; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; text: media.error !== MediaPlayer.NoError ? "Não foi possível reproduzir este vídeo.\nVerifique a conexão ou o formato do arquivo.\nEsc para voltar.\n" + media.errorString : media.mediaStatus === MediaPlayer.LoadingMedia ? "Preparando seu cinema…" : ""; color: "#eef5e5"; font.pixelSize: 23 }
    }
    MediaPlayer {
        id: media
        audioOutput: AudioOutput { id: audio; volume: 0.8 }
        videoOutput: output
        onMediaStatusChanged: {
            if (mediaStatus === MediaPlayer.LoadedMedia && pendingSeek) { pendingSeek = false; if (current.position > 0) setPosition(current.position); }
            if (mediaStatus === MediaPlayer.EndOfMedia) { library.progress(current.id, duration, duration); playing = false; }
        }
    }
    Rectangle {
        anchors.fill: parent; color: "#ed0c1211"; visible: settings
        Column {
            anchors.centerIn: parent; width: Math.min(850,parent.width-100); spacing: 22
            Text { text: "Sua Aurora"; color: "#f0f5e7"; font.pixelSize: 44 }
            Text { width: parent.width; wrapMode: Text.WordWrap; text: "Aplicativo nativo · Qt / QML · Edição computador\n\nBiblioteca: vídeos no seu computador, sem upload.\nF11 alterna tela cheia. Esc volta. Feche pela janela ou use Sair.\n\nRede, Wi-Fi, HDMI e energia são gerenciados pelo Windows. Esta versão não altera o sistema da TV Box.\n\nConteúdo: dois filmes abertos de demonstração (Sintel é trailer). Serviços comerciais, canais ao vivo e o controle pelo celular ainda não estão integrados nesta interface nativa."; color: "#bccbb2"; font.pixelSize: 19; lineHeight: 1.4 }
            Row { spacing: 15
                Action { text: "Abrir arquivo"; onActivated: library.openFile() }
                Action { text: confirmReset ? "Confirmar restauração" : "Restaurar biblioteca"; onActivated: { if (confirmReset) { library.reset(); confirmReset = false; } else confirmReset = true; } }
            }
            Row { spacing: 15
                Action { text: "← Voltar"; primary: true; onActivated: { settings = false; confirmReset = false; screen.forceActiveFocus(); } }
                Action { text: "Sair do aplicativo"; onActivated: app.close() }
            }
        }
    }
    Rectangle {
        anchors.fill: parent; color: "#ee0c1211"; visible: searching
        Column {
            anchors.centerIn: parent; width: Math.min(750, parent.width-80); spacing: 25
            Text { text: "Qual é a próxima história?"; color: "#eaf2e1"; font.pixelSize: 32 }
            TextField { id: searchInput; width: parent.width; placeholderText: "Digite um título da sua biblioteca"; font.pixelSize: 24; onAccepted: { query = text; searching = false; refresh(); screen.forceActiveFocus(); } Keys.onEscapePressed: { searching = false; screen.forceActiveFocus(); } }
            Action { text: "Buscar"; primary: true; onActivated: { query = searchInput.text; searching = false; refresh(); screen.forceActiveFocus(); } }
        }
    }
    Rectangle { anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom; anchors.bottomMargin: 35; width: Math.min(parent.width-50, toast.implicitWidth+50); height: 65; radius: 12; color: "#d4eda9"; visible: notice !== ""; Text { id: toast; anchors.centerIn: parent; width: parent.width-25; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; text: notice; color: "#192716"; font.pixelSize: 16 } }
}
