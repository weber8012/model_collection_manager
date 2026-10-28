from repositories.product_repository import ProductRepository
from repositories.collection_repository import CollectionRepository
from repositories.preorder_repository import PreorderRepository
from repositories.store_repository import StoreRepository
from repositories.storage_repository import StorageRepository


def print_result(test_name, passed):
    if passed:
        print(f"✅ {test_name}：通過")
    else:
        print(f"❌ {test_name}：失敗")


def test_product_cascade():
    print("\n=== 測試商品 CASCADE ===")

    product_id = ProductRepository.add_product(
        "TEST_關聯測試商品"
    )

    collection_id = CollectionRepository.add_item(
        product_id=product_id
    )

    preorder_id = PreorderRepository.add_preorder(
        product_id=product_id
    )

    print(f"測試商品編號：{product_id}")
    print(f"測試收藏編號：{collection_id}")
    print(f"測試預購編號：{preorder_id}")

    # 確認資料建立成功
    collection_before = (
        CollectionRepository.get_item_by_id(collection_id)
    )

    preorder_before = (
        PreorderRepository.get_preorder_by_id(preorder_id)
    )

    print_result(
        "建立測試收藏",
        collection_before is not None
    )

    print_result(
        "建立測試預購",
        preorder_before is not None
    )

    # 刪除商品
    ProductRepository.delete_product(product_id)

    # 確認收藏與預購是否一起刪除
    collection_after = (
        CollectionRepository.get_item_by_id(collection_id)
    )

    preorder_after = (
        PreorderRepository.get_preorder_by_id(preorder_id)
    )

    print_result(
        "商品刪除後收藏 CASCADE",
        collection_after is None
    )

    print_result(
        "商品刪除後預購 CASCADE",
        preorder_after is None
    )


def test_store_set_null():
    print("\n=== 測試店家 SET NULL ===")

    product_id = ProductRepository.add_product(
        "TEST_店家關聯測試商品"
    )

    store_id = StoreRepository.add_store(
        "TEST_關聯測試店家"
    )

    preorder_id = PreorderRepository.add_preorder(
        product_id=product_id,
        store_id=store_id
    )

    preorder_before = (
        PreorderRepository.get_preorder_by_id(preorder_id)
    )

    print(f"測試店家編號：{store_id}")
    print(f"測試預購編號：{preorder_id}")

    print_result(
        "預購建立成功",
        preorder_before is not None
    )

    # 刪除店家
    StoreRepository.delete_store(store_id)

    preorder_after = (
        PreorderRepository.get_preorder_by_id(preorder_id)
    )

    if preorder_after is None:
        print_result(
            "刪除店家後預購仍存在",
            False
        )
    else:
        print_result(
            "刪除店家後預購仍存在",
            True
        )

        print_result(
            "預購店家編號變成 NULL",
            preorder_after.get("店家編號") is None
        )

    # 清理測試資料
    PreorderRepository.delete_preorder(preorder_id)
    ProductRepository.delete_product(product_id)


def test_storage_set_null():
    print("\n=== 測試收納位置 SET NULL ===")

    product_id = ProductRepository.add_product(
        "TEST_收納關聯測試商品"
    )

    location_id = StorageRepository.add_location(
        "TEST_關聯測試位置"
    )

    collection_id = CollectionRepository.add_item(
        product_id=product_id,
        storage_location_id=location_id
    )

    collection_before = (
        CollectionRepository.get_item_by_id(collection_id)
    )

    print(f"測試位置編號：{location_id}")
    print(f"測試收藏編號：{collection_id}")

    print_result(
        "收藏建立成功",
        collection_before is not None
    )

    # 刪除收納位置
    StorageRepository.delete_location(location_id)

    collection_after = (
        CollectionRepository.get_item_by_id(collection_id)
    )

    if collection_after is None:
        print_result(
            "刪除收納位置後收藏仍存在",
            False
        )
    else:
        print_result(
            "刪除收納位置後收藏仍存在",
            True
        )

        print_result(
            "收藏收納位置變成 NULL",
            collection_after.get("收納位置編號") is None
        )

    # 清理測試資料
    CollectionRepository.delete_item(collection_id)
    ProductRepository.delete_product(product_id)


def test_storage_parent_set_null():
    print("\n=== 測試子收納位置 SET NULL ===")

    parent_id = StorageRepository.add_location(
        "TEST_父位置"
    )

    child_id = StorageRepository.add_location(
        "TEST_子位置",
        parent_id=parent_id
    )

    child_before = StorageRepository.get_location_by_id(
        child_id
    )

    print(f"測試父位置編號：{parent_id}")
    print(f"測試子位置編號：{child_id}")

    print_result(
        "子位置建立成功",
        child_before is not None
    )

    # 刪除父位置
    StorageRepository.delete_location(parent_id)

    child_after = StorageRepository.get_location_by_id(
        child_id
    )

    if child_after is None:
        print_result(
            "刪除父位置後子位置仍存在",
            False
        )
    else:
        print_result(
            "刪除父位置後子位置仍存在",
            True
        )

        print_result(
            "子位置父編號變成 NULL",
            child_after.get("上層位置編號") is None
        )

        # 清理子位置
        StorageRepository.delete_location(child_id)


def main():
    print("=" * 60)
    print("Repository 關聯資料刪除測試")
    print("=" * 60)

    try:
        test_product_cascade()
        test_store_set_null()
        test_storage_set_null()
        test_storage_parent_set_null()

    except Exception as error:
        print("\n❌ 測試過程發生未預期錯誤")
        print(f"錯誤內容：{error}")

    print("\n" + "=" * 60)
    print("關聯測試結束")
    print("=" * 60)


if __name__ == "__main__":
    main()