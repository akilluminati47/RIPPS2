"""Makes RIPPS2's TLS trust anchors (include/ripps2art_ta.h in the RiptOPL tree) for the cover art
download: BearSSL br_x509_trust_anchor entries for the root CAs GitHub's content host
(raw.githubusercontent.com) has been seen to chain to, so a change of CA does not break downloads.

    python elf/art/make_trust_anchors.py <cacert.pem> <out.h>

cacert.pem is any Mozilla-derived bundle (certifi's works). Only the public parts of each root go in:
its subject name and public key, as BearSSL wants them (what `brssl ta` prints). Nothing secret.
"""
import base64
import re
import sys

ROOTS = [
    'ISRG Root X1',                             # Let's Encrypt (the chain served in October 2026)
    'ISRG Root X2',                             # Let's Encrypt, ECDSA
    'DigiCert Global Root G2',                  # GitHub's earlier certificates
    'DigiCert Global Root CA',
    'USERTrust RSA Certification Authority',    # Sectigo, also used by GitHub
    'USERTrust ECC Certification Authority',
    'GlobalSign Root R46',
]

CURVES = {  # named curve OIDs -> BearSSL curve ids
    '1.2.840.10045.3.1.7': 23,  # secp256r1
    '1.3.132.0.34': 24,         # secp384r1
    '1.3.132.0.35': 25,         # secp521r1
}


def der(b, i):
    """One DER element at b[i]: (tag, start of contents, end of contents)."""
    tag = b[i]
    n = b[i + 1]
    j = i + 2
    if n & 0x80:
        k = n & 0x7F
        n = int.from_bytes(b[j:j + k], 'big')
        j += k
    return tag, j, j + n


def children(b, start, end):
    out, i = [], start
    while i < end:
        t, s, e = der(b, i)
        out.append((t, i, s, e))
        i = e
    return out


def oid(b):
    first = b[0]
    parts = [first // 40, first % 40]
    v = 0
    for c in b[1:]:
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            parts.append(v)
            v = 0
    return '.'.join(map(str, parts))


def anchor(cert):
    _, s, e = der(cert, 0)                         # Certificate
    tbs = children(cert, s, e)[0]                   # tbsCertificate
    f = children(cert, tbs[2], tbs[3])
    k = 1 if f[0][0] == 0xA0 else 0                 # [0] version present?
    subject = f[k + 4]                              # serial, sigalg, issuer, validity, subject
    spki = f[k + 5]
    dn = cert[subject[1]:subject[3]]                # the whole encoded Name
    alg, key = children(cert, spki[2], spki[3])
    algf = children(cert, alg[2], alg[3])
    algo = oid(cert[algf[0][2]:algf[0][3]])
    bits = cert[key[2] + 1:key[3]]                  # the BIT STRING, past its unused-bits byte
    if algo == '1.2.840.113549.1.1.1':              # RSA: SEQUENCE { n, e }
        _, s2, e2 = der(bits, 0)
        n_, e_ = children(bits, s2, e2)
        n = bits[n_[2]:n_[3]].lstrip(b'\x00')
        ex = bits[e_[2]:e_[3]].lstrip(b'\x00')
        return dn, ('rsa', n, ex)
    if algo == '1.2.840.10045.2.1':                 # EC: the curve in the parameters, the point
        curve = CURVES[oid(cert[algf[1][2]:algf[1][3]])]
        return dn, ('ec', curve, bits)
    raise ValueError('unsupported key ' + algo)


def carray(name, data):
    rows = [', '.join('0x%02X' % x for x in data[i:i + 12]) for i in range(0, len(data), 12)]
    return 'static const unsigned char %s[] = {\n    %s\n};\n' % (name, ',\n    '.join(rows))


def main():
    pem, out = sys.argv[1], sys.argv[2]
    text = open(pem, encoding='utf-8').read()
    blocks = re.findall(r'# Label: "([^"]+)"\n.*?-----BEGIN CERTIFICATE-----\n(.*?)-----END CERTIFICATE-----', text, re.S)
    certs = {label: base64.b64decode(''.join(body.split())) for label, body in blocks}
    lines = ['/* RIPPS2 build 73: the cover art download\'s TLS trust anchors, made by ps2-pillars',
             '   elf/art/make_trust_anchors.py from a Mozilla CA bundle. Public names and keys only. */',
             '#ifndef __RIPPS2ART_TA_H', '#define __RIPPS2ART_TA_H', '', '#include <bearssl.h>', '']
    entries = []
    for i, label in enumerate(ROOTS):
        if label not in certs:
            print('missing root', label)
            sys.exit(1)
        dn, key = anchor(certs[label])
        lines.append('/* %s */' % label)
        lines.append(carray('TA%d_DN' % i, dn))
        if key[0] == 'rsa':
            lines.append(carray('TA%d_RSA_N' % i, key[1]))
            lines.append(carray('TA%d_RSA_E' % i, key[2]))
            entries.append('    {{(unsigned char *)TA%d_DN, sizeof TA%d_DN}, BR_X509_TA_CA, {BR_KEYTYPE_RSA, {.rsa = {(unsigned char *)TA%d_RSA_N, sizeof TA%d_RSA_N, (unsigned char *)TA%d_RSA_E, sizeof TA%d_RSA_E}}}},' % ((i,) * 6))
        else:
            lines.append(carray('TA%d_EC_Q' % i, key[2]))
            entries.append('    {{(unsigned char *)TA%d_DN, sizeof TA%d_DN}, BR_X509_TA_CA, {BR_KEYTYPE_EC, {.ec = {%d, (unsigned char *)TA%d_EC_Q, sizeof TA%d_EC_Q}}}},' % (i, i, key[1], i, i))
    lines.append('static const br_x509_trust_anchor RIPPS2_TAS[] = {')
    lines += entries
    lines.append('};')
    lines.append('#define RIPPS2_TAS_NUM %d' % len(ROOTS))
    lines.append('')
    lines.append('#endif')
    open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('wrote', out, len(ROOTS), 'anchors')


if __name__ == '__main__':
    main()
