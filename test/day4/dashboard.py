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
from pyecharts.charts import Bar, Line, Page, Pie

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
# 图表 1: 饼图 — 测试用例分类分布（玫瑰图）
# ============================================================

def create_category_pie(results: list[dict]) -> Pie:
    """测试用例分类分布玫瑰图。"""
    category_counts = Counter(r["category"] for r in results)
    data_pairs = [
        (cat, count) for cat, count in category_counts.items()
    ]

    pie = (
        Pie(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .add(
            series_name="用例数",
            data_pair=data_pairs,
            radius=["20%", "70%"],              # 玫瑰图
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
                title="测试用例分类分布",
                subtitle="按测试场景类别统计",
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
        .set_colors(list(CATEGORY_COLORS.values()))
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}\n{d}%"),
        )
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
# 图表 3: 柱状图 — 各类别用例数统计
# ============================================================

def create_count_bar(results: list[dict]) -> Bar:
    """各类别测试用例数量柱状图。"""
    category_counts = Counter(r["category"] for r in results)
    categories = list(CATEGORY_COLORS.keys())
    counts = [category_counts.get(cat, 0) for cat in categories]
    bar_colors = [CATEGORY_COLORS[cat] for cat in categories]

    bar = (
        Bar(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .add_xaxis(categories)
        .add_yaxis(
            "用例数",
            counts,
            label_opts=opts.LabelOpts(
                position="top",
                formatter="{c} 条",
                color=COLORS["text"],
                font_size=12,
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_radius=[6, 6, 0, 0],
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各类别用例数量统计",
                subtitle=f"共 {sum(counts)} 条测试用例",
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
            tooltip_opts=opts.TooltipOpts(trigger="axis", formatter="{b}: {c} 条"),
            legend_opts=opts.LegendOpts(is_show=False),
        )
        .set_colors([COLORS["amber"]])
    )
    return bar


# ============================================================
# 图表 4: 折线图 — 各用例执行耗时
# ============================================================

def create_duration_line(results: list[dict]) -> Line:
    """各测试用例执行耗时折线图（按类别着色）。"""
    avg_ms = round(sum(r["duration_ms"] for r in results) / len(results))

    # 按类别分组绘制折线
    cat_data: dict[str, list[tuple[int, int]]] = {}
    for i, r in enumerate(results, 1):
        cat_data.setdefault(r["category"], []).append((i, r["duration_ms"]))

    line = (
        Line(init_opts=opts.InitOpts(bg_color=COLORS["bg"], width="600px", height="400px"))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各测试用例执行耗时",
                subtitle=f"平均耗时: {avg_ms} ms",
                title_textstyle_opts=opts.TextStyleOpts(color=COLORS["text"], font_size=18),
                subtitle_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
            ),
            xaxis_opts=opts.AxisOpts(
                name="用例序号",
                name_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
                axislabel_opts=opts.LabelOpts(color=COLORS["text"]),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color=COLORS["slate"])),
            ),
            yaxis_opts=opts.AxisOpts(
                name="耗时 (ms)",
                name_textstyle_opts=opts.TextStyleOpts(color=COLORS["slate"]),
                axislabel_opts=opts.LabelOpts(color=COLORS["text"]),
                splitline_opts=opts.SplitLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="rgba(255,255,255,0.06)")
                ),
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_right="5%",
                pos_top="center",
                textstyle_opts=opts.TextStyleOpts(color=COLORS["text"]),
            ),
        )
    )

    for cat, color in CATEGORY_COLORS.items():
        if cat in cat_data:
            xs = [p[0] for p in cat_data[cat]]
            ys = [p[1] for p in cat_data[cat]]
            line.add_xaxis(xs)
            line.add_yaxis(
                cat,
                ys,
                is_smooth=True,
                symbol="circle",
                symbol_size=6,
                linestyle_opts=opts.LineStyleOpts(color=color, width=2),
                itemstyle_opts=opts.ItemStyleOpts(color=color),
                label_opts=opts.LabelOpts(is_show=False),
            )

    # 添加平均线 marker
    line.add_yaxis(
        f"平均线 ({avg_ms}ms)",
        [avg_ms] * len(results),
        linestyle_opts=opts.LineStyleOpts(
            color=COLORS["slate"], type_="dashed", width=1.5, opacity=0.6
        ),
        symbol="none",
        label_opts=opts.LabelOpts(is_show=False),
    )

    return line


# ============================================================
# 组装大屏
# ============================================================

def build_dashboard(results: list[dict]) -> Page:
    """组装所有图表为一个 Page。"""
    page = Page(layout=Page.SimplePageLayout)
    page.add(
        create_category_pie(results),
        create_avg_duration_bar(results),
        create_count_bar(results),
        create_duration_line(results),
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
