"""Edit a posted RIPPS2 Test me message in place: the same payload make_test_embed builds, the banner and icon again,
plus the files to download. The webhook URL comes from RIPPS2_DISCORD_WEBHOOK and is never printed.
    python edit_test_post.py <message id> <build> <notes> <release> <out dir> FILE..."""
import json
import os
import sys
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_test_embed as m

msg, build, notes, release, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
extra = sys.argv[6:]
url = os.environ.get('RIPPS2_DISCORD_WEBHOOK', '')
if not url.startswith('https://discord.com/api/webhooks/'):
    sys.exit('RIPPS2_DISCORD_WEBHOOK is not set')
files = [os.path.join(out, 'test-me-%d.png' % build), os.path.join(out, 'ripps2-icon.png')] + extra
data = m.payload(build, notes, release)
data['attachments'] = [{'id': i, 'filename': os.path.basename(f)} for i, f in enumerate(files)]
b = uuid.uuid4().hex
parts = [('--%s\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n' % b).encode() +
         json.dumps(data).encode() + b'\r\n']
for i, f in enumerate(files):
    kind = 'image/png' if f.endswith('.png') else 'application/octet-stream'
    parts.append(('--%s\r\nContent-Disposition: form-data; name="files[%d]"; filename="%s"\r\nContent-Type: %s\r\n\r\n'
                  % (b, i, os.path.basename(f), kind)).encode() + open(f, 'rb').read() + b'\r\n')
parts.append(('--%s--\r\n' % b).encode())
req = urllib.request.Request('%s/messages/%s' % (url, msg), data=b''.join(parts), method='PATCH',
                             headers={'Content-Type': 'multipart/form-data; boundary=%s' % b, 'User-Agent': 'RIPPS2-test-post'})
try:
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode())
except urllib.error.HTTPError as e:
    sys.exit('HTTP %d: %s' % (e.code, e.read().decode()[:400]))
print('edited', res.get('id'), 'attachments:', ', '.join('%s (%d)' % (a['filename'], a['size']) for a in res.get('attachments', [])))
