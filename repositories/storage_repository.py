
"""
收納位置資料存取模組。

負責：
1. 新增收納位置
2. 查詢收納位置
3. 修改收納位置
4. 刪除收納位置
5. 查詢位置內的模型與玩具
6. 查詢階層式收納位置
"""

from database.database import get_connection


class StorageRepository:
    """收納位置資料存取類別。"""

    ALLOWED_FIELDS = {
        "位置名稱",
        "上層位置編號",
        "位置描述",
        "收納容量",
    }

    # ========================================================
    # 新增位置
    # ========================================================
    @staticmethod
    def add_location(
        name,
        parent_id=None,
        description=None,
        capacity=None,
    ):
        """新增收納位置，回傳位置編號。"""

        if not isinstance(name, str) or not name.strip():
            raise ValueError("位置名稱不可為空。")

        if capacity is not None and capacity < 0:
            raise ValueError("收納容量不可小於 0。")

        with get_connection() as connection:
            # 防止位置以自己為上層位置
            if parent_id is not None:
                parent = connection.execute(
                    """
                    SELECT 1
                    FROM storage_locations
                    WHERE "位置編號" = ?
                    """,
                    (parent_id,),
                ).fetchone()

                if parent is None:
                    raise ValueError("指定的上層位置不存在。")

            cursor = connection.execute(
                """
                INSERT INTO storage_locations (
                    "位置名稱",
                    "上層位置編號",
                    "位置描述",
                    "收納容量"
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name.strip(),
                    parent_id,
                    description,
                    capacity,
                ),
            )

            return cursor.lastrowid

    # ========================================================
    # 查詢所有位置
    # ========================================================
    @staticmethod
    def get_all_locations():
        """依位置編號查詢所有收納位置。"""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    "位置編號",
                    "位置名稱",
                    "上層位置編號",
                    "位置描述",
                    "收納容量"
                FROM storage_locations
                ORDER BY "位置編號"
                """
            ).fetchall()

            return [dict(row) for row in rows]

    # ========================================================
    # 查詢單一位置
    # ========================================================
    @staticmethod
    def get_location_by_id(location_id):
        """查詢單一位置，不存在時回傳 None。"""

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM storage_locations
                WHERE "位置編號" = ?
                """,
                (location_id,),
            ).fetchone()

            return dict(row) if row else None

    # ========================================================
    # 修改位置
    # ========================================================
    @staticmethod
    def update_location(location_id, **fields):
        """修改位置資料，成功時回傳 True。"""

        if not fields:
            raise ValueError("沒有提供需要修改的欄位。")

        invalid_fields = set(fields) - StorageRepository.ALLOWED_FIELDS

        if invalid_fields:
            raise ValueError(
                f"不允許修改的欄位：{invalid_fields}"
            )

        if "位置名稱" in fields:
            name = fields["位置名稱"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError("位置名稱不可為空。")

            fields["位置名稱"] = name.strip()

        if "收納容量" in fields:
            capacity = fields["收納容量"]

            if capacity is not None and (
                not isinstance(capacity, int)
                or isinstance(capacity, bool)
                or capacity < 0
            ):
                raise ValueError("收納容量必須是非負整數。")

        if "上層位置編號" in fields:
            parent_id = fields["上層位置編號"]

            if parent_id == location_id:
                raise ValueError("位置不能以自己作為上層位置。")

            if parent_id is not None:
                with get_connection() as connection:
                    parent = connection.execute(
                        """
                        SELECT 1
                        FROM storage_locations
                        WHERE "位置編號" = ?
                        """,
                        (parent_id,),
                    ).fetchone()

                    if parent is None:
                        raise ValueError("指定的上層位置不存在。")

        columns = ", ".join(
            f'"{field}" = ?' for field in fields
        )

        sql = f"""
            UPDATE storage_locations
            SET {columns}
            WHERE "位置編號" = ?
        """

        values = tuple(fields.values()) + (location_id,)

        with get_connection() as connection:
            cursor = connection.execute(sql, values)
            return cursor.rowcount > 0

    # ========================================================
    # 刪除位置
    # ========================================================
    @staticmethod
    def delete_location(location_id):
        """
        刪除收納位置。

        若有持有品使用該位置，持有品的收納位置會變成 NULL。
        若有子位置，子位置的上層位置也會變成 NULL。
        """

        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM storage_locations
                WHERE "位置編號" = ?
                """,
                (location_id,),
            )

            return cursor.rowcount > 0

    # ========================================================
    # 查詢某個位置內的持有品
    # ========================================================
    @staticmethod
    def get_items_in_location(location_id):
        """查詢指定收納位置內的所有持有品。"""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    c."持有品編號",
                    c."商品編號",
                    p."商品名稱",
                    p."品牌",
                    c."數量",
                    c."收藏狀態",
                    c."備註"
                FROM collection_items AS c
                JOIN products AS p
                    ON c."商品編號" = p."商品編號"
                WHERE c."收納位置編號" = ?
                ORDER BY p."商品名稱"
                """,
                (location_id,),
            ).fetchall()

            return [dict(row) for row in rows]

    # ========================================================
    # 查詢位置階層
    # ========================================================
    @staticmethod
    def get_location_tree():
        """回傳包含上層位置名稱的列表。"""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    child."位置編號",
                    child."位置名稱",
                    child."上層位置編號",
                    parent."位置名稱" AS "上層位置名稱",
                    child."位置描述",
                    child."收納容量"
                FROM storage_locations AS child
                LEFT JOIN storage_locations AS parent
                    ON child."上層位置編號" = parent."位置編號"
                ORDER BY child."位置編號"
                """
            ).fetchall()

            return [dict(row) for row in rows]
