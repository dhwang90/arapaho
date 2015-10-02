import json
import argparse
import time
import os

__author__ = 'jena'

def jsondump(prefix,output_dir,inst_temp,cnt):
    fname = prefix+'-'+time.strftime('%Y-%m-%d-%H-%M-')+'0'+str(cnt)+'.json'
    with open(os.path.join(output_dir,fname),'w') as fout:
        json.dump(inst_temp,fout)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_to_split')
    parser.add_argument('instance_count')
    parser.add_argument('output_dir')
    parser.add_argument('prefix')
    args = parser.parse_args()

    with open(args.json_to_split) as fin:
        json_to_split = json.load(fin)

    instance_count = int(args.instance_count)

    i = 0
    j = 0
    cnt = 0
    inst_temp = {}
    for inst_key,inst_val in json_to_split.items():
        if i%instance_count == 0 and i != 0:
            jsondump(args.prefix,args.output_dir,inst_temp,cnt)

            print 'dumping '+str(i)+' '+str(j)
            j = 0
            cnt += 1

            inst_temp = {}

        inst_temp[inst_key] = inst_val
        i+=1
        j+=1
    jsondump(args.prefix,args.output_dir,inst_temp,cnt)

    print 'dumping '+str(i)+' '+str(j)

main()