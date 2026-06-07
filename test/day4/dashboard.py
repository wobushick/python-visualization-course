"""
Day4: pyecharts 可视化大屏
==========================
读取 Selenium 自动化测试结果 JSON，生成 4 张图表并整合为单一 HTML 大屏。

用法：
    python test/day4/dashboard.py
    → 输出 test/day4/output/dashboard.html
"""

import json
from collections import Counter
from pathlib import Path

from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Pie, Scatter

# ============================================================
# 配置
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 数据源优先级：day3/output/ → day2/selenium/
SOURCES = [
    PROJECT_ROOT / "test" / "day3" / "output" / "test_results.json",
    PROJECT_ROOT / "test" / "day2" / "selenium" / "test_results.json",
]

# 深色主题配色（与 Day2/Day3 一致）
COLORS = {
    "amber": "#c9a96e",
    "cyan": "#38bdf8",
    "green": "#22c55e",
    "red": "#ef4444",
    "purple": "#a78bfa",
    "pink": "#f472b6",
    "slate": "#64748b",
    "bg": "#0f172a",
    "text": "#e2e8f0",
}

CATEGORY_COLORS = {
    "正常场景": COLORS["green"],
    "用户名异常": COLORS["amber"],
    "密码异常": COLORS["red"],
    "安全测试": COLORS["purple"],
    "边界值": COLORS["cyan"],
}


# ============================================================
# 数据加载
# ============================================================

def load_results() -> list[dict]:
    """加载测试结果，按优先级查找数据源。"""
    for src in SOURCES:
        if src.exists():
            data = json.loads(src.read_text(encoding="utf-8"))
            return data.get("results", [])
    raise FileNotFoundError(
        "找不到测试结果文件。请先在 Day3 中执行一次自动化测试。\n"
        f"已检查: {[str(s) for s in SOURCES]}"
    )


# ============================================================
# 图表 1: 饼图 — 测试输入类型分布（玫瑰图）
# ============================================================

INPUT_TYPE_COLORS = {
    "正常合法": COLORS["green"],
    "安全攻击": COLORS["red"],
    "边界值": COLORS["cyan"],
    "空值输入": COLORS["pink"],
    "格式异常": COLORS["amber"],
}


def _classify_input(username: str, password: str) -> str:
    """根据用户名和密码特征分类输入类型。"""
    combined = (username + password).lower()
    attack_kw = ["' or ", "'; --", "drop ", "delete ", "union select", "1=1",
                 "<script", "javascript:", "onerror=", "onclick="]
    if any(kw in combined for kw in attack_kw):
        return "安全攻击"
    if not username or not password:
        return "空值输入"
    if len(username) < 3 or len(username) > 20 or len(password) < 8 or len(password) > 20:
        return "边界值"
    if not username.replace("_", "").isalnum():
        return "格式异常"
    if not (any(c.islower() for c in password) and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)):
        return "格式异常"
    return "正常合法"


def create_category_pie(results: list[dict]) -> Pie:
    """测试输入类型分布玫瑰图 — 按输入特征分类。"""
    input_types = Counter()
    for r in results:
        tp = _classify_input(r["inputs"]["username"], r["inputs"]["password"])
        input_types[tp] += 1

    data_pairs = [(tp, input_types[tp]) for tp in INPUT_TYPE_COLORS if tp in input_types]

    pie = (
        Pie(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .add(
            series_name="用例数",
            data_pair=data_pairs,
            radius=["20%", "70%"],
            rosetype="area",
            label_opts=opts.LabelOpts(
                formatter="{b}\n{d}%",
                color=COLORS["text"],
                font_size=12,
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_color=COLORS["bg"],
                border_width=2,
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="测试输入类型分布",
                subtitle="按 (用户名, 密码) 特征分类",
                title_textstyle_opts=opts.TextStyleOpts(color=COLORS["text"], font_size=18),
                subtitle_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
            ),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_right="5%",
                pos_top="center",
                textstyle_opts=opts.TextStyleOpts(color=COLORS["text"]),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{b}: {c} 条 ({d}%)"),
        )
        .set_colors(list(INPUT_TYPE_COLORS.values()))
    )
    return pie


# ============================================================
# 图表 2: 柱状图 — 各类别平均耗时
# ============================================================

def create_avg_duration_bar(results: list[dict]) -> Bar:
    """各类别平均执行耗时柱状图。"""
    # 按类别分组计算平均耗时
    cat_times: dict[str, list[int]] = {}
    for r in results:
        cat_times.setdefault(r["category"], []).append(r["duration_ms"])

    categories = list(CATEGORY_COLORS.keys())
    avgs = []
    for cat in categories:
        times = cat_times.get(cat, [])
        avgs.append(round(sum(times) / len(times)) if times else 0)

    bar = (
        Bar(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .add_xaxis(categories)
        .add_yaxis(
            "平均耗时 (ms)",
            avgs,
            label_opts=opts.LabelOpts(
                position="top",
                formatter="{c} ms",
                color=COLORS["text"],
                font_size=11,
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_radius=[6, 6, 0, 0],
                color=COLORS["cyan"],
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各类别平均执行耗时",
                subtitle="单位: 毫秒 (ms)",
                title_textstyle_opts=opts.TextStyleOpts(color=COLORS["text"], font_size=18),
                subtitle_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color=COLORS["text"], rotate=15),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=COLORS["slate"])),
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color=COLORS["text"]),
                splitline_opts=opts.SplitLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="rgba(255,255,255,0.06)")
                ),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", formatter="{b}: {c} ms"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return bar


# ============================================================
# 图表 3: 水平柱状图 — 验证结果分布
# ============================================================

# 归一化规则：从 actual_output 提取关键词映射到统一类别
VALIDATION_RULES = {
    "登录成功": ["登录成功"],
    "格式校验失败": ["只能包含字母、数字和下划线", "必须包含大小写字母和数字"],
    "长度校验失败": ["长度不能少于", "长度不能超过"],
    "空值校验失败": ["不能为空"],
    "账号不匹配": ["密码错误", "用户不存在"],
    "安全拦截": ["检测到非法输入", "安全攻击被拒绝"],
}

VALIDATION_COLORS = {
    "登录成功": COLORS["green"],
    "格式校验失败": COLORS["amber"],
    "长度校验失败": COLORS["cyan"],
    "空值校验失败": COLORS["pink"],
    "账号不匹配": COLORS["purple"],
    "安全拦截": COLORS["red"],
}


def _normalize_output(actual_output: str) -> str:
    """将 actual_output 归一化为校验规则类别。"""
    for rule_name, keywords in VALIDATION_RULES.items():
        for kw in keywords:
            if kw in actual_output:
                return rule_name
    return "其他"


def create_validation_bar(results: list[dict]) -> Bar:
    """验证结果分布水平柱状图 — 分析 actual_output 中的校验规则命中统计。"""
    # 统计归一化后的规则命中次数
    rule_counts: dict[str, int] = {}
    rule_details: dict[str, list[str]] = {}  # 每类的原文示例

    for r in results:
        rule = _normalize_output(r["actual_output"])
        rule_counts[rule] = rule_counts.get(rule, 0) + 1
        if rule not in rule_details:
            rule_details[rule] = []
        msg = r["actual_output"].split(":")[-1].split("，")[0].strip()[:20]
        if msg not in rule_details[rule]:
            rule_details[rule].append(msg)

    # 按数量降序排列
    sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
    categories = [r[0] for r in sorted_rules]
    counts = [r[1] for r in sorted_rules]
    colors = [VALIDATION_COLORS.get(c, COLORS["slate"]) for c in categories]

    bar = (
        Bar(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .add_xaxis(categories)
        .add_yaxis(
            "命中次数",
            counts,
            label_opts=opts.LabelOpts(
                position="right",
                formatter="{c} 条",
                color=COLORS["text"],
                font_size=12,
            ),
            itemstyle_opts=opts.ItemStyleOpts(border_radius=[0, 6, 6, 0]),
        )
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="验证结果分布",
                subtitle="按校验规则类型统计（从 actual_output 解析）",
                title_textstyle_opts=opts.TextStyleOpts(color=COLORS["text"], font_size=18),
                subtitle_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"], font_size=11),
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color=COLORS["text"]),
                splitline_opts=opts.SplitLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="rgba(255,255,255,0.06)")
                ),
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color=COLORS["text"], font_size=12),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=COLORS["slate"])),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter=lambda x: f"{x[0].name}: {x[0].value} 条<br>包含: {', '.join(rule_details.get(x[0].name, []))}" if x else "",
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    # 逐条设置颜色
    for i, color in enumerate(colors):
        bar.set_colors(color)
    bar.set_colors(colors)
    return bar


# ============================================================
# 图表 4: 散点图 — 输入特征空间
# ============================================================

def create_duration_scatter(results: list[dict]) -> Scatter:
    """输入特征空间散点图 — X=用户名长度, Y=密码长度, 颜色=输入类型, 大小=耗时。

    展示测试用例在「输入空间」中的分布：
    - 正常登录集中在左下区域（用户名短、密码适中）
    - 边界值分布在坐标轴极端位置
    - 安全攻击 payload 分散在不同区域
    """
    # 按输入类型分组
    type_points: dict[str, list[dict]] = {}
    for r in results:
        tp = _classify_input(r["inputs"]["username"], r["inputs"]["password"])
        type_points.setdefault(tp, []).append(r)

    scatter = (
        Scatter(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="输入特征空间分布",
                subtitle="X=用户名长度  Y=密码长度  ·  气泡大小=执行耗时",
                title_textstyle_opts=opts.TextStyleOpts(color=COLORS["text"], font_size=18),
                subtitle_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"], font_size=11),
            ),
            xaxis_opts=opts.AxisOpts(
                name="用户名长度",
                name_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
                axislabel_opts=opts.LabelOpts(color=COLORS["text"]),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=COLORS["slate"])),
                splitline_opts=opts.SplitLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="rgba(255,255,255,0.06)")
                ),
                min_=-1,
            ),
            yaxis_opts=opts.AxisOpts(
                name="密码长度",
                name_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
                axislabel_opts=opts.LabelOpts(color=COLORS["text"]),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=COLORS["slate"])),
                splitline_opts=opts.SplitLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="rgba(255,255,255,0.06)")
                ),
                min_=-1,
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{b}",
            ),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_right="5%",
                pos_top="center",
                textstyle_opts=opts.TextStyleOpts(color=COLORS["text"]),
            ),
        )
    )

    # 每输入类型一个 series
    for tp, color in INPUT_TYPE_COLORS.items():
        pts = type_points.get(tp, [])
        if pts:
            xs = [len(r["inputs"]["username"]) for r in pts]
            ys = [len(r["inputs"]["password"]) for r in pts]

            scatter.add_xaxis(xs)
            scatter.add_yaxis(
                tp,
                ys,
                symbol_size=12,
                symbol="circle",
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color=color, opacity=0.8),
            )

    return scatter


# ============================================================
# 组装大屏
# ============================================================

def build_dashboard(results: list[dict]) -> Page:
    """组装所有图表为一个 Page。"""
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        create_category_pie(results),
        create_avg_duration_bar(results),
        create_validation_bar(results),
        create_duration_scatter(results),
    )
    return page


def render_dashboard_embed(results: list[dict]) -> str:
    """生成可嵌入 Gradio 的 HTML 片段（自包含 echarts CDN + 图表）。"""
    dashboard = build_dashboard(results)

    # 渲染为完整 HTML 文件再提取内容
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        dashboard.render(f.name)
        tmp_path = f.name

    html = Path(tmp_path).read_text(encoding="utf-8")
    Path(tmp_path).unlink()  # 清理临时文件

    # 提取 <head> 中的 echarts CDN
    import re
    script_tags = re.findall(r'(<script[^>]*src="[^"]*echarts[^"]*"[^>]*></script>)', html)
    echarts_cdn = "\n".join(script_tags)

    # 提取 <body> 内容
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    body_content = body_match.group(1) if body_match else ""

    # 构建嵌入友好的 HTML（深色背景适配 Gradio）
    embed_html = f"""
    <div class="dashboard-embed" style="background:{COLORS['bg']};min-height:100vh;padding:20px;font-family:'Segoe UI',sans-serif;color:{COLORS['text']};">
        <style>
            .chart-block {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .chart-block .chart-container {{ border-radius:12px; overflow:hidden; }}
            @media (max-width: 900px) {{ .chart-block {{ grid-template-columns: 1fr; }} }}
        </style>
        <div class="chart-block">
            {body_content}
        </div>
    </div>
    {echarts_cdn}
    """
    return embed_html


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    print("📊 加载测试结果...")
    results = load_results()
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = total - passed
    print(f"   共 {total} 条 | ✅ {passed} 通过 | ❌ {failed} 失败")

    print("🎨 生成图表...")
    dashboard = build_dashboard(results)

    output_path = OUTPUT_DIR / "dashboard.html"
    dashboard.render(str(output_path))
    print(f"📁 可视化大屏已生成 → {output_path}")
