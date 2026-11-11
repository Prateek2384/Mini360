from statistics import mean

CATEGORY_ORDER = ["communication", "collaboration", "accountability"]


def _gap(self_score: float | None, others: float) -> float | None:
    return None if self_score is None else self_score - others


def _self_mean(values: list[float | None]) -> float | None:
    if not values or any(v is None for v in values):
        return None
    return float(mean(values))


def compute_results(questions, self_scores: dict, rater_scores: dict) -> dict:
    items = []
    for q in sorted(questions, key=lambda q: q.position):
        others = float(mean(rater_scores[q.id]))
        self_score = self_scores.get(q.id)
        self_score = float(self_score) if self_score is not None else None
        items.append(
            {
                "question_id": q.id,
                "position": q.position,
                "category": q.category,
                "text": q.text,
                "self_score": self_score,
                "others_mean": others,
                "gap": _gap(self_score, others),
            }
        )

    categories = []
    for category in CATEGORY_ORDER:
        cat_items = [i for i in items if i["category"] == category]
        if not cat_items:
            continue
        others = float(mean(i["others_mean"] for i in cat_items))
        self_score = _self_mean([i["self_score"] for i in cat_items])
        categories.append(
            {
                "category": category,
                "self_score": self_score,
                "others_mean": others,
                "gap": _gap(self_score, others),
            }
        )

    overall_others = float(mean(i["others_mean"] for i in items))
    overall_self = _self_mean([i["self_score"] for i in items])
    focus_areas = sorted(items, key=lambda i: (i["others_mean"], i["position"]))[:2]

    return {
        "overall": {
            "self_score": overall_self,
            "others_mean": overall_others,
            "gap": _gap(overall_self, overall_others),
        },
        "categories": categories,
        "items": items,
        "focus_areas": focus_areas,
    }
