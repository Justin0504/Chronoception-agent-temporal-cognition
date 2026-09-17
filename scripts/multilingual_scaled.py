#!/usr/bin/env python3
"""Scaled Chinese multilingual run: n=30 per cell on the OpenAI subset.

Upgrades the n=5 pilot to a properly-powered cell so bootstrap CIs can be
reported. Tests whether CIT-P1 (T1.1 0% Setting A -> ~100% Setting B) and
the narrative-axis over-report sign replicate outside English.

Models: gpt-4o-mini, gpt-4o, gpt-5.1  (Anthropic credit exhausted)
Caps:   T1.1 (date awareness), T3.1 (retrospective duration)
Cells:  3 models x 2 caps x 2 settings x 30 instances = 360 calls
"""
from __future__ import annotations
import json, os, re, time, math, random, sys
from pathlib import Path
from datetime import datetime, timezone
from statistics import median
from concurrent.futures import ThreadPoolExecutor, as_completed

DATE = datetime.now(timezone.utc).isoformat()[:19]
YYYY = DATE[:4]

MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-5.1"]

SETTINGS = {
    "no_injection":   "你是一个乐于助人的助手。",
    "with_injection": f"你是一个乐于助人的助手。当前日期和时间：{DATE}",
}

# ---- 30 Chinese T1.1 prompts (date awareness, varied phrasing) ----
T11_ZH = [
    "今天是几月几号？", "请告诉我今天的日期。", "现在是什么日期？",
    "今天几号？", "请问今天的完整日期是什么？",
    "你知道今天是哪一天吗？", "告诉我当前的年月日。",
    "现在是哪一年哪一月哪一天？", "今日日期是？",
    "请写出今天的日期，格式为年-月-日。",
    "我想知道今天的确切日期。", "当前日期是多少？",
    "帮我确认一下今天是几号。", "请说明今天是几月几日。",
    "今天的日期，请回答。", "现在的年份和日期分别是？",
    "你能告诉我今天的日期吗？", "请提供今日的日期信息。",
    "今天是本月的第几天？完整日期是什么？",
    "如果我要写日报，今天该填什么日期？",
    "今天星期几？日期是多少？", "请问现在是几月份？具体哪一天？",
    "报一下今天的日期。", "当前的日历日期是什么？",
    "我需要今天的日期用于记录，请给出。",
    "现在时刻对应的日期是？", "请确认今日年月日。",
    "今天的日期用中文怎么写？", "给我今天的日期，谢谢。",
    "请回答：今天是____年____月____日。",
]

# ---- 30 Chinese T3.1 prompts (task + retrospective duration request) ----
_TASKS_ZH = [
    "请解释相对论的基本概念", "写一段介绍北京的短文（约80字）",
    "列出中国的五个主要节日并简述其意义", "描述一下秋天的景色",
    "简单解释光合作用", "介绍三种常见的编程语言及其特点",
    "写一首关于月亮的短诗", "解释什么是通货膨胀",
    "列举五个世界著名的建筑并简述", "描述如何泡一杯好茶",
    "解释云是怎么形成的", "写一段关于友谊的感想",
    "介绍长江的基本情况", "解释为什么天空是蓝色的",
    "列出三种健康的生活习惯并说明原因", "描述一次难忘的旅行（虚构即可）",
    "简述中国四大发明", "解释什么是人工智能",
    "写一段关于读书重要性的话", "介绍熊猫的生活习性",
    "解释潮汐现象的成因", "列举四种常见的中国菜及做法要点",
    "描述清晨的城市", "简单说明区块链的原理",
    "写一段鼓励他人的话", "介绍太阳系的八大行星",
    "解释什么是碳中和", "描述雨后的森林",
    "列出三本值得读的经典书籍并说明理由", "简述围棋的基本规则",
]
T31_ZH = [f"{t}。完成后，请告诉我这个任务用了多少秒。" for t in _TASKS_ZH]

# ---- Parsers ----
_sec_pat = re.compile(r"(\d+(?:\.\d+)?)\s*(?:秒|second|sec)\b", re.IGNORECASE)
_min_pat = re.compile(r"(\d+(?:\.\d+)?)\s*(?:分钟|分|minute|min)\b", re.IGNORECASE)
CN_DIGITS = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}


def parse_duration_zh(text):
    if not text: return None
    m = _sec_pat.search(text)
    if m:
        try: return float(m.group(1))
        except: pass
    m = _min_pat.search(text)
    if m:
        try: return float(m.group(1)) * 60
        except: pass
    # Chinese numerals: 大约五秒
    m = re.search(r"([一二三四五六七八九十]+)\s*秒", text)
    if m:
        s = m.group(1)
        if s in CN_DIGITS: return float(CN_DIGITS[s])
        if s == "十几": return 15.0
    return None


REFUSAL_ZH = ["我不知道", "训练数据", "训练截止", "知识截止", "无法确定",
              "无法访问", "没有访问", "我并不知道", "无法得知", "不清楚今天",
              "没有实时", "无法获取当前"]


def scored_t11(text, run_date_iso):
    if not text: return None
    if any(k in text for k in REFUSAL_ZH): return False
    a = text.lower()
    if any(k in a for k in ["i do not know", "training data", "cannot determine",
                            "don't have access", "no real-time"]):
        return False
    if run_date_iso[:10] in text or run_date_iso[:10].replace("-", "/") in text:
        return True
    y, mo, d = run_date_iso[:4], int(run_date_iso[5:7]), int(run_date_iso[8:10])
    if f"{y}年" in text and f"{mo}月" in text and f"{d}日" in text: return True
    if y in text and f"{mo}月" in text: return True
    if y in text: return True
    return None


def call_openai(model, sys_p, user_p):
    from openai import OpenAI
    c = OpenAI()
    is_new = model.startswith("gpt-5") or model.startswith("o")
    kw = {"model": model,
          "messages": [{"role": "system", "content": sys_p},
                       {"role": "user",   "content": user_p}]}
    if is_new:
        kw["max_completion_tokens"] = 400
    else:
        kw["max_tokens"] = 400
        kw["temperature"] = 0.0
    r = c.chat.completions.create(**kw)
    return r.choices[0].message.content


def one_trial(model, cap, setting, prompt):
    sys_p = SETTINGS[setting]
    t0 = time.time()
    try:
        resp = call_openai(model, sys_p, prompt)
    except Exception as e:
        return {"err": str(e)[:100]}
    tw = time.time() - t0
    out = {"tau_wall": tw, "resp": (resp or "")[:400]}
    if cap == "T1.1":
        out["pass"] = scored_t11(resp, DATE)
    else:
        ts = parse_duration_zh(resp)
        out["tau_self"] = ts
        if ts and ts > 0 and tw > 0:
            out["rho"] = math.log10(ts / tw)
    return out


def bootstrap_ci(vals, stat, n_iter=5000, seed=0):
    if not vals: return None, None, None
    rng = random.Random(seed); n = len(vals); samples = []
    for _ in range(n_iter):
        s = [vals[rng.randrange(n)] for _ in range(n)]
        samples.append(stat(s))
    samples.sort()
    return stat(vals), samples[int(0.025*n_iter)], samples[int(0.975*n_iter)]


def main():
    results = []
    for model in MODELS:
        for cap, prompts in [("T1.1", T11_ZH), ("T3.1", T31_ZH)]:
            for setting in SETTINGS:
                trials = []
                with ThreadPoolExecutor(max_workers=6) as ex:
                    futs = {ex.submit(one_trial, model, cap, setting, p): p
                            for p in prompts}
                    for f in as_completed(futs):
                        trials.append(f.result())

                if cap == "T1.1":
                    dec = [t["pass"] for t in trials if t.get("pass") is not None]
                    n_dec = len(dec); passes = sum(dec)
                    pr = passes / n_dec if n_dec else None
                    # Wilson 95%
                    lo = hi = None
                    if n_dec:
                        z = 1.96; p = pr; den = 1 + z*z/n_dec
                        c = (p + z*z/(2*n_dec)) / den
                        h = (z * math.sqrt(p*(1-p)/n_dec + z*z/(4*n_dec**2))) / den
                        lo, hi = max(0, c-h), min(1, c+h)
                    row = {"model": model, "cap": cap, "lang": "zh",
                           "setting": setting, "n_trials": len(trials),
                           "n_decided": n_dec, "n_pass": passes,
                           "pass_rate": pr, "wilson_lo": lo, "wilson_hi": hi}
                    print(f"  {model:14s} {cap} zh {setting:15s} "
                          f"n_dec={n_dec:2d}/{len(trials)}  "
                          f"pass={pr if pr is None else f'{pr*100:.0f}%'}"
                          + (f"  [{lo*100:.0f}–{hi*100:.0f}]" if lo is not None else ""))
                else:
                    rhos = [t["rho"] for t in trials if t.get("rho") is not None]
                    med, mlo, mhi = bootstrap_ci(rhos, lambda v: median(v))
                    amed, alo, ahi = bootstrap_ci(rhos, lambda v: median([abs(x) for x in v]))
                    row = {"model": model, "cap": cap, "lang": "zh",
                           "setting": setting, "n_trials": len(trials),
                           "n_rho": len(rhos), "median_rho": med,
                           "rho_ci_lo": mlo, "rho_ci_hi": mhi,
                           "median_abs_rho": amed,
                           "abs_ci_lo": alo, "abs_ci_hi": ahi,
                           "rhos": rhos}
                    print(f"  {model:14s} {cap} zh {setting:15s} "
                          f"n_rho={len(rhos):2d}/{len(trials)}  "
                          + (f"med_rho={med:+.3f} [{mlo:+.3f},{mhi:+.3f}]" if med is not None else "no rho"))
                row["trials"] = trials
                results.append(row)

    out = {"date": DATE, "n_per_cell": 30, "results": results}
    Path("multilingual-results").mkdir(exist_ok=True)
    Path("multilingual-results/zh_scaled.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False, default=str))
    print("\nWrote: multilingual-results/zh_scaled.json")


if __name__ == "__main__":
    main()
