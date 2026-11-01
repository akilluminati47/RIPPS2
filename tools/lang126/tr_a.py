"""Build 126 translations, batch A. python tools/lang126/tr_a.py writes tr126/<Language>.json"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = list(json.load(open(os.path.join(HERE, 'labels126.json'), encoding='utf-8')))
T = {}

T['German'] = ([
    '\n%d Spiel-Tastenbelegungen in GAMES', '\n1 Spiel-Tastenbelegung in GAMES', '(kein Name)', 'Beide',
    "Noch keine. Ein Profil ist eine Textdatei, benannt nach der ID des Pads, etwa 2563_0575.pad: das Format steht im Repo von RIPPS2 (docs/plans/pad-spec.md).",
    'An (schnell)', 'Pad-Profile in %s:', 'RIPPS2 %s lite (Build %d) auf RiptOPL %s',
    'RIPPS2 weiß nicht, wo sein Ordner ist, und kann daher nicht nach PADS suchen.', 'konnte nicht gelesen werden',
    'Noch etwa %d Sekunden', 'Noch etwa 1 Sekunde', 'Dauert länger als der letzte Start (bisher %d s)',
    "Die Cover in HD laden (280 x 400)? Schärfer auf einem HD-Bildschirm, je etwa 70 KB. START: Standard (140 x 200, wie bei Open PS2 Loader), je etwa 20 KB. Ein Spiel, das schon ein Cover hat, behält es.",
    'STANDARD', '%d DRIN', '%d DRIN, %d ERSETZT', 'KONNTE NICHT SCHREIBEN', 'Wird vorbereitet: %s', 'KEIN .TAR',
    'NICHTS GEÄNDERT', 'NICHTS HINZUZUFÜGEN',
    'An (schnell) legt den Startton neben RIPPS2 auf die Memory Card, von der es startet, und RIPPS2 wurde nicht von einer gestartet. Der Startton spielt wie bei An.',
    'Es gibt noch keinen Startton zum Kopieren: Audio-Einstellungen > BIOS-Sounds rippt die dieser Konsole.',
    'Dies ist RIPPS2 lite, es enthält kein PS2BBL und kann BIBLE daher nicht einrichten. Die volle RIPPS2.elf installiert und repariert es; ein schon eingerichteter Bootloader startet RIPPS2 lite weiter wie bisher.',
    '%d HINAUSKOPIERT', '%d ELEMENT   %d MARKIERT   %s', '%d ELEMENT   %d MARKIERT   %s   %s FREI',
    '%d ELEMENTE   %d MARKIERT   %s', '%d ELEMENTE   %d MARKIERT   %s   %s FREI', '%s IN %d', '%s IN %d, %s FREI',
    ', %d AUSGELASSEN', 'ZUM ÖFFNEN HINAUSKOPIEREN', 'Wird hinauskopiert: %s', 'MARKIERUNG UMKEHREN',
    'KEINE DATEIEN IN DER ZWISCHENABLAGE', 'GRÖSSE UND FREIER PLATZ',
    "CHEATS im Spielmenü schaltet jeden Cheat des Spiels während des Spielens an oder aus. Änderungen gelten bei RESUME; ein ausgeschalteter Cheat schreibt nicht mehr, was er schrieb, bleibt. Braucht Cheats für das Spiel an.",
    'Keine CHEATS im Spielmenü: die vor dem Start angehakten Cheats laufen das ganze Spiel, wie bisher.',
    'STARTTON MIT DEN SÄULEN', 'Startton: An (schnell)', 'Startton An (schnell): %s, wenn die Säulen steigen',
    'Startton An: aus dem Ordner AUDIO, sobald sein Laufwerk bereit ist', 'Startton aus (Audio-Einstellungen > Startton)',
    'Kopiert boot.adp neben RIPPS2 auf die Memory Card, von der es startet, wo der Start es liest, bevor ein Laufwerk bereit ist.',
], [
    'Titel und Beschreibung in der Liste',
    "Titel und Beschreibung des Spiels aus seiner CFG neben der Spieleliste. Theme: wie das Theme sie zeigt (das eigene Theme von RIPPS2 lässt sie weg). Die Infoseite behält sie in jedem Fall.",
    'PS1-Duplikate',
    "Ein PS1-Spiel, das sowohl als POPSTARTER-VCD als auch als Ember-Abbild vorliegt. Beide: zwei Zeilen. Ember: nur das Ember-Abbild. POPSTARTER: nur die VCD. Derselbe Titel, eine vorangestellte Disc-ID beiseite, ist dasselbe Spiel.",
    'Meine Pads',
    "Die .pad-Profile im Ordner PADS neben RIPPS2: eine Textdatei pro USB-Pad, nach seiner ID benannt (2563_0575.pad), jede geprüft. RIPPS2 führt das Format an; PADEMU liest sie in einem späteren Build.",
    "Der Startton beim Start von RIPPS2. An: aus dem Ordner AUDIO, sobald sein Laufwerk bereit ist. An (schnell): eine Kopie neben RIPPS2 auf der Memory Card, von der es startet (angeboten, wenn du es wählst), gespielt, wenn die Säulen steigen. Er spielt auch mit ausgeschalteten Soundeffekten.",
])

T['French'] = ([
    '\n%d mappages de boutons de jeu dans GAMES', '\n1 mappage de boutons de jeu dans GAMES', '(sans nom)', 'Les deux',
    "Aucun pour l'instant. Un profil est un fichier texte nommé d'après l'ID de la manette, comme 2563_0575.pad : le format est dans le dépôt de RIPPS2 (docs/plans/pad-spec.md).",
    'Activé (rapide)', 'Profils de manette dans %s :', 'RIPPS2 %s lite (build %d) sur RiptOPL %s',
    "RIPPS2 ne sait pas où est son dossier, il ne peut donc pas chercher PADS.", 'illisible',
    'Encore environ %d secondes', 'Encore environ 1 seconde', 'Plus long que son dernier démarrage (%d s jusqu\'ici)',
    "Télécharger les jaquettes en HD (280 x 400) ? Plus nettes sur un écran HD, environ 70 Ko chacune. START : Standard (140 x 200, comme Open PS2 Loader), environ 20 Ko chacune. Un jeu qui a déjà une jaquette la garde.",
    'STANDARD', '%d AJOUTÉS', '%d AJOUTÉS, %d REMPLACÉS', 'ÉCRITURE IMPOSSIBLE', 'Préparation : %s', 'PAS UN .TAR',
    'RIEN DE CHANGÉ', 'RIEN À AJOUTER',
    "Activé (rapide) garde le son de démarrage à côté de RIPPS2 sur la carte mémoire d'où il démarre, et RIPPS2 n'a pas démarré d'une carte. Le son de démarrage joue comme Activé.",
    "Pas encore de son de démarrage à copier : Paramètres audio > Sons du BIOS extrait ceux de cette console.",
    "Ceci est RIPPS2 lite, qui n'embarque pas PS2BBL, il ne peut donc pas installer BIBLE. Le RIPPS2.elf complet l'installe et le répare ; un chargeur déjà installé continue de lancer RIPPS2 lite tel quel.",
    '%d COPIÉS HORS', '%d ÉLÉMENT   %d MARQUÉ   %s', '%d ÉLÉMENT   %d MARQUÉ   %s   %s LIBRE',
    '%d ÉLÉMENTS   %d MARQUÉS   %s', '%d ÉLÉMENTS   %d MARQUÉS   %s   %s LIBRE', '%s DANS %d', '%s DANS %d, %s LIBRE',
    ', %d LAISSÉS DE CÔTÉ', 'COPIEZ-LE HORS POUR L\'OUVRIR', 'Copie hors : %s', 'INVERSER LES MARQUES',
    'AUCUN FICHIER DANS LE PRESSE-PAPIERS', 'TAILLE ET ESPACE LIBRE',
    "CHEATS dans le menu en jeu active ou désactive chaque cheat du jeu pendant la partie. Les changements s'appliquent à RESUME ; un cheat désactivé cesse d'écrire, ce qu'il a écrit reste. Nécessite les Cheats activés pour le jeu.",
    "Pas de CHEATS dans le menu en jeu : les cheats cochés avant le lancement tournent tout le jeu, comme avant.",
    'SON DE DÉMARRAGE AVEC LES PILIERS', 'Son de démarrage : Activé (rapide)', 'Son de démarrage Activé (rapide) : %s, quand les piliers montent',
    'Son de démarrage Activé : depuis le dossier AUDIO, une fois son lecteur prêt', 'Son de démarrage désactivé (Paramètres audio > Son de démarrage)',
    "Copie boot.adp à côté de RIPPS2 sur la carte mémoire d'où il démarre, où le démarrage le lit avant qu'un lecteur soit prêt.",
], [
    'Titre et description dans la liste',
    "Le titre et la description du jeu tirés de sa CFG à côté de la liste. Thème : comme le thème les montre (le thème de RIPPS2 les masque). La page d'infos les garde dans tous les cas.",
    'Doublons PS1',
    "Un jeu PS1 présent à la fois en VCD POPSTARTER et en image Ember. Les deux : deux lignes. Ember : seulement celle d'Ember. POPSTARTER : seulement la VCD. Le même titre, sans l'ID de disque en tête, est le même jeu.",
    'Mes manettes',
    "Les profils .pad du dossier PADS à côté de RIPPS2 : un fichier texte par manette USB, nommé d'après son ID (2563_0575.pad), chacun vérifié. RIPPS2 mène le format ; PADEMU les lira dans un build ultérieur.",
    "Le son de démarrage au lancement de RIPPS2. Activé : depuis le dossier AUDIO, une fois son lecteur prêt. Activé (rapide) : une copie à côté de RIPPS2 sur la carte mémoire d'où il démarre (proposée quand vous le choisissez), jouée quand les piliers montent. Il joue aussi avec les effets sonores désactivés.",
])

T['Spanish'] = ([
    '\n%d asignaciones de botones de juegos en GAMES', '\n1 asignación de botones de juego en GAMES', '(sin nombre)', 'Ambos',
    "Ninguno aún. Un perfil es un archivo de texto con el nombre de la ID del mando, como 2563_0575.pad: el formato está en el repositorio de RIPPS2 (docs/plans/pad-spec.md).",
    'Activado (rápido)', 'Perfiles de mando en %s:', 'RIPPS2 %s lite (build %d) sobre RiptOPL %s',
    'RIPPS2 no sabe dónde está su carpeta, así que no puede buscar PADS.', 'no se pudo leer',
    'Quedan unos %d segundos', 'Queda 1 segundo', 'Tarda más que su último arranque (%d s hasta ahora)',
    "¿Descargar las carátulas en HD (280 x 400)? Más nítidas en una pantalla HD, unos 70 KB cada una. START: Estándar (140 x 200, como Open PS2 Loader), unos 20 KB cada una. Un juego que ya tiene carátula la conserva.",
    'ESTÁNDAR', '%d DENTRO', '%d DENTRO, %d REEMPLAZADOS', 'NO SE PUDO ESCRIBIR', 'Preparando: %s', 'NO ES UN .TAR',
    'NADA CAMBIADO', 'NADA QUE AÑADIR',
    "Activado (rápido) guarda el sonido de inicio junto a RIPPS2 en la tarjeta de memoria desde la que arranca, y RIPPS2 no arrancó desde una. El sonido de inicio suena como Activado.",
    "Aún no hay sonido de inicio que copiar: Ajustes de audio > Sonidos de la BIOS extrae los de esta consola.",
    "Esto es RIPPS2 lite, que no lleva PS2BBL, así que no puede instalar BIBLE. El RIPPS2.elf completo lo instala y lo repara; un cargador ya instalado sigue arrancando RIPPS2 lite tal cual.",
    '%d COPIADOS FUERA', '%d ELEMENTO   %d MARCADO   %s', '%d ELEMENTO   %d MARCADO   %s   %s LIBRE',
    '%d ELEMENTOS   %d MARCADOS   %s', '%d ELEMENTOS   %d MARCADOS   %s   %s LIBRE', '%s EN %d', '%s EN %d, %s LIBRE',
    ', %d FUERA', 'CÓPIALO FUERA PARA ABRIRLO', 'Copiando fuera: %s', 'INVERTIR MARCAS',
    'NO HAY ARCHIVOS EN EL PORTAPAPELES', 'TAMAÑO Y ESPACIO LIBRE',
    "CHEATS en el menú del juego activa o desactiva cada truco del juego mientras juegas. Los cambios se aplican en RESUME; un truco desactivado deja de escribir, lo que escribió se queda. Necesita los Cheats activados para el juego.",
    "Sin CHEATS en el menú del juego: los trucos marcados antes del inicio funcionan todo el juego, como antes.",
    'SONIDO DE INICIO CON LOS PILARES', 'Sonido de inicio: Activado (rápido)', 'Sonido de inicio Activado (rápido): %s, al subir los pilares',
    'Sonido de inicio Activado: desde la carpeta AUDIO, cuando su unidad está lista', 'Sonido de inicio desactivado (Ajustes de audio > Sonido de inicio)',
    "Copia boot.adp junto a RIPPS2 en la tarjeta de memoria desde la que arranca, donde el inicio lo lee antes de que una unidad esté lista.",
], [
    'Título y descripción en la lista',
    "El título y la descripción del juego de su CFG junto a la lista. Tema: como el tema los muestre (el tema propio de RIPPS2 los oculta). La página de información los conserva siempre.",
    'Duplicados de PS1',
    "Un juego de PS1 que es a la vez un VCD de POPSTARTER y una imagen de Ember. Ambos: dos filas. Ember: solo la de Ember. POPSTARTER: solo el VCD. El mismo título, sin la ID de disco delante, es el mismo juego.",
    'Mis mandos',
    "Los perfiles .pad de la carpeta PADS junto a RIPPS2: un archivo de texto por mando USB, con el nombre de su ID (2563_0575.pad), cada uno comprobado. RIPPS2 lidera el formato; PADEMU los leerá en un build posterior.",
    "El sonido de inicio al arrancar RIPPS2. Activado: desde la carpeta AUDIO, cuando su unidad está lista. Activado (rápido): una copia junto a RIPPS2 en la tarjeta de memoria desde la que arranca (se ofrece al elegirlo), sonando al subir los pilares. Suena también con los efectos de sonido desactivados.",
])

T['Italian'] = ([
    '\n%d mappature dei tasti dei giochi in GAMES', '\n1 mappatura dei tasti di un gioco in GAMES', '(senza nome)', 'Entrambi',
    "Ancora nessuno. Un profilo è un file di testo con il nome dell'ID del pad, come 2563_0575.pad: il formato è nel repository di RIPPS2 (docs/plans/pad-spec.md).",
    'Attivo (veloce)', 'Profili pad in %s:', 'RIPPS2 %s lite (build %d) su RiptOPL %s',
    'RIPPS2 non sa dove sia la sua cartella, quindi non può cercare PADS.', 'non leggibile',
    'Circa %d secondi rimasti', 'Circa 1 secondo rimasto', "Più lento dell'ultimo avvio (%d s finora)",
    "Scaricare le copertine in HD (280 x 400)? Più nitide su uno schermo HD, circa 70 KB ciascuna. START: Standard (140 x 200, come Open PS2 Loader), circa 20 KB ciascuna. Un gioco che ha già una copertina la tiene.",
    'STANDARD', '%d DENTRO', '%d DENTRO, %d SOSTITUITI', 'SCRITTURA NON RIUSCITA', 'Preparazione: %s', 'NON È UN .TAR',
    'NIENTE CAMBIATO', 'NIENTE DA AGGIUNGERE',
    "Attivo (veloce) tiene il suono di avvio accanto a RIPPS2 sulla memory card da cui parte, e RIPPS2 non è partito da una. Il suono di avvio suona come Attivo.",
    "Non c'è ancora un suono di avvio da copiare: Impostazioni audio > Suoni del BIOS estrae quelli di questa console.",
    "Questo è RIPPS2 lite, che non porta PS2BBL, quindi non può installare BIBLE. Il RIPPS2.elf completo lo installa e lo ripara; un boot loader già installato continua ad avviare RIPPS2 lite così com'è.",
    '%d COPIATI FUORI', '%d ELEMENTO   %d SEGNATO   %s', '%d ELEMENTO   %d SEGNATO   %s   %s LIBERI',
    '%d ELEMENTI   %d SEGNATI   %s', '%d ELEMENTI   %d SEGNATI   %s   %s LIBERI', '%s IN %d', '%s IN %d, %s LIBERI',
    ', %d ESCLUSI', 'COPIALO FUORI PER APRIRLO', 'Copia fuori: %s', 'INVERTI SEGNI',
    'NESSUN FILE NEGLI APPUNTI', 'DIMENSIONE E SPAZIO LIBERO',
    "CHEATS nel menu di gioco attiva o disattiva ogni trucco del gioco mentre giochi. Le modifiche valgono a RESUME; un trucco disattivato smette di scrivere, ciò che ha scritto resta. Richiede i Cheats attivi per il gioco.",
    "Nessun CHEATS nel menu di gioco: i trucchi spuntati prima dell'avvio restano attivi per tutto il gioco, come prima.",
    'SUONO DI AVVIO CON I PILASTRI', 'Suono di avvio: Attivo (veloce)', 'Suono di avvio Attivo (veloce): %s, mentre i pilastri salgono',
    'Suono di avvio Attivo: dalla cartella AUDIO, quando la sua unità è pronta', 'Suono di avvio disattivato (Impostazioni audio > Suono di avvio)',
    "Copia boot.adp accanto a RIPPS2 sulla memory card da cui parte, dove l'avvio lo legge prima che un'unità sia pronta.",
], [
    'Titolo e descrizione nella lista',
    "Il titolo e la descrizione del gioco dalla sua CFG accanto alla lista. Tema: come li mostra il tema (il tema di RIPPS2 li nasconde). La pagina info li tiene comunque.",
    'Doppioni PS1',
    "Un gioco PS1 presente sia come VCD di POPSTARTER sia come immagine Ember. Entrambi: due righe. Ember: solo quella Ember. POPSTARTER: solo la VCD. Lo stesso titolo, a parte un ID disco iniziale, è lo stesso gioco.",
    'I miei pad',
    "I profili .pad nella cartella PADS accanto a RIPPS2: un file di testo per pad USB, col nome del suo ID (2563_0575.pad), ognuno controllato. RIPPS2 guida il formato; PADEMU li leggerà in una build successiva.",
    "Il suono di avvio all'avvio di RIPPS2. Attivo: dalla cartella AUDIO, quando la sua unità è pronta. Attivo (veloce): una copia accanto a RIPPS2 sulla memory card da cui parte (offerta quando lo scegli), suonata mentre i pilastri salgono. Suona anche con gli effetti sonori disattivati.",
])

os.makedirs(os.path.join(HERE, 'tr126'), exist_ok=True)
for lang, (s, l) in T.items():
    assert len(s) == 46 and len(l) == len(LABELS), (lang, len(s), len(l))
    json.dump({'s': {str(i): v for i, v in enumerate(s)}, 'l': dict(zip(LABELS, l))},
              open(os.path.join(HERE, 'tr126', lang + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', ', '.join(T))
