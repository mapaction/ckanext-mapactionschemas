import datetime

from ckanapi import LocalCKAN, ValidationError
from ckan.tests.helpers import FunctionalTestBase

from ckanext.mapactionschemas.plugin import Invalid, valid_float
from ckanext.mapactionimporter.plugin import create_product_themes


class TestChoices(FunctionalTestBase):
    def setup(self):
        super(TestChoices, self).setup()
        create_product_themes()
        self.lc = LocalCKAN()
        self.valid_data = self.lc.action.package_create(
            type='test_dataproduct',
            title='some title',
            name='some_map',
            mapNumber='M001',
            product_themes=['Agriculture'],
            license_id='notspecified',
            datasource='From somewhere',
            principal_country_iso3='NPL',
            country_iso3=['AFG', 'CHN'],
            data_update_frequency='Every two weeks',
            syndicate='false',
            createdate=datetime.datetime(2021, 12, 14),
            createtime='12:18',
            glideno='NA-2016-000001-CAR',
            language_iso2='EN',
            xmax='20.1',
            xmin='-20.1',
            ymax='30.1',
            ymin='-40.1'
        )

    def test_product_themes_only_accepts_given_choices(self):
        product_themes = 'somethingrandom'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_theme',
                product_themes=product_themes,
            )
        except ValidationError as e:
            assert e.error_dict['product_themes'] == \
                    ['unexpected choice "%s"' % product_themes]

        else:
            raise AssertionError('ValidationError not raised')

    def test_product_themes_accepts_valid_choice(self):
        assert self.valid_data['product_themes'] == ['Agriculture']

    def test_data_update_frequency_preset_only_accepts_given_choices(self):
        data_update_frequency = 'somethingrandom'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_theme',
                data_update_frequency=data_update_frequency,
            )
        except ValidationError as e:
            # assert that a validation error for data_update_frequency
            # is raised
            assert ("(not '%s')" % data_update_frequency
                    in e.error_dict['data_update_frequency'][0])
        else:
            raise AssertionError('ValidationError not raised')

    def test_data_update_frequency_preset_only_accepts_valid_choice(self):
        assert self.valid_data['data_update_frequency'] == "Every two weeks"

    def test_principal_country_iso3_validator_only_accepts_valid_choices(self):
        principal_country_iso3 = 'somethingrandom'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_principal_country_iso3',
                principal_country_iso3=principal_country_iso3,
            )
        except ValidationError as e:
            # assert that a validation error for principal_country_iso3
            # is raised
            assert (["Country code has to be ISO3"] ==
                    e.error_dict['principal_country_iso3'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_principal_country_iso3_validator(self):
        assert self.valid_data['principal_country_iso3'] == 'NPL'

    def test_country_iso3_validator_only_accepts_valid_choices(self):
        country_iso3 = 'somethingrandom'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_country_iso3',
                country_iso3=country_iso3,
            )
        except ValidationError as e:
            # assert that a validation error for country_iso3
            # is raised
            assert (["Country code has to be ISO3"] ==
                    e.error_dict['country_iso3'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_country_iso3_validator_only_accepts_valid_list(self):
        country_iso3 = ['AFG', 'somethingrandom']
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_country_iso3',
                country_iso3=country_iso3,
            )
        except ValidationError as e:
            # assert that a validation error for country_iso3
            # is raised
            assert (["Country code has to be ISO3"] ==
                    e.error_dict['country_iso3'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_country_iso3_validato(self):
        assert self.valid_data['country_iso3'] == ['AFG', 'CHN']

    def test_language_iso2_only_accepts_valid_choices(self):
        language_iso2 = 'ENGLISH'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_language_iso2',
                language_iso2=language_iso2,
            )
        except ValidationError as e:
            # assert that a validation error for language_iso2
            # is raised
            assert (["Language code has to be ISO639-1"] ==
                    e.error_dict['language_iso2'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_language_iso2(self):
        assert self.valid_data['language_iso2'] == 'EN'

    def test_valid_float_invalid_value(self):
        try:
            valid_float('Some string')
        except Invalid as e:
            assert e.error == "Invalid float 'Some string'"
        else:
            raise AssertionError('ValidationError not raised')

    def test_valid_float_valid_value(self):
        x = valid_float('   -50.1')
        assert x == -50.1
        x = valid_float('+25.3')
        assert x == 25.3

    def test_valid_cordinates(self):
        assert self.valid_data['xmin'] == '-20.1'
        assert self.valid_data['xmax'] == '20.1'
        assert self.valid_data['ymin'] == '-40.1'
        assert self.valid_data['ymax'] == '30.1'

    def test_xmin_only_accepts_valid_values_1(self):
        xmin = '-200'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_xmin',
                xmin=xmin,
            )
        except ValidationError as e:
            # assert that a validation error for xmin
            # is raised
            assert ([u'-180 \u2264 -200.0 \u2264 180.0'] ==
                    e.error_dict['xmin'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_xmin_only_accepts_valid_values_2(self):
        xmin = '60'
        xmax = '40'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_xmin',
                xmin=xmin,
                xmax=xmax
            )
        except ValidationError as e:
            # assert that a validation error for xmin
            # is raised
            assert ([u'-180 \u2264 60.0 \u2264 40.0'] ==
                    e.error_dict['xmin'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_xmax_only_accepts_valid_values_1(self):
        xmin = '60'
        xmax = '20'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_xmax',
                xmin=xmin,
                xmax=xmax
            )
        except ValidationError as e:
            # assert that a validation error for xmax
            # is raised
            assert ([u'60.0 \u2264 20.0 \u2264 180'] ==
                    e.error_dict['xmax'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_ymin_only_accepts_valid_values(self):
        ymin = '-100'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_ymin',
                ymin=ymin
            )
        except ValidationError as e:
            # assert that a validation error for ymin
            # is raised
            assert ([u'-90 \u2264 -100.0 \u2264 90.0'] ==
                    e.error_dict['ymin'])
        else:
            raise AssertionError('ValidationError not raised')

    def test_ymax_only_accepts_valid_values(self):
        ymin = '-60'
        ymax = '-65'
        try:
            self.lc.action.package_create(
                type='test_dataproduct',
                name='invalid_ymax',
                ymax=ymax,
                ymin=ymin
            )
        except ValidationError as e:
            # assert that a validation error for ymax
            # is raised
            assert ([u'-60.0 \u2264 -65.0 \u2264 90'] ==
                    e.error_dict['ymax'])
        else:
            raise AssertionError('ValidationError not raised')
