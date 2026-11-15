# Pre-Roman Britain and Wales: source investigation

The polity backbone leaves Britain and Wales sparse before Roman conquest. That is a dataset gap, not a claim that communities or rulers were absent. Bead `hynt-britain` now has an implemented point-evidence layer with 11 records; it adds no territorial polygons.

## Implemented selection

Enable **Britain & Wales evidence**, open **Explore Britain before conquest**, then choose **Explore Wales · 700 BCE** or browse the dated records. Global search also finds these records. Evidence type, date display and layer toggle are shareable in the URL.

The first selection includes Tinkinswood, the earlier henge at Bryn Celli Ddu, a regional hillfort-building overview, Llyn Fawr metalwork, an iron chariot tyre from Llyn Cerrig Bach, Cassivellaunus, Tasciovanus, Cunobelinus, Caratacus, and the Silures and Ordovices associations in the 51 CE episode. `pipeline/curated/britain.json` contains the original factual compilation and date/location explanations. Rebuild with `python -m pipeline.britain`.

**Recorded by this year** retains earlier evidence; it does not assert continued occupation or survival of a polity. **Dating overlaps this year** restricts markers to each cited interval. A broad interval may describe a period overview or object dating rather than activity at every year. Details explain the distinction.

Coordinates are approximate site vicinities or illustrative regional anchors. Community names and coin distributions do not become borders. Caratacus's disputed battlefield is represented by a broad association, with no proposed site chosen as definitive. No quantified confidence score is inferred.

The Cadw teaching pack gives conflicting entries for Pentre Ifan (Neolithic and c.2000 BCE). These are excluded pending reconciliation. Bryn Celli Ddu's date is explicitly labelled as the henge phase, not the later tomb. Ruler records use coin dating or dated episodes rather than invented reigns.

## Useful sources

- [Oxford Celtic Coin Index](https://cci.arch.ox.ac.uk/): coin records with named rulers and inscriptions. A [Cunobelinus record](https://cci.arch.ox.ac.uk/id/CCI-01.1141) includes a Tasciovanus legend. Findspots and mint attributions must be distinguished from territorial control. Verify record-level dating and coordinate reuse terms before importing.
- [British Museum coin record](https://www.britishmuseum.org/collection/object/C_R-12766): Cunobelin as ruler and Tasciovanus named in the inscription. The names are direct evidence; a precise kingdom boundary would be an additional interpretation.
- [University of Warwick: the Catuvellauni before Rome](https://warwick.ac.uk/fac/arts/classics/warwickclassicsnetwork/romancoventry/resources/interactions/rebellion/caratacus/): links coin evidence, rulers and Roman literary accounts. Useful for Cunobelinus and Tasciovanus; “before Rome” here primarily means before conquest, not before the Roman Empire existed.
- [Museum Wales: Iron Age Wales — Gods and War](https://museum.wales/media/50798/Iron-Age-Wales-Gods-and-War.pdf): Welsh communities, conflict and Roman accounts. Review the full document before extracting dated claims; search metadata is not enough for an import.
- [Coflein record 403831](https://coflein.gov.uk/en/sites/403831): discusses Caratacus, the Silures and Ordovices, and competing proposed locations for his defeat in 51 CE. Do not put a definitive battle marker on any one suggested site.
- [Cadw prehistoric resource](https://cadw.gov.wales/sites/default/files/2019-05/151214-prehistoricresource-eng.pdf): archaeological periods and places in Wales. Suitable starting point for a sites layer, with dates and actual site coordinates checked against individual records.

## Proposed representation

1. **Sites and material evidence:** hillforts, settlements, metalworking and coin findspots, each with occupation/manufacture/find dates distinguished. These can illuminate much earlier centuries than the named rulers.
2. **People and communities:** Silures, Ordovices and other attested groups, with dates of attestation and labelled regional associations. Roman authors' names are not automatic evidence of timeless, bounded tribes.
3. **Named rulers:** coin or textual attestations, linked to places and communities with explicit evidence. Reign dates, inferred dynasties and territorial reconstructions should carry separate sources.

Many familiar named rulers belong to the late Iron Age and conquest period. They cannot be projected back into the distant past to fill the map. Equally, absence of a named ruler or coin series must not erase archaeological evidence of settlement and complex society. Prefer points or visibly approximate regional associations until reliable dated geometry is available.

No catalogue images, bulk records or reconstructed boundaries have been copied. Original summaries and illustrative anchors are CC0; linked publications retain their own rights. This is a starting selection, not a complete catalogue of British prehistory.
