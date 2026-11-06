
-- ============================================================
-- 模型與玩具收藏管理系統
-- 資料庫：SQLite
-- 編碼：UTF-8
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- 1. 購買店家
-- ============================================================
CREATE TABLE IF NOT EXISTS stores (
    "店家編號" INTEGER PRIMARY KEY AUTOINCREMENT,
    "店家名稱" TEXT NOT NULL UNIQUE
);

-- ============================================================
-- 2. 收納位置
-- ============================================================
CREATE TABLE IF NOT EXISTS storage_locations (
    "位置編號" INTEGER PRIMARY KEY AUTOINCREMENT,
    "位置名稱" TEXT NOT NULL,
    "上層位置編號" INTEGER,
    "位置描述" TEXT,
    "收納容量" INTEGER,
    "建立時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY ("上層位置編號")
        REFERENCES storage_locations("位置編號")
        ON DELETE SET NULL
);


-- ============================================================
-- 3. 商品主檔
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    "商品編號" INTEGER PRIMARY KEY AUTOINCREMENT,
    "商品名稱" TEXT NOT NULL,
    "品牌" TEXT,
    "系列" TEXT,
    "製造商" TEXT,

    -- 組裝模型 / 完成品玩具 / 景品 / PVC / 其他
    "商品類型" TEXT NOT NULL DEFAULT '其他',

    "比例" TEXT,
    "商品型號" TEXT,
    "發售日期" TEXT,
    "官方定價" REAL,
    "商品圖片路徑" TEXT,
    "備註" TEXT,

    "建立時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "更新時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 4. 收藏與持有品
-- ============================================================
CREATE TABLE IF NOT EXISTS collection_items (
    "持有品編號" INTEGER PRIMARY KEY AUTOINCREMENT,
    "商品編號" INTEGER NOT NULL,

    -- 未開始 / 製作中 / 已完成 / 收藏
    "收藏狀態" TEXT NOT NULL DEFAULT '未開始',

    -- 全新 / 已開封 / 有損傷 / 其他
    "商品狀況" TEXT DEFAULT '全新',

    "購買日期" TEXT,
    "購買單價" REAL,
    "數量" INTEGER NOT NULL DEFAULT 1,

    -- 0 = 否，1 = 是
    "是否開封" INTEGER NOT NULL DEFAULT 0,
    "是否完成組裝" INTEGER NOT NULL DEFAULT 0,

    "收納位置編號" INTEGER,
    "備註" TEXT,

    "建立時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "更新時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY ("商品編號")
        REFERENCES products("商品編號")
        ON DELETE CASCADE,

    FOREIGN KEY ("收納位置編號")
        REFERENCES storage_locations("位置編號")
        ON DELETE SET NULL,

    CHECK ("數量" > 0),
    CHECK ("購買單價" IS NULL OR "購買單價" >= 0),
    CHECK ("是否開封" IN (0, 1)),
    CHECK ("是否完成組裝" IN (0, 1))
);


-- ============================================================
-- 5. 預購紀錄
-- ============================================================
CREATE TABLE IF NOT EXISTS preorders (
    "預購編號" INTEGER PRIMARY KEY AUTOINCREMENT,
    "商品編號" INTEGER NOT NULL,
    "店家編號" INTEGER,

    "預購日期" TEXT,
    "預計發售日期" TEXT,
    "預計到貨日期" TEXT,

    "預購數量" INTEGER NOT NULL DEFAULT 1,
    "預購單價" REAL,
    "訂金" REAL NOT NULL DEFAULT 0,
    "運費" REAL NOT NULL DEFAULT 0,
    "已付尾款" REAL NOT NULL DEFAULT 0,

    -- 預購中 / 已到貨 / 已取消 / 已完成
    "預購狀態" TEXT NOT NULL DEFAULT '預購中',

    -- 未付款 / 部分付款 / 已付款
    "付款狀態" TEXT NOT NULL DEFAULT '未付款',

    "訂單編號" TEXT,
    "備註" TEXT,

    "建立時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "更新時間" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY ("商品編號")
        REFERENCES products("商品編號")
        ON DELETE CASCADE,

    FOREIGN KEY ("店家編號")
        REFERENCES stores("店家編號")
        ON DELETE SET NULL,

    CHECK ("預購數量" > 0),
    CHECK ("預購單價" IS NULL OR "預購單價" >= 0),
    CHECK ("訂金" >= 0),
    CHECK ("運費" >= 0),
    CHECK ("已付尾款" >= 0)
);


-- ============================================================
-- 6. 索引：加快常用查詢
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_products_name
ON products("商品名稱");

CREATE INDEX IF NOT EXISTS idx_products_type
ON products("商品類型");

CREATE INDEX IF NOT EXISTS idx_collection_status
ON collection_items("收藏狀態");

CREATE INDEX IF NOT EXISTS idx_collection_location
ON collection_items("收納位置編號");

CREATE INDEX IF NOT EXISTS idx_preorders_status
ON preorders("預購狀態");

CREATE INDEX IF NOT EXISTS idx_preorders_arrival
ON preorders("預計到貨日期");


-- ============================================================
-- 7. 預設資料
-- ============================================================
/*
INSERT OR IGNORE INTO storage_locations
    ("位置名稱", "位置描述")
VALUES
    ('未分類', '尚未指定收納位置');
*/