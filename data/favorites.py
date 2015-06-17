from data.database import DataManager,FavItem,FavCollection,FavFolder, get_or_create

def add_comic_fav(comic,):
    dm = DataManager()
    dm.create()
    if comic.comic_id_number is not None:
        comic = comic
        session = dm.Session()
        comic_name = '%s #%s'%(comic.series,str(comic.issue))
        new_collection = FavCollection.as_unique(session, name='Loose Comic')

        new_favitem = FavItem.as_unique(session,comic_id_number=comic.comic_id_number)
        new_favitem.name = comic_name
        new_favitem.fav_collection.append(new_collection)

        session.add(new_favitem)
        session.commit()


        # new_fav = get_or_create(session,FavItem,comic_id_number=comic.comic_id_number)
        # new_col = get_or_create(session,FavCollection,  name='Loose Comic')
        # obj = new_fav[0]
        # fav_collection = new_col[0]
        # print fav_collection.id
        #obj.fav_collection = fav_collection
        #session.add(obj)
       # session.commit()
    return True

def add_collection(collection):
    dm = DataManager()
    dm.create()
    s = dm.Session()

    fav_collection = FavCollection()
    s.add(fav_collection)
    if collection.name == '':
        fav_collection.name = 'New Collection'
    else:
        fav_collection.name = collection.name
    if len(collection.comics)>1:
        for comic in collection.comics:
            comic_name = '%s #%s'%(comic.series,str(comic.issue))
            new_comic = FavItem(comic_id_number = comic.comic_id_number,
                      name = comic_name
                      )
            new_comic.fav_collection.append(fav_collection)
            s.add(new_comic)
    s.commit()

def get_fav_collection():
    dm = DataManager()
    dm.create()
    session = dm.Session()
    return session.query(FavCollection).order_by(FavCollection.id)

def get_single_colelction(collection_id):
    dm = DataManager()
    dm.create()
    session = dm.Session()
    return session.query(FavCollection).filter(id==collection_id).first()

def get_loose_fav():
    dm = DataManager()
    dm.create()
    session = dm.Session()
    query = session.query(FavItem).filter(FavItem.fav_collection.any(name='Loose Comic'))
    return query