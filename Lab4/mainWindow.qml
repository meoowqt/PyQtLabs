import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    id: root
    visible: true
    width: 1000
    height: 1000
    title: "Paint!"

    // Свойства
    property string lastSavedImage: ""
    property bool autoSaveEnabled: _backend.saveTimerRunning

    Rectangle {
        id: tools
        width: parent.width
        height: 200
        color: "#545454"

        property color paintColor: "#33B5E5"
        property int thickness: 1
        property int spacing: 4

        Column {
            spacing: tools.spacing
            anchors.centerIn: parent

            // Цвета
            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444"]
                    Square {
                        active: tools.paintColor === color
                        color: modelData
                        onClicked: tools.paintColor = color
                    }
                }
            }

            // Толщина линии
            Row {
                spacing: tools.spacing
                anchors.horizontalCenter: parent.horizontalCenter

                Repeater {
                    model: [1,2,3,4,5]

                    Circle {
                        id: circle
                        active: tools.thickness === thickness
                        thickness: modelData
                        text: thickness
                        onClicked: tools.thickness = thickness
                    }
                }
            }

            // Панель управления сохранением
            Rectangle {
                width: parent.width
                height: 50
                color: "transparent"

                Column {
                    spacing: 5
                    anchors.centerIn: parent

                    // Первая строка: кнопки
                    Row {
                        spacing: 10
                        anchors.horizontalCenter: parent.horizontalCenter

                        // Кнопка ручного сохранения
                        Rectangle {
                            width: 100
                            height: 30
                            color: "#4CAF50"
                            radius: 5

                            Text {
                                anchors.centerIn: parent
                                text: "Сохранить"
                                color: "white"
                                font.bold: true
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    console.log("Ручное сохранение...")
                                    saveCanvas()
                                }
                            }
                        }

                        // Кнопка автосохранения
                        Rectangle {
                            id: autoSaveToggle
                            width: 150
                            height: 30
                            color: autoSaveEnabled ? "#F44336" : "#4CAF50"
                            radius: 5

                            Text {
                                anchors.centerIn: parent
                                text: autoSaveEnabled ? "Стоп автосохран." : "Старт автосохран."
                                color: "white"
                                font.bold: true
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    _backend.toggleAutoSave()
                                }
                            }
                        }
                    }

                    // Вторая строка: информация
                    Row {
                        spacing: 10
                        anchors.horizontalCenter: parent.horizontalCenter

                        // Отображение информации
                        Text {
                            id: saveInfo
                            text: lastSavedImage ? "Последнее сохранение: " + lastSavedImage : "Еще не сохранено"
                            color: "white"
                            font.pixelSize: 12
                        }
                    }
                }
            }
        }
    }

    Canvas {
        id: canvas
        anchors {
            left: parent.left
            right: parent.right
            top: tools.bottom
            bottom: parent.bottom
            margins: 8
        }

        property real lastX
        property real lastY
        property color color: tools.paintColor

        onPaint: {
            var ctx = getContext("2d")
            ctx.lineWidth = tools.thickness
            ctx.strokeStyle = canvas.color
            ctx.beginPath()
            ctx.moveTo(lastX, lastY)

            lastX = paint_area.mouseX
            lastY = paint_area.mouseY

            ctx.lineTo(lastX, lastY)
            ctx.stroke()
        }

        // Функция для сохранения canvas
        function saveToFile() {
            var timestamp = new Date().getTime()
            var filename = "canvas_" + timestamp + ".png"
            
            // Получаем полный путь от Python бэкенда
            var fullPath = _backend.getSavePath(filename)
            
            console.log("Пытаюсь сохранить в:", fullPath)
            
            // Сохраняем в папку saved_canvases
            var saved = canvas.save(fullPath)
            
            if (saved) {
                root.lastSavedImage = filename
                console.log("Успешно сохранено:", filename)
                return true
            } else {
                console.log("Ошибка: Не удалось сохранить файл")
                return false
            }
        }

        MouseArea {
            id: paint_area
            anchors.fill: parent

            onPressed: {
                canvas.lastX = mouseX
                canvas.lastY = mouseY
            }

            onPositionChanged: {
                canvas.requestPaint()
            }
        }
    }

    // Функция сохранения canvas
    function saveCanvas() {
        console.log("Сохранение canvas...")
        if (canvas.saveToFile()) {
            console.log("Успешно сохранено!")
        } else {
            console.log("Сохранение не удалось!")
        }
    }

    // Обработчик автосохранения из Python
    Connections {
        target: _backend
        function onSaveRequested() {
            console.log("Автосохранение из Python...")
            saveCanvas()
        }
    }

    // Обновляем свойство при изменении состояния таймера
    Connections {
        target: _backend
        function onSaveTimerRunningChanged() {
            autoSaveEnabled = _backend.saveTimerRunning
            console.log("Состояние автосохранения изменено: " + (autoSaveEnabled ? "включено" : "выключено"))
        }
    }

    // Обновляем поле ввода интервала
    Connections {
        target: _backend
        function onSaveIntervalChanged() {
            console.log("Интервал автосохранения изменен: " + (_backend.saveInterval / 1000) + " секунд")
        }
    }

    Component.onCompleted: {
        console.log("Приложение Paint запущено")
        console.log("Автосохранение управляется Python бэкендом")
        console.log("Начальный интервал автосохранения: " + (_backend.saveInterval / 1000) + " секунд")
    }
}