from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from astergard.characters.models import Character, CharacterStats
from astergard.items.models import (
    Item,
    baker_shop_inventory,
    blacksmith_shop_inventory,
    fisher_shop_inventory,
    innkeeper_shop_inventory,
    merchant_shop_inventory,
    vendor_shop_inventory,
)
from astergard.npcs.combat_profiles import combat_style_for_vnum
from astergard.npcs.threat import apply_threat_profile, threat_for_vnum
from astergard.state import NPC_STATE_MACHINE, NPCState, parse_npc_state


@dataclass(slots=True)
class NPC:
    vnum: str
    name: str
    short_desc: str
    long_desc: str
    zone: str
    faction: str
    ai_state: str = "IDLE"
    room_id: int = 0
    character: Character = field(default_factory=lambda: Character("npc"))
    is_merchant: bool = False
    shop_inventory: list[Item] = field(default_factory=list)
    merchant_gold: int = 100
    id: str = field(default_factory=lambda: uuid4().hex)
    dialogue_tree: dict[str, list[str]] = field(default_factory=dict)
    home_room_id: int = 0
    respawn_delay_seconds: int = 300
    threat_tier: str = "standard"
    threat_label: str = "standardowy przeciwnik"
    daily_activity: str = ""
    daily_target_room_id: int | None = None
    daily_phase: str = ""

    def transition_ai_state(self, target: str | NPCState) -> None:
        current = parse_npc_state(self.ai_state)
        next_state = parse_npc_state(target)
        self.ai_state = NPC_STATE_MACHINE.validate(current, next_state).value

    def dialogue(self, topic: str = "default", reputation: int = 0) -> str:
        lines = self.dialogue_tree.get(topic) or self.dialogue_tree.get("default") or ["Milczy."]
        if reputation < 0 and len(lines) > 1:
            return lines[1]
        return lines[0]

    def scene_line(self) -> str:
        if not self.daily_activity:
            return self.short_desc
        activity = self.daily_activity[:1].lower() + self.daily_activity[1:]
        return f"{self.name[:1].upper() + self.name[1:]} {activity}"


class NPCFactory:
    def _finalize(self, npc: NPC) -> NPC:
        profile = threat_for_vnum(npc.vnum)
        npc.threat_tier = profile.tier
        npc.threat_label = profile.label
        npc.respawn_delay_seconds = max(30, int(npc.respawn_delay_seconds * profile.respawn_multiplier))
        apply_threat_profile(npc.character, profile)
        return npc

    def _social_dialogue(
        self,
        default: str,
        praca: str,
        miejsce: str,
        plotki: str,
        **extra: str,
    ) -> dict[str, list[str]]:
        tree = {
            "default": [default],
            "praca": [praca],
            "miejsce": [miejsce],
            "plotki": [plotki],
        }
        for topic, line in extra.items():
            tree[topic] = [line]
        return tree

    def _basic_npc(
        self,
        *,
        vnum: str,
        name: str,
        short_desc: str,
        long_desc: str,
        zone: str,
        faction: str,
        room_id: int,
        ai_state: str = "IDLE",
        stats: CharacterStats | None = None,
        equipment: dict[str, Item | None] | None = None,
        inventory: list[Item] | None = None,
        dialogue_tree: dict[str, list[str]] | None = None,
        is_merchant: bool = False,
        shop_inventory: list[Item] | None = None,
        merchant_gold: int = 100,
    ) -> NPC:
        character = Character(name.capitalize())
        if stats is not None:
            character.stats = stats
        character.inventory.clear()
        if inventory:
            character.inventory.extend(inventory)
        if equipment:
            character.equipment.update(equipment)
        npc = NPC(
            vnum=vnum,
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            zone=zone,
            faction=faction,
            ai_state=ai_state,
            room_id=room_id,
            character=character,
            is_merchant=is_merchant,
            shop_inventory=list(shop_inventory or []),
            merchant_gold=merchant_gold,
            home_room_id=room_id,
        )
        npc.character.combat_style = combat_style_for_vnum(npc.vnum)
        if dialogue_tree is not None:
            npc.dialogue_tree = dialogue_tree
        return self._finalize(npc)

    def create(self, vnum: str, room_id: int) -> NPC:
        if vnum == "astergard_guard":
            return self._basic_npc(
                vnum="astergard_guard",
                name="strażnik",
                short_desc="Strażnik miasta opiera włócznię o ramię.",
                long_desc="Nosi płaszcz w barwach Astergardu i ma twarz człowieka, który widział zbyt wiele spóźnionych kłótni.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                ai_state="GUARD",
                stats=CharacterStats(12, 11, 12, 10, 10, 110),
                equipment={
                    "prawa_reka": Item("włócznia strażnicza", "Prosta włócznia do kontroli ulic i bram.", 2.6, 18, "city_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2, initiative_modifier=0, parry_bonus=0),
                    "lewa_reka": Item("mniejsza tarcza", "Tarcza służbowa z wybitym herbem miasta.", 2.7, 14, "city_guard_shield", "shield", "lewa_reka", protection=1, shield_block=2),
                    "korpus": Item("płaszcz straży", "Wzmacniany płaszcz miejskiej straży.", 4.8, 22, "city_guard_cloak", "armor", "korpus", protection=1),
                },
                dialogue_tree=self._social_dialogue(
                    "Pilnuj drogi i nie zawracaj ludziom głowy.",
                    "Służba jest prosta: patrzeć, słuchać i nie mrugać za często.",
                    "Stoję tam, gdzie mi każą. Zwykle przy bramie albo tam, gdzie ruch jest największy.",
                    "Włóczędzy zdradzają się butami, nie słowami. Na to patrzę najpierw.",
                    brama="Przy bramie najłatwiej o kłopoty, więc patrzymy tu podwójnie uważnie.",
                ),
            )
        if vnum == "innkeeper":
            return self._basic_npc(
                vnum="innkeeper",
                name="karczmarz",
                short_desc="Karczmarz ociera dłonie o fartuch i patrzy na gości bez zaufania.",
                long_desc="Pamięta cudze rachunki lepiej niż cudze twarze, a mimo to rzadko daje się oszukać po raz drugi.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 11, 11, 100),
                is_merchant=True,
                merchant_gold=55,
                shop_inventory=innkeeper_shop_inventory(),
                dialogue_tree=self._social_dialogue(
                    "Siadaj albo idź dalej, ale nie blokuj przejścia.",
                    "Praca przy ladzie nie kończy się nigdy. Kubki same się nie myją.",
                    "Karczma stoi tam, gdzie wszyscy muszą przejść choć raz.",
                    "Plotki przychodzą szybciej niż dostawy. Dwa kufle i już wiem za dużo.",
                    piwo="Piwo jest ciemne, bo ludzie chcą zapomnieć, nie błyszczeć.",
                    gość="Z twarzy widzę, czy ktoś zasługuje na ciepły stół.",
                ),
            )
        if vnum == "podgrodzie_woznica":
            return self._basic_npc(
                vnum="podgrodzie_woznica",
                name="woźnica",
                short_desc="Woźnica stoi przy wozie i sprawdza okucia, jakby od nich zależał porządek świata.",
                long_desc="Zna każdy wybojowy objazd wokół Astergardu i wie, kiedy lepiej czekać na suchą ziemię niż na cud.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 9, 10, 95),
                equipment={
                    "korpus": Item("woźnicki kaftan", "Gruby kaftan odporny na deszcz, kurz i smar od osi.", 2.0, 8, "podgrodzie_driver_coat", "armor", "korpus", protection=1),
                    "prawa_reka": Item("bat woźnicy", "Krótki bat do poganiania koni i porządkowania przestrzeni wokół wozu.", 0.6, 6, "podgrodzie_driver_whip", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
                },
                inventory=[Item("rzemień uprzęży", "Zapasowy rzemień do naprawy uprzęży i plandek.", 0.2, 2, "podgrodzie_driver_strap", item_type="tool")],
            )
        if vnum == "podgrodzie_karczmarz":
            return self._basic_npc(
                vnum="podgrodzie_karczmarz",
                name="karczmarz",
                short_desc="Karczmarz pilnuje lady i nie pozwala, by kufle stały puste zbyt długo.",
                long_desc="Słyszy więcej przy ladzie niż w urzędzie, bo ludzie przy piwie mówią prawdę albo bardzo zbliżoną wersję.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 11, 11, 100),
                equipment={
                    "korpus": Item("karczemny fartuch", "Gruby fartuch z kieszeniami na łyżki, klucze i drobne rachunki.", 1.0, 5, "podgrodzie_inn_apron", "armor", "korpus", protection=1),
                },
                inventory=[Item("księga rachunków", "Zeszyt z zapisami należności, poplamiony tłuszczem i winem.", 0.4, 4, "podgrodzie_inn_ledger", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Siadaj, jedz, pij i nie wchodź za ladę.",
                    "Praca jest przy stole, w kuchni i przy rachunkach. Nigdy nie brakuje roboty.",
                    "Karczma stoi przy drodze, więc obcy trafiają tu sami.",
                    "Plotki znam z pierwszej ręki. Goście mówią więcej niż powinni.",
                    gość="Dach nad głową kosztuje mniej niż kłótnia przy drzwiach.",
                ),
            )
        if vnum == "podgrodzie_karczmarka":
            return self._basic_npc(
                vnum="podgrodzie_karczmarka",
                name="karczmarka",
                short_desc="Karczmarka niesie tacę pewniej niż niejeden strażnik tarczę.",
                long_desc="Wie, kto co zamawia, kto co ukradł i kto próbuje zniknąć przed zapłaceniem. W karczmie to wystarczy za talent i broń.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 10, 11, 95),
                equipment={
                    "korpus": Item("karczemny gorset", "Roboczy gorset z grubej tkaniny, odporny na kuchenny pośpiech.", 0.9, 5, "podgrodzie_inn_garment", "armor", "korpus", protection=1),
                    "prawa_reka": Item("taca z blachy", "Niewielka taca do noszenia kubków i talerzy.", 0.8, 4, "podgrodzie_inn_tray", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=1, parry_bonus=0),
                },
                inventory=[Item("ściereczka kelnerska", "Ściereczka do ścierania stołów i cudzych śladów.", 0.1, 1, "podgrodzie_inn_cloth", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Jeśli masz chwilę, to powiedz ją szybko. Mam gości do obsłużenia.",
                    "Praca? Tace, kufle i sprzątanie cudzych śladów po nocy.",
                    "Karczma stoi przy drodze, więc zawsze ktoś tu trafia.",
                    "Plotki przychodzą z każdym zamówieniem. Ja tylko udaję, że nie słucham.",
                ),
            )
        if vnum == "podgrodzie_piekarz":
            return self._basic_npc(
                vnum="podgrodzie_piekarz",
                name="piekarz",
                short_desc="Piekarz ma dłonie białe od mąki i spojrzenie człowieka, który wstaje przed resztą miasta.",
                long_desc="Dla niego wszystko mierzy się w cieście, cieple pieca i czasie wyrośnięcia. W Podgrodziu to porządek równie ważny jak straż.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 9, 10, 90),
                is_merchant=True,
                merchant_gold=45,
                shop_inventory=baker_shop_inventory(),
                equipment={
                    "korpus": Item("piekarski fartuch", "Szorstki fartuch z mąką w zagięciach.", 0.8, 4, "podgrodzie_baker_apron", "armor", "korpus", protection=1),
                    "prawa_reka": Item("łopata piekarska", "Krótka łopata do wsuwania bochenków do pieca.", 1.4, 7, "podgrodzie_baker_peel", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=2, reach=1, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("kosz bułek", "Kosz jeszcze ciepłych bułek.", 1.2, 6, "podgrodzie_baker_rolls", item_type="food")],
            )
        if vnum == "podgrodzie_handlarz":
            return self._basic_npc(
                vnum="podgrodzie_handlarz",
                name="handlarz",
                short_desc="Handlarz liczy towar szybciej niż ludzi, chyba że jedno i drugie da się sprzedać.",
                long_desc="Zna wartość wozu, worka i plotki. Na targu potrafi wyczuć, czy lepiej mówić o cenie, czy o pogodzie.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 11, 11, 95),
                is_merchant=True,
                merchant_gold=65,
                shop_inventory=merchant_shop_inventory(),
                equipment={
                    "korpus": Item("handlarski płaszcz", "Płaszcz z wieloma kieszeniami, odpowiedni do targowania się i ukrywania monet.", 1.1, 6, "podgrodzie_merchant_cloak", "armor", "korpus", protection=0),
                    "prawa_reka": Item("kijek do ważenia", "Krótki kij i miarka, które pomagają pilnować uczciwej wagi.", 0.5, 4, "podgrodzie_merchant_staff", "tool", "prawa_reka"),
                },
                inventory=[Item("tabliczka cen", "Tabliczka z kilkoma wyświechtanymi cenami.", 0.2, 2, "podgrodzie_merchant_priceboard", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Handluję, liczę i nie daję się oszukać dwa razy tego samego dnia.",
                    "Praca handlarza to waga, ceny i dobry wzrok.",
                    "Stoję tam, gdzie targ ma najgłośniejszy róg.",
                    "Plotki krążą po stoiskach szybciej niż monety.",
                ),
            )
        if vnum == "podgrodzie_przekupka":
            return self._basic_npc(
                vnum="podgrodzie_przekupka",
                name="przekupka",
                short_desc="Przekupka rozkłada towar tak, żeby każdy myślał, że właśnie znalazł okazję.",
                long_desc="Umie sprzedać jajka, cebulę i zdrowy rozsądek. W Podgrodziu takie umiejętności są równie cenne jak uczciwość rzadkiego dnia targowego.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 8, 11, 10, 85),
                is_merchant=True,
                merchant_gold=42,
                shop_inventory=vendor_shop_inventory(),
                equipment={
                    "korpus": Item("targowy kaftan", "Kaftan wzmocniony łatami i kieszeniami na monety.", 0.9, 4, "podgrodzie_vendor_apron", "armor", "korpus", protection=0),
                },
                inventory=[Item("kosz z towarem", "Kosz z drobnym handlem, gotowy do ustawienia na straganie.", 2.0, 8, "podgrodzie_vendor_basket", is_container=True, capacity=18)],
                dialogue_tree=self._social_dialogue(
                    "Nie gap się, tylko wybieraj. Towar sam się nie sprzeda.",
                    "Praca przy kramie to ciężkie ręce i szybki język.",
                    "Na targu stoję tam, gdzie najlepiej widać klientów i straż.",
                    "Plotki? Jeśli wiem, kto z kim się pokłócił, to znam też cenę cebuli.",
                ),
            )
        if vnum == "blacksmith":
            return self._basic_npc(
                vnum="blacksmith",
                name="kowal",
                short_desc="Kowal ma dłonie zgrubiałe od ognia i młota.",
                long_desc="Jego twarz nosi ślad wiecznego żaru, a ubranie pachnie węglem, olejem i rozgrzanym żelazem.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(13, 9, 12, 10, 10, 110),
                inventory=[Item("młot kowalski", "Praktyczny młot do codziennej pracy.", 2.0, 10, "npc_blacksmith_hammer", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Jak chcesz gadać, to krótko. Mam ogień do pilnowania.",
                    "Praca? Młot, żar i stal. Nic więcej nie trzeba.",
                    "Kuźnia stoi przy murze, bo tam nikt nie marudzi na hałas.",
                    "Plotki? Słyszę je od pomocników, zanim jeszcze ostygnie żelazo.",
                ),
            )
        if vnum == "podgrodzie_kowal":
            return self._basic_npc(
                vnum="podgrodzie_kowal",
                name="kowal",
                short_desc="Kowal z Podgrodzia stoi przy przenośnym palenisku i sprawdza rozgrzane żelazo.",
                long_desc="Nie ma kuźni jak w mieście, ale ma młot, palenisko i klientów, którzy wolą naprawić narzędzie niż kupować nowe.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(13, 9, 12, 10, 10, 110),
                is_merchant=True,
                merchant_gold=75,
                shop_inventory=blacksmith_shop_inventory(),
                equipment={
                    "korpus": Item("okopcony fartuch", "Skórzany fartuch chroniący przed iskrą i żarem.", 2.4, 12, "podgrodzie_smith_apron", "armor", "korpus", protection=1),
                    "prawa_reka": Item("młot kowalski", "Ciężki młot, którym da się zarówno kuć, jak i odstraszyć natrętów.", 2.2, 11, "podgrodzie_smith_hammer", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=4, reach=1, initiative_modifier=0, parry_bonus=1),
                },
                inventory=[Item("szczypce kowalskie", "Długie szczypce do rozgrzanych prętów i podków.", 1.0, 5, "podgrodzie_smith_tongs", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Młot nie robi się lżejszy od gadania, ale mam chwilę.",
                    "Praca kowala zaczyna się od ognia, a kończy na odciskach.",
                    "Stoję tu, gdzie muszę, żeby iskry nie poszły na cudze dachy.",
                    "Plotki przychodzą od pomocnika szybciej niż nowe podkowy.",
                ),
            )
        if vnum == "podgrodzie_pomocnik_kowala":
            return self._basic_npc(
                vnum="podgrodzie_pomocnik_kowala",
                name="pomocnik kowala",
                short_desc="Pomocnik kowala nosi węgiel, czyści żużel i uczy się nie stać za blisko ognia.",
                long_desc="Jeszcze nie bije samodzielnie żelaza, ale zna rytm pracy i wie, kiedy podać narzędzie bez pytania.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 9, 10, 95),
                equipment={
                    "korpus": Item("robocza kamizela", "Ciężka kamizela z łatami i sadzą na ramionach.", 1.4, 6, "podgrodzie_smith_helper_vest", "armor", "korpus", protection=0),
                    "prawa_reka": Item("szczypce pomocnika", "Lżejsze szczypce do trzymania rozgrzanych elementów.", 0.8, 3, "podgrodzie_smith_helper_tongs", "tool", "prawa_reka"),
                },
                inventory=[Item("pudełko gwoździ", "Pudełko z posortowanymi gwoździami i nitami.", 0.9, 4, "podgrodzie_smith_nails", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Jeszcze uczę się, ale i tak wszystko muszę podać zanim mistrz mruknie.",
                    "Praca pomocnika to węgiel, szczypce i pilnowanie żaru.",
                    "Najczęściej jestem przy palenisku albo po drewno biegnę.",
                    "Plotki? W kuźni szybciej lecą iskry niż słowa, ale i tak coś się usłyszy.",
                ),
            )
        if vnum == "podgrodzie_straznik_miejski":
            return self._basic_npc(
                vnum="podgrodzie_straznik_miejski",
                name="strażnik miejski",
                short_desc="Strażnik miejski zna wszystkich, którzy próbują wjechać do Podgrodzia bez pytania o zgodę.",
                long_desc="Patroluje bramę i skrzyżowania z praktycznym spokojem człowieka, który woli zapisać nazwisko niż gonić po błocie.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                ai_state="GUARD",
                stats=CharacterStats(12, 11, 12, 11, 11, 115),
                equipment={
                    "prawa_reka": Item("włócznia miejska", "Prosta włócznia do kontroli ruchu i powstrzymywania awantur.", 2.7, 18, "podgrodzie_guard_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2),
                    "lewa_reka": Item("okrągła tarcza", "Tarcza z miejskim znakiem, solidna i już dobrze przeżyta.", 3.0, 16, "podgrodzie_guard_shield", "shield", "lewa_reka", protection=1, shield_block=2),
                    "korpus": Item("płaszcz straży", "Gruby płaszcz na służbę w deszczu i błocie.", 4.5, 20, "podgrodzie_guard_cloak", "armor", "korpus", protection=1),
                },
                dialogue_tree=self._social_dialogue(
                    "Stój spokojnie i nie utrudniaj służby.",
                    "Patrol, wpisy i wypatrywanie błędu. To moja robota.",
                    "Na bramie widzę większość ludzi, którzy wchodzą do Podgrodzia.",
                    "Plotki? Najgorsze są te, które zaczynają się od 'na chwilę tylko'.",
                    brama="Brama to nie targ. Tu się wjeżdża, a nie błądzi.",
                ),
            )
        if vnum == "farmer":
            return self._basic_npc(
                vnum="farmer",
                name="rolnik",
                short_desc="Rolnik ma buty ubłocone od pól i twarz zmęczoną przed świtem.",
                long_desc="Żyje rytmem ziemi, a nie miasta. W jego sakwie prawie zawsze coś szeleści: ziarno, sznurek albo rachunek do spłacenia.",
                zone="Haldun",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 8, 9, 90),
                inventory=[Item("wiązka zboża", "Mały snopek świeżo zebranej słomy.", 0.9, 2, "npc_grain_bundle", item_type="food")],
            )
        if vnum == "podgrodzie_chlop":
            return self._basic_npc(
                vnum="podgrodzie_chlop",
                name="chłop",
                short_desc="Chłop przywiózł z pola brud, słomę i kilka worków, których nie wolno było zgubić po drodze.",
                long_desc="Pracuje jak ziemia każe, a nie jak miasto chce. Na twarzy ma pogodę, na rękach odciski, a przy pasie narzędzie, które zawsze da się użyć do pracy.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 9, 10, 8, 9, 95),
                equipment={
                    "korpus": Item("płócienna koszula", "Płócienna koszula przydatna do ciężkiej roboty w polu.", 1.0, 4, "podgrodzie_farmer_shirt", "armor", "korpus", protection=0),
                    "prawa_reka": Item("widły polne", "Proste widły do siana i obrony przed psami.", 2.2, 8, "podgrodzie_farmer_fork", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=3, reach=2, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("mała motyka", "Narzędzie do ziemi, chwastów i wyciągania się z kłopotów.", 1.0, 3, "podgrodzie_farmer_hoe", item_type="tool")],
            )
        if vnum == "podgrodzie_chlopka":
            return self._basic_npc(
                vnum="podgrodzie_chlopka",
                name="chłopka",
                short_desc="Chłopka niesie kosz, jakby ważył mniej niż jej obowiązki.",
                long_desc="Zna porę karmienia, czas pieczenia i liczenie jaj bez pomyłki. W Podgrodziu to praktyczny rodzaj mądrości.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 9, 9, 10, 90),
                equipment={
                    "korpus": Item("robocza chusta", "Chusta i fartuch chroniące przed kurzem, błotem i mąką.", 0.8, 4, "podgrodzie_farmer_apron", "armor", "korpus", protection=0),
                    "prawa_reka": Item("sierp gospodarski", "Krótki sierp, przydatny do żniw i obrony przed zbyt ciekawą gęsią.", 0.9, 7, "podgrodzie_farmer_sickle", "weapon", "prawa_reka", damage_type="cieta", base_damage=2, reach=1, initiative_modifier=1, parry_bonus=0),
                },
                inventory=[Item("kosz jaj", "Kosz z jajami, owiniętymi w słomę.", 1.4, 6, "podgrodzie_farmer_egg_basket", is_container=True, capacity=10)],
            )
        if vnum == "fisherman":
            return self._basic_npc(
                vnum="fisherman",
                name="rybak",
                short_desc="Rybak pachnie rzeką, smołą i mokrą liną.",
                long_desc="Przez większość dnia stoi przy nabrzeżu, licząc sieci, a nie słowa. Zna nurt rzeki lepiej niż bruk miasta.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 10, 11, 9, 92),
                inventory=[Item("hak do sieci", "Mały hak do naprawy sieci i lin.", 0.3, 2, "npc_fishhook", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Mam ręce zajęte rybami i liną, ale mogę chwilę pogadać.",
                    "Praca rybaka zaczyna się przed świtem i kończy, gdy zniknie ostatnia łódź.",
                    "Jestem tam, gdzie nurt jest spokojny i sieci nie plączą się o deski.",
                    "Plotki? Na nabrzeżu wszystko niesie woda: i wieści, i kłamstwa.",
                ),
            )
        if vnum == "podgrodzie_rybak":
            return self._basic_npc(
                vnum="podgrodzie_rybak",
                name="rybak",
                short_desc="Rybak z Podgrodzia ma sieć przerzuconą przez ramię i ręce zniszczone od soli.",
                long_desc="Nad rzeką zarabia na życie, a w Podgrodziu sprzedaje to, czego nie zdążył oddać do miasta przed południem.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 10, 11, 9, 92),
                is_merchant=True,
                merchant_gold=60,
                shop_inventory=fisher_shop_inventory(),
                equipment={
                    "korpus": Item("mokry kaftan", "Kaftan impregnowany smołą i rybim tłuszczem.", 1.2, 5, "podgrodzie_fisher_coat", "armor", "korpus", protection=0),
                    "prawa_reka": Item("hak rybacki", "Krótki hak do sieci, lin i nieproszonych palców.", 0.3, 3, "podgrodzie_fisher_hook", "tool", "prawa_reka"),
                },
                inventory=[Item("zwinięta sieć", "Sieć gotowa do rzutu albo naprawy.", 2.0, 10, "podgrodzie_fisher_net", item_type="tool")],
                dialogue_tree=self._social_dialogue(
                    "Sieć sama się nie naprawi, ale mogę odpowiedzieć na jedno pytanie.",
                    "Praca rybaka to mokre buty, zimne dłonie i cierpliwość.",
                    "Stoję przy rzece albo na pomoście, zależnie od pogody.",
                    "Plotki płyną szybciej niż łódź, jeśli ktoś je dobrze rozdmucha.",
                ),
            )
        if vnum == "traveler":
            return self._basic_npc(
                vnum="traveler",
                name="podróżny",
                short_desc="Podróżny stoi z sakwą przy nodze i ogląda miasto tak, jakby wciąż szukał wyjścia.",
                long_desc="Na płaszczu ma pył z kilku dróg, a na twarzy ostrożność ludzi, którzy widzieli już zbyt wiele granic.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 10, 10, 100),
                inventory=[Item("podróżna sakwa", "Niewielka sakwa z najpotrzebniejszymi rzeczami.", 1.0, 5, "npc_travel_sack", is_container=True, capacity=10)],
                dialogue_tree=self._social_dialogue(
                    "Mam tylko drogę i kilka historii, ale to wystarczy na rozmowę.",
                    "Praca podróżnego to iść, obserwować i nie ufać pierwszej gospodzie.",
                    "Stoję tam, gdzie droga przecina miasto albo gdzie mogę je opuścić.",
                    "Plotki? Na trakcie każdy niesie cudzą opowieść w sakwie.",
                ),
            )
        if vnum == "podgrodzie_pielgrzym":
            return self._basic_npc(
                vnum="podgrodzie_pielgrzym",
                name="pielgrzym",
                short_desc="Pielgrzym idzie bez pośpiechu, ale z uporem ludzi, których prowadzi nie droga, lecz cel.",
                long_desc="Niesie prosty kij, woreczek z drobnymi ofiarami i cierpliwość, którą zwykle mają tylko ludzie przyzwyczajeni do długich dróg.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 9, 11, 12, 85),
                equipment={
                    "korpus": Item("pielgrzymi płaszcz", "Płaszcz odporny na deszcz i pył z traktu.", 1.5, 6, "podgrodzie_pilgrim_cloak", "armor", "korpus", protection=0),
                    "prawa_reka": Item("kij pielgrzyma", "Prosty kij do marszu i podpierania się na długiej drodze.", 1.2, 4, "podgrodzie_pilgrim_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=2, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("woreczek ofiarny", "Woreczek z monetami i pamiątkami z modlitw.", 0.2, 2, "podgrodzie_pilgrim_pouch", is_container=True, capacity=6)],
                dialogue_tree=self._social_dialogue(
                    "Idę do świętego miejsca, ale mogę zamienić parę słów.",
                    "Praca pielgrzyma to droga, modlitwa i twarde stopy.",
                    "Stoję tam, gdzie trzeba odpocząć przed kolejnym odcinkiem szlaku.",
                    "Plotki mijają mnie codziennie, ale nie wszystkie warto nosić dalej.",
                ),
            )
        if vnum == "beggar":
            return self._basic_npc(
                vnum="beggar",
                name="żebrak",
                short_desc="Żebrak siedzi przy ścianie i wyciąga dłoń szybciej, niż unosi wzrok.",
                long_desc="Ma płaszcz łatany tak wiele razy, że bardziej przypomina mapę biedy niż ubranie. Nie wygląda groźnie, ale zna ulice lepiej niż niejeden strażnik.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(7, 8, 8, 10, 8, 75),
                inventory=[Item("miska na jałmużnę", "Mała miska na monety i okruchy.", 0.4, 1, "beggar_bowl", item_type="misc")],
                dialogue_tree=self._social_dialogue(
                    "Masz chwilę? To już dużo.",
                    "Praca? Tu się prosi, pamięta twarze i szuka cienia.",
                    "Stoję tam, gdzie nikt nie kopie zbyt mocno.",
                    "Plotki krążą po ulicach szybciej niż ja.",
                ),
            )
        if vnum == "podgrodzie_zebrak":
            return self._basic_npc(
                vnum="podgrodzie_zebrak",
                name="żebrak",
                short_desc="Żebrak przesiaduje tam, gdzie błoto jest najgłębsze i gdzie obcy najchętniej udają, że nie widzą.",
                long_desc="Nie ma nic poza miską, kijem i pamięcią do twarzy ludzi, którzy kiedyś dali mu jałmużnę. Podgrodzie nauczyło go też, gdzie stanąć, by nie przegoniła go pierwsza fala wozów.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(7, 8, 8, 10, 8, 75),
                equipment={
                    "korpus": Item("łachman i koc", "Nędzny koc i łachman chronią przed zimnem bardziej niż przed spojrzeniem.", 0.8, 1, "podgrodzie_beggar_rag", "armor", "korpus", protection=0),
                    "prawa_reka": Item("kij żebraka", "Krótki kij do podpierania się i odganiania psów.", 0.7, 1, "podgrodzie_beggar_staff", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=0, parry_bonus=0),
                },
                inventory=[Item("miska na jałmużnę", "Miska na drobne monety i czasem okruch chleba.", 0.4, 1, "podgrodzie_beggar_bowl", item_type="misc")],
                dialogue_tree=self._social_dialogue(
                    "Nie mam wiele, ale mam czas na słowo.",
                    "Praca? Pilnuję kąta, żeby ktoś nie zajął go przede mną.",
                    "Stoję tu, gdzie błoto jest najgłębsze, a wiatr najmniej wredny.",
                    "Plotki w Podgrodziu są jak błoto: przyczepiają się do butów.",
                ),
            )
        if vnum == "child":
            return self._basic_npc(
                vnum="child",
                name="dziecko",
                short_desc="Dziecko patrzy z ciekawością, której dorośli szybko by się oduczyli.",
                long_desc="Ma startą od zabawy kurtkę i spojrzenie, które widzi więcej, niż powinno w tym wieku.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 10, 7, 10, 8, 70),
            )
        if vnum == "podgrodzie_dziecko":
            return self._basic_npc(
                vnum="podgrodzie_dziecko",
                name="dziecko",
                short_desc="Dziecko biega między zagrodami i co chwilę przystaje, by obejrzeć coś nowego.",
                long_desc="Ma odrapane kolana, błoto na butach i ten rodzaj odwagi, który znika dopiero wraz z pierwszymi obowiązkami.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 10, 7, 10, 8, 70),
                equipment={
                    "prawa_reka": Item("drewniana proca", "Dziecięca proca z kawałka gałęzi i skrawka skóry.", 0.2, 1, "podgrodzie_child_sling", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=1, reach=1, initiative_modifier=2, parry_bonus=0),
                },
                inventory=[Item("gładki kamyk", "Mały kamień zebrany z ziemi dla zabawy albo do procy.", 0.02, 0, "podgrodzie_child_stone", item_type="misc")],
            )
        if vnum == "blacksmith":
            return self._basic_npc(
                vnum="blacksmith",
                name="kowal",
                short_desc="Kowal ma dłonie zgrubiałe od ognia i młota.",
                long_desc="Jego twarz nosi ślad wiecznego żaru, a ubranie pachnie węglem, olejem i rozgrzanym żelazem.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(13, 9, 12, 10, 10, 110),
                inventory=[Item("młot kowalski", "Praktyczny młot do codziennej pracy.", 2.0, 10, "npc_blacksmith_hammer", item_type="tool")],
            )
        if vnum == "farmer":
            return self._basic_npc(
                vnum="farmer",
                name="rolnik",
                short_desc="Rolnik ma buty ubłocone od pól i twarz zmęczoną przed świtem.",
                long_desc="Żyje rytmem ziemi, a nie miasta. W jego sakwie prawie zawsze coś szeleści: ziarno, sznurek albo rachunek do spłacenia.",
                zone="Haldun",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 8, 9, 90),
                inventory=[Item("wiązka zboża", "Mały snopek świeżo zebranej słomy.", 0.9, 2, "npc_grain_bundle", item_type="food")],
            )
        if vnum == "fisherman":
            return self._basic_npc(
                vnum="fisherman",
                name="rybak",
                short_desc="Rybak pachnie rzeką, smołą i mokrą liną.",
                long_desc="Przez większość dnia stoi przy nabrzeżu, licząc sieci, a nie słowa. Zna nurt rzeki lepiej niż bruk miasta.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 10, 10, 11, 9, 92),
                inventory=[Item("hak do sieci", "Mały hak do naprawy sieci i lin.", 0.3, 2, "npc_fishhook", item_type="tool")],
            )
        if vnum == "traveler":
            return self._basic_npc(
                vnum="traveler",
                name="podróżny",
                short_desc="Podróżny stoi z sakwą przy nodze i ogląda miasto tak, jakby wciąż szukał wyjścia.",
                long_desc="Na płaszczu ma pył z kilku dróg, a na twarzy ostrożność ludzi, którzy widzieli już zbyt wiele granic.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 10, 10, 100),
                inventory=[Item("podróżna sakwa", "Niewielka sakwa z najpotrzebniejszymi rzeczami.", 1.0, 5, "npc_travel_sack", is_container=True, capacity=10)],
            )
        if vnum == "child":
            return self._basic_npc(
                vnum="child",
                name="dziecko",
                short_desc="Dziecko patrzy z ciekawością, której dorośli szybko by się oduczyli.",
                long_desc="Ma startą od zabawy kurtkę i spojrzenie, które widzi więcej, niż powinno w tym wieku.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 10, 7, 10, 8, 70),
            )
        if vnum == "beggar":
            return self._basic_npc(
                vnum="beggar",
                name="żebrak",
                short_desc="Żebrak siedzi przy ścianie i wyciąga dłoń szybciej, niż unosi wzrok.",
                long_desc="Ma płaszcz łatany tak wiele razy, że bardziej przypomina mapę biedy niż ubranie. Nie wygląda groźnie, ale zna ulice lepiej niż niejeden strażnik.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(7, 8, 8, 10, 8, 75),
                inventory=[Item("miska na jałmużnę", "Mała miska na monety i okruchy.", 0.4, 1, "beggar_bowl", item_type="misc")],
            )
        if vnum == "carpenter":
            return self._basic_npc(
                vnum="carpenter",
                name="cieśla",
                short_desc="Cieśla ma dłonie pełne drzazg i pyłu.",
                long_desc="Mierzy belki okiem szybciej niż inni liczą pieniądze, a przy tym zawsze myśli o tym, co da się jeszcze uratować z drewna.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(10, 10, 10, 10, 10, 100),
                inventory=[Item("dłuto", "Robocze dłuto do drewna.", 0.4, 4, "carpenter_chisel_npc", item_type="tool")],
            )
        if vnum == "tanner":
            return self._basic_npc(
                vnum="tanner",
                name="garbarz",
                short_desc="Garbarz pachnie skórą, popiołem i gorzkim płynem z kadzi.",
                long_desc="Pracuje przy skórach bez pośpiechu, bo wie, że twarda robota i tak zrobi z niego człowieka milczącego.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 9, 10, 95),
                inventory=[Item("garbarski skrobak", "Płaski skrobak do skóry.", 0.5, 3, "tanner_scraper_npc", item_type="tool")],
            )
        if vnum == "bowyer":
            return self._basic_npc(
                vnum="bowyer",
                name="łuczarz",
                short_desc="Łuczarz niesie pod pachą giętkie drewno i klej do łuków.",
                long_desc="Nie ufa szybkim rozwiązaniom. Łuk, jak powtarza, musi pamiętać rękę, która go zrobiła.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 11, 9, 11, 10, 95),
                inventory=[Item("półfabrykat łuku", "Niedokończony łuk z giętkiego drewna.", 0.7, 6, "bowyer_blank_npc", item_type="weapon", slot="prawa_reka", damage_type="pociskowa", base_damage=2, reach=2)],
            )
        if vnum == "armorer":
            return self._basic_npc(
                vnum="armorer",
                name="płatnerz",
                short_desc="Płatnerz ma fartuch okopcony od kuźni i cierpliwość dla krzywych nitów.",
                long_desc="Naprawia pęknięcia, które inni już by wyrzucili. Tego typu ludzie trzymają miasta razem lepiej niż urzędy.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(12, 9, 12, 10, 10, 110),
                inventory=[Item("nitownica", "Ciężkie narzędzie do nitowania zbroi.", 1.0, 5, "armorer_riveter_npc", item_type="tool")],
            )
        if vnum == "dockhand":
            return self._basic_npc(
                vnum="dockhand",
                name="tragarz nabrzeża",
                short_desc="Tragarz nabrzeża ma mokre buty i plecy od worków.",
                long_desc="Przenosi beczki, skrzynie i cudze zyski. Jeśli ma humor, to zwykle dlatego, że dziś jeszcze nic na niego nie spadło.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(11, 10, 11, 9, 9, 100),
                inventory=[Item("hak ładunkowy", "Żelazny hak do przenoszenia ciężkich pakunków.", 0.8, 4, "dockhook_npc", item_type="tool")],
            )
        if vnum == "miller":
            return self._basic_npc(
                vnum="miller",
                name="młynarz",
                short_desc="Młynarz ma twarz białą od pyłu i ręce od worków z ziarnem.",
                long_desc="Wie, ile wart jest zbożowy worek i jak łatwo ludzie kłócą się o mąkę. Jego dzień zaczyna się wcześniej niż dzień miasta.",
                zone="Haldun",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 9, 10, 10, 10, 95),
                inventory=[Item("miernik ziarna", "Mały drewniany miernik do zboża.", 0.5, 3, "miller_measure_npc", item_type="tool")],
            )
        if vnum == "priest_aide":
            return self._basic_npc(
                vnum="priest_aide",
                name="pomocnik kapłana",
                short_desc="Pomocnik kapłana niesie wiadro wody i zwitek płótna.",
                long_desc="Nie ma w nim wielkiej powagi, ale zna porządek świątyni i wie, kiedy lepiej mówić mniej niż trzeba.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 9, 11, 12, 90),
                inventory=[Item("zwitek płótna", "Szorstkie płótno do świątynnych porządków.", 0.3, 2, "priest_aide_linen_npc")],
            )
        if vnum == "watch_sergeant":
            return self._basic_npc(
                vnum="watch_sergeant",
                name="sierżant warty",
                short_desc="Sierżant warty wygląda na człowieka, który nie lubi pytań po zmroku.",
                long_desc="Pilnuje bram i dziedzińców z twarzą kogoś, kto już widział za dużo cudzych wymówek. Inni strażnicy słuchają go szybciej niż radzą się sumienia.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                ai_state="GUARD",
                stats=CharacterStats(13, 11, 13, 11, 11, 125),
                equipment={
                    "prawa_reka": Item("sierżancka włócznia", "Włócznia oznaczona żelaznym pierścieniem.", 2.8, 24, "watch_sergeant_spear", "weapon", "prawa_reka", damage_type="kluta", base_damage=5, reach=2),
                    "lewa_reka": Item("sierżancka tarcza", "Cięższa tarcza dla starszego straży.", 3.1, 18, "watch_sergeant_shield", "shield", "lewa_reka", protection=1, shield_block=3),
                },
                dialogue_tree={
                    "default": [
                        "Ruch szybko. Zatrzymasz się, jeśli ja powiem.",
                        "Ruch szybko. Z taką reputacją nie będę udawał gościnności.",
                    ],
                    "brama": [
                        "Bramy pilnuje się przed świtem i po zmroku. W środku dnia też, jeśli trzeba.",
                        "Bramy pilnuje się też przed tobą, bo z taką reputacją nie ma dyskusji.",
                    ],
                },
            )
        if vnum == "customs_clerk":
            return self._basic_npc(
                vnum="customs_clerk",
                name="celnik",
                short_desc="Celnik ma kałamarz przy pasie i twarz człowieka, który liczy wszystko.",
                long_desc="Nie nosi broni ostentacyjnie, ale za to pamięta każdą pieczęć i każdy fałszywy pakunek. To wystarcza, by był niebezpieczny w zupełnie innym sensie.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 9, 11, 12, 90),
                inventory=[Item("księga ceł", "Ciężka księga zapisów celnych.", 1.3, 6, "customs_book_npc", item_type="tool")],
            )
        if vnum == "fishmonger":
            return self._basic_npc(
                vnum="fishmonger",
                name="rybaczka",
                short_desc="Rybaczka sprzedaje ryby szybko, zanim zdążą stracić sens i zapach.",
                long_desc="Ma twardy głos i ręce od soli. W porcie nikt nie pyta, skąd ma najlepszy towar, bo wszyscy to widzą.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(9, 11, 9, 10, 10, 95),
                inventory=[Item("hak do ryb", "Krótki hak do rozcinania i czyszczenia ryb.", 0.2, 2, "fishmonger_hook_npc", item_type="tool")],
            )
        if vnum == "woodcutter":
            return self._basic_npc(
                vnum="woodcutter",
                name="drwal",
                short_desc="Drwal ma topór cięższy niż jego uśmiech.",
                long_desc="Przychodzi z lasu z żywicą na rękawach i nie zadaje pytań, jeśli ktoś nie zadaje ich jego robocie.",
                zone="Podgrodzie",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(12, 10, 12, 9, 9, 110),
                inventory=[Item("topór drwala", "Użytkowy topór do ścinania drzew.", 2.9, 8, "woodcutter_axe_npc", item_type="weapon", slot="prawa_reka", damage_type="obuchowa", base_damage=4, reach=1)],
            )
        if vnum == "urchin":
            return self._basic_npc(
                vnum="urchin",
                name="dzieciak uliczny",
                short_desc="Dzieciak uliczny ogląda wszystko z ostrożnością i gotowością do biegu.",
                long_desc="Ma za duże oczy jak na swój wiek i wie dokładnie, które kieszenie są lekkie. Na ulicy to cenniejsza wiedza niż alfabet.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(6, 12, 7, 11, 8, 65),
            )
        if vnum == "vagrant":
            return self._basic_npc(
                vnum="vagrant",
                name="włóczęga",
                short_desc="Włóczęga stoi z sakwą przy nodze i wygląda, jakby znał za dużo skrótów.",
                long_desc="Nie trzyma się jednego miejsca dłużej niż trzeba. Tacy ludzie są kłopotem albo świadkami, zależnie od tego, kto pyta.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                room_id=room_id,
                stats=CharacterStats(8, 10, 8, 10, 9, 85),
                inventory=[Item("wytarta sakwa", "Stara sakwa z jednym paskiem za mało.", 0.8, 2, "vagrant_sack_npc", is_container=True, capacity=8)],
            )
        if vnum == "meekhan_soldier":
            c = Character("Żołnierz")
            c.stats = CharacterStats(12, 10, 12, 10, 10, 120)
            npc = NPC(
                vnum="meekhan_soldier",
                name="żołnierz",
                short_desc="Żołnierz Szóstej Kompanii stoi tutaj.",
                long_desc="Ma kolczugę, zmęczone oczy i rękę blisko miecza.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                ai_state="GUARD",
                room_id=room_id,
                character=c,
                home_room_id=room_id,
            )
            npc.character.combat_style = combat_style_for_vnum(npc.vnum)
            npc.character.equipment["prawa_reka"] = Item("żołnierski miecz", "Miecz piechoty Szóstej Kompanii.", 1.9, 35, "soldier_sword", "weapon", "prawa_reka", damage_type="cieta", base_damage=4, reach=1, initiative_modifier=1, parry_bonus=1)
            npc.character.equipment["lewa_reka"] = Item("okrągła tarcza", "Tarcza służbowa z obtłuczonym rantem.", 2.8, 25, "soldier_shield", "shield", "lewa_reka", protection=1, shield_block=2)
            npc.character.equipment["korpus"] = Item("kolczuga", "Krótka kolczuga patrolowa.", 8.0, 80, "mail_armor", "armor", "korpus", protection=2)
            npc.dialogue_tree = {
                "default": ["Pilnuj traktu, cywilu."],
                "wojna": ["Wojna nigdy nie kończy się tam, gdzie kończy się mapa."],
            }
            return self._finalize(npc)
        if vnum == "merchant":
            c = Character("Kupiec")
            npc = NPC(
                vnum="merchant",
                name="kupiec",
                short_desc="Kupiec sprawdza sakwy przy pasie.",
                long_desc="Płaszcz ma dobry, ale oczy niespokojne.",
                zone="Centrum_Twierdza",
                faction="MEEKHAN",
                ai_state="IDLE",
                room_id=room_id,
                character=c,
                is_merchant=True,
                home_room_id=room_id,
            )
            npc.character.combat_style = combat_style_for_vnum(npc.vnum)
            npc.character.equipment["prawa_reka"] = Item("nóż kupiecki", "Krótki nóż do cięcia sznurów i odstraszania desperatów.", 0.4, 8, "merchant_knife", "weapon", "prawa_reka", damage_type="kluta", base_damage=2, reach=1, initiative_modifier=2, parry_bonus=0)
            npc.shop_inventory = [
                Item(
                    "krzesiwo",
                    "Krzesiwo i krzemień w skórzanym woreczku.",
                    0.2,
                    2,
                    "merchant_flint",
                    "tool",
                ),
                Item("bukłak", "Mały bukłak na wodę.", 0.6, 3, "merchant_waterskin", "tool"),
                Item("latarnia podróżna", "Prosta latarnia z grubym szkłem.", 1.4, 6, "merchant_lantern", "tool"),
                Item("sakwa podróżna", "Sakwa z jedną dużą przegródką i mocnym paskiem.", 1.0, 5, "merchant_travel_sack", is_container=True, capacity=12),
                Item("zwój liny", "Zwój grubej liny, przydatny przy drodze.", 2.8, 4, "merchant_rope", "tool"),
            ]
            npc.merchant_gold = 65
            npc.dialogue_tree = self._social_dialogue(
                "Kupuj szybko albo odejdź od lady.",
                "Praca kupca to ważenie, liczenie i pilnowanie, by nikt nie skrócił mnie o grosz.",
                "Stoję tam, gdzie droga z miasta krzyżuje się z ludzką chciwością.",
                "Plotki? Jeśli są warte grosza, to już są towarem.",
                wilki="Wilki schodzą blisko traktu. Przynieś mi jedną skórę, a zapłacę.",
            )
            return self._finalize(npc)
        if vnum == "mountain_troll":
            c = Character("Troll")
            c.stats = CharacterStats(17, 9, 16, 8, 8, 160)
            c.inventory.append(Item("twarda skóra trolla", "Gruba i ciężka skóra.", 3.0, 25, "troll_hide"))
            npc = NPC(
                vnum="mountain_troll",
                name="troll",
                short_desc="Troll górski ciężko oddycha w cieniu skał.",
                long_desc="Wysoki, zgarbiony stwór o łapach jak kamienne młoty.",
                zone="Polnoc_Gory",
                faction="REBELS",
                ai_state="AGGRESSIVE",
                room_id=room_id,
                character=c,
                home_room_id=room_id,
            )
            npc.character.combat_style = combat_style_for_vnum(npc.vnum)
            npc.character.equipment["prawa_reka"] = Item("kamienna maczuga", "Ciężki głaz osadzony na pękniętym trzonku.", 7.5, 10, "troll_club", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=8, reach=1, initiative_modifier=-1, parry_bonus=0)
            npc.character.equipment["korpus"] = Item("gruba skóra", "Naturalnie twarda skóra trolla.", 0.0, 0, "troll_hide_armor", "armor", "korpus", protection=1)
            return self._finalize(npc)
        if vnum == "warband_captain":
            c = Character("Kapitan")
            c.stats = CharacterStats(15, 13, 15, 12, 13, 150)
            boss = NPC(
                vnum="warband_captain",
                name="kapitan bandy",
                short_desc="Kapitan bandy stoi tu w zużytej zbroi i mierzy wszystkich wzrokiem.",
                long_desc="To nie jest zwykły rabuś, lecz człowiek przyzwyczajony do wydawania rozkazów i przeżywania zasadzek.",
                zone="Zachod_Las",
                faction="REBELS",
                ai_state="AGGRESSIVE",
                room_id=room_id,
                character=c,
                home_room_id=room_id,
                respawn_delay_seconds=600,
            )
            boss.character.combat_style = combat_style_for_vnum(boss.vnum)
            boss.character.equipment["prawa_reka"] = Item("kapitański topór", "Ciężki topór z karbowanym ostrzem.", 3.8, 90, "captain_axe", "weapon", "prawa_reka", damage_type="obuchowa", base_damage=6, reach=1, initiative_modifier=0, parry_bonus=1)
            boss.character.equipment["lewa_reka"] = Item("wzmocniona tarcza", "Tarcza okuta żelazem.", 4.0, 70, "captain_shield", "shield", "lewa_reka", protection=2, shield_block=3)
            boss.character.equipment["korpus"] = Item("łuskowa zbroja", "Pancerz poskładany z wielu zdobycznych elementów.", 9.5, 120, "scale_armor", "armor", "korpus", protection=3)
            return self._finalize(boss)
        c = Character("Wilk")
        c.stats = CharacterStats(8, 13, 8, 12, 6, 80)
        wolf = NPC(
            vnum="wolf",
            name="wilk",
            short_desc="Wilk warczy nisko przy ziemi.",
            long_desc="Chude zwierzę o żółtych ślepiach.",
            zone="Zachod_Las",
            faction="REBELS",
            ai_state="AGGRESSIVE",
            room_id=room_id,
            character=c,
            home_room_id=room_id,
        )
        wolf.character.inventory.append(Item("wilcza skóra", "Szorstka skóra zdjęta z wilka.", 1.0, 8, "wolf_pelt"))
        wolf.character.combat_style = combat_style_for_vnum(wolf.vnum)
        wolf.character.equipment["prawa_reka"] = Item("kły wilka", "Naturalna broń drapieżnika.", 0.0, 0, "wolf_bite", "weapon", "prawa_reka", damage_type="kluta", base_damage=3, reach=1, initiative_modifier=2, parry_bonus=0)
        return self._finalize(wolf)
