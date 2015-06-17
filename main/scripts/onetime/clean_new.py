#import re
import json

__author__ = 'jena'

# f = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/new/new-all.txt"
#
#
# with open(f,'r') as fin, open(fo,'w') as fout:
#     for line in fin:
#         if line.strip() == '{}': continue
#
#         line = line.lstrip('{')
#         line = line.rstrip().rstrip(',')
#         if line.endswith('}}'):
#             line = line[:-1]
#
#         nline = re.sub(r"\, \"L",",\n\"L",line)
#
#
#         fout.write(nline+',\n')
#


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def main():
    # fo = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/new/new-all.txt.out"
    # latest_lexicon = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/consolidated/saved.json"
    # latest_lexicon_with_new = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/consolidated/saved-withnew.json"

    fo = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/alsa/alsa2732-recovered"
    latest_lexicon = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/consolidated/saved.json"
    latest_lexicon_with_new = "/Users/jena/Desktop/arapaho-data/lexicon_data/backup-2/consolidated/saved-alsa.json"


    with open(fo,'r') as fin:
        new_instances = json.load(fin)

    with open(latest_lexicon,'r') as fin:
        json_file = json.load(fin)


    save_inst = {}
    save_inst2 = {}
    cnt = 25231
    jv_by_lexkey = {}

    for jk,jv in json_file.items():
        jv_by_lexkey[jk] = (jv['lex'],jv['pos'])


    for k,instance in new_instances.items():
        inst_key = (instance['lex'],instance['pos'])
        if inst_key not in save_inst:
            save_inst[inst_key] = [instance]
        else:
            save_inst[inst_key].append(instance)


    for k,v in save_inst.items():
        save_inst2[k] = [v[0]]
        if len(v) > 1:
            for v_ in v[1:]:
                if ordered(v[0]) != ordered(v_):
                    save_inst2[k].append(v_)

    for k,v in save_inst2.items():
        if len(v) > 1:
            print(k,len(v))
        else:
            if k in jv_by_lexkey.values():
                for k_,v_ in v[0].items():
                    if v_ == '': continue
                #     print (k_,v_)
                # print('-')
            else:
                lexid = 'L'+str(cnt)
                if lexid in json_file:
                    print('DUPLICATE:', lexid)
                else:
                    json_file[lexid] = v[0]
                    print(json.dumps(v[0]))
                cnt += 1

    with open(latest_lexicon_with_new,'w') as fout:
        json.dump(json_file,fout,ensure_ascii=True,sort_keys=True)
    print ('END:' , cnt)


main()