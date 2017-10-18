#!/usr/bin/env python

import argparse
import csv
import re
import requests
import json
from functools import partial
from collections import defaultdict, Counter, OrderedDict
from settings import SHEET_URL

id = lambda x: x

MA_SCHEMA = 'ma_schema.csv'

# Define column names of interest
SCHEMA_NAME_SPACE = 'schema_name_space'
FIELDNAME = 'fieldname'
DISPLAY_FIELDNAME = 'display-fieldname'
FORM_DISPLAY_ORDER = 'form-display-order'
DESCRIPTION = 'Description'

# Product type validation rule columns
MAPSHEET = 'mapsheet'
ATLAS = 'atlas'
POWERPOINT_MAP = 'powerpoint-map'
WEBMAP = 'webmap'
DATAPRODUCT = 'dataproduct'
LEGACY = 'legacy'  # not validating
PRODUCT_TYPES = (MAPSHEET, ATLAS, POWERPOINT_MAP, WEBMAP, DATAPRODUCT)

def get_sheet():
    with open('ma_schema.csv', 'wb') as f:
        resp = requests.get(SHEET_URL)
        f.write(resp.content)

REQUIRED = lambda x: 'required' in x and x['required'] == 'true'
NULLABLE = lambda x: x
ABSENT = lambda x: x
NO_RULE = None

VALIDATE_CONDITIONS = {
    'required': REQUIRED,
    'nullable': NULLABLE,
    'not-in-schema': ABSENT
}


def build_validation_rule(row, product_type):
    condition = row[product_type]
    rule = VALIDATE_CONDITIONS.get(condition, NO_RULE)
    return rule

def lookup_validation_rule(rules, field_name):
    return rules[field_name]['validators']


def build_ma_schema():
    """ Return an schema derived from MapAction spreadsheet """
    rules = defaultdict(dict)
    with open(MA_SCHEMA, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for product_type in PRODUCT_TYPES:
                field_name = row[FIELDNAME]
                if field_name is None or '':
                    continue
                rules[product_type][field_name] = {
                    DISPLAY_FIELDNAME: row[DISPLAY_FIELDNAME],
                    'description': row[DESCRIPTION],
                    'required': True if row[product_type] == 'required' else False,
                    'validators': build_validation_rule(row, product_type),
                }
    return rules


def build_order():
    field_order = defaultdict(list)
    with open(MA_SCHEMA, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[FIELDNAME] and row[SCHEMA_NAME_SPACE]:
                try:
                   order = int(row[FORM_DISPLAY_ORDER])
                except ValueError:
                    continue

                field_order[row[SCHEMA_NAME_SPACE]].append(
                    (
                        order, row[FIELDNAME]
                    )
                )
    return field_order


filter_rules = lambda rules, f: dict((k, v) for (k, v) in rules.items() if f(k))
is_resource_rule = lambda x: x.startswith("resources.")
def compose(f, g): return lambda x: f(g(x))
not_filter = lambda x: not(x)

def validate(rules, schema):
    extras = []  # entries in schema we haven't validated
    untested_rules = rules.keys()
    results = {}

    for field in schema:
        field_name = field['field_name']
        try:
            rule = lookup_validation_rule(rules, field_name)
        except KeyError:
            extras.append(field_name)
            continue

        if rule is not None:
            results[field_name] = rule(field)
            untested_rules.remove(field_name)
        else:
            print "rule is None %s" % field_name

    return {
        'results': results,
        'untested_rules': untested_rules,
        'extras': extras
    }


def display_results(schema_file, results):
    print '%s:\n' % (schema_file.name)
    validated = results['results']
    for k, v in validated.items():
        if not v:
            print('%s:\n\t%s\n\n' % (k, v))

def validate_dataset_fields(rules, schema):
    dataset_rules = filter_rules(rules, compose(not_filter, is_resource_rule))
    return validate(rules, schema)

def validate_resource_fields(rules, schema):
    dataset_rules = filter_rules(rules, is_resource_rule)
    return validate(rules, schema)


def validate_schema_ordering(order, schema):
    validated_fields = []
    order_map = dict(order)
    for i, field in enumerate(schema):
        result = field['field_name'] == order[i]
        validated_fields.append((field, result))

    return validated_fields

def reorder_schema_fields(order, schema):
    reordered = []
    schema_map = dict((k, v) for k, v in schema.items())
    for index, field_name in order:
        schema_field = schema_map.get(field_name)
        if not schema_field:
            print 'schema_field %s missing' % field_name
            continue
        reordered.append(
            (field_name, schema_field)
        )

    return OrderedDict(reordered)


def get_field(field_name, metadata):
    return OrderedDict({
      "field_name": field_name,
      "label": metadata[DISPLAY_FIELDNAME],
      "help_text": metadata['description'],
      # "form_placeholder": "",
      # "validators": "scheming_required int_validator",
      "required": metadata['required'],
    })


def get_fields(schema_rules):
    fields = []
    for field_name, metadata in schema_rules.items():
        fields.append(get_field(field_name, metadata))
    return fields


def write_schema(dataset_type, schema_file, schema_rules, order_rules):
    scheming_schema = OrderedDict({
        "scheming_version": 1,
        "dataset_type": dataset_type,
        "about": "MapAction %s schema" % dataset_type.capitalize(),
        "about_url": "http://www.mapaction.org/",
        "dataset_fields": get_fields(reorder_schema_fields(order_rules['dataset'], schema_rules)),
        "resource_fields": get_fields(reorder_schema_fields(order_rules['resources'], schema_rules))
    })

    with open(schema_file, 'wb') as schema_file:
        json.dump(scheming_schema, schema_file, indent=4)


def validate_schema(schema_file, schema_rules, order_rules):
    with open(schema_file, 'rb') as schema_file:
        schema = json.load(schema_file, object_pairs_hook=OrderedDict)
        # metadata

        # dataset_fields
        validate_schema_ordering(order['dataset'], schema['dataset_fields'])
        display_results(
            schema_file,
            validate_dataset_fields(schema_rules, schema['dataset_fields'])
        )

        # resource_fields
        display_results(
            schema_file,
            validate_resource_fields(schema_rules, schema['resource_fields'])
        )


def unique_ordering(namespace, rows):
    ordering = Counter(x[0] for x in rows)
    if any(count != 1 for count in ordering.values()):
        raise Exception((
            "Ordering not unique: %s\n "
            "%s\n"
            ) % (
                namespace,
                [(k, v) for (k, v) in ordering.items() if v != 1]
            )
        )


def validate_order_rules(order_rules):
    for k, v in order_rules.items():
        unique_ordering(k, v)

def main(args):
    # Generate MapAction schemas
    if args.get_sheet:
        get_sheet()
    rules = build_ma_schema()
    order = build_order()

    # validate_order_rules(order)
    # validate_schema('%s.json' % MAPSHEET, rules[MAPSHEET], order)

    for product_type in PRODUCT_TYPES:
        write_schema(
            product_type,
            '%s.json' % product_type,
            rules[product_type],
            order
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--get_sheet", action='store_true',
        help="Update MA sheet")
    args = parser.parse_args()
    main(args)
