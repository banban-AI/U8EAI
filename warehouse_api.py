# -*- coding: utf-8 -*-
"""
U8 EAI - 仓库档案接口 (IF-203)
===============================
✅ 正确格式：字段直接放在 <warehouse> 节点下，字段名用小写（跟客户/供应商一致）

正确字段名（从U8模板和测试确认）:
  code          - 仓库编码（必填，最大10位）
  name          - 仓库名称（必填）
  valuestyle    - 计价方式（必填，如"全月平均法"）
  barcode       - 对应条形码（必填，不可重复）
  whmanage      - 是否货位管理（必填）
  bmrp          - 是否参与MRP运算（必填）
  brop          - 是否参与ROP计算（必填）
  iwhproperty   - 仓库属性（必填，0=普通仓）
  bcontrolserial- 控制序列号（必填）
  bincost       - 记入成本（必填）
  binavailcalcu - 纳入可用量计算（必填）
  bproxywh      - 是否代管仓（必填）
  isaconmode    - 销售可用量控制方式（必填）
  iexconmode    - 出口可用量控制方式（必填）
  istconmode    - 库存可用量控制方式（必填）
  bshop         - 是否门店（必填）
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from U8EaiClient import U8EaiClient, EaiResult


class WarehouseApi:
    """仓库档案 EAI 接口"""
    ROOTTAG = "warehouse"

    def __init__(self, client: U8EaiClient = None):
        self.client = client or U8EaiClient()

    def add(self, data: dict) -> EaiResult:
        """新增仓库档案

        最小必填:
          code (code)        - 仓库编码
          name (name)        - 仓库名称

        可选字段会自动补充默认值（对应U8模板必填项）。
        """
        defaults = {
            "valuestyle": "全月平均法",
            "whmanage": "0",
            "barcode": data.get("code", "BC001"),
            "bmrp": "1",
            "brop": "1",
            "iwhproperty": "0",
            "bcontrolserial": "0",
            "bincost": "1",
            "binavailcalcu": "1",
            "bproxywh": "0",
            "isaconmode": "0",
            "iexconmode": "0",
            "istconmode": "0",
            "bshop": "0",
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v

        # 字段映射：用户友好名 → EAI字段名（小写，与U8模板一致）
        field_map = {
            "code": "code",
            "name": "name",
            "valuestyle": "valuestyle",
            "whmanage": "whmanage",
            "barcode": "barcode",
            "bmrp": "bmrp",
            "brop": "brop",
            "iwhproperty": "iwhproperty",
            "bcontrolserial": "bcontrolserial",
            "bincost": "bincost",
            "binavailcalcu": "binavailcalcu",
            "bproxywh": "bproxywh",
            "isaconmode": "isaconmode",
            "iexconmode": "iexconmode",
            "istconmode": "istconmode",
            "bshop": "bshop",
            "depart_code": "depart_code",
            "address": "address",
            "phone": "phone",
            "person": "person",
            "ration": "ration",
            "memo": "memo",
        }

        # 构造XML字段
        field_lines = []
        for key, value in data.items():
            if value is not None:
                xml_key = field_map.get(key, key)
                field_lines.append(f"    <{xml_key}>{value}</{xml_key}>")
        fields_xml = "\n".join(field_lines)

        xml_body = f'''<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="{self.ROOTTAG}" billtype="" docid="" receiver="{self.client.receiver}"
             sender="{self.client.sender}" proc="add" codeexchanged="" exportneedexch="" version="2.0">
  <{self.ROOTTAG}>
{fields_xml}
  </{self.ROOTTAG}>
</ufinterface>'''

        return self.client._post(xml_body)


def add_warehouse(data: dict) -> EaiResult:
    """快捷函数：新增仓库档案"""
    return WarehouseApi().add(data)


if __name__ == "__main__":
    result = add_warehouse({
        "code": "EAITEST001",
        "name": "EAI自动化测试仓库",
        "valuestyle": "全月平均法",
        "barcode": "BC001",
    })
    print(f"仓库档案结果: {result}")
    print(f"成功: {result.is_success}")
    print(f"描述: {result.desc}")
