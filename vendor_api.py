# -*- coding: utf-8 -*-
"""
U8 EAI - 供应商档案接口 (IF-204)
===============================
✅ 正确格式：字段直接放在 <vendor> 节点下，字段名用小写（跟客户档案一致）

正确字段名（从U8截图和测试确认）:
  code         - 供应商编码（必填）
  name         - 供应商名称（必填）
  abbrname     - 供应商简称（必填）
  sort_code    - 供应商分类编码（必填）
  seed_date    - 发展日期（必填）
  bvencargo    - 是否采购（必填，三项至少选一个）
  cvenexch_name - 币种（必填）
"""
import sys, os
from datetime import date
sys.path.insert(0, os.path.dirname(__file__))
from U8EaiClient import U8EaiClient, EaiResult


class VendorApi:
    """供应商档案 EAI 接口"""
    ROOTTAG = "vendor"

    def __init__(self, client: U8EaiClient = None):
        self.client = client or U8EaiClient()

    def add(self, data: dict) -> EaiResult:
        """新增供应商档案

        最小必填:
          code (code)           - 供应商编码
          name (name)           - 供应商名称
          abbrname (abbrname)   - 供应商简称
          sort_code (sort_code) - 分类编码（如"01"）
          seed_date (seed_date) - 发展日期

        可选字段会自动补充默认值。
        """
        defaults = {
            "seed_date": date.today().strftime("%Y-%m-%d") + " 00:00:00",
            "bvencargo": "1",            # 是否采购（默认采购）
            "bproxyforeign": "0",        # 是否委外
            "bvenservice": "0",          # 是否服务
            "cvenexch_name": "人民币",   # 币种
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v

        # 字段映射：用户友好名 → EAI字段名（小写，跟客户档案一致）
        field_map = {
            "code": "code",
            "name": "name",
            "abbrname": "abbrname",
            "sort_code": "sort_code",
            "seed_date": "seed_date",
            "cvenexch_name": "cvenexch_name",
            "bvencargo": "bvencargo",
            "bproxyforeign": "bproxyforeign",
            "bvenservice": "bvenservice",
            "contact": "contact",
            "phone": "phone",
            "tax_reg_code": "tax_reg_code",
            "Memo": "Memo",
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


def add_vendor(data: dict) -> EaiResult:
    """快捷函数：新增供应商档案"""
    return VendorApi().add(data)


if __name__ == "__main__":
    result = add_vendor({
        "code": "EAITEST001",
        "name": "EAI自动化测试供应商",
        "abbrname": "EAI测",
        "sort_code": "01",
        "seed_date": "2026-07-04 00:00:00",
    })
    print(f"供应商档案结果: {result}")
    print(f"成功: {result.is_success}")
    print(f"描述: {result.desc}")
