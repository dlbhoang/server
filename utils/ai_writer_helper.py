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
    prompt = f"Hãy tạo một dàn ý chi tiết cho bài viết với từ khoá chính: '{main_keyword}'. Dàn ý gồm các mục lớn (H2) và mục nhỏ (H3) nếu cần."
    return call_openai(prompt)

def generate_article(data: dict, user):
    REQUIRED_CREDITS = 5000

    if user.credits < REQUIRED_CREDITS:
        raise Exception("Không đủ credits để tạo bài viết!")

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

    # B1: Tiêu đề
    if title_mode == "auto":
        title = generate_title(main_kw, sub_kws).split("\n")[0]
    else:
        title = custom_title or f"Bài viết về {main_kw}"

    # B2: Dàn ý
    if outline_mode == "auto":
        outline = generate_outline(main_kw)
    else:
        outline = "\n".join(custom_outline or ["Mở bài", "Thân bài", "Kết luận"])

    # B3: Chuẩn bị các phần phụ để tránh lỗi f-string
    semantic_text = ", ".join(semantic_kws) if semantic_kws else "Không có"
    link_text = f"Chèn liên kết cho từ khoá như sau:\n{keyword_links}" if keyword_links else "Không cần chèn liên kết"
    final_paragraph_text = f"Chèn đoạn kết sau cùng:\n{final_paragraph}" if final_paragraph else "Không cần thêm đoạn kết"

    # Prompt
    prompt = f"""
Viết một bài viết chuẩn SEO, hấp dẫn, dài ít nhất 1000 từ, với yêu cầu sau:

- Từ khoá chính: {main_kw}
- Từ khoá phụ: {', '.join(sub_kws)}
- Semantic Keywords: {semantic_text}
- Tiêu đề bài viết: {title}
- Dàn ý:
{outline}

Yêu cầu định dạng:
- {"In đậm" if bold_kw else "Không in đậm"} từ khoá chính
- {"In đậm" if bold_headings else "Không in đậm"} tiêu đề (H2, H3)
- {link_text}
- {final_paragraph_text}
- Nếu có thể, đề cập trang web: {selected_site} (nếu phù hợp nội dung)

Ngôn ngữ: {data.get("language", "Vietnamese")}
""".strip()

    # B4: Gọi OpenAI để tạo bài viết
    content = call_openai(prompt, model=model)

    # Trừ credits
    user.credits -= REQUIRED_CREDITS

    return {
        "title": title,
        "outline": outline,
        "content": content,
        "model_used": model,
        "website": selected_site,
    }
