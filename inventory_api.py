# -*- coding: utf-8 -*-
"""
U8 EAI - 存货档案接口 (IF-201)
===============================
✅ 已验证通过 | 正确格式：使用 U8EaiClient.send() 自动构建带 <header>/<body> 节点的XML

正确字段名（从U8导出XML + 用户截图确认）:
  code          - 存货编码（必填）
  name          - 存货名称（必填）
  sort_code     - 存货分类编码（必填）
  unitgroup_code - 计量单位组（必填）
  main_measure  - 主计量单位（必填）
  sale_flag     - 内销（必填）
  purchase_flag - 采购（必填）
  selfmake_flag - 自制（必填）
  prod_consu_flag - 生产耗用（必填）
  cPlanMethod   - 计划方法（U8必填，默认 R）
  cSRPolicy     - 供需政策（U8必填，默认 PE）
  iSupplyType   - 供应类型（U8必填，默认 0）
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from U8EaiClient import U8EaiClient, EaiResult


class InventoryApi:
    """存货档案 EAI 接口"""
    ROOTTAG = "inventory"

    def __init__(self, client: U8EaiClient = None):
        self.client = client or U8EaiClient()

    def add(self, data: dict) -> EaiResult:
        """新增存货档案

        最小必填:
          code (code)              - 存货编码
          name (name)              - 存货名称
          sort_code (sort_code)    - 存货分类编码

        可选字段会自动补充默认值（对应用户U8界面框出的字段）。
        """
        defaults = {
            "unitgroup_code": "01",
            "main_measure": "01",
            "sale_flag": "1",
            "purchase_flag": "1",
            "selfmake_flag": "0",
            "prod_consu_flag": "0",
            "cPlanMethod": "R",
            "cSRPolicy": "PE",
            "iSupplyType": "0",
        }
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v

        # 字段映射：用户友好名 → EAI字段名（与U8导出XML一致）
        field_map = {
            "code": "code",
            "name": "name",
            "sort_code": "sort_code",
            "unitgroup_code": "unitgroup_code",
            "main_measure": "main_measure",
            "sale_flag": "sale_flag",
            "purchase_flag": "purchase_flag",
            "selfmake_flag": "selfmake_flag",
            "prod_consu_flag": "prod_consu_flag",
            "cPlanMethod": "cPlanMethod",
            "cSRPolicy": "cSRPolicy",
            "iSupplyType": "iSupplyType",
            "specs": "specs",
            "unitgroup_name": "unitgroup_name",
            "ccomunitname": "ccomunitname",
        }

        # 构造 header_data
        header_data = {}
        for key, value in data.items():
            if value is not None:
                xml_key = field_map.get(key, key)
                header_data[xml_key] = value

        # 使用 U8EaiClient.send() 自动构建带 <header>/<body> 的XML
        return self.client.send(self.ROOTTAG, "add", header_data)


def add_inventory(data: dict) -> EaiResult:
    """快捷函数：新增存货档案"""
    return InventoryApi().add(data)


if __name__ == "__main__":
    result = add_inventory({
        "code": "EAITEST001",
        "name": "EAI自动化测试存货",
        "sort_code": "01",
    })
    print(f"存货档案结果: {result}")
    print(f"成功: {result.is_success}")
    print(f"描述: {result.desc}")
