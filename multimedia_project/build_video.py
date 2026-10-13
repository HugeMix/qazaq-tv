#!/usr/bin/env python3
"""Сборка мультимедийного проекта «Безопасность в Интернете» (MP4).
Этапы:  python3 build.py tts | preview | render
"""
import os, sys, json, math, random, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 25
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
OUT_DIR = "/home/user/qazaq-tv/multimedia_project"
AUTHOR = "Фамилия Имя"
GROUP = "Группа ___"
OUT_NAME = "Группа_Фамилия_Мультимедийный_проект.mp4"
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------- цвета / шрифты
CY = (34, 211, 238); BL = (59, 130, 246); GR = (52, 211, 153)
RD = (248, 113, 113); AM = (251, 191, 36); WH = (240, 246, 255)
DK = (14, 28, 58); MUTED = (159, 176, 208); CARD = (22, 40, 78)
BGC = (13, 25, 52)

_fc = {}
def F(size, bold=False):
    k = (size, bold)
    if k not in _fc:
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
        _fc[k] = ImageFont.truetype(p, size)
    return _fc[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eback(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def mix(a, b, k): return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

# ---------------------------------------------------------------- контент
# (озвучка, подпись или None)
SC = [
 dict(kind="title", title="Безопасность в Интернете", sents=[
   ("Здравствуйте! Тема моего проекта, безопасность в Интернете.", None),
   ("Мы каждый день учимся, общаемся и платим онлайн, поэтому важно уметь защищать себя и свои данные.", None)]),
 dict(kind="bullets", title="Введение и цель", tag="ВВЕДЕНИЕ", sprite="laptop",
  sents=[("Интернет даёт нам огромные возможности, но вместе с ними приходят и риски.", None),
         ("Цель проекта, научиться распознавать основные угрозы и применять простые правила защиты.", None),
         ("Для этого мы разберём шесть тем: от фишинга и паролей до безопасного общения в сети.", None)],
  bullets=[("Интернет: возможности и риски", 0), ("Цель: распознавать угрозы и защищаться", 1),
           ("6 тем: от фишинга до общения в сети", 2)]),
 dict(kind="threats", title="Основные угрозы", tag="ТЕМА 1 из 6",
  sents=[("Начнём с главных угроз.", None),
         ("Вредоносные программы, вирусы, шпионы и шифровальщики, крадут данные или блокируют устройство.", None),
         ("Фишинг, это обман, при котором преступники выманивают пароли через поддельные письма и сайты.", None),
         ("Мошенники также звонят, пишут в мессенджерах и создают фальшивые интернет-магазины.", None),
         ("Наконец, данные могут утечь из-за взлома сервисов, поэтому защита нужна на каждом уровне.", None)],
  cards=[("bug", "Вредоносные программы", "Вирусы, шпионы, шифровальщики", 1),
         ("hook", "Фишинг", "Поддельные письма и сайты", 2),
         ("phone", "Онлайн-мошенничество", "Звонки, чаты, фальшивые магазины", 3),
         ("db", "Утечки данных", "Взлом сервисов и баз данных", 4)]),
 dict(kind="bullets", title="Фишинг: обман в сети", tag="ТЕМА 2 из 6", sprite="hook",
  sents=[("Фишинг, самая массовая угроза для обычного пользователя.", None),
         ("Сообщение выдаёт себя за банк, магазин или соцсеть и торопит вас что-то сделать.", None),
         ("Чаще всего просят перейти по ссылке, ввести пароль или код из эс-эм-эс.", "Чаще всего просят перейти по ссылке, ввести пароль или код из СМС."),
         ("Главное правило: настоящие сервисы никогда не просят сообщить пароль или код подтверждения.", None)],
  bullets=[("Маскировка под банк, магазин, соцсеть", 1), ("Срочность и угрозы блокировки", 1),
           ("Просьба ввести пароль или код из СМС", 2), ("Правило: пароль и код — никому!", 3, "good")]),
 dict(kind="video", title="Видео: как распознать фишинг", tag="ТЕМА 2 из 6 · ВИДЕО",
  sents=[("Посмотрите короткий ролик: как распознать фишинговое письмо.", None),
         ("Во-первых, смотрим на адрес отправителя: он не совпадает с настоящим сайтом сервиса.", None),
         ("Во-вторых, письмо давит срочностью: аккаунт якобы заблокируют уже через час.", None),
         ("В-третьих, ссылка ведёт на странный домен. Не нажимайте на неё!", None),
         ("Если сомневаетесь, откройте сайт сами или позвоните в поддержку.", None)]),
 dict(kind="pass", title="Надёжные пароли", tag="ТЕМА 3 из 6",
  sents=[("Пароль, ключ от вашего аккаунта.", None),
         ("Надёжный пароль длинный: лучше от двенадцати символов, например, фраза из нескольких слов.", None),
         ("Не используйте один пароль на разных сайтах и не берите даты рождения или один, два, три, четыре, пять, шесть.",
          "Не используйте один пароль на разных сайтах и не берите даты рождения или «123456»."),
         ("Включите двухфакторную аутентификацию: даже если пароль украдут, без второго подтверждения войти не получится.", None)],
  bullets=[("Длина — от 12 символов", 1), ("Свой пароль для каждого сайта", 2),
           ("Двухфакторная аутентификация", 3, "good")], cw=570),
 dict(kind="bullets", title="Защита устройств и сетей", tag="ТЕМА 4 из 6", sprite="laptop", sprite2=("wifi", 3),
  sents=[("Защита устройств начинается с обновлений.", None),
         ("Устанавливайте обновления системы и приложений, они закрывают найденные уязвимости.", None),
         ("Используйте антивирус и скачивайте программы только из официальных магазинов.", None),
         ("В открытых сетях вай-фай не вводите пароли и банковские данные.", "В открытых сетях Wi-Fi не вводите пароли и банковские данные.")],
  bullets=[("Обновления системы и приложений", 1), ("Антивирус и официальные магазины", 2),
           ("Осторожно с публичным Wi-Fi", 3)]),
 dict(kind="bullets", title="Личные данные и соцсети", tag="ТЕМА 5 из 6", sprite="profile",
  sents=[("Личные данные, ценность, которую нужно беречь.", None),
         ("Не публикуйте в соцсетях адрес, номера документов и фотографии банковских карт.", None),
         ("Настройте приватность профиля и принимайте в друзья только тех, кого знаете.", None),
         ("Помните: то, что попало в Интернет, может остаться там навсегда.", None)],
  bullets=[("Не публикуйте адрес, документы, карты", 1), ("Закрытый профиль, друзья — только знакомые", 2),
           ("Интернет помнит всё", 3)]),
 dict(kind="bullets", title="Культура общения в сети", tag="ТЕМА 6 из 6", sprite="chat",
  sents=[("Безопасность, это ещё и культура общения.", None),
         ("Не отвечайте на оскорбления и не распространяйте чужие личные фотографии.", None),
         ("Если вас травят в сети, сохраните доказательства, заблокируйте обидчика и расскажите взрослым.", None),
         ("Критически относитесь к новостям и проверяйте источники.", None)],
  bullets=[("Уважение к другим, без оскорблений", 1), ("Травля: доказательства → блок → взрослым", 2),
           ("Проверяйте источники информации", 3)]),
 dict(kind="bullets", title="Выводы", tag="ИТОГИ", sprite="shield",
  sents=[("Подведём итоги.", None),
         ("Главные угрозы, вредоносные программы, фишинг, мошенничество и утечки данных.", None),
         ("Защитят вас надёжные уникальные пароли, двухфакторная аутентификация и обновления.", None),
         ("А главное, внимательность: не торопитесь, проверяйте и не делитесь лишним.", None),
         ("Спасибо за внимание!", None)],
  bullets=[("Угрозы: вирусы, фишинг, мошенничество, утечки", 1), ("Защита: пароли, 2FA, обновления", 2),
           ("Главное: внимательность и проверка", 3), ("Спасибо за внимание!", 4, "good")]),
 dict(kind="bullets", title="Список источников", tag="ИСТОЧНИКИ", sprite=None, cw=1140, sp=88, y0=150,
  sents=[("Использованные источники.", None),
         ("Материалы «Лаборатории Касперского», Роскомнадзора, Google, Лиги безопасного Интернета и рекомендации института нист.",
          "Материалы «Лаборатории Касперского», Роскомнадзора, Google, Лиги безопасного Интернета и рекомендации NIST.")],
  bullets=[("«Лаборатория Касперского»: фишинг и защита||www.kaspersky.ru", 1),
           ("Роскомнадзор: защита персональных данных||pd.rkn.gov.ru", 1),
           ("Google Safety Center: безопасность в Интернете||safety.google", 1),
           ("NIST SP 800-63B: рекомендации по паролям||pages.nist.gov/800-63-3", 1),
           ("Лига безопасного Интернета||ligainternet.ru", 1)]),
]

LEAD, TAIL, GAP, TR = 0.8, 0.8, 0.3, 0.7

# ---------------------------------------------------------------- тайминги
def load_timing():
    p = os.path.join(WORK, "timing.json")
    if os.path.exists(p):
        return json.load(open(p))
    return None
TM = load_timing()

# ---------------------------------------------------------------- спрайты
class Cv:
    def __init__(s, n=220, ss=4):
        s.n, s.ss, s.S = n, ss, n * ss
        s.im = Image.new("RGBA", (s.S, s.S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def p(s, v): return v * s.S / 100
    def pts(s, l): return [(s.p(x), s.p(y)) for x, y in l]
    def poly(s, l, fill): s.d.polygon(s.pts(l), fill=fill)
    def rect(s, x0, y0, x1, y1, fill, r=0, ol=None, w=0):
        kw = dict(outline=ol, width=int(s.p(w))) if ol else {}
        s.d.rounded_rectangle([s.p(x0), s.p(y0), s.p(x1), s.p(y1)], radius=s.p(r), fill=fill, **kw)
    def ell(s, x0, y0, x1, y1, fill): s.d.ellipse([s.p(x0), s.p(y0), s.p(x1), s.p(y1)], fill=fill)
    def line(s, l, fill, w): s.d.line(s.pts(l), fill=fill, width=int(s.p(w)), joint="curve")
    def arc(s, x0, y0, x1, y1, a0, a1, fill, w): s.d.arc([s.p(x0), s.p(y0), s.p(x1), s.p(y1)], a0, a1, fill=fill, width=int(s.p(w)))
    def done(s): return s.im.resize((s.n, s.n), Image.LANCZOS)

def scale_pts(l, k, c=(50, 50)):
    return [(c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k) for x, y in l]

SHIELD = [(50, 4), (89, 17), (89, 50), (50, 96), (11, 50), (11, 17)]
def sp_shield():
    c = Cv(); c.poly(SHIELD, CY); c.poly(scale_pts(SHIELD, .86), BL)
    c.rect(35, 46, 65, 74, WH, 5); c.arc(39, 26, 61, 56, 180, 360, WH, 5.5)
    c.ell(46.5, 54, 53.5, 61, DK); c.rect(48.6, 58, 51.4, 68, DK, 1); return c.done()
def sp_bug():
    c = Cv()
    for y in (50, 61, 72):
        c.line([(34, y), (16, y - 8)], (190, 70, 70), 4); c.line([(66, y), (84, y - 8)], (190, 70, 70), 4)
    c.line([(45, 30), (36, 12)], (190, 70, 70), 3.5); c.line([(55, 30), (64, 12)], (190, 70, 70), 3.5)
    c.ell(33, 36, 67, 86, RD); c.ell(39, 22, 61, 44, (200, 60, 60)); c.line([(50, 42), (50, 84)], (150, 40, 40), 3)
    c.ell(43, 28, 48, 33, WH); c.ell(52, 28, 57, 33, WH); c.ell(40, 52, 46, 58, (150, 40, 40)); c.ell(54, 66, 60, 72, (150, 40, 40))
    return c.done()
def sp_hook():
    c = Cv()
    c.rect(6, 10, 94, 60, WH, 6); c.line([(8, 13), (50, 40), (92, 13)], (140, 160, 205), 3)
    c.line([(8, 58), (38, 34)], (190, 205, 235), 2.5); c.line([(92, 58), (62, 34)], (190, 205, 235), 2.5)
    c.line([(72, 54), (72, 74)], AM, 4.5); c.arc(58, 64, 86, 92, 0, 180, AM, 4.5)
    c.line([(58, 78), (63, 70)], AM, 4.5); c.ell(66, 44, 78, 56, RD); return c.done()
def sp_phone():
    c = Cv(); c.rect(28, 4, 72, 96, (30, 41, 70), 9, CY, 2.2); c.rect(33, 14, 67, 82, (15, 30, 60), 3)
    c.poly([(50, 26), (64, 56), (36, 56)], AM); c.line([(50, 36), (50, 46)], DK, 3.2); c.ell(48.4, 49.3, 51.6, 52.5, DK)
    c.rect(40, 62, 60, 70, (40, 60, 100), 2); c.ell(45, 87, 55, 94, (60, 80, 120)); return c.done()
def sp_db():
    c = Cv(); c.rect(22, 28, 74, 70, BL); c.ell(22, 62, 74, 80, BL); c.ell(22, 18, 74, 38, (110, 170, 250))
    c.arc(22, 40, 74, 56, 0, 180, WH, 2.5); c.arc(22, 52, 74, 68, 0, 180, WH, 2.5)
    c.poly([(82, 46), (72, 68), (92, 68)], RD); c.ell(72, 62, 92, 82, RD); c.ell(79, 66, 83, 71, (255, 190, 190)); return c.done()
def sp_key():
    c = Cv(); c.rect(40, 42, 92, 50, AM, 2); c.rect(76, 50, 83, 62, AM, 1); c.rect(86, 50, 93, 66, AM, 1)
    c.ell(6, 26, 46, 66, AM); c.ell(17, 37, 35, 55, DK); return c.done()
def sp_wifi():
    c = Cv()
    for r in (46, 31, 16): c.arc(50 - r, 78 - r, 50 + r, 78 + r, 228, 312, CY, 7.5)
    c.ell(44, 72, 56, 84, CY); return c.done()
def sp_laptop():
    c = Cv(); c.rect(15, 20, 85, 68, (30, 41, 70), 4, CY, 2.5); c.rect(20, 25, 80, 63, (15, 30, 60), 2)
    c.poly([(6, 72), (94, 72), (87, 82), (13, 82)], (150, 170, 210)); c.rect(40, 72, 60, 75, (110, 130, 175), 1)
    c.poly(scale_pts([(50, 28), (64, 33), (64, 46), (50, 60), (36, 46), (36, 33)], 1, (50, 44)), GR)
    c.line([(43, 44), (48, 50), (58, 38)], DK, 2.6); return c.done()
def sp_profile():
    c = Cv(); c.ell(33, 12, 67, 46, CY); c.ell(14, 54, 86, 120, BL)
    c.rect(60, 62, 90, 90, AM, 5); c.arc(66, 46, 84, 70, 180, 360, AM, 4); c.ell(72, 71, 78, 77, DK); c.rect(74, 74, 76, 82, DK, 0.5)
    return c.done()
def sp_chat():
    c = Cv(); c.rect(6, 12, 70, 52, CY, 10); c.poly([(18, 50), (16, 66), (34, 50)], CY)
    for x in (24, 36, 48): c.ell(x, 28, x + 7, 35, DK)
    c.rect(34, 46, 94, 82, WH, 10); c.poly([(78, 80), (84, 94), (66, 80)], WH)
    c.ell(50, 56, 62, 68, RD); c.ell(62, 56, 74, 68, RD); c.poly([(50.5, 64), (73.5, 64), (62, 76)], RD); return c.done()

SPR = {}
def build_sprites():
    for k, f in dict(shield=sp_shield, bug=sp_bug, hook=sp_hook, phone=sp_phone, db=sp_db, key=sp_key,
                     wifi=sp_wifi, laptop=sp_laptop, profile=sp_profile, chat=sp_chat).items():
        SPR[k] = f()
build_sprites()

# ---------------------------------------------------------------- рисование
def _grad():
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([8, 16, 40], np.float32); bot = np.array([19, 36, 74], np.float32)
    a = (top + (bot - top) * y) * np.ones((H, W, 1), np.float32)
    return Image.fromarray(a.astype(np.uint8), "RGB")
GRAD = _grad()
_r = random.Random(5)
PART = [(_r.uniform(0, W), _r.uniform(0, H), _r.uniform(-14, 14), _r.uniform(-10, 10)) for _ in range(46)]

def bg(t):
    img = GRAD.copy(); d = ImageDraw.Draw(img)
    pts = [((x + vx * t) % W, (y + vy * t) % H) for x, y, vx, vy in PART]
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            if dist < 150:
                d.line([pts[i], pts[j]], fill=mix((14, 28, 58), (40, 72, 124), 1 - dist / 150), width=1)
    for x, y in pts:
        d.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=(48, 86, 142))
    return img

def blend_draw(img, box, fn, a=1.0):
    if a <= 0: return
    bx = (int(box[0]) - 6, int(box[1]) - 6, int(box[2]) + 6, int(box[3]) + 6)
    if a >= 0.995:
        fn(ImageDraw.Draw(img), (0, 0)); return
    crop = img.crop(bx); layer = crop.copy(); fn(ImageDraw.Draw(layer), (bx[0], bx[1]))
    img.paste(Image.blend(crop, layer, a), bx[:2])

def text_a(img, xy, s, font, fill, a=1.0, anchor="la"):
    if a <= 0 or not s: return
    d = ImageDraw.Draw(img)
    bb = d.textbbox(xy, s, font=font, anchor=anchor)
    blend_draw(img, bb, lambda dd, o: dd.text((xy[0] - o[0], xy[1] - o[1]), s, font=font, fill=fill, anchor=anchor), a)

def rrect(img, box, fill, ol=None, w=2, r=16, a=1.0):
    blend_draw(img, box, lambda d, o: d.rounded_rectangle(
        [box[0] - o[0], box[1] - o[1], box[2] - o[0], box[3] - o[1]], r, fill=fill, outline=ol, width=w), a)

def paste_sprite(img, spr, cx, cy, scale=1.0, a=1.0):
    if a <= 0 or scale <= 0.01: return
    if abs(scale - 1) > 0.005:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
    if a < 1:
        spr = spr.copy(); spr.putalpha(spr.getchannel("A").point(lambda v: int(v * a)))
    img.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)

def wrap(s, font, maxw):
    words = s.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ---------------------------------------------------------------- общие элементы
def sent_cur(sc, t):
    c = None
    for i, (a, b) in enumerate(sc["st"]):
        if a <= t < b + 0.4: c = i
    return c

def sent_start(sc, i): return sc["st"][i][0]

def bstart(sc, k):
    b = sc["bullets"][k]; rank = sum(1 for j in range(k) if sc["bullets"][j][1] == b[1])
    return sent_start(sc, b[1]) + 0.45 * rank

def header(img, t, sc, idx):
    a = eo(t / 0.6)
    text_a(img, (70, 24), sc.get("tag", ""), F(18, True), CY, a)
    text_a(img, (70 - 40 * (1 - a), 50), sc["title"], F(46, True), WH, a)
    d = ImageDraw.Draw(img); d.rectangle([70, 112, 70 + 300 * a, 116], fill=CY)

def caption(img, t, sc):
    ci = None
    for i, (a, b) in enumerate(sc["st"]):
        if a <= t < b + 0.35: ci = i
    if ci is None: return
    a0, b0 = sc["st"][ci]
    al = min(clamp((t - a0) / 0.25), clamp((b0 + 0.35 - t) / 0.25))
    text = sc["cap"][ci]
    rrect(img, (40, 622, W - 40, 706), (6, 12, 30), None, 0, 14, 0.78 * al)
    lines = wrap(text, F(26), W - 130)[:2]
    y = 664 - 17 * len(lines) + 0 + 0
    for k, ln in enumerate(lines):
        text_a(img, (W / 2, 664 + (k - (len(lines) - 1) / 2) * 36), ln, F(26), WH, al, "mm")

def progress(img, T, total):
    d = ImageDraw.Draw(img); d.rectangle([0, H - 6, W, H], fill=(10, 20, 44))
    d.rectangle([0, H - 6, int(W * T / total), H], fill=CY)

def sprite_panel(img, t, sc, cx=1000, cy=350, k=1.5):
    spr = sc.get("sprite")
    if not spr: return
    a = clamp((t - 0.3) / 0.8); sc_ = 0.35 + 0.65 * eback(a)
    d = ImageDraw.Draw(img)
    r = 175 * sc_
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 48, 94))
    rr = (190 + 10 * math.sin(t * 2.2)) * sc_
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(40, 90, 150), width=3)
    paste_sprite(img, SPR[spr], cx, cy + 8 * math.sin(t * 2), k * sc_, clamp(a * 1.5))
    s2 = sc.get("sprite2")
    if s2:
        t0 = sent_start(sc, s2[1]); a2 = clamp((t - t0) / 0.6)
        paste_sprite(img, SPR[s2[0]], cx + 110, cy - 130 + 6 * math.sin(t * 2.6 + 1), 0.8 * (0.3 + 0.7 * eback(a2)), a2)

def draw_bullets(img, t, sc):
    n = len(sc["bullets"]); sp = sc.get("sp", 120 if n <= 3 else 108); ch = sp - 16
    y0 = sc.get("y0", 170); cw = sc.get("cw", 670); cur = sent_cur(sc, t)
    for k, b in enumerate(sc["bullets"]):
        ts = bstart(sc, k); p = clamp((t - ts) / 0.5)
        if p <= 0: continue
        e = eo(p); x = 70 - 60 * (1 - e); y = y0 + k * sp
        good = len(b) > 2 and b[2] == "good"; col = GR if good else CY
        active = cur == b[1]
        box = (x, y, x + cw, y + ch)
        rrect(img, box, (20, 52, 62) if good else CARD, col if active else (46, 70, 118), 3 if active else 2, 16, e)
        cyy = y + ch / 2
        d = ImageDraw.Draw(img)
        if "||" in b[0]:
            main, sub = b[0].split("||")
            text_a(img, (x + 28, cyy - 17), main, F(25, True), WH, e, "lm")
            text_a(img, (x + 28, cyy + 16), sub, F(20), CY, e, "lm")
            text_a(img, (x + cw - 24, cyy), str(k + 1), F(28, True), MUTED, e, "rm")
        else:
            blend_draw(img, (x + 20, cyy - 24, x + 68, cyy + 24),
                       lambda dd, o: dd.ellipse([x + 20 - o[0], cyy - 24 - o[1], x + 68 - o[0], cyy + 24 - o[1]], fill=col), e)
            text_a(img, (x + 44, cyy), "✓" if good else str(k + 1), F(26, True), DK, e, "mm")
            lines = wrap(b[0], F(27, True), cw - 110)
            for li, ln in enumerate(lines):
                yy = cyy + (li - (len(lines) - 1) / 2) * 34
                text_a(img, (x + 90, yy), ln, F(27, True), (200, 255, 235) if good else WH, e, "lm")

# ---------------------------------------------------------------- сцены
def scene_title(img, t, sc):
    cx, cy = 330, 340
    a = clamp(t / 1.0); s = 0.4 + 0.6 * eback(a)
    d = ImageDraw.Draw(img)
    r = 250 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 48, 94))
    for k, rad in enumerate((275, 305)):
        rr = (rad + 12 * math.sin(t * 2 + k)) * s
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(36 + 10 * k, 80 + 10 * k, 140), width=3)
    paste_sprite(img, SPR["shield"], cx, cy + 8 * math.sin(t * 1.8), 2.1 * s, clamp(a * 1.6))
    x = 620
    text_a(img, (x, 150), "МУЛЬТИМЕДИЙНЫЙ ПРОЕКТ", F(22, True), CY, eo((t - 0.3) / 0.5))
    n1 = int(len("Безопасность") * clamp((t - 0.5) / 0.9)); n2 = int(len("в Интернете") * clamp((t - 1.3) / 0.8))
    text_a(img, (x, 190), "Безопасность"[:n1], F(66, True), WH)
    text_a(img, (x, 270), "в Интернете"[:n2], F(66, True), CY)
    ln = eo((t - 1.8) / 0.7)
    ImageDraw.Draw(img).rectangle([x, 372, x + 420 * ln, 377], fill=AM)
    p = eo((t - 2.2) / 0.6)
    text_a(img, (x, 410 + 20 * (1 - p)), "Автор: " + AUTHOR, F(30, True), WH, p)
    text_a(img, (x, 455 + 20 * (1 - p)), GROUP, F(26), MUTED, p)
    text_a(img, (x, 520), "Практическая работа № 101–102", F(22), MUTED, eo((t - 2.8) / 0.6))

def scene_bullets(img, t, sc):
    sprite_panel(img, t, sc)
    draw_bullets(img, t, sc)

def scene_threats(img, t, sc):
    cur = sent_cur(sc, t)
    for k, (spr, title, desc, si) in enumerate(sc["cards"]):
        ts = sent_start(sc, si); p = clamp((t - ts) / 0.55)
        if p <= 0: continue
        e = eo(p); x = 70 + (k % 2) * 585; y = 150 + (k // 2) * 220 + 30 * (1 - e)
        active = cur == si
        rrect(img, (x, y, x + 555, y + 190), CARD, CY if active else (46, 70, 118), 3 if active else 2, 20, e)
        d = ImageDraw.Draw(img)
        d.ellipse([x + 24, y + 30, x + 154, y + 160], fill=(24, 52, 100))
        paste_sprite(img, SPR[spr], x + 89, y + 95 + 4 * math.sin(t * 2 + k), 0.58 * (0.5 + 0.5 * eback((t - ts) / 0.7)), e)
        text_a(img, (x + 180, y + 72), title, F(26, True), WH, e, "lm")
        for li, ln in enumerate(wrap(desc, F(20), 355)):
            text_a(img, (x + 180, y + 112 + li * 26), ln, F(20), MUTED, e, "lm")

def scene_video(img, t, sc):
    dur = sc["dur"]
    x0, y0, x1, y1 = 60, 135, 820, 605
    rrect(img, (x0, y0, x1, y1), (10, 18, 40), RD, 3, 16)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y0 + 34], 16, fill=(30, 41, 70)); d.rectangle([x0, y0 + 20, x1, y0 + 34], fill=(30, 41, 70))
    for i, c in enumerate((RD, AM, GR)): d.ellipse([x0 + 16 + i * 22, y0 + 11, x0 + 28 + i * 22, y0 + 23], fill=c)
    rec = 0.5 + 0.5 * math.sin(t * 5)
    d.ellipse([x0 + 100, y0 + 11, x0 + 112, y0 + 23], fill=mix((70, 30, 30), RD, rec))
    d.text((x0 + 124, y0 + 17), "ВИДЕОРОЛИК · Как распознать фишинг", font=F(17, True), fill=WH, anchor="lm")
    px0, py0, px1, py1 = x0 + 18, y0 + 50, x1 - 18, y0 + 392
    d.rounded_rectangle([px0, py0, px1, py1], 10, fill=(244, 247, 252))
    ink = (30, 40, 60)
    d.text((px0 + 20, py0 + 26), "От:", font=F(21), fill=(110, 120, 140), anchor="lm")
    d.text((px0 + 70, py0 + 26), "support@secure-bank-verify.xyz", font=F(21, True), fill=ink, anchor="lm")
    d.text((px0 + 20, py0 + 70), "Тема: СРОЧНО! Ваш аккаунт будет заблокирован", font=F(21, True), fill=(170, 40, 40), anchor="lm")
    d.line([px0 + 14, py0 + 96, px1 - 14, py0 + 96], fill=(210, 216, 228), width=2)
    body = ["Уважаемый клиент! Мы заметили подозрительный вход",
            "в ваш аккаунт. Подтвердите данные в течение 1 часа,",
            "иначе доступ будет закрыт."]
    total_chars = sum(len(b) for b in body)
    shown = int(total_chars * clamp((t - 0.5) / (sc["st"][0][1] - 0.3)))
    for i, line in enumerate(body):
        n = max(0, min(len(line), shown)); shown -= len(line)
        d.text((px0 + 20, py0 + 126 + i * 32), line[:n], font=F(21), fill=ink, anchor="lm")
    d.rounded_rectangle([px0 + 20, py0 + 202, px0 + 290, py0 + 252], 10, fill=BL)
    d.text((px0 + 155, py0 + 227), "Подтвердить аккаунт", font=F(20, True), fill=WH, anchor="mm")
    d.text((px0 + 20, py0 + 285), "http://secure-bank-verify.xyz/login", font=F(20), fill=(40, 90, 200), anchor="lm")
    d.line([px0 + 20, py0 + 297, px0 + 382, py0 + 297], fill=(40, 90, 200), width=1)
    # флаги
    flags = [(1, (px0 + 8, py0 + 8, px0 + 470, py0 + 46), (px0 + 500, py0 + 27)),
             (2, (px0 + 8, py0 + 52, px0 + 640, py0 + 90), None),
             (2, (px0 + 8, py0 + 108, px0 + 650, py0 + 214), (px0 + 682, py0 + 160)),
             (3, (px0 + 8, py0 + 270, px0 + 395, py0 + 304), (px0 + 425, py0 + 287))]
    for num, box, badge in flags:
        ts = sent_start(sc, num); p = clamp((t - ts) / 0.45)
        if p <= 0: continue
        pul = 3 + 2 * math.sin(t * 6)
        b = (box[0] - pul * (1 - p) * 4, box[1] - pul * (1 - p) * 4, box[2] + pul * (1 - p) * 4, box[3] + pul * (1 - p) * 4)
        d.rounded_rectangle(b, 8, outline=RD, width=3)
        if badge:
            r = 17 * eback(p)
            d.ellipse([badge[0] - r, badge[1] - r, badge[0] + r, badge[1] + r], fill=RD)
            d.text(badge, str(num), font=F(20, True), fill=WH, anchor="mm")
    # курсор и «стоп»
    t3 = sent_start(sc, 3)
    if t > t3 - 0.2:
        q = eo((t - t3) / 1.4); cx = 700 + (px0 + 200 - 700) * q; cy = 580 + (py0 + 290 - 580) * q
        d.polygon([(cx, cy), (cx, cy + 26), (cx + 7, cy + 20), (cx + 14, cy + 32), (cx + 19, cy + 29), (cx + 12, cy + 18), (cx + 21, cy + 17)],
                  fill=WH, outline=(10, 10, 10))
        if t > t3 + 1.4:
            pp = eback((t - t3 - 1.4) / 0.4)
            rrect(img, (px0 + 240, py0 + 318, px0 + 240 + 230 * pp, py0 + 360), RD, None, 0, 10)
            if pp > 0.9: text_a(img, (px0 + 355, py0 + 339), "✕ Не нажимать!", F(21, True), WH, 1, "mm")
    # плеер
    d = ImageDraw.Draw(img)
    d.text((x0 + 22, y1 - 22), "▶", font=F(20), fill=WH, anchor="lm")
    bx0, bx1, by = x0 + 60, x1 - 130, y1 - 22
    d.rounded_rectangle([bx0, by - 4, bx1, by + 4], 4, fill=(50, 66, 104))
    d.rounded_rectangle([bx0, by - 4, bx0 + (bx1 - bx0) * clamp(t / dur), by + 4], 4, fill=RD)
    sec = int(min(t, dur)); tot = int(dur)
    d.text((x1 - 22, y1 - 22), "%d:%02d / %d:%02d" % (sec // 60, sec % 60, tot // 60, tot % 60), font=F(17), fill=WH, anchor="rm")
    # карточки справа
    items = [("Адрес отправителя", "Не совпадает с настоящим сайтом", 1, RD),
             ("Давление срочностью", "«Аккаунт заблокируют через час»", 2, RD),
             ("Странная ссылка", "Домен не тот, что у сервиса", 3, RD),
             ("Что делать", "Открыть сайт самому, не нажимать", 4, GR)]
    cur = sent_cur(sc, t)
    for k, (tt, ss, si, col) in enumerate(items):
        p = clamp((t - sent_start(sc, si)) / 0.5)
        if p <= 0: continue
        e = eo(p); x = 850 + 40 * (1 - e); y = 140 + k * 112
        act = cur == si
        rrect(img, (x, y, x + 380, y + 100), (20, 52, 62) if col == GR else CARD, col if act else (46, 70, 118), 3 if act else 2, 14, e)
        blend_draw(img, (x + 12, y + 28, x + 56, y + 72),
                   lambda dd, o: dd.ellipse([x + 12 - o[0], y + 28 - o[1], x + 56 - o[0], y + 72 - o[1]], fill=col), e)
        text_a(img, (x + 34, y + 50), "✓" if col == GR else str(si), F(24, True), DK if col == GR else WH, e, "mm")
        text_a(img, (x + 70, y + 26), tt, F(23, True), WH, e, "lm")
        for li, ln in enumerate(wrap(ss, F(18), 290)[:2]):
            text_a(img, (x + 70, y + 58 + li * 24), ln, F(18), MUTED, e, "lm")

def scene_pass(img, t, sc):
    draw_bullets(img, t, sc)
    cur = sent_cur(sc, t); x0, x1 = 700, 1225
    # сильный пароль
    p = clamp((t - sent_start(sc, 1)) / 0.5)
    if p > 0:
        e = eo(p); y = 150; box = (x0 + 30 * (1 - e), y, x1 + 30 * (1 - e), y + 135)
        rrect(img, box, (20, 52, 62), GR if cur == 1 else (46, 90, 90), 3 if cur == 1 else 2, 16, e)
        bx = box[0]
        text_a(img, (bx + 22, y + 24), "Надёжный пароль", F(19), MUTED, e, "lm")
        text_a(img, (bx + 22, y + 62), "Синий кот любит чай!", F(32, True), (190, 255, 230), e, "lm")
        fill = clamp((t - sent_start(sc, 1) - 0.4) / 1.4)
        d = ImageDraw.Draw(img); d.rounded_rectangle([bx + 22, y + 100, bx + 22 + 480, y + 114], 7, fill=(40, 62, 90))
        if fill > 0: d.rounded_rectangle([bx + 22, y + 100, bx + 22 + 480 * 0.96 * eo(fill) + 2, y + 114], 7, fill=GR)
    # слабый пароль
    p = clamp((t - sent_start(sc, 2)) / 0.5)
    if p > 0:
        e = eo(p); y = 305; box = (x0 + 30 * (1 - e), y, x1 + 30 * (1 - e), y + 135)
        rrect(img, box, (62, 28, 36), RD if cur == 2 else (110, 60, 70), 3 if cur == 2 else 2, 16, e)
        bx = box[0]
        text_a(img, (bx + 22, y + 24), "Слабый пароль", F(19), MUTED, e, "lm")
        text_a(img, (bx + 22, y + 62), "123456", F(32, True), (255, 190, 190), e, "lm")
        fill = clamp((t - sent_start(sc, 2) - 0.4) / 1.0)
        d = ImageDraw.Draw(img); d.rounded_rectangle([bx + 22, y + 100, bx + 22 + 480, y + 114], 7, fill=(40, 62, 90))
        if fill > 0: d.rounded_rectangle([bx + 22, y + 100, bx + 22 + 480 * 0.08 * eo(fill) + 10, y + 114], 7, fill=RD)
    # 2FA
    p = clamp((t - sent_start(sc, 3)) / 0.5)
    if p > 0:
        e = eo(p); y = 460; box = (x0 + 30 * (1 - e), y, x1 + 30 * (1 - e), y + 140)
        rrect(img, box, CARD, CY if cur == 3 else (46, 70, 118), 3 if cur == 3 else 2, 16, e)
        bx = box[0]
        text_a(img, (bx + 22, y + 24), "Код подтверждения из приложения", F(19), MUTED, e, "lm")
        code = "482913"; d = ImageDraw.Draw(img)
        for i, ch in enumerate(code):
            q = clamp((t - sent_start(sc, 3) - 0.5 - i * 0.22) / 0.25)
            if q <= 0: continue
            xx = bx + 22 + i * 56
            d.rounded_rectangle([xx, y + 50, xx + 48, y + 106], 9, fill=(10, 24, 54), outline=CY, width=2)
            d.text((xx + 24, y + 78), ch, font=F(32, True), fill=WH, anchor="mm")
        q = clamp((t - sent_start(sc, 3) - 2.2) / 0.5)
        if q > 0:
            text_a(img, (bx + 22 + 6 * 56 + 8, y + 66), "✓", F(40, True), GR, q, "lm")
            text_a(img, (bx + 22 + 6 * 56 + 8, y + 100), "Вход", F(18, True), GR, q, "lm")

SCENE_FN = dict(title=scene_title, bullets=scene_bullets, threats=scene_threats, video=scene_video, pass_=None)
SCENE_FN["pass"] = scene_pass

def render_scene(i, t, total, S):
    sc = S[i]
    img = bg(S[i]["start"] + t)
    if sc["kind"] != "title": header(img, t, sc, i)
    SCENE_FN[sc["kind"]](img, t, sc)
    caption(img, t, sc)
    progress(img, sc["start"] + t, total)
    return img

# ---------------------------------------------------------------- переходы
def transition(prev, new, p, kind):
    e = eo(p)
    if kind == 0:
        return Image.blend(prev, new, e)
    if kind == 1:
        out = Image.new("RGB", (W, H)); off = int(W * e)
        out.paste(prev, (-off, 0)); out.paste(new, (W - off, 0)); return out
    if kind == 2:
        out = prev.copy(); h = int(H * e)
        if h > 0: out.paste(new.crop((0, 0, W, h)), (0, 0))
        return out
    s = 1.12 - 0.12 * e
    z = new.resize((int(W * s), int(H * s)), Image.BILINEAR)
    z = z.crop(((z.width - W) // 2, (z.height - H) // 2, (z.width - W) // 2 + W, (z.height - H) // 2 + H))
    return Image.blend(prev, z, e)

def merged_scenes():
    S = []
    for sc, tm in zip(SC, TM["scenes"]):
        d = dict(sc); d.update(start=tm["start"], dur=tm["dur"], st=tm["st"])
        d["cap"] = [(c or s) for s, c in sc["sents"]]
        S.append(d)
    return S

def render_frame(n):
    S = _S; total = TM["total"]; T = n / FPS
    i = max(k for k in range(len(S)) if S[k]["start"] <= T + 1e-9)
    t = T - S[i]["start"]
    img = render_scene(i, t, total, S)
    if i > 0 and t < TR:
        prev = render_scene(i - 1, S[i - 1]["dur"] - 0.01, total, S)
        img = transition(prev, img, t / TR, i % 4)
    fade = clamp((total - T) / 0.8)
    if fade < 1: img = Image.blend(Image.new("RGB", (W, H)), img, fade)
    return img

def _rf(n): return render_frame(n).tobytes()

# ---------------------------------------------------------------- звук
SR = 44100
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def tts_stage():
    scenes = []; clips = []; cur = 0.0
    for si, sc in enumerate(SC):
        st = []; t = LEAD
        for k, (txt, _) in enumerate(sc["sents"]):
            path = os.path.join(WORK, "s%02d_%02d.wav" % (si, k))
            run(["espeak-ng", "-v", "ru+f3", "-s", "165", "-p", "55", "-g", "3", "-w", path, txt.replace(" — ", ", ")])
            w = wave.open(path); n = w.getnframes(); sr = w.getframerate()
            a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768; w.close()
            a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a).astype(np.float32)
            d = len(a) / SR; st.append([t, t + d]); clips.append((cur + t, a)); t += d + GAP
        dur = t - GAP + TAIL
        scenes.append(dict(start=cur, dur=dur, st=st)); cur += dur
    total = cur + 0.6
    json.dump(dict(scenes=scenes, total=total), open(os.path.join(WORK, "timing.json"), "w"), ensure_ascii=False)
    n = int(total * SR); narr = np.zeros(n, np.float32)
    for s, a in clips:
        i = int(s * SR); narr[i:i + len(a)] += a[:n - i]
    narr = narr / (np.abs(narr).max() + 1e-6) * 0.85
    # музыка
    t_ = np.arange(n) / SR; mus = np.zeros(n, np.float32); arp = np.zeros(n, np.float32)
    f = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    chords = [[45, 57, 60, 64], [41, 57, 60, 65], [48, 55, 60, 64], [43, 55, 59, 62]]
    nch = int(total // 4) + 2
    for c in range(nch):
        ch = chords[c % 4]; s0 = c * 4 - 0.5; i0 = max(0, int(s0 * SR)); i1 = min(n, int((c * 4 + 4.5) * SR))
        if i1 <= i0: continue
        tt = t_[i0:i1] - (c * 4); env = np.clip((tt + 0.5) / 1.2, 0, 1) * np.clip((4.5 - tt) / 1.2, 0, 1)
        for m in ch:
            amp = 0.22 if m < 50 else 0.11
            mus[i0:i1] += env * amp * (np.sin(2 * np.pi * f(m) * t_[i0:i1]) + 0.35 * np.sin(2 * np.pi * f(m) * 2.003 * t_[i0:i1]))
        for b in range(8):
            ts = c * 4 + b * 0.5; j0 = int(ts * SR); j1 = min(n, j0 + int(0.9 * SR))
            if j0 >= n: break
            note = ch[1:][(b * 2 + (1 if b % 2 else 0)) % 3] + 12
            lt = np.arange(j1 - j0) / SR
            arp[j0:j1] += 0.5 * np.exp(-lt * 5.0) * np.sin(2 * np.pi * f(note) * lt) * np.clip(lt / 0.01, 0, 1)
    for dly, g in ((0.375, 0.4), (0.75, 0.22), (1.125, 0.12)):
        k = int(dly * SR); arp[k:] += arp[:-k] * g if False else 0
    ar2 = arp.copy()
    for dly, g in ((0.375, 0.4), (0.75, 0.22), (1.125, 0.12)):
        k = int(dly * SR); ar2[k:] += arp[:-k] * g
    mus += ar2 * 0.55
    mus = mus / (np.abs(mus).max() + 1e-6) * 0.20
    mus *= np.clip(t_ / 1.5, 0, 1) * np.clip((total - t_) / 1.5, 0, 1)
    # whoosh
    sfx = np.zeros(n, np.float32); rng = np.random.default_rng(3)
    for sc_ in scenes[1:]:
        m = int(0.7 * SR); nz = rng.standard_normal(m).astype(np.float32)
        nz = np.convolve(nz, np.ones(40) / 40, "same"); env = np.sin(np.pi * np.linspace(0, 1, m)) ** 2
        i = int(sc_["start"] * SR); sfx[i:i + m] += nz * env * 0.9
    sfx = sfx / (np.abs(sfx).max() + 1e-6) * 0.22
    mix_ = np.clip(narr + mus + sfx, -1, 1)
    st = np.stack([mix_, mix_], 1)
    w = wave.open(os.path.join(WORK, "audio.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
    print("TOTAL %.1f s" % total)
    for i, s in enumerate(scenes): print(i + 1, "%.1f" % s["start"], "%.1f" % s["dur"])

_S = None
def init_scenes():
    global TM, _S
    TM = load_timing(); _S = merged_scenes()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "tts":
        tts_stage()
    else:
        init_scenes()
        if mode == "preview":
            for a in sys.argv[2:]:
                T = float(a); render_frame(int(T * FPS)).save(os.path.join(WORK, "p_%s.png" % a))
        elif mode == "render":
            from multiprocessing import Pool
            total = TM["total"]; nf = int(total * FPS)
            out = os.path.join(OUT_DIR, OUT_NAME)
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                                   "-r", str(FPS), "-i", "-", "-i", os.path.join(WORK, "audio.wav"),
                                   "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                                   "-c:a", "aac", "-b:a", "160k", "-t", "%.2f" % total, "-movflags", "+faststart", out],
                                  stdin=subprocess.PIPE)
            with Pool(4) as pool:
                for k, b in enumerate(pool.imap(_rf, range(nf), chunksize=6)):
                    ff.stdin.write(b)
                    if k % 250 == 0: print(k, "/", nf, flush=True)
            ff.stdin.close(); ff.wait(); print("done", out)
