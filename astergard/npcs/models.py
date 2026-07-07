from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from astergard.characters.models import Character, CharacterStats
from astergard.items.models import Item
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

    def transition_ai_state(self, target: str | NPCState) -> None:
        current = parse_npc_state(self.ai_state)
        next_state = parse_npc_state(target)
        self.ai_state = NPC_STATE_MACHINE.validate(current, next_state).value

    def dialogue(self, topic: str = "default") -> str:
        lines = self.dialogue_tree.get(topic) or self.dialogue_tree.get("default") or ["Milczy."]
        return lines[0]


class NPCFactory:
    def _finalize(self, npc: NPC) -> NPC:
        profile = threat_for_vnum(npc.vnum)
        npc.threat_tier = profile.tier
        npc.threat_label = profile.label
        npc.respawn_delay_seconds = max(30, int(npc.respawn_delay_seconds * profile.respawn_multiplier))
        apply_threat_profile(npc.character, profile)
        return npc

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
                dialogue_tree={
                    "default": ["Pilnuj drogi i nie zawracaj ludziom głowy."],
                    "brama": ["Przy bramie najłatwiej o kłopoty, więc patrzymy tu podwójnie uważnie."],
                },
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
                dialogue_tree={
                    "default": ["Siadaj albo idź dalej, ale nie blokuj przejścia."],
                    "piwo": ["Piwo jest ciemne, bo ludzie chcą zapomnieć, nie błyszczeć."],
                },
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
                    "mikstura",
                    "Gorzki napar regenerujący.",
                    0.2,
                    15,
                    "potion",
                    "potion",
                    is_consumable=True,
                    effects_on_consume={"restore_stamina": 30},
                ),
                Item(
                    "włócznia",
                    "Prosta włócznia strażnicza.",
                    2.2,
                    30,
                    "spear",
                    "weapon",
                    "prawa_reka",
                    damage_type="kluta",
                    base_damage=5,
                    reach=2,
                    initiative_modifier=-1,
                    parry_bonus=0,
                ),
            ]
            npc.dialogue_tree = {
                "default": ["Kupuj szybko albo odejdź od lady."],
                "wilki": ["Wilki schodzą blisko traktu. Przynieś mi jedną skórę, a zapłacę."],
            }
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
