# AUDIT_D52_WORLD_RENDERER_BASELINE

Baseline audit of the current world renderer before the D52 rewrite.

## Main findings

### 1. `ExplorationService.look()` assembles the room as disconnected modules

Source: `astergard/application/services/exploration_service.py`

Observed structure:
- title line,
- location description,
- time-of-day sentence,
- weather sentence,
- season sentence,
- world-state sentence,
- ambient sentence,
- exit sentence,
- item sentence,
- NPC sentence,
- other-player sentence.

This is the exact pattern that creates the "list of paragraphs" effect instead of one coherent scene.

Concrete example from the current game start room:

```text
Brama Dymnych Chorągwi.
Wąska brama wciska trakt między kamienny mur i czarne belki strażnicy.
...
Świt zmywa z krajobrazu nocny ciężar...
Lato trzyma dzień długo przy sobie...
Świat trwa tu w zwyczajnym porządku...
Drogi stąd prowadzą dalej przez znane i mniej znane przejścia.
Na północ prowadzi droga. Na południe prowadzi droga. Na wschód prowadzi droga.
Na ziemi spoczywają żelazny klucz.
W pobliżu są Żołnierz Szóstej Kompanii stoi tutaj. Kupiec sprawdza sakwy przy pasie.
```

### 2. Generic exit text is still used

Source: `astergard/application/services/exploration_service.py`

Problematic templates:
- `Drogi stąd prowadzą dalej przez znane i mniej znane przejścia.`
- `Na {kierunek} prowadzi droga.`
- `W górę wiedzie przejście.`
- `W dół prowadzą schody lub ciemniejszy otwór.`

These are mechanical and do not encode exit type, state, visibility, or destination.

### 3. Weather and season are rendered as separate standalone prose blocks

Sources:
- `astergard/narrative.py`
- `astergard/weather/time_weather.py`

Current strings are self-contained sentences like:
- `Świt zmywa z krajobrazu nocny ciężar...`
- `Lato trzyma dzień długo przy sobie...`
- `Wiatr przechodzi przez okolicę i zaraz znika.`

These are technically grammatical, but repeated across rooms they read like filler modules.

### 4. Ground items are grammatically fragile

Source: `astergard/application/services/exploration_service.py`

Current room output uses:
- `Na ziemi spoczywają ...`

This fails on:
- singular items,
- furniture and containers,
- mixed-category item lists,
- count agreement,
- item presentation state.

### 5. NPC presentation leaks systemy / mechanically concatenated text

Sources:
- `astergard/application/services/exploration_service.py`
- `astergard/npcs/models.py`

Current scene output uses:
- `W pobliżu są ...`
- `npc.scene_line()` joined with `. `

That can yield unnatural forms like:
- `W pobliżu są Żołnierz rozpoczyna zwykły dzień.`

`NPC.scene_line()` currently concatenates the NPC name and daily activity in a way that duplicates role names and produces awkward sentence shape.

### 6. The model layer lacks explicit scene semantics

Sources:
- `astergard/world/models.py`
- `astergard/items/models.py`
- `astergard/npcs/models.py`

Missing or under-specified data:
- exit type,
- exit width / material / visibility,
- item presentation category,
- item placement,
- grammatical forms for visible entities,
- NPC scene position and richer scene metadata,
- location-level grammatical forms.

### 7. World text templates are overly repetitive

Sources:
- `astergard/world/manager.py`
- `astergard/world/content.py`
- `astergard/weather/time_weather.py`

The world generator relies heavily on shared fallback prose and repeated regional atmospherics. This is acceptable as a data source, but not as the final presentation layer.

## Baseline decision

The current renderer is technically functional, but it does not satisfy the D52 requirement for a semantically composed world scene.
The rewrite should focus on:
- a scene model,
- a planning layer,
- a renderer with Polish agreement and grouping,
- removal of the generic exit / item / NPC templates.
