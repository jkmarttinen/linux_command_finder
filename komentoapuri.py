#!/usr/bin/env python3
"""Linux-komentoapuri: hakukelpoinen komentojen ohjekirja XFCE:lle.

Aja uudelleen (pikanäppäin / paneelin kuvake) niin ikkuna avautuu tai piilottuu.
"""
import os
import subprocess
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from komennot import KOMENNOT  # noqa: E402
import paketit  # noqa: E402
from kieli import KIELI, t  # noqa: E402

CSS = b"""
* { font-family: "JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace; }
window { background: #0f0f0f; }
.runko { background: #151515; border: 1px solid #333333; padding: 14px; }
entry placeholder, entry text placeholder { color: #6b6b6b; }
.logo { color: #d9701a; font-size: 16px; font-weight: bold; letter-spacing: 3px; }
.alalogo { color: #6b6b6b; font-size: 10px; letter-spacing: 2px; }
entry { background: #0f0f0f; color: #e6e6e6; font-size: 15px; padding: 9px 10px;
        border: 1px solid #333333; border-radius: 0; caret-color: #d9701a; box-shadow: none; }
entry:focus { border-color: #d9701a; }
entry selection { background: #d9701a; color: #0f0f0f; }
flowbox { background: transparent; }
flowboxchild { padding: 0; background: transparent; }
button.kat { background: #1c1c1c; color: #8a8a8a; border: 1px solid #2c2c2c; border-radius: 0;
             padding: 3px 10px; font-size: 11px; margin: 2px; box-shadow: none; text-shadow: none; background-image: none; }
button.kat:hover { color: #d9701a; border-color: #d9701a; }
button.kat:checked { color: #0f0f0f; background: #d9701a; border-color: #d9701a; font-weight: bold; }
list { background: #151515; }
list row { border-left: 3px solid transparent; border-bottom: 1px solid #222222; }
list row:hover { background: #1c1c1c; }
list row:selected { background: #222222; border-left: 3px solid #d9701a; }
.listakehys { border: 1px solid #2c2c2c; }
.kategoria { color: #6b6b6b; font-size: 10px; letter-spacing: 1px; }
.komento { color: #e8832a; font-weight: bold; font-size: 13px; }
.selitys { color: #bdbdbd; font-size: 12px; }
.otsikko { color: #e8832a; font-weight: bold; font-size: 18px; }
.vihje { color: #6b6b6b; font-size: 10px; letter-spacing: 1px; }
.esimerkki { color: #e0e0e0; font-size: 12px; padding: 8px; background: #0f0f0f;
             border: 1px solid #2c2c2c; border-left: 3px solid #d9701a; }
.paneeli { border-left: 1px solid #2c2c2c; padding-left: 4px; }
button.kopioi { background: transparent; color: #d9701a; border: 1px solid #d9701a; border-radius: 0;
                padding: 7px 12px; font-weight: bold; letter-spacing: 1px; background-image: none; text-shadow: none; box-shadow: none; }
button.kopioi:hover { background: #d9701a; color: #0f0f0f; }
.status { color: #8aa66a; font-size: 11px; }
.asennettu { color: #8aa66a; font-size: 10px; letter-spacing: 1px; }
button.toissijainen { background: transparent; color: #bdbdbd; border: 1px solid #444444; border-radius: 0;
                      padding: 6px 12px; letter-spacing: 1px; background-image: none; text-shadow: none; box-shadow: none; }
button.toissijainen:hover { border-color: #d9701a; color: #d9701a; }
tooltip { background: #1c1c1c; border: 1px solid #333333; border-radius: 0; }
tooltip label { color: #e6e6e6; font-size: 11px; }
scrollbar { background: transparent; border: none; }
scrollbar slider { background: #444444; border-radius: 0; min-width: 4px; min-height: 30px; border: none; }
scrollbar.vertical { min-width: 6px; }
scrollbar slider:hover { background: #d9701a; }
"""




def norm(s):
    return s.lower()


def luo_label(teksti="", luokka=None, wrap=False, rivi=30, selectable=False, ellipsize=False):
    w = Gtk.Label(label=teksti, xalign=0)
    if wrap:
        w.set_line_wrap(True)
        w.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        w.set_max_width_chars(rivi)
    if ellipsize:
        w.set_ellipsize(Pango.EllipsizeMode.END)
        w.set_max_width_chars(rivi)
    w.set_selectable(selectable)
    if luokka:
        w.get_style_context().add_class(luokka)
    return w


class Rivi(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()
        self.data = data  # aina suomenkielinen alkuperäinen (kategoria-avain suodatukseen)
        kat, kom, sel, _ = KIELI.komento(data)
        # haku toimii molemmilla kielillä
        self.haku = norm(" ".join(data) + " " + " ".join(KIELI.komento_en(data)))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)
        ylä = Gtk.Box(spacing=8)
        c = Gtk.Label(label=kat, xalign=1)
        c.get_style_context().add_class("kategoria")
        ylä.pack_start(luo_label(kom, "komento", ellipsize=True, rivi=28), True, True, 0)
        ylä.pack_end(c, False, False, 0)
        box.pack_start(ylä, False, False, 0)
        box.pack_start(luo_label(sel, "selitys", ellipsize=True, rivi=10), False, False, 0)
        self.add(box)


class PakettiRivi(Gtk.ListBoxRow):
    def __init__(self, nimi, kuvaus, asennettu, kirjasto):
        super().__init__()
        self.nimi, self.kuvaus, self.asennettu, self.kirjasto = nimi, kuvaus, asennettu, kirjasto
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(10)
        box.set_margin_end(10)
        ylä = Gtk.Box(spacing=8)
        ylä.pack_start(luo_label(nimi, "komento", ellipsize=True, rivi=28), True, True, 0)
        if asennettu:
            tag = Gtk.Label(label=t("asennettu_merkki"), xalign=1)
            tag.get_style_context().add_class("asennettu")
            ylä.pack_end(tag, False, False, 0)
        box.pack_start(ylä, False, False, 0)
        box.pack_start(luo_label(kuvaus, "selitys", ellipsize=True, rivi=10), False, False, 0)
        self.add(box)


class Ikkuna(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title=t("ikkunan_otsikko"))
        self.set_default_size(860, 640)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_icon_name("utilities-terminal")
        self.kategoria = None
        self.tila = "komennot"
        self.haku_token = 0
        self.haku_ajastin = None
        self.tiedot_valimuisti = {}
        self.paketti_tulokset = []

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.get_style_context().add_class("runko")
        wrap = Gtk.Box()
        wrap.set_border_width(8)
        wrap.pack_start(root, True, True, 0)
        self.add(wrap)

        # --- otsikko + tilanvaihto ---
        kop = Gtk.Box(spacing=10)
        self.logo = luo_label(t("logo"), "logo")
        kop.pack_start(self.logo, False, False, 0)
        self.nappi_kom = Gtk.RadioButton.new_with_label_from_widget(None, t("tila_komennot"))
        self.nappi_pak = Gtk.RadioButton.new_with_label_from_widget(self.nappi_kom, t("tila_paketit"))
        for b in (self.nappi_kom, self.nappi_pak):
            b.set_mode(False)
            b.set_focus_on_click(False)
            b.get_style_context().add_class("kat")
        self.nappi_kom.connect("toggled", self.tila_painike, "komennot")
        self.nappi_pak.connect("toggled", self.tila_painike, "paketit")
        tilabox = Gtk.Box(spacing=0)
        tilabox.set_margin_start(14)
        tilabox.pack_start(self.nappi_kom, False, False, 0)
        tilabox.pack_start(self.nappi_pak, False, False, 0)
        kop.pack_start(tilabox, False, False, 0)
        # kielenvaihto FI | EN
        self.nappi_fi = Gtk.RadioButton.new_with_label_from_widget(None, "FI")
        self.nappi_en = Gtk.RadioButton.new_with_label_from_widget(self.nappi_fi, "EN")
        kielibox = Gtk.Box(spacing=0)
        for b, k in ((self.nappi_fi, "fi"), (self.nappi_en, "en")):
            b.set_mode(False)
            b.set_focus_on_click(False)
            b.set_tooltip_text(t("kieli_vihje"))
            b.get_style_context().add_class("kat")
            kielibox.pack_start(b, False, False, 0)
        (self.nappi_en if KIELI.nyt == "en" else self.nappi_fi).set_active(True)
        self.nappi_fi.connect("toggled", self.kieli_painike, "fi")
        self.nappi_en.connect("toggled", self.kieli_painike, "en")
        kop.pack_end(kielibox, False, False, 0)
        root.pack_start(kop, False, False, 0)

        self.haku = Gtk.SearchEntry()
        self.haku.set_placeholder_text(t("haku_komennot"))
        self.haku.connect("search-changed", self.haku_muuttui)
        self.haku.connect("activate", lambda *_: self.kopioi())
        self.haku.connect("key-press-event", self.haku_nappi)
        root.pack_start(self.haku, False, False, 0)

        # --- suodatinrivi (kategoriat / pakettisuodattimet) ---
        self.ylastack = Gtk.Stack()
        self.ylastack.set_vhomogeneous(False)
        self.katbox = Gtk.FlowBox()
        self.katbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.katbox.set_homogeneous(False)
        self.katbox.set_max_children_per_line(30)
        self.katbox.set_row_spacing(0)
        self.katbox.set_column_spacing(0)
        self.katnapit = {}
        kategoriat = [None]
        for r in KOMENNOT:
            if r[0] not in kategoriat:
                kategoriat.append(r[0])
        for kat in kategoriat:
            b = Gtk.ToggleButton(label=(KIELI.kategoria(kat) if kat else t("kaikki")).upper())
            b.get_style_context().add_class("kat")
            b.set_focus_on_click(False)
            b.connect("toggled", self.kat_valittu, kat)
            self.katbox.add(b)
            self.katnapit[kat] = b
        self.ylastack.add_named(self.katbox, "komennot")

        pakbox = Gtk.Box(spacing=0)
        self.piilota_lib = Gtk.ToggleButton(label=t("piilota_kirjastot"))
        self.vain_asennetut = Gtk.ToggleButton(label=t("vain_asennetut"))
        self.piilota_lib.set_active(True)
        for b in (self.piilota_lib, self.vain_asennetut):
            b.get_style_context().add_class("kat")
            b.set_focus_on_click(False)
            b.connect("toggled", lambda *_: self.piirra_paketit())
            pakbox.pack_start(b, False, False, 0)
        self.paketti_tilarivi = luo_label("", "vihje")
        self.paketti_tilarivi.set_margin_start(10)
        pakbox.pack_start(self.paketti_tilarivi, False, False, 0)
        self.ylastack.add_named(pakbox, "paketit")
        root.pack_start(self.ylastack, False, False, 0)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        root.pack_start(paned, True, True, 0)

        # --- vasen: listat ---
        self.vasen = Gtk.Stack()
        self.lista = Gtk.ListBox()
        self.lista.set_activate_on_single_click(False)
        self.lista.set_filter_func(self.suodata)
        self.lista.connect("row-selected", self.valittu)
        self.lista.connect("row-activated", lambda *_: self.kopioi())
        for r in KOMENNOT:
            self.lista.add(Rivi(r))
        self.vasen.add_named(self.kehys(self.lista), "komennot")

        self.plista = Gtk.ListBox()
        self.plista.set_activate_on_single_click(False)
        self.plista.connect("row-selected", self.paketti_valittu)
        self.plista.connect("row-activated", lambda *_: self.kopioi())
        self.vasen.add_named(self.kehys(self.plista), "paketit")
        paned.pack1(self.vasen, True, False)

        # --- oikea: tietopaneelit ---
        self.oikea = Gtk.Stack()
        self.oikea.add_named(self.rakenna_komentotiedot(), "komennot")
        self.oikea.add_named(self.rakenna_pakettitiedot(), "paketit")
        paned.pack2(self.oikea, True, False)

        self.vihje = luo_label("", "vihje")
        root.pack_start(self.vihje, False, False, 0)

        self.katnapit[None].handler_block_by_func(self.kat_valittu)
        self.katnapit[None].set_active(True)
        self.katnapit[None].handler_unblock_by_func(self.kat_valittu)
        self.connect("key-press-event", self.nappi_painettu)
        self.connect("delete-event", self.piilota)
        self.paivita()
        self.aseta_tila("komennot")
        self.haku.grab_focus()

    # --- rakennusapurit ---
    def kehys(self, lista):
        sw = Gtk.ScrolledWindow()
        sw.get_style_context().add_class("listakehys")
        sw.set_overlay_scrolling(False)
        sw.set_size_request(380, -1)
        sw.add(lista)
        return sw

    def rakenna_komentotiedot(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        info.get_style_context().add_class("paneeli")
        info.set_margin_start(12)
        info.set_margin_end(4)
        self.i_kom = luo_label("", "otsikko", wrap=True, selectable=True)
        self.i_sel = luo_label("", "selitys", wrap=True, selectable=True)
        self.l_es = l_es = luo_label(t("esimerkki"), "vihje")
        self.i_es = luo_label("", "esimerkki", wrap=True, selectable=True)
        self.nappi = Gtk.Button(label=t("kopioi_leikepoydalle"))
        self.nappi.get_style_context().add_class("kopioi")
        self.nappi.connect("clicked", lambda *_: self.kopioi())
        self.status = luo_label("", "status", wrap=True)
        for w in (self.i_kom, self.i_sel, l_es, self.i_es, self.nappi, self.status):
            info.pack_start(w, False, False, 0)
        return info

    def rakenna_pakettitiedot(self):
        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        info.get_style_context().add_class("paneeli")
        info.set_margin_start(12)
        info.set_margin_end(4)
        self.p_nimi = luo_label("", "otsikko", wrap=True, selectable=True)
        self.p_tila = luo_label("", "vihje")
        self.p_lyhyt = luo_label("", "selitys", wrap=True, selectable=True)
        self.p_pitka = luo_label("", "vihje", wrap=True, selectable=True)
        self.p_pitka.set_valign(Gtk.Align.START)
        sw = Gtk.ScrolledWindow()
        sw.set_overlay_scrolling(False)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_min_content_height(80)
        sw.add(self.p_pitka)
        self.p_meta = luo_label("", "vihje", wrap=True, selectable=True)
        self.p_komento = luo_label("", "esimerkki", wrap=True, selectable=True)
        self.p_asenna = Gtk.Button(label=t("asenna_terminaalissa"))
        self.p_asenna.get_style_context().add_class("kopioi")
        self.p_asenna.connect("clicked", lambda *_: self.suorita_terminaalissa())
        self.p_kopioi = Gtk.Button(label=t("kopioi_komento"))
        self.p_kopioi.get_style_context().add_class("toissijainen")
        self.p_kopioi.connect("clicked", lambda *_: self.kopioi())
        self.p_status = luo_label("", "status", wrap=True)
        for w in (self.p_nimi, self.p_tila, self.p_lyhyt):
            info.pack_start(w, False, False, 0)
        info.pack_start(sw, True, True, 0)
        for w in (self.p_meta, self.p_komento, self.p_asenna, self.p_kopioi, self.p_status):
            info.pack_start(w, False, False, 0)
        return info

    # --- kieli ---
    def kieli_painike(self, nappi, kieli):
        if nappi.get_active() and kieli != KIELI.nyt:
            KIELI.aseta(kieli)
            self.paivita_kieli()

    def paivita_kieli(self):
        """Päivittää kaikki tekstit nykyiselle kielelle."""
        self.set_title(t("ikkunan_otsikko"))
        self.logo.set_text(t("logo"))
        self.nappi_kom.set_label(t("tila_komennot"))
        self.nappi_pak.set_label(t("tila_paketit"))
        for b in (self.nappi_fi, self.nappi_en):
            b.set_tooltip_text(t("kieli_vihje"))
        for kat, b in self.katnapit.items():
            b.set_label((KIELI.kategoria(kat) if kat else t("kaikki")).upper())
        self.piilota_lib.set_label(t("piilota_kirjastot"))
        self.vain_asennetut.set_label(t("vain_asennetut"))
        self.l_es.set_text(t("esimerkki"))
        self.nappi.set_label(t("kopioi_leikepoydalle"))
        self.p_kopioi.set_label(t("kopioi_komento"))
        self.tyhjenna_status()
        # komentolista uudelleen (rivien tekstit ovat kielikohtaisia)
        valittu_kom = self.lista.get_selected_row()
        valittu_avain = valittu_kom.data[1] if valittu_kom else None
        for r in self.lista.get_children():
            self.lista.remove(r)
        for r in KOMENNOT:
            self.lista.add(Rivi(r))
        self.lista.show_all()
        self.paivita()
        if valittu_avain:
            for r in self.lista.get_children():
                if r.data[1] == valittu_avain and self.suodata(r):
                    self.lista.select_row(r)
                    break
        self.aseta_tila(self.tila)
        if self.tila == "paketit":
            self.piirra_paketit()

    # --- tilat ---
    def tila_painike(self, nappi, tila):
        if nappi.get_active():
            self.aseta_tila(tila)

    def aseta_tila(self, tila):
        self.tila = tila
        for b, tl in ((self.nappi_kom, "komennot"), (self.nappi_pak, "paketit")):
            if b.get_active() != (tl == tila):
                b.set_active(tl == tila)
        self.ylastack.set_visible_child_name(tila)
        self.vasen.set_visible_child_name(tila)
        self.oikea.set_visible_child_name(tila)
        if tila == "komennot":
            self.haku.set_placeholder_text(t("haku_komennot"))
            self.vihje.set_text(t("vihje_komennot"))
            self.paivita()
        else:
            self.haku.set_placeholder_text(t("haku_paketit"))
            self.vihje.set_text(t("vihje_paketit"))
            self.haku_muuttui()

    def paketti_infotyhja(self, otsikko, teksti=""):
        self.p_nimi.set_text(otsikko)
        self.p_tila.set_text("")
        self.p_lyhyt.set_text(teksti)
        self.p_pitka.set_text("")
        self.p_meta.set_text("")
        self.p_komento.set_text("")
        self.p_status.set_text("")
        self.p_asenna.set_sensitive(False)
        self.p_kopioi.set_sensitive(False)

    # --- haun ohjaus ---
    def haku_muuttui(self, *_):
        if self.tila == "komennot":
            self.paivita()
            return
        if self.haku_ajastin:
            GLib.source_remove(self.haku_ajastin)
            self.haku_ajastin = None
        if not self.haku.get_text().strip():
            self.haku_token += 1
            self.paketti_tulokset = []
            self.piirra_paketit()
            return
        self.haku_ajastin = GLib.timeout_add(300, self.kaynnista_pakettihaku)

    def kaynnista_pakettihaku(self):
        self.haku_ajastin = None
        teksti = self.haku.get_text().strip()
        self.haku_token += 1
        token = self.haku_token
        self.paketti_tilarivi.set_text(t("haetaan"))

        def tyo():
            try:
                tulos = paketit.hae(teksti)
            except Exception as e:  # noqa: BLE001
                tulos = ([], [], False)
                print("pakettihaku epäonnistui:", e, file=sys.stderr)
            GLib.idle_add(self.pakettihaku_valmis, token, tulos)

        threading.Thread(target=tyo, daemon=True).start()
        return False

    def pakettihaku_valmis(self, token, tulos):
        if token != self.haku_token:
            return False
        rivit, termit, kaannetty = tulos
        self.paketti_tulokset = rivit
        self.paketti_termit = (termit, kaannetty)
        self.piirra_paketit()
        return False

    def piirra_paketit(self):
        for r in self.plista.get_children():
            self.plista.remove(r)
        teksti = self.haku.get_text().strip()
        if not teksti:
            self.paketti_tilarivi.set_text("")
            self.paketti_infotyhja(
                t("hae_sovelluksia"),
                t("hae_ohje"),
            )
            return
        lib = self.piilota_lib.get_active()
        vain = self.vain_asennetut.get_active()
        nayta = [
            r for r in self.paketti_tulokset
            if not (lib and r[3]) and not (vain and not r[2])
        ]
        piilossa = len(self.paketti_tulokset) - len(nayta)
        for n, k, a, kirj in nayta[:200]:
            self.plista.add(PakettiRivi(n, k, a, kirj))
        self.plista.show_all()
        termit, kaannetty = getattr(self, "paketti_termit", ([], False))
        osat = [t("tulosta", n=len(nayta))]
        if kaannetty and termit:
            osat.append(t("haku_termit", termit=" ".join(termit)))
        if piilossa:
            osat.append(t("piilotettu", n=piilossa))
        self.paketti_tilarivi.set_text(" · ".join(osat))
        if nayta:
            self.plista.select_row(self.plista.get_row_at_index(0))
        else:
            self.paketti_infotyhja(
                t("pak_ei_tuloksia"),
                t("pak_ei_tuloksia_ohje") + (t("pak_kirjastot_piilossa") if lib and piilossa else ""),
            )

    # --- pakettien tiedot ---
    def paketti_valittu(self, _l, rivi):
        if rivi is None:
            return
        self.p_nimi.set_text(rivi.nimi)
        self.p_lyhyt.set_text(rivi.kuvaus)
        self.p_pitka.set_text(t("haetaan_tietoja"))
        self.p_meta.set_text("")
        self.p_status.set_text("")
        self.p_tila.set_text(t("asennettu_tila") if rivi.asennettu else t("ei_asennettu_tila"))
        cmd = self.paketin_komento(rivi)
        self.p_komento.set_text(cmd)
        self.p_asenna.set_label(t("poista_terminaalissa") if rivi.asennettu else t("asenna_terminaalissa"))
        self.p_asenna.set_sensitive(paketit.nimi_kelpaa(rivi.nimi))
        self.p_kopioi.set_sensitive(True)
        nimi = rivi.nimi
        if nimi in self.tiedot_valimuisti:
            self.nayta_tiedot(nimi, self.tiedot_valimuisti[nimi])
            return

        def tyo():
            d = paketit.tiedot(nimi)
            GLib.idle_add(self.tiedot_valmis, nimi, d)

        threading.Thread(target=tyo, daemon=True).start()

    def tiedot_valmis(self, nimi, d):
        self.tiedot_valimuisti[nimi] = d
        self.nayta_tiedot(nimi, d)
        return False

    def nayta_tiedot(self, nimi, d):
        rivi = self.plista.get_selected_row()
        if rivi is None or rivi.nimi != nimi:
            return
        self.p_pitka.set_text(d.get("pitka") or t("ei_pitkaa"))
        osat = []
        if d.get("Version"):
            osat.append(t("versio", v=d["Version"]))
        try:
            osat.append(t("koko", mt=int(d["Installed-Size"]) / 1024))
        except (KeyError, ValueError):
            pass
        if d.get("Homepage"):
            osat.append(d["Homepage"])
        self.p_meta.set_text(" · ".join(osat))

    def paketin_komento(self, rivi):
        return f"sudo apt {'remove' if rivi.asennettu else 'install'} {rivi.nimi}"

    def suorita_terminaalissa(self):
        rivi = self.plista.get_selected_row()
        if not rivi or not paketit.nimi_kelpaa(rivi.nimi):
            return
        cmd = self.paketin_komento(rivi)
        skripti = f'{cmd}; echo; read -rp "{t("terminaali_valmis")}"'
        try:
            subprocess.Popen(["xfce4-terminal", "--title=Komentoapuri", "-x", "bash", "-c", skripti])
            self.hide()
        except OSError as e:
            self.p_status.set_text(t("terminaali_virhe", e=e))

    # --- komentotila ---
    def suodata(self, rivi):
        if self.kategoria and rivi.data[0] != self.kategoria:
            return False
        sanat = norm(self.haku.get_text()).split()
        return all(s in rivi.haku for s in sanat)

    def kat_valittu(self, nappi, kat):
        if not nappi.get_active():
            if self.kategoria == kat:
                nappi.handler_block_by_func(self.kat_valittu)
                nappi.set_active(True)
                nappi.handler_unblock_by_func(self.kat_valittu)
            return
        self.kategoria = kat
        for k, b in self.katnapit.items():
            if k != kat and b.get_active():
                b.handler_block_by_func(self.kat_valittu)
                b.set_active(False)
                b.handler_unblock_by_func(self.kat_valittu)
        self.paivita()

    def paivita(self, *_):
        self.lista.invalidate_filter()
        for r in self.lista.get_children():
            if r.get_child_visible() and self.suodata(r):
                self.lista.select_row(r)
                break
        else:
            self.lista.unselect_all()
            self.valittu(self.lista, None)

    def valittu(self, _lista, rivi):
        self.status.set_text("")
        if rivi is None:
            self.i_kom.set_text(t("ei_tuloksia"))
            self.i_sel.set_text(t("kokeile_toista"))
            self.i_es.set_text("")
            return
        _, kom, sel, es = KIELI.komento(rivi.data)
        self.i_kom.set_text(kom)
        self.i_sel.set_text(sel)
        self.i_es.set_text(es)

    def ilmoita_kopioitu(self, label, teksti):
        label.set_text(t("kopioitu", teksti=teksti))
        if getattr(self, "_status_ajastin", None):
            GLib.source_remove(self._status_ajastin)
        self._status_ajastin = GLib.timeout_add_seconds(3, self._status_pois)

    def _status_pois(self):
        self._status_ajastin = None
        self.tyhjenna_status()
        return False

    def leikepoydalle(self, teksti):
        # Ctrl+V käyttää CLIPBOARDia, hiiren keskinappi PRIMARY-valintaa -> asetetaan molemmat
        for valinta in (Gdk.SELECTION_CLIPBOARD, Gdk.SELECTION_PRIMARY):
            Gtk.Clipboard.get(valinta).set_text(teksti, -1)
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).store()

    def kopioi(self):
        if self.tila == "paketit":
            rivi = self.plista.get_selected_row()
            if not rivi:
                return
            teksti = self.paketin_komento(rivi)
            self.leikepoydalle(teksti)
            self.ilmoita_kopioitu(self.p_status, teksti)
            return
        rivi = self.lista.get_selected_row()
        if not rivi:
            return
        teksti = KIELI.komento(rivi.data)[3].split("   #")[0].strip()
        self.leikepoydalle(teksti)
        self.ilmoita_kopioitu(self.status, teksti)

    def liiku(self, suunta):
        if self.tila == "paketit":
            lista = self.plista
            rivit = lista.get_children()
        else:
            lista = self.lista
            rivit = [r for r in lista.get_children() if self.suodata(r)]
        if not rivit:
            return
        nyt = lista.get_selected_row()
        i = rivit.index(nyt) + suunta if nyt in rivit else 0
        i = max(0, min(len(rivit) - 1, i))
        lista.select_row(rivit[i])
        rivit[i].grab_focus()
        self.haku.grab_focus()
        self.haku.set_position(-1)

    def haku_nappi(self, _w, e):
        if e.keyval == Gdk.KEY_Down:
            self.liiku(1)
            return True
        if e.keyval == Gdk.KEY_Up:
            self.liiku(-1)
            return True
        if e.keyval in (Gdk.KEY_Tab, Gdk.KEY_ISO_Left_Tab):
            self.aseta_tila("paketit" if self.tila == "komennot" else "komennot")
            return True
        return False

    def nappi_painettu(self, _w, e):
        if e.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        if not self.haku.is_focus() and e.string and e.string.isprintable() and not (
            e.state & Gdk.ModifierType.CONTROL_MASK
        ):
            self.haku.grab_focus()
        return False

    def piilota(self, *_):
        self.hide()
        return True

    def tyhjenna_status(self):
        self.status.set_text("")
        self.p_status.set_text("")

    def nayta(self):
        self.tyhjenna_status()
        self.show_all()
        self.present_with_time(Gdk.CURRENT_TIME)
        self.haku.grab_focus()
        self.haku.select_region(0, -1)


class Sovellus(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.jkmarttinen.LinuxCommandFinder")
        self.ikkuna = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def do_activate(self):
        if self.ikkuna is None:
            self.ikkuna = Ikkuna(self)
            self.ikkuna.nayta()
            if os.environ.get("KOMENTOAPURI_TILA") == "paketit":  # testaukseen
                self.ikkuna.aseta_tila("paketit")
                self.ikkuna.haku.set_text(os.environ.get("KOMENTOAPURI_HAKU", ""))
        elif self.ikkuna.is_visible() and self.ikkuna.is_active():
            self.ikkuna.hide()  # toggle: sama pikanäppäin piilottaa
        else:
            self.ikkuna.nayta()


if __name__ == "__main__":
    sys.exit(Sovellus().run(sys.argv))
