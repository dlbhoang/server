import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(prompt, model="gpt-4", temperature=0.7):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

def generate_title(main_keyword, sub_keywords):
    joined = ", ".join(sub_keywords) if sub_keywords else ""
    prompt = f"Hãy tạo 3 tiêu đề hấp dẫn cho bài viết với từ khoá chính: '{main_keyword}' và từ khoá phụ: {joined}. Viết tiêu đề ngắn gọn, thu hút."
    return call_openai(prompt)

def generate_outline(main_keyword):
    prompt = f"Hãy tạo một dàn ý chi tiết cho bài viết với từ khoá chính: '{main_keyword}'. Dàn ý gồm các mục lớn và nhỏ nếu cần, không cần đánh số."
    return call_openai(prompt)

def generate_article(data: dict, user):
    word_count = int(data.get("word_count", 1000))  # Mặc định 1000 từ
    REQUIRED_CREDITS = word_count

    if user.credits < REQUIRED_CREDITS:
        raise Exception(f"Không đủ credits! Bạn cần ít nhất {REQUIRED_CREDITS} credits để viết {word_count} từ.")

    main_kw = data.get("main_keyword")
    sub_kws = data.get("sub_keywords", [])
    title_mode = data.get("title_mode", "auto")
    custom_title = data.get("title", "")
    outline_mode = data.get("outline_mode", "auto")
    custom_outline = data.get("custom_outline", [])
    source_mode = data.get("source_mode", "own")
    semantic_option = data.get("semantic_option", "skip")
    semantic_kws = data.get("semantic_keywords", []) if semantic_option == "semantic" else []

    model = data.get("stepSeven", {}).get("aiModel", "gpt-4")
    bold_kw = data.get("stepSeven", {}).get("boldMainKeyword", False)
    bold_headings = data.get("stepSeven", {}).get("boldHeadings", False)
    keyword_links = data.get("stepSeven", {}).get("keywordLinks", "")
    final_paragraph = data.get("stepSeven", {}).get("finalParagraph", "")
    insert_position = data.get("stepSeven", {}).get("position", None)
    selected_site = data.get("stepSeven", {}).get("selectedWebsite", "")

    if title_mode == "auto":
        title = generate_title(main_kw, sub_kws).split("\n")[0]
    else:
        title = custom_title or f"Bài viết về {main_kw}"

    if outline_mode == "auto":
        outline = generate_outline(main_kw)
    else:
        outline = "\n".join(custom_outline or ["Mở bài", "Thân bài", "Kết luận"])

    semantic_text = ", ".join(semantic_kws) if semantic_kws else "Không có"
    link_text = f"Chèn liên kết cho từ khoá như sau:\n{keyword_links}" if keyword_links else "Không cần chèn liên kết"
    final_paragraph_text = f"Chèn đoạn kết sau cùng:\n{final_paragraph}" if final_paragraph else "Không cần thêm đoạn kết"

    # ✅ Prompt viết bài theo định dạng markdown, không có số đầu dòng hay thẻ HTML
    prompt = f"""
Hãy viết một bài viết chuẩn SEO, hấp dẫn, dài khoảng {word_count} từ, với yêu cầu sau:

- Từ khoá chính: {main_kw}
- Từ khoá phụ: {', '.join(sub_kws)}
- Semantic Keywords: {semantic_text}
- Tiêu đề bài viết: {title}
- Dàn ý:
{outline}

Yêu cầu định dạng:
- KHÔNG dùng các thẻ HTML như <h1>, <h2>, <h3>, <p>, ...
- KHÔNG bắt đầu bằng số thứ tự như 1., 2., I., II.
- Tiêu đề và tiêu đề phụ in đậm bằng Markdown (**...**)
- Trình bày gọn gàng, không để khoảng trắng dư thừa giữa các đoạn
- { "In đậm từ khoá chính trong nội dung" if bold_kw else "Không cần in đậm từ khoá chính" }
- { "Tiêu đề phải in đậm" if bold_headings else "Không cần in đậm tiêu đề" }
- {link_text}
- {final_paragraph_text}
- Nếu phù hợp, đề cập website: {selected_site}

Viết bằng ngôn ngữ: {data.get("language", "Vietnamese")}
""".strip()

    content = call_openai(prompt, model=model)
    user.credits -= REQUIRED_CREDITS

    return {
        "title": title,
        "outline": outline,
        "content": content,
        "model_used": model,
        "website": selected_site,
    }
