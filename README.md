# U8 EAI 档案类接口 - 开发总结

## 📊 接口状态总览（2026-07-04 更新）

| 接口 | 档案类型 | roottag | 状态 | 验证日期 |
|------|----------|---------|------|----------|
| IF-201 | 存货档案 | `inventory` | ✅ 已验证 | 2026-07-04 |
| IF-202 | 客户档案 | `Customer` | ✅ 已验证 | 2026-07-04 |
| IF-203 | 仓库档案 | `Warehouse` | ✅ 已验证 | 2026-07-04 |
| IF-204 | 供应商档案 | `Vendor` | ✅ 已验证 | 2026-07-04 |

## 🔑 关键发现

### 1. roottag 大小写敏感
U8 12.0 的 EAI 接口对 **roottag 的大小写** 有严格要求：
- ❌ 小写 `customer` → 失败
- ✅ **大写** `Customer` → 成功
- ❌ 小写 `warehouse` → 失败
- ✅ **大写** `Warehouse` → 成功
- ❌ 小写 `vendor` → 失败
- ✅ **大写** `Vendor` → 成功
- ✅ 存货档案使用小写 `inventory`（例外）

### 2. 字段名映射规则
U8 12.0 的 EAI 接口要求使用**数据库字段名**而非 EAI 模板字段名：

| 档案类型 | API参数名 | XML字段名 | 说明 |
|----------|-----------|-----------|------|
| 客户档案 | code | cCusCode | 客户编码 |
| 客户档案 | name | cCusName | 客户名称 |
| 客户档案 | abbrname | cCusAbbr | 客户简称 |
| 客户档案 | manage_type | cCusTypeCode | 管理类型（999=普通客户） |
| 仓库档案 | code | cWhCode | 仓库编码 |
| 仓库档案 | name | cWhName | 仓库名称 |
| 仓库档案 | valuestyle | cValueStyle | 计价方式 |
| 供应商档案 | code | cVenCode | 供应商编码 |
| 供应商档案 | name | cVenName | 供应商名称 |
| 供应商档案 | cargo | bVenCargo | 是否货物 |

### 3. 必填字段说明

#### 客户档案 (IF-202)
```python
{
    'code': 'CUS001',        # 必填：客户编码
    'name': '客户名称',       # 必填：客户名称
    'abbrname': '简称',       # 必填：客户简称
    'manage_type': '999',     # 必填：管理类型（999=普通客户）
}
```

#### 仓库档案 (IF-203)
```python
{
    'code': 'WH001',          # 必填：仓库编码
    'name': '仓库名称',        # 必填：仓库名称
    'valuestyle': '全月平均法' # 必填：计价方式（名称或编码均可）
}
```

#### 供应商档案 (IF-204)
```python
{
    'code': 'VEN001',         # 必填：供应商编码
    'name': '供应商名称',      # 必填：供应商名称
    'abbrname': '简称',       # 必填：供应商简称
    'cargo': '1',             # 必填：是否货物
    'seed_date': '2026-01-01' # 必填：发展日期
}
```

## 📁 项目文件结构

```
U8EaiApi/
├── U8EaiClient.py         # 基础客户端（认证/发送/解析）
├── inventory_api.py       # IF-201 存货档案 ✅
├── customer_api.py        # IF-202 客户档案 ✅
├── warehouse_api.py       # IF-203 仓库档案 ✅
├── vendor_api.py          # IF-204 供应商档案 ✅
└── test_archives_final.py # 完整测试脚本
```

## 🚀 使用示例

### 快速调用
```python
from customer_api import add_customer
from warehouse_api import add_warehouse
from vendor_api import add_vendor
from inventory_api import add_inventory

# 新增客户
result = add_customer({
    'code': 'CUS001',
    'name': '测试客户',
    'abbrname': '测客'
})
print(result.is_success)  # True/False

# 新增仓库
result = add_warehouse({
    'code': 'WH001',
    'name': '测试仓库',
    'valuestyle': '全月平均法'
})

# 新增供应商
result = add_vendor({
    'code': 'VEN001',
    'name': '测试供应商',
    'abbrname': '测供'
})
```

## ⚠️ 注意事项

1. **编码唯一性**：每次测试建议使用不同的编码，避免重复导致失败
2. **计价方式**：使用名称（如"全月平均法"）或编码均可，但必须与 U8 中已有的数据一致
3. **币种**：默认使用"人民币"，需确保 U8 中已存在该币种
4. **管理类型**：客户档案必须指定管理类型，默认"999"表示普通客户

## 🔧 调试技巧

如果遇到错误：
1. 检查 roottag 是否使用了正确的大小写
2. 检查必填字段是否都已提供
3. 检查基础数据是否存在（如计价方式、币种、分类等）
4. 查看 U8 EAI 日志获取详细错误信息

## 📝 开发历史

### 2026-07-04
- ✅ 发现并修复了 roottag 大小写问题
- ✅ 发现并修复了数据库字段名映射问题
- ✅ 所有4个档案类接口全部验证通过
- ✅ 更新了所有API代码文件，使用正确的格式

---

**开发者**: AI Assistant  
**最后更新**: 2026-07-04  
**状态**: 全部完成 ✅
