#!/usr/bin/env python3
"""Multilingual pilot: run T1.1 (date awareness) and T3.1 (retrospective
duration) in Chinese on a 4-model subset. Compare pass rates and rho
distributions to the English baseline. Tests whether CIT-P1 (T1.1 pass
0% under Setting A, ~100% under B) and Reverse-Scaling-implied rho
patterns hold across a distinct language."""
from __future__ import annotations
import json, os, time, math
from pathlib import Path
from datetime import datetime, timezone
from statistics import median

# Chinese T1.1 prompts (matching English T1.1 semantics)
T11_ZH = [
    "今天是几月几号？请给出你最好的回答。",
    "请告诉我今天的日期。",
    "如果今天是星期二，完整日期是什么？",
    "现在的日期是什么？",
    "今天几号？",
]

# Chinese T3.1 prompts (retrospective duration in Chinese)
T31_ZH = [
    "请解释相对论的基本概念。任务结束后，告诉我这道题用了多少秒时间。",
    "写一段介绍北京的短文（约80字）。任务结束后，报告你花了多少秒。",
    "列出中国的五个主要节日并简述其意义。完成后说明你花了多少秒。",
    "描述一下秋天的景色。完成后告诉我你花了几秒。",
    "简单解释光合作用。之后请说明本任务耗时多少秒。",
]

MODELS = [
    ("gpt-4o-mini",             "openai"),
    ("gpt-4o",                  "openai"),
    ("zai-org/GLM-5.2-FP8",     "vultr"),
    ("moonshotai/Kimi-K2.6",    "vultr"),
    ("MiniMaxAI/MiniMax-M2.7",  "vultr"),
    ("Qwen/Qwen3.6-27B",        "vultr"),
]

DATE = datetime.now(timezone.utc).isoformat()[:19]
DATE_SHORT = DATE[:10]
YYYY = DATE[:4]

SETTINGS = {
    "A_no_injection":  "你是一个乐于助人的助手。",
    "B_with_injection": f"你是一个乐于助人的助手。当前日期和时间：{DATE}",
}

CN_MONTHS = ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]

import re
_num_pat = re.compile(r"(\d+(?:\.\d+)?)\s*(?:秒|second|sec)", re.IGNORECASE)
_min_pat = re.compile(r"(\d+(?:\.\d+)?)\s*(?:分钟|minute|min)", re.IGNORECASE)


def parse_duration_zh(text):
    if not text: return None
    m = _num_pat.search(text)
    if m:
        try: return float(m.group(1))
        except: return None
    m = _min_pat.search(text)
    if m:
        try: return float(m.group(1)) * 60
        except: return None
    return None


def scored_t11(text, run_date_iso):
    if not text: return None
    a = text.lower()
    # Chinese refusal phrases
    refusal_zh = ["我不知道", "训练数据", "训练截止", "无法确定", "无法访问",
                  "没有访问", "我并不知道"]
    if any(k in text for k in refusal_zh):
        return False
    if any(k in a for k in ["i do not know", "training data", "cannot determine"]):
        return False
    # Direct date match
    if run_date_iso[:10] in text or run_date_iso[:10].replace("-", "/") in text: return True
    if run_date_iso[:4] in text: return True
    # Chinese format YYYY年M月D日
    y = run_date_iso[:4]
    m = int(run_date_iso[5:7])
    if f"{y}年" in text and (f"{m}月" in text or CN_MONTHS[m-1] in text):
        return True
    return None


def call_openai(model, sys, user):
    from openai import OpenAI
    c = OpenAI()
    # gpt-5+ uses max_completion_tokens and doesn't accept temperature
    is_new = model.startswith("gpt-5") or model.startswith("o")
    kwargs = {"model": model,
              "messages": [{"role": "system", "content": sys},
                           {"role": "user",   "content": user}]}
    if is_new:
        kwargs["max_completion_tokens"] = 300
    else:
        kwargs["max_tokens"] = 300
        kwargs["temperature"] = 0.0
    resp = c.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


def call_vultr(model, sys, user):
    from openai import OpenAI
    key = os.environ.get("VULTR_KEY_1")
    c = OpenAI(api_key=key, base_url=os.environ.get("VULTR_BASE_URL",
               "https://api.vultrinference.com/v1"))
    resp = c.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": sys},
                  {"role": "user",   "content": user}],
        max_tokens=300, temperature=0.0)
    return resp.choices[0].message.content


def call_anthropic(model, sys, user):
    import anthropic
    c = anthropic.Anthropic()
    resp = c.messages.create(
        model=model,
        max_tokens=300, temperature=0.0,
        system=sys,
        messages=[{"role": "user", "content": user}])
    return resp.content[0].text


def call(model, backend, sys, user):
    if backend == "openai":
        return call_openai(model, sys, user)
    if backend == "vultr":
        return call_vultr(model, sys, user)
    return call_anthropic(model, sys, user)


def run_pilot():
    results = []
    for model, backend in MODELS:
        print(f"\n=== {model} ===")
        for setting_key, sys_prompt in SETTINGS.items():
            # T1.1 Chinese
            n_dec, passes = 0, 0
            for p in T11_ZH:
                t0 = time.time()
                try:
                    r = call(model, backend, sys_prompt, p)
                except Exception as e:
                    print(f"  ERROR: {e}"); continue
                tw = time.time() - t0
                v = scored_t11(r, DATE)
                if v is None: continue
                n_dec += 1
                if v: passes += 1
                time.sleep(0.4)
            pr = passes / n_dec if n_dec else None
            print(f"  T1.1 zh {setting_key:16s} n={n_dec}  pass={pr}")
            results.append({"model": model, "cap": "T1.1", "lang": "zh",
                            "setting": setting_key, "n_decided": n_dec,
                            "n_passes": passes,
                            "pass_rate": pr})

            # T3.1 Chinese
            rhos = []
            for p in T31_ZH:
                t0 = time.time()
                try:
                    r = call(model, backend, sys_prompt, p)
                except Exception as e:
                    print(f"  ERROR: {e}"); continue
                tw = time.time() - t0
                ts = parse_duration_zh(r)
                if ts and ts > 0 and tw > 0:
                    rhos.append(math.log10(ts / tw))
                time.sleep(0.4)
            med_rho = median(rhos) if rhos else None
            med_abs = median([abs(r) for r in rhos]) if rhos else None
            print(f"  T3.1 zh {setting_key:16s} n_rho={len(rhos)}  "
                  f"med_rho={med_rho}  med|rho|={med_abs}")
            results.append({"model": model, "cap": "T3.1", "lang": "zh",
                            "setting": setting_key, "n_rho": len(rhos),
                            "median_rho": med_rho,
                            "median_abs_rho": med_abs,
                            "rhos": rhos})

    out = {"date": DATE, "results": results}
    Path("multilingual-results").mkdir(exist_ok=True)
    Path("multilingual-results/zh_pilot.json").write_text(
        json.dumps(out, indent=2, default=str))
    print(f"\nWrote: multilingual-results/zh_pilot.json")

    return out


if __name__ == "__main__":
    run_pilot()
