from flask import Flask, request
import requests, time, json

app = Flask(__name__)


@app.route('/fund')
def fund():
    arr = []
    codes = request.args.get("codes")
    if codes is None:
        return {"code": 10002, "meesage": "codes is required", "data": arr}
    codes = codes.split("/")
    for msg in codes:
        msgs = msg.split("-")
        code = msgs[0]
        portion = msgs[1]
        try:
            arr.append(html(code, portion))
        except Exception as e:
            pass
    return {"code": 10001, "data": arr}


def html(code, portion):
    path = "http://fundgz.1234567.com.cn/js/{}.js?rt={}".format(code, int(time.time()))
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    try:
        rsp = requests.get(url=path, headers=headers, timeout=10)
        content = rsp.content.decode("utf8")
        content = content.replace("jsonpgz(", "")
        content = content.replace(");", "")
        final = json.loads(content)
        dwjz = final.get("dwjz")
        gz = final.get("gsz")
        income = (float(gz) - float(dwjz)) * float(portion)
        final["income"] = income
    except Exception as e:
        raise TypeError("no data")
    else:
        return final


if __name__ == '__main__':
    app.run()
