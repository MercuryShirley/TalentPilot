from __future__ import annotations

import json
import requests

from app.config import settings


def _safe_json_loads(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


def extract_profile_from_chat(chat_messages: list[str]) -> dict:
    merged = "\n".join(chat_messages)
    if not settings.llm_api_key:
        return {
            "interests": ["社交", "活动"],
            "skills": ["沟通"],
            "personality_tags": ["外向", "执行力"],
            "weekly_hours": 4,
            "chat_summary": "未配置LLM密钥，使用默认画像。",
        }

    prompt = (
        "你是高校社团招新助手。根据聊天内容提取结构化画像，严格返回JSON："
        '{"interests": [""], "skills": [""], "personality_tags": [""], "weekly_hours": 4, "chat_summary": ""}。'
        "不要输出JSON之外任何内容。聊天内容：\n"
        + merged
    )

    try:
        response = requests.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=settings.llm_timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = _safe_json_loads(content)
        if not parsed:
            raise ValueError("LLM返回非JSON")
        return parsed
    except Exception:
        return {
            "interests": ["社交", "活动"],
            "skills": ["沟通"],
            "personality_tags": ["外向", "执行力"],
            "weekly_hours": 4,
            "chat_summary": "LLM调用失败，使用默认画像。",
        }


def assess_personality_from_cards(assessment_answers: list[str]) -> dict:
    if not assessment_answers:
        return {
            "personality_tags": ["外向", "认真细致", "计划导向"],
            "personality_insight": "你更偏向主动沟通、结构化推进任务。",
        }

    if not settings.llm_api_key:
        return _fallback_assessment(assessment_answers)

    prompt = (
        "你是高校社团匹配产品的人格分析助手。"
        "用户给出了多道场景题选择，请输出人格标签和一句简短洞察。"
        "标签只允许从以下集合中选择3个："
        "[外向, 内向, 认真细致, 天马行空, 计划导向, 灵活应变]。"
        "严格返回JSON：{\"personality_tags\":[\"\",\"\",\"\"],\"personality_insight\":\"\"}。"
        f"用户选择：{json.dumps(assessment_answers, ensure_ascii=False)}"
    )

    try:
        response = requests.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=settings.llm_timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = _safe_json_loads(content)

        tags = parsed.get("personality_tags", [])
        insight = parsed.get("personality_insight", "")
        valid_tags = [
            tag
            for tag in tags
            if tag in {"外向", "内向", "认真细致", "天马行空", "计划导向", "灵活应变"}
        ]
        if len(valid_tags) >= 2:
            while len(valid_tags) < 3:
                valid_tags.append("计划导向")
            return {
                "personality_tags": valid_tags[:3],
                "personality_insight": insight or "你具备较好的社团适配潜力。",
            }
    except Exception:
        pass

    return _fallback_assessment(assessment_answers)


def _fallback_assessment(assessment_answers: list[str]) -> dict:
    joined = " ".join(assessment_answers)
    social = "外向" if any(word in joined for word in ["社交", "带动", "讨论", "公开表达"]) else "内向"
    thinking = "认真细致" if any(word in joined for word in ["拆解", "清单", "复盘", "稳妥"]) else "天马行空"
    execution = "计划导向" if any(word in joined for word in ["计划", "排期", "里程碑", "步骤"]) else "灵活应变"
    return {
        "personality_tags": [social, thinking, execution],
        "personality_insight": "你在社团场景中兼具参与意愿与执行潜力。",
    }


def chat_with_club_ai(club_name: str, category: str, intro: str, messages: list[dict]) -> str:
    if not messages:
        return "欢迎来咨询！你可以问我面试准备、工作节奏或成长路径。"

    if not settings.llm_api_key:
        return "当前AI学长暂时离线，建议先关注该社团的招新宣讲与公开活动。"

    system_prompt = (
        "你是高校社团招新中的‘AI学长’。回答要求："
        "1) 用中文，简洁真诚，2~4句；"
        "2) 优先回答用户问题，不说空话；"
        "3) 可结合社团信息给建议，但不要编造未提供的事实。"
        f"\n社团名称：{club_name}；类别：{category}；简介：{intro}"
    )

    chat_messages = [{"role": "system", "content": system_prompt}] + messages[-8:]

    try:
        response = requests.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": chat_messages,
                "temperature": 0.6,
            },
            timeout=settings.llm_timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "我这会儿网络有点忙，你可以先问我：面试看重什么、每周投入多少、零基础怎么准备。"


def chat_with_global_ai(clubs: list[dict], messages: list[dict]) -> str:
    if not messages:
        return "你好，我是智能社团助手。你可以告诉我兴趣方向、每周时间、是否零基础，我会给你具体社团和联系建议。"

    club_lines = []
    for c in clubs[:50]:
        name = c.get("name", "")
        category = c.get("category", "")
        intro = c.get("intro", "")
        club_lines.append(f"- {name}（{category}）：{intro}")
    club_context = "\n".join(club_lines) if club_lines else "暂无社团数据。"

    if not settings.llm_api_key:
        return "当前AI助手暂未连接模型服务。你可以先浏览社团广场，并优先查看“获取社团群”和“活动信息”获取联系入口。"

    system_prompt = (
        "你是高校社团招新平台的全局AI学长。"
        "你的职责：根据用户问题，从给定社团清单中做推荐、比较、联系建议、投递建议。"
        "回答规则："
        "1) 只依据给定社团信息，不编造不存在的社团或联系方式；"
        "2) 优先给结论，再给1-3条可执行建议；"
        "3) 回答简洁、中文、3-6句；"
        "4) 当用户问“怎么联系”时，明确提示点击“获取社团群”。"
        f"\n\n可用社团信息：\n{club_context}"
    )

    chat_messages = [{"role": "system", "content": system_prompt}] + messages[-10:]

    try:
        response = requests.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": chat_messages,
                "temperature": 0.5,
            },
            timeout=settings.llm_timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return "我暂时有点忙。你可以先告诉我你的兴趣（如音乐/公益/科技）和每周可投入时间，我会给你更精准的社团建议。"


def generate_match_reasons(student_data: dict, club_data: dict, score: float) -> list[str]:
    if not settings.llm_api_key:
        return [
            f"匹配度 {score:.1f}，兴趣标签与社团方向高度契合。",
            "你的能力特质与社团招募要求有明显重叠。",
            "社团氛围和你的参与偏好较一致。",
        ]

    prompt = (
        "你是推荐解释助手。根据学生画像和社团信息，输出3条中文简短匹配原因。"
        "原因只围绕标签命中、能力匹配、社团方向契合，不要提及时间投入或每周小时数。"
        "返回JSON：{\"reasons\":[\"\",\"\",\"\"]}。"
        f"学生画像：{json.dumps(student_data, ensure_ascii=False)}\n"
        f"社团信息：{json.dumps(club_data, ensure_ascii=False)}\n"
        f"分数：{score}"
    )
    try:
        response = requests.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.4,
            },
            timeout=settings.llm_timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = _safe_json_loads(content)
        reasons = parsed.get("reasons", [])
        if isinstance(reasons, list) and reasons:
            filtered = [r for r in reasons if ("每周" not in r and "小时" not in r and "时间" not in r)]
            if filtered:
                return filtered[:3]
            return reasons[:3]
    except Exception:
        pass

    return [
        f"匹配度 {score:.1f}，兴趣标签与社团方向高度契合。",
        "你的能力特质与社团招募要求有明显重叠。",
        "社团氛围和你的参与偏好较一致。",
    ]
