
from database.database import get_connection


class StoreRepository:

    @staticmethod
    def add_store(name):
        """新增店家，回傳店家編號"""

        if not name or not name.strip():
            raise ValueError("店家名稱不可為空")

        name = name.strip()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO stores ("店家名稱")
                VALUES (?)
                """,
                (name,)
            )

            return cursor.lastrowid

    @staticmethod
    def get_all_stores():
        """取得全部店家"""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT "店家編號", "店家名稱"
                FROM stores
                ORDER BY "店家編號"
                """
            ).fetchall()

            return [dict(row) for row in rows]

    @staticmethod
    def get_store_by_id(store_id):
        """依店家編號查詢"""

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT "店家編號", "店家名稱"
                FROM stores
                WHERE "店家編號" = ?
                """,
                (store_id,)
            ).fetchone()

            return dict(row) if row else None

    @staticmethod
    def search_stores(keyword):
        """依店家名稱搜尋"""

        keyword = f"%{keyword.strip()}%"

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT "店家編號", "店家名稱"
                FROM stores
                WHERE "店家名稱" LIKE ?
                ORDER BY "店家編號"
                """,
                (keyword,)
            ).fetchall()

            return [dict(row) for row in rows]

    @staticmethod
    def update_store(store_id, name):
        """修改店家名稱，回傳是否成功"""

        if not name or not name.strip():
            raise ValueError("店家名稱不可為空")

        name = name.strip()

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE stores
                SET "店家名稱" = ?
                WHERE "店家編號" = ?
                """,
                (name, store_id)
            )

            return cursor.rowcount > 0

    @staticmethod
    def delete_store(store_id):
        """刪除店家，回傳是否成功"""

        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM stores
                WHERE "店家編號" = ?
                """,
                (store_id,)
            )

            return cursor.rowcount > 0
