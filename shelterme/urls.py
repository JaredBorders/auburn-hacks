from shelterme import views
from django.urls import path

app_name = 'shelterme'
urlpatterns = [

    # Splash page URL
    path('', views.splash, name='splash'),

    # Index page URL
    path('shelters', views.index_or_create, name='index'),

    # New page URL
    path('shelters/new', views.new, name='new'),

    # Create page URL
    path('shelters', views.index_or_create, name='create'),

    # Show page URL
    path('shelters/<id>', views.show, name='show'),

    # Edit page URL
    path('shelters/<id>/edit', views.edit, name='edit'),

    # Update page URL
    path('shelters/<id>/update', views.update, name='update'),

    # Delete page URL
    path('shelters/<id>/delete', views.delete, name='delete'),

    # New comment page URL
    path('shelters/<id>/comments/new', views.comment_new, name='comment_new'),

    # Create comment page URL
    path(
        'shelters/<id>/comments',
        views.comment_create,
        name='comment_create'),

    # Edit comment page URL
    path('shelters/<id>/comments/<comment_id>/edit',
         views.comment_edit, name='comment_edit'),

    # Update comment page URL
    path(
        'shelters/<id>/comments/<comment_id>/update',
        views.comment_update,
        name='comment_update'),

    # Delete comment page URL
    path(
        'shelters/<id>/comments/<comment_id>/delete',
        views.comment_delete,
        name='comment_delete')

]
