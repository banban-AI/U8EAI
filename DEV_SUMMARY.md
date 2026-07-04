# U8 EAI 档案类接口 - 开发完成报告

## 最终状态：✅ 全部 4 个接口验证通过

| 接口 | 档案类型 | roottag | 字段名规则 | 状态 |
|------|----------|---------|-----------|------|
| IF-201 | 存货档案 | `inventory` (小写) | EAI模板字段 (`code`, `name`) + **有 `<header><body>` 节点** | ✅ 已验证 |
| IF-202 | 客户档案 | `customer` (小写) | 混合格式 | ✅ 已验证 |
| IF-203 | 仓库档案 | `warehouse` (小写) | **驼峰式数据库字段名** (`cWhCode`, `cWhName`, `cWhValueStyle`) | ✅ 已验证 |
| IF-204 | 供应商档案 | `vendor` (小写) | **驼峰式数据库字段名** (`cVenCode`, `cVenName`, `cVenAbbr`) | ✅ 已验证 |

## 关键发现（踩坑记录）

### 1. XML 格式差异
- **存货档案**：需要 `<inventory><header>...</header><body></body></inventory>` 结构
- **其他档案**：字段直接放在根节点下，无 header/body

### 2. 字段名规则
- **存货档案**：使用 EAI 模板中的字段名（如 `code`, `name`）
- **客户档案**：混合格式（`code` + `ccusmngtypecode` + `seed_date`）
- **仓库/供应商**：使用**驼峰式数据库列名**
  - 仓库：`cWhCode` ❌ 不是 `cwhcode` / `code`
  - 供应商：`cVenCode` ❌ 不是 `cvencode` / `code`

### 3. 必填字段
- **客户**：`ccusmngtypecode=999`（管理类型）+ `seed_date`（发展日期）
- **仓库**：`cWhValueStyle`（计价方式）+ `iWhProperty`（仓库属性）
- **供应商**：`dVenCreateDate`（发展日期）+ `cVenExch_name`（币种）

### 4. roottag 大小写
- 全部使用**小写**：`inventory`, `customer`, `warehouse`, `vendor`
- ⚠️ 不要用大写首字母

## 文件清单

```
U8EaiApi/
├── U8EaiClient.py       # 基础客户端（认证/发送/解析）
├── inventory_api.py     # IF-201 存货档案 ✅
├── customer_api.py      # IF-202 客户档案 ✅
├── warehouse_api.py     # IF-203 仓库档案 ✅（已修复为驼峰式字段名）
├── vendor_api.py        # IF-204 供应商档案 ✅（已修复为驼峰式字段名）
└── DEV_SUMMARY.md       # 本文件
```

## 使用示例

```python
from customer_api import add_customer
from warehouse_api import add_warehouse
from vendor_api import add_vendor

# 新增客户（自动补充管理类型=999、发展日期等默认值）
add_customer({
    'code': 'CUS001',
    'name': '武汉测试客户',
    'abbrname': '武测客',
    'sort_code': '01'
})

# 新增仓库（使用用户友好字段名，内部自动映射到 cWhCode 等驼峰字段）
add_warehouse({
    'code': 'WH001',           # → 映射为 cWhCode
    'name': '成品仓',           # → 映射为 cWhName
    'valuestyle': '全月平均法'   # → 映射为 cWhValueStyle
})

# 新增供应商（自动补充发展日期、币种等默认值）
add_vendor({
    'code': 'VEN001',
    'name': '武汉测试供应商',
    'abbrname': '武测供',
    'sort_code': '01'
})
```

## 下一步
- [ ] 单据类接口开发（采购入库单、销售出库单、材料出库单、调拨单等）
- [ ] 部署为 Web 服务（Flask/FastAPI），供 OA 系统调用
- [ ] 对接 OA 系统，完成完整的数据同步流程
