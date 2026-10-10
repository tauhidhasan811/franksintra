import re

MIN_CHARS = 400
MAX_CHARS = 650
OPENING_CHARS = 120
TEXT_FIELDS = ("intro", "body", "closing", "cta")
PHONE_PATTERN = re.compile(r"\+?\(?\d[\d\s().-]{7,}\d")


def city_from_location(assign_location: str) -> str:
    # "Las Vegas, NV, USA" -> "Las Vegas"; coordinates give no usable city.
    city = (assign_location or "").split(",")[0].strip()
    if not city or any(char.isdigit() for char in city):
        return ""
    return city


def gmb_post_text(post: dict) -> str:
    parts = [str(post.get(field) or "").strip() for field in TEXT_FIELDS]
    return " ".join(part for part in parts if part)


def clean_gmb_post(post: dict) -> dict:
    # The client dropped feature lists and hashtags, so these always come back empty.
    return {**post, "features": [], "hashtags": []}


def find_gmb_post_problems(post: dict, company_name: str, city: str) -> list[str]:
    text = gmb_post_text(post)
    lowered = text.lower()
    opening = lowered[:OPENING_CHARS]
    problems = []

    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        problems.append(
            f"The post is {len(text)} characters; intro, body, closing and cta joined with spaces "
            f"must total {MIN_CHARS} to {MAX_CHARS} characters."
        )

    name = (company_name or "").strip().lower()
    if name and name != "unknown":
        count = lowered.count(name)
        if count != 1:
            problems.append(f"The business name '{company_name}' appears {count} times; it must appear exactly once.")
        elif name not in opening:
            problems.append(f"The business name must appear within the first {OPENING_CHARS} characters.")

    if city:
        count = lowered.count(city.lower())
        if not 1 <= count <= 2:
            problems.append(f"The city '{city}' appears {count} times; it must appear 1 to 2 times.")
        elif city.lower() not in opening:
            problems.append(f"The city must appear within the first {OPENING_CHARS} characters.")

    title = str(post.get("title") or "").strip()
    if not title:
        problems.append("Add a short title.")
    elif name and name != "unknown" and name in title.lower():
        problems.append("Remove the business name from the title; it must appear only once, in the intro.")

    if "#" in text or "#" in title:
        problems.append("Remove all hashtags.")
    if PHONE_PATTERN.search(text) or PHONE_PATTERN.search(title):
        problems.append("Remove all phone numbers.")

    return problems
