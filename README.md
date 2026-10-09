# Walk AI

A terminal fly-brain chatbot. Real FlyWire connections. Extremely fake English skills.

## Run on the Pi

Python 3.9 or newer. No pip packages, GPU or API key needed. First run downloads about 1.1 MB of encoded connectivity once; later runs work offline.

    wget -O install.sh https://raw.githubusercontent.com/Greenisus1/walk-ai/main/install.sh && sh install.sh

Try `banana`, `water`, `bitter`, `dusty antenna`, or `hello`.
Type `/trace` to see the winning output neuron and the actual neuron-ID path.
Type `/quit` to let the fly escape.

    python3 walk_ai.py --seed 7 --once banana --trace
    python3 walk_ai.py --info

The small Python loader downloads six real-connectome chunks, verifies their combined SHA256 and caches the compressed graph locally in `walk_ai_data/brain.zlib`. Later runs use that cache without internet. Run `python3 walk_ai.py` after installation. Delete the cached file only if you want to download it again. Keep the source comments and attribution when sharing it. The original `zivvle.py` is kept alongside `walk_ai.py` so the earlier version survives. Both names run the same real graph; `zivvle.py` is the old-name launcher.

## Size and testing

Bundled graph: **5,589 real neurons and 199,165 directed edges**. Compressed data is 884,966 bytes; the loader is about 9 KB plus six base85 text chunks totaling about 1.1 MB. No 3D imagery, raw synapse locations or full-brain model is downloaded by the author.

The app used about **66 MiB peak RAM** on the development Linux machine. Loading took about 0.26 seconds and replies about 2-12 milliseconds there. Those timings are **not Pi benchmarks**. An 8 GB Pi has ample headroom for this subset, but its exact timings are untested. Tests passed for sensory identity, original archive checksum, repeatability, no-output handling and actual edge-by-edge trace traversal. Run `python3 test_walk_ai.py` for the bundled tests.

The source TSV currently has 139,248 annotation rows versus the original published 139,255-neuron connectome. The builder joins exact IDs and drops unmatched annotation IDs. It never silently invents missing annotations.

## What is real

Every graph edge and its integer synapse count comes from the open FlyWire FAFB v783 proofread connectivity archive. Counts across neuropils are added before a 5-synapse threshold is applied. No edges, neurons or weights are invented. Neuron IDs and sensory/motor classifications come from the FlyWire annotation repository for the same materialization. The script embeds its source hashes, exact URLs, selection method and counts; `--info` shows them.

The subset starts with annotated sugar, water, bitter and grooming sensory neurons and 192 ID-spaced olfactory sensory neurons. Four forward expansion steps each add up to 1,500 previously unselected neurons ranked by summed synapses from the previous frontier. The final graph contains all qualifying real connections between retained neurons. This deliberately removes most of the brain and weak connections. Olfactory sampling is an engineering choice, not a validated biological sample.

## How the app works

1. Handwritten keywords map text to the corresponding annotated sensory pools. Unknown text becomes a generic olfactory stimulus. The fly does not parse sentences.
2. 768 packets per message perform up to 16 directed hops, choosing outgoing edges in proportion to their real synapse counts. A 7% per-hop chance loses activity. This is a nonnegative weighted random walk, not a physiological spiking simulator; neurotransmitter signs are not applied.
3. Packets reaching annotated motor/descending neurons stop and contribute to the readout. The strongest output wins, with 20% of the previous output activity retained between messages. Comic templates turn it into a reply. If no output is reached, the app says so rather than making one up.

The behavior labels are intentionally approximate: ingestion/crop motor neurons get eating jokes; proboscis/haustellum/salivary motor neurons get sipping jokes; antennal motor neurons get grooming jokes; left/right descending neurons get turn jokes. **These labels are not verified behavioral predictions. Soma laterality does not prove turning direction.** Other outputs get wandering jokes. The output neuron and real route are available in trace mode, so the interface never needs to pass the jokes off as science.

## What this is NOT

Not a talking biological fly, conscious entity, LLM, trained chatbot or validated brain emulation. No neural plasticity or learning. Random-walk mass is not firing rate. Synapse counts are not calibrated physiological strength. There is no body or ventral nerve cord, so walking, turning and grooming are comic readouts, not simulated physical movements. The original v783 synapses are older than the Princeton synapse update shown by current Codex. The updated annotation main branch can evolve separately; this release pins the exact downloaded annotation bytes by SHA256.

## Data sources and credit

- Dataset and CC BY 4.0 license: https://zenodo.org/records/10676866
- Connectivity Feather, 852,022,274 bytes: https://zenodo.org/api/records/10676866/files/proofread_connections_783.feather/content
- Full synapse Feather, 9,492,998,242 bytes, NOT needed: https://zenodo.org/api/records/10676866/files/flywire_synapses_783.feather/content
- Neuron TSV, 31,720,298 bytes at build time: https://raw.githubusercontent.com/flyconnectome/flywire_annotations/main/supplemental_files/Supplemental_file1_neuron_annotations.tsv
- Annotation repository: https://github.com/flyconnectome/flywire_annotations/tree/main
- Current Codex download guidance: https://codex.flywire.ai/faq

Credit Dorkenwald et al., *Neuronal wiring diagram of an adult brain*, Nature (2024), DOI 10.1038/s41586-024-07558-y; the FlyWire Consortium and FlyWire.ai. The archive combines Buhmann et al. synapse detection, Heinrich et al. cleft segmentation, Eckstein/Bates et al. neurotransmitter predictions, and FlyWire proofreading. Annotation credit: Schlegel et al., *Whole-brain annotation and multi-connectome cell typing of Drosophila*, Nature (2024), DOI 10.1038/s41586-024-07686-5, and contributors named by the annotation repository. This app changes the data by aggregating neuropils, thresholding and subsetting, as described above.

Relevant research, not a validation of this app: https://www.nature.com/articles/s41586-024-07763-9 describes a much more detailed connectome-based spiking model and its limitations.

## Rebuild (developer only, not on the Pi)

`build_subset.py` takes the downloaded Feather and TSV files plus an output `.zlib` path. It requires numpy and pyarrow, substantial RAM and the 852 MB source download. The delivered app does not require those dependencies. `embed_data.py` supports building the original single-file variant. The GitHub release uses six base85 text chunks because the large-file web editor rejected the original embedded file.

    python3 build_subset.py connections.feather annotations.tsv flywire_subset.zlib
    python3 embed_data.py flywire_subset.zlib original_single_file.py

The source archive's expected MD5 is `f48f972d262323a102aed49af1396b8a`.

## Files

- `walk_ai.py`: main loader and chat app
- `zivvle.py`: earlier-name launcher
- `brain_1.b85` through `brain_6.b85`: compressed real graph, encoded in chunks
- `install.sh`: download-and-run helper
- `test_walk_ai.py`: source and real-path tests
- `build_subset.py`, `embed_data.py`: developer build sources
- `.gitignore`: keeps local cache and bytecode out of commits


## Version 1.1.0: world reactions

The original graph readout kept picking left/right descending neurons, so replies were repetitive and ignored danger. This version adds an explicitly handwritten world/reflex layer on top of the unchanged real graph. Water gets a sip, food gets eating, light gets cautious inspection, and heat/sun get shade. Directional obstacles get a dodge or retreat; hazards in four or more directions (or "all sides") get a trapped response, not a made-up safe route. Poison/bitter food overrides eating. These rules are comic engineering choices, not outputs proven by fly neuroscience.

Death persists: "you die" or "dead" stops graph activity and replies stay dead until `/revive`. It does not spontaneously turn or eat afterward. Negated "not dead" and "don't die" do not kill it. `/trace` separates the real graph suggestion from the handwritten world decision. It never invents a neuron path for the reflex, and a dead fly has no graph trace.

Known situations now have varied lines and avoid repeating the previous line for that behavior. Unknown text still uses generic olfactory stimulation and the comic graph readout. This is keyword parsing, not a language model: complicated negation, hypothetical scenes, distance, velocity and rich physics are not understood. A chosen dodge only assumes the unmentioned direction is clear; it is not a validated safe trajectory.

Data files and checksum are unchanged. The first-run download/offline cache flow is unchanged.

## Fullscreen Store launch

Version 1.1.1 adds a full-terminal interface when launched through the Store. Python 3 with curses and an interactive terminal are required. The original source remains available directly. Interactive output wraps and scrolls with PgUp/PgDn. Enter returns after completion. Arguments on `bash app-store.sh run` retain the original command-line path. No administrative/package/transfer action ran during validation. Linux terminal checks passed; physical Raspberry Pi and non-Linux systems are untested.
