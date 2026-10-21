
from repositories.product_repository import ProductRepository
from repositories.collection_repository import CollectionRepository


# 1. 確認是否有商品
products = ProductRepository.get_all_products()

if not products:
    product_id = ProductRepository.add_product(
        name="測試用 MG RX-78-2",
        brand="BANDAI",
        product_type="組裝模型",
        scale="1/100",
    )
else:
    product_id = products[0]["商品編號"]

print("使用商品編號：", product_id)


# 2. 新增持有品
item_id = CollectionRepository.add_item(
    product_id=product_id,
    status="未開始",
    condition="全新",
    purchase_price=1500,
    quantity=1,
    is_opened=0,
    is_completed=0,
    memo="山積管理測試",
)

print("新增持有品編號：", item_id)


# 3. 查詢持有品
item = CollectionRepository.get_item_by_id(1)
print("持有品資料：", item)


# 4. 修改狀態
success = CollectionRepository.update_item(
    item_id,
    收藏狀態="製作中",
    是否開封=1,
)
print("修改成功：", success)


# 5. 查詢製作中的持有品
print(
    "製作中：",
    CollectionRepository.get_items_by_status("製作中")
)


# 6. 統計
print("收藏統計：", CollectionRepository.get_statistics())


# 7. 刪除測試持有品（確認需要清除時再取消註解）
CollectionRepository.delete_item(1)
