# -*- coding: utf-8 -*-

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckan.lib.navl.dictization_functions as df

from ckanapi import LocalCKAN

Invalid = df.Invalid

def scheming_vocabulary_choices(field):
    """
    Required scheming field:
    "vocabulary": "name or id"

    # https://github.com/SNStatComp/ckan-CC/
    # /containers/plugins/ckanext-scheming/ckanext-scheming/ckanext/scheming/helpers.py
    """
    try:
        lc = LocalCKAN(username='')
        vocab = lc.action.vocabulary_show(id=field['vocabulary'])
        result = [{'value': tag['name'], 'label': tag['name']} for tag in vocab['tags']]
        return  [{'value': 'notSpecified', 'label': 'not specified'}] + result
    except:
        return []


class MapactionschemasPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IValidators)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'mapactionschemas')


    def get_helpers(self):
        '''Return the CKAN 2.0 template helper functions this plugin provides.

        See ITemplateHelpers.

        '''
        return {'mapactionschemas_vocabulary_choices': scheming_vocabulary_choices}


    # IValidators
    def get_validators(self):
        return {
            'equals_one': equals_one,
            'valid_float': valid_float,
            'xmax': xmax,
            'xmin': xmin,
            'ymax': ymax,
            'ymin': ymin,
        }


def equals_one(value):
    if value != 1:
        raise Invalid('not 1')
    return value


def valid_float(value):
    float_value = None
    try:
        float_value = float(value)
    except ValueError:
        print "Invalid float '%s'" % value
    return float_value

def xmax(key, flattened_data, errors, context):
    # xmin ≤ xmax ≤ 180
    unflattened = df.unflatten(flattened_data)
    value = unflattened[key[0]]
    xmin = valid_float(unflattened.get('xmin', -180))
    if xmin <= value <= 180.0:
        return value
    raise Invalid(u'%s ≤ %s ≤ 180' % (xmin, value))

def xmin(key, flattened_data, errors, context):
    # -180 ≤ xmin ≤ xmax
    unflattened = df.unflatten(flattened_data)
    value = unflattened[key[0]]
    xmax = valid_float(unflattened.get('xmax', 180))
    if -180 <= value <= xmax:
        return value
    raise Invalid(u'-180 ≤ %s ≤ %s' % (value, xmax))


def ymax(key, flattened_data, errors, context):
    # ymin ≤ ymax ≤ 90
    unflattened = df.unflatten(flattened_data)
    value = unflattened[key[0]]
    ymin = valid_float(unflattened.get('ymin', -90))
    if ymin <= value <= 90:
        return value
    raise Invalid(u'%s ≤ %s ≤ 90' % (ymin, value))

def ymin(key, flattened_data, errors, context):
    # -90 ≤ ymin ≤ ymax
    unflattened = df.unflatten(flattened_data)
    value = unflattened[key[0]]
    ymax = valid_float(unflattened.get('ymax', 90))
    if -90 <= value <= ymax:
        return value
    raise Invalid(u'-90 ≤ %s ≤ %s' % (value, ymax))
