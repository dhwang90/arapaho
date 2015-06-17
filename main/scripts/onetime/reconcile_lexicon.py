import json
import argparse
import shutil

__author__ = 'jena'

# written to reconcile multiple lexicon backups.

ALREADYSEEN = ["L1006", "L10694", "L10695", "L14139", "L14697", "L16206", "L1740",
               "L19692", "L23584", "L23698", "L23757", "L24208", "L24553", "L24750", "L24877", "L25190",
               "L25199", "L25200", "L395", "L455", "L457", "L458", "L5295", "L670", "L672", "L673",
               "L756", "L765", "L833", "L8394", "L883", "L9339", "L9829", "L9830", "L8409", "L19162", "L9324",
               "L14136", "L10394", "L10496", "L10811", "L10814", "L11009", "L11020", "L11123", "L12533", "L1334",
               "L13765", "L13766", "L13986", "L14608", "L14646", "L14661", "L15437", "L15452", "L16005", "L16339",
               "L16423", "L17221", "L17329", "L17336", "L18091", "L18414", "L18921", "L19037", "L19783", "L19930",
               "L19948", "L20147", "L20149", "L20217", "L21324", "L21552", "L21560", "L21614", "L22328",
               "L22347", "L22709", "L22832", "L22866", "L23019", "L23021", "L23588", "L23628", "L24066", "L24158",
               "L24240", "L24291", "L2571", "L2897", "L2988", "L2997", "L3000", "L3526", "L4199", "L4884", "L5517",
               "L588", "L6168", "L6312", "L6495", "L7196", "L8155", "L8165", "L8169", "L8619", "L9224", "L9619",
               "L9791","L9949", "L6403", "L5510", "L4306", "L3902", "L3748", "L3578", "L25262", "L25261", "L25260",
               "L25259", "L25258", "L25257", "L25256", "L25255", "L25254", "L25253", "L25252", "L25251", "L25250",
               "L25249", "L25248", "L25247", "L25246", "L25245", "L25244", "L25243", "L25242", "L25241", "L25240",
               "L22838", "L22834", "L22833",
               "L21995", "L21984", "L21980", "L20324", "L20315", "L19611", "L18825", "L18693", "L18614", "L18573",
               "L18254", "L17073", "L1646", "L14145", "L1390", "L12367", "L11725", "L11718", "L11255",
                "L10718", "L14932", "L17480", "L1750", "L1778", "L19017", "L20122", "L21368", "L23508", "L2756",
               "L3754", "L4024", "L6098", "L7100", "L9094"]

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('reference_file')
    parser.add_argument('comparison_file')
    parser.add_argument('--show_content', action="store_true")
    parser.add_argument('--skip_repeat', action="store_true")
    parser.add_argument('num')
    parser.add_argument('--save_file', action="store_true")
    args = parser.parse_args()

    fout_path = '/'.join(args.reference_file.split('/')[:-1])+'/'

    st_no = int(args.num)
    new_cnt = st_no

    with open(args.reference_file) as fin_ref, open(args.comparison_file) as fin_comp:
        reference_file = json.load(fin_ref)
        comparison_file = json.load(fin_comp)

    save_file = {}
    save_file_new = {}

    for lexid in comparison_file:

        if lexid not in reference_file:
            # if comparison_file[lexid]['lex'] in SKIP_NEW:
            #     continue

            new_lexid = 'L'+str(new_cnt)
            print ('\n------------------------',lexid, 'NOT IN REF', new_lexid)
            #print(comparison_file[lexid]['lex'],comparison_file[lexid]['pos'],comparison_file[lexid]['gloss'])
            if args.show_content:
                print ('COMP:')
                for k,v in sorted(comparison_file[lexid].items()):
                    print(k,v)

            save_file_new[new_lexid] = comparison_file[lexid]
            new_cnt += 1

        else:
            if ordered(comparison_file[lexid]) != ordered(reference_file[lexid]):
                printstr = '\n------------------------ '+lexid
                # if it's already been seen and it's already been tackled,
                # I want to keep my reference file, not comparison
                # although, it's the comparison by default that's saved
                # so let the ref information be saved instead:
                if lexid in ALREADYSEEN and args.skip_repeat:
                    skip = True

                    if len(reference_file[lexid]['senses']) == 1 and len(comparison_file[lexid]['senses']) == 1:
                        if 'sources' in comparison_file[lexid]['senses'][0] \
                                and ('sources' not in reference_file[lexid]['senses'][0] or reference_file[lexid]['senses'][0]['sources'] == ''):
                            reference_file[lexid]['senses'][0]['sources'] = comparison_file[lexid]['senses'][0]['sources']
                        if 'scientific' in comparison_file[lexid]['senses'][0] \
                                and ('scientific' not in reference_file[lexid]['senses'][0] or reference_file[lexid]['senses'][0]['scientific'] == ''):
                            reference_file[lexid]['senses'][0]['scientific'] = comparison_file[lexid]['senses'][0]['scientific']
                        if 'synonym' in comparison_file[lexid]['senses'][0] \
                                and ('synonym' not in reference_file[lexid]['senses'][0] or reference_file[lexid]['senses'][0]['synonym'] == ''):
                            reference_file[lexid]['senses'][0]['synonym'] = comparison_file[lexid]['senses'][0]['synonym']

                    else:
                        for sense in reference_file[lexid]['senses']:
                            for sense_ref in comparison_file[lexid]['senses']:
                                periodless = sense['definition'].strip('.').lower()
                                if sense_ref['definition'].lower() == sense['definition'].lower() or \
                                                sense_ref['definition'].lower() == periodless:
                                    #print ('xxx')
                                    if ('sources' not in sense or sense['sources']=="") and ('sources' in sense_ref):
                                        #print('xxx',sense['sources'] , sense_ref['sources'])
                                        sense['sources'] = sense_ref['sources']
                                    if ('scientific' not in sense or sense['scientific']=="") and ('scientific' in sense_ref):
                                        sense['scientific'] = sense_ref['scientific']
                                    if ('synonym' not in sense or sense['synonym']=="") and ('synonym' in sense_ref):
                                        sense['synonym'] = sense_ref['synonym']


                    if args.save_file:
                        comparison_file[lexid] = reference_file[lexid]
                else:
                    skip = False
                    if lexid in ALREADYSEEN:
                        printstr += ' REPEAT'

                if not skip:

                    if comparison_file[lexid]['lex'] != reference_file[lexid]['lex']:
                        printstr += ' MISMATCH LEX'

                    print(printstr)


                    if args.show_content:
                        print ('REF :')
                        for k,v in sorted(reference_file[lexid].items()):
                            print(k,v)
                        print ('\nCOMP:')
                        for k,v in sorted(comparison_file[lexid].items()):
                            print(k,v)


                    if 'senses' in comparison_file[lexid] and 'senses' in reference_file[lexid]:
                        if len(comparison_file[lexid]['senses']) == 1 and len(reference_file[lexid]['senses']) == 1:
                            if 'sources' in reference_file[lexid]['senses'][0] \
                                    and ('sources' not in comparison_file[lexid]['senses'][0] or comparison_file[lexid]['senses'][0]['sources'] == ''):
                                comparison_file[lexid]['senses'][0]['sources'] = reference_file[lexid]['senses'][0]['sources']
                            if 'scientific' in reference_file[lexid]['senses'][0] \
                                    and ('scientific' not in comparison_file[lexid]['senses'][0] or comparison_file[lexid]['senses'][0]['scientific'] == ''):
                                comparison_file[lexid]['senses'][0]['scientific'] = reference_file[lexid]['senses'][0]['scientific']
                            if 'synonym' in reference_file[lexid]['senses'][0] \
                                    and ('synonym' not in comparison_file[lexid]['senses'][0] or comparison_file[lexid]['senses'][0]['synonym'] == ''):
                                comparison_file[lexid]['senses'][0]['synonym'] = reference_file[lexid]['senses'][0]['synonym']

                        else:
                            for sense in comparison_file[lexid]['senses']:
                                for sense_ref in reference_file[lexid]['senses']:
                                    periodless = sense['definition'].strip('.').lower()
                                    if sense_ref['definition'].lower() == sense['definition'].lower() or \
                                                    sense_ref['definition'].lower() == periodless:
                                        #print ('xxx')
                                        if ('sources' not in sense or sense['sources']=="") and ('sources' in sense_ref):
                                            #print('xxx',sense['sources'] , sense_ref['sources'])
                                            sense['sources'] = sense_ref['sources']
                                        if ('scientific' not in sense or sense['scientific']=="") and ('scientific' in sense_ref):
                                            sense['scientific'] = sense_ref['scientific']
                                        if ('synonym' not in sense or sense['synonym']=="") and ('synonym' in sense_ref):
                                            sense['synonym'] = sense_ref['synonym']

                    if args.show_content:
                        print('\nJOIN:')
                        for k,v in sorted(comparison_file[lexid].items()):
                            print(k,v)

            if args.save_file:
                save_file[lexid] = comparison_file[lexid]

    if args.save_file:
        shutil.move(args.comparison_file,fout_path+'visited/')

        with open(fout_path+'saved.json','w') as fout:
            json.dump(save_file,fout,ensure_ascii=True)

        with open(fout_path+'new.json','a') as fout:
           fout.write(json.dumps(save_file_new,ensure_ascii=True,sort_keys=True)+'\n')

        print ('\n\nNEW added',str(new_cnt - st_no))
        print ('Next NO',str(new_cnt))

    else:
        print ('\n\nNEW entries',str(new_cnt - st_no))


main()