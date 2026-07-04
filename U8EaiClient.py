# -*- coding: utf-8 -*-
"""
U8 EAI 接口客户端 - 基础模块
===========================
通过 U8 EAI (Enterprise Application Integration) HTTP 接口调用 U8 各业务单据。
基于 U8 12.0 验证通过。

EAI 配置要求：
  - U8 服务器: localhost（或指定IP）
  - 外部系统编码: 001（在 U8 EAI接口配置 → 外部系统注册 中配置）
  - EAI 数据源: test001

调用方式:
  from U8EaiClient import U8EaiClient
  
  client = U8EaiClient(
      eai_url="http://localhost/u8eai/import.asp",
      sender="001",       # 外部系统编码
      receiver="U8"       # U8 系统
  )
  
  result = client.send("inventory", "add", xml_body)
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any


class EaiResult:
    """EAI 接口返回结果"""
    
    def __init__(self, raw_xml: str):
        self.raw_xml = raw_xml
        self.succeed: int = -1
        self.key: str = ""
        self.desc: str = ""
        self.u8key: str = ""
        self._parse(raw_xml)
    
    def _parse(self, xml_str: str):
        """解析返回的 XML"""
        try:
            root = ET.fromstring(xml_str)
            # 查找 item 节点
            item = root.find(".//item")
            if item is not None:
                self.succeed = int(item.get("succeed", "-1"))
                self.key = item.get("key", "")
                self.desc = item.get("dsc", "")
                self.u8key = item.get("u8key", "")
        except ET.ParseError:
            self.desc = xml_str
    
    @property
    def is_success(self) -> bool:
        """判断是否成功 (succeed=0 表示成功)"""
        return self.succeed == 0
    
    def __repr__(self):
        status = "SUCCESS" if self.is_success else "FAILED"
        return f"EaiResult({status}, succeed={self.succeed}, desc={self.desc}, key={self.key})"


class U8EaiClient:
    """
    U8 EAI 接口客户端
    
    通过 HTTP POST 发送 XML 到 U8 EAI 接口，实现各业务单据的新增/修改/删除操作。
    """
    
    # 默认配置
    DEFAULT_URL = "http://localhost/u8eai/import.asp"
    DEFAULT_SENDER = "001"    # 外部系统编码（在EAI接口配置中注册）
    DEFAULT_RECEIVER = "U8"  # U8 系统
    
    def __init__(
        self,
        eai_url: str = None,
        sender: str = None,
        receiver: str = None,
        timeout: int = 30
    ):
        self.eai_url = eai_url or self.DEFAULT_URL
        self.sender = sender or self.DEFAULT_SENDER
        self.receiver = receiver or self.DEFAULT_RECEIVER
        self.timeout = timeout
    
    def send(
        self,
        roottag: str,
        operation: str,
        header_data: Dict[str, Any],
        body_data: list = None,
        version: str = "2.0"
    ) -> EaiResult:
        """
        发送 EAI 请求
        
        Args:
            roottag: 业务对象类型，如 "inventory", "customer", "vendor", "storein" 等
            operation: 操作类型，如 "add"(新增), "edit"(修改), "delete"(删除)
            header_data: 表头数据字典，key 为 EAI 模板中的字段名
            body_data: 表体数据列表（可选），每行为一个字典
            version: EAI 版本号，默认 2.0
        
        Returns:
            EaiResult 对象
        """
        xml_body = self._build_xml(roottag, header_data, body_data, operation, version)
        return self._post(xml_body)
    
    def _build_xml(
        self,
        roottag: str,
        header_data: Dict[str, Any],
        body_data: list = None,
        operation: str = "add",
        version: str = "2.0"
    ) -> str:
        """构建 EAI XML 请求体"""
        
        # 构建 header 节点
        header_lines = []
        for key, value in header_data.items():
            if value is not None:
                header_lines.append(f"      <{key}>{value}</{key}>")
        header_str = "\n".join(header_lines)
        
        # 构建 body 节点
        if body_data:
            entry_lines = []
            for row in body_data:
                field_lines = [f"        <{k}>{v}</{k}>" for k, v in row.items() if v is not None]
                entry_lines.append(f"      <entry>\n" + "\n".join(field_lines) + "\n      </entry>")
            body_str = "\n".join(entry_lines)
        else:
            body_str = ""
        
        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<ufinterface roottag="{roottag}" billtype="" docid="" receiver="{self.receiver}" 
             sender="{self.sender}" proc="{operation}" codeexchanged="" exportneedexch="" version="{version}">
  <{roottag}>
    <header>
{header_str}
    </header>
    <body>
{body_str}
    </body>
  </{roottag}>
</ufinterface>'''
        
        return xml
    
    def _post(self, xml_body: str) -> EaiResult:
        """POST 发送 XML 到 EAI 接口"""
        data = xml_body.encode("utf-8")
        headers = {"Content-Type": "application/xml; charset=utf-8"}
        req = urllib.request.Request(
            self.eai_url,
            data=data,
            headers=headers,
            method="POST"
        )
        
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            return EaiResult(text)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            return EaiResult(
                f'<ufinterface><item succeed="-1" dsc="HTTP {e.code}: {body}"/></ufinterface>'
            )
        except Exception as e:
            return EaiResult(
                f'<ufinterface><item succeed="-1" dsc="{str(e)}"/></ufinterface>'
            )
    
    def test_connection(self) -> bool:
        """测试 EAI 连接是否可用"""
        try:
            req = urllib.request.Request(self.eai_url, method="GET")
            resp = urllib.request.urlopen(req, timeout=5)
            return resp.status == 200
        except:
            return False


# === 便捷函数 ===

def get_client(
    url: str = None,
    sender: str = "001",
    receiver: str = "U8"
) -> U8EaiClient:
    """获取 EAI 客户端实例（便捷方法）"""
    return U8EaiClient(eai_url=url, sender=sender, receiver=receiver)


if __name__ == "__main__":
    # 测试连接
    client = get_client()
    print(f"EAI URL: {client.eai_url}")
    print(f"连接测试: {'OK' if client.test_connection() else 'FAIL'}")
