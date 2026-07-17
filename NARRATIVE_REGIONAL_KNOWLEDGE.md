# Regional Knowledge Banks

The narrative system now uses typed regional knowledge banks as input for planning and realization.

## Structure

- `RegionalKnowledgeEntry` stores one material, construction, trace, natural, or culture item.
- `RegionalKnowledgeBank` groups entries for a region and exposes a deterministic selection surface.
- `region_style_profile(region_id)` derives a `StyleProfile` from the bank.
- `audit_region_generation(generator, world, region_id, sample_size)` samples generated descriptions and reports repetition, openings, endings, and score distribution.

## Usage

```python
from astergard.location_narrative.regional_knowledge import bank_for_region, audit_region_generation

bank = bank_for_region("Puszcza_Ciszy")
```

## Principles

- Use material reality first.
- Prefer condition-bound entries over synonym lists.
- Keep forbidden collocations explicit.
- Let the same term repeat if it is the correct technical term.
- Inspectable details should be backed by an examinable entry.
