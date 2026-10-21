from database.database import get_connection


class PreorderRepository:

    ALLOWED_FIELDS = {
        "商品編號",
        "店家編號",
        "預購日期",
        "預計發售日期",
        "預計到貨日期",
        "預購數量",
        "預購單價",
        "訂金",
        "運費",
        "已付尾款",
        "預購狀態",
        "付款狀態",
        "訂單編號",
        "備註"
    }

    @staticmethod
    def add_preorder(
        product_id,
        store_id=None,
        preorder_date=None,
        expected_release_date=None,
        expected_arrival_date=None,
        quantity=1,
        preorder_price=None,
        deposit=0,
        shipping_fee=0,
        paid_balance=0,
        preorder_status="預購中",
        payment_status="未付款",
        order_number=None,
        memo=None
    ):
        """新增預購資料"""

        if not product_id:
            raise ValueError("商品編號不可為空")

        if quantity <= 0:
            raise ValueError("預購數量必須大於 0")

        if preorder_price is not None and preorder_price < 0:
            raise ValueError("預購單價不可小於 0")

        if deposit < 0:
            raise ValueError("訂金不可小於 0")

        if shipping_fee < 0:
            raise ValueError("運費不可小於 0")

        if paid_balance < 0:
            raise ValueError("已付尾款不可小於 0")

        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO preorders (
                    "商品編號",
                    "店家編號",
                    "預購日期",
                    "預計發售日期",
                    "預計到貨日期",
                    "預購數量",
                    "預購單價",
                    "訂金",
                    "運費",
                    "已付尾款",
                    "預購狀態",
                    "付款狀態",
                    "訂單編號",
                    "備註"
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    store_id,
                    preorder_date,
                    expected_release_date,
                    expected_arrival_date,
                    quantity,
                    preorder_price,
                    deposit,
                    shipping_fee,
                    paid_balance,
                    preorder_status,
                    payment_status,
                    order_number,
                    memo
                )
            )

            return cursor.lastrowid

    @staticmethod
    def get_all_preorders():
        """取得所有預購資料"""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    p."預購編號",
                    p."商品編號",
                    product."商品名稱",
                    p."店家編號",
                    store."店家名稱",
                    p."預購日期",
                    p."預計發售日期",
                    p."預計到貨日期",
                    p."預購數量",
                    p."預購單價",
                    p."訂金",
                    p."運費",
                    p."已付尾款",
                    p."預購狀態",
                    p."付款狀態",
                    p."訂單編號",
                    p."備註",
                    p."建立時間",
                    p."更新時間"
                FROM preorders p
                LEFT JOIN products product
                    ON p."商品編號" = product."商品編號"
                LEFT JOIN stores store
                    ON p."店家編號" = store."店家編號"
                ORDER BY p."預購編號"
                """
            ).fetchall()

            return [dict(row) for row in rows]

    @staticmethod
    def get_preorder_by_id(preorder_id):
        """依預購編號取得單筆資料"""

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    p."預購編號",
                    p."商品編號",
                    product."商品名稱",
                    p."店家編號",
                    store."店家名稱",
                    p."預購日期",
                    p."預計發售日期",
                    p."預計到貨日期",
                    p."預購數量",
                    p."預購單價",
                    p."訂金",
                    p."運費",
                    p."已付尾款",
                    p."預購狀態",
                    p."付款狀態",
                    p."訂單編號",
                    p."備註",
                    p."建立時間",
                    p."更新時間"
                FROM preorders p
                LEFT JOIN products product
                    ON p."商品編號" = product."商品編號"
                LEFT JOIN stores store
                    ON p."店家編號" = store."店家編號"
                WHERE p."預購編號" = ?
                """,
                (preorder_id,)
            ).fetchone()

            return dict(row) if row else None

    @staticmethod
    def get_preorders_by_status(status):
        """依預購狀態取得資料"""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    p."預購編號",
                    p."商品編號",
                    product."商品名稱",
                    p."店家編號",
                    store."店家名稱",
                    p."預購日期",
                    p."預計發售日期",
                    p."預計到貨日期",
                    p."預購數量",
                    p."預購單價",
                    p."訂金",
                    p."運費",
                    p."已付尾款",
                    p."預購狀態",
                    p."付款狀態",
                    p."訂單編號",
                    p."備註"
                FROM preorders p
                LEFT JOIN products product
                    ON p."商品編號" = product."商品編號"
                LEFT JOIN stores store
                    ON p."店家編號" = store."店家編號"
                WHERE p."預購狀態" = ?
                ORDER BY p."預購編號"
                """,
                (status,)
            ).fetchall()

            return [dict(row) for row in rows]

    @staticmethod
    def search_preorders(keyword):
        """搜尋商品名稱、店家名稱、訂單編號"""

        keyword = f"%{keyword}%"

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    p."預購編號",
                    p."商品編號",
                    product."商品名稱",
                    p."店家編號",
                    store."店家名稱",
                    p."預購日期",
                    p."預計發售日期",
                    p."預計到貨日期",
                    p."預購數量",
                    p."預購單價",
                    p."訂金",
                    p."運費",
                    p."已付尾款",
                    p."預購狀態",
                    p."付款狀態",
                    p."訂單編號",
                    p."備註"
                FROM preorders p
                LEFT JOIN products product
                    ON p."商品編號" = product."商品編號"
                LEFT JOIN stores store
                    ON p."店家編號" = store."店家編號"
                WHERE
                    product."商品名稱" LIKE ?
                    OR store."店家名稱" LIKE ?
                    OR p."訂單編號" LIKE ?
                    OR p."備註" LIKE ?
                ORDER BY p."預購編號"
                """,
                (keyword, keyword, keyword, keyword)
            ).fetchall()

            return [dict(row) for row in rows]

    @staticmethod
    def update_preorder(preorder_id, **fields):
        """修改預購資料"""

        if not fields:
            return False

        for field in fields:
            if field not in PreorderRepository.ALLOWED_FIELDS:
                raise ValueError(f"不允許修改欄位：{field}")

        if "預購數量" in fields:
            if fields["預購數量"] <= 0:
                raise ValueError("預購數量必須大於 0")

        if "預購單價" in fields:
            if (
                fields["預購單價"] is not None
                and fields["預購單價"] < 0
            ):
                raise ValueError("預購單價不可小於 0")

        for field in ["訂金", "運費", "已付尾款"]:
            if field in fields and fields[field] < 0:
                raise ValueError(f"{field}不可小於 0")

        set_clause = ", ".join(
            f'"{field}" = ?'
            for field in fields
        )

        values = list(fields.values())
        values.append(preorder_id)

        with get_connection() as connection:
            cursor = connection.execute(
                f"""
                UPDATE preorders
                SET
                    {set_clause},
                    "更新時間" = CURRENT_TIMESTAMP
                WHERE "預購編號" = ?
                """,
                values
            )

            return cursor.rowcount > 0

    @staticmethod
    def delete_preorder(preorder_id):
        """刪除預購資料"""

        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM preorders
                WHERE "預購編號" = ?
                """,
                (preorder_id,)
            )

            return cursor.rowcount > 0

    @staticmethod
    def calculate_total(preorder_id):
        """計算預購總金額"""

        preorder = PreorderRepository.get_preorder_by_id(preorder_id)

        if preorder is None:
            return None

        price = preorder["預購單價"] or 0
        quantity = preorder["預購數量"] or 0
        shipping_fee = preorder["運費"] or 0

        total = price * quantity + shipping_fee

        return total

    @staticmethod
    def calculate_paid_amount(preorder_id):
        """計算已付款金額"""

        preorder = PreorderRepository.get_preorder_by_id(preorder_id)

        if preorder is None:
            return None

        deposit = preorder["訂金"] or 0
        paid_balance = preorder["已付尾款"] or 0

        return deposit + paid_balance

    @staticmethod
    def calculate_remaining_amount(preorder_id):
        """計算尚未付款金額"""

        total = PreorderRepository.calculate_total(preorder_id)
        paid = PreorderRepository.calculate_paid_amount(preorder_id)

        if total is None or paid is None:
            return None

        return max(total - paid, 0)