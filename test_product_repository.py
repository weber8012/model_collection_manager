from repositories.product_repository import ProductRepository


# 1. 新增測試商品
product_id = ProductRepository.add_product(
    name="MG RX-78-2 Ver.2.0",
    brand="Gundam",
    series="Master Grade",
    manufacturer="BANDAI",
    product_type="組裝模型",
    scale="1/100",
    msrp=1800,
    memo="Repository 測試資料"
)

print("新增商品編號：", product_id)


# 2. 查詢單筆商品
product = ProductRepository.get_product_by_id(1)
print("商品資料：", product)


# 3. 搜尋商品
results = ProductRepository.search_products("RX-78")
print("搜尋結果：", results)


# 4. 修改商品
success = ProductRepository.update_product(
    product_id,
    品牌="BANDAI",
    備註="已完成修改測試"
)
print("修改成功：", success)


# 5. 查詢全部商品
products = ProductRepository.get_all_products()

for item in products:
    print(item)


# 6. 刪除測試商品（確認需要清除時再取消註解）
success = ProductRepository.delete_product(1)
print("刪除成功：", success)