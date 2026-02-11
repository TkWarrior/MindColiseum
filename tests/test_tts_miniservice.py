from tts_miniservice.tts_service import clean_text_for_tts

def test_clean_text_for_tts():
    text = "**AI will transform** education"
    cleaned_text = clean_text_for_tts(text)
    assert cleaned_text == "AI will transform education"
    print("Test passed!")

if __name__ == "__main__":
    test_clean_text_for_tts()
    