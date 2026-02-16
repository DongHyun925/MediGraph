import re

def clean_persona_fluff(text: str) -> str:
    """
    AI가 생성한 텍스트에서 불필요한 공감 멘트나 수식어를 제거합니다.
    """
    if not text:
        return ""
        
    # 제거할 패턴 목록 (정규식)
    fluff_patterns = [
        r"많이 불편하시겠어요[\?\.\!\s]*",
        r"힘드시겠네요[\?\.\!\s]*",
        r"걱정이 많으시죠[\?\.\!\s]*",
        r"불편함이 크시겠네요[\?\.\!\s]*",
        r"속상하시겠어요[\?\.\!\s]*",
        r"힘든 시간을 보내고 계시네요[\?\.\!\s]*",
        r"마음이 안 좋으시겠어요[\?\.\!\s]*",
        r"증상 때문에 많이 고생하고 계시군요[\?\.\!\s]*",
        r"고생이 많으십니다[\?\.\!\s]*",
        r"얼마나 힘드실지 이해합니다[\?\.\!\s]*",
        r"쾌유를 빕니다[\?\.\!\s]*",
        # 문장 시작 부분의 인사말이나 공감 멘트
        r"^(안녕하세요|그렇군요|알겠습니다|네)[\?\.\!\s,]*",
        # "환자분의 상태를 들으니..." 같은 문구
        r"환자분의 상태를 들으니.*?(불편|걱정|생각).*?겠어요[\?\.\!\s]*",
    ]
    
    cleaned_text = text
    for pattern in fluff_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
        
    # 중복 공백 및 양끝 공백 제거
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text.strip()
