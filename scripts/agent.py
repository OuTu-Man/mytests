import json
import sys
from pathlib import Path

# 直接以脚本方式运行时，把 scripts 目录加入搜索路径（作为包导入时无副作用）
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from prompt import SYSTEM_PROMPT
from tools import TOOLS, client


def run_agent(user_input: str, history=None, user_id: str = "U1001", max_steps: int = 6):
    messages = history or []
    if not messages:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "system", "content": f"当前用户ID：{user_id}"})
    messages.append({"role": "user", "content": user_input})

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
        )
        reply = response.choices[0].message.content.strip()
        print(f"\n--- Step {step+1} ---\n{reply}")
        messages.append({"role": "assistant", "content": reply})

        # 最终答案
        if "最终答案：" in reply:
            final = reply.split("最终答案：")[-1].strip()
            return final, messages

        # 解析工具调用
        try:
            action_line = next(line for line in reply.split("\n") if line.startswith("行动："))
            param_line = next(line for line in reply.split("\n") if line.startswith("参数："))
            tool_name = action_line.replace("行动：", "").strip()
            params = json.loads(param_line.replace("参数：", "").strip())
        except Exception as e:
            messages.append({"role": "user", "content": f"格式错误：{e}，请重新按格式输出。"})
            continue

        # 执行工具
        if tool_name not in TOOLS:
            result = f"未知工具：{tool_name}"
        else:
            func, _ = TOOLS[tool_name]
            try:
                result = func(**params)
            except Exception as e:
                result = f"工具执行失败：{e}"

        print(f"观察：{result}")
        messages.append({"role": "user", "content": f"观察：{result}"})

    return "抱歉，我暂时无法处理，已为您转人工客服。", messages


# ==================== 交互式测试 ====================

if __name__ == "__main__":
    history = []
    print("星辰商城客服小星已上线，输入 exit 退出。\n")
    while True:
        user = input("用户：").strip()
        if user.lower() in ("exit", "quit"):
            break
        if not user:
            continue
        answer, history = run_agent(user, history)
        print(f"\n小星：{answer}\n")
