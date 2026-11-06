"""Tkinter desktop front end with an English / Chinese switch."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import queue
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .cad_export import export_dwg, export_dxf
from .coil_engine import CoilSpec, calculate, spiral_points
from .exports import export_csv, export_svg, read_project, write_project
from .i18n import Message, ValidationError, default_language, text, translate
from .params import PARAMETERS
from .resources import resource_path

BG = "#eef3f8"
NAVY = "#102d4b"
BLUE = "#087fad"
INK = "#20364c"
MUTED = "#6c8093"


class CoilApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.scale = max(1.0, self.winfo_fpixels("1i") / 96)
        self.language = default_language()
        self.geometry(f"{self.px(1260)}x{self.px(850)}")
        self.minsize(self.px(1100), self.px(760))
        self.configure(bg=BG)
        self._images = {}
        try:
            self.iconbitmap(default=str(resource_path("assets/icon.ico")))
            self._images["logo"] = tk.PhotoImage(file=str(resource_path("assets/icon_64.png")))
        except tk.TclError:
            pass
        self.option_add("*Font", ("Segoe UI", 10))
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.events = queue.Queue()
        self.generation = 0
        self.pending_job = None
        self.timer = None
        self.spec = None
        self.result = None
        self.closed = False
        self.current_path = None
        self.loading = False
        self.view_state = "waiting"
        self.status_key = ("status.ready", {})
        self.detail_key = ("notice.waiting", {})
        self.notice_messages = []
        self.vars = {key: tk.StringVar(value=f"{value:g}") for key, value in asdict(CoilSpec()).items()}
        self.status = tk.StringVar()
        self.notice = tk.StringVar()
        self.detail_text = tk.StringVar()
        self.result_vars = {}
        self._style()
        self._build()
        self._update_title()
        self._refresh_view()
        for var in self.vars.values():
            var.trace_add("write", self._changed)
        self.bind("<Control-s>", lambda _: self.save())
        self.bind("<Control-o>", lambda _: self.open())
        self.bind("<Return>", lambda _: self.recalculate())
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(80, self._poll)
        self.after(100, self.recalculate)

    # ------------------------------------------------------------------ helpers

    def tr(self, key, **params):
        return translate(self.language, key, **params)

    def px(self, value):
        """Convert a value designed for 96 DPI to the current display scale."""
        return int(round(value * self.scale))

    def _state_text(self, state):
        return self.tr(state[0], **state[1])

    def _set_status(self, key, **params):
        self.status_key = (key, params)
        self.status.set(self.tr(key, **params))

    def _set_notice(self, messages):
        self.notice_messages = list(messages)
        self._render_notice()

    def _render_notice(self):
        self.notice.set("\n".join(text(message, self.language) for message in self.notice_messages))

    def _error_text(self, error):
        message = getattr(error, "message", None)
        return text(message, self.language) if isinstance(message, Message) else str(error)

    def flag_image(self):
        """Flag of the language the switch button leads to."""
        target = "zh" if self.language == "en" else "en"
        suffix = "" if self.scale > 1.4 else "_small"
        path = str(resource_path(f"assets/flag_{target}{suffix}.png"))
        if path not in self._images:
            self._images[path] = tk.PhotoImage(file=path)
        return self._images[path]

    def _update_title(self):
        if self.current_path:
            self.title(self.tr("window.with_file", stem=Path(self.current_path).stem))
        else:
            self.title(self.tr("app.title"))

    def toggle_language(self):
        self.language = "zh" if self.language == "en" else "en"
        for child in self.winfo_children():
            child.destroy()
        self._build()
        self._update_title()
        self._refresh_view()

    # --------------------------------------------------------------------- view

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=(self.px(12), self.px(7)),
                        background="white", foreground=INK, borderwidth=0)
        style.map("TButton", background=[("active", "#dcecf6")])
        style.configure("Accent.TButton", background=BLUE, foreground="white")
        style.map("Accent.TButton", background=[("active", "#076d96")])
        style.configure("TEntry", padding=self.px(6), fieldbackground="#f5f8fc", bordercolor="#dae4ee",
                        lightcolor="#dae4ee", darkcolor="#dae4ee", foreground=INK)
        style.map("TEntry", bordercolor=[("focus", BLUE)])

    @staticmethod
    def label(parent, text=None, **kwargs):
        bg = kwargs.pop("bg", parent.cget("bg"))
        return tk.Label(parent, text=text, bg=bg, fg=kwargs.pop("fg", INK), **kwargs)

    def _build(self):
        header = tk.Frame(self, bg=NAVY, padx=self.px(26), pady=self.px(16))
        header.pack(fill="x")
        if "logo" in self._images:
            tk.Label(header, image=self._images["logo"], bg=NAVY).pack(side="left", padx=(0, self.px(14)))
        heading = tk.Frame(header, bg=NAVY)
        heading.pack(side="left")
        self.label(heading, self.tr("header.title"), fg="white",
                   font=("Segoe UI", 22, "bold")).pack(anchor="w")
        self.label(heading, self.tr("header.subtitle"), fg="#a9c6dc",
                   font=("Segoe UI", 10)).pack(anchor="w", pady=(self.px(5), 0))

        toolbar = tk.Frame(self, bg=BG, padx=self.px(20), pady=self.px(12))
        toolbar.pack(fill="x")
        for key, action in [("toolbar.open", self.open), ("toolbar.save", self.save),
                            ("toolbar.csv", self.csv), ("toolbar.svg", self.svg),
                            ("toolbar.dxf", self.dxf), ("toolbar.dwg", self.dwg)]:
            ttk.Button(toolbar, text=self.tr(key), command=action).pack(side="left", padx=(0, self.px(8)))
        ttk.Button(toolbar, image=self.flag_image(), text=self.tr("language.switch"), compound="left",
                   command=self.toggle_language).pack(side="right")
        ttk.Button(toolbar, text=self.tr("toolbar.about"),
                   command=self.about).pack(side="right", padx=self.px(8))
        ttk.Button(toolbar, text=self.tr("toolbar.reset"),
                   command=self.reset).pack(side="right", padx=self.px(8))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=self.px(20))
        body.columnconfigure(0, minsize=self.px(310))
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        sidebar = tk.Frame(body, bg="white", width=self.px(310), padx=self.px(18), pady=self.px(16))
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, self.px(16)))
        sidebar.pack_propagate(False)
        self.label(sidebar, self.tr("params.title"), font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.label(sidebar, self.tr("params.subtitle"), fg=MUTED,
                   font=("Segoe UI", 9)).pack(anchor="w", pady=(self.px(2), self.px(4)))
        for i, (key, title, unit) in enumerate(PARAMETERS):
            if i in (3, 6):
                tk.Frame(sidebar, bg="#e7edf3", height=1).pack(fill="x", pady=(self.px(8), self.px(7)))
            row = tk.Frame(sidebar, bg="white")
            row.pack(fill="x", pady=self.px(4))
            info = tk.Frame(row, bg="white")
            info.pack(side="left")
            self.label(info, self.tr(title), font=("Segoe UI", 10)).pack(anchor="w")
            self.label(row, unit, fg=MUTED, width=3).pack(side="right")
            entry = ttk.Entry(row, textvariable=self.vars[key], width=8, justify="right")
            entry.pack(side="right", padx=(self.px(6), self.px(4)))
        ttk.Button(sidebar, text=self.tr("params.calculate"), style="Accent.TButton",
                   command=self.recalculate).pack(fill="x", pady=(self.px(14), self.px(8)))
        self.label(sidebar, self.tr("params.hint"), fg=MUTED, justify="left",
                   wraplength=self.px(250), font=("Segoe UI", 9)).pack(anchor="w")

        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        preview = tk.Frame(right, bg="white", padx=self.px(14), pady=self.px(12))
        preview.pack(fill="both", expand=True)
        top = tk.Frame(preview, bg="white")
        top.pack(fill="x", pady=(0, self.px(10)))
        self.label(top, self.tr("preview.title"), font=("Segoe UI", 13, "bold")).pack(side="left")
        self.geometry_text = self.label(top, "", fg=MUTED, font=("Segoe UI", 10))
        self.geometry_text.pack(side="right")
        self.canvas = tk.Canvas(preview, bg="#10283f", highlightthickness=0, height=self.px(280))
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _: self.draw())
        self.label(preview, self.tr("preview.footer"), fg=MUTED,
                   font=("Segoe UI", 9)).pack(anchor="w", pady=(self.px(8), 0))

        cards = tk.Frame(right, bg=BG)
        cards.pack(fill="x", pady=(self.px(12), 0))
        for col, (key, title, unit, accent) in enumerate([
                ("equivalent", "card.equivalent", "µH", True),
                ("low", "card.low", "µH", False),
                ("resonance", "card.resonance", "MHz", False)]):
            cards.columnconfigure(col, weight=1, uniform="metrics")
            card = tk.Frame(cards, bg=BLUE if accent else "white", padx=self.px(16), pady=self.px(12))
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else self.px(8), 0))
            self.label(card, self.tr(title), fg="#d9f3ff" if accent else MUTED,
                       font=("Segoe UI", 9)).pack(anchor="w")
            var = self.result_vars.setdefault(key, tk.StringVar(value="—"))
            var.set("—")
            self.label(card, textvariable=var, fg="white" if accent else NAVY,
                       font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(self.px(3), 0))
            self.label(card, unit, fg="#d9f3ff" if accent else MUTED,
                       font=("Segoe UI", 9)).pack(anchor="w")

        details = tk.Frame(right, bg="white", padx=self.px(16), pady=self.px(10))
        details.pack(fill="x", pady=(self.px(12), 0))
        detail_label = self.label(details, textvariable=self.detail_text, justify="left", anchor="w",
                                  wraplength=self.px(750), font=("Segoe UI", 10))
        detail_label.pack(fill="x")
        notice_label = self.label(right, textvariable=self.notice, fg="#996422", justify="left", anchor="w",
                                  wraplength=self.px(750), font=("Segoe UI", 9))
        notice_label.pack(fill="x", pady=(self.px(8), 0))
        right.bind("<Configure>", lambda event: (
            detail_label.configure(wraplength=max(self.px(200), event.width - self.px(32))),
            notice_label.configure(wraplength=max(self.px(200), event.width))))

        footer = tk.Frame(self, bg=BG, padx=self.px(22), pady=self.px(10))
        footer.pack(fill="x")
        self.label(footer, textvariable=self.status, fg=MUTED, anchor="w",
                   font=("Segoe UI", 9)).pack(side="left")
        self.label(footer, self.tr("footer.note"), fg=MUTED,
                   font=("Segoe UI", 9)).pack(side="right")

    def _refresh_view(self):
        """Re-apply all language dependent state after the widgets are rebuilt."""
        self.status.set(self._state_text(self.status_key))
        self._render_notice()
        if self.view_state == "result" and self.result is not None and self.spec is not None:
            self._render_result()
        elif self.view_state == "error":
            self.draw_placeholder()
        else:
            self.detail_text.set(self._state_text(self.detail_key) if self.detail_key else "")
            self.canvas.delete("all")

    def _render_result(self):
        spec, result = self.spec, self.result
        for key, value in [("equivalent", result.equivalent_uh), ("low", result.low_frequency_uh),
                           ("resonance", result.resonance_mhz)]:
            self.result_vars[key].set(f"{value:.3f}")
        self.geometry_text.config(text=self.tr("preview.geometry", length=spec.length_mm,
                                               width=spec.width_mm, turns=spec.turns))
        self.detail_text.set(
            self.tr("detail.line1", segments=4 * int(spec.turns), length=result.trace_length_mm,
                    resistance=result.dc_resistance_ohm)
            + "\n" + self.tr("detail.line2", capacitance=result.tuning_pf))
        self._set_notice(result.warnings)
        self.draw()

    def draw_placeholder(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.px(30), self.px(35), text=self.tr("canvas.adjust"), anchor="nw",
                                fill="#b9cddd", font=("Segoe UI", 14))

    # ---------------------------------------------------------------- behaviour

    def _changed(self, *_):
        if self.loading:
            return
        self.generation += 1
        self.result = self.spec = None
        self.view_state = "waiting"
        self.detail_key = ("notice.changed", {})
        for var in self.result_vars.values():
            var.set("—")
        self.detail_text.set(self.tr("notice.changed"))
        self.geometry_text.config(text="")
        self.canvas.delete("all")
        self._set_notice([])
        self._set_status("status.editing")
        if self.timer:
            self.after_cancel(self.timer)
        self.timer = self.after(400, self.recalculate)

    def input_spec(self):
        try:
            values = {key: float(var.get().strip()) for key, var in self.vars.items()}
        except ValueError:
            raise ValidationError("error.number") from None
        spec = CoilSpec(**values)
        spec.validate()
        return CoilSpec(**{**values, "turns": int(values["turns"])})

    def recalculate(self):
        if self.timer:
            self.after_cancel(self.timer)
            self.timer = None
        self.generation += 1
        generation = self.generation
        self.result = self.spec = None
        try:
            spec = self.input_spec()
        except ValueError as error:
            self.view_state = "error"
            self._set_status("status.check")
            self._set_notice([getattr(error, "message", str(error))])
            self.draw_placeholder()
            return
        self._set_status("status.calculating")
        if self.pending_job:
            self.pending_job.cancel()
        job = self.pool.submit(calculate, spec)
        self.pending_job = job
        job.add_done_callback(lambda future: self.events.put((generation, spec, future)))

    def _poll(self):
        while True:
            try:
                generation, spec, future = self.events.get_nowait()
            except queue.Empty:
                break
            if generation != self.generation:
                continue
            try:
                result = future.result()
            except Exception as error:
                self.view_state = "waiting"
                self.detail_key = None
                self.detail_text.set("")
                self._set_notice([Message("notice.calculation_failed", error=self._error_text(error))])
                self._set_status("status.failed")
                continue
            self.spec, self.result = spec, result
            self.view_state = "result"
            self.detail_key = None
            self._set_status("status.done")
            self._render_result()
        if not self.closed:
            self.after(80, self._poll)

    def draw(self):
        c = self.canvas
        c.delete("all")
        if not self.spec:
            return
        p = self.spec
        cw, ch = c.winfo_width(), c.winfo_height()
        if cw < self.px(100) or ch < self.px(100):
            return
        grid = self.px(24)
        for x in range(0, cw, grid):
            c.create_line(x, 0, x, ch, fill="#19354d")
        for y in range(0, ch, grid):
            c.create_line(0, y, cw, y, fill="#19354d")
        scale = max(0.01, min((cw - self.px(140)) / p.length_mm,
                              (ch - self.px(105)) / p.width_mm))
        ox, oy = (cw - p.length_mm * scale) / 2, (ch - p.width_mm * scale) / 2
        xy = [(ox + x * scale, oy + y * scale) for x, y in spiral_points(p)]
        flattened = [value for point in xy for value in point]
        c.create_line(*flattened, fill="#684d2d", width=max(1, p.trace_mm * scale + self.px(3)),
                      capstyle="butt", joinstyle="miter")
        c.create_line(*flattened, fill="#efba64", width=max(1, p.trace_mm * scale),
                      capstyle="butt", joinstyle="miter")
        radius = self.px(4)
        for letter, point in zip(("A", "B"), (xy[0], xy[-1])):
            x, y = point
            c.create_oval(x - radius, y - radius, x + radius, y + radius,
                          fill="#67d8e6", outline="#10283f", width=2)
            c.create_text(x - self.px(12), y - self.px(13), text=letter, fill="#89e3ed",
                          font=("Segoe UI", 10, "bold"))
        x1, x2 = ox, ox + p.length_mm * scale
        y1, y2 = oy, oy + p.width_mm * scale
        c.create_line(x1, y1 - self.px(24), x2, y1 - self.px(24), fill="#7097b3", arrow="both")
        c.create_text((x1 + x2) / 2, y1 - self.px(37), text=f"{p.length_mm:g} mm",
                      fill="#c3d8e7", font=("Segoe UI", 10))
        c.create_line(x2 + self.px(25), y1, x2 + self.px(25), y2, fill="#7097b3", arrow="both")
        c.create_text(x2 + self.px(46), (y1 + y2) / 2, text=f"{p.width_mm:g}\nmm",
                      fill="#c3d8e7", font=("Segoe UI", 9))
        c.create_text(self.px(14), ch - self.px(14), anchor="sw", fill="#83a4bc",
                      text=self.tr("preview.scale", width=p.trace_mm, spacing=p.spacing_mm,
                                   copper=p.copper_um),
                      font=("Segoe UI", 9))

    def _require_result(self):
        if self.result is None:
            messagebox.showinfo(self.tr("dialog.waiting.title"), self.tr("dialog.waiting.text"),
                                parent=self)
            return False
        return True

    def _file_error(self, action):
        try:
            action()
        except (OSError, ValueError, TypeError) as error:
            self._set_status("status.file_error")
            messagebox.showerror(self.tr("dialog.error.title"), self._error_text(error), parent=self)

    # ------------------------------------------------------------------ actions

    def open(self):
        path = filedialog.askopenfilename(
            parent=self, title=self.tr("dialog.open.title"),
            filetypes=[(self.tr("dialog.open.type"), "*.json")])
        if not path:
            return

        def action():
            spec = read_project(path)
            self._set_spec(spec)
            self.current_path = path
            self._update_title()
        self._file_error(action)

    def save(self):
        if not self._require_result():
            return
        path = filedialog.asksaveasfilename(
            parent=self, title=self.tr("dialog.save.title"), defaultextension=".json",
            initialfile=Path(self.current_path).name if self.current_path else "coil_project.json",
            filetypes=[(self.tr("dialog.open.type"), "*.json")])
        if path:
            def action():
                write_project(path, self.spec)
                self.current_path = path
                self._update_title()
                self._set_status("status.saved", name=Path(path).name)
            self._file_error(action)

    def csv(self):
        if not self._require_result():
            return
        path = filedialog.asksaveasfilename(
            parent=self, title=self.tr("dialog.csv.title"), defaultextension=".csv",
            initialfile="coil_results.csv", filetypes=[(self.tr("dialog.csv.type"), "*.csv")])
        if path:
            def action():
                export_csv(path, self.spec, self.result)
                self._set_status("status.exported", name=Path(path).name)
            self._file_error(action)

    def svg(self):
        if not self._require_result():
            return
        path = filedialog.asksaveasfilename(
            parent=self, title=self.tr("dialog.svg.title"), defaultextension=".svg",
            initialfile="coil_preview.svg", filetypes=[(self.tr("dialog.svg.type"), "*.svg")])
        if path:
            def action():
                export_svg(path, self.spec)
                self._set_status("status.exported", name=Path(path).name)
            self._file_error(action)

    def dxf(self):
        self._export_cad("dxf", export_dxf)

    def dwg(self):
        self._export_cad("dwg", export_dwg)

    def _export_cad(self, extension, exporter):
        if not self._require_result():
            return
        name = extension.upper()
        path = filedialog.asksaveasfilename(
            parent=self, title=self.tr("dialog.cad.title", format=name),
            defaultextension=f".{extension}", initialfile=f"coil.{extension}",
            filetypes=[(self.tr("dialog.cad.type", format=name), f"*.{extension}")])
        if path:
            def action():
                self._set_status("status.cad_exporting", format=name)
                self.update_idletasks()
                exporter(path, self.spec)
                self._set_status("status.cad_exported", name=Path(path).name)
            self._file_error(action)

    def _set_spec(self, spec):
        self.loading = True
        try:
            for key, value in asdict(spec).items():
                self.vars[key].set(f"{value:g}")
        finally:
            self.loading = False
        self._changed()
        self.recalculate()

    def reset(self):
        self.current_path = None
        self._update_title()
        self._set_spec(CoilSpec())

    def about(self):
        messagebox.showinfo(self.tr("about.title"), self.tr("about.body"), parent=self)

    def close(self):
        self.closed = True
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.destroy()


def _enable_windows_dpi_awareness():
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("NFC.CoilCalculator.Desktop.1")
        windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError, OSError):
        pass


def main():
    _enable_windows_dpi_awareness()
    CoilApp().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
