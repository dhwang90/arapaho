from collections import OrderedDict
import re
from lex.lexhandlers import XMLDictReader

__author__ = 'jena'


def parse_english(filepath):
    chapter_pattern = re.compile(r'\(Luke (\d\d*)\)')
    verse_pattern = re.compile(r' \d\d* ')

    chapters = OrderedDict()

    with open(filepath) as fin:
        for chapter in fin:
            ch = chapter_pattern.match(chapter)
            if ch:
                ch_no = chapter[ch.start(1):ch.end(1)]
                verses_en = verse_pattern.split(chapter[ch.end(0)+1:])
                if ch_no == '1':print(verses_en[-1])
                chapters[ch_no] = verses_en

    return chapters


def clean_index(index_pattern,text):
    x = index_pattern.search(text)
    if x:
        return text.replace(x.group(0),'')
    return text


def parse_arapaho(filepath):
    chapter_pattern = re.compile(r'^NEHEDAUNAU (\d\d*)\.*$')
    verse_pattern = re.compile(r'^(\d\d* )')
    index_pattern = re.compile(r'(=|\d)\d\d*')

    chapters_raw = OrderedDict()
    chapters = OrderedDict()
    ch_no = ''
    verses = []
    text_complete = False

    with open(filepath, encoding='utf-8') as fin:
        for line in fin:
            if not line: continue
            if 'TEXTENDSHERE' in line:
                verses.append(verse_text)
                chapters_raw[ch_no] = verses

                text_complete = True

            line = line.strip()
            if line == '': continue



            if not text_complete:
                ch = chapter_pattern.match(line)
                if ch:
                    if ch_no != '':
                        verses.append(verse_text)
                        chapters_raw[ch_no] = verses
                    ch_no = line[ch.start(1):ch.end(1)]
                    verses = []
                    verse_text = []
                else:
                    verse = verse_pattern.match(line)
                    if verse:
                        if verse.group(1) != '1 ':
                            verses.append(verse_text)
                        text = clean_index(index_pattern,line.replace(verse.group(1),''))
                        verse_text = [text]
                    else:
                        verse_text.append(clean_index(index_pattern,line))

            else:
                pass

    for chapter,verses in chapters_raw.items():
        for verse in verses:
            verse_new = []

            for i,verse_line in enumerate(verse):
                if (i+1)%2 == 0:
                    verse_new.append(verse_line)
            if chapter not in chapters:
                chapters[chapter] = [verse_new]
            else:
                chapters[chapter].append(verse_new)

    return chapters


def byLx(lexdict):
    lexicon = {}

    for lex in lexdict:
        lx = lex.tags['lx']
        ps = lex.tags['ps']

        if lx not in lexicon:
            lexicon[lx] = {}

        if ps not in lexicon[lx]:
            lexicon[lx][ps] = [lex]
        else:
            lexicon[lx][ps].append(lex)

    return lexicon


def findTrans(word, lexicon):
    if word.lower() in lexicon:
        return findTransSub(word.lower(),lexicon)
    elif '-' in word:
        w = word.lower().strip('-')
        if w in lexicon:
            return findTransSub(w,lexicon)
    else:
        w = word.lower() + '-'
        if w in lexicon:
            return findTransSub(w,lexicon)

    return None


def findTransSub(word,lexicon):
    lexinfo = lexicon[word][next(iter(lexicon[word]))]
    if len(lexinfo) == 1:
        return lexinfo[0].tags['ge']
    else:
        return 'MULT'

def main():
    luke_path = "/Users/jena/Documents/Research/Arapahoe/Luke/"

    print('Reading files')
    luke_arapaho = parse_arapaho(luke_path+"Luke-Arapaho.txt")     # READ IN ARAPAHO
    luke_english = parse_english(luke_path+"Luke-English.txt")     # READ IN ENGLISH

    # print('Building dictionary')
    # lexicon = byLx(XMLDictReader('/Users/jena/Documents/Research/workspace-pycharm/arapaho/docs/141028/Dictionary.xml'))

    outlines = []

    print('Parsing arapaho doc')
    for ch_no, verses in luke_arapaho.items():
        outlines.append('\\id LUKE%s: Book of Luke, chapter %s\n'%(ch_no,ch_no))
        outlines.append('\\tx NIHIITONO %s'%(ch_no))
        outlines.append('\\ft Chapter %s\n'%(ch_no))

        print(ch_no)

        for v_no, verse in enumerate(verses):
            space = '0' if v_no < 9 else ''
            outlines.append('\\ref LUKE%s-0%s%s'%(ch_no,space,v_no+1))

            english_verse = luke_english[ch_no][v_no]

            verse_str = ''
            for v in verse:
                verse_str += '\\tx '+v+'\n'

            outlines.append('%s\\ft %s\n'%(verse_str,english_verse))

            # trans = ''
            # for v_line in verse:
            #     words = v_line.split()
            #     for word in words:
            #         trans_word = findTrans(word,lexicon)
            #         if trans_word:
            #             trans += trans_word
            #         elif '-' in word:
            #             segs = word.split('-')
            #             for i,seg in enumerate(segs):
            #                 trans_seg = findTrans(seg,lexicon)
            #                 if i > 0:
            #                     trans += '-'
            #                 if trans_seg:
            #                     trans+= trans_seg
            #                 else:
            #                     trans+= '***'
            #         else:
            #             trans += '***'
            #         trans = trans.lstrip('-') + ' '

    with open('/Users/jena/Documents/Research/workspace-pycharm/arapaho/docs/interlinear_text/luke.txt','w',encoding='utf-8') as fout:
        fout.write('\n'.join(outlines)+'\n')

main()