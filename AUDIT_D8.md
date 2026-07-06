# AUDIT D8 — CommandBus i fabryki handlerów

## Cel
Usunąć pośrednią znajomość kontenera usług z komend. Po D7 komendy nadal wywoływały `ctx._services.*`, czyli znały prywatny graf aplikacyjny przez kontekst. D8 przenosi wiązanie usług do etapu bootstrapu.

## Zmiany wykonane
- Dodano `astergard/application/command_bus.py`.
- Dodano `CommandBus`, który instaluje aliasy i kierunki w `CommandDispatcher`.
- `commands/registration.py` buduje command bus na podstawie `GameServices`, ale komendy nie otrzymują już kontenera usług w runtime.
- Moduły komend eksportują funkcje `build_*_handlers(service)`, które tworzą handlery z usługą zamkniętą w closure.
- `SessionFlow.send_initial_view()` używa dispatchera zamiast importować `cmd_look`.
- `GameServer._install_compatibility_methods()` wiąże publiczne metody kompatybilności z handlerami z dispatchera.

## Wynik testów

```text
python3 -W error::ResourceWarning -m unittest discover tests
Ran 32 tests in 0.130s
OK
```

## Dowody architektoniczne
- `astergard/commands/*.py` poza `registration.py` nie zawiera `ctx._services` ani `ctx.services`.
- `CommandBus` jest jedynym punktem wiązania aliasów komend z gotowymi handlerami.
- Handlery komend są nadal w swoich modułach domenowych, więc istniejące testy modułowości przechodzą.

## Krytyczna ocena
D8 poprawia separację komend od kontenera usług, ale nadal istnieje przejściowy adapter `GameContext`, który sam buduje wąskie konteksty na podstawie prywatnego `_services`. To jest akceptowalne na tym etapie, ale D9 powinien przenieść budowanie use-case contexts poza `GameContext` albo ograniczyć `GameContext` do danych sesji i portów jawnie przekazanych przez factory.

## Następny etap
D9 — uproszczenie `GameContext` do danych sesji i jawnych context factories; dodatkowo poprawa testów integracyjnych pętli command dispatcher → command bus → service.
