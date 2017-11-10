import pytz
import tzlocal
import pylons.config as config

from ckanapi import LocalCKAN

# backported from ckan 2.6
def get_display_timezone():
    ''' Returns a pytz timezone for the display_timezone setting in the
    configuration file or UTC if not specified.
    :rtype: timezone
    '''
    timezone_name = config.get('ckan.display_timezone') or 'utc'

    if timezone_name == 'server':
        return tzlocal.get_localzone()

    return pytz.timezone(timezone_name)


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
