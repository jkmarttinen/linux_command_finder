"""Kielituki (suomi/englanti): käyttöliittymän tekstit, asetusten tallennus ja komentojen käännökset."""
import json
import os

from komennot_en import ESIMERKKI as _ES_EN
from komennot_en import KATEGORIA as _KAT_EN
from komennot_en import KOMENTO as _KOM_EN
from komennot_en import SELITYS as _SEL_EN

ASETUSPOLKU = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "komentoapuri", "asetukset.json"
)

TEKSTIT = {
    "fi": {
        "ikkunan_otsikko": "Linux-komentoapuri",
        "logo": "KOMENTOAPURI",
        "tila_komennot": "KOMENNOT",
        "tila_paketit": "PAKETIT",
        "kaikki": "KAIKKI",
        "haku_komennot": "Hae komentoa tai kuvausta…",
        "haku_paketit": "Hae sovellusta, esim. kuvankäsittely, video editor, vlc…",
        "vihje_komennot": "↑↓ valitse · Enter / tuplaklikkaus kopioi · Tab: paketit · Esc piilota",
        "vihje_paketit": "↑↓ valitse · Enter kopioi asennuskomento · Tab: komennot · Esc piilota",
        "esimerkki": "ESIMERKKI",
        "kopioi_leikepoydalle": "KOPIOI LEIKEPÖYDÄLLE",
        "ei_tuloksia": "Ei tuloksia",
        "kokeile_toista": "Kokeile toista hakusanaa.",
        "kopioitu": "Kopioitu: {teksti}",
        "piilota_kirjastot": "PIILOTA KIRJASTOT",
        "vain_asennetut": "VAIN ASENNETUT",
        "haetaan": "  haetaan…",
        "tulosta": "  {n} tulosta",
        "haku_termit": "haku: {termit}",
        "piilotettu": "{n} piilotettu",
        "hae_sovelluksia": "HAE SOVELLUKSIA",
        "hae_ohje": (
            "Kirjoita mitä haluat tehdä tai ohjelman nimi, esim.\n"
            "  • kuvankäsittely\n  • video editor\n  • musiikkisoitin\n  • salasana\n  • vlc\n\n"
            "Suomenkieliset hakusanat käännetään englanniksi automaattisesti."
        ),
        "pak_ei_tuloksia": "EI TULOKSIA",
        "pak_ei_tuloksia_ohje": "Kokeile toista hakusanaa tai englanninkielistä termiä.",
        "pak_kirjastot_piilossa": " Kirjastot on piilotettu – voit näyttää ne yllä.",
        "asennettu_merkki": "ASENNETTU",
        "asennettu_tila": "● ASENNETTU",
        "ei_asennettu_tila": "○ EI ASENNETTU",
        "haetaan_tietoja": "Haetaan tietoja…",
        "ei_pitkaa": "(ei pitkää kuvausta)",
        "versio": "versio {v}",
        "koko": "koko {mt:.1f} Mt",
        "asenna_terminaalissa": "ASENNA TERMINAALISSA",
        "poista_terminaalissa": "POISTA TERMINAALISSA",
        "kopioi_komento": "KOPIOI KOMENTO",
        "terminaali_virhe": "Terminaalin avaus epäonnistui: {e}",
        "terminaali_valmis": "Valmis. Paina Enter sulkeaksesi…",
        "kieli_vihje": "Vaihda kieli / Change language",
    },
    "en": {
        "ikkunan_otsikko": "Linux Command Helper",
        "logo": "COMMAND HELPER",
        "tila_komennot": "COMMANDS",
        "tila_paketit": "PACKAGES",
        "kaikki": "ALL",
        "haku_komennot": "Search for a command or description…",
        "haku_paketit": "Search for an app, e.g. image editor, video editor, vlc…",
        "vihje_komennot": "↑↓ select · Enter / double-click copy · Tab: packages · Esc hide",
        "vihje_paketit": "↑↓ select · Enter copies the install command · Tab: commands · Esc hide",
        "esimerkki": "EXAMPLE",
        "kopioi_leikepoydalle": "COPY TO CLIPBOARD",
        "ei_tuloksia": "No results",
        "kokeile_toista": "Try another search word.",
        "kopioitu": "Copied: {teksti}",
        "piilota_kirjastot": "HIDE LIBRARIES",
        "vain_asennetut": "INSTALLED ONLY",
        "haetaan": "  searching…",
        "tulosta": "  {n} results",
        "haku_termit": "search: {termit}",
        "piilotettu": "{n} hidden",
        "hae_sovelluksia": "SEARCH FOR APPS",
        "hae_ohje": (
            "Type what you want to do or a program name, e.g.\n"
            "  • image editor\n  • video editor\n  • music player\n  • password\n  • vlc\n\n"
            "Finnish search words are translated to English automatically."
        ),
        "pak_ei_tuloksia": "NO RESULTS",
        "pak_ei_tuloksia_ohje": "Try another search word or an English term.",
        "pak_kirjastot_piilossa": " Libraries are hidden – you can show them above.",
        "asennettu_merkki": "INSTALLED",
        "asennettu_tila": "● INSTALLED",
        "ei_asennettu_tila": "○ NOT INSTALLED",
        "haetaan_tietoja": "Fetching details…",
        "ei_pitkaa": "(no long description)",
        "versio": "version {v}",
        "koko": "size {mt:.1f} MB",
        "asenna_terminaalissa": "INSTALL IN TERMINAL",
        "poista_terminaalissa": "REMOVE IN TERMINAL",
        "kopioi_komento": "COPY COMMAND",
        "terminaali_virhe": "Could not open the terminal: {e}",
        "terminaali_valmis": "Done. Press Enter to close…",
        "kieli_vihje": "Vaihda kieli / Change language",
    },
}

# Suomenkieliset paikkamerkit esimerkeissä -> englanti (pisin ensin)
_PAIKKA = [
    ("kuvankäsittely", "image editor"), ("käyttäjä", "user"), ("palvelin", "server"),
    ("tiedosto", "file"), ("kansio", "folder"), ("lähde", "source"), ("kohde", "target"),
    ("arkisto", "archive"), ("skripti", "script"), ("vanha", "old"), ("uusi", "new"),
    ("istunto", "session"), ("asetus", "settings"), ("salainen", "secret"), ("tärkeä", "important"),
    ("loki", "log"), ("essee", "essay"), ("projekti", "project"), ("kuvat", "images"),
    ("kuva", "image"), ("virhe", "error"), ("sana", "word"), ("nimet", "names"), ("nimi", "name"),
    ("kone", "host"), ("polku", "path"), ("komento", "command"), ("ohjelma", "program"),
    ("lataukset", "downloads"), ("lista", "list"), ("etä", "remote"), ("osa_", "part_"),
    ("uusi-haara", "new-branch"), ("tervehdi", "greet"), ("kaikki", "all"),
    ("tyhja", "empty"), ("uusikayttaja", "newuser"), ("osa_nimesta", "part_of_name"), ("pitka", "long"), ("linkki", "link"), ("newkayttaja", "newuser"),
    ("part_nimesta", "part_of_name"), ("raskas_", "heavy_"), ("levy.img", "disk.img"),
    ("varmuus", "backup"), ("Moi", "Hi"), ("moi", "hi"), ("rivi", "line"), ("viesti", "message"),
    ("ei asennettu", "not installed"), ("  ja  ", "  and  "), ("esimerkki.fi", "example.com"),
    ("esim.fi", "example.com"), (".versio", ".version"), ("lataa", "download"),
    ("Nimesi?", "Your name?"), ("targetfolder", "targetfolder"),
]
_PAIKKA.sort(key=lambda p: -len(p[0]))


def lataa_asetukset():
    try:
        with open(ASETUSPOLKU, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def tallenna_asetukset(data):
    try:
        os.makedirs(os.path.dirname(ASETUSPOLKU), exist_ok=True)
        with open(ASETUSPOLKU, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _oletuskieli():
    return "fi"  # oletuksena suomi; valinta tallentuu asetuksiin kun vaihdat kielen


class Kieli:
    def __init__(self):
        self.asetukset = lataa_asetukset()
        k = self.asetukset.get("kieli")
        self.nyt = k if k in TEKSTIT else _oletuskieli()

    def aseta(self, kieli):
        if kieli in TEKSTIT:
            self.nyt = kieli
            self.asetukset["kieli"] = kieli
            tallenna_asetukset(self.asetukset)

    def t(self, avain, **kw):
        s = TEKSTIT[self.nyt].get(avain) or TEKSTIT["fi"].get(avain, avain)
        return s.format(**kw) if kw else s

    # --- komentojen kääntäminen ---
    def kategoria(self, kat):
        return kat if self.nyt == "fi" else _KAT_EN.get(kat, kat)

    def komento_en(self, r):
        """Englanninkielinen versio suomenkielisestä rivistä (kieleen katsomatta)."""
        kat, kom, sel, es = r
        return (
            _KAT_EN.get(kat, kat),
            _KOM_EN.get(kom, kom),
            _SEL_EN.get(kom, sel),
            _ES_EN[kom] if kom in _ES_EN else self._esim_en(es),
        )

    def komento(self, r):
        """r = (kategoria, komento, selitys, esimerkki) suomeksi -> sama nykyisellä kielellä."""
        return r if self.nyt == "fi" else self.komento_en(r)

    @staticmethod
    def _esim_en(es):
        for fi, en in _PAIKKA:
            es = es.replace(fi, en)
        return es


KIELI = Kieli()
t = KIELI.t
