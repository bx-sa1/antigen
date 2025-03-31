class Sentence:
    def __init__(self, json_sentence: dict, trans_lang):
        self.text = getText(json_sentence)
        self.audio = getAudio(json_sentence)
        self.translation = getTranslation(json_sentence, trans_lang)
        # self.transliteration = transliteration
    
    def __iter__(self):
        return iter([self.text, 
                     "[sound:" + self.audio + "]" if self.audio is not None else None, 
                     self.translation.text if self.translation is not None else None])

def getText(json_sentence):
    return json_sentence["text"]

def getAudio(json_sentence):
    al = json_sentence.get("audios", [])
    first = safe_get(al, 0)
    return None if first == None else first.get("download_url")

def getTranslation(json_sentence, trans_lang):
    tl = json_sentence.get("translations", [])
    for t in tl:
        for u in t:
            if u["lang"] == trans_lang:
                return Sentence(u, trans_lang)
    return None

def safe_get(lst, index):
    return lst[index] if 0 <= index < len(lst) else None

