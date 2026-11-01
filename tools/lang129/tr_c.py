"""Build 129 translations, batch C. python tools/lang129/tr_c.py"""
from w129 import write

T = {}

T['Russian'] = ([
    'Не удалось записать %s.', '%s уже существует, и его не удалось отложить, поэтому он остался как был.',
    'Круг', 'Крест', 'Вниз', 'Вниз на крестовине',
    'Найден %04X:%04X. Отпустите на нём всё, и стики тоже, и подождите.', 'Есть. Отпустите.',
    'L3 (нажмите левый стик)', 'Влево на крестовине', 'Ничего не настроено, поэтому файл не записан.',
    'Подключите USB-геймпад, который хотите настроить. Если он уже подключён, отключите и подключите снова. Затем один раз нажмите на нём любую кнопку.',
    'Нажмите %s на USB-геймпаде и держите.', 'Отклоните %s и держите.', 'R3 (нажмите правый стик)', 'Вправо на крестовине',
    'Сохранить', 'Сохранено как %s. Теперь геймпад управляет меню и играет в играх при включённом Pad Emulator.',
    'Пропустить', 'Квадрат', 'Этот геймпад пока нельзя описать в .pad (%s), поэтому файл не записан.',
    'Треугольник', 'Попробуйте. То, что вы держите, видно здесь:', 'Вверх', 'Вверх на крестовине',
    'левый стик вниз', 'левый стик вправо', 'правый стик вниз', 'правый стик вправо',
], [
    'Настроить USB-геймпад',
    'Подключите USB-геймпад, которого RIPPS2 не знает, нажмите каждую кнопку, которую он попросит, и RIPPS2 запишет его .pad в PADS. SELECT на геймпаде PS2 пропускает кнопку.',
    'Профили .pad в папке PADS рядом с RIPPS2: по одному текстовому файлу на USB-геймпад, названному по его ID (2563_0575.pad), и каждый проверен. Геймпад с профилем управляет меню и играет в играх (Pad Emulator включён).',
])

T['Greek'] = ([
    'Δεν ήταν δυνατή η εγγραφή του %s.', 'Το %s υπάρχει ήδη και δεν ήταν δυνατό να μπει στην άκρη, οπότε έμεινε όπως ήταν.',
    'Κύκλος', 'Χι', 'Κάτω', 'Κάτω στο σταυρό κατεύθυνσης',
    'Βρέθηκε %04X:%04X. Άφησε τα πάντα πάνω του, και τους μοχλούς, και περίμενε.', 'Έγινε. Άφησε.',
    'L3 (πάτησε τον αριστερό μοχλό)', 'Αριστερά στο σταυρό κατεύθυνσης', 'Δεν ρυθμίστηκε τίποτα, οπότε δεν γράφτηκε αρχείο.',
    'Σύνδεσε το χειριστήριο USB που θέλεις να ρυθμίσεις. Αν είναι ήδη συνδεδεμένο, αποσύνδεσέ το και σύνδεσέ το ξανά. Μετά πάτησε μία φορά οποιοδήποτε κουμπί του.',
    'Πάτησε %s στο χειριστήριο USB και κράτησέ το.', 'Σπρώξε %s και κράτησέ τον.', 'R3 (πάτησε τον δεξί μοχλό)', 'Δεξιά στο σταυρό κατεύθυνσης',
    'Αποθήκευση', 'Αποθηκεύτηκε ως %s. Το χειριστήριο οδηγεί τώρα το μενού και παίζει στα παιχνίδια με ενεργό το Pad Emulator.',
    'Παράλειψη', 'Τετράγωνο', 'Αυτό το χειριστήριο δεν μπορεί ακόμη να περιγραφεί σε .pad (%s), οπότε δεν γράφτηκε αρχείο.',
    'Τρίγωνο', 'Δοκίμασέ το. Ό,τι κρατάς φαίνεται εδώ:', 'Πάνω', 'Πάνω στο σταυρό κατεύθυνσης',
    'τον αριστερό μοχλό κάτω', 'τον αριστερό μοχλό δεξιά', 'τον δεξί μοχλό κάτω', 'τον δεξί μοχλό δεξιά',
], [
    'Ρύθμιση χειριστηρίου USB',
    'Σύνδεσε ένα χειριστήριο USB που δεν γνωρίζει το RIPPS2, πάτησε κάθε κουμπί που ζητά, και το RIPPS2 γράφει το .pad του στο PADS. Το SELECT στο χειριστήριο PS2 παραλείπει ένα κουμπί.',
    'Τα προφίλ .pad στον φάκελο PADS δίπλα στο RIPPS2: ένα αρχείο κειμένου ανά χειριστήριο USB, με όνομα το ID του (2563_0575.pad), και το καθένα ελεγμένο. Ένα χειριστήριο με προφίλ οδηγεί το μενού και παίζει στα παιχνίδια (Pad Emulator ενεργό).',
])

T['Hungarian'] = ([
    '%s nem írható.', '%s már létezik, és nem lehetett félretenni, ezért úgy maradt, ahogy volt.',
    'Kör', 'X', 'Le', 'Le az iránygombon',
    'Megvan: %04X:%04X. Engedj el rajta mindent, a karokat is, és várj.', 'Megvan. Engedd el.',
    'L3 (nyomd be a bal kart)', 'Balra az iránygombon', 'Semmi sem lett beállítva, ezért nem készült fájl.',
    'Csatlakoztasd a beállítandó USB-kontrollert. Ha már be van dugva, húzd ki és dugd be újra. Aztán nyomj meg rajta egyszer egy tetszőleges gombot.',
    'Nyomd meg a(z) %s gombot az USB-kontrolleren, és tartsd.', 'Told %s, és tartsd.', 'R3 (nyomd be a jobb kart)', 'Jobbra az iránygombon',
    'Mentés', 'Mentve: %s. A kontroller most vezérli a menüt, és bekapcsolt Pad Emulatorral játszik a játékokban.',
    'Kihagyás', 'Négyzet', 'Ezt a kontrollert még nem lehet .pad fájlban leírni (%s), ezért nem készült fájl.',
    'Háromszög', 'Próbáld ki. Amit nyomva tartasz, itt látszik:', 'Fel', 'Fel az iránygombon',
    'a bal kart lefelé', 'a bal kart jobbra', 'a jobb kart lefelé', 'a jobb kart jobbra',
], [
    'USB-kontroller beállítása',
    'Csatlakoztass egy USB-kontrollert, amelyet a RIPPS2 nem ismer, nyomd meg az összes kért gombot, és a RIPPS2 megírja a .pad fájlját a PADS mappába. A PS2-kontroller SELECT gombja kihagy egy gombot.',
    'A .pad profilok a RIPPS2 melletti PADS mappában: USB-kontrollerenként egy szövegfájl, az azonosítója szerint elnevezve (2563_0575.pad), mindegyik ellenőrizve. A profillal rendelkező kontroller vezérli a menüt és játszik a játékokban (Pad Emulator bekapcsolva).',
])

T['Turkish'] = ([
    '%s yazılamadı.', '%s zaten var ve kenara alınamadı, bu yüzden olduğu gibi bırakıldı.',
    'Daire', 'Çarpı', 'Aşağı', 'Yön tuşunda aşağı',
    '%04X:%04X bulundu. Üzerindeki her şeyi, çubukları da bırak ve bekle.', 'Tamam. Bırak.',
    'L3 (sol çubuğa bas)', 'Yön tuşunda sol', 'Hiçbir şey ayarlanmadı, bu yüzden dosya yazılmadı.',
    'Ayarlamak istediğin USB kolu tak. Zaten takılıysa çıkar ve yeniden tak. Sonra üzerindeki herhangi bir tuşa bir kez bas.',
    'USB kolda %s tuşuna bas ve basılı tut.', '%s it ve tut.', 'R3 (sağ çubuğa bas)', 'Yön tuşunda sağ',
    'Kaydet', '%s olarak kaydedildi. Kol artık menüyü yönetiyor ve Pad Emulator açıkken oyunlarda oynuyor.',
    'Atla', 'Kare', 'Bu kol henüz bir .pad dosyasında tanımlanamıyor (%s), bu yüzden dosya yazılmadı.',
    'Üçgen', 'Dene. Basılı tuttuğun şey burada görünür:', 'Yukarı', 'Yön tuşunda yukarı',
    'sol çubuğu aşağı', 'sol çubuğu sağa', 'sağ çubuğu aşağı', 'sağ çubuğu sağa',
], [
    'USB kol ayarla',
    "RIPPS2'nin tanımadığı bir USB kol tak, istediği her tuşa bas; RIPPS2 onun .pad dosyasını PADS içine yazar. PS2 kolundaki SELECT bir tuşu atlar.",
    "RIPPS2'nin yanındaki PADS klasöründeki .pad profilleri: her USB kol için kimliğiyle adlandırılmış bir metin dosyası (2563_0575.pad), her biri denetlenmiş. Profili olan bir kol menüyü yönetir ve oyunlarda oynar (Pad Emulator açık).",
])

T['Albanian'] = ([
    '%s nuk mund të shkruhej.', '%s ekziston tashmë dhe nuk mund të lihej mënjanë, ndaj mbeti siç ishte.',
    'Rreth', 'Kryq', 'Poshtë', 'Poshtë në kryqin e drejtimit',
    'U gjet %04X:%04X. Lësho gjithçka në të, edhe levat, dhe prit.', 'U kap. Lësho.',
    'L3 (shtyp levën e majtë)', 'Majtas në kryqin e drejtimit', 'Asgjë nuk u rregullua, ndaj nuk u shkrua asnjë skedar.',
    'Lidh kontrolluesin USB që do të rregullosh. Nëse është i lidhur, hiqe dhe lidhe sërish. Pastaj shtyp një herë çfarëdo butoni në të.',
    'Shtyp %s në kontrolluesin USB dhe mbaje.', 'Shty %s dhe mbaje.', 'R3 (shtyp levën e djathtë)', 'Djathtas në kryqin e drejtimit',
    'Ruaj', 'U ruajt si %s. Kontrolluesi tani drejton menunë dhe luan në lojëra me Pad Emulator të ndezur.',
    'Kapërce', 'Katror', 'Ky kontrollues ende nuk mund të përshkruhet në një .pad (%s), ndaj nuk u shkrua asnjë skedar.',
    'Trekëndësh', 'Provoje. Ajo që mban shtypur shfaqet këtu:', 'Lart', 'Lart në kryqin e drejtimit',
    'levën e majtë poshtë', 'levën e majtë djathtas', 'levën e djathtë poshtë', 'levën e djathtë djathtas',
], [
    'Rregullo një kontrollues USB',
    'Lidh një kontrollues USB që RIPPS2 nuk e njeh, shtyp çdo buton që kërkon dhe RIPPS2 shkruan .pad-in e tij në PADS. SELECT në kontrolluesin tënd PS2 kapërcen një buton.',
    'Profilet .pad në dosjen PADS pranë RIPPS2: një skedar teksti për çdo kontrollues USB, me emrin e ID-së së tij (2563_0575.pad), secili i kontrolluar. Një kontrollues me profil drejton menunë dhe luan në lojëra (Pad Emulator i ndezur).',
])

T['Indonesian'] = ([
    '%s tidak dapat ditulis.', '%s sudah ada dan tidak dapat disisihkan, jadi dibiarkan seperti semula.',
    'Lingkaran', 'Silang', 'Bawah', 'Bawah pada d-pad',
    'Ditemukan %04X:%04X. Lepaskan semua tombolnya, stik juga, lalu tunggu.', 'Dapat. Lepaskan.',
    'L3 (tekan stik kiri)', 'Kiri pada d-pad', 'Tidak ada yang diatur, jadi tidak ada file yang ditulis.',
    'Colokkan pad USB yang ingin diatur. Jika sudah tercolok, cabut lalu colokkan lagi. Lalu tekan sekali tombol apa saja di pad itu.',
    'Tekan %s pada pad USB dan tahan.', 'Dorong %s dan tahan.', 'R3 (tekan stik kanan)', 'Kanan pada d-pad',
    'Simpan', 'Disimpan sebagai %s. Pad ini sekarang mengendalikan menu dan bermain di game dengan Pad Emulator aktif.',
    'Lewati', 'Kotak', 'Pad ini belum bisa dijelaskan dalam .pad (%s), jadi tidak ada file yang ditulis.',
    'Segitiga', 'Coba. Yang kamu tahan tampil di sini:', 'Atas', 'Atas pada d-pad',
    'stik kiri ke bawah', 'stik kiri ke kanan', 'stik kanan ke bawah', 'stik kanan ke kanan',
], [
    'Atur Pad USB',
    'Colokkan pad USB yang belum dikenal RIPPS2, tekan setiap tombol yang diminta, dan RIPPS2 menulis .pad-nya di PADS. SELECT pada pad PS2 melewati satu tombol.',
    'Profil .pad di folder PADS di samping RIPPS2: satu file teks per pad USB, diberi nama sesuai ID-nya (2563_0575.pad), dan masing-masing diperiksa. Pad yang punya profil mengendalikan menu dan bermain di game (Pad Emulator aktif).',
])

T['Filipino'] = ([
    'Hindi maisulat ang %s.', 'Nariyan na ang %s at hindi maitabi, kaya iniwan itong gaya ng dati.',
    'Bilog', 'Ekis', 'Baba', 'Baba sa d-pad',
    'Nahanap ang %04X:%04X. Bitawan ang lahat dito, pati ang mga stick, at maghintay.', 'Nakuha. Bitawan.',
    'L3 (pindutin ang kaliwang stick)', 'Kaliwa sa d-pad', 'Walang na-set up, kaya walang file na naisulat.',
    'Isaksak ang USB pad na gusto mong i-set up. Kung nakasaksak na, hugutin at isaksak ulit. Pagkatapos pindutin nang isang beses ang kahit anong button nito.',
    'Pindutin ang %s sa USB pad at diinan.', 'Itulak ang %s at hawakan.', 'R3 (pindutin ang kanang stick)', 'Kanan sa d-pad',
    'I-save', 'Na-save bilang %s. Kontrolado na ng pad ang menu, at naglalaro ito sa mga laro kapag naka-on ang Pad Emulator.',
    'Laktawan', 'Parisukat', 'Hindi pa mailarawan ang pad na ito sa isang .pad (%s), kaya walang file na naisulat.',
    'Tatsulok', 'Subukan. Lumalabas dito ang hawak mo:', 'Taas', 'Taas sa d-pad',
    'ang kaliwang stick pababa', 'ang kaliwang stick pakanan', 'ang kanang stick pababa', 'ang kanang stick pakanan',
], [
    'Mag-set Up ng USB Pad',
    'Isaksak ang USB pad na hindi kilala ng RIPPS2, pindutin ang bawat button na hinihingi nito, at isusulat ng RIPPS2 ang .pad nito sa PADS. Nilalaktawan ng SELECT sa PS2 pad mo ang isang button.',
    'Ang mga .pad profile sa PADS folder katabi ng RIPPS2: isang text file bawat USB pad, pinangalanan ayon sa ID nito (2563_0575.pad), at sinuri ang bawat isa. Kontrolado ng pad na may profile ang menu at naglalaro ito sa mga laro (naka-on ang Pad Emulator).',
])

T['Cebuano'] = ([
    'Dili masulat ang %s.', 'Anaa na ang %s ug dili maisalikway, busa gibilin kini sama sa una.',
    'Lingin', 'Ekis', 'Ubos', 'Ubos sa d-pad',
    'Nakit-an ang %04X:%04X. Buhii ang tanan niini, apil ang mga stick, ug paghulat.', 'Nakuha. Buhii.',
    'L3 (pislita ang wala nga stick)', 'Wala sa d-pad', 'Walay na-set up, busa walay file nga nasulat.',
    'Isaksak ang USB pad nga gusto nimong i-set up. Kung nakasaksak na, ibton ug isaksak pag-usab. Dayon pislita kausa ang bisan unsang button niini.',
    'Pislita ang %s sa USB pad ug kupti.', 'Iduso ang %s ug kupti.', 'R3 (pislita ang tuo nga stick)', 'Tuo sa d-pad',
    'I-save', 'Na-save isip %s. Ang pad na ang nagdumala sa menu, ug modula kini sa mga dula kung naka-on ang Pad Emulator.',
    'Laktawi', 'Kwadrado', 'Kini nga pad dili pa mahulagway sa usa ka .pad (%s), busa walay file nga nasulat.',
    'Trianggulo', 'Sulayi. Ang imong gikuptan makita dinhi:', 'Taas', 'Taas sa d-pad',
    'ang wala nga stick paubos', 'ang wala nga stick pakatuo', 'ang tuo nga stick paubos', 'ang tuo nga stick pakatuo',
], [
    'I-set Up ang USB Pad',
    'Isaksak ang USB pad nga wala mailhi sa RIPPS2, pislita ang matag button nga gipangayo niini, ug isulat sa RIPPS2 ang .pad niini sa PADS. Ang SELECT sa imong PS2 pad molaktaw og usa ka button.',
    'Ang mga .pad profile sa PADS folder tupad sa RIPPS2: usa ka text file matag USB pad, ginganlan sumala sa ID niini (2563_0575.pad), ug gisusi ang matag usa. Ang pad nga adunay profile magdumala sa menu ug modula sa mga dula (naka-on ang Pad Emulator).',
])

write(T)
