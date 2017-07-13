import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanapi import LocalCKAN

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
