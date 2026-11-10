import NumberBridge
import PreservedExamples

namespace CssDerivation.NumberTransferExamples

open NumberTransfer ParserIR

def cases : List (String × String × Bool × Exact × String) := [
  ("integer", "123px", false, ⟨123, 0, false, none⟩, "px"),
  ("explicit plus", "+12x", false, ⟨12, 0, false, some '+'⟩, "x"),
  ("negative zero sign retained", "-0;", false, ⟨0, 0, false, some '-'⟩, ";"),
  ("fraction", "3.14px", false, ⟨314, -2, true, none⟩, "px"),
  ("fraction without integer", "-.5!", false, ⟨-5, -1, true, some '-'⟩, "!"),
  ("fraction leading zeros", "0001.00!", false, ⟨100, -2, true, none⟩, "!"),
  ("positive exponent", "1e2!", false, ⟨1, 2, true, none⟩, "!"),
  ("uppercase signed exponent", "2E+3!", false, ⟨2, 3, true, none⟩, "!"),
  ("negative exponent", "2e-3!", false, ⟨2, -3, true, none⟩, "!"),
  ("fraction and exponent", "-001.20e+3px", false, ⟨-120, 1, true, some '-'⟩, "px"),
  ("symbolic large exponent", "1e9999999999!", false, ⟨1, 9999999999, true, none⟩, "!"),
  ("maximal digit run", "123456789px", false, ⟨123456789, 0, false, none⟩, "px"),
  ("fraction marker rollback", "1.", false, ⟨1, 0, false, none⟩, "."),
  ("fraction lookahead rollback", "1.e2", false, ⟨1, 0, false, none⟩, ".e2"),
  ("fraction next dot", "1.2.3", false, ⟨12, -1, true, none⟩, ".3"),
  ("exponent marker rollback", "1e", false, ⟨1, 0, false, none⟩, "e"),
  ("exponent plus rollback", "1e+", false, ⟨1, 0, false, none⟩, "e+"),
  ("exponent minus rollback", "1e-", false, ⟨1, 0, false, none⟩, "e-"),
  ("exponent sign lookahead rollback", "1e+x", false, ⟨1, 0, false, none⟩, "e+x"),
  ("exponent dot lookahead rollback", "1e.2", false, ⟨1, 0, false, none⟩, "e.2"),
  ("fraction kept when exponent fails", "1.5e+", false, ⟨15, -1, true, none⟩, "e+"),
  ("error flag with rollback", "1e+", true, ⟨1, 0, false, none⟩, "e+"),
  ("error flag with success", "2.5e-3!", true, ⟨25, -4, true, none⟩, "!")]

def readyChecks : List (String × Bool) := cases.map fun (name, source, oldError, value, rest) =>
  (name, CssSemantics.CssNumberParts.startsNumber source.toList &&
    decide (NumberTransfer.execute ⟨source.toList, oldError⟩ = some (value, ⟨rest.toList, oldError⟩)))

def offDomain : List (String × String × Exact × String) := [
  ("off-domain empty", "", ⟨0, 0, false, none⟩, ""),
  ("off-domain sign only", "+", ⟨0, 0, false, some '+'⟩, ""),
  ("off-domain sign and exponent", "-e2", ⟨0, 2, true, some '-'⟩, ""),
  ("off-domain dot", ".", ⟨0, 0, false, none⟩, ".")]

def offDomainChecks : List (String × Bool) := offDomain.map fun (name, source, value, rest) =>
  (name, !CssSemantics.CssNumberParts.startsNumber source.toList &&
    decide (NumberTransfer.execute ⟨source.toList, false⟩ = some (value, ⟨rest.toList, false⟩)))

def raisingFailure : Parser (.base .scalar) :=
  .right (.legacy (.raiseError (.ret .unit))) (.take digitPredicate)

def extraChecks : List (String × Bool) := [
  ("generic rollback restores raised error", decide (ParserIR.run (.optional raisingFailure) ⟨['x'], false⟩ = some (none, ⟨['x'], false⟩))),
  ("generic rollback preserves incoming error", decide (ParserIR.run (.optional raisingFailure) ⟨['x'], true⟩ = some (none, ⟨['x'], true⟩))),
  ("generic exponent rollback suffix", decide (ParserIR.run (.optional exponentTree) ⟨"e+!".toList, true⟩ = some (none, ⟨"e+!".toList, true⟩))),
  ("legacy escape error", decide (ParserIR.run (.legacy FirstOrder.escapeTree) ⟨[], false⟩ = some ('�', ⟨[], true⟩))),
  ("legacy initial error", decide (ParserIR.run (.legacy FirstOrder.escapeTree) ⟨['z', '!'], true⟩ = some ('z', ⟨['!'], true⟩))),
  ("generic pair different shapes", decide (ParserIR.run (.pair (.legacy (.ret (.nat 7))) (.take digitPredicate)) ⟨['5', '!'], false⟩ = some ((7, '5'), ⟨['!'], false⟩)))]

def checks := readyChecks ++ offDomainChecks ++ extraChecks

theorem checks_pass : checks.all Prod.snd = true := by decide +kernel

end CssDerivation.NumberTransferExamples
