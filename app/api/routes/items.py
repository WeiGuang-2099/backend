from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import Item, ItemCreate, ItemUpdate

router = APIRouter()

# 模拟数据库
fake_db = {}
item_id_counter = 1


@router.get("/", response_model=List[Item])
async def get_items():
    """获取所有items"""
    return list(fake_db.values())


@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """根据ID获取item"""
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    """创建新item"""
    global item_id_counter
    new_item = Item(id=item_id_counter, **item.dict())
    fake_db[item_id_counter] = new_item
    item_id_counter += 1
    return new_item


@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    """更新item"""
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stored_item = fake_db[item_id]
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item.copy(update=update_data)
    fake_db[item_id] = updated_item
    return updated_item


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """删除item"""
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[item_id]
    return {"message": "Item deleted successfully"}
