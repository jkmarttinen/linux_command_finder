"""Pakettihaun taustalogiikka (apt). Ei GTK-riippuvuuksia."""
import re
import subprocess

# Suomenkielinen hakusana (alku) -> englanninkieliset hakutermit (AND).
# Pakettien kuvaukset ovat englanniksi, joten suomi käännetään.
SANASTO = {
    "kuvankäs": ["image", "editor"],
    "kuvaeditor": ["image", "editor"],
    "kuvankatsel": ["image", "viewer"],
    "kuvien": ["image"],
    "kuvakaappa": ["screenshot"],
    "näyttökuva": ["screenshot"],
    "kuva": ["image"],
    "valokuva": ["photo"],
    "piirto": ["drawing"],
    "piirr": ["drawing"],
    "maalaus": ["paint"],
    "videoeditor": ["video", "editor"],
    "videoleik": ["video", "editor"],
    "videosoitin": ["video", "player"],
    "video": ["video"],
    "musiikkisoitin": ["music", "player"],
    "musiikki": ["music"],
    "äänityk": ["audio", "recorder"],
    "äänieditor": ["audio", "editor"],
    "ääni": ["audio"],
    "soitin": ["player"],
    "selain": ["web", "browser"],
    "sähköposti": ["email", "client"],
    "tekstieditor": ["text", "editor"],
    "tekstinkäs": ["word", "processor"],
    "editor": ["editor"],
    "muokkaus": ["editor"],
    "toimisto": ["office"],
    "taulukko": ["spreadsheet"],
    "esitys": ["presentation"],
    "pelit": ["game"],
    "peli": ["game"],
    "salasana": ["password", "manager"],
    "pakkaus": ["archive"],
    "pakkaa": ["archive"],
    "arkisto": ["archive"],
    "lataus": ["download"],
    "lataa": ["download"],
    "järjestelmän": ["system", "monitor"],
    "seuranta": ["monitor"],
    "tulostin": ["printer"],
    "tulostus": ["printing"],
    "skanneri": ["scanner"],
    "kääntäjä": ["compiler"],
    "ohjelmointi": ["programming"],
    "kehitys": ["development"],
    "tietokanta": ["database"],
    "levy": ["disk"],
    "varmuuskopio": ["backup"],
    "tiedostonhallin": ["file", "manager"],
    "terminaali": ["terminal"],
    "salaus": ["encryption"],
    "verkko": ["network"],
    "pilvi": ["cloud"],
    "fontti": ["font"],
    "kirjasin": ["font"],
    "kalenteri": ["calendar"],
    "muistiinpano": ["notes"],
    "sanakirja": ["dictionary"],
    "käännös": ["translation"],
    "näyttö": ["display"],
    "suomi": ["finnish"],
    "kieli": ["language"],
    "pdf": ["pdf"],
    "kamera": ["camera"],
    "kuvaus": ["capture"],
    "näytönjako": ["screen", "sharing"],
    "etäyhteys": ["remote", "desktop"],
    "etätyöpöytä": ["remote", "desktop"],
    "virus": ["antivirus"],
    "palomuuri": ["firewall"],
    "kirjanpito": ["accounting"],
    "kartta": ["map"],
    "sää": ["weather"],
    "kello": ["clock"],
    "laskin": ["calculator"],
    "luku": ["reader"],
    "kirja": ["ebook"],
    "ajuri": ["driver"],
    "emulaattori": ["emulator"],
    "virtuaali": ["virtual", "machine"],
    "tallennus": ["record"],
    "striimaus": ["streaming"],
    "lähetys": ["broadcast"],
    "podcast": ["podcast"],
    "torrent": ["torrent"],
    "lataaja": ["downloader"],
}


def puhdista(sana):
    return re.sub(r"[^\w.+\-]", "", sana, flags=re.UNICODE).lstrip("-")


def kaanna(sanat):
    """Palauttaa (termit, kaannetty_bool)."""
    termit, kaannetty = [], False
    avaimet = sorted(SANASTO, key=len, reverse=True)
    for s in sanat:
        s = puhdista(s.lower())
        if not s:
            continue
        for a in avaimet:
            if s.startswith(a) or (len(s) >= 5 and a.startswith(s)):
                termit.extend(SANASTO[a])
                kaannetty = True
                break
        else:
            termit.append(s)
    # poista duplikaatit järjestys säilyttäen
    return list(dict.fromkeys(termit)), kaannetty


def _apt_search(termit):
    if not termit:
        return []
    try:
        out = subprocess.run(
            ["apt-cache", "search", *termit],
            capture_output=True, text=True, timeout=20,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    tulos = []
    for rivi in out.splitlines():
        nimi, sep, kuv = rivi.partition(" - ")
        if sep and nimi:
            tulos.append((nimi.strip(), kuv.strip()))
    return tulos


def on_kirjasto(nimi):
    return nimi.startswith("lib") or nimi.endswith(
        ("-dev", "-dbg", "-dbgsym", "-doc", "-data", "-common", "-l10n", "-locale")
    ) or "-dev-" in nimi or nimi.startswith(("python3-", "golang-", "ruby-", "node-", "php-"))


def asennetut(nimet):
    """Palauttaa niiden pakettien joukon, jotka on asennettu."""
    nimet = list(nimet)
    if not nimet:
        return set()
    try:
        out = subprocess.run(
            ["dpkg-query", "-W", "-f=${binary:Package} ${db:Status-Abbrev}\n", *nimet],
            capture_output=True, text=True, timeout=20,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    joukko = set()
    for rivi in out.splitlines():
        osat = rivi.split()
        if len(osat) >= 2 and osat[1].startswith("ii"):
            joukko.add(osat[0].split(":")[0])
    return joukko


def hae(teksti, raja=1500):
    """Hakee paketteja. Palauttaa (rivit, termit, kaannetty).

    rivit = [(nimi, kuvaus, asennettu_bool, kirjasto_bool)], paras ensin.
    """
    sanat = teksti.split()
    termit, kaannetty = kaanna(sanat)
    tulos = _apt_search(termit)
    if not tulos and kaannetty:  # käännös ei tuottanut mitään -> kokeile alkuperäistä
        termit = [t for t in (puhdista(s.lower()) for s in sanat) if t]
        tulos = _apt_search(termit)
        kaannetty = False

    fraasi = " ".join(termit)

    def pisteet(rivi):
        n, kuv = rivi[0].lower(), rivi[1].lower()
        if n in termit:
            return 0
        if termit and n.startswith(termit[0]):
            return 1
        if len(termit) > 1 and fraasi in kuv:
            return 2
        if any(t in n for t in termit):
            return 3
        return 4

    tulos.sort(key=lambda r: (on_kirjasto(r[0]), pisteet(r), len(r[0]), r[0]))
    tulos = tulos[:raja]
    ase = asennetut(n for n, _ in tulos)
    rivit = [(n, k, n in ase, on_kirjasto(n)) for n, k in tulos]
    return rivit, termit, kaannetty


def tiedot(nimi):
    """apt-cache show -> dict: versio, koko, kotisivu, lyhyt, pitka."""
    try:
        out = subprocess.run(
            ["apt-cache", "show", nimi], capture_output=True, text=True, timeout=15
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    kappale = out.split("\n\n")[0]
    d, pitka, kuvauksessa = {}, [], False
    for rivi in kappale.splitlines():
        if rivi.startswith(" ") and kuvauksessa:
            t = rivi.strip()
            pitka.append("" if t == "." else t)
        elif ":" in rivi:
            k, _, v = rivi.partition(":")
            kuvauksessa = k.startswith("Description")
            if kuvauksessa:
                d["lyhyt"] = v.strip()
            else:
                d[k] = v.strip()
    d["pitka"] = "\n".join(pitka).strip()
    return d


def nimi_kelpaa(nimi):
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9+.\-]*", nimi))
