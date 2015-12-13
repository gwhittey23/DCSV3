from data.database import DataManager,FavItem,FavCollection,FavFolder, get_or_create,FavItemCollectioLink, Base

def add_comic_fav(comic, collection_name):
    dm = DataManager()
    dm.create()
    if comic.comic_id_number is not None:
        comic = comic
        session = dm.Session()
        comic_name = '%s #%s'%(comic.series,str(comic.issue))
        new_collection = session.query(FavCollection).filter_by(name=collection_name).one()

        new_favitem = FavItem.as_unique(session,comic_id_number=comic.comic_id_number)
        new_favitem.name = comic_name
        new_favitem.comic_json = comic.comic_json
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

def add_collection(collection,sort_by,add_with_items):
    dm = DataManager()
    dm.create()
    s = dm.Session()

    fav_collection = FavCollection()
    s.add(fav_collection)
    s.flush()

    if collection.name == '':
        fav_collection.name = 'New Collection'
    else:
        fav_collection.name = collection.name
    fav_collection.sort_by = sort_by
    if add_with_items== 'True':
        if len(collection.comics)>1:
            for comic in collection.comics:
                comic_name = '%s #%s'%(comic.series,str(comic.issue))
                new_comic = FavItem.as_unique(s,comic_id_number=comic.comic_id_number)
                new_comic.name = comic_name
                new_comic.comic_json=comic.comic_json

                new_comic.fav_collection.append(fav_collection)
                s.add(new_comic)
    s.commit()
    return fav_collection.id

def get_fav_collection():
    dm = DataManager()
    dm.create()
    session = dm.Session()
    return session.query(FavCollection).order_by(FavCollection.id)

def get_single_colelction(**kwargs):
    dm = DataManager()
    dm.create()
    session = dm.Session()
    query = session.query(FavCollection).filter_by(**kwargs).join(FavCollection.fav_items).one()
    return query

def delete_collection(collection_id):
    dm = DataManager()
    dm.create()
    session = dm.Session()
    query = session.query(FavCollection).get(collection_id)
    session.delete(query)
    session.commit()

def rename_collection(collection_id,new_name,sort_by,*args):
    dm = DataManager()
    dm.create()
    session = dm.Session()
    query = session.query(FavCollection).filter_by(id=collection_id).first()
    query.name = new_name
    query.sort_by = sort_by
    session.commit()

def get_loose_fav():
    dm = DataManager()
    dm.create()
    session = dm.Session()
    query = session.query(FavItem).filter(FavItem.fav_collection.any(name='Loose Comic'))
    return query


def copy_fav_item(fav_item,fav_collection_name):
    spinner_text = fav_collection_name
    dm = DataManager()
    dm.create()
    session = dm.Session()
    fav_collection = session.query(FavCollection).filter_by(name=spinner_text).first()
    x_item = session.query(FavItem).get(fav_item.id)
    x_item.fav_collection.append(fav_collection)
    session.commit()

def move_fav_item(fav_item,fav_collection_name,target_name):
    spinner_text = fav_collection_name
    dm = DataManager()
    dm.create()
    session = dm.Session()
    fav_collection = session.query(FavCollection).filter_by(name=spinner_text).first()
    target = session.query(FavCollection).filter_by(name=target_name).first()
    current_collection_id = target.id
    x_item = session.query(FavItem).get(fav_item.id)
    x_item.fav_collection.append(target)
    x_item.fav_collection.remove(fav_collection)
    session.commit()
    return current_collection_id

def delete_fav_item(fav_item_id, fav_collection_id):
    dm = DataManager()
    dm.create()
    session = dm.Session()
    fav_collection = session.query(FavCollection).get(fav_collection_id)
    x_item = session.query(FavItem).get(fav_item_id)
    x_item.fav_collection.remove(fav_collection)
    session.commit()

def delete_tables():
    dm = DataManager()
    dm.reset_data()
    dm.create()