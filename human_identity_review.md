# Human Identity Review

## Summary
- READY_FOR_HUMAN_ACCEPTANCE: 0
- NEEDS_HUMAN_CHOICE: 60
- INSUFFICIENT_WORLD_DATA: 0
- REJECTED_AS_HALLUCINATION: 0
- Average physical_relation_count: 9.00

## Review Notes
This bundle is intentionally conservative: every pilot card is presented as a human choice between two safe local microimages built from the existing world facts, inspectables, exit geometry and neighbourhood continuity.

## Trzcinowy Próg (`476`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (torf bloto błoto mul muł vs woda rozlewisko topiel).

### Existing Facts
- Existing description: Trzcinowy Próg. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: poludnie, wschod, zachod
- Existing inspectables: torf bloto błoto mul muł, woda rozlewisko topiel, slady ślady tropy

### Proposed Microimage
- anchor_object: torf bloto błoto mul muł [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Błotna Ścieżka Hookri; wschod prowadzi ku Rozlewisko Szarej Wody [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: woda rozlewisko topiel [INSPECTABLE]
- optional_examinable: torf bloto błoto mul muł [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Trzcinowy Próg. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Trzcinowy Próg
- INSPECTABLE: torf bloto błoto mul muł, woda rozlewisko topiel, slady ślady tropy
- EXIT_GEOMETRY: poludnie, wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Błotna Ścieżka Hookri, wschod:Rozlewisko Szarej Wody, poludnie:Czarna Woda
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Trzcinowy Próg', 'secondary_details': ['torf bloto błoto mul muł', 'woda rozlewisko topiel', 'slady ślady tropy', 'Trzcinowy Próg'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Błotna Ścieżka Hookri (bagienny) -> Błotna Ścieżka Hookri. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- wschod: Rozlewisko Szarej Wody (bagienny) -> Rozlewisko Szarej Wody. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody bagienny
- Trial description: Na torf bloto błoto mul muł widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Na mchu widać ślady butów.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.152
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody bagienny
- Trial description: Na skraju lasu rosną młode olsze. Na woda rozlewisko topiel widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Ścieżka otwiera się między kępami trawy.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.257
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Rozlewisko Szarej Wody (`477`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamienie krag krąg oltarz ołtarz vs trzciny sitowie zielsko).

### Existing Facts
- Existing description: Rozlewisko Szarej Wody. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: poludniowy-wschod, zachod
- Existing inspectables: trzciny sitowie zielsko, groble kladka kładka deski, kamienie krag krąg oltarz ołtarz

### Proposed Microimage
- anchor_object: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Trzcinowy Próg; poludniowy-wschod prowadzi ku Sucha Kępa pod Wierzbą [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: trzciny sitowie zielsko [INSPECTABLE]
- optional_examinable: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Rozlewisko Szarej Wody. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Rozlewisko Szarej Wody
- INSPECTABLE: trzciny sitowie zielsko, groble kladka kładka deski, kamienie krag krąg oltarz ołtarz
- EXIT_GEOMETRY: poludniowy-wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Trzcinowy Próg, poludniowy-wschod:Sucha Kępa pod Wierzbą
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Rozlewisko Szarej Wody', 'secondary_details': ['trzciny sitowie zielsko', 'groble kladka kładka deski', 'kamienie krag krąg oltarz ołtarz', 'Rozlewisko Szarej Wody'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Trzcinowy Próg (bagienny) -> Trzcinowy Próg. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- poludniowy-wschod: Sucha Kępa pod Wierzbą (bagienny) -> Sucha Kępa pod Wierzbą. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody bagienny
- Trial description: Na kamienie krag krąg oltarz ołtarz widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Sitowie zasłania niski rów z wodą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.006
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody bagienny
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody trzciny sitowie zielsko jest wyszlifowane, starte albo nadkruszone, a ruch wozów i stałe przejazdy zwęża dojście. Sitowie zasłania niski rów z wodą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.011
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Sucha Kępa pod Wierzbą (`478`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (wierzby drzewa korzenie vs woda rozlewisko topiel).

### Existing Facts
- Existing description: Sucha Kępa pod Wierzbą. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: polnocny-wschod, polnocny-zachod, wschod
- Existing inspectables: woda rozlewisko topiel, wierzby drzewa korzenie, mgla mgła opar opary

### Proposed Microimage
- anchor_object: wierzby drzewa korzenie [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na skraju roślinności lub pola [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wyznacza pieszy przejście między roślinnością [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnocny-zachod prowadzi ku Rozlewisko Szarej Wody; wschod prowadzi ku Stara Grobla [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: woda rozlewisko topiel [INSPECTABLE]
- optional_examinable: wierzby drzewa korzenie [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Sucha Kępa pod Wierzbą. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Sucha Kępa pod Wierzbą
- INSPECTABLE: woda rozlewisko topiel, wierzby drzewa korzenie, mgla mgła opar opary
- EXIT_GEOMETRY: polnocny-wschod, polnocny-zachod, wschod
- NEIGHBOUR_CONTINUITY: polnocny-zachod:Rozlewisko Szarej Wody, wschod:Stara Grobla, polnocny-wschod:Martwy Las
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Sucha Kępa pod Wierzbą', 'secondary_details': ['woda rozlewisko topiel', 'wierzby drzewa korzenie', 'mgla mgła opar opary', 'Sucha Kępa pod Wierzbą'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnocny-zachod: Rozlewisko Szarej Wody (bagienny) -> Rozlewisko Szarej Wody. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- wschod: Stara Grobla (bagienny) -> Stara Grobla. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na skraju roślinności lub pola
- Trial description: Brzegi rowu są rozmiękłe i pękają pod butem. Przy skraju roślinności lub pola wierzby drzewa korzenie jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście. Wśród sitowia słychać plusk i komary.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.120
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Łąka przechodzi w niższy pas traw. W ścieżce widać świeże koleiny. Przy dolnej krawędzi terenu albo przy brzegu wody woda rozlewisko topiel jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście. Przy skraju stoją połamane źdźbła.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.166
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Stara Grobla (`479`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (torf bloto błoto mul muł vs groble kladka kładka deski).

### Existing Facts
- Existing description: Stara Grobla. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: poludnie, poludniowy-wschod, zachod
- Existing inspectables: groble kladka kładka deski, slady ślady tropy, torf bloto błoto mul muł

### Proposed Microimage
- anchor_object: torf bloto błoto mul muł [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Sucha Kępa pod Wierzbą; poludnie prowadzi ku Powalone Drzewo nad Topielą [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: groble kladka kładka deski [INSPECTABLE]
- optional_examinable: torf bloto błoto mul muł [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Stara Grobla. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Stara Grobla
- INSPECTABLE: groble kladka kładka deski, slady ślady tropy, torf bloto błoto mul muł
- EXIT_GEOMETRY: poludnie, poludniowy-wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Sucha Kępa pod Wierzbą, poludnie:Powalone Drzewo nad Topielą, poludniowy-wschod:Martwe Wierzby
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Stara Grobla', 'secondary_details': ['groble kladka kładka deski', 'slady ślady tropy', 'torf bloto błoto mul muł', 'Stara Grobla'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Sucha Kępa pod Wierzbą (bagienny) -> Sucha Kępa pod Wierzbą. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- poludnie: Powalone Drzewo nad Topielą (bagienny) -> Powalone Drzewo nad Topielą. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Przejście
- Trial description: Na torf bloto błoto mul muł widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Na mchu widać ślady butów.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.152
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście
- Trial description: Na groble kladka kładka deski widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Na mchu widać ślady butów.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.153
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Powalone Drzewo nad Topielą (`480`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamienie krag krąg oltarz ołtarz vs trzciny sitowie zielsko).

### Existing Facts
- Existing description: Powalone Drzewo nad Topielą. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: polnoc, poludnie
- Existing inspectables: wierzby drzewa korzenie, kamienie krag krąg oltarz ołtarz, trzciny sitowie zielsko

### Proposed Microimage
- anchor_object: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Stara Grobla; poludnie prowadzi ku Grzęzawisko Cichych Bąbli [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: trzciny sitowie zielsko [INSPECTABLE]
- optional_examinable: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Powalone Drzewo nad Topielą. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Powalone Drzewo nad Topielą
- INSPECTABLE: wierzby drzewa korzenie, kamienie krag krąg oltarz ołtarz, trzciny sitowie zielsko
- EXIT_GEOMETRY: polnoc, poludnie
- NEIGHBOUR_CONTINUITY: polnoc:Stara Grobla, poludnie:Grzęzawisko Cichych Bąbli
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Powalone Drzewo nad Topielą', 'secondary_details': ['wierzby drzewa korzenie', 'kamienie krag krąg oltarz ołtarz', 'trzciny sitowie zielsko', 'Powalone Drzewo nad Topielą'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Stara Grobla (bagienny) -> Stara Grobla. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- poludnie: Grzęzawisko Cichych Bąbli (bagienny) -> Grzęzawisko Cichych Bąbli. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Brzegi rowu są rozmiękłe i pękają pod butem. Na kępie ziemia jest jeszcze twarda. Przy dolnej krawędzi terenu albo przy brzegu wody kamienie krag krąg oltarz ołtarz jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.177
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Na trzciny sitowie zielsko widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Na mchu widać ślady butów.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.047
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Grzęzawisko Cichych Bąbli (`481`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (woda rozlewisko topiel vs mgla mgła opar opary).

### Existing Facts
- Existing description: Grzęzawisko Cichych Bąbli. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: polnoc, zachod
- Existing inspectables: slady ślady tropy, mgla mgła opar opary, woda rozlewisko topiel

### Proposed Microimage
- anchor_object: woda rozlewisko topiel [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Powalone Drzewo nad Topielą; zachod prowadzi ku Czarna Woda [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: mgla mgła opar opary [INSPECTABLE]
- optional_examinable: woda rozlewisko topiel [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Grzęzawisko Cichych Bąbli. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Grzęzawisko Cichych Bąbli
- INSPECTABLE: slady ślady tropy, mgla mgła opar opary, woda rozlewisko topiel
- EXIT_GEOMETRY: polnoc, zachod
- NEIGHBOUR_CONTINUITY: polnoc:Powalone Drzewo nad Topielą, zachod:Czarna Woda
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Grzęzawisko Cichych Bąbli', 'secondary_details': ['slady ślady tropy', 'mgla mgła opar opary', 'woda rozlewisko topiel', 'Grzęzawisko Cichych Bąbli'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Powalone Drzewo nad Topielą (bagienny) -> Powalone Drzewo nad Topielą. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- zachod: Czarna Woda (bagienny) -> Czarna Woda. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Chlupot i przejście
- Trial description: Na woda rozlewisko topiel widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Na mchu widać ślady butów.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.199
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Chlupot i przejście
- Trial description: Na mgla mgła opar opary widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Na mchu widać ślady butów.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.229
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Czarna Woda (`482`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamienie krag krąg oltarz ołtarz vs torf bloto błoto mul muł).

### Existing Facts
- Existing description: Czarna Woda. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: polnoc, poludniowy-zachod, wschod
- Existing inspectables: kamienie krag krąg oltarz ołtarz, torf bloto błoto mul muł, groble kladka kładka deski

### Proposed Microimage
- anchor_object: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Grzęzawisko Cichych Bąbli; poludniowy-zachod prowadzi ku Mglista Polana [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: torf bloto błoto mul muł [INSPECTABLE]
- optional_examinable: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Czarna Woda. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Czarna Woda
- INSPECTABLE: kamienie krag krąg oltarz ołtarz, torf bloto błoto mul muł, groble kladka kładka deski
- EXIT_GEOMETRY: polnoc, poludniowy-zachod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Grzęzawisko Cichych Bąbli, poludniowy-zachod:Mglista Polana, polnoc:Trzcinowy Próg
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Czarna Woda', 'secondary_details': ['kamienie krag krąg oltarz ołtarz', 'torf bloto błoto mul muł', 'groble kladka kładka deski', 'Czarna Woda'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Grzęzawisko Cichych Bąbli (bagienny) -> Grzęzawisko Cichych Bąbli. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- poludniowy-zachod: Mglista Polana (bagienny) -> Mglista Polana. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Pnie stoją gęsto i zasłaniają drogę. Na kamienie krag krąg oltarz ołtarz widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Przy korzeniach leży połamana gałąź. Między pniami widać wąski przesmyk.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.073
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Łąka przechodzi w niższy pas traw. W ścieżce widać świeże koleiny. Na torf bloto błoto mul muł widać wyszlifowane, starte albo nadkruszone; woda i korzenie trzymają przejście w miejscu. Przy skraju stoją połamane źdźbła.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.069
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Mglista Polana (`483`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (trzciny sitowie zielsko vs wierzby drzewa korzenie).

### Existing Facts
- Existing description: Mglista Polana. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: polnocny-wschod, zachod
- Existing inspectables: mgla mgła opar opary, trzciny sitowie zielsko, wierzby drzewa korzenie

### Proposed Microimage
- anchor_object: trzciny sitowie zielsko [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na skraju roślinności lub pola [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wyznacza pieszy przejście między roślinnością [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnocny-wschod prowadzi ku Czarna Woda; zachod prowadzi ku Martwy Las [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: wierzby drzewa korzenie [INSPECTABLE]
- optional_examinable: trzciny sitowie zielsko [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Mglista Polana. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Mglista Polana
- INSPECTABLE: mgla mgła opar opary, trzciny sitowie zielsko, wierzby drzewa korzenie
- EXIT_GEOMETRY: polnocny-wschod, zachod
- NEIGHBOUR_CONTINUITY: polnocny-wschod:Czarna Woda, zachod:Martwy Las
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Mglista Polana', 'secondary_details': ['mgla mgła opar opary', 'trzciny sitowie zielsko', 'wierzby drzewa korzenie', 'Mglista Polana'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnocny-wschod: Czarna Woda (bagienny) -> Czarna Woda. Powietrze pachnie gnijącą trzciną, zimną wodą i drewnem, które dawno przestało pamiętać ogień. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- zachod: Martwy Las (bagienny) -> Martwy Las. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na skraju roślinności lub pola
- Trial description: Przy skraju roślinności lub pola trzciny sitowie zielsko jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście. Sitowie zasłania niski rów z wodą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.150
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na skraju roślinności lub pola
- Trial description: Brzegi rowu są rozmiękłe i pękają pod butem. Na kępie ziemia jest jeszcze twarda. Przy skraju roślinności lub pola wierzby drzewa korzenie jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.064
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Martwy Las (`484`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (torf bloto błoto mul muł vs woda rozlewisko topiel).

### Existing Facts
- Existing description: Martwy Las. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: poludnie, poludniowy-zachod, wschod
- Existing inspectables: torf bloto błoto mul muł, woda rozlewisko topiel, slady ślady tropy

### Proposed Microimage
- anchor_object: torf bloto błoto mul muł [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Mglista Polana; poludnie prowadzi ku Wyspa Torfowa [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: woda rozlewisko topiel [INSPECTABLE]
- optional_examinable: torf bloto błoto mul muł [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Martwy Las. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Martwy Las
- INSPECTABLE: torf bloto błoto mul muł, woda rozlewisko topiel, slady ślady tropy
- EXIT_GEOMETRY: poludnie, poludniowy-zachod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Mglista Polana, poludnie:Wyspa Torfowa, poludniowy-zachod:Sucha Kępa pod Wierzbą
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Martwy Las', 'secondary_details': ['torf bloto błoto mul muł', 'woda rozlewisko topiel', 'slady ślady tropy', 'Martwy Las'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Mglista Polana (bagienny) -> Mglista Polana. Nie ma tu prawdziwej ciszy. Są tylko pluski, szelesty, dalekie bulgotanie i nagłe milczenie ptaków. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- poludnie: Wyspa Torfowa (bagienny) -> Wyspa Torfowa. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody bagienny
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody torf bloto błoto mul muł jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście. Sitowie zasłania niski rów z wodą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.071
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody bagienny
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody woda rozlewisko topiel jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zwęża dojście. Sitowie zasłania niski rów z wodą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.090
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Wyspa Torfowa (`485`)
- Area: `Bagna_Hookri`
- Family: `natural`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamienie krag krąg oltarz ołtarz vs trzciny sitowie zielsko).

### Existing Facts
- Existing description: Wyspa Torfowa. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- Actual exits: polnoc, poludnie, wschod
- Existing inspectables: trzciny sitowie zielsko, groble kladka kładka deski, kamienie krag krąg oltarz ołtarz

### Proposed Microimage
- anchor_object: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Martwy Las; wschod prowadzi ku Zarośla Ostrych Trzcin [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: trzciny sitowie zielsko [INSPECTABLE]
- optional_examinable: kamienie krag krąg oltarz ołtarz [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Wyspa Torfowa. Mgła nie leży tu nad wodą, lecz zdaje się wyrastać z niej powoli, jak oddech czegoś ukrytego pod torfem. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- LOCATION_NAME: Wyspa Torfowa
- INSPECTABLE: trzciny sitowie zielsko, groble kladka kładka deski, kamienie krag krąg oltarz ołtarz
- EXIT_GEOMETRY: polnoc, poludnie, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Martwy Las, wschod:Zarośla Ostrych Trzcin, poludnie:Zarośnięty Brzeg
- REGIONAL_MATERIAL: torf, trzcina, drewno
- REGIONAL_PROCESS: zbiory i przeprawy
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Wyspa Torfowa', 'secondary_details': ['trzciny sitowie zielsko', 'groble kladka kładka deski', 'kamienie krag krąg oltarz ołtarz', 'Wyspa Torfowa'], 'historical_layer': 'torf, trzcina i kładki'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Martwy Las (bagienny) -> Martwy Las. Bagno nie grozi otwarcie. Ono czeka, aż człowiek sam pomyli ścieżkę z powierzchnią wody. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.
- wschod: Zarośla Ostrych Trzcin (bagienny) -> Zarośla Ostrych Trzcin. Każdy krok brzmi miękko i niepewnie; ziemia ustępuje trochę za łatwo, a potem niechętnie oddaje but. To teren, który nie potrzebuje murów ani straży; sam wybiera, kogo przepuści dalej.

### Variants
#### Variant A
- Trial short: Przejście
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody kamienie krag krąg oltarz ołtarz jest wyszlifowane, starte albo nadkruszone, a ruch wozów i stałe przejazdy zwęża dojście. Sitowie zasłania niski rów z wodą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.010
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście
- Trial description: Brzegi rowu są rozmiękłe i pękają pod butem. Przy dolnej krawędzi terenu albo przy brzegu wody trzciny sitowie zielsko jest wyszlifowane, starte albo nadkruszone, a ruch wozów i stałe przejazdy zwęża dojście. Wśród sitowia słychać plusk i komary.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.098
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Zarośnięta Droga do Karshold (`425`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (drzwi zawiasy belki vs kamien kamień mur mury).

### Existing Facts
- Existing description: Zarośnięta Droga do Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: polnoc, wschod
- Existing inspectables: kamien kamień mur mury, korzenie pnacza pnącza mech, drzwi zawiasy belki

### Proposed Microimage
- anchor_object: drzwi zawiasy belki [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Kamień Dawnej Granicy; polnoc prowadzi ku Głęboka Granica Ostępu [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kamien kamień mur mury [INSPECTABLE]
- optional_examinable: drzwi zawiasy belki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Zarośnięta Droga do Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Zarośnięta Droga do Karshold
- INSPECTABLE: kamien kamień mur mury, korzenie pnacza pnącza mech, drzwi zawiasy belki
- EXIT_GEOMETRY: polnoc, wschod
- NEIGHBOUR_CONTINUITY: wschod:Kamień Dawnej Granicy, polnoc:Głęboka Granica Ostępu
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Zarośnięta Droga do Karshold', 'secondary_details': ['kamien kamień mur mury', 'korzenie pnacza pnącza mech', 'drzwi zawiasy belki', 'Zarośnięta Droga do Karshold'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Kamień Dawnej Granicy (ruinowy) -> Kamień Dawnej Granicy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- polnoc: Głęboka Granica Ostępu (leśny) -> Głęboka Granica Ostępu. Gałęzie, korzenie i ciemne zagłębienia zmuszają do krótszych kroków. Drogę wyznaczają tu nie tablice, lecz pamięć, nacięcia w korze i ostrożność ludzi, którzy wrócili.

### Variants
#### Variant A
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Na drzwi zawiasy belki widać wydeptane i przeorane koleinami; drzwi zawiasy belki pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.111
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W osi przejazdu albo przy zwężeniu ruin
- Trial description: Na kamien kamień mur mury widać wydeptane i przeorane koleinami; kamien kamień mur mury pozwala zobaczyć pusty otwór. Urwany bieg schodów kończy się w gruzie. Po ogniu zostały czarne smugi na kamieniu. Na progu widać wtórnie wmurowany kamień.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.127
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Kamień Dawnej Granicy (`426`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kosci kości szczatki szczątki vs popiol popiół sadza ogien ogień).

### Existing Facts
- Existing description: Kamień Dawnej Granicy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: poludnie, zachod
- Existing inspectables: popiol popiół sadza ogien ogień, kosci kości szczatki szczątki, slady ślady tropy

### Proposed Microimage
- anchor_object: kosci kości szczatki szczątki [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Zarośnięta Droga do Karshold; poludnie prowadzi ku Przewrócony Obelisk [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: popiol popiół sadza ogien ogień [INSPECTABLE]
- optional_examinable: kosci kości szczatki szczątki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Kamień Dawnej Granicy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Kamień Dawnej Granicy
- INSPECTABLE: popiol popiół sadza ogien ogień, kosci kości szczatki szczątki, slady ślady tropy
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Zarośnięta Droga do Karshold, poludnie:Przewrócony Obelisk
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Kamień Dawnej Granicy', 'secondary_details': ['popiol popiół sadza ogien ogień', 'kosci kości szczatki szczątki', 'slady ślady tropy', 'Kamień Dawnej Granicy'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Zarośnięta Droga do Karshold (ruinowy) -> Zarośnięta Droga do Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- poludnie: Przewrócony Obelisk (ruinowy) -> Przewrócony Obelisk. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przejście Kamień Dawnej Granicy
- Trial description: Na kosci kości szczatki szczątki widać wyszlifowane, starte albo nadkruszone; kosci kości szczatki szczątki pozwala zobaczyć pusty otwór. U podstawy ściany widać odsłonięty fundament. Sadza osiadła nad dawnym paleniskiem.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.101
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście Kamień Dawnej Granicy
- Trial description: Jedna ściana przechodzi w rumowisko. Na popiol popiół sadza ogien ogień widać wyszlifowane, starte albo nadkruszone; popiol popiół sadza ogien ogień pozwala zobaczyć pusty otwór. Pod murem leży wypalona glina i węgiel.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.111
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Przewrócony Obelisk (`427`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (drzwi zawiasy belki vs studnia woda wilgoc wilgoć).

### Existing Facts
- Existing description: Przewrócony Obelisk. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: polnoc, wschod
- Existing inspectables: znak herb rzezba rzeźba, drzwi zawiasy belki, studnia woda wilgoc wilgoć

### Proposed Microimage
- anchor_object: drzwi zawiasy belki [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Kamień Dawnej Granicy; wschod prowadzi ku Przedpole Spalonej Bramy [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: studnia woda wilgoc wilgoć [INSPECTABLE]
- optional_examinable: drzwi zawiasy belki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Przewrócony Obelisk. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Przewrócony Obelisk
- INSPECTABLE: znak herb rzezba rzeźba, drzwi zawiasy belki, studnia woda wilgoc wilgoć
- EXIT_GEOMETRY: polnoc, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Kamień Dawnej Granicy, wschod:Przedpole Spalonej Bramy
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Przewrócony Obelisk', 'secondary_details': ['znak herb rzezba rzeźba', 'drzwi zawiasy belki', 'studnia woda wilgoc wilgoć', 'Przewrócony Obelisk'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Kamień Dawnej Granicy (ruinowy) -> Kamień Dawnej Granicy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- wschod: Przedpole Spalonej Bramy (ruinowy) -> Przedpole Spalonej Bramy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Przy wejściu lub przy przejeździe drzwi zawiasy belki jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty odsłania starszą warstwę. Została tylko niższa warstwa i wyrównany ślad po belce. Na wyższym progu widać wyryty znak po dawnym mocowaniu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.102
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Na dolnej krawędzi terenu albo przy brzegu wody ruin
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody studnia woda wilgoc wilgoć jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty odsłania starszą warstwę. Urwany bieg schodów kończy się w gruzie. Po ogniu zostały czarne smugi na kamieniu. Na progu widać wtórnie wmurowany kamień.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.095
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Przedpole Spalonej Bramy (`428`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamien kamień mur mury vs korzenie pnacza pnącza mech).

### Existing Facts
- Existing description: Przedpole Spalonej Bramy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: poludnie, zachod
- Existing inspectables: korzenie pnacza pnącza mech, slady ślady tropy, kamien kamień mur mury

### Proposed Microimage
- anchor_object: kamien kamień mur mury [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Przewrócony Obelisk; poludnie prowadzi ku Zawalona Brama Karshold [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: korzenie pnacza pnącza mech [INSPECTABLE]
- optional_examinable: kamien kamień mur mury [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Przedpole Spalonej Bramy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Przedpole Spalonej Bramy
- INSPECTABLE: korzenie pnacza pnącza mech, slady ślady tropy, kamien kamień mur mury
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Przewrócony Obelisk, poludnie:Zawalona Brama Karshold
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Przedpole Spalonej Bramy', 'secondary_details': ['korzenie pnacza pnącza mech', 'slady ślady tropy', 'kamien kamień mur mury', 'Przedpole Spalonej Bramy'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Przewrócony Obelisk (ruinowy) -> Przewrócony Obelisk. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- poludnie: Zawalona Brama Karshold (ruinowy) -> Zawalona Brama Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Strop zawalił się do środka i przygniótł izbę. Na kamien kamień mur mury widać wyszlifowane, starte albo nadkruszone; kamien kamień mur mury pozwala zobaczyć pusty otwór. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.078
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Na korzenie pnacza pnącza mech widać wyszlifowane, starte albo nadkruszone; korzenie pnacza pnącza mech pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.116
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Zawalona Brama Karshold (`429`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (studnia woda wilgoc wilgoć vs kosci kości szczatki szczątki).

### Existing Facts
- Existing description: Zawalona Brama Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: polnoc, wschod
- Existing inspectables: kosci kości szczatki szczątki, studnia woda wilgoc wilgoć, popiol popiół sadza ogien ogień

### Proposed Microimage
- anchor_object: studnia woda wilgoc wilgoć [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Przedpole Spalonej Bramy; wschod prowadzi ku Dziedziniec Popękanych Płyt [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kosci kości szczatki szczątki [INSPECTABLE]
- optional_examinable: studnia woda wilgoc wilgoć [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Zawalona Brama Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Zawalona Brama Karshold
- INSPECTABLE: kosci kości szczatki szczątki, studnia woda wilgoc wilgoć, popiol popiół sadza ogien ogień
- EXIT_GEOMETRY: polnoc, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Przedpole Spalonej Bramy, wschod:Dziedziniec Popękanych Płyt
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Zawalona Brama Karshold', 'secondary_details': ['kosci kości szczatki szczątki', 'studnia woda wilgoc wilgoć', 'popiol popiół sadza ogien ogień', 'Zawalona Brama Karshold'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Przedpole Spalonej Bramy (ruinowy) -> Przedpole Spalonej Bramy. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- wschod: Dziedziniec Popękanych Płyt (ruinowy) -> Dziedziniec Popękanych Płyt. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Jedna ściana przechodzi w rumowisko. Przy wejściu lub przy przejeździe studnia woda wilgoc wilgoć jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty odsłania starszą warstwę. Pod murem leży wypalona glina i węgiel.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.073
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Na kosci kości szczatki szczątki widać wyszlifowane, starte albo nadkruszone; kosci kości szczatki szczątki pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.076
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Dziedziniec Popękanych Płyt (`430`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (drzwi zawiasy belki vs kamien kamień mur mury).

### Existing Facts
- Existing description: Dziedziniec Popękanych Płyt. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: poludnie, zachod
- Existing inspectables: drzwi zawiasy belki, kamien kamień mur mury, znak herb rzezba rzeźba

### Proposed Microimage
- anchor_object: drzwi zawiasy belki [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Zawalona Brama Karshold; poludnie prowadzi ku Strażnica Bez Dachu [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kamien kamień mur mury [INSPECTABLE]
- optional_examinable: drzwi zawiasy belki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Dziedziniec Popękanych Płyt. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Dziedziniec Popękanych Płyt
- INSPECTABLE: drzwi zawiasy belki, kamien kamień mur mury, znak herb rzezba rzeźba
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Zawalona Brama Karshold, poludnie:Strażnica Bez Dachu
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Dziedziniec Popękanych Płyt', 'secondary_details': ['drzwi zawiasy belki', 'kamien kamień mur mury', 'znak herb rzezba rzeźba', 'Dziedziniec Popękanych Płyt'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Zawalona Brama Karshold (ruinowy) -> Zawalona Brama Karshold. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- poludnie: Strażnica Bez Dachu (ruinowy) -> Strażnica Bez Dachu. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przejście Dziedziniec Popękanych Płyt
- Trial description: Przy wejściu lub przy przejeździe drzwi zawiasy belki jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty odsłania starszą warstwę. Za pierwszym rzędem murów leży połamany strop. Pod murem leży wypalona glina i węgiel.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.097
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście Dziedziniec Popękanych Płyt
- Trial description: Przy ścianie, fundamencie albo progu kamien kamień mur mury jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty odsłania starszą warstwę. U podstawy ściany widać odsłonięty fundament. Sadza osiadła nad dawnym paleniskiem.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.097
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Strażnica Bez Dachu (`431`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (korzenie pnacza pnącza mech vs popiol popiół sadza ogien ogień).

### Existing Facts
- Existing description: Strażnica Bez Dachu. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: polnoc, wschod
- Existing inspectables: slady ślady tropy, popiol popiół sadza ogien ogień, korzenie pnacza pnącza mech

### Proposed Microimage
- anchor_object: korzenie pnacza pnącza mech [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Dziedziniec Popękanych Płyt; wschod prowadzi ku Mur Zachodni Ruin [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: popiol popiół sadza ogien ogień [INSPECTABLE]
- optional_examinable: korzenie pnacza pnącza mech [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Strażnica Bez Dachu. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Strażnica Bez Dachu
- INSPECTABLE: slady ślady tropy, popiol popiół sadza ogien ogień, korzenie pnacza pnącza mech
- EXIT_GEOMETRY: polnoc, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Dziedziniec Popękanych Płyt, wschod:Mur Zachodni Ruin
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Strażnica Bez Dachu', 'secondary_details': ['slady ślady tropy', 'popiol popiół sadza ogien ogień', 'korzenie pnacza pnącza mech', 'Strażnica Bez Dachu'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Dziedziniec Popękanych Płyt (ruinowy) -> Dziedziniec Popękanych Płyt. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- wschod: Mur Zachodni Ruin (ruinowy) -> Mur Zachodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przejście Strażnica Bez Dachu
- Trial description: Jedna ściana przechodzi w rumowisko. Na korzenie pnacza pnącza mech widać wyszlifowane, starte albo nadkruszone; korzenie pnacza pnącza mech pozwala zobaczyć pusty otwór. Pod murem leży wypalona glina i węgiel.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.041
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście Strażnica Bez Dachu
- Trial description: Na popiol popiół sadza ogien ogień widać wyszlifowane, starte albo nadkruszone; popiol popiół sadza ogien ogień pozwala zobaczyć pusty otwór. Została tylko niższa warstwa i wyrównany ślad po belce. Na wyższym progu widać wyryty znak po dawnym mocowaniu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.112
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Mur Zachodni Ruin (`432`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (studnia woda wilgoc wilgoć vs kosci kości szczatki szczątki).

### Existing Facts
- Existing description: Mur Zachodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: poludnie, zachod
- Existing inspectables: studnia woda wilgoc wilgoć, znak herb rzezba rzeźba, kosci kości szczatki szczątki

### Proposed Microimage
- anchor_object: studnia woda wilgoc wilgoć [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Strażnica Bez Dachu; poludnie prowadzi ku Mur Wschodni Ruin [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kosci kości szczatki szczątki [INSPECTABLE]
- optional_examinable: studnia woda wilgoc wilgoć [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Mur Zachodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Mur Zachodni Ruin
- INSPECTABLE: studnia woda wilgoc wilgoć, znak herb rzezba rzeźba, kosci kości szczatki szczątki
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Strażnica Bez Dachu, poludnie:Mur Wschodni Ruin
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Mur Zachodni Ruin', 'secondary_details': ['studnia woda wilgoc wilgoć', 'znak herb rzezba rzeźba', 'kosci kości szczatki szczątki', 'Mur Zachodni Ruin'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Strażnica Bez Dachu (ruinowy) -> Strażnica Bez Dachu. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Kamień nosi ślady ognia głębiej niż deszcz zdołał je wypłukać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- poludnie: Mur Wschodni Ruin (ruinowy) -> Mur Wschodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przejście Mur Zachodni Ruin
- Trial description: Na studnia woda wilgoc wilgoć widać wyszlifowane, starte albo nadkruszone; studnia woda wilgoc wilgoć pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.099
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście Mur Zachodni Ruin
- Trial description: Na kosci kości szczatki szczątki widać wyszlifowane, starte albo nadkruszone; kosci kości szczatki szczątki pozwala zobaczyć pusty otwór. Za pierwszym rzędem murów leży połamany strop. Pod murem leży wypalona glina i węgiel.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.074
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Mur Wschodni Ruin (`433`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (drzwi zawiasy belki vs kamien kamień mur mury).

### Existing Facts
- Existing description: Mur Wschodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: polnoc, wschod
- Existing inspectables: kamien kamień mur mury, korzenie pnacza pnącza mech, drzwi zawiasy belki

### Proposed Microimage
- anchor_object: drzwi zawiasy belki [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Mur Zachodni Ruin; wschod prowadzi ku Baszta Kruczych Gniazd [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kamien kamień mur mury [INSPECTABLE]
- optional_examinable: drzwi zawiasy belki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Mur Wschodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Mur Wschodni Ruin
- INSPECTABLE: kamien kamień mur mury, korzenie pnacza pnącza mech, drzwi zawiasy belki
- EXIT_GEOMETRY: polnoc, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Mur Zachodni Ruin, wschod:Baszta Kruczych Gniazd
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Mur Wschodni Ruin', 'secondary_details': ['kamien kamień mur mury', 'korzenie pnacza pnącza mech', 'drzwi zawiasy belki', 'Mur Wschodni Ruin'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Mur Zachodni Ruin (ruinowy) -> Mur Zachodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Każdy krok porusza drobny popiół, zmieszany z ziemią, igliwiem i skruszonym wapnem. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- wschod: Baszta Kruczych Gniazd (ruinowy) -> Baszta Kruczych Gniazd. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Przy wejściu lub przy przejeździe ruin
- Trial description: Na drzwi zawiasy belki widać wyszlifowane, starte albo nadkruszone; drzwi zawiasy belki pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.111
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przy ścianie, fundamencie albo progu ruin
- Trial description: Na kamien kamień mur mury widać wyszlifowane, starte albo nadkruszone; kamien kamień mur mury pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.123
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Baszta Kruczych Gniazd (`434`)
- Area: `Ruiny_Karshold`
- Family: `ruin`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kosci kości szczatki szczątki vs popiol popiół sadza ogien ogień).

### Existing Facts
- Existing description: Baszta Kruczych Gniazd. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- Actual exits: poludnie, zachod
- Existing inspectables: popiol popiół sadza ogien ogień, kosci kości szczatki szczątki, slady ślady tropy

### Proposed Microimage
- anchor_object: kosci kości szczatki szczątki [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Mur Wschodni Ruin; poludnie prowadzi ku Koszary pod Czarnym Stropem [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: popiol popiół sadza ogien ogień [INSPECTABLE]
- optional_examinable: kosci kości szczatki szczątki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Baszta Kruczych Gniazd. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Milczenie Karshold jest inne niż cisza lasu; tutaj brzmi jak rozkaz, którego nikt już nie wykonuje. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- LOCATION_NAME: Baszta Kruczych Gniazd
- INSPECTABLE: popiol popiół sadza ogien ogień, kosci kości szczatki szczątki, slady ślady tropy
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Mur Wschodni Ruin, poludnie:Koszary pod Czarnym Stropem
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: poszukiwanie przejść
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Baszta Kruczych Gniazd', 'secondary_details': ['popiol popiół sadza ogien ogień', 'kosci kości szczatki szczątki', 'slady ślady tropy', 'Baszta Kruczych Gniazd'], 'historical_layer': 'pożar i długie opuszczenie'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Mur Wschodni Ruin (ruinowy) -> Mur Wschodni Ruin. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Ruiny nie są martwe. Są cierpliwe, ciężkie i pełne miejsc, w których coś mogło przetrwać. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.
- poludnie: Koszary pod Czarnym Stropem (ruinowy) -> Koszary pod Czarnym Stropem. Dawna twierdza graniczna spłonęła tu podczas wojny; w murach widać nadpalone kamienie, odłupane blanki i czarny osad. Wiatr przechodzi przez puste okna i szczeliny tak, jakby nadal szukał ludzi, którzy dawno stąd uciekli. Przy ziemi leżą zwęglone belki, a w szczelinach murów trzyma się sadza.

### Variants
#### Variant A
- Trial short: Popiol popiół sadza ogien ogień
- Trial description: Na kosci kości szczatki szczątki widać wyszlifowane, starte albo nadkruszone; kosci kości szczatki szczątki pozwala zobaczyć pusty otwór. Po bokach zostały tylko niskie ściany i belki. W środku leżą dachówki, wapno i kurz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.076
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Popiol popiół sadza ogien ogień
- Trial description: Przy skraju roślinności lub pola popiol popiół sadza ogien ogień jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty odsłania starszą warstwę. Kamienie odsunęły się od fundamentu i zostawiły szparę. W szczelinie widać wilgoć i drobne odłamy zaprawy. Na górnej krawędzi rośnie mech.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.156
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Droga do Pól (`77`)
- Area: `Podgrodzie`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (bloto błoto koleiny vs palisada mur podmurze).

### Existing Facts
- Existing description: Droga do Pól. Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych. Towary, głosy i biegnące dzieci mijają się tu bez chwili przerwy.
- Actual exits: poludniowy-zachod, wschod
- Existing inspectables: bloto błoto koleiny, palisada mur podmurze, ludzie tragarze mieszczanie

### Proposed Microimage
- anchor_object: bloto błoto koleiny [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: wschod prowadzi ku Stary Kamień Mytny; poludniowy-zachod prowadzi ku Niska Łąka [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: palisada mur podmurze [INSPECTABLE]
- optional_examinable: bloto błoto koleiny [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Droga do Pól. Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych. Towary, głosy i biegnące dzieci mijają się tu bez chwili przerwy.
- LOCATION_NAME: Droga do Pól
- INSPECTABLE: bloto błoto koleiny, palisada mur podmurze, ludzie tragarze mieszczanie
- EXIT_GEOMETRY: poludniowy-zachod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Stary Kamień Mytny, poludniowy-zachod:Niska Łąka
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: targ i zaplecze
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Droga do Pól', 'secondary_details': ['bloto błoto koleiny', 'palisada mur podmurze', 'ludzie tragarze mieszczanie', 'Droga do Pól'], 'historical_layer': 'mokre przedmieście i łatane płoty'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Stary Kamień Mytny (przedmiejski) -> Stary Kamień Mytny. Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.
- poludniowy-zachod: Niska Łąka (przedmiejski) -> Niska Łąka. Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych. Od bram miasta dalej słychać stuk kół, nawoływania i psy przy płotach.

### Variants
#### Variant A
- Trial short: W osi przejazdu albo przy zwężeniu
- Trial description: Przy osi przejazdu albo przy zwężeniu bloto błoto koleiny jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Na środku traktu leży rozjechany żwir, a po bokach widać miękki piasek.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.047
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W osi przejazdu albo przy zwężeniu
- Trial description: Przy osi przejazdu albo przy zwężeniu palisada mur podmurze jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.043
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Droga do Haldun (`80`)
- Area: `Haldun`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (koleiny wozy vs domy zagrody).

### Existing Facts
- Existing description: Droga do Haldun wychodzi z podmiejskiego błota i przechodzi w udeptany trakt pomiędzy zagonami. Widać stąd zarówno wieś, jak i wielki ruch wokół niej: wozy, psy, ptaki i ludzi, którzy zawsze gdzieś się spieszą.
- Actual exits: polnoc, poludnie
- Existing inspectables: koleiny wozy, rowy ploty, domy zagrody

### Proposed Microimage
- anchor_object: koleiny wozy [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: przysłania skraj przejścia albo otwiera widok na pole [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: polnoc prowadzi ku Krzyżowy Kamień; poludnie prowadzi ku Pod Bramą Solną [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: domy zagrody [INSPECTABLE]
- optional_examinable: koleiny wozy [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Droga do Haldun wychodzi z podmiejskiego błota i przechodzi w udeptany trakt pomiędzy zagonami. Widać stąd zarówno wieś, jak i wielki ruch wokół niej: wozy, psy, ptaki i ludzi, którzy zawsze gdzieś się spieszą.
- LOCATION_NAME: Droga do Haldun
- INSPECTABLE: koleiny wozy, rowy ploty, domy zagrody
- EXIT_GEOMETRY: polnoc, poludnie
- NEIGHBOUR_CONTINUITY: polnoc:Krzyżowy Kamień, poludnie:Pod Bramą Solną
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Droga do Haldun', 'secondary_details': ['koleiny wozy', 'rowy ploty', 'domy zagrody', 'Droga do Haldun wychodzi z podmiejskiego błota i przechodzi w udeptany trakt pomiędzy zagonami'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Krzyżowy Kamień (wiejski) -> Przy rozstaju stoi głaz z naciętym znakiem i śladami kredy po dawnych oznaczeniach. Miejscowi zostawiają tu informacje, wiązki sznurka i wiadomości, których nie warto wozić dalej niż trzeba.
- poludnie: Pod Bramą Solną (miejski) -> Na ziemi widać kilka świeżych plam błota, jakby ktoś przyszedł tu z drogi spoza murów. W takich miejscach pod bramą solną zwykle brzmi sucho, ale dziś trzyma się naturalnie.

### Variants
#### Variant A
- Trial short: Wydeptane i przeorane koleinami wiejski
- Trial description: Przy osi przejazdu albo przy zwężeniu koleiny wozy jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.024
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Wydeptane i przeorane koleinami wiejski
- Trial description: Przy osi przejazdu albo przy zwężeniu domy zagrody jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.077
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Droga ku Fortecy (`94`)
- Area: `Haldun`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (koleiny błoto vs wozy patrole).

### Existing Facts
- Existing description: Droga ku Fortecy wychodzi z Haldun i prowadzi dalej do wojskowego pasa na północy. Tu kończy się wiejska codzienność, a zaczyna ruch żołnierzy, zapasów i tych, którzy muszą się tłumaczyć z podróży.
- Actual exits: polnoc, zachod
- Existing inspectables: wozy patrole, słup drogowskaz, koleiny błoto

### Proposed Microimage
- anchor_object: koleiny błoto [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnoc prowadzi ku Kapliczka Żniwiarzy; zachod prowadzi ku Zarośnięty Dukt [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: wozy patrole [INSPECTABLE]
- optional_examinable: koleiny błoto [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Droga ku Fortecy wychodzi z Haldun i prowadzi dalej do wojskowego pasa na północy. Tu kończy się wiejska codzienność, a zaczyna ruch żołnierzy, zapasów i tych, którzy muszą się tłumaczyć z podróży.
- LOCATION_NAME: Droga ku Fortecy
- INSPECTABLE: wozy patrole, słup drogowskaz, koleiny błoto
- EXIT_GEOMETRY: polnoc, zachod
- NEIGHBOUR_CONTINUITY: polnoc:Kapliczka Żniwiarzy, zachod:Zarośnięty Dukt
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Droga ku Fortecy', 'secondary_details': ['wozy patrole', 'słup drogowskaz', 'koleiny błoto', 'Droga ku Fortecy wychodzi z Haldun i prowadzi dalej do wojskowego pasa na północy'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Kapliczka Żniwiarzy (wiejski) -> Kapliczka stoi przy drodze do fortecy i przypomina, że żniwa też są rodzajem modlitwy. W niszy palą się świece, a wokół leżą drobne ofiary i sznury paciorków.
- zachod: Zarośnięty Dukt (drogowy) -> Zarośnięty Dukt. Ścieżka jest wąska i kapryśna; miejscami znika pod trawą, żeby wrócić kilka kroków dalej. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.

### Variants
#### Variant A
- Trial short: W osi przejazdu albo przy zwężeniu i wydeptana ziemia
- Trial description: Na koleiny błoto widać wydeptane i przeorane koleinami; ruch musi zwolnić przy osi przejazdu albo przy zwężeniu. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.015
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W osi przejazdu albo przy zwężeniu i wydeptana ziemia
- Trial description: Na wozy patrole widać wydeptane i przeorane koleinami; ruch musi zwolnić przy osi przejazdu albo przy zwężeniu. Kamienie wystają z nawierzchni i tłuką koła. Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.030
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Ścieżka Ku Puszczy (`108`)
- Area: `Osada_Mysliwych`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (skory skóry futra vs lowcy łowcy mysliwi myśliwi).

### Existing Facts
- Existing description: Ścieżka Ku Puszczy. Skóry wiszą na żerdziach. Jedne pachną dymem, inne krwią i mokrym psem. Od bram miasta dalej słychać stuk kół, nawoływania i psy przy płotach.
- Actual exits: polnocny-zachod, wschod
- Existing inspectables: skory skóry futra, slady ślady tropy, lowcy łowcy mysliwi myśliwi

### Proposed Microimage
- anchor_object: skory skóry futra [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnocny-zachod prowadzi ku Skład Wnyków; wschod prowadzi ku Ostatni Znak Toporem [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: lowcy łowcy mysliwi myśliwi [INSPECTABLE]
- optional_examinable: skory skóry futra [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Ścieżka Ku Puszczy. Skóry wiszą na żerdziach. Jedne pachną dymem, inne krwią i mokrym psem. Od bram miasta dalej słychać stuk kół, nawoływania i psy przy płotach.
- LOCATION_NAME: Ścieżka Ku Puszczy
- INSPECTABLE: skory skóry futra, slady ślady tropy, lowcy łowcy mysliwi myśliwi
- EXIT_GEOMETRY: polnocny-zachod, wschod
- NEIGHBOUR_CONTINUITY: polnocny-zachod:Skład Wnyków, wschod:Ostatni Znak Toporem
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: obróbka trofeów
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Ścieżka Ku Puszczy', 'secondary_details': ['skory skóry futra', 'slady ślady tropy', 'lowcy łowcy mysliwi myśliwi', 'Ścieżka Ku Puszczy'], 'historical_layer': 'dym, skóry i tropy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnocny-zachod: Skład Wnyków (leśny) -> Skład Wnyków. Skóry wiszą na żerdziach. Jedne pachną dymem, inne krwią i mokrym psem. Towary, głosy i biegnące dzieci mijają się tu bez chwili przerwy.
- wschod: Ostatni Znak Toporem (leśny) -> Ostatni Znak Toporem. Skóry wiszą na żerdziach. Jedne pachną dymem, inne krwią i mokrym psem. Skróty znają głównie ci, którzy codziennie mijają ten sam kamień milowy.

### Variants
#### Variant A
- Trial short: W lokalnym punkcie przejścia
- Trial description: Przy lokalnym punkcie przejścia skory skóry futra jest wyszlifowane, starte albo nadkruszone, a ruch wozów i stałe przejazdy zmienia przejazd. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.057
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W lokalnym punkcie przejścia
- Trial description: Przy miedzy pozostaje wąski przejazd. Na lowcy łowcy mysliwi myśliwi widać wyszlifowane, starte albo nadkruszone; ruch musi zwolnić przy lokalnym punkcie przejścia. Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.064
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Trakt Przy Murze (`20`)
- Area: `Centrum_Twierdza`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (mur vs wozy koleiny).

### Existing Facts
- Existing description: Trakt biegnie wzdłuż muru tak blisko, że idący mimowolnie ściszają głos. Kamienie są tu wyszlifowane przez buty patroli i obręcze wozów.
- Actual exits: polnoc, poludnie, wschod
- Existing inspectables: mur, slady ślady tropy, wozy koleiny

### Proposed Microimage
- anchor_object: mur [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Brama Dymnych Chorągwi; wschod prowadzi ku Studnia Miejska [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: wozy koleiny [INSPECTABLE]
- optional_examinable: mur [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Trakt biegnie wzdłuż muru tak blisko, że idący mimowolnie ściszają głos. Kamienie są tu wyszlifowane przez buty patroli i obręcze wozów.
- LOCATION_NAME: Trakt Przy Murze
- INSPECTABLE: mur, slady ślady tropy, wozy koleiny
- EXIT_GEOMETRY: polnoc, poludnie, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Brama Dymnych Chorągwi, wschod:Studnia Miejska, poludnie:Studnia Żołnierska
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: handel i warta
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Trakt Przy Murze', 'secondary_details': ['mur', 'slady ślady tropy', 'wozy koleiny', 'Trakt biegnie wzdłuż muru tak blisko, że idący mimowolnie ściszają głos'], 'historical_layer': 'warstwy murów i ciągłe naprawy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Brama Dymnych Chorągwi (miejski) -> Wąska brama wciska trakt między kamienny mur i czarne belki strażnicy. Na hakach wiszą mokre płaszcze wartowników, a w koleinach stoi brunatna woda. Od krat, łańcuchów i okutych wrót ciągnie zapach wilgotnego żelaza.
- wschod: Studnia Miejska (miejski) -> Studnia stoi między domami jak obowiązek, z którym nikt nie dyskutuje. Przychodzą tu wszyscy, od straży po dzieci, a kamień wokół cembrowiny jest wyślizgany do połysku.

### Variants
#### Variant A
- Trial short: W osi przejazdu albo przy zwężeniu miejski
- Trial description: Na mur widać wydeptane i przeorane koleinami; ruch musi zwolnić przy osi przejazdu albo przy zwężeniu. Kamienie wystają z nawierzchni i tłuką koła. Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.080
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W osi przejazdu albo przy zwężeniu miejski
- Trial description: Przy osi przejazdu albo przy zwężeniu wozy koleiny jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.027
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Rozstaje Traktów (`55`)
- Area: `Centrum_Twierdza`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (drogi koleiny vs kamień).

### Existing Facts
- Existing description: Rozstaje otwierają się poza miasto jak wybór, który zawsze przychodzi za późno. Tutaj drogi rozchodzą się ku polom, młynowi i mostowi, a każdy skręt ma na sobie ślady kół i decyzji.
- Actual exits: polnoc, poludniowy-wschod, wschod, zachod
- Existing inspectables: drogi koleiny, kamień

### Proposed Microimage
- anchor_object: drogi koleiny [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnoc prowadzi ku Zaułek Czeladników; zachod prowadzi ku Opuszczona Chata [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kamień [INSPECTABLE]
- optional_examinable: drogi koleiny [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Rozstaje otwierają się poza miasto jak wybór, który zawsze przychodzi za późno. Tutaj drogi rozchodzą się ku polom, młynowi i mostowi, a każdy skręt ma na sobie ślady kół i decyzji.
- LOCATION_NAME: Rozstaje Traktów
- INSPECTABLE: drogi koleiny, kamień
- EXIT_GEOMETRY: polnoc, poludniowy-wschod, wschod, zachod
- NEIGHBOUR_CONTINUITY: polnoc:Zaułek Czeladników, zachod:Opuszczona Chata, poludniowy-wschod:Kapliczka Przydrożna, wschod:Wschodnia Furta Łowców
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: handel i warta
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Rozstaje Traktów', 'secondary_details': ['drogi koleiny', 'kamień', 'Rozstaje otwierają się poza miasto jak wybór, który zawsze przychodzi za późno'], 'historical_layer': 'warstwy murów i ciągłe naprawy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Zaułek Czeladników (miejski) -> Czeladnicy mieszkają i pracują w zaułku, który nocą brzmi jak zbiór cichych sporów o narzędzia i honor. Pod ścianami stoją skrzynki, zwoje sznurów i łaty materiału.
- zachod: Opuszczona Chata (miejski) -> Chata stoi krzywo, ale jeszcze nie upadła, jakby sama nie była pewna, czy zasługuje na zapomnienie. W środku zalega kurz, stara słoma i kilka śladów po tym, że ktoś kiedyś jednak tu mieszkał.

### Variants
#### Variant A
- Trial short: Przejście miejski
- Trial description: Przy miedzy pozostaje wąski przejazd. Na drogi koleiny widać wydeptane i przeorane koleinami; ruch musi zwolnić przy osi przejazdu albo przy zwężeniu. Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.057
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście miejski
- Trial description: Przy miedzy pozostaje wąski przejazd. Na kamień widać wydeptane i przeorane koleinami; ruch musi zwolnić przy osi przejazdu albo przy zwężeniu. Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.124
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=REGIONAL_MATERIAL, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Mur Nad Traktem (`119`)
- Area: `Forteca_Dungrim`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (przedmurze droga vs straż patrzenie).

### Existing Facts
- Existing description: Mur Nad Traktem pozwala obserwować drogę w dół i wyłapywać każdy ruch wozów oraz pieszych. Wiatry są tu ostre, a rozmowy krótkie.
- Actual exits: wschod, zachod
- Existing inspectables: przedmurze droga, straż patrzenie, szczeliny wiatr

### Proposed Microimage
- anchor_object: przedmurze droga [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Izba Oficerska; wschod prowadzi ku Sala Dowódcy [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: straż patrzenie [INSPECTABLE]
- optional_examinable: przedmurze droga [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Mur Nad Traktem pozwala obserwować drogę w dół i wyłapywać każdy ruch wozów oraz pieszych. Wiatry są tu ostre, a rozmowy krótkie.
- LOCATION_NAME: Mur Nad Traktem
- INSPECTABLE: przedmurze droga, straż patrzenie, szczeliny wiatr
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Izba Oficerska, wschod:Sala Dowódcy
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Mur Nad Traktem', 'secondary_details': ['przedmurze droga', 'straż patrzenie', 'szczeliny wiatr', 'Mur Nad Traktem pozwala obserwować drogę w dół i wyłapywać każdy ruch wozów oraz pieszych'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Izba Oficerska (forteczny) -> Izba Oficerska jest bardziej spokojna niż reszta fortu, ale tylko dlatego, że tu zapadają decyzje. Na stole leżą mapy, pieczęcie i zamknięte raporty.
- wschod: Sala Dowódcy (forteczny) -> Sala Dowódcy jest najciszej strzeżonym miejscem w fortecy. Mapa działań, pieczęcie i krzesło przy stole mówią, że tu ważą się decyzje o całym garnizonie.

### Variants
#### Variant A
- Trial short: W osi przejazdu albo przy zwężeniu i świeża naprawa muru
- Trial description: Przy osi przejazdu albo przy zwężeniu przedmurze droga jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Na środku traktu leży rozjechany żwir, a po bokach widać miękki piasek.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.019
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W osi przejazdu albo przy zwężeniu i świeża naprawa muru
- Trial description: Na straż patrzenie widać wydeptane i przeorane koleinami; ruch musi zwolnić przy osi przejazdu albo przy zwężeniu. Woda stoi w koleinie przy rowie. Ubita ziemia pęka przy brzegu, a koleina rozszerza się ku dołowi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.114
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Wyjazd na Zachodni Trakt (`124`)
- Area: `Forteca_Dungrim`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (szlaban trakt vs błoto ślady).

### Existing Facts
- Existing description: Wyjazd na Zachodni Trakt jest ostatnim punktem fortecy przed drogą w otwarty teren. Tu kontroluje się wóz, pieczęć i ostatni raz patrzy na zawartość ładunku.
- Actual exits: poludnie, wschod
- Existing inspectables: szlaban trakt, pieczęcie warta, błoto ślady

### Proposed Microimage
- anchor_object: szlaban trakt [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: wschod prowadzi ku Skład Racji; poludnie prowadzi ku Stara Droga za Furtą [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: błoto ślady [INSPECTABLE]
- optional_examinable: szlaban trakt [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Wyjazd na Zachodni Trakt jest ostatnim punktem fortecy przed drogą w otwarty teren. Tu kontroluje się wóz, pieczęć i ostatni raz patrzy na zawartość ładunku.
- LOCATION_NAME: Wyjazd na Zachodni Trakt
- INSPECTABLE: szlaban trakt, pieczęcie warta, błoto ślady
- EXIT_GEOMETRY: poludnie, wschod
- NEIGHBOUR_CONTINUITY: wschod:Skład Racji, poludnie:Stara Droga za Furtą
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Wyjazd na Zachodni Trakt', 'secondary_details': ['szlaban trakt', 'pieczęcie warta', 'błoto ślady', 'Wyjazd na Zachodni Trakt jest ostatnim punktem fortecy przed drogą w otwarty teren'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Skład Racji (forteczny) -> Skład Racji trzyma to, co najczęściej znika: chleb, sól, suszone mięso i lampowy tłuszcz. Każda półka ma własny znak, a wszystko pachnie sucho i praktycznie.
- poludnie: Stara Droga za Furtą (drogowy) -> Stara Droga za Furtą. Ścieżka jest wąska i kapryśna; miejscami znika pod trawą, żeby wrócić kilka kroków dalej. Przy bramach stoją beczki, skrzynie i płoty naprawiane po zimie.

### Variants
#### Variant A
- Trial short: Wojsko i magazyny Forteca_Dungrim
- Trial description: Przy osi przejazdu albo przy zwężeniu szlaban trakt jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Na środku traktu leży rozjechany żwir, a po bokach widać miękki piasek.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.067
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Wojsko i magazyny Forteca_Dungrim
- Trial description: Przy osi przejazdu albo przy zwężeniu błoto ślady jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.137
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Kapliczka Podróżnych za Murem (`135`)
- Area: `Trakty`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamien kapliczka vs ofiary świece wosk).

### Existing Facts
- Existing description: Kamienna kapliczka stoi przy rozjeździe, trochę cofnięta od traktu, żeby wozy nie rozbijały jej przy każdym mijaniu. Nad niszami wiszą woski i drobne dary zostawione przez ludzi, którzy chcą bezpiecznie minąć kolejne mile. Miejsce służy odpoczynkowi, modlitwie i sprawdzeniu uprzęży, zanim droga znów zawęzi się między mokrą ziemią a rowem.
- Actual exits: polnoc, polnocny-zachod, poludniowy-wschod
- Existing inspectables: kamien kapliczka, ofiary świece wosk, trakt rozjazd

### Proposed Microimage
- anchor_object: kamien kapliczka [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: przy ścianie, fundamencie albo progu [LOCATION_DESCRIPTION]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: sprawia, że ruch zwalnia przy zatrzymaniu [LOCATION_DESCRIPTION]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: polnoc prowadzi ku Ulica Popiołów; poludniowy-wschod prowadzi ku Pierwszy Kamień Milowy [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: ofiary świece wosk [INSPECTABLE]
- optional_examinable: kamien kapliczka [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Kamienna kapliczka stoi przy rozjeździe, trochę cofnięta od traktu, żeby wozy nie rozbijały jej przy każdym mijaniu. Nad niszami wiszą woski i drobne dary zostawione przez ludzi, którzy chcą bezpiecznie minąć kolejne mile. Miejsce służy odpoczynkowi, modlitwie i sprawdzeniu uprzęży, zanim droga znów zawęzi się między mokrą ziemią a rowem.
- LOCATION_NAME: Kapliczka Podróżnych za Murem
- INSPECTABLE: kamien kapliczka, ofiary świece wosk, trakt rozjazd
- EXIT_GEOMETRY: polnoc, polnocny-zachod, poludniowy-wschod
- NEIGHBOUR_CONTINUITY: polnoc:Ulica Popiołów, poludniowy-wschod:Pierwszy Kamień Milowy, polnocny-zachod:Kapliczka Przydrożna
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: karawany
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Kapliczka Podróżnych za Murem', 'secondary_details': ['kamien kapliczka', 'ofiary świece wosk', 'trakt rozjazd', 'Kamienna kapliczka stoi przy rozjeździe, trochę cofnięta od traktu, żeby wozy nie rozbijały jej przy każdym mijaniu'], 'historical_layer': 'ruch karawan i łatanie drogi'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Ulica Popiołów (przedmiejski) -> Ulica Popiołów. Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych. Przy bramach stoją beczki, skrzynie i płoty naprawiane po zimie.
- poludniowy-wschod: Pierwszy Kamień Milowy (drogowy) -> Pierwszy Kamień Milowy. Kamień, słup albo znak przypomina, że na trakcie myli się tylko ten, kto nie patrzy pod nogi. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.

### Variants
#### Variant A
- Trial short: Przy ścianie, fundamencie albo progu
- Trial description: Na kamien kapliczka widać wydeptane i przeorane koleinami; ruch musi zwolnić przy ścianie, fundamencie albo progu. Korzenie wypychają bruk na jednym łuku. Na środku leżą rumosz i suche liście.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.130
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przy ścianie, fundamencie albo progu
- Trial description: Na ofiary świece wosk widać wydeptane i przeorane koleinami; ruch musi zwolnić przy ścianie, fundamencie albo progu. Kamienie wystają z nawierzchni i tłuką koła. Koleiny prowadzą wprost do osady, a przy furtce zbiera się błoto.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.036
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Pierwszy Kamień Milowy (`136`)
- Area: `Trakty`
- Family: `road`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (koleiny vs wiatr).

### Existing Facts
- Existing description: Pierwszy Kamień Milowy. Kamień, słup albo znak przypomina, że na trakcie myli się tylko ten, kto nie patrzy pod nogi. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.
- Actual exits: polnocny-zachod, poludnie
- Existing inspectables: znaki, koleiny, wiatr

### Proposed Microimage
- anchor_object: koleiny [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnocny-zachod prowadzi ku Kapliczka Podróżnych za Murem; poludnie prowadzi ku Mokra Koleina [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: wiatr [INSPECTABLE]
- optional_examinable: koleiny [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Pierwszy Kamień Milowy. Kamień, słup albo znak przypomina, że na trakcie myli się tylko ten, kto nie patrzy pod nogi. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.
- LOCATION_NAME: Pierwszy Kamień Milowy
- INSPECTABLE: znaki, koleiny, wiatr
- EXIT_GEOMETRY: polnocny-zachod, poludnie
- NEIGHBOUR_CONTINUITY: polnocny-zachod:Kapliczka Podróżnych za Murem, poludnie:Mokra Koleina
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: karawany
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Pierwszy Kamień Milowy', 'secondary_details': ['znaki', 'koleiny', 'wiatr', 'Pierwszy Kamień Milowy'], 'historical_layer': 'ruch karawan i łatanie drogi'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnocny-zachod: Kapliczka Podróżnych za Murem (drogowy) -> Kamienna kapliczka stoi przy rozjeździe, trochę cofnięta od traktu, żeby wozy nie rozbijały jej przy każdym mijaniu. Nad niszami wiszą woski i drobne dary zostawione przez ludzi, którzy chcą bezpiecznie minąć kolejne mile. Miejsce służy odpoczynkowi, modlitwie i sprawdzeniu uprzęży, zanim droga znów zawęzi się między mokrą ziemią a rowem.
- poludnie: Mokra Koleina (drogowy) -> Mokra Koleina. Tu wozy zwalniają, a karawany ustawiają się w kolejkę do kolejnego odcinka drogi. Towary, głosy i biegnące dzieci mijają się tu bez chwili przerwy.

### Variants
#### Variant A
- Trial short: Wydeptane i przeorane koleinami drogowy
- Trial description: Przy osi przejazdu albo przy zwężeniu koleiny jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia przejazd. Na środku traktu leży rozjechany żwir, a po bokach widać miękki piasek.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.069
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Koleiny, żwir lub bruk o różnej głębokości drogowy
- Trial description: Przy lokalnym punkcie przejścia wiatr jest koleiny, żwir lub bruk o różnej głębokości, więc zwęża przejście i rozlewa wodę na bok. Za zakrętem ubita ziemia przechodzi w płaskie kamienie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.074
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Błotna Brama (`60`)
- Area: `Podgrodzie`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (brama wjazd vs koleina błoto woda).

### Existing Facts
- Existing description: Błotna Brama trzyma południowy wjazd podgrodzia. W wysokich odgrodach odcisnęły się koła wozów, a przy zawiasach widać świeżą smołę i naprawiane po zimie deski. To tutaj ruch zwalnia, bo każdy musi minąć wartę, palenisko i szeroką koleinę pełną brunatnej wody.
- Actual exits: polnoc, poludnie
- Existing inspectables: brama wjazd, warta wartownicy, koleina błoto woda

### Proposed Microimage
- anchor_object: brama wjazd [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: poludnie prowadzi ku Szopa Tragarzy; polnoc prowadzi ku Opuszczona Chata [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: koleina błoto woda [INSPECTABLE]
- optional_examinable: brama wjazd [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Błotna Brama trzyma południowy wjazd podgrodzia. W wysokich odgrodach odcisnęły się koła wozów, a przy zawiasach widać świeżą smołę i naprawiane po zimie deski. To tutaj ruch zwalnia, bo każdy musi minąć wartę, palenisko i szeroką koleinę pełną brunatnej wody.
- LOCATION_NAME: Błotna Brama
- INSPECTABLE: brama wjazd, warta wartownicy, koleina błoto woda
- EXIT_GEOMETRY: polnoc, poludnie
- NEIGHBOUR_CONTINUITY: poludnie:Szopa Tragarzy, polnoc:Opuszczona Chata
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: targ i zaplecze
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Błotna Brama', 'secondary_details': ['brama wjazd', 'warta wartownicy', 'koleina błoto woda', 'Błotna Brama trzyma południowy wjazd podgrodzia'], 'historical_layer': 'mokre przedmieście i łatane płoty'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- poludnie: Szopa Tragarzy (przedmiejski) -> Szopa Tragarzy. Błoto jest tu ciężkie i ciemne. W koleinach stoją ślady wozów, ludzi i zwierząt pociągowych. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.
- polnoc: Opuszczona Chata (miejski) -> Chata stoi krzywo, ale jeszcze nie upadła, jakby sama nie była pewna, czy zasługuje na zapomnienie. W środku zalega kurz, stara słoma i kilka śladów po tym, że ktoś kiedyś jednak tu mieszkał.

### Variants
#### Variant A
- Trial short: Błotna Brama
- Trial description: Przy granicy teren przechodzi z bruku w ubity grunt. Na styku brama wjazd i sąsiedniego terenu widać wydeptane i przeorane koleinami. Przy słupie stoi łańcuch i odgarnięty żwir. Ślady butów kończą się przed suchą częścią drogi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.143
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Błotna Brama
- Trial description: Przy wejściu lub przy przejeździe koleina błoto woda jest wydeptane i przeorane koleinami, a po drugiej stronie po poludnie stronie przechodzi w przedmiejski teren. Po jednej stronie leżą zaprawione kamienie, po drugiej szary żwir. Przy wejściu widać ślady zawracania i cięższy ruch. W wykopie zbiera się woda po ostatnim deszczu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.058
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Wschodnia Furta Łowców (`95`)
- Area: `Osada_Mysliwych`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (furta palisada vs sidła kłody).

### Existing Facts
- Existing description: Wschodnia furta otwiera się na wąski przesmyk między palisadą a pierwszymi drzewami. Z jednej strony stoi suszarnia skór, z drugiej wiszą pęki sidła i świeżo obrane kłody. To wejście do osady działa bardziej jak punkt wymiany niż prawdziwa brama: tu oddaje się zwierzynę, odbiera narzędzia i liczy, kto wrócił z lasu.
- Actual exits: wschod, zachod
- Existing inspectables: furta palisada, suszarnia skory, sidła kłody

### Proposed Microimage
- anchor_object: furta palisada [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Suszarnia Skór; zachod prowadzi ku Rozstaje Traktów [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: sidła kłody [INSPECTABLE]
- optional_examinable: furta palisada [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Wschodnia furta otwiera się na wąski przesmyk między palisadą a pierwszymi drzewami. Z jednej strony stoi suszarnia skór, z drugiej wiszą pęki sidła i świeżo obrane kłody. To wejście do osady działa bardziej jak punkt wymiany niż prawdziwa brama: tu oddaje się zwierzynę, odbiera narzędzia i liczy, kto wrócił z lasu.
- LOCATION_NAME: Wschodnia Furta Łowców
- INSPECTABLE: furta palisada, suszarnia skory, sidła kłody
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: wschod:Suszarnia Skór, zachod:Rozstaje Traktów
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: obróbka trofeów
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Wschodnia Furta Łowców', 'secondary_details': ['furta palisada', 'suszarnia skory', 'sidła kłody', 'Wschodnia furta otwiera się na wąski przesmyk między palisadą a pierwszymi drzewami'], 'historical_layer': 'dym, skóry i tropy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Suszarnia Skór (leśny) -> Suszarnia Skór. Skóry wiszą na żerdziach. Jedne pachną dymem, inne krwią i mokrym psem. Pył, dym i zapach wilgotnego drewna wiszą nisko między domami.
- zachod: Rozstaje Traktów (miejski) -> Rozstaje otwierają się poza miasto jak wybór, który zawsze przychodzi za późno. Tutaj drogi rozchodzą się ku polom, młynowi i mostowi, a każdy skręt ma na sobie ślady kół i decyzji.

### Variants
#### Variant A
- Trial short: Wschodnia Furta Łowców
- Trial description: Przy wejściu lub przy przejeździe furta palisada jest wyszlifowane, starte albo nadkruszone, a po drugiej stronie po wschod stronie przechodzi w leśny teren. Po jednej stronie leży bruk, po drugiej ubita ziemia.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.059
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Wschodnia Furta Łowców
- Trial description: Przy wejściu lub przy przejeździe sidła kłody jest wyszlifowane, starte albo nadkruszone, a po drugiej stronie po wschod stronie przechodzi w leśny teren. Na jednej krawędzi widać żelazne okucia, na drugiej kamień z licem. W koleinach stoi błoto po wozach zawracających przed bramą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.112
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Brama Dymnych Chorągwi (`0`)
- Area: `Centrum_Twierdza`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (brama vs koleiny blotnista droga droga).

### Existing Facts
- Existing description: Wąska brama wciska trakt między kamienny mur i czarne belki strażnicy. Na hakach wiszą mokre płaszcze wartowników, a w koleinach stoi brunatna woda. Od krat, łańcuchów i okutych wrót ciągnie zapach wilgotnego żelaza.
- Actual exits: polnoc, poludnie, wschod
- Existing inspectables: brama, mur, warta wartownicy zolnierz zolnierze, koleiny blotnista droga droga

### Proposed Microimage
- anchor_object: brama [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Plac Przed Wartownią; poludnie prowadzi ku Trakt Przy Murze [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: koleiny blotnista droga droga [INSPECTABLE]
- optional_examinable: brama [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Wąska brama wciska trakt między kamienny mur i czarne belki strażnicy. Na hakach wiszą mokre płaszcze wartowników, a w koleinach stoi brunatna woda. Od krat, łańcuchów i okutych wrót ciągnie zapach wilgotnego żelaza.
- LOCATION_NAME: Brama Dymnych Chorągwi
- INSPECTABLE: brama, mur, warta wartownicy zolnierz zolnierze, koleiny blotnista droga droga
- EXIT_GEOMETRY: polnoc, poludnie, wschod
- NEIGHBOUR_CONTINUITY: wschod:Plac Przed Wartownią, poludnie:Trakt Przy Murze, polnoc:Brama Strażnicy Przełęczy
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: handel i warta
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Brama Dymnych Chorągwi', 'secondary_details': ['brama', 'mur', 'warta wartownicy zolnierz zolnierze', 'koleiny blotnista droga droga'], 'historical_layer': 'warstwy murów i ciągłe naprawy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Plac Przed Wartownią (miejski) -> Plac jest bardziej ubity niż wybrukowany. Pod ścianą wartowni leżą polana, skrzynki z grotami i tarcze odstawione do naprawy. Z komina idzie niski dym, który nie chce podnieść się nad dach.
- poludnie: Trakt Przy Murze (miejski) -> Trakt biegnie wzdłuż muru tak blisko, że idący mimowolnie ściszają głos. Kamienie są tu wyszlifowane przez buty patroli i obręcze wozów.

### Variants
#### Variant A
- Trial short: Brama Dymnych Chorągwi
- Trial description: Na styku brama i sąsiedniego terenu widać wydeptane i przeorane koleinami. Światło gaśnie pod pierwszymi pniami.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.056
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Brama Dymnych Chorągwi
- Trial description: Przy wejściu lub przy przejeździe koleiny blotnista droga droga jest wydeptane i przeorane koleinami, a po drugiej stronie po wschod stronie przechodzi w miejski teren. Roślinność wciska się pod krawężnik i pod ławę.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.067
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Brama Dungrim (`110`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (brama hak vs mur przejazd).

### Existing Facts
- Existing description: Brama Dungrim zamyka fortecę na wąskim przesmyku drogi. Żelazne okucia, hak do łańcucha i zgrana warta mówią jasno, że to nie jest miejsce dla przypadkowych przejazdów.
- Actual exits: polnocny-wschod, wschod
- Existing inspectables: brama hak, warta straż, mur przejazd

### Proposed Microimage
- anchor_object: brama hak [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Przedbramie Wilczych Haków; polnocny-wschod prowadzi ku Brama do Dungrim [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: mur przejazd [INSPECTABLE]
- optional_examinable: brama hak [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Brama Dungrim zamyka fortecę na wąskim przesmyku drogi. Żelazne okucia, hak do łańcucha i zgrana warta mówią jasno, że to nie jest miejsce dla przypadkowych przejazdów.
- LOCATION_NAME: Brama Dungrim
- INSPECTABLE: brama hak, warta straż, mur przejazd
- EXIT_GEOMETRY: polnocny-wschod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Przedbramie Wilczych Haków, polnocny-wschod:Brama do Dungrim
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Brama Dungrim', 'secondary_details': ['brama hak', 'warta straż', 'mur przejazd', 'Brama Dungrim zamyka fortecę na wąskim przesmyku drogi'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Przedbramie Wilczych Haków (forteczny) -> Przedbramie jest ciasne, niskie i zbudowane tak, by spowolnić każdego, kto nie został tu oczekiwany. Na belkach wiszą stare haki, a pod nogami widać ślady po kołach wozów i butach wartowników.
- polnocny-wschod: Brama do Dungrim (górski) -> Brama do Dungrim zamyka Strażnicę Przełęczy od strony zachodniego zejścia. To ostatni punkt, w którym straż liczy pieczęcie, zanim droga spadnie ku wojskowemu fortowi.

### Variants
#### Variant A
- Trial short: Brama Dungrim
- Trial description: Na styku brama hak i sąsiedniego terenu widać wyszlifowane, starte albo nadkruszone. Po jednej stronie leży bruk, po drugiej ubita ziemia.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.195
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Brama Dungrim
- Trial description: Na styku mur przejazd i sąsiedniego terenu widać wyszlifowane, starte albo nadkruszone. Na jednej krawędzi widać żelazne okucia, na drugiej kamień z licem. W koleinach stoi błoto po wozach zawracających przed bramą.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.073
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Przedbramie Wilczych Haków (`111`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (haki belki vs warta drzwi).

### Existing Facts
- Existing description: Przedbramie jest ciasne, niskie i zbudowane tak, by spowolnić każdego, kto nie został tu oczekiwany. Na belkach wiszą stare haki, a pod nogami widać ślady po kołach wozów i butach wartowników.
- Actual exits: wschod, zachod
- Existing inspectables: haki belki, ślady koła, warta drzwi

### Proposed Microimage
- anchor_object: haki belki [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: przy wejściu lub przy przejeździe [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: zwalnia przejście i wymusza kontrolę ruchu [EXIT_GEOMETRY]
- relation_to_visibility: ogranicza widok lub rozcina linię wzroku [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Brama Dungrim; wschod prowadzi ku Dziedziniec Garnizonu [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: warta drzwi [INSPECTABLE]
- optional_examinable: haki belki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Przedbramie jest ciasne, niskie i zbudowane tak, by spowolnić każdego, kto nie został tu oczekiwany. Na belkach wiszą stare haki, a pod nogami widać ślady po kołach wozów i butach wartowników.
- LOCATION_NAME: Przedbramie Wilczych Haków
- INSPECTABLE: haki belki, ślady koła, warta drzwi
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Brama Dungrim, wschod:Dziedziniec Garnizonu
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Przedbramie Wilczych Haków', 'secondary_details': ['haki belki', 'ślady koła', 'warta drzwi', 'Przedbramie jest ciasne, niskie i zbudowane tak, by spowolnić każdego, kto nie został tu oczekiwany'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Brama Dungrim (forteczny) -> Brama Dungrim zamyka fortecę na wąskim przesmyku drogi. Żelazne okucia, hak do łańcucha i zgrana warta mówią jasno, że to nie jest miejsce dla przypadkowych przejazdów.
- wschod: Dziedziniec Garnizonu (forteczny) -> Dziedziniec Garnizonu jest sercem codziennego ruchu. Tu ćwiczą oddziały, tu stają skrzynie z zapasami i tu każdy rozkaz robi się głośniejszy, niż chciałby dowódca.

### Variants
#### Variant A
- Trial short: Przedbramie Wilczych Haków
- Trial description: Przy granicy teren przechodzi z bruku w ubity grunt. Na styku haki belki i sąsiedniego terenu widać wydeptane i przeorane koleinami. Przy słupie stoi łańcuch i odgarnięty żwir. Ślady butów kończą się przed suchą częścią drogi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.047
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przedbramie Wilczych Haków
- Trial description: Przy wejściu lub przy przejeździe warta drzwi jest wydeptane i przeorane koleinami, a po drugiej stronie po zachod stronie przechodzi w forteczny teren. Po jednej stronie leżą zaprawione kamienie, po drugiej szary żwir. Przy wejściu widać ślady zawracania i cięższy ruch. W wykopie zbiera się woda po ostatnim deszczu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.045
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Dziedziniec Garnizonu (`112`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (błoto koła vs plac tarcze).

### Existing Facts
- Existing description: Dziedziniec Garnizonu jest sercem codziennego ruchu. Tu ćwiczą oddziały, tu stają skrzynie z zapasami i tu każdy rozkaz robi się głośniejszy, niż chciałby dowódca.
- Actual exits: poludnie, zachod
- Existing inspectables: plac tarcze, żołnierze ćwiczenia, błoto koła

### Proposed Microimage
- anchor_object: błoto koła [INSPECTABLE]
- physical_state: używane, ustawione równo albo zabrudzone pracą [LOCATION_DESCRIPTION]
- precise_position: przy ścianie albo na skraju gospodarczym [LOCATION_DESCRIPTION]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: zbiera ludzi wokół codziennej czynności [LOCATION_DESCRIPTION]
- relation_to_visibility: pokazuje porządek prac albo ustawienie zabudowań [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Przedbramie Wilczych Haków; poludnie prowadzi ku Studnia Forteczna [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: plac tarcze [INSPECTABLE]
- optional_examinable: błoto koła [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Dziedziniec Garnizonu jest sercem codziennego ruchu. Tu ćwiczą oddziały, tu stają skrzynie z zapasami i tu każdy rozkaz robi się głośniejszy, niż chciałby dowódca.
- LOCATION_NAME: Dziedziniec Garnizonu
- INSPECTABLE: plac tarcze, żołnierze ćwiczenia, błoto koła
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Przedbramie Wilczych Haków, poludnie:Studnia Forteczna
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Dziedziniec Garnizonu', 'secondary_details': ['plac tarcze', 'żołnierze ćwiczenia', 'błoto koła', 'Dziedziniec Garnizonu jest sercem codziennego ruchu'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Przedbramie Wilczych Haków (forteczny) -> Przedbramie jest ciasne, niskie i zbudowane tak, by spowolnić każdego, kto nie został tu oczekiwany. Na belkach wiszą stare haki, a pod nogami widać ślady po kołach wozów i butach wartowników.
- poludnie: Studnia Forteczna (forteczny) -> Studnia forteczna stoi na środku dziedzińca i obsługuje nie tylko ludzi, ale i konie, kuchnię oraz magazyny. Woda jest zimna, ciężka i pilnowana prawie jak zapasy bełtów.

### Variants
#### Variant A
- Trial short: Dziedziniec Garnizonu
- Trial description: Na styku błoto koła i sąsiedniego terenu widać używane, ustawione równo albo zabrudzone pracą. Las dochodzi do drogi bez bramy i bez muru.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.083
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Dziedziniec Garnizonu
- Trial description: Przy ścianie albo na skraju gospodarczym plac tarcze jest używane, ustawione równo albo zabrudzone pracą, a po drugiej stronie po zachod stronie przechodzi w forteczny teren. Rów i palisada zamykają przesmyk.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.074
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Studnia Forteczna (`113`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamien woda vs cisza echo).

### Existing Facts
- Existing description: Studnia forteczna stoi na środku dziedzińca i obsługuje nie tylko ludzi, ale i konie, kuchnię oraz magazyny. Woda jest zimna, ciężka i pilnowana prawie jak zapasy bełtów.
- Actual exits: polnoc, poludnie
- Existing inspectables: łańcuch wiadro, kamien woda, cisza echo

### Proposed Microimage
- anchor_object: kamien woda [INSPECTABLE]
- physical_state: podmokłe, rozmiękłe albo zamulone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: spływ wody i osiadanie podłoża [REGIONAL_PROCESS]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: zasnuwa albo obniża widoczność przy krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: polnoc prowadzi ku Dziedziniec Garnizonu; poludnie prowadzi ku Stajnie Patroli [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: cisza echo [INSPECTABLE]
- optional_examinable: kamien woda [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Studnia forteczna stoi na środku dziedzińca i obsługuje nie tylko ludzi, ale i konie, kuchnię oraz magazyny. Woda jest zimna, ciężka i pilnowana prawie jak zapasy bełtów.
- LOCATION_NAME: Studnia Forteczna
- INSPECTABLE: łańcuch wiadro, kamien woda, cisza echo
- EXIT_GEOMETRY: polnoc, poludnie
- NEIGHBOUR_CONTINUITY: polnoc:Dziedziniec Garnizonu, poludnie:Stajnie Patroli
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Studnia Forteczna', 'secondary_details': ['łańcuch wiadro', 'kamien woda', 'cisza echo', 'Studnia forteczna stoi na środku dziedzińca i obsługuje nie tylko ludzi, ale i konie, kuchnię oraz magazyny'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Dziedziniec Garnizonu (forteczny) -> Dziedziniec Garnizonu jest sercem codziennego ruchu. Tu ćwiczą oddziały, tu stają skrzynie z zapasami i tu każdy rozkaz robi się głośniejszy, niż chciałby dowódca.
- poludnie: Stajnie Patroli (forteczny) -> Stajnie są niskie, ciepłe i pełne zapachu słomy oraz mokrej skóry. Konie patrolowe stoją w oddzielnych boksach, gotowe do wyjazdu w każdej chwili.

### Variants
#### Variant A
- Trial short: Studnia Forteczna
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody kamien woda jest podmokłe, rozmiękłe albo zamulone, a po drugiej stronie po polnoc stronie przechodzi w forteczny teren. Po jednej stronie leżą zaprawione kamienie, po drugiej szary żwir. Przy wejściu widać ślady zawracania i cięższy ruch. W wykopie zbiera się woda po ostatnim deszczu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.040
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=REGIONAL_PROCESS, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Studnia Forteczna
- Trial description: Przy ścianie albo na skraju gospodarczym cisza echo jest podmokłe, rozmiękłe albo zamulone, a po drugiej stronie po polnoc stronie przechodzi w forteczny teren. Roślinność wciska się pod krawężnik i pod ławę.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.167
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=LOCATION_DESCRIPTION, physical_cause=REGIONAL_PROCESS, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Stajnie Patroli (`114`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (siano uzda vs boks konie).

### Existing Facts
- Existing description: Stajnie są niskie, ciepłe i pełne zapachu słomy oraz mokrej skóry. Konie patrolowe stoją w oddzielnych boksach, gotowe do wyjazdu w każdej chwili.
- Actual exits: polnoc, zachod
- Existing inspectables: boks konie, siano uzda, kopyta błoto

### Proposed Microimage
- anchor_object: siano uzda [INSPECTABLE]
- physical_state: starta i przytarta [HUMAN_REVIEW_REQUIRED]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: warta, handel lub ciągły ruch [HUMAN_REVIEW_REQUIRED]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnoc prowadzi ku Studnia Forteczna; zachod prowadzi ku Kuchnia Garnizonowa [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: boks konie [INSPECTABLE]
- optional_examinable: siano uzda [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Stajnie są niskie, ciepłe i pełne zapachu słomy oraz mokrej skóry. Konie patrolowe stoją w oddzielnych boksach, gotowe do wyjazdu w każdej chwili.
- LOCATION_NAME: Stajnie Patroli
- INSPECTABLE: boks konie, siano uzda, kopyta błoto
- EXIT_GEOMETRY: polnoc, zachod
- NEIGHBOUR_CONTINUITY: polnoc:Studnia Forteczna, zachod:Kuchnia Garnizonowa
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Stajnie Patroli', 'secondary_details': ['boks konie', 'siano uzda', 'kopyta błoto', 'Stajnie są niskie, ciepłe i pełne zapachu słomy oraz mokrej skóry'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Studnia Forteczna (forteczny) -> Studnia forteczna stoi na środku dziedzińca i obsługuje nie tylko ludzi, ale i konie, kuchnię oraz magazyny. Woda jest zimna, ciężka i pilnowana prawie jak zapasy bełtów.
- zachod: Kuchnia Garnizonowa (forteczny) -> Kuchnia garnizonowa pracuje bez przerwy. Kotły, łopaty do pieca i ciężkie garnki są tu ważniejsze niż ozdoby, bo cała załoga ma jeść na czas.

### Variants
#### Variant A
- Trial short: Stajnie Patroli
- Trial description: Przy lokalnym punkcie przejścia siano uzda jest starta i przytarta, a po drugiej stronie po polnoc stronie przechodzi w forteczny teren. Światło gaśnie pod pierwszymi pniami.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.167
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=HUMAN_REVIEW_REQUIRED, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Stajnie Patroli
- Trial description: Przy lokalnym punkcie przejścia boks konie jest starta i przytarta, a po drugiej stronie po polnoc stronie przechodzi w forteczny teren. Las dochodzi do drogi bez bramy i bez muru.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.078
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=HUMAN_REVIEW_REQUIRED, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Kuchnia Garnizonowa (`115`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (gulasz racje vs kotly ogien).

### Existing Facts
- Existing description: Kuchnia garnizonowa pracuje bez przerwy. Kotły, łopaty do pieca i ciężkie garnki są tu ważniejsze niż ozdoby, bo cała załoga ma jeść na czas.
- Actual exits: wschod, zachod
- Existing inspectables: kotly ogien, gulasz racje, zlew noze

### Proposed Microimage
- anchor_object: gulasz racje [INSPECTABLE]
- physical_state: używane, ustawione równo albo zabrudzone pracą [LOCATION_DESCRIPTION]
- precise_position: przy ścianie albo na skraju gospodarczym [LOCATION_DESCRIPTION]
- physical_cause: codzienna praca, przechowywanie albo musztra [EXISTING_WORLD_FACT]
- relation_to_movement: zbiera ludzi wokół codziennej czynności [LOCATION_DESCRIPTION]
- relation_to_visibility: pokazuje porządek prac albo ustawienie zabudowań [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Stajnie Patroli; zachod prowadzi ku Koszary Zachodnie [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kotly ogien [INSPECTABLE]
- optional_examinable: gulasz racje [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Kuchnia garnizonowa pracuje bez przerwy. Kotły, łopaty do pieca i ciężkie garnki są tu ważniejsze niż ozdoby, bo cała załoga ma jeść na czas.
- LOCATION_NAME: Kuchnia Garnizonowa
- INSPECTABLE: kotly ogien, gulasz racje, zlew noze
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: wschod:Stajnie Patroli, zachod:Koszary Zachodnie
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Kuchnia Garnizonowa', 'secondary_details': ['kotly ogien', 'gulasz racje', 'zlew noze', 'Kuchnia garnizonowa pracuje bez przerwy'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Stajnie Patroli (forteczny) -> Stajnie są niskie, ciepłe i pełne zapachu słomy oraz mokrej skóry. Konie patrolowe stoją w oddzielnych boksach, gotowe do wyjazdu w każdej chwili.
- zachod: Koszary Zachodnie (forteczny) -> Koszary Zachodnie to długi budynek z pryczami, skrzyniami i tablicą rozkazów. W środku zawsze ktoś śpi, ktoś czyści sprzęt, a ktoś inny udaje, że nie słyszy pobudki.

### Variants
#### Variant A
- Trial short: Kuchnia Garnizonowa
- Trial description: Na styku gulasz racje i sąsiedniego terenu widać używane, ustawione równo albo zabrudzone pracą. Roślinność wciska się pod krawężnik i pod ławę.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.176
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Kuchnia Garnizonowa
- Trial description: Na styku kotly ogien i sąsiedniego terenu widać używane, ustawione równo albo zabrudzone pracą. Po jednej stronie leży bruk, po drugiej ubita ziemia.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.061
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Koszary Zachodnie (`116`)
- Area: `Forteca_Dungrim`
- Family: `border`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (prycze skrzynie vs tablica rozkaz).

### Existing Facts
- Existing description: Koszary Zachodnie to długi budynek z pryczami, skrzyniami i tablicą rozkazów. W środku zawsze ktoś śpi, ktoś czyści sprzęt, a ktoś inny udaje, że nie słyszy pobudki.
- Actual exits: polnoc, poludniowy-wschod, wschod
- Existing inspectables: prycze skrzynie, tablica rozkaz, buty pasy

### Proposed Microimage
- anchor_object: prycze skrzynie [INSPECTABLE]
- physical_state: używane, ustawione równo albo zabrudzone pracą [LOCATION_DESCRIPTION]
- precise_position: przy ścianie albo na skraju gospodarczym [LOCATION_DESCRIPTION]
- physical_cause: codzienna praca, przechowywanie albo musztra [EXISTING_WORLD_FACT]
- relation_to_movement: zbiera ludzi wokół codziennej czynności [LOCATION_DESCRIPTION]
- relation_to_visibility: pokazuje porządek prac albo ustawienie zabudowań [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Kuchnia Garnizonowa; polnoc prowadzi ku Kuźnia Wojskowa [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: tablica rozkaz [INSPECTABLE]
- optional_examinable: prycze skrzynie [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Koszary Zachodnie to długi budynek z pryczami, skrzyniami i tablicą rozkazów. W środku zawsze ktoś śpi, ktoś czyści sprzęt, a ktoś inny udaje, że nie słyszy pobudki.
- LOCATION_NAME: Koszary Zachodnie
- INSPECTABLE: prycze skrzynie, tablica rozkaz, buty pasy
- EXIT_GEOMETRY: polnoc, poludniowy-wschod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Kuchnia Garnizonowa, polnoc:Kuźnia Wojskowa, poludniowy-wschod:Skręt ku Dungrim
- REGIONAL_MATERIAL: kamień, drewno, żelazo
- REGIONAL_PROCESS: wojsko i magazyny
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Koszary Zachodnie', 'secondary_details': ['prycze skrzynie', 'tablica rozkaz', 'buty pasy', 'Koszary Zachodnie to długi budynek z pryczami, skrzyniami i tablicą rozkazów'], 'historical_layer': 'żelazo, warta i zapasy'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Kuchnia Garnizonowa (forteczny) -> Kuchnia garnizonowa pracuje bez przerwy. Kotły, łopaty do pieca i ciężkie garnki są tu ważniejsze niż ozdoby, bo cała załoga ma jeść na czas.
- polnoc: Kuźnia Wojskowa (forteczny) -> Kuźnia wojskowa jest gorąca, ciasna i nieustannie pełna dźwięku metalu. Naprawia się tu groty, podkowy, nity i rzeczy, które nie mogą się zepsuć w czasie marszu.

### Variants
#### Variant A
- Trial short: Koszary Zachodnie
- Trial description: Na styku prycze skrzynie i sąsiedniego terenu widać używane, ustawione równo albo zabrudzone pracą. Roślinność wciska się pod krawężnik i pod ławę.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.082
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Koszary Zachodnie
- Trial description: Na styku tablica rozkaz i sąsiedniego terenu widać używane, ustawione równo albo zabrudzone pracą. Po jednej stronie leżą zaprawione kamienie, po drugiej szary żwir. Przy wejściu widać ślady zawracania i cięższy ruch. W wykopie zbiera się woda po ostatnim deszczu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.101
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Wrota Kopalni Żelaza (`390`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (woda wilgoc wilgoć strumien strumień vs lampy swiatlo światło).

### Existing Facts
- Existing description: Wrota Kopalni Żelaza. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: polnocny-zachod, wschod
- Existing inspectables: ruda zelazo żelazo zyla żyła, lampy swiatlo światło, woda wilgoc wilgoć strumien strumień

### Proposed Microimage
- anchor_object: woda wilgoc wilgoć strumien strumień [INSPECTABLE]
- physical_state: podmokłe, rozmiękłe albo zamulone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: spływ wody i osiadanie podłoża [REGIONAL_PROCESS]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: zasnuwa albo obniża widoczność przy krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: wschod prowadzi ku Plac Przed Szybem; polnocny-zachod prowadzi ku Zejście ku Kopalni Żelaza [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: lampy swiatlo światło [INSPECTABLE]
- optional_examinable: woda wilgoc wilgoć strumien strumień [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Wrota Kopalni Żelaza. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Wrota Kopalni Żelaza
- INSPECTABLE: ruda zelazo żelazo zyla żyła, lampy swiatlo światło, woda wilgoc wilgoć strumien strumień
- EXIT_GEOMETRY: polnocny-zachod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Plac Przed Szybem, polnocny-zachod:Zejście ku Kopalni Żelaza
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Wrota Kopalni Żelaza', 'secondary_details': ['ruda zelazo żelazo zyla żyła', 'lampy swiatlo światło', 'woda wilgoc wilgoć strumien strumień', 'Wrota Kopalni Żelaza'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Plac Przed Szybem (podziemny) -> Plac Przed Szybem. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- polnocny-zachod: Zejście ku Kopalni Żelaza (górski) -> Zejście ku Kopalni Żelaza. To nie jest miejsce dla kolumny wojska. To kraj zwiadowców, tragarzy, pasterzy i ludzi, którzy wiedzą, kiedy zawrócić. Każdy zakos odsłania inną cenę przejścia: czas, ostrożność albo krew.

### Variants
#### Variant A
- Trial short: Przejście na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody woda wilgoc wilgoć strumien strumień jest podmokłe, rozmiękłe albo zamulone, a spływ wody i osiadanie podłoża osypuje kamień niżej. Na kamieniach widać wyślizgane stopnie. Na dnie szybu leży wilgoć i luźny gruz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.085
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=REGIONAL_PROCESS, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście w lokalnym punkcie przejścia
- Trial description: Na lampy swiatlo światło widać pokryte pyłem, żużlem albo odpadkami; niższy stopień łapie spadający gruz. Z góry spada pył i drobne kamienie. Przy krawędzi stoi wygięta lina i pęknięty klin.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.080
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Plac Przed Szybem (`391`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kilofy narzedzia narzędzia vs stemple belki drewno).

### Existing Facts
- Existing description: Plac Przed Szybem. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: wschod, zachod
- Existing inspectables: stemple belki drewno, zawal zawał rumowisko, kilofy narzedzia narzędzia

### Proposed Microimage
- anchor_object: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_state: używane, ustawione równo albo zabrudzone pracą [LOCATION_DESCRIPTION]
- precise_position: na krawędzi pionowego przejścia [EXIT_GEOMETRY]
- physical_cause: codzienna praca, przechowywanie albo musztra [EXISTING_WORLD_FACT]
- relation_to_movement: zbiera ludzi wokół codziennej czynności [LOCATION_DESCRIPTION]
- relation_to_visibility: pokazuje porządek prac albo ustawienie zabudowań [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Wrota Kopalni Żelaza; wschod prowadzi ku Szopa Cechu Górników [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: stemple belki drewno [INSPECTABLE]
- optional_examinable: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Plac Przed Szybem. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Plac Przed Szybem
- INSPECTABLE: stemple belki drewno, zawal zawał rumowisko, kilofy narzedzia narzędzia
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Wrota Kopalni Żelaza, wschod:Szopa Cechu Górników
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Plac Przed Szybem', 'secondary_details': ['stemple belki drewno', 'zawal zawał rumowisko', 'kilofy narzedzia narzędzia', 'Plac Przed Szybem'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Wrota Kopalni Żelaza (podziemny) -> Wrota Kopalni Żelaza. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- wschod: Szopa Cechu Górników (podziemny) -> Szopa Cechu Górników. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Na krawędzi pionowego przejścia pionu
- Trial description: Przy krawędzi pionowego przejścia kilofy narzedzia narzędzia jest używane, ustawione równo albo zabrudzone pracą, a codzienna praca, przechowywanie albo musztra osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.202
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przy ścianie, fundamencie albo progu pionu
- Trial description: Przy ścianie, fundamencie albo progu stemple belki drewno jest używane, ustawione równo albo zabrudzone pracą, a codzienna praca, przechowywanie albo musztra osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.153
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Szopa Cechu Górników (`392`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (tory wozki wózki vs woda wilgoc wilgoć strumien strumień).

### Existing Facts
- Existing description: Szopa Cechu Górników. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: dol, poludnie, zachod
- Existing inspectables: tory wozki wózki, woda wilgoc wilgoć strumien strumień, szyb lina kolowrot kołowrót

### Proposed Microimage
- anchor_object: tory wozki wózki [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: zachod prowadzi ku Plac Przed Szybem; poludnie prowadzi ku Waga Rudy [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: woda wilgoc wilgoć strumien strumień [INSPECTABLE]
- optional_examinable: tory wozki wózki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Szopa Cechu Górników. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Szopa Cechu Górników
- INSPECTABLE: tory wozki wózki, woda wilgoc wilgoć strumien strumień, szyb lina kolowrot kołowrót
- EXIT_GEOMETRY: dol, poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Plac Przed Szybem, poludnie:Waga Rudy, dol:Nisza z Lampami
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Szopa Cechu Górników', 'secondary_details': ['tory wozki wózki', 'woda wilgoc wilgoć strumien strumień', 'szyb lina kolowrot kołowrót', 'Szopa Cechu Górników'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Plac Przed Szybem (podziemny) -> Plac Przed Szybem. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- poludnie: Waga Rudy (podziemny) -> Waga Rudy. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Przejście w osi przejazdu albo przy zwężeniu
- Trial description: Na tory wozki wózki widać wydeptane i przeorane koleinami; niższy stopień łapie spadający gruz. Z góry spada pył i drobne kamienie. Przy krawędzi stoi wygięta lina i pęknięty klin.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.080
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście na dolnej krawędzi terenu albo przy brzegu wody
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody woda wilgoc wilgoć strumien strumień jest podmokłe, rozmiękłe albo zamulone, a ruch wozów i stałe przejazdy osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.055
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Waga Rudy (`393`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kilofy narzedzia narzędzia vs lampy swiatlo światło).

### Existing Facts
- Existing description: Waga Rudy. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: polnoc, zachod
- Existing inspectables: lampy swiatlo światło, kilofy narzedzia narzędzia, ruda zelazo żelazo zyla żyła

### Proposed Microimage
- anchor_object: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_state: pokryte pyłem, żużlem albo odpadkami [HUMAN_REVIEW_REQUIRED]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: wilgoć, cień albo praca rolnicza [REGIONAL_PROCESS]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnoc prowadzi ku Szopa Cechu Górników; zachod prowadzi ku Stary Kołowrót [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: lampy swiatlo światło [INSPECTABLE]
- optional_examinable: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Waga Rudy. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Waga Rudy
- INSPECTABLE: lampy swiatlo światło, kilofy narzedzia narzędzia, ruda zelazo żelazo zyla żyła
- EXIT_GEOMETRY: polnoc, zachod
- NEIGHBOUR_CONTINUITY: polnoc:Szopa Cechu Górników, zachod:Stary Kołowrót
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Waga Rudy', 'secondary_details': ['lampy swiatlo światło', 'kilofy narzedzia narzędzia', 'ruda zelazo żelazo zyla żyła', 'Waga Rudy'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Szopa Cechu Górników (podziemny) -> Szopa Cechu Górników. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- zachod: Stary Kołowrót (podziemny) -> Stary Kołowrót. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: W lokalnym punkcie przejścia pionu
- Trial description: Przy lokalnym punkcie przejścia kilofy narzedzia narzędzia jest pokryte pyłem, żużlem albo odpadkami, a wilgoć, cień albo praca rolnicza osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.203
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W lokalnym punkcie przejścia pionu
- Trial description: Przy lokalnym punkcie przejścia lampy swiatlo światło jest pokryte pyłem, żużlem albo odpadkami, a wilgoć, cień albo praca rolnicza osypuje kamień niżej. Skarpa urywa się przy kamiennym progu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.097
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Stary Kołowrót (`394`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (stemple belki drewno vs szyb lina kolowrot kołowrót).

### Existing Facts
- Existing description: Stary Kołowrót. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: dol, wschod
- Existing inspectables: zawal zawał rumowisko, szyb lina kolowrot kołowrót, stemple belki drewno

### Proposed Microimage
- anchor_object: stemple belki drewno [INSPECTABLE]
- physical_state: pokryte pyłem, żużlem albo odpadkami [HUMAN_REVIEW_REQUIRED]
- precise_position: przy ścianie, fundamencie albo progu [LOCATION_DESCRIPTION]
- physical_cause: obróbka, transport lub czyszczenie [HUMAN_REVIEW_REQUIRED]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: wschod prowadzi ku Waga Rudy; dol prowadzi ku Zjazd do Górnego Chodnika [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: szyb lina kolowrot kołowrót [INSPECTABLE]
- optional_examinable: stemple belki drewno [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Stary Kołowrót. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Stary Kołowrót
- INSPECTABLE: zawal zawał rumowisko, szyb lina kolowrot kołowrót, stemple belki drewno
- EXIT_GEOMETRY: dol, wschod
- NEIGHBOUR_CONTINUITY: wschod:Waga Rudy, dol:Zjazd do Górnego Chodnika
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Stary Kołowrót', 'secondary_details': ['zawal zawał rumowisko', 'szyb lina kolowrot kołowrót', 'stemple belki drewno', 'Stary Kołowrót'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Waga Rudy (podziemny) -> Waga Rudy. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- dol: Zjazd do Górnego Chodnika (podziemny) -> Zjazd do Górnego Chodnika. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Sadza na ścianach Kopalnia_Zelaza
- Trial description: Przy ścianie, fundamencie albo progu stemple belki drewno jest pokryte pyłem, żużlem albo odpadkami, a obróbka, transport lub czyszczenie osypuje kamień niżej. Skarpa urywa się przy kamiennym progu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.060
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=LOCATION_DESCRIPTION, physical_cause=HUMAN_REVIEW_REQUIRED, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Sadza na ścianach Kopalnia_Zelaza
- Trial description: Urwisko urywa dojście od dołu. Na szyb lina kolowrot kołowrót widać pochylone, osypujące się albo mocno wydeptane; niższy stopień łapie spadający gruz. Przy krawędzi stoi wygięta lina i pęknięty klin.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.042
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=REGIONAL_PROCESS, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=EXIT_GEOMETRY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Zjazd do Górnego Chodnika (`395`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (tory wozki wózki vs woda wilgoc wilgoć strumien strumień).

### Existing Facts
- Existing description: Zjazd do Górnego Chodnika. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: gora, wschod
- Existing inspectables: woda wilgoc wilgoć strumien strumień, ruda zelazo żelazo zyla żyła, tory wozki wózki

### Proposed Microimage
- anchor_object: tory wozki wózki [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: gora prowadzi ku Stary Kołowrót; wschod prowadzi ku Górny Chodnik Północny [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: woda wilgoc wilgoć strumien strumień [INSPECTABLE]
- optional_examinable: tory wozki wózki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Zjazd do Górnego Chodnika. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Zjazd do Górnego Chodnika
- INSPECTABLE: woda wilgoc wilgoć strumien strumień, ruda zelazo żelazo zyla żyła, tory wozki wózki
- EXIT_GEOMETRY: gora, wschod
- NEIGHBOUR_CONTINUITY: gora:Stary Kołowrót, wschod:Górny Chodnik Północny
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Zjazd do Górnego Chodnika', 'secondary_details': ['woda wilgoc wilgoć strumien strumień', 'ruda zelazo żelazo zyla żyła', 'tory wozki wózki', 'Zjazd do Górnego Chodnika'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- gora: Stary Kołowrót (podziemny) -> Stary Kołowrót. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- wschod: Górny Chodnik Północny (podziemny) -> Górny Chodnik Północny. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Zjazd do Górnego Chodnika
- Trial description: Na tory wozki wózki widać wydeptane i przeorane koleinami; niższy stopień łapie spadający gruz. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.121
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Zjazd do Górnego Chodnika
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody woda wilgoc wilgoć strumien strumień jest podmokłe, rozmiękłe albo zamulone, a ruch wozów i stałe przejazdy osypuje kamień niżej. Skarpa urywa się przy kamiennym progu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.021
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Górny Chodnik Północny (`396`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kilofy narzedzia narzędzia vs lampy swiatlo światło).

### Existing Facts
- Existing description: Górny Chodnik Północny. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: wschod, zachod
- Existing inspectables: kilofy narzedzia narzędzia, stemple belki drewno, lampy swiatlo światło

### Proposed Microimage
- anchor_object: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_state: pokryte pyłem, żużlem albo odpadkami [HUMAN_REVIEW_REQUIRED]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: wilgoć, cień albo praca rolnicza [REGIONAL_PROCESS]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: zachod prowadzi ku Zjazd do Górnego Chodnika; wschod prowadzi ku Nisza z Lampami [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: lampy swiatlo światło [INSPECTABLE]
- optional_examinable: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Górny Chodnik Północny. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Górny Chodnik Północny
- INSPECTABLE: kilofy narzedzia narzędzia, stemple belki drewno, lampy swiatlo światło
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Zjazd do Górnego Chodnika, wschod:Nisza z Lampami
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Górny Chodnik Północny', 'secondary_details': ['kilofy narzedzia narzędzia', 'stemple belki drewno', 'lampy swiatlo światło', 'Górny Chodnik Północny'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Zjazd do Górnego Chodnika (podziemny) -> Zjazd do Górnego Chodnika. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- wschod: Nisza z Lampami (podziemny) -> Nisza z Lampami. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: W lokalnym punkcie przejścia pionu
- Trial description: Przy lokalnym punkcie przejścia kilofy narzedzia narzędzia jest pokryte pyłem, żużlem albo odpadkami, a wilgoć, cień albo praca rolnicza osypuje kamień niżej. Skarpa urywa się przy kamiennym progu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.097
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W lokalnym punkcie przejścia pionu
- Trial description: Na lampy swiatlo światło widać pokryte pyłem, żużlem albo odpadkami; niższy stopień łapie spadający gruz. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.113
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Nisza z Lampami (`397`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (tory wozki wózki vs szyb lina kolowrot kołowrót).

### Existing Facts
- Existing description: Nisza z Lampami. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: gora, polnocny-wschod, zachod
- Existing inspectables: szyb lina kolowrot kołowrót, tory wozki wózki, zawal zawał rumowisko

### Proposed Microimage
- anchor_object: tory wozki wózki [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: zbiera wzrok na małym punkcie przy drodze [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Górny Chodnik Północny; polnocny-wschod prowadzi ku Skład Kilofów [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: szyb lina kolowrot kołowrót [INSPECTABLE]
- optional_examinable: tory wozki wózki [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Nisza z Lampami. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Nisza z Lampami
- INSPECTABLE: szyb lina kolowrot kołowrót, tory wozki wózki, zawal zawał rumowisko
- EXIT_GEOMETRY: gora, polnocny-wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Górny Chodnik Północny, polnocny-wschod:Skład Kilofów, gora:Szopa Cechu Górników
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Nisza z Lampami', 'secondary_details': ['szyb lina kolowrot kołowrót', 'tory wozki wózki', 'zawal zawał rumowisko', 'Nisza z Lampami'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Górny Chodnik Północny (podziemny) -> Górny Chodnik Północny. Stempli jest tu więcej niż zaufania. Każdy trzyma skałę, lecz żaden nie wygląda na wieczny. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- polnocny-wschod: Skład Kilofów (podziemny) -> Skład Kilofów. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Wydeptane i przeorane koleinami
- Trial description: Przy osi przejazdu albo przy zwężeniu tory wozki wózki jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.112
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Osadzone od dotyku, wosku albo ofiar
- Trial description: Przy u podstawy kapliczki lub w niszy szyb lina kolowrot kołowrót jest osadzone od dotyku, wosku albo ofiar, a ruch wozów i stałe przejazdy osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.046
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Skład Kilofów (`398`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (woda wilgoc wilgoć strumien strumień vs lampy swiatlo światło).

### Existing Facts
- Existing description: Skład Kilofów. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: poludniowy-zachod, wschod
- Existing inspectables: ruda zelazo żelazo zyla żyła, lampy swiatlo światło, woda wilgoc wilgoć strumien strumień

### Proposed Microimage
- anchor_object: woda wilgoc wilgoć strumien strumień [INSPECTABLE]
- physical_state: podmokłe, rozmiękłe albo zamulone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: spływ wody i osiadanie podłoża [REGIONAL_PROCESS]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: zasnuwa albo obniża widoczność przy krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: poludniowy-zachod prowadzi ku Nisza z Lampami; wschod prowadzi ku Ślepy Przodek [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: lampy swiatlo światło [INSPECTABLE]
- optional_examinable: woda wilgoc wilgoć strumien strumień [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Skład Kilofów. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Skład Kilofów
- INSPECTABLE: ruda zelazo żelazo zyla żyła, lampy swiatlo światło, woda wilgoc wilgoć strumien strumień
- EXIT_GEOMETRY: poludniowy-zachod, wschod
- NEIGHBOUR_CONTINUITY: poludniowy-zachod:Nisza z Lampami, wschod:Ślepy Przodek
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Skład Kilofów', 'secondary_details': ['ruda zelazo żelazo zyla żyła', 'lampy swiatlo światło', 'woda wilgoc wilgoć strumien strumień', 'Skład Kilofów'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- poludniowy-zachod: Nisza z Lampami (podziemny) -> Nisza z Lampami. Czerwonawe żyły w kamieniu przypominają zaschnięte rany góry, z których ludzie uczynili dochód. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- wschod: Ślepy Przodek (podziemny) -> Ślepy Przodek. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Wilgoć w spoinach Kopalnia_Zelaza
- Trial description: Przy dolnej krawędzi terenu albo przy brzegu wody woda wilgoc wilgoć strumien strumień jest podmokłe, rozmiękłe albo zamulone, a spływ wody i osiadanie podłoża osypuje kamień niżej. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.105
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=REGIONAL_PROCESS, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Wilgoć w spoinach Kopalnia_Zelaza
- Trial description: Na lampy swiatlo światło widać pokryte pyłem, żużlem albo odpadkami; niższy stopień łapie spadający gruz. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.128
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Ślepy Przodek (`399`)
- Area: `Kopalnia_Zelaza`
- Family: `vertical`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kilofy narzedzia narzędzia vs stemple belki drewno).

### Existing Facts
- Existing description: Ślepy Przodek. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- Actual exits: poludnie, poludniowy-wschod, zachod
- Existing inspectables: stemple belki drewno, zawal zawał rumowisko, kilofy narzedzia narzędzia

### Proposed Microimage
- anchor_object: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_state: pokryte pyłem, żużlem albo odpadkami [HUMAN_REVIEW_REQUIRED]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: wilgoć, cień albo praca rolnicza [REGIONAL_PROCESS]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: zachod prowadzi ku Skład Kilofów; poludnie prowadzi ku Rozwidlenie Pod Stemplami [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: stemple belki drewno [INSPECTABLE]
- optional_examinable: kilofy narzedzia narzędzia [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Ślepy Przodek. W korytarzach stoją stemple, lampy i świeże kliny wbite w skałę. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- LOCATION_NAME: Ślepy Przodek
- INSPECTABLE: stemple belki drewno, zawal zawał rumowisko, kilofy narzedzia narzędzia
- EXIT_GEOMETRY: poludnie, poludniowy-wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Skład Kilofów, poludnie:Rozwidlenie Pod Stemplami, poludniowy-wschod:Schody do Drugiego Poziomu
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: wydobycie
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Ślepy Przodek', 'secondary_details': ['stemple belki drewno', 'zawal zawał rumowisko', 'kilofy narzedzia narzędzia', 'Ślepy Przodek'], 'historical_layer': 'wydobycie i obudowa chodników'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Skład Kilofów (podziemny) -> Skład Kilofów. Światło lamp nie rozprasza ciemności, tylko pokazuje, gdzie zaczyna się następna. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.
- poludnie: Rozwidlenie Pod Stemplami (podziemny) -> Rozwidlenie Pod Stemplami. Powietrze jest ciężkie od rdzy, potu i mokrego drewna, a każdy dźwięk idzie dalej, niż powinien. Każdy chodnik ma tu praktyczny sens: prowadzi do rudy, powietrza, wody albo wyjścia, jeśli góra pozwoli.

### Variants
#### Variant A
- Trial short: Ślepy Przodek
- Trial description: Na kilofy narzedzia narzędzia widać pokryte pyłem, żużlem albo odpadkami; niższy stopień łapie spadający gruz. Lina ocierała skałę przy zakręcie.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.114
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Ślepy Przodek
- Trial description: Schody urywają się przy skalnym gzymsie. Na stemple belki drewno widać pokryte pyłem, żużlem albo odpadkami; niższy stopień łapie spadający gruz. Na dnie szybu leży wilgoć i luźny gruz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.091
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=LOCATION_DESCRIPTION, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Krzyżowy Kamień (`81`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kamien znak vs kreda ogloszenia).

### Existing Facts
- Existing description: Przy rozstaju stoi głaz z naciętym znakiem i śladami kredy po dawnych oznaczeniach. Miejscowi zostawiają tu informacje, wiązki sznurka i wiadomości, których nie warto wozić dalej niż trzeba.
- Actual exits: poludnie, wschod
- Existing inspectables: kamien znak, kreda ogloszenia, rozstaje droga

### Proposed Microimage
- anchor_object: kamien znak [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: poludnie prowadzi ku Droga do Haldun; wschod prowadzi ku Pierwsze Zagony [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: kreda ogloszenia [INSPECTABLE]
- optional_examinable: kamien znak [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Przy rozstaju stoi głaz z naciętym znakiem i śladami kredy po dawnych oznaczeniach. Miejscowi zostawiają tu informacje, wiązki sznurka i wiadomości, których nie warto wozić dalej niż trzeba.
- LOCATION_NAME: Krzyżowy Kamień
- INSPECTABLE: kamien znak, kreda ogloszenia, rozstaje droga
- EXIT_GEOMETRY: poludnie, wschod
- NEIGHBOUR_CONTINUITY: poludnie:Droga do Haldun, wschod:Pierwsze Zagony
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Krzyżowy Kamień', 'secondary_details': ['kamien znak', 'kreda ogloszenia', 'rozstaje droga', 'Przy rozstaju stoi głaz z naciętym znakiem i śladami kredy po dawnych oznaczeniach'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- poludnie: Droga do Haldun (wiejski) -> Droga do Haldun wychodzi z podmiejskiego błota i przechodzi w udeptany trakt pomiędzy zagonami. Widać stąd zarówno wieś, jak i wielki ruch wokół niej: wozy, psy, ptaki i ludzi, którzy zawsze gdzieś się spieszą.
- wschod: Pierwsze Zagony (wiejski) -> Pierwsze zagony są wąskie, ale już dobrze wytyczone. Tutaj zaczyna się ziemia, która musi wyżywić domy, stodoły i tych, którzy nie chcą pracować ciężej niż trzeba.

### Variants
#### Variant A
- Trial short: W lokalnym punkcie przejścia w lokalnym punkcie przejścia
- Trial description: Przy lokalnym punkcie przejścia kamien znak jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Na skraju drogi leżą połamane gałęzie. Światło jest ostre i nierówne na całej długości zbocza.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.122
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W lokalnym punkcie przejścia w lokalnym punkcie przejścia
- Trial description: W oddali widać linię drzew i płytki jar. Przy lokalnym punkcie przejścia kreda ogloszenia jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Światło jest ostre i nierówne na całej długości zbocza.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.126
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Pierwsze Zagony (`82`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (narzedzia sierp vs sadzonki ziemia).

### Existing Facts
- Existing description: Pierwsze zagony są wąskie, ale już dobrze wytyczone. Tutaj zaczyna się ziemia, która musi wyżywić domy, stodoły i tych, którzy nie chcą pracować ciężej niż trzeba.
- Actual exits: wschod, zachod
- Existing inspectables: sadzonki ziemia, strach na wróble, narzedzia sierp

### Proposed Microimage
- anchor_object: narzedzia sierp [INSPECTABLE]
- physical_state: wilgotne, przygniecione albo szerzej rozstawione [LOCATION_DESCRIPTION]
- precise_position: na skraju roślinności lub pola [NEIGHBOUR_CONTINUITY]
- physical_cause: nachylenie terenu i osypywanie materiału [REGIONAL_PROCESS]
- relation_to_movement: wyznacza pieszy przejście między roślinnością [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: przysłania skraj przejścia albo otwiera widok na pole [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: zachod prowadzi ku Krzyżowy Kamień; wschod prowadzi ku Studnia Haldun [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: sadzonki ziemia [INSPECTABLE]
- optional_examinable: narzedzia sierp [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Pierwsze zagony są wąskie, ale już dobrze wytyczone. Tutaj zaczyna się ziemia, która musi wyżywić domy, stodoły i tych, którzy nie chcą pracować ciężej niż trzeba.
- LOCATION_NAME: Pierwsze Zagony
- INSPECTABLE: sadzonki ziemia, strach na wróble, narzedzia sierp
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Krzyżowy Kamień, wschod:Studnia Haldun
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Pierwsze Zagony', 'secondary_details': ['sadzonki ziemia', 'strach na wróble', 'narzedzia sierp', 'Pierwsze zagony są wąskie, ale już dobrze wytyczone'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Krzyżowy Kamień (wiejski) -> Przy rozstaju stoi głaz z naciętym znakiem i śladami kredy po dawnych oznaczeniach. Miejscowi zostawiają tu informacje, wiązki sznurka i wiadomości, których nie warto wozić dalej niż trzeba.
- wschod: Studnia Haldun (wiejski) -> Studnia stoi pośrodku wsi jak punkt odniesienia dla wszystkich spraw. Przy cembrowinie leżą wiadra, sznury i ślady butów tak głębokie, że widać, kto przychodzi tu codziennie, a kto tylko raz.

### Variants
#### Variant A
- Trial short: Haldun na skraju roślinności lub pola
- Trial description: Sztucznie usypany nasyp przecina otwarty teren. Na narzedzia sierp widać wilgotne, przygniecione albo szerzej rozstawione; wiatr i spływ rozcinają zbocze. Słychać kamyki zsuwające się po zboczu.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.053
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=REGIONAL_PROCESS, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Haldun na skraju roślinności lub pola
- Trial description: Na sadzonki ziemia widać wilgotne, przygniecione albo szerzej rozstawione; wiatr i spływ rozcinają zbocze. Na skraju drogi leżą połamane gałęzie. Światło jest ostre i nierówne na całej długości zbocza.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.130
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=REGIONAL_PROCESS, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Zagony pod Wierzbami (`84`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (wierzby cień vs ślad wóz).

### Existing Facts
- Existing description: Zagony pod Wierzbami leżą szerzej niż pierwsze pola i widać po nich, że ziemia dostaje tu więcej uwagi niż gdzie indziej. Wierzby dają cień, ale też zbierają wilgoć, więc rolnicy pracują tu ostrożniej.
- Actual exits: polnocny-zachod, poludnie, poludniowy-wschod
- Existing inspectables: wierzby cień, zboze łany, ślad wóz

### Proposed Microimage
- anchor_object: wierzby cień [INSPECTABLE]
- physical_state: wilgotne, przygniecione albo szerzej rozstawione [LOCATION_DESCRIPTION]
- precise_position: na skraju roślinności lub pola [NEIGHBOUR_CONTINUITY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wyznacza pieszy przejście między roślinnością [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: przysłania skraj przejścia albo otwiera widok na pole [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: polnocny-zachod prowadzi ku Studnia Haldun; poludnie prowadzi ku Chata Sołtysa [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: ślad wóz [INSPECTABLE]
- optional_examinable: wierzby cień [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Zagony pod Wierzbami leżą szerzej niż pierwsze pola i widać po nich, że ziemia dostaje tu więcej uwagi niż gdzie indziej. Wierzby dają cień, ale też zbierają wilgoć, więc rolnicy pracują tu ostrożniej.
- LOCATION_NAME: Zagony pod Wierzbami
- INSPECTABLE: wierzby cień, zboze łany, ślad wóz
- EXIT_GEOMETRY: polnocny-zachod, poludnie, poludniowy-wschod
- NEIGHBOUR_CONTINUITY: polnocny-zachod:Studnia Haldun, poludnie:Chata Sołtysa, poludniowy-wschod:Droga przy Łanach
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Zagony pod Wierzbami', 'secondary_details': ['wierzby cień', 'zboze łany', 'ślad wóz', 'Zagony pod Wierzbami leżą szerzej niż pierwsze pola i widać po nich, że ziemia dostaje tu więcej uwagi niż gdzie indziej'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnocny-zachod: Studnia Haldun (wiejski) -> Studnia stoi pośrodku wsi jak punkt odniesienia dla wszystkich spraw. Przy cembrowinie leżą wiadra, sznury i ślady butów tak głębokie, że widać, kto przychodzi tu codziennie, a kto tylko raz.
- poludnie: Chata Sołtysa (wiejski) -> Chata sołtysa stoi bliżej środka wsi niż większość domów, bo tu przychodzą sprawy, które trzeba liczyć, spisywać i rozstrzygać. Przy drzwiach wisi deska z ogłoszeniami, a na ławie leży księga zapisów.

### Variants
#### Variant A
- Trial short: Wydeptana ziemia wiejski
- Trial description: Przy skraju roślinności lub pola wierzby cień jest wilgotne, przygniecione albo szerzej rozstawione, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Po obu stronach widać inne nachylenie gruntu. Powietrze jest suche i ruchliwe od wiatru. Przy samej krawędzi leży żwir i kilka gałęzi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.102
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Wydeptana ziemia wiejski
- Trial description: Grzbiet przechodzi w niższy jar bez wyraźnej krawędzi. Przy osi przejazdu albo przy zwężeniu ślad wóz jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Powietrze jest suche i ruchliwe od wiatru. Przy samej krawędzi leży żwir i kilka gałęzi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.104
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Chata Sołtysa (`85`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (deska ogloszenia vs drzwi próg).

### Existing Facts
- Existing description: Chata sołtysa stoi bliżej środka wsi niż większość domów, bo tu przychodzą sprawy, które trzeba liczyć, spisywać i rozstrzygać. Przy drzwiach wisi deska z ogłoszeniami, a na ławie leży księga zapisów.
- Actual exits: polnoc, zachod
- Existing inspectables: deska ogloszenia, ksiega wpisy, drzwi próg

### Proposed Microimage
- anchor_object: deska ogloszenia [INSPECTABLE]
- physical_state: wyszlifowane, starte albo nadkruszone [INSPECTABLE]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: ciągłe otwieranie, zamykanie i obsługa warty [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnoc prowadzi ku Zagony pod Wierzbami; zachod prowadzi ku Obora pod Wierzbami [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: drzwi próg [INSPECTABLE]
- optional_examinable: deska ogloszenia [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Chata sołtysa stoi bliżej środka wsi niż większość domów, bo tu przychodzą sprawy, które trzeba liczyć, spisywać i rozstrzygać. Przy drzwiach wisi deska z ogłoszeniami, a na ławie leży księga zapisów.
- LOCATION_NAME: Chata Sołtysa
- INSPECTABLE: deska ogloszenia, ksiega wpisy, drzwi próg
- EXIT_GEOMETRY: polnoc, zachod
- NEIGHBOUR_CONTINUITY: polnoc:Zagony pod Wierzbami, zachod:Obora pod Wierzbami
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Chata Sołtysa', 'secondary_details': ['deska ogloszenia', 'ksiega wpisy', 'drzwi próg', 'Chata sołtysa stoi bliżej środka wsi niż większość domów, bo tu przychodzą sprawy, które trzeba liczyć, spisywać i rozstrzygać'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Zagony pod Wierzbami (wiejski) -> Zagony pod Wierzbami leżą szerzej niż pierwsze pola i widać po nich, że ziemia dostaje tu więcej uwagi niż gdzie indziej. Wierzby dają cień, ale też zbierają wilgoć, więc rolnicy pracują tu ostrożniej.
- zachod: Obora pod Wierzbami (wiejski) -> Obora stoi przy zaroślach i pachnie sianem, mlekiem oraz mokrą deską. Nie jest duża, ale miejscowi trzymają tu zwierzęta lepiej niż wiele większych gospodarstw.

### Variants
#### Variant A
- Trial short: W lokalnym punkcie przejścia w lokalnym punkcie przejścia
- Trial description: Przy lokalnym punkcie przejścia deska ogloszenia jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zmienia krawędź terenu. Na grzbiecie stoi samotny głaz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.267
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przy wejściu lub przy przejeździe przy wejściu lub przy przejeździe
- Trial description: Szeroki stok opada ku dolinie. Przy wejściu lub przy przejeździe drzwi próg jest wyszlifowane, starte albo nadkruszone, a ciągłe otwieranie, zamykanie i obsługa warty zmienia krawędź terenu. Wiatr niesie kurz ze zbocza. Na krawędzi leży kilka odłamków kamienia.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.091
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Obora pod Wierzbami (`86`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (krowy żłób vs żłób siano).

### Existing Facts
- Existing description: Obora stoi przy zaroślach i pachnie sianem, mlekiem oraz mokrą deską. Nie jest duża, ale miejscowi trzymają tu zwierzęta lepiej niż wiele większych gospodarstw.
- Actual exits: wschod, zachod
- Existing inspectables: krowy żłób, żłób siano, drzwi zagroda

### Proposed Microimage
- anchor_object: krowy żłób [INSPECTABLE]
- physical_state: używane, ustawione równo albo zabrudzone pracą [LOCATION_DESCRIPTION]
- precise_position: przy ścianie albo na skraju gospodarczym [LOCATION_DESCRIPTION]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: zbiera ludzi wokół codziennej czynności [LOCATION_DESCRIPTION]
- relation_to_visibility: pokazuje porządek prac albo ustawienie zabudowań [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: wschod prowadzi ku Chata Sołtysa; zachod prowadzi ku Stodoły Zachodnie [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: żłób siano [INSPECTABLE]
- optional_examinable: krowy żłób [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Obora stoi przy zaroślach i pachnie sianem, mlekiem oraz mokrą deską. Nie jest duża, ale miejscowi trzymają tu zwierzęta lepiej niż wiele większych gospodarstw.
- LOCATION_NAME: Obora pod Wierzbami
- INSPECTABLE: krowy żłób, żłób siano, drzwi zagroda
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: wschod:Chata Sołtysa, zachod:Stodoły Zachodnie
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Obora pod Wierzbami', 'secondary_details': ['krowy żłób', 'żłób siano', 'drzwi zagroda', 'Obora stoi przy zaroślach i pachnie sianem, mlekiem oraz mokrą deską'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Chata Sołtysa (wiejski) -> Chata sołtysa stoi bliżej środka wsi niż większość domów, bo tu przychodzą sprawy, które trzeba liczyć, spisywać i rozstrzygać. Przy drzwiach wisi deska z ogłoszeniami, a na ławie leży księga zapisów.
- zachod: Stodoły Zachodnie (wiejski) -> Kilka stodół stoi tu obok siebie jak długi magazyn wsi. Powietrze pachnie słomą, pyłem i drewnem, a deski szumią przy każdym mocniejszym podmuchu.

### Variants
#### Variant A
- Trial short: Haldun przy ścianie albo na skraju gospodarczym
- Trial description: Grzbiet przechodzi w niższy jar bez wyraźnej krawędzi. Przy ścianie albo na skraju gospodarczym krowy żłób jest używane, ustawione równo albo zabrudzone pracą, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Powietrze jest suche i ruchliwe od wiatru. Przy samej krawędzi leży żwir i kilka gałęzi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.101
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Haldun przy ścianie albo na skraju gospodarczym
- Trial description: Szeroki stok opada ku dolinie. Przy ścianie albo na skraju gospodarczym żłób siano jest używane, ustawione równo albo zabrudzone pracą, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Wiatr niesie kurz ze zbocza. Na krawędzi leży kilka odłamków kamienia.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.095
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Stodoły Zachodnie (`87`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (wóz siano vs belka krokiew).

### Existing Facts
- Existing description: Kilka stodół stoi tu obok siebie jak długi magazyn wsi. Powietrze pachnie słomą, pyłem i drewnem, a deski szumią przy każdym mocniejszym podmuchu.
- Actual exits: poludniowy-zachod, wschod
- Existing inspectables: stodoła dach, wóz siano, belka krokiew

### Proposed Microimage
- anchor_object: wóz siano [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: prowadzi ruch wozów i pieszych w jednym śladzie [EXIT_GEOMETRY]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: wschod prowadzi ku Obora pod Wierzbami; poludniowy-zachod prowadzi ku Młynny Rów [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: belka krokiew [INSPECTABLE]
- optional_examinable: wóz siano [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Kilka stodół stoi tu obok siebie jak długi magazyn wsi. Powietrze pachnie słomą, pyłem i drewnem, a deski szumią przy każdym mocniejszym podmuchu.
- LOCATION_NAME: Stodoły Zachodnie
- INSPECTABLE: stodoła dach, wóz siano, belka krokiew
- EXIT_GEOMETRY: poludniowy-zachod, wschod
- NEIGHBOUR_CONTINUITY: wschod:Obora pod Wierzbami, poludniowy-zachod:Młynny Rów
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Stodoły Zachodnie', 'secondary_details': ['stodoła dach', 'wóz siano', 'belka krokiew', 'Kilka stodół stoi tu obok siebie jak długi magazyn wsi'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- wschod: Obora pod Wierzbami (wiejski) -> Obora stoi przy zaroślach i pachnie sianem, mlekiem oraz mokrą deską. Nie jest duża, ale miejscowi trzymają tu zwierzęta lepiej niż wiele większych gospodarstw.
- poludniowy-zachod: Młynny Rów (wiejski) -> Młynny rów prowadzi wodę do koła i oddaje ją dalej, wzdłuż zabudowań. Woda szumi tu stale, a pył mączny osiada na kamieniu i deskach jak cienka warstwa śniegu.

### Variants
#### Variant A
- Trial short: Wydeptana ziemia wiejski
- Trial description: Przy osi przejazdu albo przy zwężeniu wóz siano jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Kamienie przy krawędzi noszą zacieki po deszczu, a niżej leży wąski pas trawy.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.089
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Wydeptana ziemia wiejski
- Trial description: Przy ścianie, fundamencie albo progu belka krokiew jest rozjechana i pofalowana, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Na skraju drogi leżą połamane gałęzie. Światło jest ostre i nierówne na całej długości zbocza.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.133
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Młynny Rów (`88`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (koło woda vs pył mąka).

### Existing Facts
- Existing description: Młynny rów prowadzi wodę do koła i oddaje ją dalej, wzdłuż zabudowań. Woda szumi tu stale, a pył mączny osiada na kamieniu i deskach jak cienka warstwa śniegu.
- Actual exits: polnocny-wschod, poludnie
- Existing inspectables: koło woda, sluz rów, pył mąka

### Proposed Microimage
- anchor_object: koło woda [INSPECTABLE]
- physical_state: podmokłe, rozmiękłe albo zamulone [INSPECTABLE]
- precise_position: na dolnej krawędzi terenu albo przy brzegu wody [NEIGHBOUR_CONTINUITY]
- physical_cause: spływ wody i osiadanie podłoża [REGIONAL_PROCESS]
- relation_to_movement: wymusza ostrożny krok albo omijanie mokrej krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_visibility: zasnuwa albo obniża widoczność przy krawędzi [NEIGHBOUR_CONTINUITY]
- relation_to_neighbouring_locations: polnocny-wschod prowadzi ku Stodoły Zachodnie; poludnie prowadzi ku Mostek nad Strugą [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: pył mąka [INSPECTABLE]
- optional_examinable: koło woda [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Młynny rów prowadzi wodę do koła i oddaje ją dalej, wzdłuż zabudowań. Woda szumi tu stale, a pył mączny osiada na kamieniu i deskach jak cienka warstwa śniegu.
- LOCATION_NAME: Młynny Rów
- INSPECTABLE: koło woda, sluz rów, pył mąka
- EXIT_GEOMETRY: polnocny-wschod, poludnie
- NEIGHBOUR_CONTINUITY: polnocny-wschod:Stodoły Zachodnie, poludnie:Mostek nad Strugą
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Młynny Rów', 'secondary_details': ['koło woda', 'sluz rów', 'pył mąka', 'Młynny rów prowadzi wodę do koła i oddaje ją dalej, wzdłuż zabudowań'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnocny-wschod: Stodoły Zachodnie (wiejski) -> Kilka stodół stoi tu obok siebie jak długi magazyn wsi. Powietrze pachnie słomą, pyłem i drewnem, a deski szumią przy każdym mocniejszym podmuchu.
- poludnie: Mostek nad Strugą (wiejski) -> Mostek łączy oba brzegi strugi tak, by wóz nie musiał brnąć przez wodę. W tym miejscu zbiegają się gospodarstwa, handel i ścieżki, więc zawsze ktoś tu stoi choćby na chwilę.

### Variants
#### Variant A
- Trial short: Koło woda
- Trial description: Grzbiet przechodzi w niższy jar bez wyraźnej krawędzi. Na koło woda widać podmokłe, rozmiękłe albo zamulone; wiatr i spływ rozcinają zbocze. Powietrze jest suche i ruchliwe od wiatru. Przy samej krawędzi leży żwir i kilka gałęzi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.079
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=NEIGHBOUR_CONTINUITY, physical_cause=REGIONAL_PROCESS, relation_to_movement=NEIGHBOUR_CONTINUITY, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Pył mąka
- Trial description: Grzbiet przechodzi w niższy jar bez wyraźnej krawędzi. Na pył mąka widać podmokłe, rozmiękłe albo zamulone; wiatr i spływ rozcinają zbocze. Powietrze jest suche i ruchliwe od wiatru. Przy samej krawędzi leży żwir i kilka gałęzi.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: True
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.079
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=NEIGHBOUR_CONTINUITY, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Mostek nad Strugą (`89`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (deski most vs handel wóz).

### Existing Facts
- Existing description: Mostek łączy oba brzegi strugi tak, by wóz nie musiał brnąć przez wodę. W tym miejscu zbiegają się gospodarstwa, handel i ścieżki, więc zawsze ktoś tu stoi choćby na chwilę.
- Actual exits: polnoc, wschod
- Existing inspectables: deski most, struga nurt, handel wóz

### Proposed Microimage
- anchor_object: deski most [INSPECTABLE]
- physical_state: wydeptane i przeorane koleinami [LOCATION_DESCRIPTION]
- precise_position: w osi przejazdu albo przy zwężeniu [EXIT_GEOMETRY]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: polnoc prowadzi ku Młynny Rów; wschod prowadzi ku Pola Jęczmienne [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: handel wóz [INSPECTABLE]
- optional_examinable: deski most [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Mostek łączy oba brzegi strugi tak, by wóz nie musiał brnąć przez wodę. W tym miejscu zbiegają się gospodarstwa, handel i ścieżki, więc zawsze ktoś tu stoi choćby na chwilę.
- LOCATION_NAME: Mostek nad Strugą
- INSPECTABLE: deski most, struga nurt, handel wóz
- EXIT_GEOMETRY: polnoc, wschod
- NEIGHBOUR_CONTINUITY: polnoc:Młynny Rów, wschod:Pola Jęczmienne
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Mostek nad Strugą', 'secondary_details': ['deski most', 'struga nurt', 'handel wóz', 'Mostek łączy oba brzegi strugi tak, by wóz nie musiał brnąć przez wodę'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- polnoc: Młynny Rów (wiejski) -> Młynny rów prowadzi wodę do koła i oddaje ją dalej, wzdłuż zabudowań. Woda szumi tu stale, a pył mączny osiada na kamieniu i deskach jak cienka warstwa śniegu.
- wschod: Pola Jęczmienne (wiejski) -> Pola jęczmienne ciągną się szeroko i równo, aż po linię drzew przy drodze. To tutaj widać, czy rok był łaskawy, bo wszystko mierzy się liczbą kłosów i tym, ile zostało po gradzie.

### Variants
#### Variant A
- Trial short: Przejście
- Trial description: Na deski most widać wydeptane i przeorane koleinami; wiatr i spływ rozcinają zbocze. Na skraju drogi leżą połamane gałęzie. Światło jest ostre i nierówne na całej długości zbocza.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.145
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: Przejście
- Trial description: Przy osi przejazdu albo przy zwężeniu handel wóz jest wydeptane i przeorane koleinami, a ruch wozów i stałe przejazdy zmienia krawędź terenu. Na grzbiecie stoi samotny głaz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.089
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Pola Jęczmienne (`90`)
- Area: `Haldun`
- Family: `landscape`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (kłosy zboże vs sierpy widły).

### Existing Facts
- Existing description: Pola jęczmienne ciągną się szeroko i równo, aż po linię drzew przy drodze. To tutaj widać, czy rok był łaskawy, bo wszystko mierzy się liczbą kłosów i tym, ile zostało po gradzie.
- Actual exits: wschod, zachod
- Existing inspectables: kłosy zboże, sierpy widły, wiatr pył

### Proposed Microimage
- anchor_object: kłosy zboże [INSPECTABLE]
- physical_state: rozjechana i pofalowana [HUMAN_REVIEW_REQUIRED]
- precise_position: w lokalnym punkcie przejścia [HUMAN_REVIEW_REQUIRED]
- physical_cause: wilgoć, cień albo praca rolnicza [REGIONAL_PROCESS]
- relation_to_movement: wiąże przejście z lokalnym ruchem [HUMAN_REVIEW_REQUIRED]
- relation_to_visibility: wymaga ręcznej decyzji [HUMAN_REVIEW_REQUIRED]
- relation_to_neighbouring_locations: zachod prowadzi ku Mostek nad Strugą; wschod prowadzi ku Sad Kwaśnych Jabłek [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: sierpy widły [INSPECTABLE]
- optional_examinable: kłosy zboże [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Pola jęczmienne ciągną się szeroko i równo, aż po linię drzew przy drodze. To tutaj widać, czy rok był łaskawy, bo wszystko mierzy się liczbą kłosów i tym, ile zostało po gradzie.
- LOCATION_NAME: Pola Jęczmienne
- INSPECTABLE: kłosy zboże, sierpy widły, wiatr pył
- EXIT_GEOMETRY: wschod, zachod
- NEIGHBOUR_CONTINUITY: zachod:Mostek nad Strugą, wschod:Sad Kwaśnych Jabłek
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Pola Jęczmienne', 'secondary_details': ['kłosy zboże', 'sierpy widły', 'wiatr pył', 'Pola jęczmienne ciągną się szeroko i równo, aż po linię drzew przy drodze'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Mostek nad Strugą (wiejski) -> Mostek łączy oba brzegi strugi tak, by wóz nie musiał brnąć przez wodę. W tym miejscu zbiegają się gospodarstwa, handel i ścieżki, więc zawsze ktoś tu stoi choćby na chwilę.
- wschod: Sad Kwaśnych Jabłek (wiejski) -> Sad jest mały, ale zadbany, a jabłka mają wyraźnie kwaśny smak i twardą skórkę. Drzewa rosną nisko, przez co trzeba schylać się po owoce i uważać na spadające gałęzie.

### Variants
#### Variant A
- Trial short: W lokalnym punkcie przejścia w lokalnym punkcie przejścia
- Trial description: Na kłosy zboże widać rozjechana i pofalowana; wiatr i spływ rozcinają zbocze. Na skraju drogi leżą połamane gałęzie. Światło jest ostre i nierówne na całej długości zbocza.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.152
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W lokalnym punkcie przejścia w lokalnym punkcie przejścia
- Trial description: Przy lokalnym punkcie przejścia sierpy widły jest rozjechana i pofalowana, a wilgoć, cień albo praca rolnicza zmienia krawędź terenu. Na grzbiecie stoi samotny głaz.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: True
- expressed_movement_relation: True
- expressed_neighbour_relation: False
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.186
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=HUMAN_REVIEW_REQUIRED, precise_position=HUMAN_REVIEW_REQUIRED, physical_cause=REGIONAL_PROCESS, relation_to_movement=HUMAN_REVIEW_REQUIRED, relation_to_visibility=HUMAN_REVIEW_REQUIRED, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Kapliczka Żniwiarzy (`93`)
- Area: `Haldun`
- Family: `sacred`
- Review status: `NEEDS_HUMAN_CHOICE`
- Reason: Dwa bezpieczne mikroobrazy; wariant A i B różnią się lokalnym punktem zaczepienia (paciorki ofiary vs droga forteca).

### Existing Facts
- Existing description: Kapliczka stoi przy drodze do fortecy i przypomina, że żniwa też są rodzajem modlitwy. W niszy palą się świece, a wokół leżą drobne ofiary i sznury paciorków.
- Actual exits: poludnie, zachod
- Existing inspectables: swiece wosk, paciorki ofiary, droga forteca

### Proposed Microimage
- anchor_object: paciorki ofiary [INSPECTABLE]
- physical_state: osadzone od dotyku, wosku albo ofiar [INSPECTABLE]
- precise_position: u podstawy kapliczki lub w niszy [LOCATION_DESCRIPTION]
- physical_cause: ruch wozów i stałe przejazdy [EXISTING_WORLD_FACT]
- relation_to_movement: sprawia, że ruch zwalnia przy zatrzymaniu [LOCATION_DESCRIPTION]
- relation_to_visibility: zbiera wzrok na małym punkcie przy drodze [LOCATION_DESCRIPTION]
- relation_to_neighbouring_locations: zachod prowadzi ku Pastwisko Koni; poludnie prowadzi ku Droga ku Fortecy [NEIGHBOUR_CONTINUITY]
- optional_secondary_object: droga forteca [INSPECTABLE]
- optional_examinable: paciorki ofiary [INSPECTABLE]
- physical_relation_count: 9

### Sources
- LOCATION_DESCRIPTION: Kapliczka stoi przy drodze do fortecy i przypomina, że żniwa też są rodzajem modlitwy. W niszy palą się świece, a wokół leżą drobne ofiary i sznury paciorków.
- LOCATION_NAME: Kapliczka Żniwiarzy
- INSPECTABLE: swiece wosk, paciorki ofiary, droga forteca
- EXIT_GEOMETRY: poludnie, zachod
- NEIGHBOUR_CONTINUITY: zachod:Pastwisko Koni, poludnie:Droga ku Fortecy
- REGIONAL_MATERIAL: kamień, drewno
- REGIONAL_PROCESS: rolnictwo
- EXISTING_WORLD_FACT: {'dominant_landmark': 'Kapliczka Żniwiarzy', 'secondary_details': ['swiece wosk', 'paciorki ofiary', 'droga forteca', 'Kapliczka stoi przy drodze do fortecy i przypomina, że żniwa też są rodzajem modlitwy'], 'historical_layer': 'praca pól i studni'}
- HUMAN_REVIEW_REQUIRED: choose between local anchors derived from inspectables and geometry

### Neighbours
- zachod: Pastwisko Koni (wiejski) -> Pastwisko jest szerokie i wietrzne, a konie trzymają się tu bliżej ogrodzeń niż środka pola. Widać po nich, że znały już ciężkie wozy i bardziej niż chleb cenią spokój.
- poludnie: Droga ku Fortecy (wiejski) -> Droga ku Fortecy wychodzi z Haldun i prowadzi dalej do wojskowego pasa na północy. Tu kończy się wiejska codzienność, a zaczyna ruch żołnierzy, zapasów i tych, którzy muszą się tłumaczyć z podróży.

### Variants
#### Variant A
- Trial short: U podstawy kapliczki lub w niszy i cisza
- Trial description: Na kamieniu przy ołtarzu widać starte kolana. Próg jest starty od butów i klękania. Na paciorki ofiary widać osadzone od dotyku, wosku albo ofiar; paciorki ofiary zbiera ślady dłoni przy podstawie. Kamienna ława odcina boczną niszę od nawy.
- expressed_anchor: True
- expressed_state: True
- expressed_position: False
- expressed_cause: False
- expressed_movement_relation: True
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.056
- human_readability_note: czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- Microimage source map: anchor_object=INSPECTABLE, physical_state=INSPECTABLE, precise_position=LOCATION_DESCRIPTION, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=LOCATION_DESCRIPTION, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

#### Variant B
- Trial short: W osi przejazdu albo przy zwężeniu i cisza
- Trial description: Próg jest starty od butów i klękania. Na droga forteca widać wydeptane i przeorane koleinami; droga forteca zbiera ślady dłoni przy podstawie. Dym osiada pod stropem i przy belkach.
- expressed_anchor: True
- expressed_state: True
- expressed_position: True
- expressed_cause: False
- expressed_movement_relation: False
- expressed_neighbour_relation: True
- expressed_examinable: True
- hallucinated_facts: none
- physical_relation_count: 9
- similarity_to_neighbours: 0.174
- human_readability_note: czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- Microimage source map: anchor_object=INSPECTABLE, physical_state=LOCATION_DESCRIPTION, precise_position=EXIT_GEOMETRY, physical_cause=EXISTING_WORLD_FACT, relation_to_movement=EXIT_GEOMETRY, relation_to_visibility=LOCATION_DESCRIPTION, relation_to_neighbouring_locations=NEIGHBOUR_CONTINUITY, optional_secondary_object=INSPECTABLE, optional_examinable=INSPECTABLE, facts_that_must_not_be_added=HUMAN_REVIEW_REQUIRED, expected_player_memory=HUMAN_REVIEW_REQUIRED

### Decision
DECISION: EDIT
REVIEWER_NOTE: Choose the variant that best matches the local microimage and reject any proposal that would require new large objects or unverified history.

## Final Report
- READY_FOR_HUMAN_ACCEPTANCE: 0
- NEEDS_HUMAN_CHOICE: 60
- INSUFFICIENT_WORLD_DATA: 0
- REJECTED_AS_HALLUCINATION: 0
- Average physical_relation_count: 9.00
- Most similar locations:
  - `85` Chata Sołtysa: 0.267
  - `393` Waga Rudy: 0.203
  - `391` Plac Przed Szybem: 0.202
  - `481` Grzęzawisko Cichych Bąbli: 0.199
  - `110` Brama Dungrim: 0.195
  - `480` Powalone Drzewo nad Topielą: 0.177
  - `115` Kuchnia Garnizonowa: 0.176
  - `114` Stajnie Patroli: 0.167
  - `476` Trzcinowy Próg: 0.152
  - `479` Stara Grobla: 0.152
- Most frequently used sources:
  - INSPECTABLE: 415
  - HUMAN_REVIEW_REQUIRED: 341
  - NEIGHBOUR_CONTINUITY: 198
  - LOCATION_DESCRIPTION: 158
  - EXISTING_WORLD_FACT: 98
  - EXIT_GEOMETRY: 90
  - REGIONAL_PROCESS: 19
  - REGIONAL_MATERIAL: 1
- Families requiring manual decision:
  - natural: 10
  - ruin: 10
  - road: 10
  - border: 10
  - vertical: 10
  - landscape: 9
  - sacred: 1
## 10 Best Proposals
- `397` Nisza z Lampami variant B: score 95, similarity 0.046, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `394` Stary Kołowrót variant A: score 95, similarity 0.060, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `136` Pierwszy Kamień Milowy variant B: score 95, similarity 0.074, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `485` Wyspa Torfowa variant A: score 94, similarity 0.010, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `392` Szopa Cechu Górników variant B: score 94, similarity 0.055, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `484` Martwy Las variant A: score 94, similarity 0.071, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `477` Rozlewisko Szarej Wody variant B: score 93, similarity 0.011, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `94` Droga ku Fortecy variant A: score 93, similarity 0.015, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `119` Mur Nad Traktem variant A: score 93, similarity 0.019, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `395` Zjazd do Górnego Chodnika variant B: score 93, similarity 0.021, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
## 10 Weakest Proposals
- `115` Kuchnia Garnizonowa variant B: score 0, similarity 0.061, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `116` Koszary Zachodnie variant A: score 0, similarity 0.082, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `393` Waga Rudy variant B: score 0, similarity 0.097, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `396` Górny Chodnik Północny variant A: score 0, similarity 0.097, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `116` Koszary Zachodnie variant B: score 0, similarity 0.101, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `396` Górny Chodnik Północny variant B: score 0, similarity 0.113, relations 9; czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- `399` Ślepy Przodek variant A: score 0, similarity 0.114, relations 9; czytelny częściowo; warto doprecyzować lokalny punkt zaczepienia
- `391` Plac Przed Szybem variant B: score 0, similarity 0.153, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `115` Kuchnia Garnizonowa variant A: score 0, similarity 0.176, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
- `391` Plac Przed Szybem variant A: score 0, similarity 0.202, relations 9; czytelny, bo trzyma się konkretnego obiektu i fizycznego śladu
## Verification
- pytest: 314 passed in 63.57s
- ruff: All checks passed!
- mypy: Success: no issues found in 201 source files

## Verdict
HUMAN REVIEW READY
