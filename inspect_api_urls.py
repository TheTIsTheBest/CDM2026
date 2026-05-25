import urllib.request

url = 'https://play.fifa.com/components/main.bundle.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=20) as r:
    data = r.read().decode('utf-8', errors='replace')

seen = []
for p in data.split('https://'):
    if 'cxm-api.fifa.com' in p or 'api.fifa.com' in p:
        u = p.split('"', 1)[0].split("'", 1)[0]
        if u not in seen:
            seen.append(u)

print('\n'.join(seen[:50]))
