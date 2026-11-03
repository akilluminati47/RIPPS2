"""A BIBLE release post for the BIBLE channel (the user, 11/03: "bible webhook for the release flow too - not a test me
banner just use the 1080i gif and somewhat of a full release post"): one card with the release's GIF as its picture,
what is new, how it was tested, where to get it and how to set it, and the release's files attached.

The webhook comes from RIPPS2_DISCORD_WEBHOOK_BIBLE (~/.ripps2/discord.env, local only): never write it to a file.

    python post_bible_release.py --notes notes/bible-<tag>.json --gif <gif> [--attach <file> ...] [--post]

The notes file holds the card: {"title", "url", "description", "fields": [[name, value], ...], "footer"}.
Without --post it only writes post-bible.json beside the notes, to read before posting.
"""
import argparse
import json
import os
import sys
import urllib.request
import uuid

COLOR = 0x2A6BD6  # BIBLE's sky blue


def payload(notes, gif):
    n = json.load(open(notes, encoding='utf-8'))
    card = {'title': n['title'], 'url': n['url'], 'description': n['description'], 'color': COLOR,
            'fields': [{'name': k, 'value': v, 'inline': False} for k, v in n['fields']],
            'image': {'url': 'attachment://' + os.path.basename(gif)}}
    if n.get('footer'):
        card['footer'] = {'text': n['footer']}
    for f in card['fields']:
        assert len(f['name']) <= 256 and len(f['value']) <= 1024, f['name']
    assert len(card['description']) <= 4096 and len(json.dumps(card)) < 6000
    text = json.dumps(card)
    assert '—' not in text, 'no em dashes'
    return {'content': n.get('content', ''), 'embeds': [card], 'allowed_mentions': {'parse': []}}


def post(data, files):
    url = os.environ.get('RIPPS2_DISCORD_WEBHOOK_BIBLE', '')
    if not url.startswith('https://discord.com/api/webhooks/'):
        sys.exit('RIPPS2_DISCORD_WEBHOOK_BIBLE is not set to a Discord webhook URL')
    boundary = uuid.uuid4().hex
    data = dict(data, attachments=[{'id': i, 'filename': os.path.basename(p)} for i, p in enumerate(files)])
    parts = [('--%s\r\nContent-Disposition: form-data; name="payload_json"\r\nContent-Type: application/json\r\n\r\n' % boundary).encode() +
             json.dumps(data).encode() + b'\r\n']
    for i, path in enumerate(files):
        kind = 'image/gif' if path.lower().endswith('.gif') else 'application/octet-stream'
        parts.append(('--%s\r\nContent-Disposition: form-data; name="files[%d]"; filename="%s"\r\nContent-Type: %s\r\n\r\n'
                      % (boundary, i, os.path.basename(path), kind)).encode() + open(path, 'rb').read() + b'\r\n')
    parts.append(('--%s--\r\n' % boundary).encode())
    req = urllib.request.Request(url + '?wait=true', data=b''.join(parts), method='POST',
                                 headers={'Content-Type': 'multipart/form-data; boundary=%s' % boundary, 'User-Agent': 'RIPPS2-release-post'})
    with urllib.request.urlopen(req) as r:
        msg = json.loads(r.read().decode())
    print('posted, message id', msg.get('id'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--notes', required=True)
    ap.add_argument('--gif', required=True)
    ap.add_argument('--attach', action='append', default=[])
    ap.add_argument('--post', action='store_true')
    a = ap.parse_args()
    data = payload(a.notes, a.gif)
    out = os.path.join(os.path.dirname(os.path.abspath(a.notes)), 'post-bible.json')
    json.dump(data, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('wrote', out, 'card about', len(json.dumps(data['embeds'][0])), 'of 6000 characters')
    if a.post:
        post(data, [a.gif] + a.attach)


if __name__ == '__main__':
    main()
