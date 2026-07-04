# -*- coding: utf-8 -*-
"""
U8 EAI - 客户档案接口 (IF-202)
===============================
✅ 已验证通过 | 正确使用格式：字段直接放在 <customer> 节点下，字段名用小写

正确字段名（从U8导出XML确认）:
  code       - 客户编码（必填）
  name       - 客户名称（必填）
  abbrname   - 客户简称（必填）
  sort_code  - 客户分类编码（必填）
  seed_date  - 发展日期（必填）
"""
import sys, os
from datetime import date
sys.path.insert(0, os.path.dirname(__file__))
from U8EaiClient import U8EaiClient, EaiResult


class CustomerApi:
    """客户档案 EAI 接口"""
    ROOTTAG = "customer"

    def __init__(self, client: U8EaiClient = None):
        self.client = client or U8EaiClient()

    def add(self, data: dict) -> EaiResult:
        """新增客户档案

        最小必填:
          code (code)         - 客户编码
          name (name)         - 客户名称
          abbrname (abbrname) - 客户简称
          sort_code (sort_code) - 客户分类编码
          seed_date (seed_date) - 发展日期

        可选字段会自动补充默认值。
        """
        defaults = {
            "seed_date": date.today().strftime("%Y-%m-%d") + " 00:00:00",
            "ccusexch_name": "人民币",
            "ccusmngtypecode": "999",  # 普通客户
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v

        # 构造XML字段
        field_lines = []
        for key, value in data.items():
            if value is not None:
                field_lines.append(f"    <{key}>{value}</{key}>")
        fields_xml = "\n".join(field_lines)

        xml_body = f'''<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="{self.ROOTTAG}" billtype="" docid="" receiver="{self.client.receiver}"
             sender="{self.client.sender}" proc="add" codeexchanged="" exportneedexch="" version="2.0">
  <{self.ROOTTAG}>
{fields_xml}
  </{self.ROOTTAG}>
</ufinterface>'''

        return self.client._post(xml_body)


def add_customer(data: dict) -> EaiResult:
    """快捷函数：新增客户档案"""
    return CustomerApi().add(data)


if __name__ == "__main__":
    result = add_customer({
        "code": "EAITEST001",
        "name": "EAI自动化测试客户",
        "abbrname": "EAI测",
        "sort_code": "01",
        "seed_date": "2026-07-04 00:00:00",
    })
    print(f"客户档案结果: {result}")
    print(f"成功: {result.is_success}")
    print(f"描述: {result.desc}")
