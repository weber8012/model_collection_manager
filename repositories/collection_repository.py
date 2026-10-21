
"""
收藏與持有品資料存取模組。

負責：
1. 新增持有品
2. 查詢持有品
3. 搜尋持有品
4. 修改持有品
5. 刪除持有品
6. 統計山積與組裝狀態
"""

from database.database import get_connection


class CollectionRepository:
    """收藏與持有品資料存取類別。"""

    ALLOWED_FIELDS = {
        "商品編號",
        "收藏狀態",
        "商品狀況",
        "購買日期",
        "購買單價",
        "數量",
        "是否開封",
        "是否完成組裝",
        "收納位置編號",
        "備註",
    }

    # ========================================================
    # 新增持有品
    # ========================================================
    @staticmethod
    def add_item(
        product_id,
        status="未開始",
        condition="全新",
        purchase_date=None,
        purchase_price=None,
        quantity=1,
        is_opened=0,
        is_completed=0,
        storage_location_id=None,
        memo=None,
    ):
        """新增一筆持有品，回傳持有品編號。"""

        if quantity < 1:
            raise ValueError("數量必須大於 0。")

        if purchase_price is not None and purchase_price < 0:
            raise ValueError("購買單價不可小於 0。")

        if is_opened not in (0, 1):
            raise ValueError("是否開封只能填入 0 或 1。")

        if is_completed not in (0, 1):
            raise ValueError("是否完成組裝只能填入 0 或 1。")

        sql = """
            INSERT INTO collection_items (
                "商品編號",
                "收藏狀態",
                "商品狀況",
                "購買日期",
                "購買單價",
                "數量",
                "是否開封",
                "是否完成組裝",
                "收納位置編號",
                "備註"
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            product_id,
            status,
            condition,
            purchase_date,
            purchase_price,
            quantity,
            is_opened,
            is_completed,
            storage_location_id,
            memo,
        )

        with get_connection() as connection:
            cursor = connection.execute(sql, values)
            return cursor.lastrowid

    # ========================================================
    # 查詢全部持有品
    # ========================================================
    @staticmethod
    def get_all_items():
        """查詢持有品，並附帶商品名稱與收納位置。"""

        sql = """
            SELECT
                c.*,
                p."商品名稱",
                p."品牌",
                p."商品類型",
                s."位置名稱"
            FROM collection_items AS c
            JOIN products AS p
                ON c."商品編號" = p."商品編號"
            LEFT JOIN storage_locations AS s
                ON c."收納位置編號" = s."位置編號"
            ORDER BY c."持有品編號" DESC
        """

        with get_connection() as connection:
            rows = connection.execute(sql).fetchall()
            return [dict(row) for row in rows]

    # ========================================================
    # 依編號查詢持有品
    # ========================================================
    @staticmethod
    def get_item_by_id(item_id):
        """查詢單筆持有品，不存在時回傳 None。"""

        sql = """
            SELECT
                c.*,
                p."商品名稱",
                p."品牌",
                p."商品類型",
                s."位置名稱"
            FROM collection_items AS c
            JOIN products AS p
                ON c."商品編號" = p."商品編號"
            LEFT JOIN storage_locations AS s
                ON c."收納位置編號" = s."位置編號"
            WHERE c."持有品編號" = ?
        """

        with get_connection() as connection:
            row = connection.execute(
                sql, (item_id,)
            ).fetchone()

            return dict(row) if row else None

    # ========================================================
    # 依狀態查詢
    # ========================================================
    @staticmethod
    def get_items_by_status(status):
        """依收藏狀態查詢持有品。"""

        sql = """
            SELECT
                c.*,
                p."商品名稱",
                p."品牌",
                s."位置名稱"
            FROM collection_items AS c
            JOIN products AS p
                ON c."商品編號" = p."商品編號"
            LEFT JOIN storage_locations AS s
                ON c."收納位置編號" = s."位置編號"
            WHERE c."收藏狀態" = ?
            ORDER BY c."持有品編號" DESC
        """

        with get_connection() as connection:
            rows = connection.execute(
                sql, (status,)
            ).fetchall()

            return [dict(row) for row in rows]

    # ========================================================
    # 搜尋持有品
    # ========================================================
    @staticmethod
    def search_items(keyword):
        """依商品名稱、品牌或備註搜尋。"""

        pattern = f"%{keyword}%"

        sql = """
            SELECT
                c.*,
                p."商品名稱",
                p."品牌",
                s."位置名稱"
            FROM collection_items AS c
            JOIN products AS p
                ON c."商品編號" = p."商品編號"
            LEFT JOIN storage_locations AS s
                ON c."收納位置編號" = s."位置編號"
            WHERE p."商品名稱" LIKE ?
               OR p."品牌" LIKE ?
               OR c."備註" LIKE ?
            ORDER BY c."持有品編號" DESC
        """

        with get_connection() as connection:
            rows = connection.execute(
                sql, (pattern, pattern, pattern)
            ).fetchall()

            return [dict(row) for row in rows]

    # ========================================================
    # 修改持有品
    # ========================================================
    @staticmethod
    def update_item(item_id, **fields):
        """修改持有品欄位，成功時回傳 True。"""

        if not fields:
            raise ValueError("沒有提供需要修改的欄位。")

        invalid_fields = set(fields) - CollectionRepository.ALLOWED_FIELDS

        if invalid_fields:
            raise ValueError(
                f"不允許修改的欄位：{invalid_fields}"
            )

        if "數量" in fields and fields["數量"] < 1:
            raise ValueError("數量必須大於 0。")

        if (
            "購買單價" in fields
            and fields["購買單價"] is not None
            and fields["購買單價"] < 0
        ):
            raise ValueError("購買單價不可小於 0。")

        for field in ("是否開封", "是否完成組裝"):
            if field in fields and fields[field] not in (0, 1):
                raise ValueError(f"{field}只能填入 0 或 1。")

        columns = ", ".join(
            f'"{field}" = ?' for field in fields
        )

        sql = f"""
            UPDATE collection_items
            SET {columns},
                "更新時間" = CURRENT_TIMESTAMP
            WHERE "持有品編號" = ?
        """

        values = tuple(fields.values()) + (item_id,)

        with get_connection() as connection:
            cursor = connection.execute(sql, values)
            return cursor.rowcount > 0

    # ========================================================
    # 刪除持有品
    # ========================================================
    @staticmethod
    def delete_item(item_id):
        """刪除持有品，不會刪除商品主檔。"""

        sql = """
            DELETE FROM collection_items
            WHERE "持有品編號" = ?
        """

        with get_connection() as connection:
            cursor = connection.execute(sql, (item_id,))
            return cursor.rowcount > 0

    # ========================================================
    # 統計持有品
    # ========================================================
    @staticmethod
    def get_statistics():
        """取得持有品數量與各狀態的數量統計。"""

        sql = """
            SELECT
                COUNT(*) AS 持有品筆數,
                COALESCE(SUM("數量"), 0) AS 持有總數,
                COALESCE(
                    SUM(
                        CASE
                            WHEN "收藏狀態" = '未開始'
                            THEN "數量"
                            ELSE 0
                        END
                    ), 0
                ) AS 未開始數量,
                COALESCE(
                    SUM(
                        CASE
                            WHEN "收藏狀態" = '製作中'
                            THEN "數量"
                            ELSE 0
                        END
                    ), 0
                ) AS 製作中數量,
                COALESCE(
                    SUM(
                        CASE
                            WHEN "是否完成組裝" = 1
                            THEN "數量"
                            ELSE 0
                        END
                    ), 0
                ) AS 已完成數量
            FROM collection_items
        """

        with get_connection() as connection:
            row = connection.execute(sql).fetchone()
            return dict(row)
