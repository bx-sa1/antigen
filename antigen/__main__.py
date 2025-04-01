import sys
import requests
import csv
from sentence import Sentence
import pandas as pd

def help():
    return '''
Usage: anti [[flag] [value]]...
    Flags:
        -f - Original sentence language (from)
        -t - Translation sentence language (to)
        -s - Tatoeba sorting algorithm'''

def get_sentences(req_url: str | None, to, limit):
    next_req = req_url
    count = 0
    all_sentences = pd.DataFrame(None)

    while next_req is not None:
        count += 1

        resp = requests.get(next_req) 

        json = resp.json()
        sentences = json["data"]
        paging = json["paging"]

        def audios_map(row):
            row = row.copy()
            audios = row["audios"]
            if len(audios) > 0:
                audios = audios[0]["download_url"]
            else:
                audios = None
            return row

        def translations_map(row):
            row = row.copy()
            translations = row["translations"]
            for t in translations[0]:
                if t["lang"] == to:
                    translations = t["text"]
                    return row
            translations = None
            return row
            
        sentences_table = pd.json_normalize(sentences)
        sentences_table = sentences_table.filter(items=["text", "audios", "translations"]) \
                                         .apply(audios_map, axis=1) \
                                         .apply(translations_map, axis=1)
        print(sentences_table.to_string())

        all_sentences = pd.concat([all_sentences, sentences_table])

        next_req = str(paging["next"]) if paging["has_next"] == True and all_sentences.size < limit else None

    return all_sentences


    

def main():
    arg_from = None
    arg_to = "eng"
    arg_sort = "words"
    arg_limit = "500"

    args = iter(sys.argv[1:])
    for a in args:
        if a == "-f":
            arg_from = next(args) 
        elif a == "-t":
            arg_to = next(args)
        elif a == "-s":
            arg_sort = next(args)
        elif a == "-l":
            arg_limit = next(args)
        else:
            print(help())
            exit(1)

    REQ_URL = "https://api.tatoeba.org/unstable/sentences?lang={}&trans:lang={}&sort={}&limit={}"
    sentences = get_sentences(REQ_URL.format(arg_from, arg_to, arg_sort, arg_limit), arg_to, int(arg_limit))

    fields = ["Text", "Audio", "Translation"]
    writer = csv.writer(sys.stdout)
    writer.writerow(fields)
    writer.writerows(sentences)

if __name__ == "__main__":
    main()
