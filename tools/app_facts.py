#!/usr/bin/env python3
""""At a glance" facts box on every app page, in all six languages.

Price and data wording is hand-written below (keep it true to each app page and
the homepage transparency table). Minimum iOS, languages and age rating come
live from the App Store (UK) on every run, so re-run after a release:
    python3 tools/app_facts.py
The box sits right after the page's <nav class="app-nav"> and is replaced in
place on re-runs (between the app-facts comments).
"""
import html, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ["en", "de", "es", "fr", "ja", "zh"]
DIRS = {"en": "", "de": "de/", "es": "es/", "fr": "fr/", "ja": "ja/", "zh": "zh-CN/"}

LABELS = {
    "title":    ["At a glance", "Auf einen Blick", "De un vistazo", "En bref", "概要", "概览"],
    "price":    ["Price", "Preis", "Precio", "Prix", "価格", "价格"],
    "devices":  ["Devices", "Geräte", "Dispositivos", "Appareils", "対応デバイス", "支持设备"],
    "requires": ["Requires", "Voraussetzung", "Requisitos", "Configuration requise", "動作環境", "系统要求"],
    "langs":    ["Languages", "Sprachen", "Idiomas", "Langues", "対応言語", "语言"],
    "age":      ["Age rating", "Altersfreigabe", "Clasificación por edad", "Classification", "年齢制限", "年龄分级"],
    "account":  ["Account", "Konto", "Cuenta", "Compte", "アカウント", "账户"],
    "ads":      ["Ads", "Werbung", "Anuncios", "Publicité", "広告", "广告"],
    "data":     ["Your data", "Deine Daten", "Tus datos", "Vos données", "データ", "你的数据"],
    "status":   ["Status", "Status", "Estado", "Statut", "状況", "状态"],
}
VALUES = {
    "no_account": ["Not needed", "Nicht nötig", "No hace falta", "Pas nécessaire", "不要", "不需要"],
    "no_ads":     ["None", "Keine", "Ninguno", "Aucune", "なし", "无"],
    "requires":   ["iOS {v} or later", "iOS {v} oder neuer", "iOS {v} o posterior", "iOS {v} ou version ultérieure", "iOS {v} 以降", "iOS {v} 或更高版本"],
    "coming":     ["Coming soon to iPhone and iPad", "Bald für iPhone und iPad", "Próximamente para iPhone y iPad", "Bientôt sur iPhone et iPad", "iPhone・iPad 向けに近日公開", "即将登陆 iPhone 和 iPad"],
}
LANG_NAMES = {
    "EN": ["English", "Englisch", "inglés", "anglais", "英語", "英语"],
    "DE": ["German", "Deutsch", "alemán", "allemand", "ドイツ語", "德语"],
    "ES": ["Spanish", "Spanisch", "español", "espagnol", "スペイン語", "西班牙语"],
    "FR": ["French", "Französisch", "francés", "français", "フランス語", "法语"],
    "JA": ["Japanese", "Japanisch", "japonés", "japonais", "日本語", "日语"],
    "ZH": ["Chinese (Simplified)", "Chinesisch (vereinfacht)", "chino simplificado", "chinois simplifié", "中国語（簡体字）", "简体中文"],
    "HI": ["Hindi", "Hindi", "hindi", "hindi", "ヒンディー語", "印地语"],
    "RO": ["Romanian", "Rumänisch", "rumano", "roumain", "ルーマニア語", "罗马尼亚语"],
    "KO": ["Korean", "Koreanisch", "coreano", "coréen", "韓国語", "韩语"],
}
LANG_ORDER = ["EN", "DE", "ES", "FR", "JA", "ZH", "HI", "RO", "KO"]

PRICE = {
    "trial7": ["7-day free trial, then a one-time purchase", "7 Tage kostenlos testen, dann ein Einmalkauf", "7 días de prueba gratis y después un pago único", "Essai gratuit de 7 jours, puis un achat unique", "7日間の無料体験後、買い切り", "免费试用 7 天，之后一次性购买"],
    "freetier7": ["Free version; 7-day trial of everything, then a one-time purchase", "Kostenlose Version; alles 7 Tage testen, dann ein Einmalkauf", "Versión gratuita; 7 días para probarlo todo y después un pago único", "Version gratuite ; tout essayer 7 jours, puis un achat unique", "無料版あり。7日間すべて試せて、その後は買い切り", "提供免费版；全部功能试用 7 天，之后一次性购买"],
    "trial3": ["3-day free trial, then a one-time purchase", "3 Tage kostenlos testen, dann ein Einmalkauf", "3 días de prueba gratis y después un pago único", "Essai gratuit de 3 jours, puis un achat unique", "3日間の無料体験後、買い切り", "免费试用 3 天，之后一次性购买"],
    "tickview": ["7-day Pro trial, then a one-time purchase or a monthly subscription", "Pro 7 Tage testen, dann Einmalkauf oder Monatsabo", "7 días de prueba de Pro y después pago único o suscripción mensual", "Essai de Pro pendant 7 jours, puis achat unique ou abonnement mensuel", "Pro を7日間試用後、買い切りまたは月額サブスクリプション", "Pro 试用 7 天，之后一次性购买或按月订阅"],
    "oncegame": ["Free download; a one-time purchase unlocks the full game", "Kostenloser Download; ein Einmalkauf schaltet das ganze Spiel frei", "Descarga gratuita; un pago único desbloquea el juego completo", "Téléchargement gratuit ; un achat unique débloque le jeu complet", "無料ダウンロード。買い切りでゲーム全体を解放", "免费下载；一次性购买解锁完整游戏"],
    "once": ["One-time purchase, no subscription", "Einmalkauf, kein Abo", "Pago único, sin suscripción", "Achat unique, sans abonnement", "買い切り、サブスクリプションなし", "一次性购买，无订阅"],
    "pro_once": ["Free download; Pro is a one-time purchase", "Kostenloser Download; Pro ist ein Einmalkauf", "Descarga gratuita; Pro es un pago único", "Téléchargement gratuit ; Pro est un achat unique", "無料ダウンロード。Pro は買い切り", "免费下载；Pro 为一次性购买"],
    "family_once": ["Free download; one purchase unlocks everything for the whole family", "Kostenloser Download; ein Kauf schaltet alles für die ganze Familie frei", "Descarga gratuita; una sola compra lo desbloquea todo para toda la familia", "Téléchargement gratuit ; un seul achat débloque tout pour toute la famille", "無料ダウンロード。1回の購入で家族全員のすべてを解放", "免费下载；一次购买即可为全家解锁全部内容"],
    "f2p": ["Free to play; optional in-app purchases", "Kostenlos spielbar; optionale In-App-Käufe", "Gratis; compras opcionales dentro de la app", "Gratuit ; achats intégrés facultatifs", "基本プレイ無料。アプリ内課金は任意", "免费游玩；可选内购"],
    "f2p_earn": ["Free to play; everything can be earned by playing, with optional purchases", "Kostenlos spielbar; alles lässt sich erspielen, Käufe sind optional", "Gratis; todo se puede ganar jugando, con compras opcionales", "Gratuit ; tout se gagne en jouant, achats facultatifs", "基本プレイ無料。すべてプレイで入手でき、購入は任意", "免费游玩；一切都能通过游戏获得，购买为可选"],
    "photoguessr": ["Free, with nothing to buy", "Kostenlos, ohne Käufe", "Gratis, sin nada que comprar", "Gratuit, rien à acheter", "無料、購入要素なし", "免费，无任何购买项目"],
    "mittenly": ["40 levels and a daily puzzle free; a one-time purchase unlocks endless levels", "40 Level und ein tägliches Rätsel gratis; ein Einmalkauf schaltet endlose Level frei", "40 niveles y un puzle diario gratis; un pago único desbloquea niveles infinitos", "40 niveaux et un puzzle quotidien gratuits ; un achat unique débloque des niveaux à l'infini", "40レベルとデイリーパズルは無料。買い切りでレベル無制限", "40 关和每日谜题免费；一次性购买解锁无限关卡"],
    "hollowstead": ["Chapter 1 free; a one-time purchase unlocks the full game", "Kapitel 1 gratis; ein Einmalkauf schaltet das ganze Spiel frei", "Capítulo 1 gratis; un pago único desbloquea el juego completo", "Chapitre 1 gratuit ; un achat unique débloque le jeu complet", "第1章は無料。買い切りでゲーム全体を解放", "第 1 章免费；一次性购买解锁完整游戏"],
    "holdout": ["Free demo; a one-time purchase unlocks the full game", "Kostenlose Demo; ein Einmalkauf schaltet das ganze Spiel frei", "Demo gratuita; un pago único desbloquea el juego completo", "Démo gratuite ; un achat unique débloque le jeu complet", "無料体験版あり。買い切りでゲーム全体を解放", "免费试玩；一次性购买解锁完整游戏"],
}
DATA = {
    "local": ["Stays on your device", "Bleiben auf deinem Gerät", "Se quedan en tu dispositivo", "Restent sur votre appareil", "端末内に保存", "保存在你的设备上"],
    "tickview": ["Stays on your device; the app fetches public market data", "Bleiben auf deinem Gerät; die App lädt öffentliche Marktdaten", "Se quedan en tu dispositivo; la app descarga datos de mercado públicos", "Restent sur votre appareil ; l'app récupère des données de marché publiques", "端末内に保存。公開市場データのみ取得", "保存在你的设备上；应用只获取公开市场数据"],
    "custoda": ["Stays on your device; barcode lookups send only the barcode number", "Bleiben auf deinem Gerät; bei Barcode-Abfragen wird nur die Nummer gesendet", "Se quedan en tu dispositivo; al buscar un código solo se envía el número", "Restent sur votre appareil ; la recherche d'un code-barres n'envoie que son numéro", "端末内に保存。バーコード検索で送るのは番号のみ", "保存在你的设备上；查询条形码只发送条码号"],
    "photoflight": ["Travel history stays on your device", "Der Reiseverlauf bleibt auf deinem Gerät", "Tu historial de viajes se queda en tu dispositivo", "L'historique de voyage reste sur votre appareil", "旅行履歴は端末内に保存", "旅行记录保存在你的设备上"],
    "pacegrid": ["Workouts stay on your device", "Trainings bleiben auf deinem Gerät", "Tus entrenamientos se quedan en tu dispositivo", "Les entraînements restent sur votre appareil", "ワークアウトは端末内に保存", "运动记录保存在你的设备上"],
    "cloudmesh": ["Approximate location is used for forecasts and rain alerts", "Für Vorhersagen und Regenwarnungen wird der ungefähre Standort genutzt", "Se usa la ubicación aproximada para pronósticos y avisos de lluvia", "La position approximative sert aux prévisions et alertes pluie", "予報と雨アラートにおおよその位置情報を使用", "预报和降雨提醒使用大致位置"],
}

# slug: (store id or None, price key, data key, devices)
APPS = {
    "kanesh": ("6760582379", "tickview", "tickview", ["iPhone", "iPad"]),
    "cognithix": ("6760035436", "trial7", "local", ["iPhone", "iPad"]),
    "arithmetix": ("6759711397", "trial7", "local", ["iPhone", "iPad"]),
    "sparks-studios": ("6760515470", "family_once", "local", ["iPhone", "iPad"]),
    "photoflight": ("6761143528", "pro_once", "photoflight", ["iPhone", "iPad"]),
    "cyla": ("6760896784", "freetier7", "local", ["iPhone", "iPad"]),
    "cloudmesh": ("6760612651", "freetier7", "cloudmesh", ["iPhone", "iPad", "Mac", "Apple Watch"]),
    "pacegrid": ("6760843225", "freetier7", "pacegrid", ["iPhone", "iPad", "Apple Watch"]),
    "minua": ("6760611967", "once", "local", ["iPhone", "iPad"]),
    "bellgrave": ("6761905396", "oncegame", "local", ["iPhone", "iPad", "Mac"]),
    "cardbash": ("6775067276", "f2p", "local", ["iPhone", "iPad"]),
    "custoda": ("6787263003", "freetier7", "custoda", ["iPhone"]),
    "mergebash": ("6776048979", "f2p", "local", ["iPhone", "iPad"]),
    "keystrike": ("6763947075", "trial3", "local", ["iPhone", "iPad", "Mac"]),
    "penlicence": ("6761393693", "trial7", "local", ["iPhone", "iPad"]),
    "farewars": ("6815887660", "f2p_earn", "local", ["iPhone", "iPad"]),
    "robotrooftoprun": ("6811426255", "f2p", "local", ["iPhone", "iPad"]),
    "monsoonrush": (None, "f2p_earn", "local", ["iPhone", "iPad"]),
    "photoguessr": (None, "photoguessr", "local", ["iPhone", "iPad"]),
    "mittenly": (None, "mittenly", "local", ["iPhone", "iPad"]),
    "hollowstead": (None, "hollowstead", "local", ["iPhone", "iPad"]),
    "seriousbellgrave": (None, "holdout", "local", ["iPhone", "iPad"]),
}
START, END = "<!-- app-facts -->", "<!-- /app-facts -->"


def store_facts():
    ids = ",".join(v[0] for v in APPS.values() if v[0])
    req = urllib.request.Request(f"https://itunes.apple.com/lookup?id={ids}&country=gb",
                                 headers={"User-Agent": "bfgapps-facts/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return {str(x["trackId"]): x for x in json.load(r)["results"]}


def box(slug, i, store):
    sid, price, data, devices = APPS[slug]
    sep = "、" if LANGS[i] in ("ja", "zh") else ", "
    rows = []
    if not sid:
        rows.append(("status", VALUES["coming"][i]))
    rows.append(("price", PRICE[price][i]))
    rows.append(("devices", sep.join(devices)))
    if sid:
        s = store[sid]
        rows.append(("requires", VALUES["requires"][i].format(v=s["minimumOsVersion"])))
        codes = [c for c in LANG_ORDER if c in s.get("languageCodesISO2A", [])]
        if codes:
            rows.append(("langs", sep.join(LANG_NAMES[c][i] for c in codes)))
        rows.append(("age", s["contentAdvisoryRating"]))
    rows += [("account", VALUES["no_account"][i]), ("ads", VALUES["no_ads"][i]), ("data", DATA[data][i])]
    items = "".join(f"<div><dt>{LABELS[k][i]}</dt><dd>{html.escape(v)}</dd></div>" for k, v in rows)
    return (f'{START}<section class="app-facts" aria-labelledby="app-facts-title">'
            f'<h2 id="app-facts-title" class="app-facts-title">{LABELS["title"][i]}</h2>'
            f'<dl class="app-facts-grid">{items}</dl></section>{END}')


def main():
    store = store_facts()
    n = 0
    for slug in APPS:
        for i, lang in enumerate(LANGS):
            path = os.path.join(ROOT, DIRS[lang], "apps", slug, "index.html")
            if not os.path.exists(path):
                continue
            s = open(path, encoding="utf-8").read()
            new_box = box(slug, i, store)
            if START in s:
                new = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda m: new_box, s, flags=re.S)
            else:
                m = re.search(r'<nav class="app-nav">.*?</nav>', s, re.S)
                if not m:
                    print("no app-nav:", path)
                    continue
                pre = s[:m.start()]
                indent = pre[pre.rfind("\n") + 1:] if pre.rfind("\n") >= 0 else ""
                indent = indent if indent.strip() == "" else ""
                new = s[:m.end()] + ("\n\n" + indent if indent else "") + new_box + s[m.end():]
            if new != s:
                open(path, "w", encoding="utf-8").write(new)
                n += 1
    print("updated", n, "pages")


if __name__ == "__main__":
    main()
