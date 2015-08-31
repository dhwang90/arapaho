from collections import OrderedDict
import glob
import os

__author__ = 'jena'

def get_text(line):
    l = line.split(' ')
    return ' '.join(l[1:])

def main():
    docpath = "/Users/jena/Documents/Research/workspace-pycharm/arapaho/docs/interlinear/textcopy/"
    docpath_out = docpath+"dep/"
    docpath_out_all = docpath+"dep_all/"

    if not os.path.exists(docpath_out):
        os.makedirs(docpath_out)


    for file in glob.glob(docpath+'*.txt'):
        projects = {}
        with open(file,encoding="latin-1") as fin:
            first_project = True
            first_sentence = True

            pid = ''
            ref = ''
            lines = fin.readlines()

            for line_num,line in enumerate(lines):
                if line == '' or not line: continue
                if not line.startswith('\\'):
                    continue

                line = line.replace('\x93','"')
                line = line.replace('\x94','"')
                line = line.replace('\x92',"'")
                line = line.replace('\x91',"'")

                line = line.strip('\n')

                if len(lines) > line_num+1 and not lines[line_num+1].startswith('\\'):
                    line += lines[line_num+1].strip('\n')

                if line.startswith('\id '):
                    if not first_project:
                        sentences[ref] = sentence
                        projects[ref.split('.')[0]] = sentences
                        print(ref.split('.')[0])

                    sentences = {}
                    sentence = []
                    first_project = False

                elif line.startswith('\\ref '):
                    if not first_sentence:
                        sentences[ref] = sentence

                    ref = get_text(line)
                    sentence = []
                    first_sentence = False

                elif line.startswith('\\tx '):
                    sentence.extend(get_text(line).split())

            sentences[ref] = sentence
            projects[pid] = sentences


        for pid,sentences in projects.items():
            with open(docpath_out+pid+'.txt','w') as fout:
                #out_text = 'ref,word,num,dep,label,dep2,label2\n'
                out_text = 'ref|word|num|dep|label|dep2|label2\n'
                for ref,sentence in sorted(sentences.items()):
                    for i,word in enumerate(sentence):

                        #out_text += '"%s","%s","%s",,,,\n'%(ref.replace('\"','\'\''),word.replace('\"','\'\''),i+1)  # pipe delimited
                        out_text += '%s|%s|%s||||\n'%(ref.replace('\"','\'\''),word.replace('\"','\'\''),i+1)  # pipe delimited

                fout.write(out_text)



main()