from __future__ import annotations

from collections import deque

from astergard.world.content import apply_content_pack
from astergard.world.models import Exit, Location

STARTING_ROOM_ID = 14

OPPOSITE = {
    "polnoc": "poludnie",
    "poludnie": "polnoc",
    "wschod": "zachod",
    "zachod": "wschod",
    "polnocny-wschod": "poludniowy-zachod",
    "poludniowy-zachod": "polnocny-wschod",
    "polnocny-zachod": "poludniowy-wschod",
    "poludniowy-wschod": "polnocny-zachod",
    "gora": "dol",
    "dol": "gora",
}

REGION_RANGES: tuple[tuple[int, int, str, str], ...] = (
    (0, 59, "Centrum_Twierdza", "Twierdza Astergard"),
    (60, 79, "Podgrodzie", "Podgrodzie Astergardu"),
    (80, 94, "Haldun", "Haldun"),
    (95, 109, "Osada_Mysliwych", "Osada Myśliwych"),
    (110, 124, "Forteca_Dungrim", "Forteca Dungrim"),
    (125, 134, "Straznica_Przeleczy", "Strażnica Przełęczy"),
    (135, 179, "Trakty", "Trakty Północnego Pogranicza"),
    (180, 209, "Boczne_Drogi", "Przedpola Astergardu"),
    (210, 279, "Puszcza_Ciszy", "Puszcza Ciszy"),
    (280, 334, "Knieja_Cichych_Sciezek", "Knieja Cichych Ścieżek"),
    (335, 389, "Gory_Mekhara", "Góry Mekhara"),
    (390, 424, "Kopalnia_Zelaza", "Kopalnia Żelaza"),
    (425, 454, "Ruiny_Karshold", "Ruiny Karshold"),
    (455, 474, "Jaskinie_Wilkow", "Jaskinie Wilków"),
    (475, 499, "Bagna_Hookri", "Bagna Hookri"),
)

REGION_LABELS: dict[str, str] = {zone: label for _, _, zone, label in REGION_RANGES}

REGION_MAP_ORIGINS: dict[str, tuple[int, int, int]] = {
    "Centrum_Twierdza": (0, 0, 0),
    "Podgrodzie": (40, 0, 0),
    "Haldun": (80, 10, 0),
    "Osada_Mysliwych": (120, 10, 0),
    "Forteca_Dungrim": (160, 0, 1),
    "Straznica_Przeleczy": (200, 18, 1),
    "Trakty": (240, 0, 0),
    "Boczne_Drogi": (280, -10, 0),
    "Puszcza_Ciszy": (320, 0, 0),
    "Knieja_Cichych_Sciezek": (360, 10, 0),
    "Gory_Mekhara": (400, 18, 1),
    "Kopalnia_Zelaza": (440, 18, 2),
    "Ruiny_Karshold": (480, -10, 0),
    "Jaskinie_Wilkow": (520, -10, 2),
    "Bagna_Hookri": (560, -20, 0),
}

MAP_DIRECTION_DELTAS: dict[str, tuple[int, int, int]] = {
    "polnoc": (0, 1, 0),
    "poludnie": (0, -1, 0),
    "wschod": (1, 0, 0),
    "zachod": (-1, 0, 0),
    "polnocny-wschod": (1, 1, 0),
    "polnocny-zachod": (-1, 1, 0),
    "poludniowy-wschod": (1, -1, 0),
    "poludniowy-zachod": (-1, -1, 0),
    "gora": (0, 0, 1),
    "dol": (0, 0, -1),
}

_CITY_BASE_NAMES = {
    0: "Brama Dymnych Chorągwi",
    1: "Plac Przed Wartownią",
    2: "Targ Północny",
    3: "Kramy Płócienników",
    4: "Podcienia Kupieckie",
    5: "Zaułek za Kramami",
    6: "Chata Drwala",
    7: "Zagroda Koźlarza",
    8: "Kładka nad Rynsztokiem",
    9: "Schody do Cystern",
    10: "Dom Snycerza",
    11: "Stary Spichlerz",
    12: "Kuźnia przy Murze",
    13: "Szeroka Brukowana",
    14: "Karczma pod Żurawiem",
    15: "Tyły Karczmy",
    16: "Mała Stajnia",
    17: "Róg Bednarzy",
    18: "Ulica Popielarzy",
    19: "Pod Bramą Solną",
    20: "Trakt Przy Murze",
    21: "Dziedziniec Suchych Studni",
    22: "Zaułek Garbarzy",
    23: "Ulica Przy Składach",
    24: "Cichy Przesmyk",
    25: "Plac Wozów",
    26: "Studnia Żołnierska",
    27: "Próg Lazaretu",
    28: "Izba Cyrulika",
    29: "Dziedziniec Magazynów",
    30: "Przejście pod Łukiem",
    31: "Warsztat Łuczarza",
    32: "Plac Musztry",
    33: "Cień Wieży Zachodniej",
    34: "Zbrojownia Zewnętrzna",
    35: "Pralnia przy Kanale",
    36: "Kamienny Przepust",
    37: "Ogród Ziół",
    38: "Szopa Rybaków",
    39: "Mały Mostek",
    40: "Skwer Dłużników",
    41: "Ulica Cieśli",
    42: "Boczna Furta",
    43: "Przy Słupie Ogłoszeń",
    44: "Dom Pisarza",
    45: "Schody Wartowników",
    46: "Kram Świecarza",
    47: "Rynek Żelazny",
    48: "Przejście Rymarzy",
    49: "Plac Popasowy",
    50: "Ciemna Sień",
    51: "Górka Strażnicza",
    52: "Kantor Wagowy",
    53: "Zaułek Farbiarzy",
    54: "Skład Soli",
    55: "Niska Brama",
    56: "Koniec Bruku",
    57: "Droga pod Palisadą",
    58: "Stary Cmentarzyk",
    59: "Kapliczka Podróżnych",
}

_REGION_FALLBACKS = {
    "Podgrodzie": "Przedmieścia żyją tu dymem z pieców, błotem spod kół i ruchem ludzi wracających z murów.",
    "Haldun": "Rolnicza wieś trzyma się ziemi, studni i pracy, która zaczyna się jeszcze przed świtem.",
    "Osada_Mysliwych": "Łowiecka osada pachnie dymem, skórą i świeżo okorowanym drewnem.",
    "Forteca_Dungrim": "Graniczny garnizon nie śpi długo; tu liczy się warta, zapasy i porządek.",
    "Straznica_Przeleczy": "Północna strażnica żyje meldunkami, wiatrem i ruchem karawan na stromej drodze.",
    "Trakty": "Główne trakty są rzekami kurzu, błota i wieści niesionych między osadami.",
    "Boczne_Drogi": "Przedpola Astergardu noszą ślady wozów, patroli i tych, którzy wolą nie jechać główną bramą.",
    "Puszcza_Ciszy": "Puszcza tłumi głosy, ale nie ukrywa wszystkiego; tropy, popiół i wilgoć opowiadają własną historię.",
    "Knieja_Cichych_Sciezek": "Głębsza knieja jest starsza, cięższa i mniej chętna, by oddawać drogę za darmo.",
    "Gory_Mekhara": "Góry noszą metal, wiatr i twarde lekcje dla każdego, kto chce przejść wyżej.",
    "Kopalnia_Zelaza": "Kopalnia żyje oddechem szybów, skrzypieniem wózków i ciężarem rudy.",
    "Ruiny_Karshold": "Ruiny pamiętają ogień dłużej niż ludzi, którzy je spalili.",
    "Jaskinie_Wilkow": "Jaskinie są labiryntem sierści, kości i zbyt dawno niepokojonej ciemności.",
    "Bagna_Hookri": "Bagna Hookri oddychają mgłą, torfem i cierpliwością wszystkiego, co nie chce zostać znalezione.",
}


class WorldManager:
    def __init__(self) -> None:
        self.locations: dict[int, Location] = {}
        self.respawn_queue: list[dict[str, object]] = []
        self.ambient_messages_by_zone: dict[str, str] = {}

    def generate_world(self, seed: int = 12345) -> None:  # seed kept for API compatibility
        self.locations.clear()
        self.respawn_queue.clear()
        self.ambient_messages_by_zone.clear()
        self._create_locations()
        self._build_region_graph()
        apply_content_pack(self.locations)
        self._assign_map_coordinates()

    def set_ambient_message(self, zone: str, message: str) -> None:
        if zone:
            self.ambient_messages_by_zone[zone] = message

    def pop_ambient_message(self, zone: str) -> str | None:
        if not zone:
            return None
        return self.ambient_messages_by_zone.pop(zone, None)

    def _create_locations(self) -> None:
        for start, end, zone, label in REGION_RANGES:
            for room_id in range(start, end + 1):
                if zone == "Centrum_Twierdza":
                    name = _CITY_BASE_NAMES[room_id]
                    if room_id == 15:
                        description = "Tyły Karczmy należy do wąskiego zaplecza za kuchennym wejściem. Przy ścianie stoją puste beczki, skrzynie po warzywach i poplamiony stół do czyszczenia kufli."
                    else:
                        description = "Kamienne serce Twierdzy Astergard: bruk, dym z pieców, ruch wozów i echo kroków odbite od murów."
                else:
                    offset = room_id - start + 1
                    name = f"{label} {offset}"
                    description = _REGION_FALLBACKS[zone]
                self.locations[room_id] = Location(room_id, name, description, zone)

    def _build_region_graph(self) -> None:
        self._build_astergard_graph()
        self._build_d351b_outer_settlement_graph()
        self._build_d351c_silent_forest_graph()
        self._build_d351d_deep_forest_graph()
        self._build_d351e_mountains_pass_graph()
        self._build_d351f_mines_caves_graph()
        self._build_d351g_ruins_graph()
        self._build_d351h_swamp_graph()
        self._build_inter_region_roads()

    def _build_astergard_graph(self) -> None:
        # Organiczny układ miasta: bramy, rynek, dzielnice rzemieślnicze, garnizon,
        # magazyny i wyjścia na podgrodzie. Nie jest to prostokątna siatka.
        links = [
            (0, 1, "wschod"), (0, 20, "poludnie"), (1, 2, "wschod"), (1, 25, "poludnie"),
            (2, 3, "wschod"), (3, 4, "wschod"), (4, 5, "poludniowy-wschod"),
            (5, 14, "poludnie"), (14, 15, "poludnie"), (15, 16, "wschod"),
            (16, 25, "poludniowy-zachod"), (2, 10, "poludnie"), (10, 11, "wschod"),
            (11, 12, "wschod"), (12, 13, "wschod"), (13, 14, "wschod"),
            (20, 21, "wschod"), (21, 22, "wschod"), (22, 23, "wschod"), (23, 24, "wschod"),
            (20, 26, "poludnie"), (21, 27, "poludnie"), (22, 28, "poludnie"),
            (23, 29, "poludnie"), (24, 30, "poludniowy-zachod"),
            (25, 26, "wschod"), (26, 27, "wschod"), (27, 28, "wschod"),
            (28, 29, "wschod"), (29, 30, "wschod"),
            (30, 31, "poludnie"), (31, 32, "wschod"), (32, 33, "wschod"),
            (33, 34, "polnoc"), (34, 35, "wschod"), (35, 36, "poludnie"),
            (36, 37, "poludnie"), (37, 38, "zachod"), (38, 39, "poludnie"),
            (39, 40, "zachod"), (40, 41, "zachod"), (41, 42, "polnoc"),
            (42, 43, "polnoc"), (43, 44, "wschod"), (44, 45, "wschod"),
            (45, 46, "wschod"), (46, 47, "poludnie"), (47, 48, "zachod"),
            (48, 49, "zachod"), (49, 50, "poludnie"), (50, 51, "wschod"),
            (51, 52, "wschod"), (52, 53, "poludnie"), (53, 54, "zachod"),
            (54, 55, "poludnie"), (55, 56, "zachod"), (56, 57, "zachod"),
            (57, 58, "poludnie"), (58, 59, "wschod"),
            # skróty miejskie i naturalne obejścia
            (4, 13, "poludniowy-zachod"), (8, 21, "poludnie"), (12, 22, "poludniowy-zachod"),
            (17, 18, "wschod"), (18, 19, "wschod"), (19, 24, "poludnie"),
            (32, 45, "poludniowy-zachod"), (47, 52, "poludniowy-wschod"),
            (55, 59, "poludniowy-wschod"), (6, 7, "wschod"), (7, 8, "wschod"), (8, 9, "wschod"),
            (9, 10, "poludniowy-wschod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)


    def _build_d351b_outer_settlement_graph(self) -> None:
        # D35.1B: hand-authored topology for the playable belt outside Astergard.
        # The map is intentionally not a grid: roads bend, villages branch around
        # wells/fields, and military sites are chokepoints rather than open meshes.
        links = [
            # Podgrodzie 60-79: muddy lower town under the southern wall.
            (60, 61, "poludnie"), (61, 62, "wschod"), (62, 63, "poludniowy-wschod"),
            (63, 64, "wschod"), (64, 65, "poludnie"), (65, 66, "poludnie"),
            (66, 67, "zachod"), (67, 68, "poludniowy-zachod"), (68, 69, "zachod"),
            (69, 70, "poludnie"), (70, 71, "wschod"), (71, 72, "wschod"),
            (72, 73, "poludniowy-wschod"), (73, 74, "wschod"), (74, 75, "poludnie"),
            (75, 76, "zachod"), (76, 77, "zachod"), (77, 78, "poludniowy-zachod"),
            (78, 79, "poludnie"), (61, 66, "poludniowy-wschod"), (64, 72, "poludniowy-zachod"),
            (70, 135, "poludnie"), (79, 137, "poludniowy-wschod"),

            # Haldun 80-94: compact farming village north-west of the city.
            (80, 81, "polnoc"), (81, 82, "wschod"), (82, 83, "wschod"),
            (83, 84, "poludniowy-wschod"), (84, 85, "poludnie"), (85, 86, "zachod"),
            (86, 87, "zachod"), (87, 88, "poludniowy-zachod"), (88, 89, "poludnie"),
            (89, 90, "wschod"), (90, 91, "wschod"), (91, 92, "polnocny-wschod"),
            (92, 93, "wschod"), (93, 94, "poludnie"), (84, 140, "poludniowy-wschod"),
            (94, 181, "zachod"),

            # Osada Myśliwych 95-109: eastern hide, smokehouses and forest edge.
            (95, 96, "wschod"), (96, 97, "wschod"), (97, 98, "polnocny-wschod"),
            (98, 99, "wschod"), (99, 100, "poludnie"), (100, 101, "poludnie"),
            (101, 102, "zachod"), (102, 103, "poludniowy-zachod"), (103, 104, "zachod"),
            (104, 105, "poludnie"), (105, 106, "wschod"), (106, 107, "wschod"),
            (107, 108, "poludniowy-wschod"), (108, 109, "wschod"), (101, 145, "poludniowy-zachod"),
            (109, 210, "wschod"),

            # Forteca Dungrim 110-124: western military knot and caravan control.
            (110, 111, "wschod"), (111, 112, "wschod"), (112, 113, "poludnie"),
            (113, 114, "poludnie"), (114, 115, "zachod"), (115, 116, "zachod"),
            (116, 117, "polnoc"), (117, 118, "polnoc"), (118, 119, "wschod"),
            (119, 120, "wschod"), (120, 121, "poludniowy-wschod"), (121, 122, "poludnie"),
            (122, 123, "zachod"), (123, 124, "zachod"), (116, 150, "poludniowy-wschod"),
            (124, 180, "poludnie"),

            # Main trade roads 135-179: three named tracts meeting at milestones.
            (135, 136, "poludniowy-wschod"), (136, 137, "poludnie"), (137, 138, "poludnie"),
            (138, 139, "poludniowy-zachod"), (139, 140, "zachod"), (140, 141, "poludnie"),
            (141, 142, "poludnie"), (142, 143, "poludniowy-wschod"), (143, 144, "wschod"),
            (144, 145, "wschod"), (145, 146, "poludnie"), (146, 147, "poludnie"),
            (147, 148, "poludniowy-wschod"), (148, 149, "wschod"), (149, 150, "wschod"),
            (150, 151, "polnocny-wschod"), (151, 152, "wschod"), (152, 153, "wschod"),
            (153, 154, "poludniowy-wschod"), (154, 155, "poludnie"), (155, 156, "poludnie"),
            (156, 157, "poludniowy-zachod"), (157, 158, "zachod"), (158, 159, "zachod"),
            (159, 160, "poludnie"), (160, 161, "poludnie"), (161, 162, "poludniowy-wschod"),
            (162, 163, "wschod"), (163, 164, "wschod"), (164, 165, "poludnie"),
            (165, 166, "poludnie"), (166, 167, "poludniowy-zachod"), (167, 168, "zachod"),
            (168, 169, "zachod"), (169, 170, "poludnie"), (170, 171, "poludnie"),
            (171, 172, "poludniowy-wschod"), (172, 173, "wschod"), (173, 174, "wschod"),
            (174, 175, "polnocny-wschod"), (175, 176, "wschod"), (176, 177, "wschod"),
            (177, 178, "poludniowy-wschod"), (178, 179, "poludnie"),
            (142, 185, "zachod"), (154, 190, "poludniowy-zachod"), (166, 195, "zachod"),
            (174, 200, "polnocny-zachod"),

            # Side roads 180-209: old smugglers' lanes, field paths and ford approaches.
            (180, 181, "poludniowy-wschod"), (181, 182, "poludnie"), (182, 183, "wschod"),
            (183, 184, "wschod"), (184, 185, "poludnie"), (185, 186, "poludniowy-wschod"),
            (186, 187, "wschod"), (187, 188, "poludnie"), (188, 189, "poludniowy-zachod"),
            (189, 190, "zachod"), (190, 191, "poludnie"), (191, 192, "poludnie"),
            (192, 193, "wschod"), (193, 194, "wschod"), (194, 195, "poludniowy-wschod"),
            (195, 196, "poludniowy-wschod"), (196, 197, "polnocny-wschod"), (197, 198, "wschod"),
            (198, 199, "poludnie"), (199, 200, "poludnie"), (200, 201, "wschod"),
            (201, 202, "wschod"), (202, 203, "poludniowy-wschod"), (203, 204, "wschod"),
            (204, 205, "poludnie"), (205, 206, "poludniowy-zachod"), (206, 207, "zachod"),
            (207, 208, "poludnie"), (208, 209, "wschod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)

    def _build_d351c_silent_forest_graph(self) -> None:
        # D35.1C: Puszcza Ciszy is a navigable forest, not a rectangular grid.
        # Main hunter/drummer paths bend through landmarks; side loops create
        # hunting grounds, bandit camps and future resource nodes.
        links = [
            # western forest entrance and forester belt
            (210, 211, "wschod"), (211, 212, "wschod"), (212, 213, "poludniowy-wschod"),
            (213, 214, "wschod"), (214, 215, "poludnie"), (215, 216, "poludnie"),
            (216, 217, "poludniowy-zachod"), (217, 218, "zachod"), (218, 219, "poludnie"),
            (219, 220, "wschod"), (220, 221, "poludniowy-wschod"), (221, 222, "wschod"),
            (222, 223, "polnocny-wschod"), (223, 224, "wschod"),

            # old oaks and stream crossing
            (224, 225, "poludnie"), (225, 226, "poludnie"), (226, 227, "poludniowy-wschod"),
            (227, 228, "wschod"), (228, 229, "wschod"), (229, 230, "polnocny-wschod"),
            (230, 231, "wschod"), (231, 232, "poludniowy-wschod"), (232, 233, "poludnie"),
            (233, 234, "poludnie"), (234, 235, "poludniowy-zachod"), (235, 236, "zachod"),
            (236, 237, "poludnie"), (237, 238, "wschod"), (238, 239, "wschod"),

            # bandit and wolf belt
            (239, 240, "poludniowy-wschod"), (240, 241, "wschod"), (241, 242, "polnocny-wschod"),
            (242, 243, "wschod"), (243, 244, "poludnie"), (244, 245, "poludnie"),
            (245, 246, "poludniowy-zachod"), (246, 247, "zachod"), (247, 248, "poludnie"),
            (248, 249, "wschod"), (249, 250, "wschod"), (250, 251, "poludniowy-wschod"),
            (251, 252, "wschod"),

            # eastern deepening and transitions to the next forest
            (252, 253, "polnocny-wschod"), (253, 254, "wschod"), (254, 255, "poludnie"),
            (255, 256, "poludnie"), (256, 257, "poludniowy-zachod"), (257, 258, "zachod"),
            (258, 259, "poludnie"), (259, 260, "poludniowy-wschod"), (260, 261, "wschod"),
            (261, 262, "wschod"), (262, 263, "polnocny-wschod"), (263, 264, "wschod"),
            (264, 265, "poludnie"), (265, 266, "poludnie"), (266, 267, "poludniowy-wschod"),
            (267, 268, "wschod"), (268, 269, "wschod"), (269, 270, "poludnie"),
            (270, 271, "poludnie"), (271, 272, "poludniowy-zachod"), (272, 273, "zachod"),
            (273, 274, "poludnie"), (274, 275, "wschod"), (275, 276, "wschod"),
            (276, 277, "poludniowy-wschod"), (277, 278, "wschod"), (278, 279, "wschod"),

            # local loops, shortcuts and future gameplay pockets
            (212, 218, "poludnie"), (214, 222, "poludniowy-wschod"), (221, 227, "poludnie"),
            (229, 236, "poludniowy-zachod"), (232, 240, "wschod"),
            (238, 246, "poludniowy-wschod"), (244, 251, "wschod"),
            (250, 257, "poludnie"), (256, 263, "wschod"),
            (262, 269, "poludniowy-wschod"), (268, 275, "poludniowy-zachod"),
            (273, 279, "poludniowy-wschod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)


    def _build_d351d_deep_forest_graph(self) -> None:
        # D35.1D: Knieja Cichych Ścieżek is a deeper exploration zone.
        # It keeps a low exit density, uses diagonals for natural turns and
        # provides three controlled transitions: Puszcza, mountains and bogs.
        links = [
            # entry belt from Puszcza Ciszy and old forest road
            (280, 281, "wschod"), (281, 282, "poludniowy-wschod"), (282, 283, "wschod"),
            (283, 284, "polnocny-wschod"), (284, 285, "wschod"), (285, 286, "poludnie"),
            (286, 287, "poludnie"), (287, 288, "poludniowy-zachod"), (288, 289, "zachod"),
            (289, 290, "poludnie"), (290, 291, "wschod"), (291, 292, "wschod"),
            (292, 293, "poludniowy-wschod"), (293, 294, "wschod"),

            # smolars, old signs and central lost paths
            (294, 295, "poludnie"), (295, 296, "poludnie"), (296, 297, "poludniowy-zachod"),
            (297, 298, "zachod"), (298, 299, "poludnie"), (299, 300, "wschod"),
            (300, 301, "wschod"), (301, 302, "polnocny-wschod"), (302, 303, "wschod"),
            (303, 304, "poludnie"), (304, 305, "poludnie"), (305, 306, "poludniowy-wschod"),
            (306, 307, "wschod"), (307, 308, "wschod"), (308, 309, "poludnie"),

            # gaj, hidden bends and rising northern edge
            (309, 310, "poludnie"), (310, 311, "poludniowy-zachod"), (311, 312, "zachod"),
            (312, 313, "poludnie"), (313, 314, "wschod"), (314, 315, "wschod"),
            (315, 316, "poludniowy-wschod"), (316, 317, "wschod"), (317, 318, "polnocny-wschod"),
            (318, 319, "wschod"), (319, 320, "poludnie"), (320, 321, "poludnie"),
            (321, 322, "poludniowy-zachod"), (322, 323, "zachod"), (323, 324, "poludnie"),

            # southern wet exit and eastern deep boundary
            (324, 325, "wschod"), (325, 326, "wschod"), (326, 327, "poludniowy-wschod"),
            (327, 328, "wschod"), (328, 329, "poludnie"), (329, 330, "poludnie"),
            (330, 331, "poludniowy-zachod"), (331, 332, "zachod"), (332, 333, "poludnie"),
            (333, 334, "wschod"),

            # loops and misleading shortcuts: useful for exploration, not a grid
            (282, 288, "poludnie"), (286, 292, "poludniowy-wschod"), (291, 297, "poludnie"),
            (300, 306, "poludnie"), (305, 312, "poludniowy-zachod"), (314, 320, "poludniowy-wschod"),
            (320, 326, "poludniowy-wschod"), (326, 333, "poludniowy-zachod"),
            (303, 310, "poludniowy-wschod"), (317, 324, "poludniowy-zachod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)



    def _build_d351e_mountains_pass_graph(self) -> None:
        # D35.1E: Strażnica Przełęczy and Góry Mekhara form a controlled
        # northern chokepoint. The topology is intentionally sparse: one main
        # caravan/military ascent, a few risky ledges and side pockets for later
        # encounters, not a walkable grid.
        links = [
            # Strażnica Przełęczy 125-134: compact fortification and choke point.
            (125, 126, "wschod"), (126, 127, "wschod"), (127, 128, "polnocny-wschod"),
            (128, 129, "wschod"), (129, 130, "poludnie"), (130, 131, "poludnie"),
            (131, 132, "zachod"), (132, 133, "poludniowy-zachod"), (133, 134, "zachod"),
            (126, 131, "poludniowy-wschod"), (128, 133, "poludniowy-wschod"),

            # Main mountain ascent from the pass.
            (335, 336, "polnoc"), (336, 337, "polnocny-wschod"), (337, 338, "wschod"),
            (338, 339, "polnocny-wschod"), (339, 340, "wschod"), (340, 341, "poludnie"),
            (341, 342, "poludniowy-wschod"), (342, 343, "wschod"), (343, 344, "polnocny-wschod"),
            (344, 345, "wschod"), (345, 346, "poludnie"), (346, 347, "poludnie"),
            (347, 348, "poludniowy-zachod"), (348, 349, "zachod"), (349, 350, "poludnie"),
            (350, 351, "wschod"), (351, 352, "wschod"), (352, 353, "polnocny-wschod"),
            (353, 354, "wschod"), (354, 355, "poludnie"),

            # High ledges and old guard road.
            (355, 356, "poludnie"), (356, 357, "poludniowy-wschod"), (357, 358, "wschod"),
            (358, 359, "wschod"), (359, 360, "polnocny-wschod"), (360, 361, "wschod"),
            (361, 362, "poludnie"), (362, 363, "poludnie"), (363, 364, "poludniowy-zachod"),
            (364, 365, "zachod"), (365, 366, "poludnie"), (366, 367, "wschod"),
            (367, 368, "wschod"), (368, 369, "poludniowy-wschod"), (369, 370, "wschod"),

            # Mining approach and eastern descent to the future Kopalnia Żelaza.
            (370, 371, "poludnie"), (371, 372, "poludnie"), (372, 373, "poludniowy-zachod"),
            (373, 374, "zachod"), (374, 375, "poludnie"), (375, 376, "wschod"),
            (376, 377, "wschod"), (377, 378, "polnocny-wschod"), (378, 379, "wschod"),
            (379, 380, "poludnie"), (380, 381, "poludnie"), (381, 382, "poludniowy-wschod"),
            (382, 383, "wschod"), (383, 384, "wschod"), (384, 385, "poludnie"),
            (385, 386, "poludnie"), (386, 387, "poludniowy-zachod"), (387, 388, "zachod"),
            (388, 389, "poludnie"),

            # Mountain loops and side approaches, including a route from the deep forest.
            (334, 335, "polnocny-wschod"), (129, 335, "polnocny-zachod"),
            (337, 343, "poludniowy-wschod"), (341, 348, "poludnie"),
            (346, 352, "polnocny-wschod"), (352, 359, "poludniowy-wschod"),
            (358, 365, "poludnie"), (363, 370, "poludniowy-wschod"),
            (369, 376, "poludniowy-zachod"), (376, 383, "poludniowy-wschod"),
            (382, 389, "poludniowy-zachod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)


    def _build_d351f_mines_caves_graph(self) -> None:
        # D35.1F: Kopalnia Żelaza and Jaskinie Wilków. The mine has vertical
        # structure and operational logic: surface yard, upper works, lower
        # works and deep wet galleries. The wolf caves are organic, tighter and
        # less legible than human tunnels.
        links = [
            # Kopalnia Żelaza 390-424: entrance yard and upper level.
            (390, 391, "wschod"), (391, 392, "wschod"), (392, 393, "poludnie"),
            (393, 394, "zachod"), (394, 395, "dol"), (395, 396, "wschod"),
            (396, 397, "wschod"), (397, 398, "polnocny-wschod"), (398, 399, "wschod"),
            (399, 400, "poludnie"), (400, 401, "poludnie"), (401, 402, "poludniowy-zachod"),
            (402, 403, "zachod"), (403, 404, "poludnie"),

            # Second level and working chambers.
            (404, 405, "dol"), (405, 406, "wschod"), (406, 407, "wschod"),
            (407, 408, "polnocny-wschod"), (408, 409, "wschod"), (409, 410, "poludnie"),
            (410, 411, "poludnie"), (411, 412, "poludniowy-zachod"), (412, 413, "zachod"),
            (413, 414, "poludnie"), (414, 415, "wschod"), (415, 416, "wschod"),

            # Deep galleries and wet exits.
            (416, 417, "dol"), (417, 418, "wschod"), (418, 419, "wschod"),
            (419, 420, "poludniowy-wschod"), (420, 421, "wschod"), (421, 422, "poludnie"),
            (422, 423, "poludnie"), (423, 424, "poludniowy-zachod"),

            # Mine loops: work routes, ventilation and unsafe shortcuts.
            (392, 397, "dol"), (399, 407, "poludniowy-wschod"), (406, 414, "poludniowy-wschod"),
            (412, 418, "dol"), (418, 424, "poludnie"),

            # Jaskinie Wilków 455-474: natural lair connected to the old mine.
            (455, 456, "poludnie"), (456, 457, "polnocny-wschod"), (457, 458, "wschod"),
            (458, 459, "poludnie"), (459, 460, "poludnie"), (460, 461, "poludniowy-zachod"),
            (461, 462, "zachod"), (462, 463, "poludnie"), (463, 464, "poludniowy-wschod"),
            (464, 465, "wschod"), (465, 466, "wschod"), (466, 467, "polnocny-wschod"),
            (467, 468, "wschod"), (468, 469, "poludnie"), (469, 470, "poludnie"),
            (470, 471, "poludniowy-zachod"), (471, 472, "zachod"), (472, 473, "poludnie"),
            (473, 474, "wschod"),

            # Cave loops and second way back toward mine air shafts.
            (457, 462, "poludnie"), (462, 468, "poludniowy-wschod"),
            (466, 472, "poludniowy-zachod"), (470, 474, "poludniowy-wschod"),
            (424, 455, "zachod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)

    def _build_d351g_ruins_graph(self) -> None:
        # D35.1G: Ruiny Karshold are a linear traversal through the old fort:
        # approach road, ruined outer wall, inner keep, crypt access and the
        # collapsed exit toward the swamp.
        links = [
            (425, 426, "wschod"), (426, 427, "poludnie"), (427, 428, "wschod"),
            (428, 429, "poludnie"), (429, 430, "wschod"), (430, 431, "poludnie"),
            (431, 432, "wschod"), (432, 433, "poludnie"), (433, 434, "wschod"),
            (434, 435, "poludnie"), (435, 436, "wschod"), (436, 437, "poludnie"),
            (437, 438, "wschod"), (438, 439, "poludnie"), (439, 440, "wschod"),
            (440, 441, "poludnie"), (441, 442, "wschod"), (442, 443, "poludnie"),
            (443, 444, "wschod"), (444, 445, "poludnie"), (445, 446, "wschod"),
            (446, 447, "poludnie"), (447, 448, "wschod"), (448, 449, "poludnie"),
            (449, 450, "wschod"), (450, 451, "poludnie"), (451, 452, "wschod"),
            (452, 453, "poludnie"), (453, 454, "wschod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)

    def _build_d351h_swamp_graph(self) -> None:
        # D35.1H: Bagna Hookri are wet, winding and intentionally low-visibility.
        links = [
            (475, 476, "wschod"), (476, 477, "wschod"), (477, 478, "poludniowy-wschod"),
            (478, 479, "wschod"), (479, 480, "poludnie"), (480, 481, "poludnie"),
            (481, 482, "zachod"), (482, 483, "poludniowy-zachod"), (483, 484, "zachod"),
            (484, 485, "poludnie"), (485, 486, "wschod"), (486, 487, "wschod"),
            (487, 488, "poludniowy-wschod"), (488, 489, "wschod"), (489, 490, "poludnie"),
            (490, 491, "poludnie"), (491, 492, "zachod"), (492, 493, "poludniowy-zachod"),
            (493, 494, "zachod"), (494, 495, "poludnie"), (495, 496, "wschod"),
            (496, 497, "wschod"), (497, 498, "poludniowy-wschod"), (498, 499, "wschod"),
            (476, 482, "poludnie"), (479, 487, "poludniowy-wschod"), (485, 492, "poludnie"),
            (490, 496, "poludniowy-zachod"), (478, 484, "polnocny-wschod"), (494, 499, "poludniowy-wschod"),
        ]
        for a, b, direction in links:
            self._link(a, b, direction)

    def _build_inter_region_roads(self) -> None:
        # Główne wyjścia z Astergardu do przyszłych ręcznie rozpisywanych regionów.
        roads = [
            (56, 60, "poludnie"),   # podgrodzie przez niską bramę
            (59, 135, "poludniowy-wschod"),  # zejście ku południowemu traktowi przy kapliczce
            (0, 125, "polnoc"),     # droga do strażnicy przełęczy
            (42, 180, "zachod"),    # boczna furta na stare drogi
            (55, 95, "wschod"),     # wyjście ku osadzie myśliwych
            (19, 80, "polnoc"),     # droga ku Haldun
            (125, 335, "polnoc"), (134, 110, "poludniowy-zachod"), (179, 210, "polnocny-zachod"),
            (209, 280, "wschod"), (279, 280, "polnocny-wschod"), (334, 425, "poludnie"), (389, 390, "poludniowy-wschod"),
            (424, 455, "zachod"), (454, 475, "poludnie"),
        ]
        for a, b, direction in roads:
            self._link(a, b, direction)

    def _assign_map_coordinates(self) -> None:
        for _, _, zone, _ in REGION_RANGES:
            room_ids = sorted(room_id for room_id, loc in self.locations.items() if loc.zone == zone)
            if not room_ids:
                continue
            anchor = room_ids[0]
            base_x, base_y, base_z = REGION_MAP_ORIGINS.get(zone, (0, 0, 0))
            assigned: dict[int, tuple[int, int, int]] = {anchor: (base_x, base_y, base_z)}
            occupied: set[tuple[int, int, int]] = {(base_x, base_y, base_z)}
            queue: deque[int] = deque([anchor])
            while queue:
                room_id = queue.popleft()
                loc = self.locations[room_id]
                origin = assigned[room_id]
                for direction, exit_ in sorted(loc.exits.items()):
                    target = self.locations.get(exit_.target_room)
                    if target is None or target.zone != zone or target.id in assigned:
                        continue
                    delta = MAP_DIRECTION_DELTAS.get(direction)
                    if delta is None:
                        continue
                    desired = (origin[0] + delta[0], origin[1] + delta[1], origin[2] + delta[2])
                    coords = self._nearest_free_coords(desired, occupied)
                    assigned[target.id] = coords
                    occupied.add(coords)
                    queue.append(target.id)
            for index, room_id in enumerate(room_ids):
                if room_id in assigned:
                    continue
                fallback = (base_x + (index % 8), base_y - (index // 8), base_z)
                coords = self._nearest_free_coords(fallback, occupied)
                assigned[room_id] = coords
                occupied.add(coords)
            for room_id, (x, y, z) in assigned.items():
                loc = self.locations[room_id]
                loc.map_x = x
                loc.map_y = y
                loc.map_z = z

    def _nearest_free_coords(self, desired: tuple[int, int, int], occupied: set[tuple[int, int, int]]) -> tuple[int, int, int]:
        if desired not in occupied:
            return desired
        for radius in range(1, 12):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    for dz in range(-1, 2):
                        if abs(dx) + abs(dy) + abs(dz) > radius + 1:
                            continue
                        candidate = (desired[0] + dx, desired[1] + dy, desired[2] + dz)
                        if candidate not in occupied:
                            return candidate
        return (desired[0] + 13, desired[1] + 13, desired[2])

    def _link(self, a: int, b: int, direction: str) -> None:
        if a not in self.locations or b not in self.locations:
            raise KeyError(f"Cannot link missing rooms: {a} -> {b}")
        if direction not in OPPOSITE:
            raise KeyError(f"Unknown direction: {direction}")
        if direction not in self.locations[a].exits:
            self.locations[a].exits[direction] = Exit(b)
        opp = OPPOSITE[direction]
        if opp not in self.locations[b].exits:
            self.locations[b].exits[opp] = Exit(a)

    def get_location(self, loc_id: int) -> Location | None:
        return self.locations.get(loc_id)

    def unlock_exit(self, room_id: int, direction: str) -> bool:
        loc = self.locations[room_id]
        ex = loc.exits.get(direction)
        if not ex:
            return False
        ex.is_locked = False
        other = self.locations[ex.target_room]
        for back in other.exits.values():
            if back.target_room == room_id:
                back.is_locked = False
        return True
