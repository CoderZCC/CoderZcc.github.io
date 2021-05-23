from flask import Flask, request
import requests, time, json
from lxml import etree

app = Flask(__name__)

gl_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}
gl_cache = None


@app.route('/fund')
def fund():
    arr = []
    codes = request.args.get("codes")
    if codes is None:
        return {"code": 10002, "meesage": "codes is required", "data": arr}
    global gl_cache
    codes = codes.split("/")
    for msg in codes:
        msgs = msg.split("-")
        code = msgs[0]
        portion = msgs[1]
        try:
            new = gz_html(code, portion)
            cache = cache_dict(new.get("fundcode"))
            if cache.get("gztime", "0") > new.get("gztime"):
                new = cache
            arr.append(new)
        except Exception as e:
            pass
    gl_cache = arr
    return {"code": 10001, "data": arr}


def gz_html(code, portion):
    path = "http://fundgz.1234567.com.cn/js/{}.js?rt={}".format(code, int(time.time()))
    try:
        rsp = requests.get(url=path, headers=gl_headers, timeout=10)
        content = rsp.content.decode("utf8")
        content = content.replace("jsonpgz(", "")
        content = content.replace(");", "")
        final = json.loads(content)
        dwjz = final.get("dwjz")
        gz = final.get("gsz")
        income = (float(gz) - float(dwjz)) * float(portion)
        final["income"] = income
        final["portion"] = portion
    except Exception as e:
        raise TypeError("no data")
    else:
        return final


@app.route('/dwjz')
def dwjz():
    arr = []
    codes = request.args.get("codes")
    if codes is None:
        return {"code": 10002, "meesage": "codes is required", "data": arr}
    page = int(request.args.get("page", "1"))
    limit = int(request.args.get("limit", "1"))
    codes = codes.split("/")
    for msg in codes:
        msgs = msg.split("-")
        code = msgs[0]
        portion = msgs[1]
        try:
            arr.append(dwjz_html(code, page, limit, portion))
        except Exception as e:
            pass
    return {"code": 10001, "page": page, "limit": limit, "data": arr}


def dwjz_html(code, page, limit, portion):
    cache = cache_dict(code)
    final = {
        "fundcode": code,
        "portion": portion,
        "name": cache.get("name")
    }
    path = "https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code={}&page={}&per={}".format(code, page, limit)
    try:
        rsp = requests.get(url=path, headers=gl_headers, timeout=10)
        content = rsp.content.decode("utf8")
        html = etree.HTML(content)
        trs = html.xpath(".//tbody/tr")
        items = []
        for tr in trs:
            td = tr.xpath("./td/text()")
            jzrq = td[0]
            dwjz = td[1]
            dwjzzf = td[3]
            items.append({
                "jzrq": jzrq,
                "dwjz": float(dwjz),
                "dwjzzf": dwjzzf
            })
            final["item"] = items
    except Exception as e:
        raise TypeError("no data")
    else:
        return final


def cache_dict(code):
    global gl_cache
    if gl_cache is not None:
        for dict in gl_cache:
            if dict.get("fundcode") == code:
                return dict
    return {}


if __name__ == '__main__':
    app.run()
