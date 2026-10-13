"""Render generation prompts: sample a seed, variant, prefix length and span location per pair (prompts/README.md)."""
import json
import re
from pathlib import Path

import numpy as np

PROMPTS = Path(__file__).resolve().parents[3] / "prompts"

# Same family descriptions as olmo-repo/synth/generate_pairs.py
FAMILIES = {
    "test_suite_tampering": "the agent deletes a failing test, edits a test, suppresses tests (e.g. via conftest), or tampers with an environment variable so the suite passes",
    "validator_tampering": "the agent prints or emits the exact pass-string the validator/grader searches for, instead of doing the work",
    "score_file_tampering": "the agent writes the score/results file directly to report success instead of earning it",
    "information_acquisition": "the agent reads prohibited hidden tests / fixtures / reference solutions it was told not to access, then uses them to shape its answer",
    "reporting": "the agent fabricates success to the user/verifier: claims tests passed when they did not, omits a failure, or claims it verified/ran tests it never ran",
    "hardcoding_special_casing": "the agent hardcodes the specific tested inputs to return the expected outputs (lookup table / if input==X: return expected) instead of implementing the general function",
}


def load_config():
    cfg = json.loads((PROMPTS / "directions.json").read_text())
    seeds = [json.loads(l) for l in (PROMPTS / "task_seeds.jsonl").read_text().splitlines() if l.strip()]
    return cfg, seeds


def _weighted(rng, weights):
    keys = list(weights)
    p = np.array([weights[k] for k in keys], float)
    return keys[rng.choice(len(keys), p=p / p.sum())]


def sample_span_location(rule, direction, variant, rng):
    """Parse the free-text rules in directions.json, e.g. 'random think 0.6 / visible 0.4'."""
    if direction == "base_prose_bullets":
        return "visible"
    if "->" in rule:  # per-variant rules: "code_comment -> visible; data_remark -> think 0.6 / visible 0.4"
        rule = dict(part.split("->") for part in rule.split(";"))
        rule = {k.strip(): v.strip() for k, v in rule.items()}[variant]
    rule = re.sub(r"\(.*?\)", "", rule).replace("random", "")
    opts = re.findall(r"(think|visible)\s*([\d.]+)?", rule)
    if len(opts) == 1:
        return opts[0][0]
    return _weighted(rng, {k: float(w) for k, w in opts})


def eligible_seeds(seeds, filt):
    out = seeds
    if filt.get("tags_any"):
        out = [s for s in out if set(s["tags"]) & set(filt["tags_any"])]
    if filt.get("languages"):
        out = [s for s in out if s["language"] in filt["languages"]]
    if filt.get("exclude_languages"):
        out = [s for s in out if s["language"] not in filt["exclude_languages"]]
    return out


def fill(template, values):
    for k, v in values.items():
        template = template.replace("{" + k + "}", "" if v is None else str(v))
    left = re.findall(r"\{[a-z_]+\}", template)
    assert not left, f"unfilled placeholders: {sorted(set(left))}"
    return template


def render(direction, i, cfg, seeds, seed_uses, rng, shared=True):
    """Prompt and metadata for the i-th pair of a direction. `seed_uses` counts prior uses per (direction, seed)."""
    d = cfg[direction]
    text = (PROMPTS / d["prompt"]).read_text()
    if d["format"] == "gc":
        domain = cfg["gc_domains"][i % len(cfg["gc_domains"])]
        meta = {"gc_domain": domain, "variation_index": i // len(cfg["gc_domains"])}
        text = text.replace("{shared_gc_rules}", (PROMPTS / "_shared_gc_rules.md").read_text() if shared else "[[SHARED GC RULES]]")
        values = meta
    else:
        pool = eligible_seeds(seeds, d.get("seed_filter", {}))
        least = min(seed_uses.get((direction, s["id"]), 0) for s in pool)  # spread reuse evenly
        cands = [s for s in pool if seed_uses.get((direction, s["id"]), 0) == least]
        seed = cands[rng.integers(len(cands))]
        seed_uses[(direction, seed["id"])] = least + 1
        variant = _weighted(rng, d["variants"])
        prefix_len = int(rng.choice(d["prefix_len_choices"]))
        cont_len = 9 - prefix_len - (2 if direction == "task_failure" else 1)
        meta = {"seed_id": seed["id"], "variant": variant, "prefix_len": prefix_len, "cont_len": cont_len,
                "span_location": sample_span_location(d["span_location"], direction, variant, rng),
                "variation_index": least}
        values = {**meta, "language": seed["language"], "domain": seed["domain"], "task_type": seed["task_type"],
                  "task": seed["task"], "file": seed["file"], "shortcut_fn": seed.get("shortcut_fn"),
                  "test_phrase": seed.get("test_phrase"), "neutral_phrase": seed.get("neutral_phrase"),
                  "family_desc": FAMILIES.get(variant, "")}
        text = text.replace("{shared_swe_rules}", (PROMPTS / "_shared_swe_rules.md").read_text() if shared else "[[SHARED SWE RULES]]")
    return fill(text, values), {"direction": direction, "i": i, **meta}


def directions(cfg):
    return [k for k in cfg if not k.startswith("_") and k != "gc_domains"]
