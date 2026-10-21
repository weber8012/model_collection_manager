from repositories.product_repository import ProductRepository
from repositories.preorder_repository import PreorderRepository


# ============================================================
# 1. 建立測試商品
# ============================================================

product_id = ProductRepository.add_product(
    name="預購測試模型",
    brand="測試品牌",
    series="測試系列",
    product_type="塑膠組裝模型",
    msrp=1500,
    memo="預購 Repository 測試用"
)

print("建立測試商品成功")
print("商品編號：", product_id)


# ============================================================
# 2. 新增預購
# ============================================================

preorder_id = PreorderRepository.add_preorder(
    product_id=product_id,
    preorder_date="2026-10-21",
    expected_release_date="2026-12-01",
    expected_arrival_date="2026-12-10",
    quantity=2,
    preorder_price=1200,
    deposit=500,
    shipping_fee=100,
    paid_balance=0,
    preorder_status="預購中",
    payment_status="部分付款",
    order_number="TEST-001",
    memo="Repository 測試資料"
)

print("\n新增預購成功")
print("預購編號：", preorder_id)


# ============================================================
# 3. 查詢單筆
# ============================================================

preorder = PreorderRepository.get_preorder_by_id(1)

print("\n單筆預購資料：")
print(preorder)


# ============================================================
# 4. 計算金額
# ============================================================

total = PreorderRepository.calculate_total(preorder_id)
paid = PreorderRepository.calculate_paid_amount(preorder_id)
remaining = PreorderRepository.calculate_remaining_amount(preorder_id)

print("\n金額計算：")
print("預購總金額：", total)
print("已付款：", paid)
print("待付款：", remaining)


# ============================================================
# 5. 修改
# ============================================================

success = PreorderRepository.update_preorder(
    preorder_id,
    付款狀態="已付款",
    已付尾款=2000
)

print("\n修改結果：", success)


# ============================================================
# 6. 再次計算
# ============================================================

paid = PreorderRepository.calculate_paid_amount(preorder_id)
remaining = PreorderRepository.calculate_remaining_amount(preorder_id)

print("\n修改付款資料後：")
print("已付款：", paid)
print("待付款：", remaining)


# ============================================================
# 7. 刪除測試資料
# ============================================================

# 測試完全確認沒問題後，再取消下面兩行註解

PreorderRepository.delete_preorder(preorder_id)
ProductRepository.delete_product(product_id)