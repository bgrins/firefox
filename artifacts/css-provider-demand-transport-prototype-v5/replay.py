#!/usr/bin/env python3
"""Finite source-correspondence witness; does not execute Firefox or Lean."""
import json
from pathlib import Path


class Incomplete(Exception):
    pass


class Witness:
    def __init__(self, visibility, consumer="A"):
        self.visibility = visibility
        self.raw = {"A": ("B", None), "B": ("A", None), "C": (consumer, "C")}
        self.index = {}
        self.info = []
        self.stack = []
        self.pending = set()
        self.applying = set()
        self.values = {}
        self.font_size = None
        self.trace = []

    def log(self, event, **fields):
        self.trace.append(dict(event=event, **fields))

    def default(self, name):
        if name in self.applying:
            self.log("default_reentry_incomplete", name=name)
            raise Incomplete(name)
        self.applying.add(name)
        try:
            if name == "B":
                if self.font_size is None:
                    self.log("B_initial_demands_font_size")
                    self.visit("C")
                    self.font_size = self.values["C"]
                    self.log("font_size_ready", value=self.font_size)
                value = 10 * self.font_size
            else:
                value = {"A": 5, "C": 7}[name]
            self.values[name] = value
            self.pending.remove(name)
            self.log("default_published", name=name, value=value)
        finally:
            self.applying.remove(name)

    def visit(self, name):
        if name in self.pending:
            if self.visibility == "finalize":
                self.log("pending_participant_serviced", name=name)
                self.default(name)
                return None
            if self.visibility == "missing":
                self.log("pending_participant_mistaken_for_missing", name=name)
                return None
        if name in self.values:
            return None
        if name in self.index:
            index = self.index[name]
            self.log("existing_index", name=name, index=index, active=self.info[index]["active"])
            return index
        index = len(self.info)
        self.index[name] = index
        self.info.append(dict(name=name, lowlink=index, active=True))
        self.stack.append(index)
        lowlink = index
        self_ref = False

        def link(target):
            nonlocal lowlink, self_ref
            other = self.visit(target)
            if other is None:
                return
            if other > index:
                lowlink = min(lowlink, self.info[other]["lowlink"])
            elif other == index:
                self_ref = True
            elif self.info[other]["active"]:
                lowlink = min(lowlink, other)

        primary, fallback = self.raw[name]
        link(primary)
        if primary not in self.values and fallback is not None:
            self.log("fallback_selected", owner=name, pending_primary=primary in self.pending)
            link(fallback)
        self.info[index]["lowlink"] = lowlink
        if lowlink != index:
            return index
        cyclic = self_ref or self.stack[-1] != index
        if cyclic:
            participants = []
            while True:
                member = self.stack.pop()
                self.info[member]["active"] = False
                participants.append(self.info[member]["name"])
                if member == index:
                    break
            self.pending.update(participants)
            self.log("component_classified", participants=participants)
            for participant in participants:
                if participant in self.pending:
                    self.default(participant)
            return None
        self.values[name] = self.values[primary]
        self.log("selected_primary_published", name=name, value=self.values[name])
        assert self.stack.pop() == index
        self.info[index]["active"] = False
        return None


def run(visibility):
    witness = Witness(visibility)
    witness.visit("A")
    assert not witness.pending and not witness.applying and not witness.stack
    return dict(values=witness.values, font_size=witness.font_size, trace=witness.trace)


def main():
    corrected = run("finalize")
    original = run("raw")
    missing = run("missing")
    expected = {"A": 5, "B": 50, "C": 5}
    assert corrected["values"] == expected and corrected["font_size"] == 5
    rejected = []
    for label, value in [("v4_pending_raw_visibility", original), ("pending_as_missing", missing)]:
        assert value["values"] == {"A": 5, "B": 70, "C": 7}
        try:
            assert value["values"] == expected
        except AssertionError:
            rejected.append(label)
        else:
            raise AssertionError("False control unexpectedly met the readiness oracle")
    reentry = Witness("finalize", consumer="B")
    try:
        reentry.visit("A")
    except Incomplete as error:
        assert error.args == ("B",)
        assert "C" not in reentry.values
        assert not reentry.applying
    else:
        raise AssertionError("Reentrant pending default was incorrectly completed")
    result = dict(
        scope="Finite source-correspondence model, not native or normative execution",
        assumptions=["A/B registrations and B initial 10em are admitted", "A is the traversal root", "completion owner certifies the stated constant/em footprint"],
        corrected=corrected,
        sealed_v4_model=original,
        missing_model=missing,
        rejected_false_controls=rejected,
        reentrant_default_returns_incomplete=True,
        reentrant_trace=reentry.trace,
        browser_executed=False,
        native_typechecked=False,
        lean_kernel_checked=False,
    )
    Path(__file__).with_name("REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"corrected": corrected["values"], "v4": original["values"], "false_controls_rejected": len(rejected), "reentry_incomplete": True}))


if __name__ == "__main__":
    main()
