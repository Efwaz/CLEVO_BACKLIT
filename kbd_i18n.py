"""UI, CLI and launcher texts. English is the default and the fallback for any missing key."""
import os

LANG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "kbd-lang.txt")

LANGS = [("es", "Español"), ("en", "English"), ("pt", "Português"), ("fr", "Français"),
         ("de", "Deutsch"), ("it", "Italiano"), ("zh", "简体中文"), ("ja", "日本語"),
         ("ru", "Русский"), ("ko", "한국어")]

# order of every value tuple below
_KEYS = ["title", "brightness", "custom", "custom_tip", "screen_once", "screen_once_tip",
         "screen_live", "screen_live_tip", "battery", "battery_tip", "effects", "effects_off",
         "speed", "save", "cancel", "accept", "rename", "delete", "rename_title",
         "err_tools", "err_capture", "language",
         "color.Blanco", "color.Rojo", "color.Verde", "color.Azul", "color.Morado", "color.Cian", "color.Apagado",
         "fx.respiracion", "fx.respiracion.tip", "fx.arcoiris", "fx.arcoiris.tip", "fx.onda", "fx.onda.tip",
         "fx.pulsacion", "fx.pulsacion.tip", "fx.fuego", "fx.fuego.tip", "fx.latido", "fx.latido.tip",
         "screen_live_warn", "settings", "menu_rate", "menu_rate_tip", "about", "about_comments",
         "about_uses", "about_inspired"]

_TEXTS = {
    "es": ("Luz del teclado", "Brillo", "Personalizado", "Rueda de color y favoritos.",
           "Color de pantalla", "Toma el color dominante de una zona.",
           "Pantalla en vivo", "Sigue en vivo el color de una zona.",
           "Batería", "Color según la carga; pulsa al cargar.",
           "Efectos (color actual)", "Efectos (no disponibles)", "Velocidad",
           "★ Guardar", "Cancelar", "Aceptar", "Renombrar", "Eliminar", "Renombrar favorito",
           "Falta instalar grim y slurp", "Error de captura", "Idioma",
           "Blanco", "Rojo", "Verde", "Azul", "Morado", "Cian", "Apagado",
           "Respiración", "Brillo que sube y baja.", "Arcoíris", "Recorre todos los colores.",
           "Onda", "El color oscila suavemente.", "Pulsación", "Destella al pulsar una tecla.",
           "Fuego", "Parpadeo de llama.", "Latido", "Dos pulsos y una pausa.",
           "Puede afectar el rendimiento, sobre todo con zonas grandes.",
           "Ajustes", "Tasa de actualización", "Capturas por segundo en Pantalla en vivo. Más alta = más sincronía y más CPU.", "Acerca de", "Control de la luz del teclado: colores, efectos, batería y pantalla.", "Hecho con", "Inspirado en"),
    "en": ("Keyboard light", "Brightness", "Custom", "Color wheel and favorites.",
           "Screen color", "Grab the dominant color of an area.",
           "Live screen", "Follow an area's color live.",
           "Battery", "Color by charge; pulses while charging.",
           "Effects (current color)", "Effects (unavailable)", "Speed",
           "★ Save", "Cancel", "OK", "Rename", "Delete", "Rename favorite",
           "grim and slurp are required", "Capture failed", "Language",
           "White", "Red", "Green", "Blue", "Purple", "Cyan", "Off",
           "Breathing", "Brightness rises and falls.", "Rainbow", "Cycles through all colors.",
           "Wave", "Color sways gently.", "Reactive", "Flashes on key press.",
           "Fire", "Flickering flame.", "Heartbeat", "Two pulses, then a pause.",
           "May affect performance, especially with large areas.",
           "Settings", "Refresh rate", "Screen captures per second in Live screen. Higher = tighter sync, more CPU.", "About", "Keyboard backlight control: colors, effects, battery and screen modes.", "Built with", "Inspired by"),
    "pt": ("Luz do teclado", "Brilho", "Personalizado", "Roda de cores e favoritos.",
           "Cor da tela", "Pega a cor dominante de uma área.",
           "Tela ao vivo", "Acompanha a cor de uma área.",
           "Bateria", "Cor conforme a carga; pulsa ao carregar.",
           "Efeitos (cor atual)", "Efeitos (indisponíveis)", "Velocidade",
           "★ Salvar", "Cancelar", "OK", "Renomear", "Excluir", "Renomear favorito",
           "É preciso instalar grim e slurp", "Falha na captura", "Idioma",
           "Branco", "Vermelho", "Verde", "Azul", "Roxo", "Ciano", "Desligado",
           "Respiração", "O brilho sobe e desce.", "Arco-íris", "Percorre todas as cores.",
           "Onda", "A cor oscila suavemente.", "Pulsação", "Pisca ao pressionar uma tecla.",
           "Fogo", "Chama tremulante.", "Batimento", "Dois pulsos e uma pausa.",
           "Pode afetar o desempenho, principalmente com áreas grandes.",
           "Configurações", "Taxa de atualização", "Capturas por segundo em Tela ao vivo. Maior = mais sincronia e mais CPU.", "Sobre", "Controle da luz do teclado: cores, efeitos, bateria e tela.", "Feito com", "Inspirado em"),
    "fr": ("Éclairage clavier", "Luminosité", "Personnalisé", "Roue de couleurs et favoris.",
           "Couleur d'écran", "Prend la couleur dominante d'une zone.",
           "Écran en direct", "Suit la couleur d'une zone.",
           "Batterie", "Couleur selon la charge ; pulse en charge.",
           "Effets (couleur actuelle)", "Effets (indisponibles)", "Vitesse",
           "★ Enregistrer", "Annuler", "OK", "Renommer", "Supprimer", "Renommer le favori",
           "grim et slurp sont requis", "Échec de la capture", "Langue",
           "Blanc", "Rouge", "Vert", "Bleu", "Violet", "Cyan", "Éteint",
           "Respiration", "La luminosité monte et descend.", "Arc-en-ciel", "Parcourt toutes les couleurs.",
           "Vague", "La couleur ondule doucement.", "Réactif", "S'illumine à chaque frappe.",
           "Feu", "Flamme vacillante.", "Battement", "Deux pulsations, puis une pause.",
           "Peut affecter les performances, surtout avec de grandes zones.",
           "Paramètres", "Fréquence d'actualisation", "Captures par seconde en Écran en direct. Plus élevé = plus synchrone, plus de CPU.", "À propos", "Contrôle du rétroéclairage : couleurs, effets, batterie et écran.", "Réalisé avec", "Inspiré de"),
    "de": ("Tastaturbeleuchtung", "Helligkeit", "Eigene Farbe", "Farbrad und Favoriten.",
           "Bildschirmfarbe", "Übernimmt die Hauptfarbe eines Bereichs.",
           "Bildschirm live", "Folgt der Farbe eines Bereichs.",
           "Akku", "Farbe nach Ladestand; pulsiert beim Laden.",
           "Effekte (aktuelle Farbe)", "Effekte (nicht verfügbar)", "Geschwindigkeit",
           "★ Speichern", "Abbrechen", "OK", "Umbenennen", "Löschen", "Favorit umbenennen",
           "grim und slurp fehlen", "Aufnahme fehlgeschlagen", "Sprache",
           "Weiß", "Rot", "Grün", "Blau", "Violett", "Cyan", "Aus",
           "Atmen", "Helligkeit steigt und fällt.", "Regenbogen", "Durchläuft alle Farben.",
           "Welle", "Die Farbe schwankt sanft.", "Reaktiv", "Blitzt beim Tastendruck auf.",
           "Feuer", "Flackernde Flamme.", "Herzschlag", "Zwei Pulse, dann Pause.",
           "Kann die Leistung beeinträchtigen, besonders bei großen Bereichen.",
           "Einstellungen", "Aktualisierungsrate", "Aufnahmen pro Sekunde bei Bildschirm live. Höher = synchroner, mehr CPU.", "Info", "Tastaturbeleuchtung steuern: Farben, Effekte, Akku und Bildschirm.", "Erstellt mit", "Inspiriert von"),
    "it": ("Luce tastiera", "Luminosità", "Personalizzato", "Ruota colori e preferiti.",
           "Colore schermo", "Prende il colore dominante di un'area.",
           "Schermo live", "Segue il colore di un'area.",
           "Batteria", "Colore in base alla carica; pulsa in ricarica.",
           "Effetti (colore attuale)", "Effetti (non disponibili)", "Velocità",
           "★ Salva", "Annulla", "OK", "Rinomina", "Elimina", "Rinomina preferito",
           "Servono grim e slurp", "Cattura non riuscita", "Lingua",
           "Bianco", "Rosso", "Verde", "Blu", "Viola", "Ciano", "Spento",
           "Respiro", "La luminosità sale e scende.", "Arcobaleno", "Percorre tutti i colori.",
           "Onda", "Il colore oscilla dolcemente.", "Reattivo", "Lampeggia alla pressione di un tasto.",
           "Fuoco", "Fiamma tremolante.", "Battito", "Due impulsi e una pausa.",
           "Può influire sulle prestazioni, soprattutto con aree grandi.",
           "Impostazioni", "Frequenza di aggiornamento", "Catture al secondo in Schermo live. Più alta = più sincronia, più CPU.", "Informazioni", "Controllo della retroilluminazione: colori, effetti, batteria e schermo.", "Realizzato con", "Ispirato a"),
    "zh": ("键盘背光", "亮度", "自定义", "色轮与收藏。",
           "屏幕取色", "取某个区域的主色。",
           "屏幕实时", "实时跟随某区域的颜色。",
           "电池", "颜色随电量变化，充电时呼吸。",
           "效果（当前颜色）", "效果（不可用）", "速度",
           "★ 保存", "取消", "确定", "重命名", "删除", "重命名收藏",
           "需要安装 grim 和 slurp", "截图失败", "语言",
           "白", "红", "绿", "蓝", "紫", "青", "关闭",
           "呼吸", "亮度缓慢起伏。", "彩虹", "循环所有颜色。",
           "波浪", "颜色轻轻摆动。", "按键反应", "按键时闪亮。",
           "火焰", "火焰般闪烁。", "心跳", "两次搏动后停顿。",
           "可能影响性能，区域越大越明显。",
           "设置", "刷新率", "“屏幕实时”每秒截取次数。越高越同步，占用 CPU 越多。", "关于", "键盘背光控制：颜色、效果、电池与屏幕模式。", "构建于", "灵感来自"),
    "ja": ("キーボード照明", "明るさ", "カスタム", "カラーホイールとお気に入り。",
           "画面の色", "選択範囲の主要な色を取得。",
           "画面連動", "選択範囲の色にリアルタイムで追従。",
           "バッテリー", "残量で色が変化。充電中は脈動。",
           "エフェクト（現在の色）", "エフェクト（利用不可）", "速度",
           "★ 保存", "キャンセル", "OK", "名前を変更", "削除", "お気に入りの名前を変更",
           "grim と slurp が必要です", "キャプチャに失敗", "言語",
           "白", "赤", "緑", "青", "紫", "シアン", "オフ",
           "呼吸", "明るさがゆっくり増減。", "虹", "全ての色を巡る。",
           "波", "色がゆらぐ。", "打鍵反応", "キーを押すと光る。",
           "炎", "炎のゆらめき。", "鼓動", "2回脈打って一休み。",
           "パフォーマンスに影響する場合があります。特に広い範囲で顕著です。",
           "設定", "更新レート", "「画面連動」の1秒あたりのキャプチャ数。高いほど同期し、CPU負荷も増えます。", "情報", "キーボードバックライト制御：色、エフェクト、バッテリー、画面連動。", "使用技術", "参考にしたもの"),
    "ru": ("Подсветка клавиатуры", "Яркость", "Свой цвет", "Цветовой круг и избранное.",
           "Цвет экрана", "Берёт основной цвет области.",
           "Экран онлайн", "Следует за цветом области.",
           "Батарея", "Цвет по заряду; пульсирует при зарядке.",
           "Эффекты (текущий цвет)", "Эффекты (недоступны)", "Скорость",
           "★ Сохранить", "Отмена", "ОК", "Переименовать", "Удалить", "Переименовать избранное",
           "Нужны grim и slurp", "Ошибка захвата", "Язык",
           "Белый", "Красный", "Зелёный", "Синий", "Фиолетовый", "Голубой", "Выкл",
           "Дыхание", "Яркость плавно меняется.", "Радуга", "Перебирает все цвета.",
           "Волна", "Цвет плавно колеблется.", "Отклик", "Вспыхивает при нажатии клавиши.",
           "Огонь", "Мерцание пламени.", "Сердцебиение", "Два удара и пауза.",
           "Может снижать производительность, особенно на больших областях.",
           "Настройки", "Частота обновления", "Снимков в секунду в режиме «Экран онлайн». Выше — точнее синхронизация, больше нагрузка на CPU.", "О программе", "Управление подсветкой клавиатуры: цвета, эффекты, батарея и экран.", "Создано с помощью", "Вдохновлено"),
    "ko": ("키보드 조명", "밝기", "사용자 지정", "색상환과 즐겨찾기.",
           "화면 색상", "선택 영역의 주된 색을 가져옵니다.",
           "화면 실시간", "선택 영역의 색을 실시간으로 따라갑니다.",
           "배터리", "충전량에 따라 색 변경, 충전 중 맥동.",
           "효과 (현재 색)", "효과 (사용 불가)", "속도",
           "★ 저장", "취소", "확인", "이름 변경", "삭제", "즐겨찾기 이름 변경",
           "grim과 slurp가 필요합니다", "캡처 실패", "언어",
           "흰색", "빨강", "초록", "파랑", "보라", "청록", "끄기",
           "숨쉬기", "밝기가 오르내립니다.", "무지개", "모든 색을 순환합니다.",
           "물결", "색이 부드럽게 흔들립니다.", "키 반응", "키를 누르면 반짝입니다.",
           "불꽃", "불꽃처럼 깜박입니다.", "심장박동", "두 번 뛰고 쉽니다.",
           "성능에 영향을 줄 수 있으며, 넓은 영역일수록 큽니다.",
           "설정", "새로 고침 빈도", "‘화면 실시간’의 초당 캡처 횟수. 높을수록 동기화가 좋고 CPU를 더 씁니다.", "정보", "키보드 백라이트 제어: 색상, 효과, 배터리, 화면 모드.", "사용 기술", "영감을 받은 곳"),
}

# command line + launcher texts, same order per language
_CLI_KEYS = ["err_no_led", "cli_desc", "cli_color", "cli_brightness", "cli_battery", "cli_effect",
             "cli_speed", "cli_off", "cli_need_arg", "cli_bad_color", "cli_bad_effect"]
_CLI = {
    "es": ("LED del teclado no encontrado", "Controla la luz del teclado.",
           "define un color: nombre, #RRGGBB o R,G,B", "define el brillo, 0-100",
           "modo batería (persiste al reiniciar)", "activa un efecto", "velocidad del efecto, 1-10",
           "apaga la luz", "indica --color, --brightness, --battery, --effect o --off",
           "Color no válido: {}", "Efecto no válido: {}"),
    "en": ("Keyboard LED not found", "Control the keyboard backlight.",
           "set a color: name, #RRGGBB or R,G,B", "set brightness, 0-100",
           "battery mode (persists after reboot)", "run an effect", "effect speed, 1-10",
           "turn the backlight off", "specify --color, --brightness, --battery, --effect or --off",
           "Invalid color: {}", "Invalid effect: {}"),
    "pt": ("LED do teclado não encontrado", "Controla a luz do teclado.",
           "define uma cor: nome, #RRGGBB ou R,G,B", "define o brilho, 0-100",
           "modo bateria (persiste após reiniciar)", "ativa um efeito", "velocidade do efeito, 1-10",
           "desliga a luz", "indique --color, --brightness, --battery, --effect ou --off",
           "Cor inválida: {}", "Efeito inválido: {}"),
    "fr": ("LED du clavier introuvable", "Contrôle le rétroéclairage du clavier.",
           "définit une couleur : nom, #RRGGBB ou R,G,B", "règle la luminosité, 0-100",
           "mode batterie (persiste après redémarrage)", "lance un effet", "vitesse de l'effet, 1-10",
           "éteint le rétroéclairage", "indiquez --color, --brightness, --battery, --effect ou --off",
           "Couleur invalide : {}", "Effet invalide : {}"),
    "de": ("Tastatur-LED nicht gefunden", "Steuert die Tastaturbeleuchtung.",
           "setzt eine Farbe: Name, #RRGGBB oder R,G,B", "setzt die Helligkeit, 0-100",
           "Akku-Modus (bleibt nach Neustart)", "startet einen Effekt", "Effektgeschwindigkeit, 1-10",
           "schaltet die Beleuchtung aus", "--color, --brightness, --battery, --effect oder --off angeben",
           "Ungültige Farbe: {}", "Ungültiger Effekt: {}"),
    "it": ("LED della tastiera non trovato", "Controlla la retroilluminazione della tastiera.",
           "imposta un colore: nome, #RRGGBB o R,G,B", "imposta la luminosità, 0-100",
           "modalità batteria (resta dopo il riavvio)", "avvia un effetto", "velocità dell'effetto, 1-10",
           "spegne la retroilluminazione", "indica --color, --brightness, --battery, --effect o --off",
           "Colore non valido: {}", "Effetto non valido: {}"),
    "zh": ("未找到键盘 LED", "控制键盘背光。",
           "设置颜色：名称、#RRGGBB 或 R,G,B", "设置亮度，0-100",
           "电池模式（重启后保留）", "运行效果", "效果速度，1-10",
           "关闭背光", "请指定 --color、--brightness、--battery、--effect 或 --off",
           "无效的颜色：{}", "无效的效果：{}"),
    "ja": ("キーボード LED が見つかりません", "キーボードのバックライトを制御します。",
           "色を設定：名前、#RRGGBB または R,G,B", "明るさを設定、0-100",
           "バッテリーモード（再起動後も維持）", "エフェクトを実行", "エフェクトの速度、1-10",
           "バックライトを消す", "--color、--brightness、--battery、--effect、--off のいずれかを指定してください",
           "無効な色：{}", "無効なエフェクト：{}"),
    "ru": ("LED клавиатуры не найден", "Управление подсветкой клавиатуры.",
           "задать цвет: имя, #RRGGBB или R,G,B", "задать яркость, 0-100",
           "режим батареи (сохраняется после перезагрузки)", "запустить эффект", "скорость эффекта, 1-10",
           "выключить подсветку", "укажите --color, --brightness, --battery, --effect или --off",
           "Неверный цвет: {}", "Неверный эффект: {}"),
    "ko": ("키보드 LED를 찾을 수 없습니다", "키보드 백라이트를 제어합니다.",
           "색상 설정: 이름, #RRGGBB 또는 R,G,B", "밝기 설정, 0-100",
           "배터리 모드 (재부팅 후에도 유지)", "효과 실행", "효과 속도, 1-10",
           "백라이트 끄기", "--color, --brightness, --battery, --effect, --off 중 하나를 지정하세요",
           "잘못된 색상: {}", "잘못된 효과: {}"),
}
assert all(len(v) == len(_KEYS) for v in _TEXTS.values()), "every language needs every UI key"
assert all(len(v) == len(_CLI_KEYS) for v in _CLI.values()), "every language needs every CLI key"
STRINGS = {lang: {**dict(zip(_KEYS, _TEXTS[lang])), **dict(zip(_CLI_KEYS, _CLI[lang]))} for lang in _TEXTS}


def _saved():
    try:
        with open(LANG_FILE) as f:
            code = f.read().strip()
        return code if code in STRINGS else "en"
    except OSError:
        return "en"


current = _saved()


def set_lang(code):
    global current
    current = code
    with open(LANG_FILE, "w") as f:
        f.write(code)


def t(key):
    return STRINGS[current].get(key) or STRINGS["en"][key]


if __name__ == "__main__":  # used by the shell launcher: kbd_i18n.py KEY
    import sys
    print(t(sys.argv[1]))
