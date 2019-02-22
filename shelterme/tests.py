from shelterme.views import valid_city_state_zip
from shelterme.models import Location, Shelter
from django.urls import reverse
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.http import Http404


# Analysis -- shelterme.views.index
#
# Given a correctly formatted, valid zip code and an integer radius in miles,
# the index view will return all of the shelters within the radius of the
# zip code. Given an incorrectly formatted zip code, the splash page
# will be rendered with an appropriate error message. Given a correctly
# formatted but invalid zip code (00000), the splash page will be rendered
# with an appropriate error message. Given no zip code, the default zip


# of 36830 will be used. Given no radius, the default radius of 10 miles
# will be used.

# long long long long long long long long long long long long long long
# long long long long long long long long


# In future iterations, no given zip will use the user's previously
# searched zip.


# Parameters
# zip       string      len == 5, numeric       mandatory
# unvalidated     default='36830'
# radius    integer     .GT 0, .LE 100          mandatory
# unvalidated     default=10
#
# Happy path:
# correctly formatted, valid zip '36849' in db, valid radius
# no zip '', valid radius
# correctly formatted, valid zip not in db '32323', valid radius
# correctly formatted, valid zip '36849' in db, no radius
# no zip '', no radius
# correctly formatted, valid zip not in db '32323', no radius
#
# Sad path:
# incorrectly formatted zip 'abcde'
# correctly formatted, invalid zip '00000'
# radius out of range
# radius not an int
class IndexViewTests(TestCase):

    def setUp(self):

        self.locations = []
        self.shelters = []

        # Set up location 1 - Auburn, AL
        self.locations.append(
            Location.objects.create(
                city="Auburn", state="AL"))

        # Set up shelter - Test Shelter 1
        self.shelters.append(
            Shelter.objects.create(
                name="Test Shelter 1",
                street_addr="234 Test Street",
                location=self.locations[0],
                zip="36832",
                max_capacity=15,
                current_capacity=0,
                photo="https://images.unsplash.com/p\
                                                     hoto-1480074568708\
                                                     -e7b720bb3f09?ixlib\
                                                     =rb-1.2.1&ixid=eyJhcHBfaWQiOj\
                                                     EyMDd9&auto=format&fit=crop&w=\
                                                     1353&q=80",
                owner="NotHunter"))

        # Set up location 2 - Auburn University, AL
        self.locations.append(
            Location.objects.create(
                city="Auburn University",
                state="AL"))

        # Set up shelter - Test Shelter 2
        self.shelters.append(
            Shelter.objects.create(
                name="Test Shelter 2",
                street_addr="123 Test Street",
                location=self.locations[1],
                zip="36849",
                max_capacity=2500,
                current_capacity=0,
                photo="https://images.unsplash.com/p\
                                                     hoto-1480074568708\
                                                     -e7b720bb3f09?ixlib\
                                                     =rb-1.2.1&ixid=eyJhcHBfaWQiOj\
                                                     EyMDd9&auto=format&fit=crop&w=\
                                                     1353&q=80",
                owner="Hunter"))

        # URL
        self.url = reverse('shelterme:index')

        # Form
        self.get_form = {'zip': '', 'radius': ''}

    # Happy path
    def test_when_valid_zip_and_valid_radius_then_return_populated_index(self):
        self.get_form['zip'] = '36830'
        self.get_form['radius'] = 5
        response = self.client.get(self.url, self.get_form)
        self.assertEqual(response.status_code, 200)
        for location in self.locations:
            self.assertTrue(location in response.context['locations'])
            for shelter in location.shelter_set.all():
                self.assertContains(response, shelter.name)

    def test_when_blank_zip_then_return_splash_with_error_msg(self):
        self.get_form['zip'] = ''
        self.get_form['radius'] = 5
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_valid_zip_not_in_db_then_redirect_to_splash_with_error_msg(
            self):
        self.get_form['zip'] = '32323'
        self.get_form['radius'] = 5
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_valid_zip_and_default_radius_then_return_populated_index(
            self):
        self.get_form['zip'] = '36830'
        response = self.client.get(self.url, self.get_form)
        self.assertEqual(response.status_code, 200)
        for location in self.locations:
            self.assertTrue(location in response.context['locations'])
            for shelter in location.shelter_set.all():
                self.assertContains(response, shelter.name)

    def test_when_blank_zip_and_default_radius_then_return_splash_wi_error_msg(
            self):
        self.get_form['zip'] = ''
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_valid_zip_not_in_db_and_default_radius_then_redirect_to_splash_with_error_msg(
            self):
        self.get_form['zip'] = '32323'
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    # Sad path
    def test_when_badly_formatted_zip_then_return_splash_with_error_msg(self):
        self.get_form['zip'] = 'a'
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_invalid_zip_then_return_splash_with_error_msg(self):
        self.get_form['zip'] = '00000'
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_low_radius_then_return_splash_with_error_msg(self):
        self.get_form['zip'] = '36832'
        self.get_form['radius'] = 0
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_high_radius_then_return_splash_with_error_msg(self):
        self.get_form['zip'] = '36832'
        self.get_form['radius'] = 51
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))

    def test_when_invalid_radius_then_return_splash_with_error_msg(self):
        self.get_form['zip'] = '36832'
        self.get_form['radius'] = 'r'
        response = self.client.get(self.url, self.get_form)
        self.assertRedirects(response, reverse('shelterme:splash'))


# Analysis -- shelterme.views.edit
# Happy: Render the edit form populated with the data from the given 'id'
# Parameters
# id      integer     .GT 0       mandatory   unvalidated
#
# Happy Path:
# id
# maps to db object
# doesn't map to db object
#
# Sad Path:
#
# id
# not an int
# invalid int (<= 0)
class EditViewTests(TestCase):

    def setUp(self):
        loc = Location.objects.create(city="Auburn", state="AL")
        self.shelter = Shelter.objects.create(name="Test Shelter",
                                              street_addr="123 Test Street",
                                              location=loc,
                                              zip="35004",
                                              max_capacity=2500,
                                              current_capacity=0,
                                              photo="https://images.unsplash.com/p\
                                                     hoto-1480074568708\
                                                     -e7b720bb3f09?ixlib\
                                                     =rb-1.2.1&ixid=eyJhcHBfaWQiOj\
                                                     EyMDd9&auto=format&fit=crop&w=\
                                                     1353&q=80",
                                              owner="Hunter")

    # Happy path
    def test_id_maps_to_db_object(self):
        url = reverse('shelterme:edit', args=(self.shelter.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html_var_names = ["Shelter Name",
                          "Street Address",
                          "City",
                          "State",
                          "Zip Code",
                          "Max Capacity",
                          "Photo Link",
                          "Update"]
        for var in html_var_names:
            self.assertContains(response, var)
        self.assertEquals(response.context['shelter'], self.shelter)

    def test_id_doesnt_map_to_db_object(self):
        nonexistent_dbid = 10
        url = reverse('shelterme:edit', args=(nonexistent_dbid,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # Sad path
    def test_id_not_an_int(self):
        invalid_dbid = 'not an int, but a string'
        url = reverse('shelterme:edit', args=(invalid_dbid,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_id_invalid_int(self):
        invalid_dbid = '-1'
        url = reverse('shelterme:edit', args=(invalid_dbid,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


# Analysis -- shelterme.views.update
# Happy: Updates the shelter indicated by id using the data from the post form
# Sad: Redirects to the show page with an error message or 404
# Parameters
# id                    integer     len .GT 0           mandatory   unvalidated
# shelter_name          string      len .GT 0, .LE 50       mandatory   unvalidated
# shelter_addresss      string      len .GT 0, .LE 100       mandatory   unvalidated
# city                  string      len .GT 0, .LE 50        mandatory   unvalidated
# state                 string      len = 2, alpha  mandatory   unvalidated
# zip_code              string      len = 5, number mandatory   unvalidated
# max_cap               integer     .GT 0, .LE 10000         mandatory   unvalidated
# photourl              string      ^http[s]        optional    unvalidated
#                       default='static/shelterme/logo.png'
#
# Happy Path:
# id        shelter_name        shelter_address     city        state       zip_code        max_cap     photourl
# exist     valid               valid               exist       exist       exist           valid       http            -> updates existing shelter
# exist     valid               valid               exist       exist       exist           valid       https           -> updates existing shelter
# exist     valid               valid               exist       exist       exist           valid       blank           -> updates existing shelter
# !exist     valid               valid               exist       exist       exist           valid       valid          -> 404
# exist     valid               valid               !exist       !exist       !exist           valid       valid        -> adds new location, updates existing sheleter
# exist     valid               valid               !match       !match       !match           valid       valid        -> 404
#
# Sad Path:
#
# id not an int
# id invalid int (<= 0)
# invalid shelter name length -- empty
# invalid shelter name length -- too long
# invalid shelter address length (empty & too long)
# invalid city length
# invalid state length
# numeric state
# invalid zip code length
# alpha zip code
# invalid max capacity
# invalid photourl (no http or https)
# invalid photourl (ftp://)
# get request
#
class updateViewTests(TestCase):

    def setUp(self):
        loc = Location.objects.create(city="Auburn", state="AL")
        self.shelter_to_update = Shelter.objects.create(
            name="Test Shelter",
            street_addr="123 Test Street",
            location=loc,
            zip="35004",
            max_capacity=2500,
            current_capacity=0,
            photo="https://images.unsplash.com/p\
                                                     hoto-1480074568708\
                                                     -e7b720bb3f09?ixlib\
                                                     =rb-1.2.1&ixid=eyJhcHBfaWQiOj\
                                                     EyMDd9&auto=format&fit=crop&w=\
                                                     1353&q=80",
            owner="Hunter")
        self.http_photourl = 'http://acameraandacookbook.com/wp-content/uploads/\
            Other/8.18.2017.mell_classroom.13.jpg'
        self.https_photourl = "https://images.unsplash.com/photo-148007\
            4568708-e7b720bb3f09?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=\
                format&fit=crop&w=1353&q=80"
        self.form_params = {
            'shelter_name': 'Updated Test Shelter',
            'street_address': '123 Updated Test Lane',
            'city': self.shelter_to_update.location.city,
            'state': self.shelter_to_update.location.state,
            'zip_code': self.shelter_to_update.zip,
            'max_cap': 15,
            'photourl': self.http_photourl
        }

    def assertDatabaseUpdate(self, retr_shelter):
        self.assertEquals(retr_shelter.name, self.form_params['shelter_name'])
        self.assertEquals(
            retr_shelter.street_addr,
            self.form_params['street_address'])
        self.assertEquals(retr_shelter.location.city, self.form_params['city'])
        self.assertEquals(
            retr_shelter.location.state,
            self.form_params['state'])
        self.assertEquals(retr_shelter.zip, self.form_params['zip_code'])
        self.assertEquals(
            retr_shelter.max_capacity,
            self.form_params['max_cap'])
        self.assertEquals(retr_shelter.photo, self.form_params['photourl'])

    def test_all_valid_photourl_http(self):

        # Configure URL
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:show', args=(
                    self.shelter_to_update.id,)))
        try:
            retr_shelter = get_object_or_404(
                Shelter, id=self.shelter_to_update.id)
        except Http404:
            self.assertTrue(False)
        self.assertDatabaseUpdate(retr_shelter)

    def test_all_valid_photourl_https(self):

        # Configure URL
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['photourl'] = self.https_photourl

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:show', args=(
                    self.shelter_to_update.id,)))
        try:
            retr_shelter = get_object_or_404(
                Shelter, id=self.shelter_to_update.id)
        except Http404:
            self.assertTrue(False)
        self.assertDatabaseUpdate(retr_shelter)

    def test_all_valid_photourl_blank(self):

        # Configure URL
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['photourl'] = ''
        expected_photourl = 'shelterme/logo.png'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:show', args=(
                    self.shelter_to_update.id,)))
        try:
            retr_shelter = get_object_or_404(
                Shelter, id=self.shelter_to_update.id)
        except Http404:
            self.assertTrue(False)
        self.assertEquals(retr_shelter.name, self.form_params['shelter_name'])
        self.assertEquals(
            retr_shelter.street_addr,
            self.form_params['street_address'])
        self.assertEquals(retr_shelter.location.city, self.form_params['city'])
        self.assertEquals(
            retr_shelter.location.state,
            self.form_params['state'])
        self.assertEquals(retr_shelter.zip, self.form_params['zip_code'])
        self.assertEquals(
            retr_shelter.max_capacity,
            self.form_params['max_cap'])
        self.assertEquals(retr_shelter.photo, expected_photourl)

    def test_all_valid_nonexistent_dbid(self):

        # Configure url and new data into form parameters
        invalid_dbid = 1000
        url = reverse('shelterme:update', args=(invalid_dbid,))

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertEquals(response.status_code, 404)

    def test_all_valid_location_not_in_db(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['city'] = 'Moody'
        self.form_params['state'] = 'AL'
        self.form_params['zip'] = '35004'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:show', args=(
                    self.shelter_to_update.id,)))
        try:
            retr_shelter = get_object_or_404(
                Shelter, id=self.shelter_to_update.id)
        except Http404:
            self.assertTrue(False)
        self.assertDatabaseUpdate(retr_shelter)

    def test_invalid_location(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['city'] = 'Nonexistent'
        self.form_params['state'] = 'AL'
        self.form_params['zip'] = '35004'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_id_not_an_int(self):

        # Configure url and new data into form parameters
        invalid_dbid = "not an int"
        url = reverse('shelterme:update', args=(invalid_dbid,))

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertEquals(response.status_code, 404)

    def test_id_invalid_int(self):

        # Configure url and new data into form parameters
        invalid_dbid = -1
        url = reverse('shelterme:update', args=(invalid_dbid,))

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertEquals(response.status_code, 404)

    def test_empty_name(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['shelter_name'] = ''

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_too_long_name(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['city'] = 'A' * 51

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_empty_address(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['street_address'] = ''

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_too_long_address(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['street_address'] = 'A' * 101

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_empty_city(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['city'] = ''

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_too_long_city(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['city'] = 'A' * 51

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_long_state(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['state'] = 'ALA'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_empty_state(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['state'] = ''

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_numeric_state(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['state'] = '23'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_max_cap_not_an_int(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['max_cap'] = 'not an int'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_max_cap_0(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['max_cap'] = 0

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_max_cap_10000(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['max_cap'] = 10001

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_photourl_no_http_or_https(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))
        self.form_params['photourl'] = 'google.com'

        # Send request
        response = self.client.post(url, self.form_params)

        # Assess correctness
        self.assertRedirects(
            response, reverse(
                'shelterme:edit', args=(
                    self.shelter_to_update.id,)))

    def test_get(self):

        # Configure url and new data into form parameters
        url = reverse('shelterme:update', args=(self.shelter_to_update.id,))

        # Send request
        response = self.client.get(url)

        # Assess correctness
        self.assertEqual(response.status_code, 404)

# Analysis -- shelterme.views.delete
# Parameters
#   id
#   type: int
#   range: .GE. 0
#   mandatory
#   unvalidated
# Happy path:
# valid id
#
# Sad path:
# no id
# wrong type id
# Below range id
# get request


class DeleteViewTests(TestCase):

    def setUp(self):
        self.loc = Location(city='Auburn', state='AL')
        self.loc.save()

        self.shelter_to_delete = Shelter(
            name='Test Shelter',
            street_addr='123 Test Street',
            location=self.loc,
            zip='36830',
            max_capacity=20,
            photo='http://acameraandacookbook.com/wp-content/\
                uploads/Other/8.18.2017.mell_classroom.13.jpg',
            owner='Hunter')
        self.shelter_to_delete.save()

    def test_when_valid_id_then_delete_redirect_index(self):

        # Configure URL
        url = reverse('shelterme:delete', args=(self.shelter_to_delete.id,))

        # Send request
        self.client.post(url)

        # Assess correctness
        with self.assertRaises(Http404):
            get_object_or_404(Shelter, id=self.shelter_to_delete.id)
        # self.assertRedirects(response, reverse('shelterme:index'))


# Analysis -- shelterme.views.edit
# Happy: Render the edit form populated with the data from the given 'id'
# Sad: Redirects to the show page with an error message
# Analysis -- shelterme.views.valid_city_state_zip
# Returns True if the given city and state match the given zip code
# Parameters
#       city        string      alpha               mandatory       unvalidated
#       state       string      2-letter alpha      mandatory       unvalidated
#       zip         string         5-digit #           mandatory    unvalidated
#
# Happy Path:
# city      state       zip
# good      good        good
# good      good        wrong
# good      wrong       good
# good      wrong       wrong
# wrong     good        good
# wrong     good        wrong
# wrong     wrong       good
# wrong     wrong       wrong
#
# Sad Path:
#
# no parameters
# empty city, not empty state and not empty zip
# not empty city, empty state, not empty zip
# not empty city, not empty state, empty zip
# not string city
# not string state
# not int zip
class ValidateCityStateZIPTests(TestCase):

    # Happy path:
    def test_good_city_state_zip(self):
        city = "Auburn"
        state = "AL"
        zip = "36830"
        expected = True
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_goodcity_goodstate_wrongzip(self):
        city = "Auburn"
        state = "AL"
        zip = "35004"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_goodcity_wrongstate_goodzip(self):
        city = "Auburn"
        state = "CO"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_goodcity_wrongstate_wrongzip(self):
        city = "Auburn"
        state = "CO"
        zip = "35004"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_wrongcity_goodstate_goodzip(self):
        city = "Birmingham"
        state = "AL"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_wrongcity_goodstate_wrongzip(self):
        city = "Birmingham"
        state = "AL"
        zip = "32845"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_wrongcity_wrongstate_goodzip(self):
        city = "Birmingham"
        state = "CO"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_wrongcity_wrongstate_wrongzip(self):
        city = "Auburn"
        state = "CO"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    # # Sad path:
    def test_empty_params(self):
        city = ""
        state = ""
        zip = ""
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_empty_city(self):
        city = ""
        state = "AL"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_empty_state(self):
        city = "Auburn"
        state = ""
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_empty_zip(self):
        city = "Auburn"
        state = "AL"
        zip = ""
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_invalid_city(self):
        city = "alksdfj,xcmnvopweihrlskdjfn12345678654"
        state = "AL"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_invalid_state(self):
        city = "Auburn"
        state = "alksdfj,xcmnvopweihrlskdjfn12345678654"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_invalid_zip(self):
        city = "Auburn"
        state = "AL"
        zip = "alksdfj,xcmnvopweihrlskdjfn12345678654"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)

    def test_not_two_letter_state(self):
        city = "Auburn"
        state = "Alabama"
        zip = "36830"
        expected = False
        actual = valid_city_state_zip(city, state, zip)
        self.assertIs(expected, actual)
