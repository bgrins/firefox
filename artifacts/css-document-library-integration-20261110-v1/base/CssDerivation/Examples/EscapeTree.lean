import CssDerivation.Lowering

namespace CssDerivation.FirstOrder

def hexExpr {Γ : List Ty} : Expr (.scalar :: Γ) .bool :=
  (.or (.or (.and (.leChar (.scalar (Char.ofNat 48)) (.var .here)) (.leChar (.var .here) (.scalar (Char.ofNat 57)))) (.and (.leChar (.scalar (Char.ofNat 65)) (.var .here)) (.leChar (.var .here) (.scalar (Char.ofNat 70))))) (.and (.leChar (.scalar (Char.ofNat 97)) (.var .here)) (.leChar (.var .here) (.scalar (Char.ofNat 102)))))

def whitespaceExpr {Γ : List Ty} : Expr (.scalar :: Γ) .bool :=
  (.or (.or (.eqChar (.var .here) (.scalar (Char.ofNat 10))) (.eqChar (.var .here) (.scalar (Char.ofNat 9)))) (.eqChar (.var .here) (.scalar (Char.ofNat 32))))

def magnitudeExpr {Γ : List Ty} : Expr (.chars :: Γ) .nat :=
  (.foldNat (.var .here) (.nat 0) (.add (.mul (.var (.there .here)) (.nat 16)) (.ite (.leChar (.var .here) (.scalar (Char.ofNat 57))) (.sub (.code (.var .here)) (.nat 48)) (.ite (.leChar (.var .here) (.scalar (Char.ofNat 70))) (.sub (.code (.var .here)) (.nat 55)) (.sub (.code (.var .here)) (.nat 87))))))

def decodeExpr {Γ : List Ty} : Expr (.nat :: Γ) .scalar :=
  (.ite (.or (.or (.eqNat (.var .here) (.nat 0)) (.and (.leNat (.nat 55296) (.var .here)) (.leNat (.var .here) (.nat 57343)))) (.ltNat (.nat 1114111) (.var .here))) (.scalar (Char.ofNat 65533)) (.scalarOf (.var .here)))

def escapeTree : Stmt [] .scalar :=
  (.read (.raiseError (.ret (.scalar (Char.ofNat 65533)))) (.branch hexExpr (.scan 5 hexExpr (.scan 1 whitespaceExpr (.letE (.cons (.var (.there (.there .here))) (.var (.there .here))) (.letE magnitudeExpr (.ret decodeExpr))))) (.ret (.var .here))))

end CssDerivation.FirstOrder
