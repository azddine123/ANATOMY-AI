# Asset licenses and attributions

Verified 2026-09-13. No proprietary competitor assets are included.

## Imported anatomical assets

**BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.**

Official license: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html (updated 2025-02-27).
License: https://creativecommons.org/licenses/by/4.0/
Official acquisition base: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/

Imported files: `isa_BP3D_4.0_obj_99.zip`, `isa_parts_list_e.txt`, `isa_inclusion_relation_list.txt`, `isa_element_parts.txt`. Exact URLs and SHA-256 are in `data/source/provenance.json`. A snapshot of the official license is in `data/source/license.html`. Each mesh stores a source OBJ hash; each delivered pack stores a GLB hash. Original large ZIP is deliberately excluded from Git, reproducible with `tools/fetch_sources.py`.

Distributed derivatives: `public/packs/*.glb`, `public/software/*.json`, `public/catalog.json`, and corresponding build outputs. Changes: normalization to Y-up metres; degenerate-face cleanup; computed normals; limited simplification; colors; organization into streamed packs; CPU fallback LOD; editorial translation overlay.

Commercial use and redistribution are permitted under this distribution's CC BY 4.0 notice. Attribution, license link, indication of modifications and no implied endorsement are required. No NC or ShareAlike condition is specified for the directly acquired archive distribution. The old Anatomography license page still refers to CC BY-SA 2.1 Japan; this mismatch is documented, not silently ignored. Do not replace these files with files from another mirror and assume the same distribution notice applies.

## Excluded resources

## Human Reference Atlas left ovary

Kristen Browne; Heidi Schlehlein (2022), **3D Reference Organ for Ovary, Female, Left v1.1**, HuBMAP. DOI: https://doi.org/10.48539/HBM499.JLMB.357. CC BY 4.0; commercial redistribution allowed with attribution and indication of changes. This separate reference organ is not anatomically registered to BodyParts3D. Source URL, checksum, official license snapshot and transformations: `data/curation/hra-ovary-provenance.json`. The preceding BodyParts3D attribution applies only to BodyParts3D derivatives, not this HRA mesh.

The M2 reference checklist is an original editorial matching aid, not an imported ontology. It contains no copied medical prose, no external ontology identifiers and no additional anatomical models. External terminology mapping remains pending.

## Resources not incorporated

Z-Anatomy was evaluated, not imported. Its blanket CC BY-SA 4.0 notice coexists with component acknowledgements including an inner ear under CC BY-NC-SA 4.0. `data/source/Z-Anatomy-License.txt` records the full notice; no models, images or code from that project are included. A component-level license map is required before inclusion.

Visible Human and independent FMA OWL exports were not imported. Independent FMA licensing remains unresolved; FMA IDs in this catalogue come from BodyParts3D tables only. OpenStax prose was excluded after current NC-SA notices were observed. No LLM/RAG corpus is distributed.

## UI and software dependencies

Three.js 0.180.0: MIT, https://github.com/mrdoob/three.js/blob/r180/LICENSE.
Lucide 0.468.0: ISC, https://github.com/lucide-icons/lucide/blob/main/LICENSE.
DM Sans: SIL Open Font License, https://github.com/google/fonts/blob/main/ofl/dmsans/OFL.txt.
Manrope: SIL Open Font License, https://github.com/google/fonts/blob/main/ofl/manrope/OFL.txt.
The font binaries are served locally. Vite is build tooling. No generated raster image is used to stand in for anatomy.

Settings exposes a Licenses & Attributions section. Retain it in every build and in native ports.

### 2026-09-13 nervous classification correction
`nervous-corrected-other-00.glb` and corresponding software pack are lossless repartitions of existing BodyParts3D-derived assets, not additional source content. Same CC BY 4.0 attribution; original OBJ hashes retained. Official license rechecked 2026-09-13. Three additional PART-OF metadata tables were acquired for audit only, with hashes in `data/source/partof-audit-provenance.json`. No Z-Anatomy assets or PART-OF meshes incorporated.
