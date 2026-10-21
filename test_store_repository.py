
from repositories.store_repository import StoreRepository


# 1. 新增測試店家
store_id = StoreRepository.add_store("測試模型店")

print("新增店家編號：", store_id)


# 2. 查詢全部店家
print("\n全部店家：")
for store in StoreRepository.get_all_stores():
    print(store)


# 3. 查詢單筆店家
print("\n單筆店家：")
print(StoreRepository.get_store_by_id(store_id))


# 4. 搜尋店家
print("\n搜尋結果：")
print(StoreRepository.search_stores("測試"))


# 5. 修改店家名稱
success = StoreRepository.update_store(
    store_id,
    "測試模型店（已修改）"
)
print("\n修改結果：", success)


# 6. 再次查詢
print("\n修改後資料：")
print(StoreRepository.get_store_by_id(store_id))


# 7. 刪除測試店家
# 確認測試完成後，再取消以下兩行註解
#
success = StoreRepository.delete_store(store_id)
print("\n刪除結果：", success)
