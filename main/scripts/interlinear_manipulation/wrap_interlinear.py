from collections import OrderedDict
import glob
import os

__author__ = 'jena'


class Project(object):
    def __init__(self,pid,sentences):
        self.sentences = sentences
        self.id = pid

    @property
    def forms(self):
        strout = '\id %s\n\n'%self.id
        for sentence in self.sentences:
            strout += sentence.forms
        return strout

class Sentence(object):
    def __init__(self,ref,interlinear_lines,ft):
        self.ref = ref
        assert isinstance(interlinear_lines, list)
        self.interlinear_lines = interlinear_lines
        self.ft = ft # free translation


    @property
    def forms(self):
        strout = '\\ref %s\n'%self.ref
        for ilines in self.interlinear_lines:
            strout += ilines.forms
        strout += '\\ft %s\n\n'%self.ft
        return strout

class InterlinearLine(object):
    def __init__(self,tx,mb,ge,ps):
        self.tx = self._get_text(tx)
        self.mb = self._get_text(mb)
        self.ge = self._get_text(ge)
        self.ps = self._get_text(ps)
        self.segment_idx = self.analyze_tx()
        self.interlinear = self.get_segments()

    def get_segments(self):
        tx_segs = self._get_segment(self.tx,self.segment_idx)
        mb_segs = self._get_segment(self.mb,self.segment_idx)
        ge_segs = self._get_segment(self.ge,self.segment_idx)
        ps_segs = self._get_segment(self.ps,self.segment_idx)

        return [tx_segs,mb_segs,ge_segs,ps_segs]

    @staticmethod
    def _get_segment(line,segment_idx):
        if len(segment_idx) == 0:
            return [line]


        line_segs = [line[0:segment_idx[0]]]
        for i,idx in enumerate(segment_idx):
            if len(segment_idx) > i+1:
                line_seg = line[idx:segment_idx[i+1]]
            else:
                line_seg = line[idx:]
            line_segs.append(line_seg)
        return line_segs

    @staticmethod
    def _get_text(line):
        if line.startswith('\\'):
            l = line.split(' ')
            return ' '.join(l[1:])
        else:
            return line

    def analyze_tx(self):
        idx_list = []
        for i,letter in enumerate(self.tx):
            if letter != ' ' and self.tx[i-1] == ' ':
                idx_list.append(i)

        return idx_list

    @property
    def forms(self):
        strout = []
        length = 0
        idx = 0

        longest = self._get_longest(self.interlinear)

        for i,segment in enumerate(longest):
            length+=len(segment)
            if length > 70:
                x=''.join(self.interlinear[0][idx:i])
                segout = '\\tx '+''.join(self.interlinear[0][idx:i])+'\n'
                segout += '\\mb '+''.join(self.interlinear[1][idx:i])+'\n'
                segout += '\\ge '+''.join(self.interlinear[2][idx:i])+'\n'
                segout += '\\ps '+''.join(self.interlinear[3][idx:i])+'\n'
                strout.append(segout)
                idx = i
                length = len(segment)

        segout = '\\tx '+''.join(self.interlinear[0][idx:])+'\n'
        segout += '\\mb '+''.join(self.interlinear[1][idx:])+'\n'
        segout += '\\ge '+''.join(self.interlinear[2][idx:])+'\n'
        segout += '\\ps '+''.join(self.interlinear[3][idx:])+'\n'
        strout.append(segout)


        return '\n'.join(strout)

    @staticmethod
    def _get_longest(lst):
        longest = lst[0]
        size = len(''.join(lst[0]))
        for l in lst[1:]:
            curr_size = len(''.join(l))
            if curr_size > size:
                longest = l
        return longest


def get_text(line):
    l = line.split(' ')
    return ' '.join(l[1:])


def get_longest(lst):
    longest = lst[0]
    size = len(''.join(lst[0]))
    for l in lst[1:]:
        curr_size = len(''.join(l))
        if curr_size > size:
            longest = l
    return longest


def resolve_size(interlinear_content):
    interlinear_content_resolved = {}

    maxlengths = {}


    for tag,interlinear in interlinear_content.items():
        for i,segment in enumerate(interlinear):
            if (i not in maxlengths) or (len(segment) > maxlengths[i]):
                maxlengths[i] = len(segment)


    for tag,interlinear in interlinear_content.items():
        full_line = ''
        for i,segment in enumerate(interlinear):
            diff = maxlengths[i] - len(segment)
            if diff > 0:
                for j in range(diff):
                    segment += ' '
            if full_line != '':
                full_line += ' ' + segment
            else:
                full_line = segment
        interlinear_content_resolved[tag] = full_line

    return interlinear_content_resolved

def main():
    docpath_pre = "/Users/jena/Documents/Research/Arapahoe/WY_Archive_Deposit/pre/"
    docpath_post = "/Users/jena/Documents/Research/Arapahoe/WY_Archive_Deposit/post/"

    interlinear_tags = ['tx','mb','ge','ps']

    for file in glob.glob(docpath_pre+'*.txt'):
        projects = []
        with open(file,encoding="latin-1") as fin:
            first_project = True
            first_sentence = True
            first_interlinear = True
            interlinear_content = OrderedDict()
            pid = ''
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
                tag = line.split(' ')[0][1:]

                if len(lines) > line_num+1 and not lines[line_num+1].startswith('\\'):
                     line += lines[line_num+1].strip('\n')

                if line.startswith('\id '):
                    if not first_project: projects.append(Project(pid,sentences))
                    pid = get_text(line)
                    sentences = []
                    first_project = False
                elif line.startswith('\\ref '):
                    if not first_sentence:
                        interlinear_content_resolved = resolve_size(interlinear_content)
                        if 'ge' not in interlinear_content_resolved:
                            interlinear_content_resolved['ge'] = ''
                        if 'ps' not in interlinear_content_resolved:
                            interlinear_content_resolved['ps'] = ''
                        if 'mb' not in interlinear_content_resolved:
                            interlinear_content_resolved['mb'] = ''
                        interlinear_lines.append(InterlinearLine(**interlinear_content_resolved))
                        sentence = Sentence(ref,interlinear_lines,freetrans)
                        sentences.append(sentence)
                    ref = get_text(line)
                    interlinear_lines = []
                    interlinear_content = OrderedDict()
                    freetrans = ''
                    first_sentence = False
                    first_interlinear = True

                elif line.startswith('\\') and tag in interlinear_tags:
                    if tag in interlinear_content:
                        interlinear_content[tag].append(get_text(line))
                    else:
                        interlinear_content[tag] = [get_text(line)]
                elif line.startswith('\\ft '):
                    freetrans = get_text(line)


            sentence = Sentence(ref,interlinear_lines,freetrans)
            sentences.append(sentence)
            interlinear_content_resolved = resolve_size(interlinear_content)
            if 'ge' not in interlinear_content_resolved:
                interlinear_content_resolved['ge'] = ''
            if 'ps' not in interlinear_content_resolved:
                interlinear_content_resolved['ps'] = ''
            if 'mb' not in interlinear_content_resolved:
                interlinear_content_resolved['mb'] = ''
            interlinear_lines.append(InterlinearLine(**interlinear_content_resolved))
            projects.append(Project(pid,sentences))

        outfile = docpath_post+os.path.basename(file)
        print(outfile)
        with open(outfile,'w',encoding='utf-8') as fout:
            for project in projects:
                fout.write(project.forms)


main()