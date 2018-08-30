import yaml
import json
import re
import codecs
from collections import OrderedDict

# OrderedDictに対応するためのpyyamlの内部処理の設定
def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

def construct_odict(loader, node):
    return OrderedDict(loader.construct_pairs(node))

# alis_api.yamlの生成
def generate_api_doc():
    with open('alis_api.yaml', 'w') as api_doc:
        with open('api-template.yaml', 'r') as base_yaml_file:
            for base_yaml_line in base_yaml_file:
                fix_yaml_line = base_yaml_line.replace('!', '')
                if re.match("  LambdaRole:$", base_yaml_line):
                    return
                api_doc.write(fix_yaml_line)

def prepare_api_doc():
    api_yaml = open('alis_api.yaml')
    data = yaml.load(api_yaml)
    output_json = OrderedDict(data['Resources']['RestApi']['Properties']['DefinitionBody'])

    # 各URLの不必要なSwaggerの記述を削除
    paths = list(output_json['paths'].keys())

    for path in paths:
        if 'get' in output_json['paths'][path].keys():
            del output_json['paths'][path]['get']['x-amazon-apigateway-integration']
        if 'post' in output_json['paths'][path].keys():
            del output_json['paths'][path]['post']['x-amazon-apigateway-integration']
        if 'put' in output_json['paths'][path].keys():
            del output_json['paths'][path]['put']['x-amazon-apigateway-integration']
        if 'delete' in output_json['paths'][path].keys():
            del output_json['paths'][path]['delete']['x-amazon-apigateway-integration']

    # 固定値の項目を挿入する
    output_json['info']['title'] = 'alisapi'
    output_json['basePath'] = '/api'
    output_json['host'] = 'alis.to'
    print('api-docsのバージョンを入力してください')
    version = input()
    output_json['info']['version'] = str(version)

    # jsonファイル作成
    f = open('alis_api.json', 'w')
    json.dump(output_json, f, ensure_ascii=False, indent=2)

    # 整形したPythonオブジェクトをyamlに変換
    with codecs.open('alis_api.yaml', 'w', 'utf-8') as f:
        yaml.dump(output_json, f, encoding='utf-8', allow_unicode=True, default_flow_style=False)

yaml.add_representer(OrderedDict, represent_odict)
yaml.add_constructor('tag:yaml.org,2002:map', construct_odict)
generate_api_doc()
prepare_api_doc()
