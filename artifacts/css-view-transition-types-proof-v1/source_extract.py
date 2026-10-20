import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('use -I -S without optimization')
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parent

def body(file, marker):
    raw=(ROOT/'source'/file).read_text()
    if raw.count(marker)!=1:raise RuntimeError('nonunique marker: '+marker)
    start=raw.index(marker);opening=raw.index('{',start)
    depth=0;i=opening;state='code'
    while i<len(raw):
        c=raw[i];n=raw[i:i+2]
        if state=='line':
            if c=='\n':state='code'
        elif state=='comment':
            if n=='*/':state='code';i+=1
        elif state in ('"',"'"):
            if c=='\\':i+=1
            elif c==state:state='code'
        elif n=='//':state='line';i+=1
        elif n=='/*':state='comment';i+=1
        elif c in ('"',"'"):state=c
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                text=raw[start:i+1]
                return dict(source='source/'+file,marker=marker,offset=len(raw[:start].encode()),bytes=len(text.encode()),sha256=hashlib.sha256(text.encode()).hexdigest(),complete_text=text)
        i+=1
    raise RuntimeError('unclosed body: '+marker)

SPECS=[
('atom_key_specialization','xpcom__ds__nsTHashMap.h','struct nsKeyClass<nsAtom*> {'),
('weak_atom_key','xpcom__ds__nsAtomHashKeys.h','struct nsWeakAtomHashKey : public nsPtrHashKey<nsAtom> {'),
('startup_original','Document.original.cpp','already_AddRefed<ViewTransition> Document::StartViewTransition('),
('startup','dom__base__Document.cpp','already_AddRefed<ViewTransition> Document::StartViewTransition('),
('constructor','dom__view-transitions__ViewTransition.cpp','ViewTransition::ViewTransition(Document& aDoc,'),
('types','dom__view-transitions__ViewTransition.cpp','ViewTransitionTypeSet* ViewTransition::Types()'),
('add','dom__view-transitions__ViewTransitionTypeSet.cpp','ViewTransitionTypeSet* ViewTransitionTypeSet::Add('),
('clear','dom__view-transitions__ViewTransitionTypeSet.cpp','void ViewTransitionTypeSet::Clear('),
('delete','dom__view-transitions__ViewTransitionTypeSet.cpp','bool ViewTransitionTypeSet::Delete('),
('generated_helpers','objdir-full.noindex__dom__bindings__ViewTransitionBinding.cpp','namespace SetlikeHelpers {'),
('selector_bridge','layout__style__GeckoBindings.cpp','bool Gecko_HasActiveViewTransitionTypes('),
('selector_validity','layout__style__GeckoBindings.cpp','static bool IsValidViewTransitionType('),
('selector_branch','servo__components__style__gecko__wrapper.rs','NonTSPseudoClass::ActiveViewTransitionType(ref types) => {'),
('selector_state','servo__components__style__gecko__selector_parser.rs','    pub fn state_flag(&self) -> ElementState {'),
('hashset_insert','xpcom__ds__nsTHashSet.h','  bool EnsureInserted(ValueType aValue) {'),
('hash_count_insert','xpcom__ds__nsTHashtable.h','  [[nodiscard]] bool EnsureInserted(KeyType aKey,'),
('pointer_equals','xpcom__ds__nsPointerHashKeys.h','  bool KeyEquals(KeyTypePointer aKey) const {'),
('atom_equals','xpcom__ds__nsAtom.h','  bool Equals(char16ptr_t aString, uint32_t aLength) const {'),
('atom_key_equals','xpcom__ds__nsAtomTable.cpp','  bool Equals(const nsAtom* aAtom) const {'),
('atom_lookup_insert','xpcom__ds__nsAtomTable.cpp','already_AddRefed<nsAtom> nsAtomTable::GetOrInsert(const nsAString& aUTF16String,'),
('atom_main_thread','xpcom__ds__nsAtomTable.cpp','already_AddRefed<nsAtom> nsAtomTable::AtomizeMainThread(\n    const nsAString& aUTF16String)'),
('atom_entry','xpcom__ds__nsAtomTable.cpp','already_AddRefed<nsAtom> NS_AtomizeMainThread(const nsAString& aUTF16String)'),
('array_index','xpcom__ds__nsTArray.h','  [[nodiscard]] index_type IndexOf(const Item& aItem, index_type aStart,'),
('array_remove','xpcom__ds__nsTArray.h','  bool RemoveElement(const Item& aItem, const Comparator& aComp) {'),
('array_remove_default','xpcom__ds__nsTArray.h','  bool RemoveElement(const Item& aItem) {')]

def bindings():
    rows=[]
    for name,file,marker in SPECS:
        row=body(file,marker);row['name']=name;rows.append(row)
    return rows
if __name__=='__main__':
    print(json.dumps(bindings(),indent=2))
