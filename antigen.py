#!/usr/bin/python3
import sys
import requests
import csv

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def safe_get(lst, index):
        return lst[index] if 0 <= index < len(lst) else None

def help():
    return '''
Usage: anti [[flag] [value]]...
    Flags:
        -f - Original sentence language (from)
        -t - Translation sentence language (to)
        -s - Tatoeba sorting algorithm
        -l - Sentence limit
        -ts - Transcription Script (ISO-15924)'''

class Sentence:
    def __init__(self, json_sentence: dict, trans_lang: str, script: str | None):
        self.text = Sentence.getText(json_sentence)
        self.audio = Sentence.getAudio(json_sentence)
        self.translation = Sentence.getTranslation(json_sentence, trans_lang)
        self.transcription = Sentence.getTranscription(json_sentence, script)
    
    def __iter__(self):
        return iter([self.text, 
                     "[sound:" + self.audio + "]" if self.audio is not None else None, 
                     self.translation.text if self.translation is not None else None, 
                     self.transcription if self.transcription is not None else None])

    @staticmethod
    def getText(json_sentence):
        return json_sentence["text"]

    @staticmethod
    def getAudio(json_sentence):
        al = json_sentence.get("audios", [])
        first = safe_get(al, 0)
        return None if first == None else first.get("download_url")

    @staticmethod
    def getTranslation(json_sentence, trans_lang):
        tl = json_sentence.get("translations", [])
        for t in tl:
            for u in t:
                if u["lang"] == trans_lang:
                    return Sentence(u, trans_lang, None)
        return None

    @staticmethod
    def getTranscription(json_sentence, script):
        if script == None:
            return None
        tc = json_sentence.get("transcriptions", [])
        for t in tc:
            if t["script"] == script:
                return t["html"]

def fetch(url: str, trans_lang: str, script: str|None) -> tuple[list[Sentence], str | None] | None:
    resp = requests.get(url)
    if resp.status_code != 200:
        return None

    json = resp.json()
    sentences = json["data"]
    paging = json["paging"]

    return (list(map(lambda x: Sentence(x, trans_lang, script) , sentences)), paging["next"] if paging["has_next"] else None)

def main():
    arg_from = None
    arg_to = "eng"
    arg_sort = "words"
    arg_limit = "500"
    arg_transcript_script = None

    args = sys.argv[1:]
    if len(args) == 0:
        print(help())
        return 1
    else:
        args = iter(args)
        for a in args:
            if a == "-f":
                arg_from = next(args) 
            elif a == "-t":
                arg_to = next(args)
            elif a == "-s":
                arg_sort = next(args)
            elif a == "-l":
                arg_limit = next(args)
            elif a == "-ts":
                arg_transcript_script = next(args)
            elif a == "-h":
                print(help())
                return 1
            else:
                print("Unknown argument ", a)
                return 1

    REQ_URL = "https://api.tatoeba.org/unstable/sentences?lang={}&trans:lang={}&sort={}&limit={}".format(arg_from, arg_to, arg_sort, arg_limit)
    res = fetch(REQ_URL, arg_to, arg_transcript_script)
    if res == None:
        eprint("Failed to fetch first page: ", REQ_URL)
        return 1

    (sentences, next_page) = res
    while next_page != None and len(sentences) < int(arg_limit):
        res = fetch(next_page, arg_to, arg_transcript_script)
        if res == None:
            eprint("Failed to load next page: ", next_page)
            return 1
        (new_sentences, next_page) = res
        sentences.extend(new_sentences)

    fields = ["Text", "Audio", "Translation", "Transcription"]
    writer = csv.writer(sys.stdout)
    writer.writerow(fields)
    writer.writerows(sentences)

    return 0

if __name__ == "__main__":
    sys.exit(main())
