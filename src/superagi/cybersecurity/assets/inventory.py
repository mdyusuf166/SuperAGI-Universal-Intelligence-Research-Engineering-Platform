class AssetInventory:
 def __init__(self):self._items={}
 def register(self,asset):self._items[asset.id]=asset;return asset
 def remove(self,id):return self._items.pop(id,None)
 def get(self,id):return self._items.get(id)
 def list(self):return list(self._items.values())
 def search(self,q):return [x for x in self._items.values() if q.lower() in x.name.lower()]
