"""Build 129 translations, batch B (Romance, Slavic). python tools/lang129/tr_b.py"""
from w129 import write

T = {}

T['Portuguese'] = ([
    'Não foi possível escrever %s.', '%s já existe e não pôde ser posto de parte, por isso ficou como estava.',
    'Círculo', 'Cruz', 'Baixo', 'Baixo no direcional',
    'Encontrado %04X:%04X. Larga tudo nele, também os analógicos, e espera.', 'Feito. Larga.',
    'L3 (carrega no analógico esquerdo)', 'Esquerda no direcional', 'Nada foi configurado, por isso nenhum ficheiro foi escrito.',
    'Liga o comando USB que queres configurar. Se já estiver ligado, desliga-o e volta a ligá-lo. Depois carrega uma vez em qualquer botão.',
    'Carrega em %s no comando USB e mantém.', 'Empurra %s e mantém.', 'R3 (carrega no analógico direito)', 'Direita no direcional',
    'Guardar', 'Guardado como %s. O comando já controla o menu e joga nos jogos com o Pad Emulator ligado.',
    'Saltar', 'Quadrado', 'Este comando ainda não pode ser descrito num .pad (%s), por isso nenhum ficheiro foi escrito.',
    'Triângulo', 'Experimenta. O que manténs premido aparece aqui:', 'Cima', 'Cima no direcional',
    'o analógico esquerdo para baixo', 'o analógico esquerdo para a direita', 'o analógico direito para baixo', 'o analógico direito para a direita',
], [
    'Configurar um comando USB',
    'Liga um comando USB que o RIPPS2 não conheça, carrega em cada botão que ele pedir e o RIPPS2 escreve o seu .pad em PADS. SELECT no teu comando PS2 salta um botão.',
    'Os perfis .pad na pasta PADS ao lado do RIPPS2: um ficheiro de texto por comando USB, com o nome do seu ID (2563_0575.pad), e cada um verificado. Um comando com perfil controla o menu e joga nos jogos (Pad Emulator ligado).',
])

T['Portuguese_BR'] = ([
    'Não foi possível gravar %s.', '%s já existe e não pôde ser deixado de lado, então ficou como estava.',
    'Círculo', 'X', 'Baixo', 'Baixo no direcional',
    'Encontrado %04X:%04X. Solte tudo nele, os analógicos também, e espere.', 'Pronto. Solte.',
    'L3 (aperte o analógico esquerdo)', 'Esquerda no direcional', 'Nada foi configurado, então nenhum arquivo foi gravado.',
    'Conecte o controle USB que você quer configurar. Se ele já estiver conectado, desconecte e conecte de novo. Depois aperte qualquer botão nele uma vez.',
    'Aperte %s no controle USB e segure.', 'Empurre %s e segure.', 'R3 (aperte o analógico direito)', 'Direita no direcional',
    'Salvar', 'Salvo como %s. O controle agora comanda o menu e joga nos jogos com o Pad Emulator ligado.',
    'Pular', 'Quadrado', 'Este controle ainda não pode ser descrito em um .pad (%s), então nenhum arquivo foi gravado.',
    'Triângulo', 'Teste. O que você segurar aparece aqui:', 'Cima', 'Cima no direcional',
    'o analógico esquerdo para baixo', 'o analógico esquerdo para a direita', 'o analógico direito para baixo', 'o analógico direito para a direita',
], [
    'Configurar um controle USB',
    'Conecte um controle USB que o RIPPS2 não conhece, aperte cada botão que ele pedir e o RIPPS2 grava o .pad dele em PADS. SELECT no seu controle de PS2 pula um botão.',
    'Os perfis .pad na pasta PADS ao lado do RIPPS2: um arquivo de texto por controle USB, com o nome do ID dele (2563_0575.pad), e cada um verificado. Um controle com perfil comanda o menu e joga nos jogos (Pad Emulator ligado).',
])

T['Romana'] = ([
    '%s nu a putut fi scris.', '%s există deja și nu a putut fi pus deoparte, așa că a rămas cum era.',
    'Cerc', 'X', 'Jos', 'Jos pe cruce',
    'Găsit %04X:%04X. Eliberează tot de pe el, și stick-urile, și așteaptă.', 'Gata. Eliberează.',
    'L3 (apasă stick-ul stâng)', 'Stânga pe cruce', 'Nu s-a configurat nimic, așa că nu s-a scris niciun fișier.',
    'Conectează controlerul USB pe care vrei să-l configurezi. Dacă e deja conectat, scoate-l și conectează-l din nou. Apoi apasă o dată orice buton de pe el.',
    'Apasă %s pe controlerul USB și ține apăsat.', 'Împinge %s și ține-l.', 'R3 (apasă stick-ul drept)', 'Dreapta pe cruce',
    'Salvează', 'Salvat ca %s. Controlerul conduce acum meniul și joacă în jocuri cu Pad Emulator pornit.',
    'Sari', 'Pătrat', 'Acest controler nu poate fi descris încă într-un .pad (%s), așa că nu s-a scris niciun fișier.',
    'Triunghi', 'Încearcă. Ce ții apăsat apare aici:', 'Sus', 'Sus pe cruce',
    'stick-ul stâng în jos', 'stick-ul stâng la dreapta', 'stick-ul drept în jos', 'stick-ul drept la dreapta',
], [
    'Configurează un controler USB',
    'Conectează un controler USB pe care RIPPS2 nu-l cunoaște, apasă fiecare buton cerut, iar RIPPS2 îi scrie .pad-ul în PADS. SELECT pe controlerul tău PS2 sare peste un buton.',
    'Profilurile .pad din folderul PADS de lângă RIPPS2: un fișier text pentru fiecare controler USB, numit după ID-ul lui (2563_0575.pad), și fiecare verificat. Un controler cu profil conduce meniul și joacă în jocuri (Pad Emulator pornit).',
])

T['Polish'] = ([
    'Nie udało się zapisać %s.', '%s już istnieje i nie dało się go odłożyć na bok, więc zostało bez zmian.',
    'Kółko', 'Krzyżyk', 'Dół', 'Dół na krzyżaku',
    'Znaleziono %04X:%04X. Puść wszystko na nim, gałki też, i zaczekaj.', 'Jest. Puść.',
    'L3 (wciśnij lewą gałkę)', 'Lewo na krzyżaku', 'Nic nie zostało ustawione, więc nie zapisano żadnego pliku.',
    'Podłącz pad USB, który chcesz ustawić. Jeśli już jest podłączony, odłącz go i podłącz ponownie. Potem naciśnij raz dowolny przycisk.',
    'Naciśnij %s na padzie USB i przytrzymaj.', 'Wychyl %s i przytrzymaj.', 'R3 (wciśnij prawą gałkę)', 'Prawo na krzyżaku',
    'Zapisz', 'Zapisano jako %s. Pad steruje teraz menu i gra w grach z włączonym Pad Emulator.',
    'Pomiń', 'Kwadrat', 'Tego pada nie da się jeszcze opisać w pliku .pad (%s), więc nie zapisano żadnego pliku.',
    'Trójkąt', 'Wypróbuj. To, co trzymasz, pojawia się tutaj:', 'Góra', 'Góra na krzyżaku',
    'lewą gałkę w dół', 'lewą gałkę w prawo', 'prawą gałkę w dół', 'prawą gałkę w prawo',
], [
    'Ustaw pad USB',
    'Podłącz pad USB, którego RIPPS2 nie zna, naciskaj każdy przycisk, o który prosi, a RIPPS2 zapisze jego .pad w PADS. SELECT na padzie PS2 pomija przycisk.',
    'Profile .pad w folderze PADS obok RIPPS2: jeden plik tekstowy na pad USB, nazwany jego ID (2563_0575.pad), każdy sprawdzony. Pad z profilem steruje menu i gra w grach (Pad Emulator włączony).',
])

T['Czech'] = ([
    '%s se nepodařilo zapsat.', '%s už existuje a nepodařilo se ho odložit stranou, takže zůstal, jak byl.',
    'Kolečko', 'Křížek', 'Dolů', 'Dolů na směrovém kříži',
    'Nalezeno %04X:%04X. Pusť na něm vše, i páčky, a počkej.', 'Mám to. Pusť.',
    'L3 (zmáčkni levou páčku)', 'Vlevo na směrovém kříži', 'Nic nebylo nastaveno, takže se nezapsal žádný soubor.',
    'Připoj USB ovladač, který chceš nastavit. Pokud už je připojený, odpoj ho a připoj znovu. Pak na něm jednou stiskni libovolné tlačítko.',
    'Stiskni %s na USB ovladači a drž.', 'Vychyl %s a drž.', 'R3 (zmáčkni pravou páčku)', 'Vpravo na směrovém kříži',
    'Uložit', 'Uloženo jako %s. Ovladač teď ovládá menu a hraje ve hrách se zapnutým Pad Emulator.',
    'Přeskočit', 'Čtverec', 'Tento ovladač zatím nejde popsat v souboru .pad (%s), takže se nezapsal žádný soubor.',
    'Trojúhelník', 'Vyzkoušej to. Co držíš, se ukáže zde:', 'Nahoru', 'Nahoru na směrovém kříži',
    'levou páčku dolů', 'levou páčku doprava', 'pravou páčku dolů', 'pravou páčku doprava',
], [
    'Nastavit USB ovladač',
    'Připoj USB ovladač, který RIPPS2 nezná, stiskni každé tlačítko, o které požádá, a RIPPS2 zapíše jeho .pad do PADS. SELECT na tvém ovladači PS2 tlačítko přeskočí.',
    'Profily .pad ve složce PADS vedle RIPPS2: jeden textový soubor na USB ovladač, pojmenovaný podle jeho ID (2563_0575.pad), každý zkontrolovaný. Ovladač s profilem ovládá menu a hraje ve hrách (Pad Emulator zapnutý).',
])

T['Croatian'] = ([
    '%s nije moguće zapisati.', '%s već postoji i nije ga bilo moguće skloniti, pa je ostao kakav je bio.',
    'Krug', 'Križić', 'Dolje', 'Dolje na križu',
    'Pronađen %04X:%04X. Pusti sve na njemu, i palice, i pričekaj.', 'Uhvaćeno. Pusti.',
    'L3 (pritisni lijevu palicu)', 'Lijevo na križu', 'Ništa nije postavljeno, pa nijedna datoteka nije zapisana.',
    'Uključi USB kontroler koji želiš postaviti. Ako je već uključen, izvadi ga i uključi ponovno. Zatim jednom pritisni bilo koju tipku na njemu.',
    'Pritisni %s na USB kontroleru i drži.', 'Pomakni %s i drži.', 'R3 (pritisni desnu palicu)', 'Desno na križu',
    'Spremi', 'Spremljeno kao %s. Kontroler sada upravlja izbornikom i igra u igrama s uključenim Pad Emulatorom.',
    'Preskoči', 'Kvadrat', 'Ovaj kontroler još se ne može opisati u .pad datoteci (%s), pa nijedna datoteka nije zapisana.',
    'Trokut', 'Isprobaj. Ono što držiš prikazuje se ovdje:', 'Gore', 'Gore na križu',
    'lijevu palicu dolje', 'lijevu palicu udesno', 'desnu palicu dolje', 'desnu palicu udesno',
], [
    'Postavi USB kontroler',
    'Uključi USB kontroler koji RIPPS2 ne poznaje, pritisni svaku tipku koju zatraži i RIPPS2 zapisuje njegov .pad u PADS. SELECT na tvom PS2 kontroleru preskače tipku.',
    '.pad profili u mapi PADS pokraj RIPPS2: jedna tekstualna datoteka po USB kontroleru, nazvana po njegovom ID-u (2563_0575.pad), i svaki provjeren. Kontroler s profilom upravlja izbornikom i igra u igrama (Pad Emulator uključen).',
])

T['Serbian'] = ([
    '%s nije moguće upisati.', '%s već postoji i nije ga bilo moguće skloniti, pa je ostao kakav je bio.',
    'Krug', 'Iks', 'Dole', 'Dole na krstu',
    'Pronađen %04X:%04X. Pusti sve na njemu, i palice, i sačekaj.', 'Uhvaćeno. Pusti.',
    'L3 (pritisni levu palicu)', 'Levo na krstu', 'Ništa nije podešeno, pa nijedna datoteka nije upisana.',
    'Priključi USB kontroler koji želiš da podesiš. Ako je već priključen, izvadi ga i priključi ponovo. Zatim jednom pritisni bilo koje dugme na njemu.',
    'Pritisni %s na USB kontroleru i drži.', 'Pomeri %s i drži.', 'R3 (pritisni desnu palicu)', 'Desno na krstu',
    'Sačuvaj', 'Sačuvano kao %s. Kontroler sada upravlja menijem i igra u igrama sa uključenim Pad Emulatorom.',
    'Preskoči', 'Kvadrat', 'Ovaj kontroler još ne može da se opiše u .pad datoteci (%s), pa nijedna datoteka nije upisana.',
    'Trougao', 'Isprobaj. Ono što držiš prikazuje se ovde:', 'Gore', 'Gore na krstu',
    'levu palicu dole', 'levu palicu udesno', 'desnu palicu dole', 'desnu palicu udesno',
], [
    'Podesi USB kontroler',
    'Priključi USB kontroler koji RIPPS2 ne poznaje, pritisni svako dugme koje zatraži i RIPPS2 upisuje njegov .pad u PADS. SELECT na tvom PS2 kontroleru preskače dugme.',
    '.pad profili u fascikli PADS pored RIPPS2: jedna tekstualna datoteka po USB kontroleru, nazvana po njegovom ID-u (2563_0575.pad), i svaki proveren. Kontroler sa profilom upravlja menijem i igra u igrama (Pad Emulator uključen).',
])

T['Bulgarian'] = ([
    '%s не можа да бъде записан.', '%s вече съществува и не можа да бъде преместен настрана, затова остана както беше.',
    'Кръг', 'Кръстче', 'Надолу', 'Надолу на кръстачката',
    'Намерен %04X:%04X. Пусни всичко по него, и стиковете, и изчакай.', 'Готово. Пусни.',
    'L3 (натисни левия стик)', 'Наляво на кръстачката', 'Нищо не беше настроено, затова не беше записан файл.',
    'Включи USB контролера, който искаш да настроиш. Ако вече е включен, извади го и го включи отново. После натисни веднъж произволен бутон на него.',
    'Натисни %s на USB контролера и задръж.', 'Бутни %s и задръж.', 'R3 (натисни десния стик)', 'Надясно на кръстачката',
    'Запази', 'Запазено като %s. Контролерът вече управлява менюто и играе в игри с включен Pad Emulator.',
    'Пропусни', 'Квадрат', 'Този контролер още не може да бъде описан в .pad (%s), затова не беше записан файл.',
    'Триъгълник', 'Пробвай. Това, което държиш, се показва тук:', 'Нагоре', 'Нагоре на кръстачката',
    'левия стик надолу', 'левия стик надясно', 'десния стик надолу', 'десния стик надясно',
], [
    'Настрой USB контролер',
    'Включи USB контролер, който RIPPS2 не познава, натисни всеки бутон, който поиска, и RIPPS2 записва неговия .pad в PADS. SELECT на твоя PS2 контролер пропуска бутон.',
    '.pad профилите в папката PADS до RIPPS2: по един текстов файл за USB контролер, наречен по неговото ID (2563_0575.pad), и всеки проверен. Контролер с профил управлява менюто и играе в игри (Pad Emulator включен).',
])

write(T)
