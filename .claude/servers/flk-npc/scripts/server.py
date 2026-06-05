"""
国家法规数据库 MCP Server
======================
基于国家法律法规数据库 (flk.npc.gov.cn) 公开 API 的 MCP 协议封装，干净室实现。

可独立部署，无需第三方 API Key，免费使用。

公共 API 文档来源：国家法律法规数据库官方网站
"""

from __future__ import annotations

import os
import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# --- 服务初始化 ---

mcp = FastMCP("flk-npc", host="127.0.0.1", port=18062)

# --- API 配置 ---

API_BASE = "https://flk.npc.gov.cn/law-search/"
REQUEST_DELAY = 0.5  # 请求间隔（秒），遵守网站限频要求

# --- HTTP 客户端 ---

class LawIndex:
    """国家法规库 API 的 HTTP 客户端封装"""

    def __init__(self) -> None:
        self._handle: httpx.AsyncClient | None = None
        self._last_call: float = 0.0

    def _acquire(self) -> httpx.AsyncClient:
        if self._handle is None or self._handle.is_closed:
            self._handle = httpx.AsyncClient(
                base_url=API_BASE,
                headers={
                    "User-Agent": "flk-npc-mcp/1.0",
                    "Content-Type": "application/json",
                    "Referer": "https://flk.npc.gov.cn/",
                    "Origin": "https://flk.npc.gov.cn",
                },
                timeout=30.0,
            )
        return self._handle

    async def _throttle(self) -> None:
        now = time.monotonic()
        gap = now - self._last_call
        if gap < REQUEST_DELAY:
            await asyncio.sleep(REQUEST_DELAY - gap)
        self._last_call = time.monotonic()

    async def post(self, suffix: str, payload: dict | None = None) -> dict:
        await self._throttle()
        client = self._acquire()
        resp = await client.post(suffix, json=payload or {})
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"API 异常: {data.get('msg', '未知错误')} (code={data.get('code')})")
        return data

    async def get(self, suffix: str) -> dict:
        await self._throttle()
        client = self._acquire()
        resp = await client.get(suffix)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 200:
            raise RuntimeError(f"API 异常: {data.get('msg', '未知错误')} (code={data.get('code')})")
        return data


_api = LawIndex()

# --- Pydantic 输入模型 ---

class SearchParams(BaseModel):
    keyword: str = Field(default="", description="搜索关键词", max_length=200)
    match_mode: int = Field(default=2, description="匹配模式：1=精确 2=模糊(默认)", ge=1, le=2)
    scope: int = Field(default=1, description="搜索范围：1=标题(默认) 2=全文", ge=1, le=2)
    category_ids: list[str] = Field(default_factory=list, description="法律分类代码（从 flk_get_categories 获取）")
    authority_ids: list[str] = Field(default_factory=list, description="制定机关代码（从 flk_get_authorities 获取）")
    year_filter: list[str] = Field(default_factory=list, description="公布年份过滤，如 ['2024']")
    validity: int | None = Field(default=None, description="时效性：1=已废止 2=已被修改 3=生效中(默认) 4=未生效", ge=1, le=4)
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页条数", ge=1, le=50)

class LawDetailParams(BaseModel):
    law_id: str = Field(..., description="法规 ID（搜索结果中的 bbbs 字段）", min_length=1)

class HitDisplayParams(BaseModel):
    law_id: str = Field(..., description="法规 ID")
    keyword: str = Field(..., description="搜索关键词")
    match_mode: int = Field(default=2, ge=1, le=2)
    scope: int = Field(default=1, ge=1, le=2)

class EnumParams(BaseModel):
    enum_key: str = Field(..., description="枚举键：flfgfl(法律分类) zdjgfl(制定机关) sxx(时效性)")

class SuggestParams(BaseModel):
    keyword: str = Field(..., description="搜索关键词前缀", max_length=100)

class RelatedParams(BaseModel):
    law_id: str = Field(..., description="法规 ID")

class AdvancedSearchParams(BaseModel):
    keyword: str = Field(default="", description="搜索关键词")
    scope: int = Field(default=1, ge=1, le=2)
    category_ids: list[str] = Field(default_factory=list)
    authority_ids: list[str] = Field(default_factory=list)
    year_filter: list[str] = Field(default_factory=list)
    validity: int | None = Field(default=None, ge=1, le=4)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

class AdvancedRelatedParams(BaseModel):
    law_id: str = Field(..., min_length=1)
    keyword: str = Field(default="")

# --- Markdown 格式化函数 ---

def _fmt_table(headers: list[str], rows: list[list[str]]) -> str:
    """生成 Markdown 表格"""
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    header = "| " + " | ".join(headers) + " |"
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return f"{header}\n{sep}\n{body}"

def _wrap_result(title: str, content: str, error: str | None = None) -> str:
    if error:
        return f"⚠️ **{title}**\n\n{error}"
    return f"## {title}\n\n{content}"

# --- MCP 工具（按功能分组） ---

# 1. 基础搜索

@mcp.tool(
    name="flk_search",
    annotations={
        "title": "检索法律法规",
        "readOnlyHint": True,
    },
)
async def search_laws(params: SearchParams) -> str:
    """在国家法律法规数据库中检索法律、行政法规、部门规章、司法解释等。

    支持标题搜索和全文搜索，可按分类、制定机关、年份、时效性等条件过滤。

    Args:
        params: 搜索参数。keyword 为关键词，scope 控制搜索范围（1=标题, 2=全文）。

    Returns:
        Markdown 格式的搜索结果列表，每条包含 ID、标题、状态、制定机关等。
    """
    try:
        body = {
            "searchContent": params.keyword,
            "searchType": params.match_mode,
            "searchRange": params.scope,
            "flfgCodeId": params.category_ids,
            "zdjgCodeId": params.authority_ids,
            "gbrqYear": params.year_filter,
            "sxx": [params.validity] if params.validity is not None else [],
            "orderByParam": {"order": "", "sort": ""},
            "pageNum": params.page,
            "pageSize": params.page_size,
        }
        data = await _api.post("search/list", body)
        rows = data.get("rows", [])
        total = data.get("total", 0)

        if not rows:
            return _wrap_result("检索结果", "未找到匹配的法律法规。", "无结果")

        output = [f"共 {total} 条结果（第 {params.page} 页）：\n"]
        headers = ["序号", "标题", "时效性", "制定机关", "公布日期"]
        table_rows = []
        for i, item in enumerate(rows, 1):
            table_rows.append([
                str(i),
                item.get("title", "无标题"),
                _validity_label(item.get("sxx", 0)),
                item.get("zdjg", ""),
                item.get("gbrq", ""),
            ])
        output.append(_fmt_table(headers, table_rows))
        output.append(f"\n> 使用 **flk_get_detail** 查看完整内容，需传入 law_id（搜索结果中的 bbbs）。")
        return _wrap_result("检索结果", "\n".join(output))
    except Exception as e:
        return _wrap_result("检索失败", "", str(e))


def _validity_label(code: int) -> str:
    """时效性代码转中文"""
    labels = {0: "未知", 1: "已废止", 2: "已被修改", 3: "生效中", 4: "未生效"}
    return labels.get(code, f"代码{code}")


# 2. 法规详情

@mcp.tool(
    name="flk_get_detail",
    annotations={
        "title": "获取法规详情",
        "readOnlyHint": True,
    },
)
async def get_law_detail(params: LawDetailParams) -> str:
    """获取指定法律法规的完整详情，包括目录结构、正文和各版本。

    使用搜索结果中的 law_id（bbbs 字段）作为参数。

    Args:
        params: law_id（必填，法规 ID）。

    Returns:
        Markdown 格式的法规详情，含完整章节/条目目录树。
    """
    try:
        data = await _api.get(f"search/flfgDetails?bbbs={params.law_id}")
        info = data.get("data", {})

        title = info.get("title", "未命名法规")
        lines = [f"# {title}\n"]
        lines.append(f"- **时效性**：{_validity_label(info.get('sxx', 0))}")
        lines.append(f"- **制定机关**：{info.get('zdjg', '无')}")
        lines.append(f"- **公布日期**：{info.get('gbrq', '无')}")
        lines.append(f"- **施行日期**：{info.get('sxrq', '无')}")
        lines.append(f"- **法规编号**：{info.get('flgid', '无')}\n")

        # 章节树
        chapters = info.get("catalogTree", [])
        if chapters:
            lines.append("## 目录结构\n")
            _render_tree(chapters, lines, indent=0)

        # 正文
        articles = info.get("articleList", [])
        if articles:
            lines.append("\n## 正文\n")
            for art in articles:
                seq = art.get("articleSeq", "")
                text = art.get("articleBody", "")
                lines.append(f"**第{seq}条** {text}\n")

        return _wrap_result("法规详情", "\n".join(lines))
    except Exception as e:
        return _wrap_result("获取详情失败", "", str(e))


def _render_tree(nodes: list[dict], lines: list[str], indent: int = 0) -> None:
    """递归渲染目录树"""
    prefix = "  " * indent
    for node in nodes:
        label = node.get("catalogName", node.get("chapterName", ""))
        lines.append(f"{prefix}- **{label}**")
        children = node.get("children", [])
        if children:
            _render_tree(children, lines, indent + 1)


# 3. 命中显示

@mcp.tool(
    name="flk_hit_display",
    annotations={
        "title": "法条命中定位",
        "readOnlyHint": True,
    },
)
async def show_hits(params: HitDisplayParams) -> str:
    """获取指定法规中关键词命中的法条片段，用于快速定位适用法条。

    Args:
        params: law_id（法规 ID）+ keyword（搜索关键词）。

    Returns:
        Markdown 格式的命中法条片段列表，关键词已加粗显示。
    """
    try:
        body = {
            "bbbs": params.law_id,
            "searchContent": params.keyword,
            "searchType": params.match_mode,
            "searchRange": params.scope,
        }
        data = await _api.post("search/hitDisplay", body)
        rows = data.get("rows", [])
        if not rows:
            return _wrap_result("命中定位", "未找到匹配的法条。", "无命中")

        output = [f"在法规中搜索「{params.keyword}」找到 {len(rows)} 处命中：\n"]
        for hit in rows:
            seq = hit.get("AS", "")
            text = hit.get("DZNR", "")
            output.append(f"- **第{seq}条**：{text}\n")

        return _wrap_result("命中定位", "\n".join(output))
    except Exception as e:
        return _wrap_result("命中定位失败", "", str(e))


# 4. 枚举查询

@mcp.tool(
    name="flk_get_categories",
    annotations={
        "title": "获取分类枚举",
        "readOnlyHint": True,
    },
)
async def get_categories(params: EnumParams) -> str:
    """获取法律分类/制定机关等枚举数据，用于搜索过滤。

    Args:
        params: enum_key - flfgfl（法律分类）或 zdjgfl（制定机关）。

    Returns:
        Markdown 格式的枚举列表，包含代码和名称。
    """
    try:
        data = await _api.get(f"search/enum?key={params.enum_key}")
        items = data.get("data", [])
        if not items:
            return _wrap_result("分类枚举", "无数据", "未获取到枚举值")

        label_map = {"flfgfl": "法律分类", "zdjgfl": "制定机关", "sxx": "时效性"}
        title = label_map.get(params.enum_key, f"枚举({params.enum_key})")

        output = [f"### {title}\n"]
        headers = ["代码", "名称"]
        table_rows = []
        for item in items:
            code = item.get("code", item.get("id", ""))
            name = item.get("name", item.get("label", ""))
            table_rows.append([str(code), str(name)])

        output.append(_fmt_table(headers, table_rows))
        return _wrap_result(title, "\n".join(output))
    except Exception as e:
        return _wrap_result("获取枚举失败", "", str(e))


# 5. 搜索建议

@mcp.tool(
    name="flk_suggest",
    annotations={
        "title": "搜索建议",
        "readOnlyHint": True,
    },
)
async def get_suggestions(params: SuggestParams) -> str:
    """根据输入的前缀返回搜索建议词。

    Args:
        params: keyword（搜索前缀）。

    Returns:
        关键词建议列表。
    """
    try:
        data = await _api.post("search/suggest", {"searchContent": params.keyword})
        suggestions = data.get("data", [])
        if not suggestions:
            return _wrap_result("搜索建议", "无建议词")

        lines = [f"关键词「{params.keyword}」的建议：\n"]
        for s in suggestions:
            lines.append(f"- {s}")
        return _wrap_result("搜索建议", "\n".join(lines))
    except Exception as e:
        return _wrap_result("获取建议失败", "", str(e))


# 6. 关联法规

@mcp.tool(
    name="flk_related",
    annotations={
        "title": "关联法规",
        "readOnlyHint": True,
    },
)
async def get_related_laws(params: RelatedParams) -> str:
    """获取指定法规的关联法规列表。

    Args:
        params: law_id（法规 ID）。

    Returns:
        关联法规列表。
    """
    try:
        data = await _api.get(f"search/related?bbbs={params.law_id}")
        items = data.get("rows", [])
        if not items:
            return _wrap_result("关联法规", "无关联法规")

        output = ["### 关联法规\n"]
        headers = ["标题", "时效性", "制定机关", "公布日期"]
        table_rows = []
        for item in items:
            table_rows.append([
                item.get("title", ""),
                _validity_label(item.get("sxx", 0)),
                item.get("zdjg", ""),
                item.get("gbrq", ""),
            ])
        output.append(_fmt_table(headers, table_rows))
        return _wrap_result("关联法规", "\n".join(output))
    except Exception as e:
        return _wrap_result("获取关联法规失败", "", str(e))


# 7. 高级搜索

@mcp.tool(
    name="flk_advanced_search",
    annotations={
        "title": "高级检索（精确）",
        "readOnlyHint": True,
    },
)
async def advanced_search(params: AdvancedSearchParams) -> str:
    """精确模式下的法律法规检索，适合需要精细过滤的场景。

    Args:
        params: 高级搜索参数，支持分类、机关、年份、时效性组合过滤。

    Returns:
        Markdown 搜索结果。
    """
    try:
        body = {
            "searchContent": params.keyword,
            "searchRange": params.scope,
            "flfgCodeId": params.category_ids,
            "zdjgCodeId": params.authority_ids,
            "gbrqYear": params.year_filter,
            "sxx": [params.validity] if params.validity is not None else [],
            "orderByParam": {"order": "", "sort": ""},
            "pageNum": params.page,
            "pageSize": params.page_size,
        }
        data = await _api.post("search/highSearch", body)
        rows = data.get("rows", [])
        total = data.get("total", 0)

        if not rows:
            return _wrap_result("高级检索", "未找到匹配结果。", "无结果")

        output = [f"共 {total} 条匹配（高级检索）：\n"]
        headers = ["序号", "标题", "制定机关", "公布日期"]
        table_rows = []
        for i, item in enumerate(rows, 1):
            table_rows.append([
                str(i),
                item.get("title", ""),
                item.get("zdjg", ""),
                item.get("gbrq", ""),
            ])
        output.append(_fmt_table(headers, table_rows))
        return _wrap_result("高级检索", "\n".join(output))
    except Exception as e:
        return _wrap_result("高级检索失败", "", str(e))


# --- 启动入口 ---

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
