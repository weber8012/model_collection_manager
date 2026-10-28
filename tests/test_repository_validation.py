# -*- coding: utf-8 -*-

from repositories.product_repository import ProductRepository
from repositories.collection_repository import CollectionRepository
from repositories.preorder_repository import PreorderRepository
from repositories.store_repository import StoreRepository


def test_product_empty_name():
    print("\n[測試] 商品名稱不可為空")

    try:
        ProductRepository.add_product("")
        print("❌ 測試失敗：空白商品名稱竟然可以建立")
    except Exception:
        print("✅ 通過")


def test_collection_invalid_quantity():
    print("\n[測試] 收藏數量必須大於 0")

    products = ProductRepository.get_all_products()

    if not products:
        print("⚠️ 跳過：目前沒有商品資料")
        return

    product_id = products[0]["商品編號"]

    try:
        CollectionRepository.add_item(
            product_id=product_id,
            quantity=0
        )
        print("❌ 測試失敗：數量 0 竟然可以建立")
    except Exception:
        print("✅ 通過")


def test_collection_negative_price():
    print("\n[測試] 收藏購買價格不可為負數")

    products = ProductRepository.get_all_products()

    if not products:
        print("⚠️ 跳過：目前沒有商品資料")
        return

    product_id = products[0]["商品編號"]

    try:
        CollectionRepository.add_item(
            product_id=product_id,
            purchase_price=-1
        )
        print("❌ 測試失敗：負數價格竟然可以建立")
    except Exception:
        print("✅ 通過")


def test_preorder_invalid_quantity():
    print("\n[測試] 預購數量必須大於 0")

    products = ProductRepository.get_all_products()

    if not products:
        print("⚠️ 跳過：目前沒有商品資料")
        return

    product_id = products[0]["商品編號"]

    try:
        PreorderRepository.add_preorder(
            product_id=product_id,
            quantity=0
        )
        print("❌ 測試失敗：預購數量 0 竟然可以建立")
    except Exception:
        print("✅ 通過")


def test_preorder_negative_deposit():
    print("\n[測試] 預購訂金不可為負數")

    products = ProductRepository.get_all_products()

    if not products:
        print("⚠️ 跳過：目前沒有商品資料")
        return

    product_id = products[0]["商品編號"]

    try:
        PreorderRepository.add_preorder(
            product_id=product_id,
            deposit=-1
        )
        print("❌ 測試失敗：負數訂金竟然可以建立")
    except Exception:
        print("✅ 通過")


def test_store_empty_name():
    print("\n[測試] 店家名稱不可為空")

    try:
        StoreRepository.add_store("")
        print("❌ 測試失敗：空白店家名稱竟然可以建立")
    except Exception:
        print("✅ 通過")


def main():
    print("=" * 50)
    print("Repository 資料驗證測試")
    print("=" * 50)

    test_product_empty_name()
    test_collection_invalid_quantity()
    test_collection_negative_price()
    test_preorder_invalid_quantity()
    test_preorder_negative_deposit()
    test_store_empty_name()

    print("\n" + "=" * 50)
    print("測試結束")
    print("=" * 50)


if __name__ == "__main__":
    main()
