import math
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ─────────────────── 箱・段・余り ＋ 計算式 ───────────────────
def describe_amount(remaining: int, target: int,
                    box_cap: int, levels: int) -> tuple[str, str]:
    """
    箱玉数が割り切れないとき:
        ・上段 (levels-1 段) は floor(box_cap/levels) 玉ずつ
        ・最下段だけ 余り分を加算して調整
    例: 箱1459/段5 → 上 4 段=291 玉, 下段=295 玉
    戻り値 (desc, calc)
    """
    base     = box_cap // levels            # 上段の玉数 (291)
    extra    = box_cap % levels             # 最下段に足す玉 (4)
    last_cap = base + extra                 # 最下段容量 (295)

    # ─── 箱数 ───
    boxes = remaining // box_cap
    after_boxes = remaining - boxes * box_cap

    # ─── 段数 (上段を優先的に埋める) ───
    levels_filled = min(after_boxes // base, levels - 1)
    rest = after_boxes - levels_filled * base

    # 最下段に突入
    if rest >= last_cap:
        levels_filled += 1
        rest -= last_cap

    desc = f"{boxes}箱 {levels_filled}段 余り{rest}玉"

    # 計算式の可読化
    calc = (f"({remaining + target}−{target})−{box_cap}×{boxes}"
            f" = {after_boxes} → {after_boxes}−{base}×{levels_filled}"
            f"{'−'+str(last_cap) if levels_filled==levels else ''}"
            f" = {rest}")

    return desc, calc


# ─────────────────── 1250 区切り一覧 ───────────────────
def breakpoints(hold: int, box_cap: int, levels: int) -> list[dict]:
    """
    1250 ずつ引き算し、残りが 0〜1249 になったところでストップ。
    各行に clip, desc, calc を持たせる。
    """
    res = []
    k = 1
    while True:
        target = 1250 * k
        if target > hold:
            break

        remaining = hold - target
        desc, calc = describe_amount(remaining, target, box_cap, levels)

        res.append({"clip": f"{target}#", "desc": desc, "calc": calc})

        if remaining < 1250:
            # 最終余り行
            res.append({"clip": "", "desc": f"余り {remaining} 玉", "calc": ""})
            break
        k += 1
    return res


# ─────────────────── Flask ルート ───────────────────
@app.route("/")
def index():
    return render_template("box.html", tab="box")


@app.route("/box", methods=["POST"])
def box_api():
    hold     = int(request.form["hold"])
    box_cap  = int(request.form["box_cap"])
    levels   = int(request.form["levels"])
    data = breakpoints(hold, box_cap, levels)
    return jsonify(data)


# ───────── （回転数計算ページは変わらないため割愛） ─────────
@app.route("/spin", methods=["GET", "POST"])
def spin():
    if request.method == "POST":
        base = int(request.form["base"])
        now  = int(request.form["now"])
        diff = now - base
        return jsonify({"diff": diff})
    return render_template("spin.html", tab="spin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
