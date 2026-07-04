# 用友 U8 EAI 档案类接口开发文档

> 版本：v1.0 | 日期：2026-07-04 | 状态：✅ 四接口全部验证通过

---

## 一、概述

本文档记录了用友 U8 通过 EAI（Enterprise Application Integration）接口实现四大基础档案（存货、客户、仓库、供应商）新增功能的开发全过程。所有接口基于 U8 12.0 验证通过。

### 系统架构

```
外部系统 → HTTP POST XML → U8 EAI (http://localhost/u8eai/import.asp) → U8 数据库
```

### 基础配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| EAI 接口地址 | `http://localhost/u8eai/import.asp` | U8 EAI 标准入口 |
| 外部系统编码（sender） | `001` | 需在 U8 EAI 接口配置中注册 |
| 接收系统（receiver） | `U8` | U8 系统标识 |
| 数据源 | `test001` | 在 U8 EAI 中维护 |

### 核心规则（踩坑总结）

1. **字段名必须用小写**：U8 EAI 接口不识别驼峰字段名（如 `cInvClassCode`），必须使用 U8 EAI XML 模板中的小写字段名（如 `sort_code`）
2. **存货档案特殊**：需要使用 `<header>`+`<body>` 节点结构，其他三类档案字段直接放在根节点下
3. **返回判断**：`succeed="0"` + `desc="ok"` 表示成功；`succeed="0"` 但 `key=""` 表示未实际写入

---

## 二、公共模块：U8EaiClient

**文件：** `U8EaiClient.py`

### 功能说明

提供 EAI 调用的基础能力：
- 构建标准 XML 请求体
- 通过 HTTP POST 发送到 U8 EAI 接口
- 解析返回的 XML 结果

### 核心类

#### `U8EaiClient`

| 方法 | 参数 | 说明 |
|------|------|------|
| `send(roottag, operation, header_data, body_data)` | 业务类型、操作、表头数据、表体数据 | 发送 EAI 请求（自动构建带 header/body 的 XML） |
| `test_connection()` | 无 | 测试 EAI 连接是否可用 |

#### `EaiResult`

| 属性 | 类型 | 说明 |
|------|------|------|
| `succeed` | int | 0=成功，-1=失败 |
| `desc` | str | 返回描述 |
| `key` | str | 返回的主键值（如档案编码） |
| `is_success` | bool | 便捷判断是否成功 |

---

## 三、存货档案接口（IF-201）

**文件：** `inventory_api.py` | **状态：** ✅ 已验证通过

### XML 结构（带 header/body）

```xml
<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="inventory" billtype="" docid="" receiver="U8"
             sender="001" proc="add" codeexchanged="" exportneedexch="" version="2.0">
  <inventory>
    <header>
      <code>EAITEST001</code>
      <name>EAI自动化测试存货</name>
      <sort_code>01</sort_code>
      <main_measure>01</main_measure>
      <unitgroup_code>01</unitgroup_code>
      ...
    </header>
    <body>
    </body>
  </inventory>
</ufinterface>
```

### 必填字段

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `code` | 存货编码 | 必填 |
| `name` | 存货名称 | 必填 |
| `sort_code` | 存货分类编码 | 必填 |
| `unitgroup_code` | 计量单位组 | `01` |
| `main_measure` | 主计量单位 | `01` |
| `sale_flag` | 内销 | `1` |
| `purchase_flag` | 采购 | `1` |
| `selfmake_flag` | 自制 | `0` |
| `prod_consu_flag` | 生产耗用 | `0` |
| `cPlanMethod` | 计划方法 | `R` |
| `cSRPolicy` | 供需政策 | `PE` |
| `iSupplyType` | 供应类型 | `0` |

### 调用示例

```python
from inventory_api import add_inventory

result = add_inventory({
    "code": "MAT001",
    "name": "测试原材料A",
    "sort_code": "01",
})
print(f"成功: {result.is_success}")   # True
print(f"描述: {result.desc}")         # "ok"
print(f"编码: {result.key}")          # "MAT001"
```

### 注意事项

- ❗ **唯一特殊结构**：存货档案是所有四类中唯一需要使用 `<header>`+`<body>` 节点的
- 必须调用 `U8EaiClient.send()` 方法自动构建带 header 的 XML
- `cPlanMethod`/`cSRPolicy`/`iSupplyType` 为 U8 内部必填，代码自动补充默认值

---

## 四、客户档案接口（IF-202）

**文件：** `customer_api.py` | **状态：** ✅ 已验证通过

### XML 结构

```xml
<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="customer" billtype="" docid="" receiver="U8"
             sender="001" proc="add" codeexchanged="" exportneedexch="" version="2.0">
  <customer>
    <code>CUST001</code>
    <name>测试客户</name>
    <abbrname>测试客</abbrname>
    <sort_code>01</sort_code>
    <seed_date>2026-07-04 00:00:00</seed_date>
    <ccusexch_name>人民币</ccusexch_name>
    <ccusmngtypecode>999</ccusmngtypecode>
  </customer>
</ufinterface>
```

### 必填字段

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `code` | 客户编码 | 必填 |
| `name` | 客户名称 | 必填 |
| `abbrname` | 客户简称 | 必填 |
| `sort_code` | 客户分类编码 | 必填 |
| `seed_date` | 发展日期 | `当天日期` |
| `ccusexch_name` | 币种 | `人民币` |
| `ccusmngtypecode` | 客户管理类型 | `999`（普通客户） |

### 调用示例

```python
from customer_api import add_customer

result = add_customer({
    "code": "CUST001",
    "name": "某某科技有限公司",
    "abbrname": "某某科技",
    "sort_code": "01",
})
print(f"成功: {result.is_success}")   # True
```

---

## 五、仓库档案接口（IF-203）

**文件：** `warehouse_api.py` | **状态：** ✅ 已验证通过

### XML 结构

```xml
<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="warehouse" billtype="" docid="" receiver="U8"
             sender="001" proc="add" codeexchanged="" exportneedexch="" version="2.0">
  <warehouse>
    <code>WH843</code>
    <name>测试仓库</name>
    <valuestyle>全月平均法</valuestyle>
    <barcode>WH843</barcode>
    <whmanage>0</whmanage>
    <bmrp>1</bmrp>
    <brop>1</brop>
    <iwhproperty>0</iwhproperty>
    <bcontrolserial>0</bcontrolserial>
    <bincost>1</bincost>
    <binavailcalcu>1</binavailcalcu>
    <bproxywh>0</bproxywh>
    <isaconmode>0</isaconmode>
    <iexconmode>0</iexconmode>
    <istconmode>0</istconmode>
    <bshop>0</bshop>
  </warehouse>
</ufinterface>
```

### 必填字段

> 字段名来源于 U8 EAI 模板文件 `D:\U8SOFT\EAI\XML\Template\Warehouse.xml`

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `code` | 仓库编码（最大10位） | 必填 |
| `name` | 仓库名称 | 必填 |
| `valuestyle` | 计价方式 | `全月平均法` |
| `barcode` | 对应条形码（不可重复） | 默认取 `code` 值 |
| `whmanage` | 货位管理 | `0` |
| `bmrp` | MRP运算 | `1` |
| `brop` | ROP计算 | `1` |
| `iwhproperty` | 仓库属性 | `0`（普通仓） |
| `bcontrolserial` | 控制序列号 | `0` |
| `bincost` | 记入成本 | `1` |
| `binavailcalcu` | 纳入可用量计算 | `1` |
| `bproxywh` | 代管仓 | `0` |
| `isaconmode` | 销售可用量控制方式 | `0` |
| `iexconmode` | 出口可用量控制方式 | `0` |
| `istconmode` | 库存可用量控制方式 | `0` |
| `bshop` | 门店 | `0` |

### 调用示例

```python
from warehouse_api import add_warehouse

result = add_warehouse({
    "code": "WH001",
    "name": "主仓库",
})
print(f"成功: {result.is_success}")   # True
```

### 注意事项

- ❗ `barcode`（对应条形码）不能重复，建议默认使用仓库编码作为条形码
- ❗ 曾踩坑：使用驼峰字段名 `cWhCode` 导致 U8 报"数据库没有提供的字段(cwhcode)"，必须使用小写名

---

## 六、供应商档案接口（IF-204）

**文件：** `vendor_api.py` | **状态：** ✅ 已验证通过

### XML 结构

```xml
<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="vendor" billtype="" docid="" receiver="U8"
             sender="001" proc="add" codeexchanged="" exportneedexch="" version="2.0">
  <vendor>
    <code>VEN001</code>
    <name>测试供应商</name>
    <abbrname>测试供</abbrname>
    <sort_code>01</sort_code>
    <seed_date>2026-07-04 00:00:00</seed_date>
    <bvencargo>1</bvencargo>
    <bproxyforeign>0</bproxyforeign>
    <bvenservice>0</bvenservice>
    <cvenexch_name>人民币</cvenexch_name>
  </vendor>
</ufinterface>
```

### 必填字段

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `code` | 供应商编码 | 必填 |
| `name` | 供应商名称 | 必填 |
| `abbrname` | 供应商简称 | 必填 |
| `sort_code` | 供应商分类编码 | 必填 |
| `seed_date` | 发展日期 | `当天日期` |
| `bvencargo` | 是否采购 | `1` |
| `bproxyforeign` | 是否委外 | `0` |
| `bvenservice` | 是否服务 | `0` |
| `cvenexch_name` | 币种 | `人民币` |

### 调用示例

```python
from vendor_api import add_vendor

result = add_vendor({
    "code": "VEN001",
    "name": "某某供应链有限公司",
    "abbrname": "某某供应链",
    "sort_code": "01",
})
print(f"成功: {result.is_success}")   # True
```

### 注意事项

- ❗ 字段名必须为全小写 `cvenexch_name`，不能使用驼峰 `cVenExch_name`
- ❗ `bvencargo`/`bproxyforeign`/`bvenservice` 三项至少选一个，否则报"必须至少选择一个业务范围"
- ❗ 供应商简称 `abbrname` 和币种 `cvenexch_name` 不可为空

---

## 七、接口对比一览表

| 特性 | 存货档案 | 客户档案 | 仓库档案 | 供应商档案 |
|------|---------|---------|---------|-----------|
| roottag | `inventory` | `customer` | `warehouse` | `vendor` |
| XML 结构 | header+body | 平铺 | 平铺 | 平铺 |
| 字段命名 | 小写 | 小写 | 小写 | 小写 |
| 默认值补充 | ✅ | ✅ | ✅ | ✅ |
| 验证状态 | ✅ 通过 | ✅ 通过 | ✅ 通过 | ✅ 通过 |
| 对应 IF 编号 | IF-201 | IF-202 | IF-203 | IF-204 |

### 通用调用模式

```python
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# 导入对应的 API 模块
from inventory_api import add_inventory
from customer_api import add_customer
from warehouse_api import add_warehouse
from vendor_api import add_vendor

# 新增档案（四个接口统一调用方式）
result = add_xxx({
    "code": "CODE001",
    "name": "名称",
    ...
})
```

---

## 八、常见问题（FAQ）

### Q1: 返回 succeed=0 但 key 为空/desc 为空？

**原因**：XML 字段名不匹配。U8 返回了 succeed=0（表结构解析成功）但未实际写入数据。
**解决**：检查字段名是否使用了 U8 EAI 模板中的小写名，而非用友系统中的属性名（如 `cWhCode` → `code`）。

### Q2: 如何确认正确的字段名？

打开 U8 EAI 模板文件（路径：`D:\U8SOFT\EAI\XML\Template\`），找到对应档案的 `.xml` 文件查看字段定义。

常见模板文件：
- `D:\U8SOFT\EAI\XML\Template\Inventory.xml` - 存货档案
- `D:\U8SOFT\EAI\XML\Template\Customer.xml` - 客户档案
- `D:\U8SOFT\EAI\XML\Template\Warehouse.xml` - 仓库档案
- `D:\U8SOFT\EAI\XML\Template\Vendor.xml` - 供应商档案

### Q3: 测试时提示 xxx 编码已存在？

EAI 新增接口不能重复写入同一编码，测试时每次使用不同编码或先在 U8 中删除测试数据。

### Q4: 返回 HTTP 500 错误？

通常为 XML 格式错误或缺少必填字段。检查 XML 格式完整性及必填字段是否齐全。

---

## 九、项目文件清单

| 文件 | 说明 |
|------|------|
| `U8EaiClient.py` | EAI 基础客户端（通用模块） |
| `inventory_api.py` | 存货档案接口（IF-201） |
| `customer_api.py` | 客户档案接口（IF-202） |
| `warehouse_api.py` | 仓库档案接口（IF-203） |
| `vendor_api.py` | 供应商档案接口（IF-204） |

---

## 十、附录：U8 EAI 环境配置

1. 打开 U8 企业应用平台 → **基础设置** → **EAI接口配置**
2. 勾选需要开放接口的业务模块（存货、客户、仓库、供应商等）
3. 在 **外部系统注册** 中新增外部系统，编码设为 `001`
4. 配置 EAI 数据源（如 `test001`）
5. 确保 IIS 中 U8 EAI 虚拟目录正常运行，访问 `http://localhost/u8eai/import.asp` 确认可通
