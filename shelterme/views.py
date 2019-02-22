from shelterme.models import Location, Shelter, Comment
from ast import literal_eval
from pyzipcode import ZipCodeDatabase
from zipcodes import matching, is_real
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404
from django.contrib import messages

# TODO: write new view tests


# Create your views here.
def splash(request):
    return render(request, 'shelterme/splash.html')


# Shelter -- index (GET) & create (POST)
def index_or_create(request):
    # Shelter - index view
    # Shows an index of all shelters
    if request.method == 'GET':

        # Get data from the get request
        try:
            zip_code = request.GET['zip'][:5]
        except KeyError:
            zip_code = '36830'  # temporary, eventually we will use the user's last queried zip
        try:
            radius = request.GET['radius']
        except KeyError:
            radius = 10

        # Scrub data
        # Scrub zip
        # If the zip code is empty, return the splash page with an error
        # message
        if not zip_code:
            messages.error(request, 'Invalid ZIP. Please try again.')
            return redirect('shelterme:splash')

        # If the zip code is not in a valid form or real, return the splash
        # page with an error message
        try:
            if not is_real(zip_code):
                messages.error(request, 'Invalid ZIP. Please try again.')
                return redirect('shelterme:splash')
        except ValueError:
            messages.error(request, 'Invalid ZIP. Please try again.')
            return redirect('shelterme:splash')

        # Scrub radius
        if not radius:
            radius = 10
        else:
            try:
                radius = int(radius)
            except ValueError:
                messages.error(request, 'Invalid radius. Please try again.')
                return redirect('shelterme:splash')
            if radius < 1 or radius > 50:
                messages.error(
                    request, 'Radius can\'t be less than 1 or greater than 50. \
                              Please try again.')
                return redirect('shelterme:splash')

        # Retrieve list of locations within radius of zip
        locs = get_locations_within_radius(zip_code, radius)

        # Retrieve locations from the db
        locations = []
        for loc in locs:
            tmp_loc = Location.objects.filter(
                city=loc['city'], state=loc['state'])
            if tmp_loc:
                locations.append(tmp_loc[0])
        if not locations:
            messages.error(
                request, 'We don\'t have your location in our database. \
                          Sorry!')
            return redirect('shelterme:splash')

        # Render template with all of the location's shelter data
        return render(request, 'shelterme/index.html',
                      {'locations': locations})

    # Shelter -- create view
    # Creates a new shelter with data from the new view form
    elif request.method == 'POST':  # NEXT

        # TODO Authentication

        # Get data from post form to create a new shelter
        name = request.POST['shelter_name']
        street_addr = request.POST['street_address']
        city = request.POST['city']
        city = city[0].upper() + city[1:len(city)].lower()
        state = request.POST['state']
        state = state.upper()
        zip = request.POST['zip_code']
        max_cap = request.POST['max_capacity']
        photourl = request.POST['photourl']

        # Retrieve location from the db
        try:
            loc = get_object_or_404(Location, city=city, state=state)

        # If the location doesn't exist:
        except Http404:

            # If the location is valid: add it to the db
            if valid_city_state_zip(city, state, zip):
                loc = Location(city=city, state=state)
                loc.save()

            # Else -- the location isn't valid -- return an error message
            # and redirect to index page
            else:
                messages.error(request, 'Unable to locate the location. \
                                         What a shame!')
                return redirect('splash')
                # TODO eventually we want to redirect to the index page
                # of the user's last zip query

        # Create new shelter
        shelter = Shelter(name=name, street_addr=street_addr, location=loc,
                          zip=zip, max_capacity=max_cap, current_capacity=0,
                          photo=photourl, owner='User')
        shelter.save()

        # Redirect to show page
        return redirect('shelterme:show', id=shelter.id)

    # Neither GET nor POST -- return error
    else:
        messages.error('This URL only responds to GET and PUT requests.')
        return redirect('splash')


# Shelter -- New view
def new(request):
    return render(request, 'shelterme/create.html')


# Shelter -- Show view
def show(request, id):
    shelter = get_object_or_404(Shelter, id=id)
    return render(request, 'shelterme/show.html', {'shelter': shelter})


# Shelter -- Edit view
def edit(request, id):

    # Ensure the given id is an int
    try:
        int(id)
    except ValueError:
        raise Http404

    # Retrieve shelter from db
    shelter = get_object_or_404(Shelter, id=id)

    # Render the edit form
    return render(request, 'shelterme/edit.html', {'shelter': shelter})


# Shelter -- update view
def update(request, id):

    # Ensure post request
    if request.method == 'POST':

        # Scrub id
        try:
            int(id)
        except ValueError:
            raise Http404

        # Retrieve shelter from db -- 404 if nonexistent
        shelter = get_object_or_404(Shelter, id=id)

        # Read shelter data
        name = request.POST['shelter_name']
        street_addr = request.POST['street_address']
        city = request.POST['city']
        state = request.POST['state']
        zip = request.POST['zip_code']
        max_capacity = request.POST['max_cap']
        photo = request.POST['photourl']

        # Scrub shelter data
        # Scrub name
        if not name:
            messages.error(request, 'Shelter name can\'t be empty.')
            return redirect('shelterme:edit', id=id)
        if len(name) > 50:
            messages.error(request, 'Shelter name must be shorter than \
                                     51 characters.')
            return redirect('shelterme:edit', id=id)

        # Scrub street address
        if not street_addr:
            messages.error(request, 'Street address can\'t be empty.')
            return redirect('shelterme:edit', id=id)
        if len(street_addr) > 100:
            messages.error(request, 'Street address must be shorter than 101 \
                                     characters.')
            return redirect('shelterme:edit', id=id)

        # Scrub max capacity
        try:
            max_capacity = int(max_capacity)
        except ValueError:
            messages.error(request, 'Maximum capacity cannot be blank.')
            return redirect('shelterme:edit', id=id)
        if max_capacity <= 0 or max_capacity > 10000:
            messages.error(request, 'Maximum capacity must be between 0 and \
                                     10,000.')
            return redirect('shelterme:edit', id=id)

        # Scrub location
        try:
            loc = get_object_or_404(Location, city=city, state=state)
        except Http404:
            if not valid_city_state_zip(city, state, zip):
                messages.error(request, 'City, State, and ZIP do not match. \
                                         Please try again.')
                return redirect('shelterme:edit', id=id)

            else:
                loc = Location(city=city, state=state)
                loc.save()

        # Scrub photo url
        if not photo:
            photo = 'shelterme/logo.png'
        elif photo[0:7] != 'http://' and photo[0:8] != 'https://':
            messages.error(request, 'Invalid Photo URL.')
            return redirect('shelterme:edit', id=id)

        # Update shelter data
        shelter.name = name
        shelter.street_addr = street_addr
        shelter.location = loc
        shelter.zip = zip
        shelter.max_capacity = max_capacity
        shelter.photo = photo

        # Save shelter to the db
        shelter.save()

        # Render the show page for the shelter
        return redirect('shelterme:show', id=shelter.id)

    # Not a POST request -- 404
    else:
        raise Http404


# Shelter -- delete view
def delete(request, id):

    # TODO add authentication

    # Retrieve shelter from db using id
    shelter = get_object_or_404(Shelter, id=id)

    # Delete the shelter
    shelter.delete()

    # Redirect to the index page
    return redirect('shelterme:index')


def comment_new(request, id):
    shelter = get_object_or_404(Shelter, id=id)
    return render(request, 'shelterme/comment_new.html', {'shelter': shelter})


def comment_create(request, id):
    content = request.POST['content']
    shelter = get_object_or_404(Shelter, id=id)
    comment = Comment(author='Hunter', content=content, shelter=shelter)
    comment.save()
    return redirect('shelterme:show', id=id)


def comment_edit(request, id, comment_id):
    shelter = get_object_or_404(Shelter, id=id)
    comment = get_object_or_404(Comment, id=comment_id)
    return render(request, 'shelterme/comment_edit.html',
                  {'shelter': shelter, 'comment': comment})


def comment_update(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    content = request.POST['content']
    comment.content = content
    comment.save()
    return redirect('shelterme:show', id=id)


def comment_delete(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect('shelterme:show', id=id)


# Returns True if the given city and state match the given zip code
# Returns False otherwise
def valid_city_state_zip(city, state, zip):

    # Ensure none of the fields are blank
    if not city or not state or not zip:
        return False

    # Look up the zip and extract the city and state
    try:
        zip_info = matching(str(zip))
    except ValueError:
        return False
    if not zip_info:
        return False
    zip_info = zip_info[0]
    zip_city = zip_info['city']
    zip_state = zip_info['state']

    # Check validity
    if city.lower() == zip_city.lower() and state.lower() == zip_state.lower():
        return True
    return False


def get_locations_within_radius(zip_code, radius):
    zips = []
    for z in ZipCodeDatabase().get_zipcodes_around_radius(zip_code, radius):
        zips.append(z.zip)

    tmp_locations = []
    for z in zips:
        zip_info = matching(z)
        zip_info = zip_info[0]
        city = ''
        tmp_city = str(zip_info['city'])
        for word in tmp_city.split(' '):
            city += word[0].upper() + word[1:len(word)].lower() + ' '
        state = str(zip_info['state']).upper()
        tmp_locations.append(
            '{"city": "' + city.strip() + '", "state": "' + state + '"}')
    tmp_locations = set(tmp_locations)
    locations = []
    for location in tmp_locations:
        locations.append(literal_eval(location))
    return locations
