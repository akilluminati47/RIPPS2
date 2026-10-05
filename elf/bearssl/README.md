# BearSSL (bundled)

**BearSSL** 0.6 by Thomas Pornin, <https://bearssl.org/>, MIT licence (`LICENSE.txt` beside this file).

`bearssl-0.6.tar.gz` is the release as published (SHA-256
`6705bba1714961b41a728dfc5debbe348d2966c117649392f8c8139efc83ff14`). RIPPS2's `elf/build.sh` unpacks it
and compiles it for the EE as `lib/libbearssl.a`; it is the TLS behind **Settings > Network > Cover Art**,
which fetches covers from xlenore's ps2-covers on GitHub over HTTPS. The trust anchors are made by
`elf/art/make_trust_anchors.py` (public CA names and keys only).
