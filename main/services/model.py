import datetime, operator

OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}

def infer_season(dt=None):
    date = dt or datetime.date.today()
    month = date.month

    if 6 <= month <= 10: 
        return "kharif"
    
    if 11 <= month or month <= 4: 
        return "rabi"
    
    return "zaid"

def parse_cmp(expr):
    if not isinstance(expr, str):
        return None, None
    
    parts = expr.strip().split()

    if len(parts) != 2:
        return None, None
    
    op_s, num_s = parts 
    try:
        return op_s, float(num_s)
    except Exception:
        return None, None
    

def eval_rule_cond(cond: dict, ctx: dict) -> bool:
    if "season" in cond:
        v = cond["season"]
        if not isinstance(v, str) or ctx.get("season") != v:
            return False
        
    if "crop" in cond:
        v = cond["crop"]
        if not isinstance(v, str) or (ctx.get("crop_current") or "") != v.lower():
            return False
    
    if "soil_in" in cond:
        allowed = cond["soil_in"]
        if not isinstance(allowed, (list, tuple)):
            return False
        
        soil = (ctx.get("soil_type") or "")
        if soil not in [str(x).lower() for x in allowed]:
            return False
        
    for key_ctx, key_cond in (
        ("das","das"),
        ("max_rain_next48","max_rain_next48"),
        ("tmax_today","tmax_today"),
        ("tmin_today","tmin_today"),
    ):
        if key_cond in cond:
            op_s, val = parse_cmp(cond[key_cond])
            if not op_s or OPS.get(op_s) is None:
                return False 
            left = float(ctx.get(key_ctx, 0) or 0)
            if not OPS[op_s](left, val):
                return False

    return True

def best_crops_rules():
    return [
        {"id":"crop-wheat","when":{"season":"rabi","soil_in":["loamy","alluvial"]},"advice":{"type":"crop","title":"Wheat","reason":"Suited for Rabi in loamy/alluvial soils"}},
        {"id":"crop-mustard","when":{"season":"rabi","soil_in":["sandy","loamy"]},"advice":{"type":"crop","title":"Mustard","reason":"Rabi oilseed; moderate water"}},
        {"id":"crop-rice","when":{"season":"kharif","soil_in":["clay","alluvial","loamy"]},"advice":{"type":"crop","title":"Rice","reason":"Kharif crop; high water availability"}},
        {"id":"crop-maize","when":{"season":"kharif","soil_in":["loamy","sandy"]},"advice":{"type":"crop","title":"Maize","reason":"Kharif; lower water than rice"}},
    ]

def irrigation_rules():
    return [
        {"id":"irr-need","when":{"tmax_today":">= 32","max_rain_next48":"< 40"}, "advice":{"type":"irrigation","title":"Irrigate","detail":"Morning irrigation recommended"}},
        {"id":"irr-defer","when":{"max_rain_next48":">= 60"}, "advice":{"type":"irrigation","title":"Defer Irrigation","detail":"Rain likely in 48h"}},
    ]

def fertilizer_rules():
    return [
        {"id":"fert-urea-top","when":{"crop":"wheat","das":">= 20","max_rain_next48":"< 60"}, "advice":{"type":"fertilizer","title":"Top-dress Urea","detail":"Apply 25–30 kg/acre"}},
        {"id":"fert-delay-rain","when":{"crop":"wheat","das":">= 20","max_rain_next48":">= 60"}, "advice":{"type":"fertilizer","title":"Delay Urea","detail":"High rain risk; postpone 1–2 days"}},
    ]

def pest_rules():
    return [
        {"id":"pest-aphid-risk","when":{"season":"rabi","crop":"wheat","tmin_today":">= 10","tmax_today":"<= 28"}, "advice":{"type":"pest","title":"Aphid Risk","detail":"Scout leaves; use neem spray if needed"}},
    ]


def evaluate_all(ctx_input: dict):
    weather = (ctx_input.get("weather") or {})
    daily = (ctx_input.get("weather") or {}).get("daily", [])
    if not isinstance(daily, list):
        daily = []
    first = daily if daily and isinstance(daily, dict) else {}
    tmax_today = float(first.get("tmax", 0) or 0)
    tmin_today = float(first.get("tmin", 0) or 0)
    max_rain_next48 = float(max((d.get("rain_prob", 0) for d in daily[:2] if isinstance(d, dict)), default=0))

    sow_date = ctx_input.get("sow_date")
    das = (datetime.date.today() - sow_date).days if sow_date else 0
    season = infer_season(sow_date)

    base = {
        "season": season,
        "soil_type": (ctx_input.get("soil_type") or "").lower(),
        "crop_current": (ctx_input.get("crop_current") or "").lower(),
        "das": int(das),
        "max_rain_next48": float(max_rain_next48),
        "tmax_today": float(tmax_today),
        "tmin_today": float(tmin_today),
    }

    def run(rule_list):
        out = []
        for r in rule_list:
            if eval_rule_cond(r.get("when", {}), base):
                advice = dict(r.get("advice", {}))
                advice["rule_id"] = r.get("id")
                out.append(advice)
        return out

    return {
        "crops": run(best_crops_rules()),
        "irrigation": run(irrigation_rules()),
        "fertilizer": run(fertilizer_rules()),
        "pest": run(pest_rules()),
        "ctx": base,
    }