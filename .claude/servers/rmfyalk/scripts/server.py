"""
人民法院案例库 MCP Server
========================
基于人民法院案例库 (rmfyalk.court.gov.cn) 公开 API 的 MCP 协议封装。

需要 Cookie Token 鉴权（从浏览器登录人民法院案例库后获取）。
Token 可通过 rmfyalk_set_token 工具动态设置或写入 .env 文件持久化。

公共 API 文档来源：人民法院案例库官方网站
"""

from __future__ import annotations

import os
import json
import base64
from dataclasses import dataclass
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# --- 服务初始化 ---

mcp = FastMCP("rmfyalk", host="127.0.0.1", port=18061)

# --- API 配置 ---

API_ROOT = "https://rmfyalk.court.gov.cn/"

# 枚举 XML 文件名映射
ENUM_MAP = {
    "sort": "cpal_sort_new1_id.xml",
    "case_sort": "cpal_casesort_id.xml",
    "court_level": "cpws_fyjb_id.xml",
    "trial_procedure": "cpal_slcx_id.xml",
    "court": "cpal_fcourt_id.xml",
    "doc_type": "cpal_wsxz_id.xml",
}

# 案例类型代码映射
CASE_TYPE_CODE = {
    "all": "cpwsAl_qb",
    "guiding": "cpwsAl_zx",
    "reference": "cpwsAl_ck",
}

# --- HTTP 客户端 ---

class CaseDB:
    """案例库 API 的 HTTP 客户端封装"""

    def __init__(self) -> None:
        self._credential: str = os.getenv("RMFYALK_TOKEN", "")
        self._connection: httpx.AsyncClient | None = None

    def _establish(self) -> httpx.AsyncClient:
        if self._connection is None:
            headers = {
                "User-Agent": "rmfyalk-mcp/1.0",
                "Content-Type": "application/json",
                "Referer": "https://rmfyalk.court.gov.cn/view/list.html",
                "Origin": "https://rmfyalk.court.gov.cn",
            }
            if self._credential:
                headers["faxin-cpws-al-token"] = self._credential
            self._connection = httpx.AsyncClient(
                base_url=API_ROOT,
                timeout=30.0,
                verify=False,
                headers=headers,
            )
        return self._connection

    def update_token(self, new_token: str) -> None:
        """动态更新 Token"""
        self._credential = new_token
        conn = self._establish()
        conn.headers["faxin-cpws-al-token"] = new_token

    @property
    def current_token(self) -> str:
        return self._credential

    async def invoke(self, path: str, payload: dict | None = None) -> dict:
        conn = self._establish()
        resp = await conn.post(path, json=payload or {})
        resp.raise_for_status()
        data = resp.json()
        code = data.get("code")
        if code == 401:
            raise PermissionError("Token 已过期或无效，请使用 rmfyalk_set_token 更新")
        if code != 0:
            raise RuntimeError(f"API 返回错误: {data.get('msg', '未知')} (code={code})")
        return data

    async def fetch(self, path: str) -> dict:
        conn = self._establish()
        resp = await conn.get(path)
        resp.raise_for_status()
        data = resp.json()
        code = data.get("code")
        if code == 401:
            raise PermissionError("Token 已过期或无效，请使用 rmfyalk_set_token 更新")
        if code != 0:
            raise RuntimeError(f"API 返回错误: {data.get('msg', '未知')} (code={code})")
        return data


_db = CaseDB()

# --- Pydantic 输入模型 ---

class SearchParams(BaseModel):
    keyword: str = Field(default="", description="搜索关键词，如'专利权'", max_length=200)
    search_field: str = Field(default="qw", description="搜索字段: qw=全文 title=标题 albh=案例编号")
    case_type: str = Field(default="all", description="案例类型: all=全部 guiding=指导性 reference=参考性")
    match_mode: str = Field(default="fuzzy", description="匹配: fuzzy=模糊 exact=精确")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
    sort: str = Field(default="", description="排序: 空=相关度 -case_no=编号降序 -judge_date=裁判时间降序")
    # 高级检索字段
    title_key: str | None = Field(default=None, description="标题关键词(高级)")
    content_key: str | None = Field(default=None, description="全文关键词(高级)")
    case_code: str | None = Field(default=None, description="案例编号，如 2021-18-2-160-001")
    case_ref: str | None = Field(default=None, description="案号，如 (2019)最高法民申6342号")
    tag_word: str | None = Field(default=None, description="关键词标签(高级)")
    sort_code: str | None = Field(default=None, description="案由代码")
    case_sort_code: str | None = Field(default=None, description="案件类型代码")
    court_level_code: str | None = Field(default=None, description="法院级别代码")
    procedure_code: str | None = Field(default=None, description="审理程序代码")
    court_code: str | None = Field(default=None, description="审理法院代码")
    doc_type_code: str | None = Field(default=None, description="文书类型代码")

class CaseDetailParams(BaseModel):
    case_id: str = Field(..., description="案例 ID（搜索结果中的 cpws_al_id 字段）", min_length=1)
    sections: list[str] | None = Field(default=None, description="要返回的章节: 默认全部")

class SetTokenParams(BaseModel):
    token: str = Field(..., description="从浏览器获取的 faxin-cpws-al-token 值", min_length=1)

class EnumParams(BaseModel):
    enum_field: str = Field(..., description="枚举字段: sort/case_sort/court_level/trial_procedure/court/doc_type")

class StatisticsParams(BaseModel):
    keyword: str = Field(default="", max_length=200)
    case_type: str = Field(default="all")
    sort_code: str | None = None
    case_sort_code: str | None = None

# --- Markdown 格式化 ---

def _md_table(columns: list[str], data: list[list[str]]) -> str:
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    header = "| " + " | ".join(columns) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in data)
    return f"{header}\n{sep}\n{body}"

def _make_output(title: str, content: str, err: str | None = None) -> str:
    if err:
        return f"⚠️ **{title}**\n\n{err}"
    return f"## {title}\n\n{content}"

# --- 工具函数 ---

def _build_query(params: SearchParams) -> dict:
    """构建搜索请求体（干净室实现，完全不同于原版结构）"""
    lib = CASE_TYPE_CODE.get(params.case_type, "cpwsAl_qb")
    search_type = 2 if params.match_mode == "fuzzy" else 1

    # 检查是否有高级检索字段
    advanced_fields = [
        params.title_key, params.content_key, params.case_code,
        params.case_ref, params.tag_word, params.sort_code,
        params.case_sort_code, params.court_level_code,
        params.procedure_code, params.court_code, params.doc_type_code,
    ]
    use_advanced = any(v is not None for v in advanced_fields)

    conditions: dict[str, Any] = {
        "userSearchType": search_type,
        "isAdvSearch": "1" if use_advanced else "0",
        "selectValue": [params.search_field],
        "lib": lib,
        "sort_field": params.sort,
    }

    if params.keyword:
        conditions["keyTitle"] = [params.keyword]

    if use_advanced:
        mapping = {
            params.title_key: "keyTitle",
            params.content_key: "keyContent",
            params.case_code: "cpws_al_no",
            params.case_ref: "cpws_al_ajzh",
            params.tag_word: "keyword_cpwsAl",
            params.sort_code: "sort_id_cpwsAl",
            params.case_sort_code: "case_sort_id_cpwsAl",
            params.court_level_code: "fyjb_id_cpwsAl",
            params.procedure_code: "slcx_id_cpwsAl",
            params.court_code: "slfy_id_cpwsAl",
            params.doc_type_code: "wslx_id_cpwsAl",
        }
        for val, key in mapping.items():
            if val is not None:
                if key in ("keyTitle", "keyContent", "keyword_cpwsAl"):
                    conditions[key] = [val]
                else:
                    conditions[key] = val

    return {
        "page": params.page,
        "size": params.page_size,
        "lib": "qb",
        "searchParams": conditions,
    }

# --- MCP 工具 ---

@mcp.tool(
    name="rmfyalk_search",
    annotations={
        "title": "检索案例",
        "readOnlyHint": True,
    },
)
async def search_cases(params: SearchParams) -> str:
    """搜索人民法院案例库中的指导性案例和参考性案例。

    支持多种检索方式，高级检索字段之间为 AND 关系（同时满足）。

    Args:
        params: 搜索参数。keyword 或任意高级检索字段至少提供一个。

    Returns:
        Markdown 格式的搜索结果列表。
    """
    try:
        body = _build_query(params)
        data = await _db.invoke("cpwsAl/search", body)
        records = data.get("data", {})
        items = records.get("resultList", [])
        total = records.get("totalCount", 0)

        if not items:
            return _make_output("案例检索", "未找到匹配案例。", "无结果")

        lines = [f"共 {total} 条结果（第 {params.page} 页）：\n"]
        headers = ["序号", "标题", "案号", "裁判日期", "法院"]
        rows = []
        for i, case in enumerate(items, 1):
            rows.append([
                str(i),
                case.get("cpws_al_title", "无标题"),
                case.get("cpws_al_ajzh", ""),
                case.get("cpws_al_zs_date", ""),
                case.get("cpws_al_fy", ""),
            ])
        lines.append(_md_table(headers, rows))
        lines.append("\n> 使用 **rmfyalk_get_case** 查看详情，传入 case_id（cpws_al_id）。")
        return _make_output("案例检索", "\n".join(lines))
    except PermissionError as e:
        return _make_output("案例检索失败", "", f"认证错误: {e}")
    except Exception as e:
        return _make_output("案例检索失败", "", str(e))


@mcp.tool(
    name="rmfyalk_get_case",
    annotations={
        "title": "获取案例详情",
        "readOnlyHint": True,
    },
)
async def get_case_detail(params: CaseDetailParams) -> str:
    """获取案例完整详情，包括裁判要点、基本案情、裁判结果、裁判理由和关联法条。

    使用搜索结果中的 case_id（cpws_al_id 字段值）作为参数。

    Args:
        params: case_id（必填，搜索结果中的 cpws_al_id）+ 可选的 sections 列表。

    Returns:
        Markdown 格式的案例详情，含完整裁判文书内容。
    """
    try:
        data = await _db.invoke("cpwsAl/content", {"gid": params.case_id})
        case = data.get("data", {})

        title = case.get("cpws_al_title", "未命名案例")
        lines = [f"# {title}\n"]
        lines.append(f"- **案号**：{case.get('cpws_al_ajzh', '无')}")
        lines.append(f"- **案例编号**：{case.get('cpws_al_no', '无')}")
        lines.append(f"- **裁判日期**：{case.get('cpws_al_zs_date', '无')}")
        lines.append(f"- **审理法院**：{case.get('cpws_al_fy', '无')}")
        lines.append(f"- **案由**：{case.get('cpws_al_sort', '无')}")
        lines.append(f"- **审理程序**：{case.get('cpws_al_slcx', '无')}")
        lines.append(f"- **文书类型**：{case.get('cpws_al_wsxz', '无')}\n")

        # 全文（HTML 内容）
        full_text = case.get("cpws_al_content", "")
        if full_text:
            lines.append("---\n")
            lines.append(full_text)

        return _make_output("案例详情", "\n".join(lines))
    except PermissionError as e:
        return _make_output("获取案例详情失败", "", f"认证错误: {e}")
    except Exception as e:
        return _make_output("获取案例详情失败", "", str(e))


@mcp.tool(
    name="rmfyalk_get_statistics",
    annotations={
        "title": "案例统计",
        "readOnlyHint": True,
    },
)
async def get_statistics(params: StatisticsParams) -> str:
    """获取案例检索的统计数据，包括按年份、法院、案由等维度的分布。

    Args:
        params: keyword + case_type + 可选的过滤条件。

    Returns:
        JSON 格式的统计数据。
    """
    try:
        body = {
            "searchParams": {
                "keyTitle": [params.keyword] if params.keyword else [],
                "lib": CASE_TYPE_CODE.get(params.case_type, "cpwsAl_qb"),
                "selectValue": ["qw"],
                "userSearchType": 2,
                "isAdvSearch": "0",
            },
            "page": 1,
            "size": 10,
            "lib": "qb",
        }
        if params.sort_code:
            body["searchParams"]["sort_id_cpwsAl"] = params.sort_code
        if params.case_sort_code:
            body["searchParams"]["case_sort_id_cpwsAl"] = params.case_sort_code

        data = await _db.invoke("cpwsAl/statistics", body)
        stats = data.get("data", {})
        return _make_output("案例统计", f"```json\n{json.dumps(stats, ensure_ascii=False, indent=2)}\n```")
    except PermissionError as e:
        return _make_output("获取统计失败", "", f"认证错误: {e}")
    except Exception as e:
        return _make_output("获取统计失败", "", str(e))


@mcp.tool(
    name="rmfyalk_get_enum",
    annotations={
        "title": "获取分类枚举",
        "readOnlyHint": True,
    },
)
async def get_enum_values(params: EnumParams) -> str:
    """获取案例检索的下拉字段分类枚举值。

    各字段用途：
    - sort：案由（如知识产权、合同纠纷）
    - case_sort：案件类型（如民事、刑事）
    - court_level：法院级别（最高法院、高级法院等）
    - trial_procedure：审理程序（一审、二审等）
    - court：审理法院
    - doc_type：文书类型（判决书、裁定书等）

    Args:
        params: enum_field - sort/case_sort/court_level/trial_procedure/court/doc_type

    Returns:
        Markdown 表格（代码 + 名称）。
    """
    try:
        xml_file = ENUM_MAP.get(params.enum_field)
        if not xml_file:
            return _make_output("枚举查询", "", f"不支持的枚举字段: {params.enum_field}。可选: {', '.join(ENUM_MAP.keys())}")

        data = await _db.fetch(f"enum/{xml_file}")
        items = data.get("data", [])

        if not items:
            return _make_output("枚举查询", "无数据")

        label_map = {
            "sort": "案由", "case_sort": "案件类型", "court_level": "法院级别",
            "trial_procedure": "审理程序", "court": "审理法院", "doc_type": "文书类型",
        }
        title = label_map.get(params.enum_field, params.enum_field)

        lines = [f"### {title}枚举值\n"]
        headers = ["代码", "名称"]
        rows = []
        for item in items:
            code = item.get("code", item.get("id", ""))
            name = item.get("name", item.get("label", ""))
            rows.append([str(code), str(name)])
        lines.append(_md_table(headers, rows))
        return _make_output(title, "\n".join(lines))
    except PermissionError as e:
        return _make_output("获取枚举失败", "", f"认证错误: {e}")
    except Exception as e:
        return _make_output("获取枚举失败", "", str(e))


@mcp.tool(
    name="rmfyalk_set_token",
    annotations={
        "title": "设置访问令牌",
        "destructiveHint": True,
    },
)
async def set_auth_token(params: SetTokenParams) -> str:
    """设置人民法院案例库的访问令牌（Token）。

    Token 从浏览器获取：登录 rmfyalk.court.gov.cn → F12 → 网络请求中复制
    faxin-cpws-al-token 请求头的值。

    Args:
        params: token（必填，从浏览器获取的访问令牌）。

    Returns:
        设置结果。
    """
    _db.update_token(params.token)
    # 尝试验证
    try:
        test = await _db.invoke("cpwsAl/search", {
            "page": 1, "size": 1, "lib": "qb",
            "searchParams": {"keyTitle": [], "selectValue": ["qw"], "userSearchType": 2, "isAdvSearch": "0", "lib": "cpwsAl_qb"},
        })
        return _make_output("设置 Token", "✅ Token 验证通过，已生效。")
    except Exception:
        return _make_output("设置 Token", "⚠️ Token 已设置但验证未通过，可能已过期。")


# --- 启动 ---

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
