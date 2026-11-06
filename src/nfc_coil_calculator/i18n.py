"""Window translations.

Source code, documentation, exported files and log output stay English; only the
Tkinter interface can switch language at run time.
"""
import os

MESSAGES = {
    "en": {
        "app.title": "NFC Coil Calculator",
        "window.with_file": "{stem} — NFC Coil Calculator",
        "header.title": "NFC  /  COIL CALCULATOR",
        "header.subtitle": "Rectangular PCB spiral antenna     ·     13.56 MHz     ·     "
                           "Offline desktop app",
        "toolbar.open": "Open project",
        "toolbar.save": "Save project",
        "toolbar.csv": "Export CSV",
        "toolbar.svg": "Export SVG",
        "toolbar.dxf": "Export DXF",
        "toolbar.dwg": "Export DWG",
        "toolbar.about": "About the model",
        "toolbar.reset": "Reset defaults",
        "language.switch": "中文",
        "params.title": "Design parameters",
        "params.subtitle": "Single layer · vertical segmentation · 1-15 turns",
        "params.calculate": "Calculate / update preview",
        "params.hint": "Recalculates automatically after edits; press Enter to update now.\n"
                       "Dimensions are copper outer edges; spacing is edge to edge.",
        "param.turns": "Turns",
        "param.length_mm": "Antenna length",
        "param.width_mm": "Antenna width",
        "param.trace_mm": "Conductor width",
        "param.spacing_mm": "Conductor spacing",
        "param.copper_um": "Copper thickness",
        "param.substrate_mm": "Substrate thickness",
        "param.epsilon_r": "Relative permittivity",
        "preview.title": "Coil preview",
        "preview.geometry": "{length:g} × {width:g} mm  /  {turns} turns",
        "preview.footer": "Copper centerline drawn to scale   ·   A / B are illustrative terminals"
                          "   ·   SVG export is a preview only",
        "preview.scale": "w {width:g} mm    s {spacing:g} mm    Cu {copper:g} µm",
        "card.equivalent": "Equivalent inductance @ 13.56 MHz",
        "card.low": "Low-frequency inductance",
        "card.resonance": "Model self-resonant frequency",
        "detail.line1": "Vertical segmentation  {segments} segments        Model conductor length  "
                        "{length:.1f} mm       DC resistance ≈ {resistance:.3f} Ω",
        "detail.line2": "Ideal total tuning capacitance @ 13.56 MHz ≈ {capacitance:.2f} pF "
                        "(includes the IC and other external parallel capacitance)",
        "canvas.adjust": "Adjust the parameters on the left",
        "footer.note": "Independent Python implementation of the published ST eDesignSuite formulas",
        "notice.waiting": "Waiting for a calculation…",
        "notice.changed": "Parameters changed, waiting for the calculation…",
        "notice.calculation_failed": "Calculation did not finish: {error}",
        "status.ready": "Ready",
        "status.editing": "Editing…",
        "status.calculating": "Calculating segment inductances and frequency correction…",
        "status.check": "Check the parameters",
        "status.failed": "Calculation failed, adjust the parameters",
        "status.done": "Calculated · everything runs on this machine",
        "status.file_error": "File operation did not finish",
        "status.saved": "Saved: {name}",
        "status.exported": "Exported: {name}",
        "status.cad_exporting": "Exporting {format}…",
        "status.cad_exported": "Exported: {name} · 1:1 mm · COPPER outline",
        "dialog.open.title": "Open coil project",
        "dialog.open.type": "Coil project",
        "dialog.save.title": "Save coil project",
        "dialog.csv.title": "Export parameters and results",
        "dialog.csv.type": "CSV table",
        "dialog.svg.title": "Export coil preview",
        "dialog.svg.type": "SVG image",
        "dialog.cad.title": "Export {format} · 1:1 mm copper outline",
        "dialog.cad.type": "CAD {format}",
        "dialog.waiting.title": "Waiting for a calculation",
        "dialog.waiting.text": "Enter valid parameters and wait for the calculation to finish.",
        "dialog.error.title": "File operation failed",
        "about.title": "About the model",
        "about.body": "Rectangular, single layer PCB spiral coil with vertical segmentation.\n\n"
                      "Ported from the published ST eDesignSuite script: Grover segment self "
                      "inductance, mutual inductance of parallel segments, parasitic capacitance, "
                      "self-resonance scan and the 13.56 MHz correction.\n\n"
                      "Substrate thickness behaves as on the source site: it can be entered and "
                      "saved, but the single layer formula does not use it.\n"
                      "Self-resonance is a model estimate; resonances below the scan start cannot be "
                      "resolved reliably.\n\n"
                      "DC resistance uses the 20 °C copper resistivity. The tuning capacitance is the "
                      "ideal total external parallel capacitance, so subtract the IC and other "
                      "external capacitance.\n"
                      "The preview and SVG only show the shape and are not manufacturing data.\n\n"
                      "DXF and DWG exports carry a closed copper outline at 1:1 in millimetres; the "
                      "CENTERLINE and REFERENCE layers start hidden.\n"
                      "DWG is AutoCAD 2000 format, converted offline with the bundled LibreDWG "
                      "binary.\n"
                      "CAD files contain no pads, vias or terminals; add them and check design rules "
                      "before fabrication.\n\n"
                      "This is an independent Python implementation, not ST software. Sources and "
                      "limits are documented in docs/ALGORITHM.md.",
        "error.number": "Enter a complete number for every field, using a dot as the decimal "
                        "separator.",
        "error.field_finite": "{field} must be a finite number.",
        "error.turns": "Turns must be an integer between 1 and 15.",
        "error.trace": "Conductor width must be between 0.15 and 6 mm.",
        "error.spacing": "Conductor spacing must be between 0.15 and 2 mm.",
        "error.thickness": "Copper thickness must exceed 0.1 µm and substrate thickness must exceed "
                           "0.1 mm.",
        "error.permittivity": "Relative permittivity (epsilon_r) must be between 2 and 6.",
        "error.minimum_dimension": "The outer length and width must both exceed {minimum:g} mm for "
                                   "these turns, width and spacing.",
        "error.numeric_range": "Dimensions exceed the numeric range of this tool.",
        "error.no_inductance": "These parameters do not yield a valid positive equivalent inductance "
                               "at 13.56 MHz.",
        "warning.accuracy_over_15": "Source model note: the equivalent inductance error may exceed "
                                    "15% for this design.",
        "warning.accuracy_15": "Source model note: the equivalent inductance error is about 15% for "
                               "this design.",
        "warning.accuracy_10": "Source model note: the equivalent inductance error is about 10% for "
                               "this design.",
        "warning.scan_fallback": "The self-resonance scan found no minimum; the source model's "
                                 "scan-limit fallback is shown and is not a measured self-resonant "
                                 "frequency.",
        "warning.negative_segments": "Some segment inductances are not positive; verify this geometry "
                                     "with an EM simulation or measurement.",
        "error.zero_segment": "The coil centerline contains a zero-length segment; adjust the "
                              "parameters.",
        "error.doubling_back": "The coil doubles back on itself, so no valid copper outline can be "
                               "built.",
        "error.cad_template": "The CAD template is incomplete; reinstall the application.",
        "error.converter_missing": "The bundled DWG converter is missing; use the full distribution "
                                   "(see docs/BUILD.md).",
        "error.builder_missing": "The DWG geometry builder is missing; use the full distribution.",
        "error.dwg_geometry": "DWG geometry generation failed: {detail}",
        "error.dwg_timeout": "DWG conversion timed out; retry or export DXF instead.",
        "error.dwg_start": "Could not start the DWG converter: {error}",
        "error.dwg_failed": "DWG conversion failed. {detail}",
        "error.dwg_signature": "The converter did not produce a valid AutoCAD 2000 DWG file.",
        "error.project_large": "Project file is too large; choose a JSON project saved by this tool.",
        "error.project_format": "Unsupported project format.",
        "error.project_parameters": "Project parameters are missing or contain unknown fields.",
    },
    "zh": {
        "app.title": "NFC 线圈计算器",
        "window.with_file": "{stem} · NFC 线圈计算器",
        "header.title": "NFC  /  线圈计算器",
        "header.subtitle": "矩形 PCB 螺旋天线     ·     13.56 MHz     ·     离线桌面版",
        "toolbar.open": "打开项目",
        "toolbar.save": "保存项目",
        "toolbar.csv": "导出 CSV",
        "toolbar.svg": "导出 SVG",
        "toolbar.dxf": "导出 DXF",
        "toolbar.dwg": "导出 DWG",
        "toolbar.about": "计算说明",
        "toolbar.reset": "恢复默认",
        "language.switch": "English",
        "params.title": "设计参数",
        "params.subtitle": "单层 · 垂直分段 · 1～15 匝",
        "params.calculate": "计算 / 更新预览",
        "params.hint": "修改参数后自动计算；按 Enter 立即更新。\n"
                       "尺寸均为铜箔外边界，间距为边缘间距。",
        "param.turns": "匝数",
        "param.length_mm": "天线外长",
        "param.width_mm": "天线外宽",
        "param.trace_mm": "导体宽度",
        "param.spacing_mm": "导体间距",
        "param.copper_um": "铜厚",
        "param.substrate_mm": "基板厚度",
        "param.epsilon_r": "相对介电常数",
        "preview.title": "线圈预览",
        "preview.geometry": "{length:g} × {width:g} mm  /  {turns} 匝",
        "preview.footer": "铜箔中心线按比例绘制   ·   A / B 为示意端点   ·   SVG 为预览图",
        "preview.scale": "线宽 {width:g} mm    间距 {spacing:g} mm    铜厚 {copper:g} µm",
        "card.equivalent": "等效电感 @ 13.56 MHz",
        "card.low": "低频电感",
        "card.resonance": "模型自谐振频率",
        "detail.line1": "垂直分段  {segments} 段       模型导体总长  {length:.1f} mm       "
                        "直流电阻 ≈ {resistance:.3f} Ω",
        "detail.line2": "13.56 MHz 理想总调谐电容 ≈ {capacitance:.2f} pF"
                        "（包含芯片及其它外部并联电容）",
        "canvas.adjust": "请调整左侧参数",
        "footer.note": "独立 Python 实现 · 参考 ST eDesignSuite 公开算法",
        "notice.waiting": "等待计算…",
        "notice.changed": "参数已更改，等待计算…",
        "notice.calculation_failed": "计算未完成：{error}",
        "status.ready": "就绪",
        "status.editing": "正在编辑…",
        "status.calculating": "正在计算分段电感与频率修正…",
        "status.check": "请检查参数",
        "status.failed": "计算失败，请调整参数",
        "status.done": "计算完成 · 所有计算均在本机运行",
        "status.file_error": "文件操作未完成",
        "status.saved": "已保存：{name}",
        "status.exported": "已导出：{name}",
        "status.cad_exporting": "正在导出 {format}…",
        "status.cad_exported": "已导出：{name} · 1:1 mm · COPPER 铜箔轮廓",
        "dialog.open.title": "打开线圈项目",
        "dialog.open.type": "线圈项目",
        "dialog.save.title": "保存线圈项目",
        "dialog.csv.title": "导出参数与计算结果",
        "dialog.csv.type": "CSV 表格",
        "dialog.svg.title": "导出线圈预览图",
        "dialog.svg.type": "SVG 矢量图",
        "dialog.cad.title": "导出 {format} · 1:1 mm 铜箔轮廓",
        "dialog.cad.type": "CAD {format}",
        "dialog.waiting.title": "等待计算",
        "dialog.waiting.text": "请先输入有效参数并等待计算完成。",
        "dialog.error.title": "文件操作失败",
        "about.title": "计算说明",
        "about.body": "矩形、单层 PCB 螺旋线圈，垂直分段。\n\n"
                      "按 ST eDesignSuite 公开脚本移植：Grover 分段自感、平行段互感、寄生电容、"
                      "自谐振扫描及 13.56 MHz 修正。\n\n"
                      "基板厚度与原站一致：可输入及保存，但未参与该单层模型的公式。\n"
                      "自谐振为原模型估计；低于扫描起点的谐振不能可靠识别。\n\n"
                      "直流电阻使用 20°C 铜电阻率；调谐电容为理想总外部并联电容，"
                      "应扣除芯片及其它外部并联电容。\n"
                      "预览和 SVG 仅表示形状，不能直接用于 PCB 制造。\n\n"
                      "DXF / DWG 按 1:1 mm 输出闭合铜箔轮廓；CENTERLINE 和 REFERENCE 层默认隐藏。\n"
                      "DWG 为 AutoCAD 2000 格式，通过随应用提供的 LibreDWG 离线转换。\n"
                      "CAD 不含焊盘、过孔和引线，PCB 制板前请补充并检查设计规则。\n\n"
                      "这是独立 Python 实现，不是 ST 官方软件。详细来源与限制见 docs/ALGORITHM.md。",
        "error.number": "请完整输入数值，小数点使用英文句点。",
        "error.field_finite": "{field} 必须是有限数值。",
        "error.turns": "匝数必须是 1～15 的整数。",
        "error.trace": "导体宽度须在 0.15～6 mm 之间。",
        "error.spacing": "导体间距须在 0.15～2 mm 之间。",
        "error.thickness": "铜厚须大于 0.1 µm，基板厚度须大于 0.1 mm。",
        "error.permittivity": "相对介电常数 εr 须在 2～6 之间。",
        "error.minimum_dimension": "当前匝数、线宽和间距要求外长及外宽均大于 {minimum:g} mm。",
        "error.numeric_range": "尺寸超出本地工具的数值计算范围。",
        "error.no_inductance": "该参数组合在 13.56 MHz 下无法得到有效的正等效电感。",
        "warning.accuracy_over_15": "原站模型提示：此参数组合的等效电感估计误差可能超过 15%。",
        "warning.accuracy_15": "原站模型提示：此参数组合的等效电感估计误差约 15%。",
        "warning.accuracy_10": "原站模型提示：此参数组合的等效电感估计误差约 10%。",
        "warning.scan_fallback": "自谐振扫描未找到峰值；显示的是原站的扫描上限回退值，"
                                 "不能视为实测自谐振频率。",
        "warning.negative_segments": "部分分段等效电感非正；此几何组合应通过电磁仿真或实测复核。",
        "error.zero_segment": "线圈中心线包含零长度段，请调整参数。",
        "error.doubling_back": "线圈出现折返，无法形成有效的铜箔轮廓。",
        "error.cad_template": "CAD 文档模板不完整，请重新安装应用。",
        "error.converter_missing": "缺少随应用提供的 DWG 转换器，请使用完整发行版"
                                   "（见 docs/BUILD.md）。",
        "error.builder_missing": "缺少 DWG 几何生成器，请使用完整发行版。",
        "error.dwg_geometry": "DWG 几何生成失败：{detail}",
        "error.dwg_timeout": "DWG 转换超时，请重试或先导出 DXF。",
        "error.dwg_start": "无法启动 DWG 转换器：{error}",
        "error.dwg_failed": "DWG 转换失败。{detail}",
        "error.dwg_signature": "转换器没有生成有效的 AutoCAD 2000 DWG 文件。",
        "error.project_large": "项目文件过大，请选择本工具保存的 JSON 项目。",
        "error.project_format": "项目格式不受支持。",
        "error.project_parameters": "项目参数缺失或包含未知字段。",
    },
}

LANGUAGES = ("en", "zh")


def format_message(language, key, params=None):
    """Format ``key`` for ``language``, falling back to English and then to the key."""
    template = MESSAGES.get(language, {}).get(key) or MESSAGES["en"].get(key, key)
    if not params:
        return template
    try:
        return template.format(**params)
    except (KeyError, IndexError, ValueError):
        return template


def translate(language, key, **params):
    return format_message(language, key, params)


class Message(str):
    """A string that also remembers the message id, so it can be shown in any language."""

    def __new__(cls, key, **params):
        message = super().__new__(cls, format_message("en", key, params))
        message.key = key
        message.params = params
        return message


class ValidationError(ValueError):
    """Input or export error carrying a translatable message."""

    def __init__(self, key, **params):
        self.message = Message(key, **params)
        super().__init__(str(self.message))


def text(value, language):
    """Render a :class:`Message` in ``language``; other values are converted with ``str``."""
    if isinstance(value, Message):
        return format_message(language, value.key, value.params)
    return str(value)


def default_language():
    """Pick Chinese on Chinese Windows (or a zh_* locale), English otherwise."""
    if os.name == "nt":
        try:
            import ctypes
            if (ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF) == 0x04:
                return "zh"
            return "en"
        except (AttributeError, OSError):
            pass
    for variable in ("LC_ALL", "LC_MESSAGES", "LANG"):
        if os.environ.get(variable, "").lower().startswith("zh"):
            return "zh"
    return "en"
