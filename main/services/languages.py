STRINGS = {
    "en": {
        "task_irrigate": "Irrigate field",
        "task_defer_irrigation": "Defer irrigation",
        "task_fertilize": "Top-dress urea",
        "task_delay_fertilize": "Delay fertilizer",
        "task_scout_pest": "Scout for pests",
        "today_tasks": "Today's Tasks",
        "rainfall_vs_irrigation": "Rainfall vs Irrigation",
    },
    "hi": {
        "task_irrigate": "सिंचाई करें",
        "task_defer_irrigation": "सिंचाई टालें",
        "task_fertilize": "टॉप-ड्रेस यूरिया",
        "task_delay_fertilize": "खाद देना टालें",
        "task_scout_pest": "कीट निरीक्षण करें",
        "today_tasks": "आज के काम",
        "rainfall_vs_irrigation": "वर्षा बनाम सिंचाई",
    },
}

def show_lang(lang, key):
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)
