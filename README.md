# U8EAI

用友 U8 EAI 档案类接口 - 存货 / 客户 / 仓库 / 供应商 四接口 Python 实现，全部通过 U8 12.0 验证。

## 接口状态

| 接口 | 档案类型 | roottag | 状态 |
|------|----------|---------|------|
| IF-201 | 存货档案 | `inventory` | ✅ 已验证 |
| IF-202 | 客户档案 | `customer` | ✅ 已验证 |
| IF-203 | 仓库档案 | `warehouse` | ✅ 已验证 |
| IF-204 | 供应商档案 | `vendor` | ✅ 已验证 |

## 关键规则

- **字段名统一用小写**：来自 U8 EAI 模板文件（`D:\U8SOFT\EAI\XML\Template\`），不是 U8 数据库列名，也不是驼峰。
- **存货档案**使用 `<header>` + `<body>` 节点结构；其余三类字段直接放在根节点下。
- **成功标志**：返回 XML 中 `succeed="0"` 且 `desc="ok"`。

## 文件结构

```
U8EaiApi/
├── U8EaiClient.py                    # 基础客户端（发送 / 解析）
├── inventory_api.py                  # IF-201 存货档案
├── customer_api.py                   # IF-202 客户档案
├── warehouse_api.py                  # IF-203 仓库档案
├── vendor_api.py                     # IF-204 供应商档案
├── U8EAI档案类接口开发文档.md        # 完整开发文档
└── README.md                         # 本文件
```

## 快速使用

```python
from customer_api import add_customer
from warehouse_api import add_warehouse
from vendor_api import add_vendor
from inventory_api import add_inventory

# 新增客户
result = add_customer({
    "code": "CUS001",
    "name": "测试客户",
    "abbrname": "测客",
    "sort_code": "01"
})
print(result.is_success)  # True
```

## 详细说明

详见《U8EAI档案类接口开发文档.md》，包含：
- EAI 环境配置
- 各接口 XML 结构与必填字段
- 调用示例
- 踩坑记录与 FAQ
