#!/usr/bin/env python3
"""Zivvle: real FlyWire wiring, deliberately unserious chat interface. Python 3.9+."""
import argparse
import base64
import bisect
import collections
import json
import random
import re
import zlib
from pathlib import Path

# Data attribution: FlyWire Consortium / Dorkenwald et al. (Nature 2024),
# doi:10.1038/s41586-024-07558-y; Schlegel et al., doi:10.1038/s41586-024-07686-5.
# Buhmann synapse detection, Heinrich clefts, Eckstein/Bates NT predictions.
# Dataset license: CC BY 4.0, https://zenodo.org/records/10676866
# Annotations: https://github.com/flyconnectome/flywire_annotations/tree/main
# Modified by summing neuropils, retaining edges >=5 synapses, and sensory-rooted subsetting.
# This is a comic random-walk interface, not a validated brain/behavior model.
# The release builder embeds the compressed, attributed real-data subset here.
from walk_ai import main

if __name__ == '__main__':
    main()
