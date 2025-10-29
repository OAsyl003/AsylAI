import re

def parse_message(text: str) -> tuple[str | None, int | None, str]:


    m = re.search(r"\b(19|20)\d{2}\b", text)
    if not m:
        # Год не найден — возвращаем весь текст как симптом
        return None, None, text.strip()

    year = int(m.group(0))
    brand = text[: m.start()].strip()
    symptom = text[m.end():].strip()
    return (brand or None), year, symptom
