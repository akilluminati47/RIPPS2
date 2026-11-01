"""Build 129 translations, batch A (Germanic and Romance). python tools/lang129/tr_a.py"""
from w129 import write

T = {}

T['German'] = ([
    '%s konnte nicht geschrieben werden.', '%s ist schon da und konnte nicht beiseitegelegt werden, also blieb es, wie es war.',
    'Kreis', 'Kreuz', 'Unten', 'Unten auf dem Steuerkreuz',
    '%04X:%04X gefunden. Lass alles daran los, auch die Sticks, und warte.', 'Erkannt. Loslassen.',
    'L3 (den linken Stick hineindrücken)', 'Links auf dem Steuerkreuz', 'Nichts wurde eingerichtet, also wurde keine Datei geschrieben.',
    'Steck das USB-Pad ein, das du einrichten willst. Steckt es schon, zieh es ab und steck es wieder ein. Drück dann einmal eine beliebige Taste darauf.',
    'Drück %s auf dem USB-Pad und halte es.', 'Drück %s und halte ihn.', 'R3 (den rechten Stick hineindrücken)', 'Rechts auf dem Steuerkreuz',
    'Speichern', 'Gespeichert als %s. Das Pad steuert jetzt das Menü und spielt in Spielen mit eingeschaltetem Pad-Emulator.',
    'Überspringen', 'Quadrat', 'Dieses Pad lässt sich noch nicht in einer .pad beschreiben (%s), also wurde keine Datei geschrieben.',
    'Dreieck', 'Probier es aus. Was du hältst, erscheint hier:', 'Oben', 'Oben auf dem Steuerkreuz',
    'den linken Stick nach unten', 'den linken Stick nach rechts', 'den rechten Stick nach unten', 'den rechten Stick nach rechts',
], [
    'USB-Pad einrichten',
    'Steck ein USB-Pad ein, das RIPPS2 nicht kennt, drück jede Taste, nach der es fragt, und RIPPS2 schreibt seine .pad in PADS. SELECT auf deinem PS2-Pad überspringt eine Taste.',
    'Die .pad-Profile im Ordner PADS neben RIPPS2: eine Textdatei pro USB-Pad, nach seiner ID benannt (2563_0575.pad), jede geprüft. Ein Pad mit Profil steuert das Menü und spielt in Spielen (Pad-Emulator an).',
])

T['Dutch'] = ([
    '%s kon niet worden geschreven.', '%s bestaat al en kon niet opzij worden gezet, dus het bleef zoals het was.',
    'Cirkel', 'Kruis', 'Omlaag', 'Omlaag op de d-pad',
    '%04X:%04X gevonden. Laat alles erop los, ook de sticks, en wacht.', 'Gelukt. Loslaten.',
    'L3 (druk de linkerstick in)', 'Links op de d-pad', 'Er is niets ingesteld, dus er is geen bestand geschreven.',
    'Sluit de USB-pad aan die je wilt instellen. Zit hij er al in, haal hem eruit en sluit hem opnieuw aan. Druk dan één keer op een willekeurige knop.',
    'Druk %s op de USB-pad in en houd vast.', 'Duw %s en houd vast.', 'R3 (druk de rechterstick in)', 'Rechts op de d-pad',
    'Opslaan', 'Opgeslagen als %s. De pad bestuurt nu het menu en speelt in games met de Pad Emulator aan.',
    'Overslaan', 'Vierkant', 'Deze pad kan nog niet in een .pad worden beschreven (%s), dus er is geen bestand geschreven.',
    'Driehoek', 'Probeer het. Wat je vasthoudt, staat hier:', 'Omhoog', 'Omhoog op de d-pad',
    'de linkerstick omlaag', 'de linkerstick naar rechts', 'de rechterstick omlaag', 'de rechterstick naar rechts',
], [
    'Een USB-pad instellen',
    'Sluit een USB-pad aan die RIPPS2 niet kent, druk elke knop in waar het om vraagt, en RIPPS2 schrijft zijn .pad in PADS. SELECT op je PS2-pad slaat een knop over.',
    'De .pad-profielen in de map PADS naast RIPPS2: één tekstbestand per USB-pad, genoemd naar zijn ID (2563_0575.pad), elk gecontroleerd. Een pad met profiel bestuurt het menu en speelt in games (Pad Emulator aan).',
])

T['Danish'] = ([
    '%s kunne ikke skrives.', '%s findes allerede og kunne ikke lægges til side, så det blev, som det var.',
    'Cirkel', 'Kryds', 'Ned', 'Ned på retningsknappen',
    'Fandt %04X:%04X. Slip alt på den, også pindene, og vent.', 'Fanget. Slip.',
    'L3 (tryk venstre pind ind)', 'Venstre på retningsknappen', 'Intet blev sat op, så ingen fil blev skrevet.',
    'Sæt den USB-controller i, du vil sætte op. Sidder den allerede i, så tag den ud og sæt den i igen. Tryk så én gang på en vilkårlig knap på den.',
    'Tryk %s på USB-controlleren, og hold den.', 'Skub %s, og hold den.', 'R3 (tryk højre pind ind)', 'Højre på retningsknappen',
    'Gem', 'Gemt som %s. Controlleren styrer nu menuen og spiller i spil med Pad Emulator slået til.',
    'Spring over', 'Firkant', 'Denne controller kan endnu ikke beskrives i en .pad (%s), så ingen fil blev skrevet.',
    'Trekant', 'Prøv den. Det, du holder, vises her:', 'Op', 'Op på retningsknappen',
    'venstre pind ned', 'venstre pind til højre', 'højre pind ned', 'højre pind til højre',
], [
    'Sæt en USB-controller op',
    'Sæt en USB-controller i, som RIPPS2 ikke kender, tryk på hver knap, den beder om, og RIPPS2 skriver dens .pad i PADS. SELECT på din PS2-controller springer en knap over.',
    '.pad-profilerne i mappen PADS ved siden af RIPPS2: én tekstfil pr. USB-controller, navngivet efter dens ID (2563_0575.pad), og hver af dem tjekket. En controller med profil styrer menuen og spiller i spil (Pad Emulator til).',
])

T['Swedish'] = ([
    '%s kunde inte skrivas.', '%s finns redan och kunde inte läggas undan, så den lämnades som den var.',
    'Cirkel', 'Kryss', 'Ner', 'Ner på styrkorset',
    'Hittade %04X:%04X. Släpp allt på den, spakarna också, och vänta.', 'Klart. Släpp.',
    'L3 (tryck in vänster spak)', 'Vänster på styrkorset', 'Inget ställdes in, så ingen fil skrevs.',
    'Anslut USB-handkontrollen du vill ställa in. Sitter den redan i, dra ur den och anslut den igen. Tryck sedan en gång på valfri knapp på den.',
    'Tryck %s på USB-handkontrollen och håll in.', 'För %s och håll kvar.', 'R3 (tryck in höger spak)', 'Höger på styrkorset',
    'Spara', 'Sparad som %s. Handkontrollen styr nu menyn och spelar i spel med Pad Emulator på.',
    'Hoppa över', 'Fyrkant', 'Den här handkontrollen kan inte beskrivas i en .pad än (%s), så ingen fil skrevs.',
    'Triangel', 'Prova. Det du håller in visas här:', 'Upp', 'Upp på styrkorset',
    'vänster spak nedåt', 'vänster spak åt höger', 'höger spak nedåt', 'höger spak åt höger',
], [
    'Ställ in en USB-handkontroll',
    'Anslut en USB-handkontroll som RIPPS2 inte känner till, tryck på varje knapp den ber om, så skriver RIPPS2 dess .pad i PADS. SELECT på din PS2-handkontroll hoppar över en knapp.',
    '.pad-profilerna i mappen PADS bredvid RIPPS2: en textfil per USB-handkontroll, namngiven efter dess ID (2563_0575.pad), och var och en kontrollerad. En handkontroll med profil styr menyn och spelar i spel (Pad Emulator på).',
])

T['French'] = ([
    "%s n'a pas pu être écrit.", "%s existe déjà et n'a pas pu être mis de côté, il a donc été laissé tel quel.",
    'Rond', 'Croix', 'Bas', 'Bas sur la croix directionnelle',
    '%04X:%04X trouvée. Relâchez tout dessus, sticks compris, et attendez.', 'Reçu. Relâchez.',
    'L3 (enfoncez le stick gauche)', 'Gauche sur la croix directionnelle', "Rien n'a été configuré, donc aucun fichier n'a été écrit.",
    "Branchez la manette USB à configurer. Si elle est déjà branchée, débranchez-la puis rebranchez-la. Appuyez ensuite une fois sur n'importe quel bouton.",
    'Appuyez sur %s sur la manette USB et maintenez.', 'Poussez %s et maintenez.', 'R3 (enfoncez le stick droit)', 'Droite sur la croix directionnelle',
    'Enregistrer', 'Enregistré sous %s. La manette pilote maintenant le menu et joue dans les jeux avec le Pad Emulator activé.',
    'Passer', 'Carré', "Cette manette ne peut pas encore être décrite dans un .pad (%s), donc aucun fichier n'a été écrit.",
    'Triangle', 'Essayez. Ce que vous maintenez s\'affiche ici :', 'Haut', 'Haut sur la croix directionnelle',
    'le stick gauche vers le bas', 'le stick gauche vers la droite', 'le stick droit vers le bas', 'le stick droit vers la droite',
], [
    'Configurer une manette USB',
    "Branchez une manette USB que RIPPS2 ne connaît pas, appuyez sur chaque bouton demandé, et RIPPS2 écrit son .pad dans PADS. SELECT sur votre manette PS2 passe un bouton.",
    "Les profils .pad du dossier PADS à côté de RIPPS2 : un fichier texte par manette USB, nommé d'après son ID (2563_0575.pad), chacun vérifié. Une manette profilée pilote le menu et joue dans les jeux (Pad Emulator activé).",
])

T['Spanish'] = ([
    'No se pudo escribir %s.', '%s ya existe y no se pudo apartar, así que se dejó como estaba.',
    'Círculo', 'Equis', 'Abajo', 'Abajo en la cruceta',
    'Encontrado %04X:%04X. Suelta todo en él, también los sticks, y espera.', 'Hecho. Suelta.',
    'L3 (pulsa el stick izquierdo)', 'Izquierda en la cruceta', 'No se configuró nada, así que no se escribió ningún archivo.',
    'Conecta el mando USB que quieres configurar. Si ya está conectado, desconéctalo y vuelve a conectarlo. Luego pulsa una vez cualquier botón.',
    'Pulsa %s en el mando USB y mantenlo.', 'Mueve %s y mantenlo.', 'R3 (pulsa el stick derecho)', 'Derecha en la cruceta',
    'Guardar', 'Guardado como %s. El mando ya maneja el menú y juega en los juegos con el Pad Emulator activado.',
    'Omitir', 'Cuadrado', 'Este mando aún no se puede describir en un .pad (%s), así que no se escribió ningún archivo.',
    'Triángulo', 'Pruébalo. Lo que mantengas pulsado aparece aquí:', 'Arriba', 'Arriba en la cruceta',
    'el stick izquierdo hacia abajo', 'el stick izquierdo hacia la derecha', 'el stick derecho hacia abajo', 'el stick derecho hacia la derecha',
], [
    'Configurar un mando USB',
    'Conecta un mando USB que RIPPS2 no conozca, pulsa cada botón que te pida y RIPPS2 escribe su .pad en PADS. SELECT en tu mando de PS2 omite un botón.',
    'Los perfiles .pad de la carpeta PADS junto a RIPPS2: un archivo de texto por mando USB, con el nombre de su ID (2563_0575.pad), y cada uno comprobado. Un mando con perfil maneja el menú y juega en los juegos (Pad Emulator activado).',
])

T['Galician'] = ([
    'Non se puido escribir %s.', '%s xa existe e non se puido apartar, así que quedou como estaba.',
    'Círculo', 'Aspa', 'Abaixo', 'Abaixo na cruceta',
    'Atopado %04X:%04X. Solta todo nel, tamén os sticks, e agarda.', 'Feito. Solta.',
    'L3 (preme o stick esquerdo)', 'Esquerda na cruceta', 'Non se configurou nada, así que non se escribiu ningún ficheiro.',
    'Conecta o mando USB que queres configurar. Se xa está conectado, desconéctao e volve conectalo. Despois preme unha vez calquera botón.',
    'Preme %s no mando USB e mantéño.', 'Move %s e mantéño.', 'R3 (preme o stick dereito)', 'Dereita na cruceta',
    'Gardar', 'Gardado como %s. O mando xa manexa o menú e xoga nos xogos co Pad Emulator activado.',
    'Omitir', 'Cadrado', 'Este mando aínda non se pode describir nun .pad (%s), así que non se escribiu ningún ficheiro.',
    'Triángulo', 'Próbao. O que manteñas premido aparece aquí:', 'Arriba', 'Arriba na cruceta',
    'o stick esquerdo cara abaixo', 'o stick esquerdo cara á dereita', 'o stick dereito cara abaixo', 'o stick dereito cara á dereita',
], [
    'Configurar un mando USB',
    'Conecta un mando USB que RIPPS2 non coñeza, preme cada botón que che pida e RIPPS2 escribe o seu .pad en PADS. SELECT no teu mando de PS2 omite un botón.',
    'Os perfís .pad do cartafol PADS xunto a RIPPS2: un ficheiro de texto por mando USB, co nome do seu ID (2563_0575.pad), e cada un comprobado. Un mando con perfil manexa o menú e xoga nos xogos (Pad Emulator activado).',
])

T['Italian'] = ([
    'Impossibile scrivere %s.', "%s esiste già e non è stato possibile metterlo da parte, quindi è rimasto com'era.",
    'Cerchio', 'Croce', 'Giù', 'Giù sulla croce direzionale',
    'Trovato %04X:%04X. Rilascia tutto, anche le levette, e attendi.', 'Fatto. Rilascia.',
    'L3 (premi la levetta sinistra)', 'Sinistra sulla croce direzionale', 'Non è stato configurato nulla, quindi non è stato scritto alcun file.',
    'Collega il pad USB da configurare. Se è già collegato, scollegalo e ricollegalo. Poi premi una volta un tasto qualsiasi.',
    'Premi %s sul pad USB e tienilo premuto.', 'Spingi %s e tienila.', 'R3 (premi la levetta destra)', 'Destra sulla croce direzionale',
    'Salva', 'Salvato come %s. Il pad ora comanda il menu e gioca nei giochi con il Pad Emulator attivo.',
    'Salta', 'Quadrato', 'Questo pad non può ancora essere descritto in un .pad (%s), quindi non è stato scritto alcun file.',
    'Triangolo', 'Provalo. Ciò che tieni premuto appare qui:', 'Su', 'Su sulla croce direzionale',
    'la levetta sinistra in giù', 'la levetta sinistra a destra', 'la levetta destra in giù', 'la levetta destra a destra',
], [
    'Configura un pad USB',
    'Collega un pad USB che RIPPS2 non conosce, premi ogni tasto richiesto e RIPPS2 scrive il suo .pad in PADS. SELECT sul tuo pad PS2 salta un tasto.',
    "I profili .pad nella cartella PADS accanto a RIPPS2: un file di testo per pad USB, col nome del suo ID (2563_0575.pad), ognuno controllato. Un pad con profilo comanda il menu e gioca nei giochi (Pad Emulator attivo).",
])

write(T)
