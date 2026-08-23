#!/usr/bin/env python3
"""ดักสัญญาณจาก Claude Code แล้วเขียนลง activity.jsonl ให้หน้า dashboard อ่าน

เรียกจาก .claude/settings.json — รับ JSON ทาง stdin ชื่อเหตุการณ์ทาง argv[1]
ห้าม crash และห้ามพิมพ์อะไรออก stdout เด็ดขาด ไม่งั้นจะไปกวน Claude Code
"""
import sys, os, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "dash", "activity.jsonl")
CAP = 400  # ตัดข้อความยาวๆ ทิ้ง ไฟล์จะได้ไม่บวม


def clip(s, n=CAP):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def describe(tool, ti):
    """สรุปเป็นบรรทัดเดียวว่าเครื่องมือนี้กำลังทำอะไรกับอะไร"""
    if not isinstance(ti, dict):
        return ""
    for key in ("command", "pattern", "file_path", "path", "url", "query", "prompt"):
        if ti.get(key):
            return clip(ti[key])
    if ti.get("description"):
        return clip(ti["description"])
    return clip(json.dumps(ti, ensure_ascii=False))


def main():
    ev = sys.argv[1] if len(sys.argv) > 1 else "?"
    try:
        raw = sys.stdin.read()
        d = json.loads(raw) if raw.strip() else {}
    except Exception:
        d = {}

    tool = d.get("tool_name") or ""
    ti = d.get("tool_input") or {}

    rec = {
        "ts": round(time.time(), 3),
        "ev": ev,
        "sid": (d.get("session_id") or "")[:8],
        "tool": tool,
        "what": describe(tool, ti),
    }

    # ใช้จับคู่ "เริ่ม" กับ "จบ" ของเครื่องมือตัวเดียวกัน
    tid = d.get("tool_use_id") or d.get("toolUseId") or ""
    if tid:
        rec["tid"] = str(tid)[-12:]

    # ตัวย่อยที่ถูกเรียก — เก็บชื่อไว้ให้รู้ว่าใครทำอะไร
    who = (
        d.get("subagent_type")
        or d.get("agent_type")
        or d.get("agent_name")
        or ti.get("subagent_type")
        or ""
    )
    if who:
        rec["agent"] = who
    if ti.get("description"):
        rec["task"] = clip(ti["description"], 120)

    # ผลลัพธ์ของเครื่องมือ — เอาแค่ว่าพังไหม ไม่เก็บเนื้อ
    tr = d.get("tool_response")
    if isinstance(tr, dict):
        if "success" in tr:
            rec["ok"] = bool(tr["success"])
        if tr.get("error"):
            rec["err"] = clip(tr["error"], 200)
    if ev == "PostToolUseFailure":
        rec["ok"] = False

    # เหตุการณ์ระดับ session/agent ที่ไม่มี tool — เก็บคีย์ที่เหลือไว้ดูว่ามีอะไรบ้าง
    if not tool and ev not in ("UserPromptSubmit",):
        extra = {
            k: clip(v, 120)
            for k, v in d.items()
            if k not in ("session_id", "transcript_path", "tool_input", "tool_response", "cwd")
            and isinstance(v, (str, int, float, bool))
        }
        if extra:
            rec["meta"] = extra

    if ev == "UserPromptSubmit":
        rec["what"] = clip(d.get("prompt") or "", 200)

    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        trim()
    except Exception:
        pass


KEEP = 3000  # เก็บย้อนหลังเท่านี้บรรทัด ไฟล์จะได้ไม่โตไม่รู้จบ


def trim():
    try:
        if os.path.getsize(LOG) < 900_000:
            return
        with open(LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) <= KEEP:
            return
        with open(LOG, "w", encoding="utf-8") as f:
            f.writelines(lines[-KEEP:])
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
