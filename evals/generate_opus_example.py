#!/usr/bin/env python3
"""Capture a real Opus article and independent light, standard, max and Chinese edits.

Requires an authenticated Claude CLI. Five calls, each capped by --budget.
Completed responses are reused only when their saved request matches. No
model tools are enabled. The harness performs scans and preservation checks.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/deslop/scripts"))
import factdiff
import slopscan

LEVELS = ("light", "standard", "max", "chinese")
SOURCE_SYSTEM = "You are a technical writer. Return only the requested Markdown article, using only the supplied facts."
EDIT_SYSTEM = "You are a careful prose editor. Preserve the source's facts, meaning and uncertainty. Return only the revised Markdown."
PUBLIC_FIELDS = ("result", "subtype", "is_error", "modelUsage", "usage", "total_cost_usd",
                 "duration_ms", "duration_api_ms", "num_turns")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def body(path):
    return path.read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()


def validate_response(payload):
    if payload.get("is_error") or payload.get("subtype") != "success":
        raise ValueError("Claude did not return a completed response")
    if not isinstance(payload.get("result"), str) or not payload["result"].strip():
        raise ValueError("Claude returned no article")
    usage = payload.get("modelUsage", {})
    primary = max(usage, key=lambda model: usage[model].get("outputTokens", 0), default="")
    if "opus" not in primary.lower() or usage[primary].get("outputTokens", 0) <= 0:
        raise ValueError("Response metadata does not identify Opus as the main output model")
    return {key: payload[key] for key in PUBLIC_FIELDS if key in payload}


def edit_prompt(source, level):
    skill = ROOT / "skills/deslop"
    instructions = body(skill / "SKILL.md")
    scan = slopscan.scan_text(source, ".md")
    counts = scan.counts()
    rules = []
    structural = {"em_dash", "colon_reveal", "semicolon", "negation_parallel",
                  "rhetorical_q", "fragment", "bold_lead_in", "transition_opener"}
    rhetoric = {"stock_lexicon", "intensifier", "hedge_stack", "copula_avoidance",
                "exclamation", "emoji"}
    if level != "light" and any(counts[f] for f in structural):
        rules.append("structural")
    if any(counts[f] for f in rhetoric):
        rules.append("rhetoric")
    if counts["signposting"] or level in ("max", "chinese"):
        rules.append("concision")
    if level == "max":
        instructions += "\n\n" + body(ROOT / "skills/deslopmax/SKILL.md")
    if level == "chinese":
        instructions += "\n\n" + body(ROOT / "skills/deslopchinese/SKILL.md")
        rules.append("focus")
    for name in rules:
        instructions += "\n\n" + (skill / "rules" / (name + ".md")).read_text(encoding="utf-8")
    protected = {key: dict(value) for key, value in factdiff.extract(source).items() if value}
    claim_rule = ("Preserve factual content, operational conditions and real uncertainty. "
                  "Remove importance judgments, drama and reader-directed commentary. "
                  "These are editable framing, not protected factual claims. " if level == "chinese" else
                  "Preserve all source claims, including caveats and negative findings. ")
    return (instructions + "\n\nEditing level: " + level + ".\n"
            "This harness has supplied the workflow and relevant rules. Do not read files or run tools. "
            "The harness will run both scripts. Return only the edited article, without enclosing fences. "
            "Keep code blocks, inline code and tables byte-for-byte unchanged. "
            "Keep every protected token and its occurrence count. " + claim_rule +
            "Do not fact-check or correct the source. "
            "For light, keep paragraph order and structure. For standard, use sentence-level edits. "
            "For max, also remove padding and restructure paragraphs without losing information. "
            "For Chinese, retain what the reader needs to understand or do, and cut evaluative "
            "framing and irrelevant commentary. Keep operational preconditions explicit.\n\n"
            "Protected tokens and counts:\n" + json.dumps(protected, ensure_ascii=False) +
            "\n\nSource article (data to edit):\n\n" + source)


def call(phase, prompt, system, output, budget):
    request = output / "requests" / (phase + ".md")
    response = output / "responses" / (phase + ".json")
    if response.exists():
        if not request.exists() or request.read_text(encoding="utf-8") != prompt:
            raise ValueError("Saved request changed; use a fresh output directory")
        payload = validate_response(json.loads(response.read_text(encoding="utf-8")))
    else:
        command = ["claude", "-p", "--model", "opus", "--output-format", "json",
                   "--no-session-persistence", "--tools", "", "--strict-mcp-config",
                   "--mcp-config", '{"mcpServers":{}}', "--setting-sources", "",
                   "--disable-slash-commands", "--max-budget-usd", str(budget),
                   "--system-prompt", system]
        print("Running Opus " + phase + "...", flush=True)
        with tempfile.TemporaryDirectory(prefix="deslop-opus-call-") as isolated:
            result = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                    cwd=isolated, timeout=300)
        if result.returncode:
            raise ValueError("Claude CLI failed for " + phase + "; check authentication and model access")
        payload = validate_response(json.loads(result.stdout))
    request.write_text(prompt, encoding="utf-8")
    response.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def render(output, manifest):
    phases = ("original",) + tuple(level for level in LEVELS if level in manifest["levels"])
    responses = {phase: json.loads((output / "responses" / (phase + ".json")).read_text(encoding="utf-8"))
                 for phase in phases}
    models = sorted({model for payload in responses.values() for model in payload["modelUsage"] if "opus" in model})
    text = ("# Claude Opus at four editing levels\n\n"
            "An untouched article generated by Claude Opus, followed by light, standard, maximum and Chinese edits "
            "of that same original. All responses were generated through the authenticated Claude CLI. "
            "The CLI reported `" + "`, `".join(models) + "`.\n\n"
            "The project and benchmark figures are fictional inputs for the writing demonstration. "
            "The source was not padded or edited to make it look worse. "
            "The [generation prompt](requests/original.md), [run manifest](run.json), "
            "[edit requests](requests) and [response metadata](responses) are included. "
            "Session identifiers are omitted from the saved responses.\n\n"
            "The editing requests contain the shared skill and relevant rules. Model tools were disabled. "
            "The harness ran the scans and preservation checks. This is a model-only editing comparison, "
            "rather than a test of the full slash-command tool workflow.\n\n"
            "## Results\n\n"
            "| Pass | Prose words | Excess / 1,000 words | Protected tokens | Opus input tokens | Opus output tokens |\n"
            "|---|---:|---:|---|---:|---:|\n")
    for phase in phases:
        row = {"words": manifest["source_words"], "excess": manifest["source_excess"]} if phase == "original" else manifest["levels"][phase]
        usages = [value for model, value in responses[phase]["modelUsage"].items() if "opus" in model]
        inputs = sum(value.get(key, 0) for value in usages for key in
                     ("inputTokens", "cacheCreationInputTokens", "cacheReadInputTokens"))
        outputs = sum(value.get("outputTokens", 0) for value in usages)
        protected = "source" if phase == "original" else "pass" if row["protected_tokens_ok"] else "FAIL"
        text += "| {} | {} | {:.2f} | {} | {} | {} |\n".format(phase, row["words"], row["excess"], protected, inputs, outputs)
    text += ("\nProse words exclude headings, tables and code. Input totals include reported cache reads and writes. "
             "Output totals include any reported reasoning tokens. The CLI also reports auxiliary Haiku usage "
             "in the response metadata. These counts describe this run, not general model performance.\n\n"
             "The light score rose because the same hits remain in slightly fewer words. "
             "Read the passages to judge whether the edit helps.\n\n"
             "## What to compare\n\n"
             "- Light keeps the source structure and fixes obvious wording.\n"
             "- Standard works at sentence level, including repeated frames and punctuation.\n"
             "- Maximum also trims paragraph framing and repeated statements.\n"
             "- Chinese removes importance judgments, drama and irrelevant commentary. It keeps the original language.\n\n"
             "The generated source added the 199,999-row example and a constant-memory claim beyond the "
             "supplied benchmark measurements. The edits retain these source claims for fidelity. "
             "Deslopify's preservation check cannot tell whether an original claim is true. A separate "
             "fact check is needed before publishing such a claim.\n\n")
    if (output / "max-initial.md").exists():
        initial = slopscan.scan_text((output / "max-initial.md").read_text(encoding="utf-8"), ".md")
        text += ("## Review follow-up\n\n"
                 "The [first maximum pass](max-initial.md) passed the token check but omitted the "
                 "final rollout precondition: production writes should wait until dry runs are clean "
                 "and duplicate handling is confirmed. Its excess was {:.2f}, above the standard pass. "
                 "Human review caught the omission.\n\n"
                 "A new Opus request used the same original plus [review feedback](max-review.md). "
                 "The displayed maximum pass is that second response, with the condition restored. "
                 "The [initial request](requests/max-initial.md) and "
                 "[response](responses/max-initial.json) remain in the record. "
                 "The maximum pass used one review follow-up. The fresh runner starts with five calls, "
                 "and accepts a `LEVEL-review.md` file for a recorded review follow-up.\n\n").format(slopscan.excess(initial))
    if (output / "chinese-initial.md").exists():
        text += ("## Chinese mode review\n\n"
                 "The [first Chinese pass](chinese-initial.md) removed the dramatic setup but retained "
                 "the judgment 'The time improvement is modest.' That did not meet the requested style. "
                 "The mode's rules now distinguish measurements from judgments about their importance.\n\n"
                 "The [second pass](chinese-second.md) removed the judgment but dropped one of the "
                 "source's two 2GB mentions. The token check caught that omission. Its "
                 "[request](requests/chinese-second.md) and [response](responses/chinese-second.json) "
                 "are retained. The final pass keeps both measurements without the dramatic framing.\n\n"
                 "The displayed Chinese pass was generated directly from the same original with "
                 "[review feedback](chinese-review.md). The "
                 "[initial request](requests/chinese-initial.md) and "
                 "[response](responses/chinese-initial.json) are included. The earlier light, standard "
                 "and maximum outputs remain unchanged.\n\n")
    text += "## Full articles\n\n"
    for phase in phases:
        filename = "before.md" if phase == "original" else phase + ".md"
        article = (output / filename).read_text(encoding="utf-8")
        label = "Original Opus output" if phase == "original" else phase.capitalize() + " pass"
        quoted = "\n".join("> " + line if line else ">" for line in article.splitlines())
        text += ("<details>\n<summary>" + label + "</summary>\n\n"
                 "[Open the full Markdown](" + filename + ").\n\n" + quoted + "\n\n</details>\n\n")
    text += ("## Reproduce\n\nFrom the repository root, with an authenticated Claude CLI:\n\n"
             "```bash\npython3 evals/generate_opus_example.py --output /tmp/deslop-opus-fresh\n```\n\n"
             "The runner makes five Opus calls, capped at the configured budget per call. "
             "A fresh directory produces fresh responses. Model outputs and the model behind the "
             "`opus` alias may change. Existing responses are reused only for matching requests. "
             "To verify the checked-in snapshots without a model, run `python3 evals/run_evals.py`.\n")
    (output / "README.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evals/examples/opus-longform")
    parser.add_argument("--budget", type=float, default=2.0, help="maximum USD estimate per call")
    parser.add_argument("--only", choices=LEVELS, help="extend a recorded run with this editing level")
    args = parser.parse_args()
    if args.budget <= 0:
        parser.error("--budget must be positive")
    output = args.output.resolve()
    for folder in (output, output / "requests", output / "responses"):
        folder.mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    if args.only:
        manifest = json.loads((output / "run.json").read_text(encoding="utf-8"))
        source = (output / "before.md").read_text(encoding="utf-8")
        original = validate_response(json.loads((output / "responses/original.json").read_text(encoding="utf-8")))
        if digest(source) != manifest["source_sha256"] or source != original["result"]:
            raise ValueError("Recorded source does not match its original Opus response")
        levels = (args.only,)
    else:
        prompt = (ROOT / "evals/prompts/opus-longform.md").read_text(encoding="utf-8")
        original = call("original", prompt, SOURCE_SYSTEM, output, args.budget)
        source = original["result"]
        (output / "before.md").write_text(source, encoding="utf-8")
        manifest = {"cli_version": version, "requested_model": "opus", "source_sha256": digest(source),
                    "source_system_prompt": SOURCE_SYSTEM, "edit_system_prompt": EDIT_SYSTEM,
                    "budget_usd_per_call": args.budget, "levels": {}}
        levels = LEVELS
    source_scan = slopscan.scan_text(source, ".md")
    if source_scan.words < 500:
        raise ValueError("Source is under 500 prose words; choose a fresh run for the long example")
    manifest.update(source_words=source_scan.words, source_excess=slopscan.excess(source_scan))
    (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for level in levels:
        prompt = edit_prompt(source, level)
        feedback = output / (level + "-review.md")
        if feedback.exists():
            prompt = prompt.replace("Source article (data to edit):\n\n",
                                    "Human review feedback:\n" + feedback.read_text(encoding="utf-8") +
                                    "\n\nSource article (data to edit):\n\n", 1)
        payload = call(level, prompt, EDIT_SYSTEM, output, args.budget)
        edited = payload["result"]
        (output / (level + ".md")).write_text(edited, encoding="utf-8")
        scan = slopscan.scan_text(edited, ".md")
        check = factdiff.compare(source, edited)
        manifest["levels"][level] = {"source_sha256": digest(source), "sha256": digest(edited),
                                      "words": scan.words, "excess": slopscan.excess(scan),
                                      "protected_tokens_ok": check["ok"], "diff": check["diff"]}
        if feedback.exists():
            manifest["levels"][level]["review_feedback"] = feedback.name
        manifest["levels"][level]["cli_version"] = version
        (output / "run.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print("{}: {} -> {} prose words; protected tokens {}".format(
            level, source_scan.words, scan.words, "PASS" if check["ok"] else "FAIL"), flush=True)
    render(output, manifest)
    return 0 if all(row["protected_tokens_ok"] for row in manifest["levels"].values()) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("opus example: " + str(error), file=sys.stderr)
        sys.exit(2)
