
"""
商品資料存取模組
負責商品主檔的新增、查詢、修改與刪除。
"""

from database.database import get_connection


class ProductRepository:
    """商品資料存取類別。"""

    # ========================================================
    # 新增商品
    # ========================================================
    @staticmethod
    def add_product(
        name,
        brand=None,
        series=None,
        manufacturer=None,
        product_type="其他",
        scale=None,
        model_number=None,
        release_date=None,
        msrp=None,
        image_path=None,
        memo=None
    ):
        """
        新增一筆商品資料。
        成功時回傳新商品的編號。
        """

        if not name or not name.strip():
            raise ValueError("商品名稱不可為空。")

        sql = """
            INSERT INTO products (
                "商品名稱",
                "品牌",
                "系列",
                "製造商",
                "商品類型",
                "比例",
                "商品型號",
                "發售日期",
                "官方定價",
                "商品圖片路徑",
                "備註"
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            name.strip(),
            brand,
            series,
            manufacturer,
            product_type,
            scale,
            model_number,
            release_date,
            msrp,
            image_path,
            memo
        )

        with get_connection() as connection:
            cursor = connection.execute(sql, values)
            return cursor.lastrowid

    # ========================================================
    # 查詢全部商品
    # ========================================================
    @staticmethod
    def get_all_products():
        """依商品編號順序取得所有商品。"""

        sql = """
            SELECT *
            FROM products
            ORDER BY "商品編號" DESC
        """

        with get_connection() as connection:
            rows = connection.execute(sql).fetchall()
            return [dict(row) for row in rows]

    # ========================================================
    # 依編號查詢商品
    # ========================================================
    @staticmethod
    def get_product_by_id(product_id):
        """依商品編號取得單筆商品；不存在時回傳 None。"""

        sql = """
            SELECT *
            FROM products
            WHERE "商品編號" = ?
        """

        with get_connection() as connection:
            row = connection.execute(
                sql, (product_id,)
            ).fetchone()

            return dict(row) if row else None

    # ========================================================
    # 依名稱搜尋商品
    # ========================================================
    @staticmethod
    def search_products(keyword):
        """以商品名稱、品牌或系列搜尋商品。"""

        sql = """
            SELECT *
            FROM products
            WHERE "商品名稱" LIKE ?
               OR "品牌" LIKE ?
               OR "系列" LIKE ?
            ORDER BY "商品編號" DESC
        """

        pattern = f"%{keyword}%"

        with get_connection() as connection:
            rows = connection.execute(
                sql, (pattern, pattern, pattern)
            ).fetchall()

            return [dict(row) for row in rows]

    # ========================================================
    # 修改商品
    # ========================================================
    @staticmethod
    def update_product(product_id, **fields):
        """
        修改指定商品。

        例如：
        update_product(1, 品牌="BANDAI", 官方定價=1500)

        欄位名稱必須與 schema.sql 一致。
        """

        allowed_fields = {
            "商品名稱",
            "品牌",
            "系列",
            "製造商",
            "商品類型",
            "比例",
            "商品型號",
            "發售日期",
            "官方定價",
            "商品圖片路徑",
            "備註"
        }

        if not fields:
            raise ValueError("沒有提供需要修改的欄位。")

        invalid_fields = set(fields) - allowed_fields

        if invalid_fields:
            raise ValueError(
                f"不允許修改的欄位：{invalid_fields}"
            )

        if "商品名稱" in fields:
            name = fields["商品名稱"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError("商品名稱不可為空。")

            fields["商品名稱"] = name.strip()

        columns = ", ".join(
            f'"{field}" = ?' for field in fields
        )

        sql = f"""
            UPDATE products
            SET {columns},
                "更新時間" = CURRENT_TIMESTAMP
            WHERE "商品編號" = ?
        """

        values = tuple(fields.values()) + (product_id,)

        with get_connection() as connection:
            cursor = connection.execute(sql, values)
            return cursor.rowcount > 0

    # ========================================================
    # 刪除商品
    # ========================================================
    @staticmethod
    def delete_product(product_id):
        """
        刪除指定商品。
        成功刪除時回傳 True，找不到商品時回傳 False。
        """

        sql = """
            DELETE FROM products
            WHERE "商品編號" = ?
        """

        with get_connection() as connection:
            cursor = connection.execute(sql, (product_id,))
            return cursor.rowcount > 0
