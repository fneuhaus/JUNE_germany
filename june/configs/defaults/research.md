# Infection parameters





### JUNE/configs/defaults/distributors/hospital_distributor.yaml

Aktuell freie Intensivbetten pro Bundesland:

- [source](https://www.intensivregister.de/#/aktuelle-lage/laendertabelle)

Patienten pro Mediziner:

- [source](https://www.bundesgesundheitsministerium.de/personaluntergrenzen.html?r=artikellink)
- Intensivmedizin: 2 Patienten pro Pflegekraft Tagsüber, 3 Patienten Nachts
- Innere Medizin: 10 Patienten Tags, 22 Nachts


### household distribution
- no changes



### school distribution
- Aktuell sind die meisten Klassen nicht im Präsenzunterricht
- Schüler pro Lehrer letzter Stand: 2018
- ca 14 Schüler pro Lehrer
- [source](https://www.deutschlandinzahlen.de/tab/deutschland/bildung/schule/allgemeinbildende/schueler-je-lehrer-allgemeinbildende-schulen)
- KMK (Kulturministerkonferenz) seit 2018 keine neuen Zahlen

	

### worker distribution TODO
- 5.57 Millionen Menschen im Gesundheitssektor
- - 1.112.983 Krankenschwestern/-pfleger
- - [source](https://de.statista.com/statistik/daten/studie/243449/umfrage/anzahl-der-beschaeftigten-krankenschwestern-und-hebammen-in-deutschland/#:~:text=Am%2031.,Hebammen%20und%20Rettungsdienstler%20in%20Deutschland.)
- - 402100 berufstätige Ärzte
- - [source](https://de.statista.com/themen/576/aerzte/)
- Verhältnis Krankenpfleger / Arzt: 73,4602% Krankenpfleger, 26,54% Ärzte
- 54.5% männliche Ärzte, 20% Männer Krankenpfleger
- - [source Pfleger](https://de.statista.com/statistik/daten/studie/1029877/umfrage/verteilung-von-pflegekraefte-in-deutschland-nach-pflegeart-und-geschlecht/)
- - [source Ärzte](https://de.statista.com/statistik/daten/studie/553309/umfrage/verteilung-von-krankenhausaerzten-in-deutschland-nach-geschlecht/)

- 796.489 Angestellte in Pflegeheimen
- - [source](https://de.statista.com/statistik/daten/studie/412574/umfrage/pflegeheime-anzahl-des-personals-nach-taetigkeitsbereich/#:~:text=Die%20Statistik%20zeigt%20die%20Anzahl,der%20Gesch%C3%A4ftsf%C3%BChrung%20deutscher%20Pflegeheime%20t%C3%A4tig.)
- zusammen: 2.311.572: 2,78436%

- ABER andere Quelle sagt insgesamt 5.57 Millionen angestellte im gesamten Gesundheitssektor (benutzte Werte)
- - [source](https://www.bundesgesundheitsministerium.de/themen/gesundheitswesen/gesundheitswirtschaft/gesundheitswirtschaft-als-jobmotor.html#:~:text=Im%20Gesundheitswesen%20arbeiten%20derzeit%205,um%201%2C6%20Millionen%20zugenommen.)
- 75.6% Frauenanteil
- - [source](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Gesundheit/Gesundheitspersonal/_inhalt.html)

	
- 782.613 Lehrkräfte an deutschen Schulen
- - [source](https://de.statista.com/statistik/daten/studie/162263/umfrage/anzahl-der-lehrkraefte-nach-schularten/#:~:text=Im%20Schuljahr%202019%2F2020%20arbeiteten,782.613%20Lehrkr%C3%A4fte%20an%20allgemeinbildenden%20Schulen.)
- - ~0.94 %
- - davon 234.513 an Grundschulen ~30%
- 682.942 Fachkräfte Kinderbetreuung
- - [source](https://de.statista.com/statistik/daten/studie/1011406/umfrage/fachkraefte-in-der-kinderbetreuung-in-deutschland/#:~:text=M%C3%A4rz%202020%20wurden%20bundesweit%20knapp,in%20Einrichtungen%20der%20Kindertagesbetreuung%20t%C3%A4tig.)
- - 0,822 %
- 48.547 Professoren
- - [source](https://de.statista.com/statistik/daten/studie/160365/umfrage/professoren-und-professorinnen-an-deutschen-hochschulen/#:~:text=Die%20Statistik%20zeigt%20die%20Anzahl,Professoren%20und%2012.408%20hauptberufliche%20Professorinnen.)
- - 0,05848 %
- Gesamt: 1,82378 %


### Groups
#### leisure/cinemas
- ca 105.435.400 Kinobesucher 2019
- - [source](https://de.statista.com/themen/48/kino/#:~:text=Rund%205%2C27%20Millionen%20Deutsche,pro%20Einwohner%20in%20Deutschland%20gez%C3%A4hlt.)

### HomeOffice
- 25% im Homeoffice beschäftigt Stand 8.12.20
- - [source](https://www.bitkom.org/Presse/Presseinformation/Mehr-als-10-Millionen-arbeiten-ausschliesslich-im-Homeoffice#:~:text=3%2C2%20Millionen%20(8%20Prozent,6%2C3%20Millionen)%20teilweise.)

### groups/households
- same sex couple ratio
- - Anzahl verheirateter homosexueller Paare: 58.072
- - Entspricht 0,15274 %
- - - [source](https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Eheschliessungen-Ehescheidungen-Lebenspartnerschaften/Tabellen/eheschliessungen-paarkonstellation.html)

### policies/company_closure
- G: Key workers: Autohandel seems to be important


### Effectiveness of Facemask 
- ca 70% weniger Viren übertragen
- - [source](https://msphere.asm.org/content/msph/5/5/e00637-20.full.pdf)

### Infection Transmisson
- "Under baseline assumptions, approximately 59% of all transmission came from asymptomatic transmission: 35% from presymptomatic individuals and 24% from individuals who are never symptomatic"
- Peak infection ~day 4-6
- - [source](https://jamanetwork.com/journals/jamanetworkopen/article-abstract/2774707)
- - Daten von einem Paper, das 07.01.2021 veröffentlich wurde, 07.12.20 wurde das Paper eingereicht
