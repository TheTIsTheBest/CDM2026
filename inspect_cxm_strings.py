import urllib.request
url='https://play.fifa.com/components/main.bundle.js'
req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=20) as r:
    data=r.read().decode('utf-8', errors='replace')
for i in range(0, len(data)):
    idx = data.find('fifaplusweb/api', i)
    if idx == -1:
        break
    print(data[max(0, idx-120):idx+160])
    i = idx + 1
