import sys
import requests
import csv
from sentence import Sentence

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
    sentence_objs = []

    while next_req is not None and len(sentence_objs) < limit:
        count += 1

        resp = requests.get(next_req) 

        json = resp.json()
        sentences = json["data"]
        paging = json["paging"]

        for s in sentences:
            sentence_objs.append(Sentence(s, to))

        next_req = str(paging["next"]) if paging["has_next"] == True else None

    return sentence_objs


    

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
