import io
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import reader_check  # noqa: E402


def check(text: str, suffix: str = ".html", **limits) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"doc{suffix}"
        path.write_text(text, encoding="utf-8")
        return reader_check.analyse(
            reader_check.parse(path),
            limits.get("para", 100),
            limits.get("cell", 40),
            limits.get("opening", 200),
            limits.get("run", 14),
        )


class HtmlVisibilityTests(unittest.TestCase):
    def test_folded_hidden_script_and_nav_text_is_excluded_but_summary_stays(self):
        result = check(
            "<nav>目录 一 二 三</nav><button>切换明暗</button>"
            "<h1>结论标题</h1><p>正文一句。</p>"
            "<details><summary>展开明细</summary><p>折叠里的长段落</p></details>"
            "<p hidden>隐藏文字</p><script>var x = '脚本';</script>"
        )
        text = " ".join(result["opening"])
        self.assertIn("结论标题", text)
        self.assertIn("展开明细", text)
        for absent in ("折叠里的长段落", "隐藏文字", "脚本", "目录", "切换明暗"):
            self.assertNotIn(absent, text)

    def test_div_cards_are_separate_blocks_not_one_merged_paragraph(self):
        cards = "".join(f"<div class='chip'>组件{i}：一句说明这个组件在流程里做什么事情</div>" for i in range(6))
        result = check(f"<h2>组件地图</h2><div>{cards}</div>")
        self.assertEqual(result["long_paragraphs"], [])

    def test_text_before_first_figure_counts_only_what_precedes_it(self):
        result = check("<h1>标题</h1><p>四个汉字</p><svg><text>图里的字</text></svg><p>之后的正文</p>")
        self.assertEqual(result["text_before_first_figure"], 6)
        self.assertIn("[figure] 图里的字", result["opening"])


class DefectDetectionTests(unittest.TestCase):
    def test_long_paragraph_and_cell_use_cjk_width_with_ascii_counting_half(self):
        result = check(
            "<p>" + "字" * 101 + "</p><p>" + "a" * 150 + "</p>"
            "<table><tr><th>项</th></tr><tr><td>" + "格" * 41 + "</td></tr></table>"
        )
        self.assertEqual([w for w, _ in result["long_paragraphs"]], [101])
        self.assertEqual([w for w, _ in result["long_cells"]], [41])

    def test_near_constant_column_is_reported_and_varied_one_is_not(self):
        rows = "".join(f"<tr><td>组件{i}</td><td>改造</td></tr>" for i in range(5))
        result = check(f"<table><tr><th>名称</th><th>状态</th></tr>{rows}</table>")
        self.assertEqual([c[0] for c in result["near_constant_columns"]], ["状态"])

    def test_repeated_numbers_and_shared_runs_across_blocks(self):
        claim = "配置中心兼着三份不该它干的活导致保存很慢"
        result = check(f"<p>{claim}，一次 70.6 秒。</p><p>再说一遍：{claim}。</p><li>保存 70.6 秒</li>")
        self.assertIn(("70.6秒", 2), result["repeated_numbers"])
        self.assertTrue(any(claim in run for run, _ in result["shared_runs"]))

    def test_terms_are_listed_by_first_appearance_and_prose_code_is_ignored(self):
        result = check("<p>先讲清楚。</p><p>Agent 读 <code>USER_NAMESPACE</code>，<code>-</code>，<code>中文示意片段</code></p>")
        names = [t[0] for t in result["terms"]]
        self.assertIn("USER_NAMESPACE", names)
        self.assertNotIn("-", names)
        self.assertNotIn("中文示意片段", names)
        self.assertEqual(dict((t[0], t[2]) for t in result["terms"])["USER_NAMESPACE"], 1)


class MarkdownTests(unittest.TestCase):
    def test_fences_and_details_are_skipped_tables_and_mermaid_are_read(self):
        md = (
            "# 标题\n\n开头一句。\n\n```mermaid\nflowchart LR\n  A-->B\n```\n\n"
            "```bash\necho 代码里的很长很长的内容\n```\n\n"
            "<details><summary>明细</summary>\n\n折叠内容\n\n</details>\n\n"
            "| 名称 | 状态 |\n| --- | --- |\n" + "".join(f"| 项{i} | 同时 |\n" for i in range(5))
        )
        result = check(md, suffix=".md")
        self.assertEqual(result["outline"], ["标题"])
        self.assertEqual(result["text_before_first_figure"], 7)
        self.assertEqual([c[0] for c in result["near_constant_columns"]], ["状态"])
        flat = " ".join(result["opening"])
        self.assertNotIn("代码里", flat)
        self.assertNotIn("折叠内容", flat)


class CliTests(unittest.TestCase):
    def test_missing_file_exits_2_and_report_renders(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(reader_check.main(["/nonexistent/file.html"]), 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.html"
            path.write_text("<h1>标题</h1><p>一句。</p>", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(reader_check.main([str(path)]), 0)
            self.assertIn("Outline", out.getvalue())


if __name__ == "__main__":
    unittest.main()
