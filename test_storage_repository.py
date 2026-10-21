
from repositories.storage_repository import StorageRepository


# 1. 建立收納位置
cabinet_id = StorageRepository.add_location(
    name="A櫃",
    description="模型收納櫃",
    capacity=30,
)

shelf_id = StorageRepository.add_location(
    name="A-01",
    parent_id=cabinet_id,
    description="A櫃第一層",
    capacity=10,
)

print("A櫃編號：", cabinet_id)
print("A-01 編號：", shelf_id)


# 2. 查詢所有位置
print("\n所有收納位置：")

for location in StorageRepository.get_all_locations():
    print(location)


# 3. 查詢階層
print("\n收納位置階層：")

for location in StorageRepository.get_location_tree():
    print(location)


# 4. 修改位置
success = StorageRepository.update_location(
    shelf_id,
    位置描述="A櫃第一層，放置未組裝模型",
)

print("\n修改成功：", success)


# 5. 查詢位置內的持有品
items = StorageRepository.get_items_in_location(shelf_id)

print("\nA-01 內的持有品：")

for item in items:
    print(item)


# 6. 刪除測試位置
# 確認需要清除測試資料時，再取消下列註解。
StorageRepository.delete_location(shelf_id)
StorageRepository.delete_location(cabinet_id)
