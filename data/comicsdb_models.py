from peewee import *
import os
database = SqliteDatabase('data/cachedb.sqlite', **{})




class BaseModel(Model):
    class Meta:
        database = database

class Characters(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'characters'

class Comics(BaseModel):
    added_ts = DateTimeField(null=True)
    comments = TextField(null=True)  # VARCHAR
    date = DateTimeField(null=True)
    day = IntegerField(null=True)
    imprint = CharField(null=True)  # VARCHAR
    issue = CharField(null=True)  # VARCHAR
    lastread_page = IntegerField(null=True)
    lastread_ts = DateTimeField(null=True)
    mod_ts = DateTimeField(null=True)
    month = IntegerField(null=True)
    year = IntegerField(null=True)
    page_count = IntegerField(null=True)
    publisher = CharField(null=True)  # VARCHAR
    series = CharField(null=True)  # VARCHAR
    title = CharField(null=True)  # VARCHAR
    volume = IntegerField(null=True)
    weblink = CharField(null=True)  # VARCHAR
    year = IntegerField(null=True)
    comicstream_number = PrimaryKeyField(null=False, unique=True)

    class Meta:
        db_table = 'comics'



class ComicsCharacters(BaseModel):
    character = ForeignKeyField(db_column='character_id', null=True, rel_model=Characters, to_field='id')
    comic = ForeignKeyField(db_column='comic_comicstream_number', null=True, rel_model=Comics, to_field='comicstream_number')

    class Meta:
        db_table = 'comics_characters'

class Generictags(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'generictags'
0
class ComicsGenerictags(BaseModel):
    comic = ForeignKeyField(db_column='comic_comicstream_number', null=True, rel_model=Comics, to_field='comicstream_number')
    generictags = ForeignKeyField(db_column='generictags_id', null=True, rel_model=Generictags, to_field='id')

    class Meta:
        db_table = 'comics_generictags'

class Genres(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'genres'

class ComicsGenres(BaseModel):
    comic = ForeignKeyField(db_column='comic_comicstream_number', null=True, rel_model=Comics, to_field='comicstream_number')
    genre = ForeignKeyField(db_column='genre_id', null=True, rel_model=Genres, to_field='id')

    class Meta:
        db_table = 'comics_genres'

class Locations(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'locations'

class ComicsLocations(BaseModel):
    comic = ForeignKeyField(db_column='comic_comicstream_number', null=True, rel_model=Comics, to_field='comicstream_number')
    location = ForeignKeyField(db_column='location_id', null=True, rel_model=Locations, to_field='id')

    class Meta:
        db_table = 'comics_locations'

class Storyarcs(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'storyarcs'

class ComicsStoryarcs(BaseModel):
    comic = ForeignKeyField(db_column='comic_comicstream_number', null=True, rel_model=Comics, to_field='comicstream_number')
    storyarc = ForeignKeyField(db_column='storyarc_id', null=True, rel_model=Storyarcs, to_field='id')

    class Meta:
        db_table = 'comics_storyarcs'

class Teams(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'teams'

class ComicsTeams(BaseModel):
    comic = ForeignKeyField(db_column='comic_comicstream_number', null=True, rel_model=Comics, to_field='comicstream_number')
    team = ForeignKeyField(db_column='team_id', null=True, rel_model=Teams, to_field='id')

    class Meta:
        db_table = 'comics_teams'

class Persons(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'persons'

class Roles(BaseModel):
    name = CharField(null=True, unique=True)  # VARCHAR

    class Meta:
        db_table = 'roles'

class Credits(BaseModel):
    comic = ForeignKeyField(db_column='comic_comicstream_number', rel_model=Comics, to_field='comicstream_number')
    person = ForeignKeyField(db_column='person_id', rel_model=Persons, to_field='id')
    role = ForeignKeyField(db_column='role_id', rel_model=Roles, to_field='id')

    class Meta:
        db_table = 'credits'
        primary_key = CompositeKey('comic', 'person', 'role')
        db_table = 'dbid'
        db_table = 'deletedcomics'

class SeriesList(BaseModel):
    name = CharField(null=True)

class DbInfo(BaseModel):
    last_updated = DateTimeField(null=True)

