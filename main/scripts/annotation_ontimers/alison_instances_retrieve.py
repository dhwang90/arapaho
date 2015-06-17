import json

__author__ = 'jena'

# in this case, afile has committed alison's unadjudicated data
# separates out the instances based on date added and modified to make them into adjudicatable file


afile = '/Users/jena/Documents/Research/workspace3/arapaho/lexicon_data_workspace/alison_data/problem_files/arapaho_lexicon-alison_add.json'
afile_diff = '/Users/jena/Documents/Research/workspace3/arapaho/lexicon_data_workspace/alison_data/good_to_go/alsa2732-2015-05-27-14-30-00.json'

with open(afile,'r') as fin:
    lexicon = json.load(fin)

lexout = {}
i = 0
j = 0
for lexid, lexitem in lexicon.items():
    if "2015-05-27" in lexitem['date_added']:
        lexitem['lexid'] = 'New-'+str(i)
        lexout[i] = lexitem
        i+= 1
        j+= 1

    elif "2015-05-27" in lexitem['date_modified']:
        lexitem['lexid'] = lexid
        lexout[i] = lexitem
        i+= 1


print (i)
print (j)

with open(afile_diff,'w') as fout:
    json.dump(lexout,fout,ensure_ascii=True)