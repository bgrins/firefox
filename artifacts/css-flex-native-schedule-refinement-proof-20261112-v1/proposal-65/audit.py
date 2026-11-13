import re

ALLOWED = {'ClassicalDedekindReals.sig_not_dec', 'ClassicalDedekindReals.sig_forall_dec', 'FunctionalExtensionality.functional_extensionality_dep', 'Classical_Prop.classic'}
TYPES = {'ClassicalDedekindReals.sig_not_dec': 'forall P : Prop, {~ ~ P} + {~ P}', 'ClassicalDedekindReals.sig_forall_dec': 'forall P : nat -> Prop, (forall n : nat, {P n} + {~ P n}) -> {n : nat | ~ P n} + {forall n : nat, P n}', 'FunctionalExtensionality.functional_extensionality_dep': 'forall (A : Type) (B : A -> Type) (f g : forall x : A, B x), (forall x : A, f x = g x) -> f = g', 'Classical_Prop.classic': 'forall P : Prop, P \\/ ~ P'}

def audit(text, roots):
    if not roots:
        assert not text.strip()
        return []
    blocks = text.split('Axioms:\n')
    assert not blocks[0].strip() and len(blocks) == len(roots) + 1
    result = []
    for root, block in zip(roots, blocks[1:]):
        records = list(re.finditer('^([A-Za-z_][\\w.]*)\\s*:', block, re.M))
        assert records and (not block[:records[0].start()].strip())
        names = []
        for i, record in enumerate(records):
            name = 'Classical_Prop.classic' if record[1] == 'classic' else record[1]
            assert name in ALLOWED
            end = records[i + 1].start() if i + 1 < len(records) else len(block)
            body = block[record.end():end]
            assert ''.join(body.split()) == ''.join(TYPES[name].split()), (root, name, body)
            names.append(name)
        assert len(names) == len(set(names))
        result.append({'root': root, 'axioms': sorted(names)})
    return result
