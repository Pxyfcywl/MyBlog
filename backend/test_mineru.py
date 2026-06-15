"""MinerU + 审查功能测试脚本

用法：
    python test_mineru.py <pdf文件路径>

示例：
    python test_mineru.py C:/Users/ACER/Desktop/test.pdf
"""
import sys
import os

# 确保能导入 app 模块
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.services.mineru import MinerUClient
from app.services.reviewer import match_keywords, validate_dates


def main():
    if len(sys.argv) < 2:
        print("用法: python test_mineru.py <pdf文件路径>")
        print("示例: python test_mineru.py C:/Users/ACER/Desktop/test.pdf")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)

    file_size = os.path.getsize(file_path) / 1024 / 1024
    print(f"📄 文件: {file_path}")
    print(f"📦 大小: {file_size:.1f} MB")
    print()

    # ── Step 1: 提交到 MinerU ──
    print("=" * 50)
    print("Step 1: 提交文件到 MinerU...")
    print("=" * 50)

    client = MinerUClient()

    try:
        batch_id = client.submit_batch([file_path])
        print(f"✅ 提交成功! batch_id: {batch_id}")
    except Exception as e:
        print(f"❌ 提交失败: {e}")
        sys.exit(1)

    # ── Step 2: 轮询等待结果 ──
    print()
    print("=" * 50)
    print("Step 2: 等待解析完成...")
    print("=" * 50)

    import time
    start = time.time()

    while True:
        state, files = client.poll_batch(batch_id)
        elapsed = int(time.time() - start)

        for f in files:
            if f.state == "running":
                progress = f.extract_progress
                total = progress.get("total_pages", "?")
                done = progress.get("extracted_pages", "?")
                print(f"  ⏳ [{elapsed}s] 解析中... {done}/{total} 页")
            elif f.state == "pending":
                print(f"  ⏳ [{elapsed}s] 排队中...")
            elif f.state == "done":
                print(f"  ✅ [{elapsed}s] 解析完成!")
            elif f.state == "failed":
                print(f"  ❌ [{elapsed}s] 解析失败: {f.err_msg}")
                sys.exit(1)

        if state == "done":
            break

        time.sleep(3)

    # ── Step 3: 获取 Markdown ──
    print()
    print("=" * 50)
    print("Step 3: 下载 Markdown 内容...")
    print("=" * 50)

    result = files[0]
    md_url = result.full_zip_url.rsplit("/", 1)[0] + "/full.md"
    print(f"📎 Markdown URL: {md_url}")

    try:
        markdown = client.fetch_markdown(md_url)
        print(f"✅ 下载成功! 内容长度: {len(markdown)} 字符")
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        sys.exit(1)

    # 显示前 500 字符预览
    print()
    print("=" * 50)
    print("Markdown 内容预览（前 500 字符）:")
    print("=" * 50)
    print(markdown[:500])
    print("..." if len(markdown) > 500 else "")

    # ── Step 4: 测试审查功能 ──
    print()
    print("=" * 50)
    print("Step 4: 测试审查功能...")
    print("=" * 50)

    # 关键词测试
    test_keywords = ["合同", "甲方", "乙方", "日期", "签字"]
    print(f"\n🔍 关键词匹配 (关键词: {test_keywords}):")
    matches = match_keywords(markdown, test_keywords)
    if matches:
        for m in matches[:10]:  # 最多显示 10 个
            print(f"  [{m.keyword}] 行 {m.line_number}: {m.context[:80]}...")
        if len(matches) > 10:
            print(f"  ... 共 {len(matches)} 个匹配")
    else:
        print("  未找到匹配的关键词")

    # 日期测试
    print(f"\n📅 日期校验 (范围: 2020-01-01 ~ 2025-12-31):")
    date_findings = validate_dates(markdown, "2020-01-01", "2025-12-31")
    if date_findings:
        for d in date_findings[:10]:
            status = "✅" if d.in_range else "❌ 超出范围"
            print(f"  {d.date_str} → {d.parsed} {status} (行 {d.line_number})")
        if len(date_findings) > 10:
            print(f"  ... 共 {len(date_findings)} 个日期")
    else:
        print("  未找到日期")

    # ── 完成 ──
    print()
    print("=" * 50)
    print("🎉 全部测试完成!")
    print("=" * 50)
    print(f"\nbatch_id: {batch_id}")
    print(f"你可以用这个 batch_id 调用 POST /api/tools/review 进行审查")


if __name__ == "__main__":
    main()
