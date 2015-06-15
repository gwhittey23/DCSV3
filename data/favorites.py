from data.database import DataManager,FavItem,FavCollection,FavFolder

def add_comic_fav(comic,):
    dm = DataManager()
    dm.create()
    if comic.comic_id_number is not None:
        comic = comic
        session = dm.Session()
        comic_name = '%s #%s'%(comic.series,str(comic.issue))
        obj = FavItem(comic_id_number=comic.comic_id_number,
                      name=comic_name
                      )
        session.add(obj)
        session.commit()
    return True
