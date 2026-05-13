import json
my_dict = {
    'air05':26374.0,
    'beasleyC3':753.999,
    'binkar10_1':6742.199,
    'cod105':-12.0,
    'dano3_3':576.344,
    'eil33-2':934.00,
    'hypothyroid-k1':-2851.0,
    'istanbul-no-cutoff':204.081,
    'markshare_4_0':1.0,
    'mas76':40005.05,
    'mc11':11689.00,
    'mik-250-20-75-4':-52301.0,
    'n5-3': 8105.00,
    'neos-860300':3201.00,
    'neos-957323':-237.756,
    'neos-1445765':-17783.0,
    'nw04':16862.0,
    'piperout-27':8124.00,
    'pk1':11.0,
    'seymour1':410.763
}
json_string = json.dumps(my_dict)
with open('train20.json', 'w') as json_file:
    json_file.write(json_string)
